import os
import shutil
import json
import logging
import hashlib
from datetime import datetime

class FileOrganizer:
    HISTORY_FILE = ".organizer_history"
    SESSION_MARKER = "=== SESSION START ==="

    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.rules = self.config.get("rules", {})
        self.target_base = os.path.expanduser(self.config.get("target_base", "~/Organized"))
        
        # Setup Logging with specific level and format
        self.logger = logging.getLogger("FileOrganizer")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.FileHandler("organizer.log")
            handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            self.logger.addHandler(handler)

    def _load_config(self, path):
        """Loads configuration with fallback to defaults."""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "rules": {
                    "Images": [".jpg", ".png", ".jpeg"],
                    "Documents": [".pdf", ".txt", ".docx"],
                    "Archives": [".zip", ".rar"]
                },
                "target_base": "~/Organized"
            }

    def _calculate_hash(self, file_path):
        """Calculate SHA-256 hash using streaming to avoid memory spikes."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except IOError:
            return None

    def _log_history(self, source, destination, is_start=False):
        """Append move operations to history file with session markers."""
        with open(self.HISTORY_FILE, "a") as f:
            if is_start:
                f.write(f"{self.SESSION_MARKER} {datetime.now()}\n")
            f.write(f"{source}|{destination}\n")

    def undo(self):
        """Rolls back ONLY the most recent organization session."""
        if not os.path.exists(self.HISTORY_FILE):
            print("❌ No history found to undo.")
            return

        with open(self.HISTORY_FILE, "r") as f:
            lines = f.readlines()

        if not lines:
            print("❌ History is empty.")
            return

        # Find the start of the last session
        last_session_idx = -1
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].startswith(self.SESSION_MARKER):
                last_session_idx = i
                break

        if last_session_idx == -1:
            print("⚠️ No session markers found. Undoing everything...")
            session_lines = lines
        else:
            session_lines = lines[last_session_idx+1:]

        print(f"🔄 Undoing last session ({len(session_lines)} files)...")
        
        remaining_lines = lines[:last_session_idx] if last_session_idx != -1 else []
        
        for line in reversed(session_lines):
            if "|" not in line: continue
            try:
                src, dest = line.strip().split("|")
                if os.path.exists(dest):
                    os.makedirs(os.path.dirname(src), exist_ok=True)
                    shutil.move(dest, src)
                    print(f"  ⏪ Restored: {os.path.basename(src)}")
            except Exception as e:
                print(f"  ⚠️ Failed to restore {line.strip()}: {e}")

        # Update history file by removing the undone session
        if remaining_lines:
            with open(self.HISTORY_FILE, "w") as f:
                f.writelines(remaining_lines)
        else:
            if os.path.exists(self.HISTORY_FILE):
                os.remove(self.HISTORY_FILE)
        
        print("✅ Undo complete.")

    def run(self, source_folder, dry_run=False, skip_duplicates=False, rename_mode="none"):
        """Primary execution loop for file organization."""
        source_folder = os.path.abspath(os.path.expanduser(source_folder))
        moved_count = 0
        skipped_count = 0

        print(f"{' [DRY RUN] ' if dry_run else ''}🚀 Organizing: {source_folder}")
        self.logger.info(f"Session Start: {source_folder} (Dry: {dry_run}, Skip: {skip_duplicates}, Rename: {rename_mode})")

        if not dry_run:
            self._log_history("", "", is_start=True)

        for item in os.listdir(source_folder):
            item_path = os.path.join(source_folder, item)

            if os.path.isfile(item_path) and not item.startswith("."):
                ext = os.path.splitext(item)[1].lower()
                
                for category, extensions in self.rules.items():
                    if ext in extensions:
                        dest_dir = os.path.join(self.target_base, category)
                        
                        # Generate New Filename
                        new_name = item
                        if rename_mode == "date":
                            mtime = os.path.getmtime(item_path)
                            date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                            new_name = f"{date_str}_{item}"

                        dest_path = os.path.join(dest_dir, new_name)
                        
                        # Collision Detection
                        if os.path.exists(dest_path):
                            if skip_duplicates:
                                if self._calculate_hash(item_path) == self._calculate_hash(dest_path):
                                    print(f"  ⏭️  Skipping duplicate: {item}")
                                    self.logger.info(f"Skipped duplicate: {item}")
                                    skipped_count += 1
                                    break
                            else:
                                # Resolve name conflict by appending timestamp
                                timestamp = datetime.now().strftime("%H%M%S")
                                name, ext_part = os.path.splitext(new_name)
                                new_name = f"{name}_{timestamp}{ext_part}"
                                dest_path = os.path.join(dest_dir, new_name)

                        if not dry_run:
                            try:
                                os.makedirs(dest_dir, exist_ok=True)
                                self._log_history(item_path, dest_path)
                                shutil.move(item_path, dest_path)
                                self.logger.info(f"Moved: {item_path} -> {dest_path}")
                            except Exception as e:
                                print(f"  ❌ Failed to move {item}: {e}")
                                self.logger.error(f"Move failed: {item} -> {e}")
                                break
                        
                        status = "would be moved" if dry_run else "moved"
                        print(f"  ➡️  {item} {status} to {category}/{new_name}")
                        moved_count += 1
                        break
        
        print(f"\n✅ Finished. Moved: {moved_count}, Skipped: {skipped_count}")
