import json
import os
import re
import subprocess
from collections import defaultdict

dockerfile_pattern = re.compile(
    r'```dockerfile\n# (.+)\nADD file:(.+) in / \n# (.+)\nCMD \["(.+)"]\n```'
)
section_name_pattern = re.compile(r"`(.*?)`")
header_pattern = re.compile(r"^(##+)\s+(.*)", re.MULTILINE)


def get_base_files(dir_path: str) -> dict[str, list]:
    """
    Walk through all directories in specified dir_path and extract
    base file info from 'tag-details.md' files
    """
    # Initialize base files dict
    base_files = {}

    # Walk through all directories
    for dir_name in os.listdir(dir_path):
        tag_file = os.path.join(dir_path, dir_name, "tag-details.md")

        # If 'tag-details.md' file exists
        if os.path.isfile(tag_file):
            temp_set = set()

            # Open the file and search for snippets that match the pattern
            with open(tag_file, "r") as file:
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
    """
    Parse markdown file by headers to make mapping of header
    name to extracted content
    """
    # Header group
    headers = []
    # Position indexes
    positions = []

    # Finding all headers in the file
    for match in header_pattern.finditer(md_content):
        headers.append(match.group(2))
        positions.append(match.start())

    sections = {}

    # Extract content between headers
    for i in range(len(headers)):
        # Cut header content
        start = positions[i] + len(headers[i])
        end = positions[i + 1] if i + 1 < len(positions) else len(md_content)
        section_content = md_content[start:end].strip()

        # Trimmer to next header begin (position-wise)
        next_header_match = header_pattern.search(section_content)
        if next_header_match:
            section_content = section_content[: next_header_match.start()].strip()

        # Assign content to the section
        sections[headers[i]] = section_content

    return sections


def get_base_files_with_version(dir_path: str) -> dict[str, list]:
    """
    Walk through all directories in specified dir_path and extract
    base file info from 'tag-details.md' files including versions
    """
    # Initialize base files dict
    base_files = {}

    # Walk through all directories
    for dir_name in os.listdir(dir_path):
        tag_file = os.path.join(dir_path, dir_name, "tag-details.md")

        # If 'tag-details.md' file exists
        if os.path.isfile(tag_file):
            temp_set = set()

            # Open the file and extract markdown content by headers
            with open(tag_file, "r") as file:
                try:
                    markdown_text = file.read()
                    sections = parse_markdown_file(markdown_text)
                except UnicodeDecodeError:
                    sections = {}

            for section_name, content in sections.items():
                # Search for snippets that match the pattern
                dockerfile_matches = dockerfile_pattern.findall(content)

                # Extract file line from the matched snippets
                for match in dockerfile_matches:
                    fileline = match[1]
                    temp_set.add(fileline)

                if len(temp_set) > 0:
                    name_matches = section_name_pattern.findall(section_name)
                    # Find section name; default = dir_name
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
    """
    Inside 'dir_path' move git HEAD 'commit_num' commits behind
    Used for traversing git history
    """
    subprocess.run(["git", "checkout", f"HEAD~{commit_num}"], cwd=dir_path)


def get_len_initial_commit(dir_path: str) -> int:
    """
    Inside 'dir_path' find number of commits from HEAD to initial
    """
    return int(
        subprocess.run(
            ["git", "rev-list", "--count", "HEAD"], cwd=dir_path, capture_output=True
        ).stdout
    )


def merge_dicts(dict1: dict[str, list], dict2: dict[str, list]) -> dict[str, list]:
    """
    Merge unique values of dicts by keys
    """
    merged_dict = dict1.copy()

    for key, value in dict2.items():
        if key in merged_dict:
            merged_dict[key] = list(set(merged_dict[key]).union(set(value)))
        else:
            merged_dict[key] = value

    return merged_dict


def get_base_files_full_history(
    base_files_full_history_path: str,
    docker_repo_info_path: str,
    commit_step: int = 100,
):
    """
    Traverse git commits inside 'docker_repo_info_path' and scan them for base files.
    After git history traversed save results to 'base_files_full_history_path'
    """
    base_files_full_history = json.load(open(base_files_full_history_path, "r"))
    commit_num = get_len_initial_commit(docker_repo_info_path)

    iteration = 0
    # First commits are technical and we are not interested in them
    commit_threshold = 25
    # Every n iteration save current state to file
    iteration_save_step = 30

    while commit_num > commit_threshold + commit_step:
        commit_num -= commit_step
        iteration += 1
        if iteration % iteration_save_step == 0:
            json.dump(
                base_files_full_history,
                open(base_files_full_history_path, "w"),
                indent=4,
            )

        base_files_dir = get_base_files_with_version(docker_repo_info_path)
        base_files_full_history = merge_dicts(base_files_full_history, base_files_dir)

        move_head_commits_behind(docker_repo_info_path, commit_step)
        print(f"{iteration=} - {commit_num=}")

    print("Initial commit reached. Process completed.")
    json.dump(
        base_files_full_history, open(base_files_full_history_path, "w"), indent=4
    )


def sort_files_keys(base_files: dict[str, list]) -> list[str]:
    """
    Firstly sort files with numeric tags, then with string tags
    and return concatenated result
    """
    pattern = re.compile(r"^([a-zA-Z]+):(\d+\.\d+\.\d+|\d+\.\d+)(-[a-zA-Z]+)?$")

    matched = [img for img in base_files.keys() if pattern.match(img)]
    unmatched = [img for img in base_files.keys() if not pattern.match(img)]

    return sorted(matched) + sorted(unmatched)


def get_base_files_full_history_compressed(
    base_files_full_history_path: str, base_files_full_history_compressed_path: str
):
    """
    Compress base files by sorting file keys and getting only unique file hashes
    """
    compressed_files_full_history = defaultdict(list)
    base_files_full_history = json.load(open(base_files_full_history_path, "r"))

    files_keys = sort_files_keys(base_files_full_history)

    for image_name in files_keys:
        file_hashes = base_files_full_history[image_name]
        for file_hash in file_hashes:
            # If file hash is unique then add it to result
            if not any(
                file_hash in hash_list
                for hash_list in compressed_files_full_history.values()
            ):
                compressed_files_full_history[image_name].append(file_hash)

    json.dump(
        compressed_files_full_history,
        open(base_files_full_history_compressed_path, "w"),
        indent=4,
    )


if __name__ == "__main__":
    repo_info_path = "path_to/repo-info/repos"
    base_files_path = "base_files_full_history.json"
    base_files_compressed_path = "base_files_full_history_compressed.json"

    # get_base_files_full_history(base_files_full_history_path=base_files_path, docker_repo_info_path=repo_info_path)
    get_base_files_full_history_compressed(
        base_files_full_history_path=base_files_path,
        base_files_full_history_compressed_path=base_files_compressed_path,
    )
