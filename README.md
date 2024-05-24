# Docker files scanner

## Program description

Docker scanner - program that can give STIG recommendations based on data parsed from found files with Docker images.
The main features are:

* Extracting images from Dockerfile, Docker compose, k8s, Helm, Terraform files;
* Dynamic detection of base image based on SHA256 hashes without running the actual image;
* Automatic STIG scan using oscap command.

## Repository content

### Artifacts

This directory contain parsed files with base docker hashes: compressed + initial versions. Moreover, it contains script
and description of how to get this artifacts by yourself.

### Bin

Contains executables that are used in project

The most important is oscap - binary for running oscap commands

### Outputs

Contains examples of program outputs and oscap reports

### Scan dir

Contains examples of files that can be parsed for with docker images

* Docker compose
* Dockerfile
* k8s
* Helm
* Terraform

### Scap content

Contains docker image to stig mapping and stig profiles

### Src

Contains source code of the program, oscap_docker_python library and experiment script with experiment description file

## Run locally

Create virtual env:

```shell
python3 -m venv .venv
```

Activate venv:

```shell
source ./.venv/bin/activate
```

Run main script with sudo:

```shell
cd src/
sudo RECURSE=true BASE_IMAGE=true INSPECT_INFO=true STIGS_SCAN=true ../.venv/bin/python3 main.py "path_to_scan_dir"
```

## Dockerize

The docker version currently can not run oscap scan due to permission setup.
This option should be further developed.

### Build docker

```shell
docker build -t quiner/docker_scanner:1.0.0 .
```

### Run docker

Run without RUNTIME_INFO and STIGS_SCAN

```shell
docker run -v ./:/scan_dir:ro -v /var/run/docker.sock:/var/run/docker.sock -e RECURSE=true \
-e BASE_IMAGE=true -e INSPECT_INFO=true quiner/docker_scanner:1.0.0 
 ```
