import os

import yaml

from docker_unit_file import (
    Dockerfile,
    DockerCompose,
    DockerUnitFile,
    KubernetesFile,
    HelmFile,
    TerraformFile,
)
from docker_image import DockerImage, DockerImageAnalytics
from constants import PrintColors


def filter_usage_links(usage_links: list[str], extend_links: list[str]) -> list[str]:
    """
    Filter file usage links. Return only unique links based on absolute path.
    """
    return list(
        set(os.path.realpath(usage_link) for usage_link in usage_links + extend_links)
    )


def check_file_k8s_or_helm(file_path: str, filename: str) -> DockerUnitFile | None:
    """
    Function to check if a file is a Kubernetes or Helm manifest
    """
    try:
        with open(file_path, "r") as file:
            content = yaml.safe_load(file)
        if content:
            # Check for typical Kubernetes and Helm-specific fields
            if isinstance(content, dict):
                # Kubernetes' resources usually have 'apiVersion', 'kind' and 'spec' fields
                # Or are name like deployment.*, ingress.*, service.*
                if (
                    "apiVersion" in content
                    and "kind" in content
                    and "spec" in content
                    or (
                        filename.startswith("deployment.")
                        or filename.startswith("ingress.")
                        or filename.startswith("service.")
                    )
                ):
                    return KubernetesFile(file_path=file_path)
                # Supporting Helm values files
                if "image" in content and "values" in filename:
                    return HelmFile(file_path=file_path)
    except yaml.YAMLError:
        pass
    except Exception as e:
        print(
            f"{PrintColors.FAIL}Error processing file {file_path}: {e}{PrintColors.ENDC}"
        )
    return None


class DockerScanner:
    def __init__(
        self,
        scan_dir: str,
        recurse_flag: bool = False,
        base_image_flag: bool = True,
        inspect_info_flag: bool = True,
        runtime_info_flag: bool = True,
        stigs_flag: bool = True,
    ):
        self.scan_dir = scan_dir
        self.recurse_flag = recurse_flag
        self.docker_images: list[DockerImage] = []
        self.docker_image_analytics: list[DockerImageAnalytics] = []
        self.base_image_flag = base_image_flag
        self.inspect_info_flag = inspect_info_flag
        self.runtime_info_flag = runtime_info_flag
        self.stigs_flag = stigs_flag

    def traverse_directory(self):
        """
        Walk through directory to find files that contain Docker images.
        Collect them in self.docker_images list with usage links
        """
        print(f"{PrintColors.HEADER}Start directory traversing{PrintColors.ENDC}")
        for root, _, f_names in os.walk(self.scan_dir):
            for filename in f_names:
                # Dockerfile
                if ".dockerfile" in filename.lower():
                    print(
                        f"{PrintColors.BOLD}Detected Dockerfile{PrintColors.ENDC}: {filename}"
                    )
                    self.docker_images.extend(
                        Dockerfile(
                            file_path=os.path.join(root, filename)
                        ).get_docker_images()
                    )
                # Docker compose and k8s/helm
                elif filename.endswith(".yml") or filename.endswith(".yaml"):
                    if "docker-compose" in filename.lower():
                        print(
                            f"{PrintColors.BOLD}Detected docker compose file{PrintColors.ENDC}: {filename}"
                        )
                        self.docker_images.extend(
                            DockerCompose(
                                file_path=os.path.join(root, filename), compose_dir=root
                            ).get_docker_images()
                        )
                    else:
                        docker_file: DockerUnitFile = check_file_k8s_or_helm(
                            file_path=os.path.join(root, filename), filename=filename
                        )
                        if docker_file:
                            print(
                                f"{PrintColors.BOLD}Detected k8s/helm manifest{PrintColors.ENDC}: {filename}"
                            )
                            self.docker_images.extend(docker_file.get_docker_images())
                # Terraform
                elif filename.endswith(".tf"):
                    print(
                        f"{PrintColors.BOLD}Detected terraform file{PrintColors.ENDC}: {filename}"
                    )
                    self.docker_images.extend(
                        TerraformFile(
                            file_path=os.path.join(root, filename)
                        ).get_docker_images()
                    )

            # If recurse flag false: stop at first iteration
            if not self.recurse_flag:
                break

        print(f"{PrintColors.OKGREEN}Finish directory traversing{PrintColors.ENDC}\n")
        return self

    def filter_images(self):
        """
        Filter Docker images from self.docker_images. Filter their usage links.
        """
        print(f"{PrintColors.HEADER}Start image filtering{PrintColors.ENDC}")
        # Mapping of unique Docker images to their usage links
        image_mapping: dict[str, list[str]] = {}

        for docker_image in self.docker_images:
            # Image already found: extend usage links
            if docker_image.image_name in image_mapping:
                image_mapping[docker_image.image_name] = filter_usage_links(
                    usage_links=image_mapping[docker_image.image_name],
                    extend_links=docker_image.usage_links,
                )
            # Image previously not found: add to mapping
            else:
                image_mapping[docker_image.image_name] = filter_usage_links(
                    usage_links=docker_image.usage_links, extend_links=[]
                )

        # Update docker images list with only unique images
        self.docker_images = [
            DockerImage(image_name=image_name, usage_link=usage_links)
            for image_name, usage_links in image_mapping.items()
        ]

        print(f"Found {len(self.docker_images)} unique docker images")
        print(f"{PrintColors.OKGREEN}Finish image filtering{PrintColors.ENDC}\n")
        return self

    def make_docker_analytics(self):
        """
        For each image in self docker_images make analytics using DockerImageAnalytics class
        """
        print(f"{PrintColors.HEADER}Start image analytics{PrintColors.ENDC}")
        for docker_image in self.docker_images:
            print(
                f"{PrintColors.BOLD}Analyzing docker image{PrintColors.ENDC}: {docker_image.image_name}"
            )
            docker_analytics = DockerImageAnalytics(
                docker_image=docker_image,
                base_image_flag=self.base_image_flag,
                inspect_info_flag=self.inspect_info_flag,
                runtime_info_flag=self.runtime_info_flag,
                stigs_flag=self.stigs_flag,
            )
            docker_analytics.analyze_docker_image()
            self.docker_image_analytics.append(docker_analytics)

        print(f"{PrintColors.OKGREEN}Finish image analytics{PrintColors.ENDC}\n")
        return self

    def print_report(self):
        """
        Print report based on self docker image analytics list
        """
        print(f"{PrintColors.HEADER}Start generating report{PrintColors.ENDC}")
        for docker_analytics in self.docker_image_analytics:
            print(
                f"\n{PrintColors.UNDERLINE}Analytics for docker image: "
                f"{docker_analytics.docker_image.image_name}{PrintColors.ENDC}:"
            )
            docker_analytics.print_report()

        print(f"{PrintColors.OKGREEN}Finish generating report{PrintColors.ENDC}")
        return self
