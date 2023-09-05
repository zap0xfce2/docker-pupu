#!/usr/bin/python3

# We need crane as an executable binary in the same directory
# https://github.com/google/go-containerregistry/blob/main/cmd/crane/doc/crane.md
import subprocess
import timeit

# Source and target registries
source_registry = "localhost:5555"
target_registry = "localhost:6666"

# Print info and start timer
print(f"Starting registry sync from {source_registry} to {target_registry}!")
start_timer = timeit.default_timer()
print("\n")

# Read repos from source registry
repo_list = subprocess.run(["./crane", "catalog", source_registry, "--insecure"], capture_output=True, text=True)
repo_array = repo_list.stdout.strip().split()

# Process each repo
for repo in repo_array:

    # Fetch tags for the current repo (assuming they are separated by spaces)
    tag_list = subprocess.run(["./crane", "ls", f"{source_registry}/{repo}", "--insecure"], capture_output=True, text=True)
    tag_array = tag_list.stdout.strip().split()

    # Pull, retag, and push all tags for the repo
    for tag in tag_array:
        # Pull image from source registry
        print(f"Downloading: {repo}:{tag} from {source_registry}...")
        subprocess.run(["docker", "pull", f"{source_registry}/{repo}:{tag}"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        # Retag image for target registry
        print(f"Retagging from {source_registry}/{repo}:{tag} to {target_registry}/{repo}:{tag}")
        subprocess.run(["docker", "tag", f"{source_registry}/{repo}:{tag}", f"{target_registry}/{repo}:{tag}"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        # Push image to target registry
        print(f"Uploading {repo}:{tag} to {target_registry}...")
        subprocess.run(["docker", "push", f"{target_registry}/{repo}:{tag}"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        
        # Remove image from local storage
        # It's better to remove everything as leftovers can cause errors if the script is interrupted
        print(f"Cleaning up...\n")
        subprocess.run(["docker", "image", "prune", "--all", "--force"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

# Stop timer and print summary
stop_timer = timeit.default_timer()
duration = round(stop_timer - start_timer, 2)
print(f"Registry sync from {source_registry} to {target_registry} completed in {duration:.0f} seconds!")
