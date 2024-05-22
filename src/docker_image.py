import re
import docker
from docker.errors import ContainerError, APIError, ImageNotFound
from docker import DockerClient

from constants import (
    base_files_full_history,
    base_file_pattern,
    docker_image_stigs,
    PrintColors,
)
from oscap_docker_python.oscap_docker_common import OscapResult
from oscap_docker_python.oscap_docker_util_noatomic import OscapDockerScan


def get_stig_info(docker_image_name: str | None) -> dict | None:
    if docker_image_name is None:
        return None

    stig_info = None
    for docker_family in docker_image_stigs.keys():
        if docker_image_name.startswith(docker_family):
            base_docker_stigs = docker_image_stigs[docker_family]
            for docker_family_member in base_docker_stigs.keys():
                if docker_image_name.startswith(docker_family_member):
                    stig_info = base_docker_stigs[docker_family_member]
            if stig_info is None:
                stig_info = base_docker_stigs.get("default")
    return stig_info


class StigInfo:
    def __init__(self, docker_image_name: str | None, base_image_name: str | None):
        stig_info = get_stig_info(docker_image_name=docker_image_name)

        # STIG not found or default STIG info is used
        if stig_info is None or len(stig_info.keys()) == 1:
            base_stig_info = get_stig_info(docker_image_name=base_image_name)
            if base_stig_info is not None:
                # Found better stig for base image
                if stig_info is None or len(base_stig_info.keys()) > len(
                    stig_info.keys()
                ):
                    stig_info = base_stig_info

        if stig_info is None:
            stig_info = {}

        self.stig_name = stig_info.get("name")
        self.profile = stig_info.get("profile", None)
        self.datastream_id = stig_info.get("datastream_id", None)
        self.xccdf_id = stig_info.get("xccdf_id", None)
        self.scap_file = stig_info.get("scap_file", None)
        self.oscap_result: OscapResult | None = None
        self.passed: int | None = None
        self.failed: int | None = None
        self.not_applicable: int | None = None

    def scan_docker_image(self, docker_image_name: str | None):
        if docker_image_name is None:
            return None

        leftover_args = [
            "xccdf",
            "eval",
            "--fetch-remote-resources",
            "--datastream-id",
            self.datastream_id,
            "--xccdf-id",
            self.xccdf_id,
            "--profile",
            self.profile,
            "--oval-results",
            "--report",
            f"{docker_image_name.replace(':', '_')}_report.html",
            f"../scap-content/{self.scap_file}",
        ]

        try:
            oscap_docker = OscapDockerScan(
                target=docker_image_name, is_image=True, oscap_binary="/usr/bin/oscap"
            )
            self.oscap_result = OscapDockerScan.scan(oscap_docker, leftover_args)

            # Define a pattern to find the Result lines and their statuses.
            result_pattern = re.compile(r"^Result\s+(pass|fail|notapplicable)$", re.M)

            # Find all matches according to the pattern
            results = result_pattern.findall(self.oscap_result.stdout)

            # Count each type of result
            self.passed = results.count("pass")
            self.failed = results.count("fail")
            self.not_applicable = results.count("notapplicable")
        except (ValueError, RuntimeError) as e:
            print(e)
        except FileNotFoundError as e:
            print("Target {0} not found.\n".format(docker_image_name))
        except Exception as exc:
            print(exc)

    def print_report(self):
        print(f"\tSTIG name: {self.stig_name}")
        print(f"\tProfile: {self.profile}")
        print(f"\tDatastream ID: {self.datastream_id}")
        print(f"\tXCCDF ID: {self.xccdf_id}")
        print(f"\tSCAP file: {self.scap_file}")
        print(f"\tOSCAP passed: {self.passed}")
        print(f"\tOSCAP failed: {self.failed}")
        print(f"\tOSCAP not_applicable: {self.not_applicable}")


def find_base_image(file_hash: str | None) -> str | None:
    for base_image_name, file_hashes in base_files_full_history.items():
        if file_hash in file_hashes:
            return base_image_name
    return None


class DockerInspectInfo:
    def __init__(self, os_info: str, arch_info: str):
        self.os_info = os_info
        self.arch_info = arch_info

    def print_report(self):
        print(f"\tOS: {self.os_info}")
        print(f"\tArchitecture: {self.arch_info}")


class DockerRuntimeInfo:
    def __init__(self, exec_log: dict[str, str | None]):
        self.uname_kernel_name = exec_log.get("uname_kernel_name", "Not found").strip()
        self.uname_machine_arch = exec_log.get(
            "uname_machine_arch", "Not found"
        ).strip()
        self.uname_os = exec_log.get("uname_os", "Not found").strip()

        release_info_name_pattern = re.compile(r'PRETTY_NAME="([^"]*)"')
        matches = release_info_name_pattern.findall(exec_log.get("os_release_info", ""))
        if len(matches) > 0:
            self.release_info_name = matches[0]
        else:
            self.release_info_name = "Not found"

        self.proc_version = exec_log.get("proc_version", "Not found").strip()

    @staticmethod
    def get_exec_commands() -> dict[str, str]:
        return {
            "uname_kernel_name": "uname -s",
            "uname_machine_arch": "uname -m",
            "uname_os": "uname -o",
            "os_release_info": "cat /etc/os-release",
            "proc_version": "cat /proc/version",
        }

    def print_report(self):
        print(f"\tKernel name: {self.uname_kernel_name}")
        print(f"\tMachine architecture: {self.uname_machine_arch}")
        print(f"\tOperating System: {self.uname_os}")
        print(f"\tRelease info name: {self.release_info_name}")
        print(f"\tDistribution info: {self.proc_version}")


class DockerImage:
    def __init__(self, image_name: str, usage_link: str | list[str]):
        self.image_name = image_name
        if isinstance(usage_link, list):
            self.usage_links = usage_link
        else:
            self.usage_links = [usage_link]
        self.inspect_info: DockerInspectInfo | None = None
        self.base_image_name: str | None = None
        self.stig_info: StigInfo | None = None
        self.runtime_info: DockerRuntimeInfo | None = None

    def pull_docker_image(self, docker_client: DockerClient):
        # Pull docker image
        docker_client.images.pull(self.image_name)

    def inspect_docker_image(self, docker_client: DockerClient):
        # Inspect docker image and extract Os and Arch info
        image = docker_client.images.get(self.image_name)
        self.inspect_info = DockerInspectInfo(
            os_info=image.attrs.get("Os", "Undefined"),
            arch_info=image.attrs.get("Architecture", "Undefined"),
        )

    def get_base_image(self, docker_client: DockerClient):
        # Get history of image and extract the hash of the base image layer
        image = docker_client.images.get(self.image_name)
        image_history = image.history()
        matches = base_file_pattern.findall(str(image_history))
        file_hash = matches[-1] if len(matches) > 0 else None
        self.base_image_name = find_base_image(file_hash)

    def get_image_stig_analytics(self):
        self.stig_info = StigInfo(
            docker_image_name=self.image_name, base_image_name=self.base_image_name
        )
        self.stig_info.scan_docker_image(docker_image_name=self.image_name)

    def docker_exec_commands(
        self, commands: dict[str, str], docker_client: DockerClient
    ) -> dict[str, str | None]:
        # Create the container but do not start it yet
        output = {command: None for command in commands.keys()}
        error_text = None
        container = None

        try:
            container = docker_client.containers.create(
                self.image_name, command="/bin/sh", tty=True
            )
            # Start the container
            container.start()

            # Execute each command separately
            for command_key, command_exec in commands.items():
                exec_log = container.exec_run(command_exec, tty=True)
                output[command_key] = exec_log.output.decode("utf-8")

            # Stop and remove the container
            container.stop()

        except ContainerError as e:
            error_text = f"Container error: {e}"
        except ImageNotFound:
            error_text = f"Image {self.image_name} not found"
        except APIError as e:
            error_text = f"API error: {e}"

        if error_text:
            print(f"{PrintColors.FAIL}{error_text}{PrintColors.ENDC}")
        if container is not None:
            container.remove()
        return output

    def get_runtime_info(self, docker_client: DockerClient):
        exec_log = self.docker_exec_commands(
            DockerRuntimeInfo.get_exec_commands(), docker_client=docker_client
        )
        self.runtime_info = DockerRuntimeInfo(exec_log=exec_log)

    def add_usage_link(self, usage_link: str):
        if usage_link not in self.usage_links:
            self.usage_links.append(usage_link)


class DockerImageAnalytics:
    def __init__(
        self,
        docker_image: DockerImage,
        base_image_flag: bool = True,
        inspect_info_flag: bool = True,
        runtime_info_flag: bool = True,
        stigs_flag: bool = True,
    ):
        self.docker_image = docker_image
        self.base_image_flag = base_image_flag
        self.inspect_info_flag = inspect_info_flag
        self.runtime_info_flag = runtime_info_flag
        self.stigs_flag = stigs_flag

    def analyze_docker_image(self):
        docker_client = docker.from_env()

        # Pull image only once at start
        if self.base_image_flag or self.inspect_info_flag or self.runtime_info_flag:
            self.docker_image.pull_docker_image(docker_client=docker_client)

        if self.base_image_flag:
            self.docker_image.get_base_image(docker_client=docker_client)

        if self.inspect_info_flag:
            self.docker_image.inspect_docker_image(docker_client=docker_client)

        if self.runtime_info_flag:
            self.docker_image.get_runtime_info(docker_client=docker_client)

        if self.stigs_flag:
            self.docker_image.get_image_stig_analytics()

    def print_report(self):
        if self.base_image_flag:
            print(f"Found base image: {self.docker_image.base_image_name}")
        if self.inspect_info_flag:
            print("Found inspect info:")
            self.docker_image.inspect_info.print_report()
        if self.runtime_info_flag:
            print("Image runtime info:")
            self.docker_image.runtime_info.print_report()
        if self.stigs_flag:
            print("Found available STIGs:")
            self.docker_image.stig_info.print_report()

        print("Image usage links:")
        for usage_link in self.docker_image.usage_links:
            print(f"\t{usage_link}")
