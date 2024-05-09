import json
import pprint
from collections import defaultdict

# if __name__ == '__main__':
#     compressed_files_full_history = defaultdict(list)
#     base_files_full_history = json.load(open('artifacts/base_files_full_history.json', 'r'))
#
#     for image_name, file_hashes in base_files_full_history.items():
#         for file_hash in file_hashes:
#             if not any(file_hash in hash_list for hash_list in compressed_files_full_history.values()):
#                 compressed_files_full_history[image_name].append(file_hash)
#
#     json.dump(compressed_files_full_history, open('artifacts/base_files_full_history_compressed.json', 'w'), indent=4)


if __name__ == '__main__':
    compressed_files_full_history = defaultdict(list)
    base_files_full_history = json.load(open('../artifacts/base_files_full_history.json', 'r'))

    for image_name, file_hashes in base_files_full_history.items():
        print(image_name)
        for file_hash in file_hashes:
            count = 0
            for hash_list in base_files_full_history.values():
                if file_hash in hash_list:
                    count += 1
            if count == 1:
                compressed_files_full_history[image_name].append(file_hash)
    pprint.pprint(compressed_files_full_history)
