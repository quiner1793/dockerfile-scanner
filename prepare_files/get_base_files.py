import json
import os
import re
from pprint import pprint

base_files = {}

base_dir = "/home/quiner/innopolis/thesis/repo-info/repos"
for dir_name in os.listdir(base_dir):
    tag_file = os.path.join(base_dir, dir_name, "tag-details.md")
    if os.path.isfile(tag_file):
        temp_set = set()
        pattern = re.compile(r'```dockerfile\n# (.+)\nADD file:(.+) in / \n# (.+)\nCMD \["(.+)"]\n```')

        # Open the file and search for snippets that match the pattern
        with open(tag_file, 'r') as file:
            data = file.read()
            matches = pattern.findall(data)

        # Extract file line from the matched snippets
        for match in matches:
            fileline = match[1]
            temp_set.add(fileline)

        if len(temp_set) > 0:
            base_files[dir_name] = list(temp_set)

pprint(base_files)
json.dump(base_files, open('../artifacts/base_files2.json', 'w'), indent=4)
