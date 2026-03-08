import os
import time

from pc_storage_history.scanner import FastScanner


def main() -> None:
    """
    Test the FastScanner performance.
    """
    target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    print(f"Scanning directory: {target_dir}")

    scanner = FastScanner(target_dir)

    start_time = time.time()
    file_count = 0
    dir_count = 0
    total_size = 0

    for node in scanner.scan():
        if node.is_dir:
            dir_count += 1
        else:
            file_count += 1
            total_size += node.size

    end_time = time.time()
    duration = end_time - start_time

    print(f"Scan complete in {duration:.4f} seconds.")
    print(f"Found {dir_count} directories and {file_count} files.")
    print(f"Total size: {total_size / (1024 * 1024):.2f} MB")


if __name__ == "__main__":
    main()
