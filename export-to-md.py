import os

# Project root (change if needed)
PROJECT_ROOT = "."

# Output file
OUTPUT_FILE = "codebase.md"

# Extensions to exclude (files with these extensions will be skipped)
EXCLUDE_EXTS = (".pyc", ".pyo", ".log", ".tmp", ".sqlite3", ".db", ".lock")

# Directories to exclude
EXCLUDE_DIRS = {".git", "__pycache__", ".venv", "node_modules", ".pytest_cache"}

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    out.write("# Project Codebase\n\n")
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Remove excluded directories from traversal
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        # Write folder name
        rel_path = os.path.relpath(root, PROJECT_ROOT)
        if rel_path == ".":
            rel_path = "Root"
        out.write(f"\n\n## 📂 {rel_path}\n\n")

        for file in sorted(files):
            # Skip files with excluded extensions
            if any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                continue
            filepath = os.path.join(root, file)
            ext = filepath.split(".")[-1] if "." in file else ""
            out.write(f"\n### 📄 {file}\n\n")
            out.write(f"```{ext}\n")
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    out.write(f.read())
            except Exception as e:
                out.write(f"⚠️ Could not read file: {e}")
            out.write("\n```\n\n")

print(f"✅ Codebase exported to {OUTPUT_FILE}. Now run:")
print("   pandoc codebase.md -o codebase.pdf   # convert to PDF")
