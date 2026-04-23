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
                    # Ensure the source directory exists
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
                
                found_match = False
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
                        found_match = True
                        break
        
        print(f"\n✅ Finished. Total files processed: {moved_count}")
