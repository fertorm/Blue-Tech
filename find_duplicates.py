import os
import hashlib
import shutil
from collections import defaultdict
from pathlib import Path
import uuid


def get_file_hash(filepath):
    """Calculates the MD5 hash of a file."""
    hasher = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError as e:
        print(f"Error reading {filepath}: {e}", flush=True)
        return None


def find_an_move_duplicates(root_dir, quarantine_dir):
    """Scans for duplicates and moves them to quarantine."""
    print(f"Scanning {root_dir}...", flush=True)

    hashes = defaultdict(list)
    files_count = 0

    # Ensure quarantine directory exists
    if not os.path.exists(quarantine_dir):
        os.makedirs(quarantine_dir)
        print(f"Created quarantine directory: {quarantine_dir}", flush=True)

    # First pass: Walk and Hash
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip the quarantine directory itself to avoid re-scanning moved files
        if os.path.abspath(dirpath).startswith(os.path.abspath(quarantine_dir)):
            continue

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            files_count += 1
            if files_count % 100 == 0:
                print(f"Processed {files_count} files...", end="\r", flush=True)

            file_hash = get_file_hash(filepath)
            if file_hash:
                hashes[file_hash].append(filepath)

    print(f"\nScan complete. Found {files_count} files.")

    duplicates_found = 0
    bytes_saved = 0

    # Second pass: Identify and Move
    for file_hash, paths in hashes.items():
        if len(paths) > 1:
            # Sort paths to keep the "original".
            # Strategy: Keep the one with the shortest path length (closest to root),
            # tie-break with alphabetical order.
            paths.sort(key=lambda p: (len(p), p))

            original = paths[0]
            duplicates = paths[1:]

            print(f"Original: {original}")
            for dup in duplicates:
                duplicates_found += 1
                try:
                    size = os.path.getsize(dup)
                    bytes_saved += size

                    # Create target path in quarantine
                    # We flatten the structure or recreate it? Flattening might cause name collisions.
                    # Let's recreate relative structure to avoid collisions.

                    rel_path = os.path.relpath(dup, root_dir)
                    target_path = os.path.join(quarantine_dir, rel_path)
                    target_dir = os.path.dirname(target_path)

                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)

                    # Handle if a file with same name already exists in quarantine (weird edge case)
                    if os.path.exists(target_path):
                        base, ext = os.path.splitext(target_path)
                        target_path = f"{base}_{uuid.uuid4().hex[:6]}{ext}"

                    print(f"  -> Moving duplicate: {dup}")
                    shutil.move(dup, target_path)

                except OSError as e:
                    print(f"  -> Error moving {dup}: {e}", flush=True)

    print(f"\nSummary:", flush=True)
    print(f"  Total files scanned: {files_count}", flush=True)
    print(f"  Duplicates moved: {duplicates_found}", flush=True)
    print(f"  Space reclaimed (approx): {bytes_saved / (1024*1024):.2f} MB", flush=True)
    print(f"  Duplicates are in: {quarantine_dir}", flush=True)


if __name__ == "__main__":
    print("--- Duplicate File Finder ---", flush=True)
    # Default to the path the user originally asked for, for convenience
    default_path = r"E:\Recuperado 10-01-2026\lft_7\Documents"

    user_input = input(
        f"Enter folder path to scan (Press Enter for default: {default_path}): "
    ).strip()

    if user_input:
        target_directory = user_input.strip('"')  # Remove quotes if user copied as path
    else:
        target_directory = default_path

    quarantine_directory = os.path.join(target_directory, "_Duplicates_Quarantine")

    # Safety check
    if not os.path.exists(target_directory):
        print(f"Error: Directory not found: {target_directory}", flush=True)
    else:
        print(f"Target: {target_directory}", flush=True)
        print(f"Quarantine: {quarantine_directory}", flush=True)
        confirm = input("Start scan? (y/n): ").lower()
        if confirm == "y":
            find_an_move_duplicates(target_directory, quarantine_directory)
        else:
            print("Operation cancelled.", flush=True)
