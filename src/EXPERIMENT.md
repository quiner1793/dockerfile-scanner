# Experiment

This manifest describes the process of precision analysis of the program on determining the platform information
of Docker images based on layer hashes.

## Obtaining experiment exemplars

To prepare experiment candidates, we analyzed the lists of most popular Docker images. We have chosen 11 Docker Official Images of different
versions.

This list includes:

* Alpine
* BusyBox
* Nginx
* Ubuntu
* Python
* PostgreSQL
* Redis
* Apache httpd
* Node
* MongoDB
* RabbitMQ

We selected versions from recent minor versions with the penultimate patch
version. We used this approach, because official images are updating constantly,
and the penultimate patch version is the one that is not updated, and its layer
hashes are in our database.

## Prepare base image mapping

The second phase was manual image analysis to determine the base platform. For this phase, we ran each image using
the docker run -it image name sh command.
Then we extracted /etc/os-release or /etc/debian version information based on distribution.

## Analyse tool results

The final phase was executing the method from our program to determine the base image.
This was implemented in experiment.py file.

## Conclusion

Based on experiment results, our program demonstrates strong performance in identifying platform names and major versions.
However, it requires improvements in its handling of minor versions for specific platforms, like Alpine. The
cornerstone of this problem lies in the algorithm of sorting and filtering of base layers hashes.
