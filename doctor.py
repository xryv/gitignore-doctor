#!/usr/bin/env python3
# gitignore-doctor — single-file, zero-deps .gitignore generator
# License: MIT

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(os.getcwd())

# ---------- helpers ----------
def is_git_repo() -> bool:
    return (ROOT / ".git").exists()

def git_tracked_files():
    if not is_git_repo():
        return []
    try:
        out = subprocess.check_output(
            ["git", "ls-files"],
            cwd=ROOT,
            stderr=subprocess.DEVNULL
        )
        return out.decode().splitlines()
    except Exception:
        return []

def has_any(exts=None, names=None):
    exts = exts or []
    names = names or []
    for dirpath, _, filenames in os.walk(ROOT):
        # skip heavy/irrelevant dirs
        p = dirpath.replace("\\", "/")
        if "/.git" in p or "/node_modules" in p or "/dist" in p or "/build" in p or "/target" in p:
            continue
        for f in filenames:
            fl = f.lower()
            if any(fl.endswith(e) for e in exts):
                return True
            if f in names:
                return True
    return False

def file_exists_any(paths):
    return any((ROOT / p).exists() for p in paths)

def dir_exists_any(paths):
    return any((ROOT / p).is_dir() for p in paths)

# ---------- detectors ----------
def detect_node():
    return file_exists_any(["package.json"]) or dir_exists_any(["node_modules"]) or has_any(exts=[".ts",".tsx",".js"])

def detect_python():
    return file_exists_any(["pyproject.toml","requirements.txt","Pipfile"]) or has_any(exts=[".py"])

def detect_go():
    return file_exists_any(["go.mod","go.sum"]) or has_any(exts=[".go"])

def detect_rust():
    return file_exists_any(["Cargo.toml"]) or has_any(exts=[".rs"])

def detect_java():
    return file_exists_any(["pom.xml","build.gradle","gradle.properties"]) or has_any(exts=[".java",".jar",".war",".class"])

def detect_csharp():
    return has_any(exts=[".cs",".csproj",".sln"])

def detect_swift():
    return has_any(exts=[".swift"]) or file_exists_any(["Package.swift"])

def detect_docker():
    return file_exists_any(["Dockerfile"]) or file_exists_any(["docker-compose.yml","docker-compose.yaml"])

def detect_editors():
    return True  # always useful: .vscode, .idea, etc.

def detect_os_cruft():
    return True  # always useful: .DS_Store, Thumbs.db, etc.

def detect_platforms():
    stacks = []
    if detect_node(): stacks.append("node")
    if detect_python(): stacks.append("python")
    if detect_go(): stacks.append("go")
    if detect_rust(): stacks.append("rust")
    if detect_java(): stacks.append("java")
    if detect_csharp(): stacks.append("csharp")
    if detect_swift(): stacks.append("swift")
    if detect_docker(): stacks.append("docker")
    if detect_editors(): stacks.append("editors")
    if detect_os_cruft(): stacks.append("os")
    # stable nice order
    order = ["node","python","go","rust","java","csharp","swift","docker","editors","os"]
    return [s for s in order if s in stacks]

# ---------- templates ----------
TEMPLATES = {
    "node": {
        "title": "Node (build artifacts)",
        "rules": [
            "node_modules/",
            "npm-debug.log*",
            "yarn-debug.log*",
            "yarn-error.log*",
            "pnpm-debug.log*",
            "dist/",
            "build/",
            ".next/",
            ".nuxt/",
            ".svelte-kit/",
            ".cache/",
            "*.tgz",
        ],
    },
    "python": {
        "title": "Python (bytecode & venv)",
        "rules": [
            "__pycache__/",
            "*.py[cod]",
            "*$py.class",
            ".venv/",
            "venv/",
            "env/",
            "*.egg-info/",
            ".pytest_cache/",
            ".mypy_cache/",
            ".ruff_cache/",
        ],
    },
    "go": {
        "title": "Go (build & modules)",
        "rules": [
            "bin/",
            "*.exe",
            "*.test",
            "vendor/",
        ],
    },
    "rust": {
        "title": "Rust (cargo target)",
        "rules": [
            "target/",
            "**/*.rs.bk",
        ],
    },
    "java": {
        "title": "Java (build output)",
        "rules": [
            "target/",
            "out/",
            "build/",
            "*.class",
            "*.jar",
            "*.war",
            ".gradle/",
            ".idea/",
        ],
    },
    "csharp": {
        "title": "C# (.NET build)",
        "rules": [
            "bin/",
            "obj/",
            "*.user",
            "*.suo",
            ".vs/",
        ],
    },
    "swift": {
        "title": "Swift / Xcode",
        "rules": [
            "DerivedData/",
            "*.xcworkspace/xcuserdata/",
            "*.xcuserdata/",
            "Pods/",
            ".build/",
        ],
    },
    "docker": {
        "title": "Docker",
        "rules": [
            ".docker/",
            "**/.env.local",
        ],
    },
    "editors": {
        "title": "Editors / IDEs",
        "rules": [
            ".vscode/",
            ".idea/",
            "*.iml",
        ],
    },
    "os": {
        "title": "OS cruft (macOS/Windows/Linux)",
        "rules": [
            ".DS_Store",
            "Thumbs.db",
            "Desktop.ini",
            "$RECYCLE.BIN/",
        ],
    },
}

RISKY_HINTS = {
    "secrets": [
        ".env", ".env.local", ".env.production", "id_rsa", "id_dsa",
        "credentials.json", "serviceAccountKey.json"
    ],
    "binaries_ext": [
        ".exe",".dll",".so",".dylib",".bin",".o",".a",".lib",
        ".zip",".tar",".gz",".7z",".rar",".pdf"
    ]
}

# ---------- core ----------
DOCTOR_BEGIN = "# >>> gitignore-doctor:begin"
DOCTOR_END   = "# >>> gitignore-doctor:end"

def generate_gitignore(stacks, explain=True):
    lines = []
    used = set()
    for s in stacks:
        tpl = TEMPLATES.get(s)
        if not tpl:
            continue
        if explain:
            lines.append(f"### {tpl['title']}")
        for r in tpl["rules"]:
            if r not in used:
                lines.append(r)
                used.add(r)
        if explain:
            lines.append("")  # blank line
    result = "\n".join(lines).rstrip() + "\n"
    return result

def merge_with_existing(new_block: str, existing_text: str) -> str:
    """
    Preserve user content outside our managed block.
    We replace only the section between DOCTOR_BEGIN/DOCTOR_END.
    If no block exists, append ours at the end with markers.
    """
    if DOCTOR_BEGIN in existing_text and DOCTOR_END in existing_text:
        before = existing_text.split(DOCTOR_BEGIN)[0]
        after  = existing_text.split(DOCTOR_END)[-1]
        return before + DOCTOR_BEGIN + "\n" + new_block + DOCTOR_END + after
    else:
        base = existing_text.rstrip() + "\n\n" if existing_text.strip() else ""
        return base + DOCTOR_BEGIN + "\n" + new_block + DOCTOR_END + "\n"

def scan_risks(tracked):
    risky = []
    for f in tracked:
        name = os.path.basename(f)
        low = f.lower()
        if any(name == s or low.endswith(s.lower()) for s in RISKY_HINTS["secrets"]):
            risky.append(("secret", f))
        if any(low.endswith(ext) for ext in RISKY_HINTS["binaries_ext"]):
            risky.append(("binary", f))
    return risky

# ---------- cli ----------
def main():
    import argparse

    parser = argparse.ArgumentParser(description=".gitignore doctor — prescribes the right ignore file")
    parser.add_argument("--write", action="store_true", help="Write .gitignore (otherwise dry-run preview)")
    parser.add_argument("--risks", action="store_true", help="List risky tracked files (secrets/binaries)")
    parser.add_argument("--only", nargs="+", default=[], help="Force specific stacks (node python go rust java csharp swift docker editors os)")
    parser.add_argument("--no-explain", action="store_true", help="Omit comments/rationales in the generated file")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if risky tracked files are found")
    args = parser.parse_args()

    stacks = args.only if args.only else detect_platforms()
    if not stacks:
        stacks = ["editors", "os"]

    content = generate_gitignore(stacks, explain=not args.no_explain)

    # Risks
    if args.risks or args.strict:
        tracked = git_tracked_files()
        risks = scan_risks(tracked)
        if risks:
            print("Tracked risky files detected:")
            for kind, f in risks:
                print("  - [{}] {}".format(kind, f))
            if args.strict:
                sys.exit(2)
        else:
            print("No tracked risky files detected.")
        print("")

    # Write or preview
    if args.write:
        existing = Path(".gitignore").read_text(encoding="utf-8") if Path(".gitignore").exists() else ""
        merged = merge_with_existing(content, existing)
        Path(".gitignore").write_text(merged, encoding="utf-8")
        print("Wrote .gitignore (managed block between markers).")
        print("Markers:", DOCTOR_BEGIN, "…", DOCTOR_END)
    else:
        print("Detected stacks: {}".format(", ".join(stacks)))
        print("Would write .gitignore block:\n")
        print(DOCTOR_BEGIN)
        print(content.rstrip())
        print(DOCTOR_END)

if __name__ == "__main__":
    main()
