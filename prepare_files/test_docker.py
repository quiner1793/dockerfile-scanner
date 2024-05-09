from os import walk


def scan_docker_dir(docker_dir: str):
    filenames = next(walk(docker_dir), (None, None, []))[2]

    for filename in filenames:
        print(filename)


if __name__ == '__main__':
    docker_dir_path = ["/scan_dir"]

    for dir_path in docker_dir_path:
        scan_docker_dir(dir_path)
