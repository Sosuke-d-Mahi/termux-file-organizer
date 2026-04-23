import os
import shutil
import json
import logging
import hashlib
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

    def _calculate_hash(self, file_path):
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

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

    def run(self, source_folder, dry_run=False, skip_duplicates=False, rename_mode="none"):
        source_folder = os.path.expanduser(source_folder)
        moved_count = 0
        skipped_count = 0

        print(f"{' [DRY RUN] ' if dry_run else ''}🚀 Organizing: {source_folder}")
        logging.info(f"Starting session in {source_folder} (Dry run: {dry_run}, Skip Duplicates: {skip_duplicates}, Rename: {rename_mode})")

        for item in os.listdir(source_folder):
            item_path = os.path.join(source_folder, item)

            if os.path.isfile(item_path) and not item.startswith("."):
                ext = os.path.splitext(item)[1].lower()
                
                for category, extensions in self.rules.items():
                    if ext in extensions:
                        dest_dir = os.path.join(self.target_base, category)
                        
                        # Handle Renaming
                        new_name = item
                        if rename_mode == "date":
                            mtime = os.path.getmtime(item_path)
                            date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                            new_name = f"{date_str}_{item}"

                        dest_path = os.path.join(dest_dir, new_name)
                        
                        # Duplicate Detection
                        if skip_duplicates and os.path.exists(dest_path):
                            if self._calculate_hash(item_path) == self._calculate_hash(dest_path):
                                print(f"  ⏭️  Skipping duplicate: {item}")
                                logging.info(f"Skipped duplicate: {item}")
                                skipped_count += 1
                                break

                        if not dry_run:
                            os.makedirs(dest_dir, exist_ok=True)
                            self._log_history(item_path, dest_path)
                            shutil.move(item_path, dest_path)
                            logging.info(f"Moved: {item_path} -> {dest_path}")
                        
                        status = "would be moved" if dry_run else "moved"
                        print(f"  ➡️  {item} {status} to {category}/{new_name}")
                        moved_count += 1
                        break
        
        print(f"\n✅ Finished. Moved: {moved_count}, Skipped: {skipped_count}")
