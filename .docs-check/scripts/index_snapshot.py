"""Read-only, minimal Git-index filesystem view for the existing portal validator."""
from contextlib import contextmanager
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tempfile

import portal


def _git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise ValueError("Git index unavailable: " + result.stderr.decode(errors="replace").strip())
    return result.stdout


def _blob(root, oid):
    return _git(root, "cat-file", "blob", oid)


def _index(root):
    result = {}
    for row in _git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not row:
            continue
        head, raw = row.split(b"\t", 1)
        mode, oid, stage = head.decode("ascii").split()
        if stage != "0":
            raise ValueError("unmerged Git index")
        name = raw.decode("utf-8")
        path = PurePosixPath(name)
        if (not name or path.is_absolute() or any(part in (".", "..", "") for part in name.split("/"))
                or "\\" in name):
            raise ValueError("unsafe index path")
        result[name] = (mode, oid)
    return result


def _is_private(name, public_sources=()):
    # Use the same record-scoped safe-source policy as the canonical validator.
    # Other omitted public paths still need name-only metadata for classification.
    return not portal.allowed_source(name, public_sources) or any(
        part in {".git", ".venv", "node_modules", "__pycache__", "secrets", "private", "runtime", "logs"}
        for part in PurePosixPath(name).parts)


def _within(name, prefix):
    return name == prefix or name.startswith(prefix.rstrip("/") + "/")


def _selected_git_root(record, override):
    original = Path(record["root"])
    if record.get("git_root"):
        original_git = Path(record["git_root"])
    elif original.exists():
        original_git = Path(_git(original, "rev-parse", "--show-toplevel").decode().strip())
    else:
        raise ValueError("relocated nested root requires declared git_root")
    if not original.is_relative_to(original_git):
        raise ValueError("project root outside declared Git worktree")
    if original.exists() and not override:
        actual_original = Path(_git(original, "rev-parse", "--show-toplevel").decode().strip())
        if actual_original != original_git:
            raise ValueError("declared Git root differs from actual worktree")
    root = Path(override).resolve() if override else original_git
    actual = Path(_git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    if actual != root.resolve():
        raise ValueError("override_root must be the selected Git worktree root")
    return root, original_git, original.relative_to(original_git)


@contextmanager
def indexed_registry(registry_path: Path, project_key: str, override_root: Path | None = None):
    """Yield a disposable registry whose selected project reads index bytes only.

    An external registry remains a trusted local policy input, not a claim that
    its bytes are staged in a different repository. The caller validates through
    portal.check and decides whether pending/invalid results block submission.
    """
    registry_path = Path(registry_path).resolve()
    data = portal.registry_data(registry_path, validate_paths=override_root is None)
    selected = next((row for row in data["workspaces"] if row.get("site", {}).get("key") == project_key), None)
    if selected is None:
        raise ValueError("unknown selected project key")
    root, original_git, offset = _selected_git_root(selected, override_root)
    index = _index(root)
    executing = Path(portal.__file__).resolve()
    schemas = executing.parents[1] / "schemas"
    policies = ((registry_path, "registry"), (executing, "validator"),
                (schemas / "manifest.schema.json", "manifest schema"),
                (schemas / "review.schema.json", "review schema"))
    for policy_path, label in policies:
        if policy_path.is_relative_to(root):
            name = policy_path.relative_to(root).as_posix()
        elif not override_root and policy_path.is_relative_to(original_git):
            name = policy_path.relative_to(original_git).as_posix()
        else:
            continue  # central policy outside this worktree is a separate trust boundary
        policy = index.get(name)
        if not policy or policy[0] not in ("100644", "100755") or _blob(root, policy[1]) != policy_path.read_bytes():
            raise ValueError("indexed " + label + " policy differs from executing bytes")
    prefix = offset.as_posix() + "/" if offset.parts else ""
    def name_for(relative):
        return prefix + relative
    manifest_name = name_for(selected["site"]["verification"] + "/manifest.json")
    manifest_item = index.get(manifest_name)
    manifest = None
    if manifest_item:
        if manifest_item[0] not in ("100644", "100755"):
            raise ValueError("nonregular indexed manifest")
        manifest = json.loads(_blob(root, manifest_item[1]))
    excluded = [item["path"] for item in manifest.get("excluded", [])] if manifest else []
    for path in excluded:
        portal.relpath(path, path.endswith("/"), excluded=True)
    nested = [Path(row["root"]).relative_to(selected["root"]).as_posix() + "/" for row in data["workspaces"]
              if row is not selected and Path(row["root"]).is_relative_to(Path(selected["root"]))]
    docs = selected["site"]["source"] + "/"
    declarations = [item["path"] for item in manifest.get("sources", [])] if manifest else []
    public_sources = selected["site"].get("public_source_paths", {})
    for path in declarations:
        portal.relpath(path, path.endswith("/"), public_sources=public_sources)
    with tempfile.TemporaryDirectory(prefix="docs-index-") as temporary:
        shadow_git = Path(temporary)
        shadow = shadow_git / offset
        shadow.mkdir(parents=True, exist_ok=True)
        for name, (mode, oid) in index.items():
            if not name.startswith(prefix):
                continue
            relative = name.removeprefix(prefix)
            receipt = relative in (selected["site"]["verification"] + "/manifest.json", selected["site"]["verification"] + "/review.json")
            if portal.excluded_path(relative, excluded) and not receipt:
                continue
            if any(_within(relative, pattern) for pattern in nested):
                continue
            if _is_private(relative, public_sources) and relative not in (".gitignore",):
                continue
            if (relative == ".gitignore" or relative.startswith((".github/workflows/", ".githooks/", ".docs-check/"))) and not any(
                    _within(relative, entry) if entry.endswith("/") else relative == entry for entry in declarations):
                raise ValueError("unclassified indexed policy path: " + relative)
            if relative.startswith(docs) and any(part in portal.BLOCKED for part in PurePosixPath(relative[len(docs):]).parts):
                continue
            declared = any(_within(relative, entry) if entry.endswith("/") else relative == entry for entry in declarations)
            handbook = relative.startswith(docs)
            receipt = relative in (selected["site"]["verification"] + "/manifest.json", selected["site"]["verification"] + "/review.json")
            if mode not in ("100644", "100755"):
                raise ValueError("symlink or nonregular meaningful index entry: " + relative)
            # An unclassified file only needs a name to make portal reject it.
            content = _blob(root, oid) if (declared or handbook or receipt) else b"UNCLASSIFIED_INDEX_PATH"
            target = shadow / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        relocated = dict(selected)
        relocated["root"] = str(shadow)
        if relocated.get("git_root"):
            relocated["git_root"] = str(shadow_git)
        for field in ("docs", "entry"):
            if selected.get(field) and Path(selected[field]).is_relative_to(Path(selected["root"])):
                relocated[field] = str(shadow / Path(selected[field]).relative_to(selected["root"]))
        # Site source and verification are root-relative; preserve them verbatim.
        records = [relocated]
        for row in data["workspaces"]:
            if row is selected or not Path(row["root"]).is_relative_to(Path(selected["root"])):
                continue
            records.append({"id": row["id"], "root": str(shadow / Path(row["root"]).relative_to(selected["root"])),
                            "title": row["title"], "kind": row["kind"], "reason": row.get("reason", "nested independent owner")})
        registry = Path(tempfile.mkdtemp(prefix="docs-policy-")) / "registry.json"
        try:
            registry.write_text(json.dumps({"schema": 1, "workspaces": records}))
            yield registry, project_key
        finally:
            shutil.rmtree(registry.parent)
