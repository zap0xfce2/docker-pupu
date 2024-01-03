# Docker-PuPu

A simple script to clone the contens of an docker repository to an remote repository.

## Requirements

- Python 3.x
- Crane executable
- Skopeo executable

## Setup

1. Download `crane` from [this github page](https://github.com/google/go-containerregistry) and put it in the same directory as the script.
2. Download `skopeo` from [this github page](https://github.com/containers/skopeo/releases) and put it in the same directory as the script.
3. Edit **source_registry** and **target_registry** in `docker-pupu.py`.

If you don't have two registries for testing, you can create them using:

```bash
docker run -d -p 5555:5000 --restart always --name registry1 registry:2
docker run -d -p 6666:5000 --restart always --name registry2 registry:2
```

## Run

To run the script, type:

```bash
chmod +x docker-pupu.py
./docker-pupu.py 
``````
