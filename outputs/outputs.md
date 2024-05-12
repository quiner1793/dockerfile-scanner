# Example outputs

## Output of main.py
```shell
sudo ../.venv/bin/python3 main.py
Start directory traversing
Detected Dockerfile: oraclelinux.Dockerfile
Detected Dockerfile: python.Dockerfile
Detected Dockerfile: ubuntu.Dockerfile
Detected Dockerfile: golang.Dockerfile
Detected Dockerfile: almalinux.Dockerfile
Finish directory traversing

Start image filtering
Found 5 unique docker images
Finish image filtering

Start image analytics
Analyzing docker image: oraclelinux:8
Running given image in a temporary container ...
Docker container tmp_oscap_86a074cc-10a5-11ef-a14b-4cd577f12e99 ready to be scanned.
Temporary container tmp_oscap_86a074cc-10a5-11ef-a14b-4cd577f12e99 cleaned
Analyzing docker image: python:3.11
Running given image in a temporary container ...
Docker container tmp_oscap_8f45b51a-10a5-11ef-a14b-4cd577f12e99 ready to be scanned.
Temporary container tmp_oscap_8f45b51a-10a5-11ef-a14b-4cd577f12e99 cleaned
Analyzing docker image: ubuntu:18.04
Running given image in a temporary container ...
Docker container tmp_oscap_9773b8a4-10a5-11ef-a14b-4cd577f12e99 ready to be scanned.
Temporary container tmp_oscap_9773b8a4-10a5-11ef-a14b-4cd577f12e99 cleaned
Analyzing docker image: golang:1.21-alpine
Running given image in a temporary container ...
Docker container tmp_oscap_9f7db91e-10a5-11ef-a14b-4cd577f12e99 ready to be scanned.
expected str, bytes or os.PathLike object, not NoneType
Analyzing docker image: almalinux:8
Running given image in a temporary container ...
Docker container tmp_oscap_a08ddd0c-10a5-11ef-a14b-4cd577f12e99 ready to be scanned.
Temporary container tmp_oscap_a08ddd0c-10a5-11ef-a14b-4cd577f12e99 cleaned
Finish image analytics

Start generating report

Analytics for docker image: oraclelinux:8:
Found base image: None
Found inspect info:
        OS: linux
        Architecture: amd64
Found available STIGs:
        STIG name: Oracle Linux 8
        Profile: xccdf_org.ssgproject.content_profile_anssi_bp28_enhanced
        Datastream ID: scap_org.open-scap_datastream_from_xccdf_ssg-ol8-xccdf.xml
        XCCDF ID: scap_org.open-scap_cref_ssg-ol8-xccdf.xml
        SCAP file: ssg-oraclelinux8-ds.xml
        OSCAP passed: 0
        OSCAP failed: 0
        OSCAP not_applicable: 239
Image usage links:
        /home/quiner/PycharmProjects/dockerfile_scanner/dockerfiles/oraclelinux.Dockerfile

Analytics for docker image: python:3.11:
Found base image: debian:12.5
Found inspect info:
        OS: linux
        Architecture: amd64
Found available STIGs:
        STIG name: None
        Profile: xccdf_org.ssgproject.content_profile_anssi_bp28_enhanced
        Datastream ID: scap_org.open-scap_datastream_from_xccdf_ssg-debian12-xccdf.xml
        XCCDF ID: scap_org.open-scap_cref_ssg-debian12-xccdf.xml
        SCAP file: ssg-debian12-ds.xml
        OSCAP passed: 12
        OSCAP failed: 7
        OSCAP not_applicable: 90
Image usage links:
        /home/quiner/PycharmProjects/dockerfile_scanner/dockerfiles/python.Dockerfile

Analytics for docker image: ubuntu:18.04:
Found base image: None
Found inspect info:
        OS: linux
        Architecture: amd64
Found available STIGs:
        STIG name: Ubuntu 18.04
        Profile: xccdf_org.ssgproject.content_profile_anssi_np_nt28_average
        Datastream ID: scap_org.open-scap_datastream_from_xccdf_ssg-ubuntu1804-xccdf.xml
        XCCDF ID: scap_org.open-scap_cref_ssg-ubuntu1804-xccdf.xml
        SCAP file: ssg-ubuntu1804-ds.xml
        OSCAP passed: 20
        OSCAP failed: 1
        OSCAP not_applicable: 19
Image usage links:
        /home/quiner/PycharmProjects/dockerfile_scanner/dockerfiles/ubuntu.Dockerfile

Analytics for docker image: golang:1.21-alpine:
Found base image: alpine:3.16
Found inspect info:
        OS: linux
        Architecture: amd64
Found available STIGs:
        STIG name: Operating System Security Requirements Guide (UNIX Version)
        Profile: None
        Datastream ID: None
        XCCDF ID: None
        SCAP file: None
        OSCAP passed: None
        OSCAP failed: None
        OSCAP not_applicable: None
Image usage links:
        /home/quiner/PycharmProjects/dockerfile_scanner/dockerfiles/golang.Dockerfile

Analytics for docker image: almalinux:8:
Found base image: almalinux:8.9
Found inspect info:
        OS: linux
        Architecture: amd64
Found available STIGs:
        STIG name: Red Hat Enterprise Linux 8
        Profile: xccdf_org.ssgproject.content_profile_anssi_bp28_enhanced
        Datastream ID: scap_org.open-scap_datastream_from_xccdf_ssg-almalinux8-xccdf.xml
        XCCDF ID: scap_org.open-scap_cref_ssg-almalinux8-xccdf.xml
        SCAP file: ssg-almalinux8-ds.xml
        OSCAP passed: 0
        OSCAP failed: 0
        OSCAP not_applicable: 239
Image usage links:
        /home/quiner/PycharmProjects/dockerfile_scanner/dockerfiles/almalinux.Dockerfile
Finish generating report
```