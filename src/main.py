import os
import sys

from docker_scanner import DockerScanner


if __name__ == "__main__":
    docker_dir_path = sys.argv[1]
    # docker_dir_path = "../"
    recurse = True if os.getenv("RECURSE", default="false") == "true" else False
    base_image = True if os.getenv("BASE_IMAGE", default="false") == "true" else False
    inspect_info = (
        True if os.getenv("INSPECT_INFO", default="false") == "true" else False
    )
    runtime_info = (
        True if os.getenv("RUNTIME_INFO", default="false") == "true" else False
    )
    stigs_scan = True if os.getenv("STIGS_SCAN", default="false") == "true" else False

    scanner = DockerScanner(
        scan_dir=docker_dir_path,
        recurse_flag=recurse,
        base_image_flag=base_image,
        inspect_info_flag=inspect_info,
        runtime_info_flag=False,
        stigs_flag=stigs_scan,
    )
    scanner.traverse_directory().filter_images().make_docker_analytics().print_report()
