import docker
from tabulate import tabulate

from docker_image import DockerImage

manual_base_images = {
    "alpine:3.17.1": "alpine:3.17.1",
    "alpine:3.18.5": "alpine:3.18.5",
    "alpine:3.19.1": "alpine:3.19.1",
    "busybox:1.34.1": "busybox:1.34.1",
    "nginx:1.23.1": "debian:11.5",
    "nginx:1.24.0": "debian:11.9",
    "nginx:1.25.1": "debian:12.1",
    "ubuntu:18.04": "ubuntu:18.04.6",
    "ubuntu:20.04": "ubuntu:20.04.6",
    "ubuntu:22.04": "ubuntu:22.04.4",
    "python:3.12.2": "debian:12.5",
    "python:3.11.8": "debian:12.5",
    "python:3.10.13": "debian:12.5",
    "postgres:15.6": "debian:12.5",
    "postgres:14.11": "debian:12.5",
    "redis:7.2.3": "debian:12.4",
    "redis:7.0.14": "debian:12.4",
    "httpd:2.4.58": "debian:12.5",
    "node:22.2.0-alpine3.18": "alpine:3.18.6",
    "node:21.7.2-bookworm": "debian:12.5",
    "mongo:7.0.9": "ubuntu:22.04.4",
    "rabbitmq:3.13.1": "ubuntu:22.04.4",
    "rabbitmq:3.12.14-alpine": "alpine:3.19.1",
}

if __name__ == "__main__":
    images = [
        DockerImage(image_name=image_name, usage_link="")
        for image_name in manual_base_images.keys()
    ]

    docker_client = docker.from_env()
    for image in images:
        print(f"Pulling docker image: {image.image_name}")
        image.pull_docker_image(docker_client=docker_client)

    print("Getting base docker images")
    [image.get_base_image(docker_client=docker_client) for image in images]

    print(
        tabulate(
            [
                [
                    image.image_name,
                    image.base_image_name,
                    manual_base_images.get(image.image_name),
                ]
                for image in images
            ],
            headers=["Image name", "Found base image", "Manual base image"],
            tablefmt="orgtbl",
        )
    )
