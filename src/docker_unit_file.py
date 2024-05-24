import re
from os import path
import yaml
from dockerfile_parse import DockerfileParser

from docker_image import DockerImage
from constants import PrintColors


class DockerUnitFile:
    """Base file with Docker image usage"""
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_docker_images(self) -> list[DockerImage]:
        raise NotImplementedError("Method not implemented")


class Dockerfile(DockerUnitFile):
    def __init__(self, file_path: str):
        super().__init__(file_path)

    def get_docker_images(self) -> list[DockerImage]:
        """Get images based on Dockerfile FROM instruction"""
        docker_images: list[DockerImage] = []

        if path.exists(self.file_path):
            dfp = DockerfileParser(path=self.file_path)
            for element in dfp.structure:
                if element["instruction"] == "FROM":
                    image_name = element["value"].split()[0]
                    docker_images.append(
                        DockerImage(image_name=image_name, usage_link=self.file_path)
                    )

        return docker_images


class DockerCompose(DockerUnitFile):
    def __init__(self, file_path: str, compose_dir: str):
        super().__init__(file_path)
        self.compose_dir = compose_dir

    def get_images_docker_compose_build(
        self, build_context: str | None, dockerfile_path: str | None
    ) -> list[DockerImage]:
        """Utilize Dockerfile class for cases when image is build in runtime"""
        if build_context is not None:
            dockerfile_path = path.join(build_context, dockerfile_path)
        joined_dockerfile_path = path.join(self.compose_dir, dockerfile_path)

        return Dockerfile(file_path=joined_dockerfile_path).get_docker_images()

    def get_docker_images(self) -> list[DockerImage]:
        """Get images based on docker compose services"""
        docker_images: list[DockerImage] = []

        with open(self.file_path) as stream:
            try:
                docker_compose = yaml.safe_load(stream)
                # Iterate through compose services
                for service_name, service_content in docker_compose["services"].items():
                    image_name = service_content.get("image")
                    build_info = service_content.get("build")
                    if build_info is not None:
                        # Firstly check for build info
                        if isinstance(build_info, str):
                            if "dockerfile" not in build_info.lower():
                                # Invalid name: replace with Dockerfile
                                build_info = path.join(build_info, "Dockerfile")
                            # If build info is str => no build context
                            build_context = None
                            dockerfile_path = build_info
                        elif isinstance(build_info, dict):
                            # For dict build info both build context and dockerfile
                            # path should be present
                            build_context = build_info.get("context")
                            dockerfile_path = build_info.get("dockerfile")
                        else:
                            break

                        # Utilize Dockerfile logic
                        temp_docker_images = self.get_images_docker_compose_build(
                            build_context=build_context,
                            dockerfile_path=dockerfile_path,
                        )
                        for docker_image in temp_docker_images:
                            docker_image.add_usage_link(self.file_path)
                        docker_images.extend(temp_docker_images)

                    elif image_name is not None:
                        # Direct docker image provided
                        docker_images.append(
                            DockerImage(
                                image_name=image_name, usage_link=self.file_path
                            )
                        )
            except yaml.YAMLError as exc:
                print(exc)

        return docker_images


def recursive_find_images(content):
    """
    Recursively parse content dict and check for image key
    """
    images = []
    if isinstance(content, dict):
        for key, value in content.items():
            if key == "image":
                if isinstance(value, str):
                    # Image introduced directly
                    images.append(value)
                elif "repository" in value and "tag" in value:
                    # Image could be introduced with repository and tag
                    images.append(value["repository"] + ":" + value["tag"])
            elif isinstance(content, dict) or isinstance(content, list):
                # Continue search
                images.extend(recursive_find_images(value))
    elif isinstance(content, list):
        for item in content:
            images.extend(recursive_find_images(item))
    return images


def parse_k8s_helm_images(file_path: str) -> list[str]:
    """
    Recursively parse content of k8s or helm files for docker images
    """
    images = []
    try:
        with open(file_path, "r") as file:
            docs = yaml.safe_load_all(file)
            for doc in docs:
                if doc and isinstance(doc, dict):
                    # Recursively search for image keys in document
                    images.extend(recursive_find_images(doc))
    except Exception as e:
        print(
            f"{PrintColors.FAIL}Error reading file {file_path}: {e}{PrintColors.ENDC}"
        )
    return images


class KubernetesFile(DockerUnitFile):
    def __init__(self, file_path: str):
        super().__init__(file_path)

    def get_docker_images(self) -> list[DockerImage]:
        """
        Get images using recursive content parsing
        """
        return [
            DockerImage(image_name=image_name, usage_link=self.file_path)
            for image_name in parse_k8s_helm_images(self.file_path)
        ]


class HelmFile(DockerUnitFile):
    def __init__(self, file_path: str):
        super().__init__(file_path)

    def get_docker_images(self) -> list[DockerImage]:
        """
        Get images using recursive content parsing
        """
        return [
            DockerImage(image_name=image_name, usage_link=self.file_path)
            for image_name in parse_k8s_helm_images(self.file_path)
        ]


class TerraformFile(DockerUnitFile):
    def __init__(self, file_path: str):
        super().__init__(file_path)

    def get_docker_images(self) -> list[DockerImage]:
        """
        Get images based on terraform docker_image resource
        """
        docker_images: list[DockerImage] = []
        # From docker_image resource section extract image name
        docker_image_pattern = re.compile(
            r'resource\s+"docker_image"\s+"\w+"\s*\{\s*name\s*=\s*"([^"]+)"',
            re.IGNORECASE | re.DOTALL,
        )
        try:
            with open(self.file_path, "r") as file:
                content = file.read()
                matches = docker_image_pattern.findall(content)
                for match in matches:
                    docker_images.append(
                        DockerImage(image_name=match, usage_link=self.file_path)
                    )
        except Exception as e:
            print(
                f"{PrintColors.FAIL}Error reading file {self.file_path}: {e}{PrintColors.ENDC}"
            )
        return docker_images
