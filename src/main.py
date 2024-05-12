import os
from docker_scanner import DockerScanner


if __name__ == "__main__":
    # docker_dir_path = sys.argv[1]
    docker_dir_path = "../"
    recurse = True if os.getenv("RECURSE", default="false") == "true" else False

    scanner = DockerScanner(scan_dir=docker_dir_path, recurse_flag=True)
    scanner.traverse_directory().filter_images().make_docker_analytics().print_report()
