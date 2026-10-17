#!/usr/bin/env python3
"""Check one selected project through the shared validator against a complete Git index."""
import argparse
import hashlib
import json
import stat
from pathlib import Path
import sys

import index_snapshot
import portal


def bundle_inventory(folder, files):
    """Inventory all descendants without following links; reject unknown names/types."""
    folder = Path(folder)
    allowed_files = set(files)
    allowed_dirs = {str(parent) for name in allowed_files for parent in Path(name).parents
                    if str(parent) != "."}
    if folder.is_symlink() or (folder.exists() and not stat.S_ISDIR(folder.lstat().st_mode)):
        raise ValueError("non-directory/symlink CI bundle")
    found_files = set()
    if folder.exists():
        def walk(directory):
            for entry in directory.iterdir():
                relative = entry.relative_to(folder).as_posix()
                mode = entry.lstat().st_mode
                if stat.S_ISDIR(mode) and relative in allowed_dirs:
                    walk(entry)
                elif stat.S_ISREG(mode) and relative in allowed_files:
                    found_files.add(relative)
                else:
                    raise ValueError("unowned or nonregular CI bundle member: " + relative)
        walk(folder)
    return found_files


def bound_members(root, paths, receipt=None):
    """Refuse executing submitted policy that differs from the complete stage-0 index."""
    indexed = index_snapshot._index(root)
    if receipt is not None:
        paths = [*paths, receipt]
    for path in paths:
        supplied = Path(path).absolute()
        # Check the spelled traversal before resolving: a symlink alias cannot
        # silently turn a checkout member into trusted external policy.
        cursor = Path(supplied.anchor)
        for part in supplied.parts[1:]:
            cursor = cursor / part
            if cursor.is_symlink():
                raise ValueError(f"symlink indexed policy member: {supplied}")
        path = supplied.resolve()
        if not path.is_relative_to(root):
            continue  # Central fleet policy outside an owner checkout is trusted, not staged there.
        name = path.relative_to(root).as_posix()
        entry = indexed.get(name)
        if not entry or entry[0] not in ("100644", "100755") or not path.is_file():
            raise ValueError(f"indexed policy member missing or nonregular: {name}")
        if index_snapshot._blob(root, entry[1]) != path.read_bytes():
            raise ValueError(f"indexed policy member differs from executing bytes: {name}")
    if receipt is None:
        return
    data = json.loads(receipt.read_text())
    if data.get("schema") != 1 or data.get("generator") != "fleet-index/documentation/enforce.py":
        raise ValueError("invalid bundle receipt")
    bundle = receipt.parent
    hashes = data.get("hashes")
    if not isinstance(hashes, dict) or any(
            not isinstance(name, str) or not isinstance(digest, str)
            or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)
            or Path(name).is_absolute() or ".." in Path(name).parts
            for name, digest in hashes.items()):
        raise ValueError("invalid bundle receipt members")
    required = {"scripts/check_index.py", "scripts/index_snapshot.py", "scripts/portal.py",
                "schemas/manifest.schema.json", "schemas/review.schema.json", "workspaces.json"}
    if (set(hashes) != required or
            bundle_inventory(bundle, required | {"receipt.json"}) != required | {"receipt.json"}):
        raise ValueError("bundle members differ from receipt")
    prefix = bundle.relative_to(root).as_posix() + "/"
    submitted = {name.removeprefix(prefix) for name, (mode, _) in indexed.items()
                 if name.startswith(prefix)}
    if submitted != required | {"receipt.json"} or any(
            indexed[prefix + name][0] not in ("100644", "100755") for name in submitted):
        raise ValueError("indexed bundle members differ from receipt")
    for name, expected in hashes.items():
        path = bundle / name
        if (any(part.is_symlink() for part in (path, *path.parents) if part.is_relative_to(bundle))
                or hashlib.sha256(path.read_bytes()).hexdigest() != expected):
            raise ValueError(f"bundle receipt mismatch: {name}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check",))
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--git-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--caller", type=Path, help="central hook caller, if it belongs to the selected checkout")
    args = parser.parse_args(argv)
    try:
        root = args.git_root.resolve()
        if args.receipt and args.caller:
            raise ValueError("portable bundle cannot depend on central caller")
        if not args.receipt and not args.caller:
            raise ValueError("local check requires its enforcing caller")
        members = [Path(__file__).absolute(), Path(index_snapshot.__file__).absolute(),
                   Path(portal.__file__).absolute(), args.registry.absolute(),
                   *(Path(portal.__file__).absolute().parents[1] / "schemas" / name
                     for name in ("manifest.schema.json", "review.schema.json"))]
        if args.caller: members.append(args.caller.absolute())
        bound_members(root, members, args.receipt.absolute() if args.receipt else None)
        if args.receipt:
            bundle = args.receipt.resolve().parent
            if not bundle.is_relative_to(root):
                raise ValueError("bundle outside selected Git checkout")
            if not all(p.resolve().is_relative_to(bundle) for p in members):
                raise ValueError("bundle executor/validator/helper/schema outside receipt")
            if args.registry.resolve() != bundle / "workspaces.json":
                raise ValueError("bundle registry outside receipt")
            receipt = json.loads(args.receipt.read_text())
            if args.project not in receipt.get("project_keys", []):
                raise ValueError("selected project absent from bundle receipt")
            registry_ids = {record["site"]["key"] for record in
                            portal.registry_data(args.registry, validate_paths=False)["workspaces"]
                            if record.get("site")}
            if (not isinstance(receipt.get("project_keys"), list)
                    or registry_ids != set(receipt["project_keys"])):
                raise ValueError("portable selected registry differs from receipt")
        with index_snapshot.indexed_registry(
                args.registry, args.project, override_root=root if args.receipt else None
        ) as (temporary, key):
            state = portal.check(temporary, key)["projects"][key]
        print(json.dumps({"project": key, **state}, sort_keys=True))
        return 0 if state["state"] == "admitted" else 1
    except (OSError, ValueError, KeyError, TypeError, UnicodeDecodeError, portal.PortalError) as error:
        print("docs index: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
