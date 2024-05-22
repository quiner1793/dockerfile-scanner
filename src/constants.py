import json
import re

base_files_full_history = json.load(
    open("../artifacts/base_files_full_history_compressed.json", "r")
)
docker_image_stigs: dict[str, dict] = json.load(
    open("../scap-content/docker_image_stigs.json", "r")
)
base_file_pattern = re.compile(r"file:(\w{64}) in /")


class PrintColors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
