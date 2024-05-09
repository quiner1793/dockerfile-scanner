import json
import os
import re
import subprocess

dockerfile_pattern = re.compile(r'```dockerfile\n# (.+)\nADD file:(.+) in / \n# (.+)\nCMD \["(.+)"]\n```')
section_name_pattern = re.compile(r"`(.*?)`")
header_pattern = re.compile(r'^(##+)\s+(.*)', re.MULTILINE)


def get_base_files(dir_path: str) -> dict[str, list]:
    base_files = {}

    for dir_name in os.listdir(dir_path):
        tag_file = os.path.join(dir_path, dir_name, "tag-details.md")
        if os.path.isfile(tag_file):
            temp_set = set()

            # Open the file and search for snippets that match the pattern
            with open(tag_file, 'r') as file:
                try:
                    data = file.read()
                    matches = dockerfile_pattern.findall(data)
                except UnicodeDecodeError:
                    matches = []

            # Extract file line from the matched snippets
            for match in matches:
                fileline = match[1]
                temp_set.add(fileline)

            if len(temp_set) > 0:
                base_files[dir_name] = list(temp_set)

    return base_files


def parse_markdown_file(md_content):
    # Patterns to identify markdown headers
    headers = []
    positions = []

    # Finding all headers in the file
    for match in header_pattern.finditer(md_content):
        headers.append(match.group(2))
        positions.append(match.start())

    sections = {}

    # Extract content between headers
    for i in range(len(headers)):
        start = positions[i] + len(headers[i])
        end = positions[i + 1] if i + 1 < len(positions) else len(md_content)
        section_content = md_content[start:end].strip()

        # Trimmer to next header begin (position-wise)
        next_header_match = header_pattern.search(section_content)
        if next_header_match:
            section_content = section_content[:next_header_match.start()].strip()

        # Assign content to the section
        sections[headers[i]] = section_content

    return sections


def get_base_files_with_version(dir_path: str) -> dict[str, list]:
    base_files = {}

    for dir_name in os.listdir(dir_path):
        tag_file = os.path.join(dir_path, dir_name, "tag-details.md")
        if os.path.isfile(tag_file):
            temp_set = set()

            # Open the file and search for snippets that match the pattern
            with open(tag_file, 'r') as file:
                try:
                    markdown_text = file.read()
                    sections = parse_markdown_file(markdown_text)
                except UnicodeDecodeError:
                    sections = {}

            for section_name, content in sections.items():
                dockerfile_matches = dockerfile_pattern.findall(content)

                # Extract file line from the matched snippets
                for match in dockerfile_matches:
                    fileline = match[1]
                    temp_set.add(fileline)

                if len(temp_set) > 0:
                    name_matches = section_name_pattern.findall(section_name)
                    if len(name_matches) > 0:
                        section_key = name_matches[0]
                    else:
                        section_key = dir_name

                    if section_key in base_files:
                        base_files[section_key].extend(list(temp_set))
                    else:
                        base_files[section_key] = list(temp_set)

    return base_files


def move_head_commits_behind(dir_path: str, commit_num: int) -> None:
    subprocess.run(["git", "checkout", f"HEAD~{commit_num}"], cwd=dir_path)


def get_len_initial_commit(dir_path) -> int:
    return int(subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=dir_path, capture_output=True).stdout)


def merge_dicts(dict1: dict[str, list], dict2: dict[str, list]) -> dict[str, list]:
    merged_dict = dict1.copy()

    for key, value in dict2.items():
        if key in merged_dict:
            merged_dict[key] = list(set(merged_dict[key]).union(set(value)))
        else:
            merged_dict[key] = value

    return merged_dict


if __name__ == '__main__':
    base_dir = "/home/quiner/innopolis/thesis/repo-info/repos"

    base_files_full_history = json.load(open('../artifacts/base_files_full_history.json', 'r'))
    commit_num = get_len_initial_commit(base_dir)
    COMMIT_STEP = 300
    iteration = 0

    while commit_num > 25 + COMMIT_STEP:
        commit_num -= COMMIT_STEP
        iteration += 1
        if iteration % 30 == 0:
            json.dump(base_files_full_history, open('../artifacts/base_files_full_history.json', 'w'), indent=4)

        base_files_dir = get_base_files_with_version(base_dir)
        base_files_full_history = merge_dicts(base_files_full_history, base_files_dir)

        move_head_commits_behind(base_dir, 100)
        print(f"{iteration=} - {commit_num=}")

    print("Initial commit reached. Process completed.")
    json.dump(base_files_full_history, open('../artifacts/base_files_full_history.json', 'w'), indent=4)
