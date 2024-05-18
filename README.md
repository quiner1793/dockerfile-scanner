# Dockerfile (compose) scanner

## Build docker

```shell
docker build -t quiner/docker_scanner:1.0.0 .
```

## Run docker

```shell
docker run -v ./:/scan_dir:ro -v /var/run/docker.sock:/var/run/docker.sock quiner/docker_scanner:1.0.0 
 ```