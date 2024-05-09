# Dockerfile (compose) scanner

## Build docker

```shell
docker build -t docker_scanner .
```

## Run docker

```shell
docker run -v ./dockerfiles/:/scan_dir:ro -v /var/run/docker.sock:/var/run/docker.sock --env scan_dir=/scan_dir docker_scanner
```
