# 📂 Smart File Organizer (CLI)

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Termux%20%7C%20Linux-orange.svg)](https://termux.dev/)
[![Author](https://img.shields.io/badge/author-sosuke--d--mahi-blueviolet.svg)](https://github.com/sosuke-d-mahi)

A high-performance Python CLI tool designed to declutter your environment instantly. Sort messy directories into organized subfolders based on intelligent file-type rules. Perfect for Termux, Linux, and MacOS.

---

## 🚀 Key Features

*   **⚡ Instant Sorting:** Organize thousands of files with a single command.
*   **⏪ Instant Undo:** Rollback the last organization session with `--undo`.
*   **🔍 Dry-Run Support:** Preview changes before they happen using `--dry-run`.
*   **👯 Duplicate Detection:** Prevent redundant files using SHA-256 hash checking.
*   **📅 Auto-Renaming:** Automatically prefix files with creation dates.
*   **📜 Detailed Logging:** All operations are logged to `organizer.log`.

---

## 🛠️ Quick Start

### 1. Installation
```bash
git clone https://github.com/sosuke-d-mahi/smart-file-organizer.git
cd smart-file-organizer
pip install -r requirements.txt
```

### 2. Basic Usage
Organize your Downloads folder:
```bash
python main.py ~/storage/downloads
```

### 3. Advanced Commands
**Preview Changes (Safe Mode):**
```bash
python main.py ~/storage/downloads --dry-run
```

**Undo Last Operation:**
```bash
python main.py --undo
```

---

## 📋 Configuration (`config.json`)

Customize where your files go. The tool automatically maps extensions to folders defined here.

```json
{
  "rules": {
    "Images": [".jpg", ".png", ".jpeg", ".webp", ".gif"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx"],
    "Audio": [".mp3", ".wav", ".flac"],
    "Archives": [".zip", ".rar", ".7z", ".tar.gz"]
  },
  "target_base": "./Organized"
}
```

---

## 🗺️ Roadmap

- [x] **Dry-Run Mode:** `--dry-run` flag to preview changes safely.
- [x] **Undo Feature:** Instantly rollback moves with `--undo`.
- [x] **Duplicate Detection:** Smart hash checking (SHA-256) to prevent redundant files.
- [x] **File Renaming:** Auto-rename patterns based on date prefixes.

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for new features or find a bug:
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License
Distributed under the **MIT License**. See `LICENSE` for more information.

---
Developed with ❤️ by [sosuke-d-mahi](https://github.com/sosuke-d-mahi)
