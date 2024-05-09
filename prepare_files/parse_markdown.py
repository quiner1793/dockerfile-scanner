import re
from get_base_files_full_history import parse_markdown_file

if __name__ == '__main__':
    dir_name = "alpine"
    with open("tag-details.md", 'r') as file:
        markdown_text = file.read()
        sections = parse_markdown_file(markdown_text)

    dockerfile_pattern = re.compile(r'```dockerfile\n# (.+)\nADD file:(.+) in / \n# (.+)\nCMD \["(.+)"]\n```')
    section_name_pattern = re.compile(r"`(.*?)`")
    temp_set = set()

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

            print(section_key)
            if section_key in base_files:
                base_files[section_key].extend(list(temp_set))
            else:
                base_files[section_key] = list(temp_set)
