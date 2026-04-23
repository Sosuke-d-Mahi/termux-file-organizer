# 📂 Smart File Organizer (CLI)

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Termux%20%7C%20Linux-orange.svg)](https://termux.dev/)
[![Author](https://img.shields.io/badge/author-sosuke--d--mahi-blueviolet.svg)](https://github.com/sosuke-d-mahi)

A high-performance Python CLI tool designed to declutter your Termux or Linux environment instantly. Sort messy directories into organized subfolders based on intelligent file-type rules.

---

## 🚀 Key Features

*   **⚡ Instant Sorting:** Organize thousands of files with a single command.
*   **🧠 Config-Driven:** Fully customizable rules via `config.json`.
*   **🔍 Dry-Run Support:** Preview changes before they happen (Roadmap).
*   **🧹 Deep Clean:** Designed specifically for chaotic `Downloads` folders.
*   **📱 Termux Optimized:** Lightweight and efficient for mobile environments.

---

## 🛠️ Quick Start

### 1. Environment Setup
Ensure you have Python and Git installed in Termux:
```bash
pkg update && pkg upgrade -y
pkg install git python -y
termux-setup-storage
```

### 2. Installation
```bash
git clone https://github.com/sosuke-d-mahi/smart-file-organizer.git
cd smart-file-organizer
pip install -r requirements.txt
```

### 🧠 Example Usage

### Standard Organize
```bash
python main.py ~/storage/downloads
```

### Dry Run (Preview)
```bash
python main.py ~/storage/downloads --dry-run
```

### Undo Last Session
```bash
python main.py --undo
```

### Skip Duplicates
```bash
python main.py ~/storage/downloads --skip-duplicates
```

### Auto-Rename (Date Prefix)
```bash
python main.py ~/storage/downloads --rename date
```

---

## 📋 Configuration (`config.json`)

Define your own categories and extensions. The tool uses this map to determine where files should go.

```json
{
  "rules": {
    "Images": [".jpg", ".png", ".jpeg", ".webp", ".gif"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx"],
    "Audio": [".mp3", ".wav", ".flac"],
    "Archives": [".zip", ".rar", ".7z", ".tar.gz"]
  },
  "target_base": "~/storage/shared/Organized"
}
```

---

## 💻 Core Implementation

### `main.py`
```python
import argparse
import os
from organizer import FileOrganizer

def main():
    parser = argparse.ArgumentParser(description="Smart File Organizer for Termux/Linux")
    parser.add_argument("path", nargs="?", help="The directory to organize")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without moving files")
    parser.add_argument("--undo", action="store_true", help="Rollback the last organization session")
    parser.add_argument("--skip-duplicates", action="store_true", help="Don't move files if a duplicate already exists in destination")
    parser.add_argument("--rename", choices=["date", "none"], default="none", help="Rename files (e.g., prefix with date)")
    parser.add_argument("--config", default="config.json", help="Path to custom config.json")
    
    args = parser.parse_args()
    organizer = FileOrganizer(args.config)

    if args.undo:
        organizer.undo()
        return

    if not args.path:
        print("❌ Error: Please specify a folder path or use --undo.")
        return

    if not os.path.exists(args.path):
        print(f"❌ Error: The path '{args.path}' does not exist.")
        return

    organizer.run(args.path, dry_run=args.dry_run, skip_duplicates=args.skip_duplicates, rename_mode=args.rename)

if __name__ == "__main__":
    main()
```

### `organizer.py`
```python
import os
import shutil
import json
import logging
from datetime import datetime

class FileOrganizer:
    HISTORY_FILE = ".organizer_history"

    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.rules = self.config.get("rules", {})
        self.target_base = os.path.expanduser(self.config.get("target_base", "~/Organized"))
        
        # Setup Logging
        logging.basicConfig(
            filename="organizer.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def _load_config(self, path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return {"rules": {"Docs": [".pdf", ".txt"]}, "target_base": "~/Organized"}

    def _log_history(self, source, destination):
        with open(self.HISTORY_FILE, "a") as f:
            f.write(f"{source}|{destination}\n")

    def undo(self):
        if not os.path.exists(self.HISTORY_FILE):
            print("❌ No history found to undo.")
            return

        with open(self.HISTORY_FILE, "r") as f:
            lines = f.readlines()

        if not lines:
            print("❌ History is empty.")
            return

        print("🔄 Undoing last session...")
        for line in reversed(lines):
            try:
                src, dest = line.strip().split("|")
                if os.path.exists(dest):
                    os.makedirs(os.path.dirname(src), exist_ok=True)
                    shutil.move(dest, src)
                    print(f"  ⏪ Restored: {os.path.basename(src)}")
            except Exception as e:
                print(f"  ⚠️ Failed to restore {line}: {e}")

        os.remove(self.HISTORY_FILE)
        print("✅ Undo complete.")

    def run(self, source_folder, dry_run=False):
        source_folder = os.path.expanduser(source_folder)
        moved_count = 0

        print(f"{' [DRY RUN] ' if dry_run else ''}🚀 Organizing: {source_folder}")
        logging.info(f"Starting session in {source_folder} (Dry run: {dry_run})")

        for item in os.listdir(source_folder):
            item_path = os.path.join(source_folder, item)

            if os.path.isfile(item_path):
                ext = os.path.splitext(item)[1].lower()
                
                for category, extensions in self.rules.items():
                    if ext in extensions:
                        dest_dir = os.path.join(self.target_base, category)
                        dest_path = os.path.join(dest_dir, item)
                        
                        if not dry_run:
                            os.makedirs(dest_dir, exist_ok=True)
                            self._log_history(item_path, dest_path)
                            shutil.move(item_path, dest_path)
                            logging.info(f"Moved: {item_path} -> {dest_path}")
                        
                        print(f"  ➡️  {item} {'would be moved' if dry_run else 'moved'} to {category}/")
                        moved_count += 1
                        break
        
        print(f"\n✅ Finished. Total files processed: {moved_count}")
```

---

## 🗺️ Roadmap

- [x] **Dry-Run Mode:** `--dry-run` flag to preview changes safely.
- [x] **Undo Feature:** Instantly rollback moves with `--undo`.
- [x] **Duplicate Detection:** Smart hash checking (SHA-256) via `--skip-duplicates`.
- [x] **File Renaming:** Auto-rename with date prefixes using `--rename date`.

---

## 🤝 Contributing & Support

Contributions are what make the open-source community amazing. Feel free to fork, open issues, or submit PRs.

⭐ **Enjoying the tool?** Give this repo a star!

---

## 📜 License
Distributed under the **MIT License**. See `LICENSE` for more information.
