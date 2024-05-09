import json
from sys import argv

import docker


class ImageNotFound(Exception):
    pass


class ReverseDockerfile:
    def __init__(self, image_id: str):
        super(ReverseDockerfile, self).__init__()
        self.commands = []
        self.cli = docker.APIClient(base_url='unix://var/run/docker.sock')
        self._get_image(image_id)
        self.hist = self.cli.history(self.img['RepoTags'][0])
        self._parse_history()
        self.commands.reverse()

    def _print_commands(self):
        for i in self.commands:
            print(i)

    def _get_image(self, img_hash):
        images = self.cli.images()
        for i in images:
            if img_hash in i['Id']:
                self.img = i
                return
        raise ImageNotFound("Image {} not found\n".format(img_hash))

    def _insert_step(self, step):
        if "#(nop)" in step:
            to_add = step.split("#(nop) ")[1]
        else:
            to_add = ("RUN {}".format(step))
        to_add = to_add.replace("&&", "\\\n    &&")
        self.commands.append(to_add.strip(' '))

    def _parse_history(self, rec=False):
        first_tag = False
        actual_tag = False
        for i in self.hist:
            if i['Tags']:
                actual_tag = i['Tags'][0]
                if first_tag and not rec:
                    break
                first_tag = True
            self._insert_step(i['CreatedBy'])
        if not rec:
            self.commands.append("FROM {}".format(actual_tag))


def find_base_layer(file_hash: str):
    with open("../artifacts/base_files.json", "r") as f:
        base_files = json.load(f)
        for base_name, base_values in base_files.items():
            if file_hash in base_values:
                return base_name

        return "Not found"


if __name__ == '__main__':
    reverser = ReverseDockerfile(image_id=argv[-1])
    file = (reverser.commands[1].split()[1].split(":")[1])
    print(find_base_layer(file_hash=file))
