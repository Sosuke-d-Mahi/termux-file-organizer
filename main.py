import argparse
import os
from organizer import FileOrganizer

def main():
    parser = argparse.ArgumentParser(description="Smart File Organizer for Termux/Linux")
    parser.add_argument("path", nargs="?", help="The directory to organize")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without moving files")
    parser.add_argument("--undo", action="store_true", help="Rollback the last organization session")
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

    organizer.run(args.path, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
