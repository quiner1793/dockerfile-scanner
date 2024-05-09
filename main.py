import json
import logging
from logging import log
import re
import sys

import yaml
from os import walk, path
from dockerfile_parse import DockerfileParser
import docker

base_files_full_history = json.load(open('base_files_full_history_compressed.json', 'r'))
docker_image_stigs: dict[str, str] = json.load(open('docker_image_stigs.json', 'r'))
base_file_pattern = re.compile(r"file:(\w{64}) in /")


def find_base_images(file_hash: str | None) -> list[str]:
    if file_hash is None:
        return []

    found_keys = []
    for base_image_name, file_hashes in base_files_full_history.items():
        if file_hash in file_hashes:
            found_keys.append(base_image_name)
    return found_keys


def get_base_image(docker_image_name: str) -> list[str]:
    # Initialize the Docker client
    client = docker.from_env()

    # Step 1: Pull Docker image
    client.images.pull(docker_image_name)

    # Step 2: Get history of image and extract the hash of the base image layer
    image = client.images.get(docker_image_name)
    image_history = image.history()
    matches = base_file_pattern.findall(str(image_history))
    file_hash = matches[-1] if len(matches) > 0 else None
    return find_base_images(file_hash)


def get_available_stigs(docker_image_name: str) -> list[str]:
    if docker_image_name in docker_image_stigs.keys():
        return [docker_image_stigs[docker_image_name]]
    return []


def analyze_docker_image(docker_image_name: str) -> None:
    stigs = get_available_stigs(docker_image_name)
    if len(stigs) > 0:
        print(f"Found available STIGs for {docker_image_name} image: {' '.join(stigs)}")
    else:
        print(f"No available STIGs for {docker_image_name} image. Analyzing base image...")
        base_image_name = get_base_image(docker_image_name)
        if base_image_name is not None:
            print(f"Found base image for {docker_image_name} image: {base_image_name}")
            stigs = get_available_stigs(docker_image_name)
            if len(stigs) > 0:
                print(f"Available STIGs: {' '.join(stigs)}")
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


def scan_docker_dir(docker_dir: str):
    filenames = next(walk(docker_dir), (None, None, []))[2]

    for filename in filenames:
        print(filename)
        if "dockerfile" in filename.lower():
            print("------------------------------------------------------------")
            print(f"Detected Dockerfile: {filename}. Analyzing...")
            print("------------------------------------------------------------")
            scan_dockerfile(dockerfile_path=path.join(docker_dir, filename))
            print("\n")

        elif "docker-compose" in filename.lower() and (filename.endswith(".yml") or filename.endswith(".yaml")):
            print("------------------------------------------------------------")
            print(f"Detected docker compose file: {filename}. Analyzing...")
            print("------------------------------------------------------------")
            scan_docker_compose(docker_compose_dir=docker_dir, docker_compose_path=path.join(docker_dir, filename))
            print("\n")


if __name__ == '__main__':
    # docker_dir_path = ["dockerfiles/", "docker-composes/"]
    # docker_dir_path = ["docker-composes/"]
    # docker_dir_path = ["dockerfiles/"]
    docker_dir_path = sys.argv[1]
    scan_docker_dir(docker_dir_path)
