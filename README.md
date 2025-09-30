<p align="center">
  <img src="https://img.shields.io/badge/zero%20deps-✔-00E5FF?style=for-the-badge">
  <img src="https://img.shields.io/badge/one%20file-1-777?style=for-the-badge">
  <img src="https://img.shields.io/badge/offline-works-00E5FF?style=for-the-badge">
</p>

<h1 align="center">gitignore-doctor</h1>
<p align="center">
  A single-file, zero-deps CLI that <b>scans your repo</b> and prescribes the perfect <code>.gitignore</code> with explanations.
</p>

---

## Why?

Getting `.gitignore` right is annoying:
- You add Node + Python + Docker + OS junk… and forget half of it.
- Web generators don’t know your actual tree.
- Existing templates don’t explain <i>why</i> lines exist.

**gitignore-doctor** inspects your repo, detects stacks, merges the correct rules, warns about risky files already tracked, and writes a clean, commented `.gitignore`.

---

## Features

- 🔍 **Auto-detects stacks:** Node, Python, Go, Rust, Java, C#, Swift, Docker, VSCode/JetBrains, macOS/Windows/Linux cruft.
- 🧪 **Dry-run by default:** shows what it would write and why.
- 🧠 **Explains** each rule (commented sections).
- 🧹 **Warns** about secrets/binaries already tracked.
- ⚡ **No dependencies**, instant startup, offline.
- 🧩 **Merges** multiple ecosystems cleanly (no duplicate noise).

---

## Quickstart

```bash
# in any repo
python ./doctor.py             # preview the managed block
python ./doctor.py --write     # write/update .gitignore (safe: preserves your custom content)
python ./doctor.py --risks     # show tracked secrets/binaries
python ./doctor.py --strict    # exit non-zero if risks found (great for CI)
```

---

<p align="center">
  <img
    alt="gitignore-doctor visits"
    src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.countapi.xyz%2Fhit%2Fxryv.gitignore-doctor%2Fvisits&query=value&label=visits&color=00E5FF&labelColor=777&cacheSeconds=300"
  />
</p>

<p align="center">
  <sub>👣 If this number ticked, another dev just dropped by. Be the reason it moves again.</sub>
</p>
