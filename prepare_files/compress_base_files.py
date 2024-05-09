import json
import re
from collections import defaultdict


def sort_files_keys(base_files: dict[str, list]) -> list[str]:
    pattern = re.compile(r'^([a-zA-Z]+):(\d+\.\d+\.\d+|\d+\.\d+)(-[a-zA-Z]+)?$')

    matched = [img for img in base_files.keys() if pattern.match(img)]
    unmatched = [img for img in base_files.keys() if not pattern.match(img)]

    return sorted(matched) + sorted(unmatched)


if __name__ == '__main__':
    compressed_files_full_history = defaultdict(list)
    base_files_full_history = json.load(open('artifacts/base_files_full_history.json', 'r'))

    files_keys = sort_files_keys(base_files_full_history)

    for image_name in files_keys:
        file_hashes = base_files_full_history[image_name]
        for file_hash in file_hashes:
            if not any(file_hash in hash_list for hash_list in compressed_files_full_history.values()):
                compressed_files_full_history[image_name].append(file_hash)

    json.dump(compressed_files_full_history, open('artifacts/base_files_full_history_compressed.json', 'w'), indent=4)
