import json
import os
import re
import sys

import yaml
from os import walk, path
from dockerfile_parse import DockerfileParser
import docker

base_files_full_history = json.load(open('base_files_full_history_compressed.json', 'r'))
docker_image_stigs: dict[str, str] = json.load(open('docker_image_stigs.json', 'r'))
base_file_pattern = re.compile(r"file:(\w{64}) in /")
base_image_names = ["rockylinux", "alpine", "debian", "almalinux", "oraclelinux", "busybox", "amazonlinux"]


def find_base_image(file_hash: str | None) -> str | None:
    for base_image_name, file_hashes in base_files_full_history.items():
        if file_hash in file_hashes:
            return base_image_name
    return None


def get_base_image(docker_image_name: str) -> str | None:
    # Initialize the Docker client
    client = docker.from_env()

    # Step 1: Pull Docker image
    client.images.pull(docker_image_name)

    # Step 2: Get history of image and extract the hash of the base image layer
    image = client.images.get(docker_image_name)
    image_history = image.history()
    matches = base_file_pattern.findall(str(image_history))
    file_hash = matches[-1] if len(matches) > 0 else None
    return find_base_image(file_hash)


def get_available_stigs(docker_image_name: str) -> str | None:
    if docker_image_name in docker_image_stigs.keys():
        return docker_image_stigs[docker_image_name]

    for base_image_name in base_image_names:
        if docker_image_name.startswith(f"{base_image_name}:"):
            return docker_image_stigs[base_image_name]

    return None


def analyze_docker_image(docker_image_name: str) -> None:
    stigs = get_available_stigs(docker_image_name)
    if stigs is not None:
        print(f"Found available STIGs for {docker_image_name} image: {stigs}")
    else:
        print(f"No available STIGs for {docker_image_name} image. Analyzing base image...")
        base_image_name = get_base_image(docker_image_name)
        if base_image_name is not None:
            print(f"Found base image for {docker_image_name} image: {base_image_name}")
            stigs = get_available_stigs(base_image_name)
            if stigs is not None:
                print(f"Available STIGs: {stigs}")
            else:
                print(f"Available STIGs: None")
        else:
            print(f"No base image found for {docker_image_name} image.")


def scan_dockerfile(dockerfile_path: str):
    dfp = DockerfileParser(path=dockerfile_path)

    for element in dfp.structure:
        if element["instruction"] == "FROM":
            image_name = element["value"].split()[0]
            print(f"Detected FROM instruction: {element['content']}")
            analyze_docker_image(image_name)


def scan_docker_compose_build(docker_compose_dir: str, build_context: str | None, dockerfile_path: str) -> None:
    if build_context is not None:
        dockerfile_path = path.join(build_context, dockerfile_path)
    joined_dockerfile_path = path.join(docker_compose_dir, dockerfile_path)
    if path.exists(joined_dockerfile_path):
        print(f"Found Dockerfile: {joined_dockerfile_path}. Analyzing...")
        scan_dockerfile(dockerfile_path=joined_dockerfile_path)
    else:
        print(f"Dockerfile: {joined_dockerfile_path} not found.")


def scan_docker_compose(docker_compose_dir: str, docker_compose_path: str):
    with open(docker_compose_path) as stream:
        try:
            docker_compose = yaml.safe_load(stream)
            for service_name, service_content in docker_compose['services'].items():
                print(f"Detected service: {service_name}")
                image_name = service_content.get('image')
                build_info = service_content.get('build')
                if build_info is not None:
                    print(f"Found build info for service {service_name}")

                    if isinstance(build_info, str):
                        if "dockerfile" not in build_info:
                            build_info = path.join(build_info, "Dockerfile")
                        build_context = None
                        dockerfile_path = build_info
                    elif isinstance(build_info, dict):
                        build_context = build_info.get('context')
                        dockerfile_path = build_info.get('dockerfile')
                    else:
                        print("No Dockerfile found.")
                        break

                    scan_docker_compose_build(docker_compose_dir=docker_compose_dir, build_context=build_context,
                                              dockerfile_path=dockerfile_path)

                elif image_name is not None:
                    print(f"Found image for service {service_name} in Docker Compose: {image_name}. Analyzing image...")
                    analyze_docker_image(image_name)

                print("----------\n")

        except yaml.YAMLError as exc:
            print(exc)


def scan_docker_dir(docker_dir: str, recurse: bool = False):
    for root, _, f_names in walk(docker_dir):
        for filename in f_names:
            if "dockerfile" in filename.lower():
                print("------------------------------------------------------------")
                print(f"Detected Dockerfile: {filename}. Analyzing...")
                print("------------------------------------------------------------")
                scan_dockerfile(dockerfile_path=path.join(root, filename))
                print("\n")

            elif "docker-compose" in filename.lower() and (filename.endswith(".yml") or filename.endswith(".yaml")):
                print("------------------------------------------------------------")
                print(f"Detected docker compose file: {filename}. Analyzing...")
                print("------------------------------------------------------------")
                scan_docker_compose(docker_compose_dir=root, docker_compose_path=path.join(root, filename))
                print("\n")
        if not recurse:
            break


if __name__ == '__main__':
    docker_dir_path = sys.argv[1]
    recurse = True if os.getenv("RECURSE", default='false') == 'true' else False
    scan_docker_dir(docker_dir_path, recurse=recurse)
