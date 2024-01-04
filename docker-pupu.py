#!/usr/bin/python3

# We need crane & skopeo as an executable binary in the same directory
# https://github.com/google/go-containerregistry/releases
# https://github.com/containers/skopeo/releases
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
repo_list = subprocess.run(
    ["./crane", "catalog", source_registry, "--insecure"],
    capture_output=True,
    text=True,
)
repo_array = repo_list.stdout.strip().split()

# Process each repo
for repo in repo_array:
    # Fetch tags for the current repo (assuming they are separated by spaces)
    tag_list = subprocess.run(
        ["./crane", "ls", f"{source_registry}/{repo}", "--insecure"],
        capture_output=True,
        text=True,
    )
    tag_array = tag_list.stdout.strip().split()

    # Sync every tag with skopeo
    for tag in tag_array:
        print(f"Uploading {repo}:{tag} to {target_registry}...")
        copy_command = [
            "./skopeo",
            "copy",
            "--quiet",
            f"docker://{source_registry}/{repo}:{tag}",
            f"docker://{target_registry}/{repo}:{tag}",
        ]
        subprocess.run(copy_command)
        verify_source_command = [
            "./skopeo",
            "inspect",
            f"docker://{source_registry}/{repo}:{tag}",
            "--format",
            "'{{.Digest}}'",
        ]
        verify_target_command = [
            "./skopeo",
            "inspect",
            f"docker://{target_registry}/{repo}:{tag}",
            "--format",
            "'{{.Digest}}'",
        ]
        checksum_source = subprocess.run(
            verify_source_command, capture_output=True, text=True
        ).stdout.strip()
        checksum_target = subprocess.run(
            verify_target_command, capture_output=True, text=True
        ).stdout.strip()

        # Retry the copy if there is a checksum mismatch
        retry_limit = 3
        retries = 0
        while checksum_source != checksum_target and retries < retry_limit:
            print(f"Checksum mismatch for {repo}:{tag}. Retrying...")

            delete_command = [
                "./skopeo",
                "delete",
                f"docker://{target_registry}/{repo}:{tag}",
            ]
            subprocess.run(delete_command)

            subprocess.run(copy_command)

            checksum_source = subprocess.run(
                verify_source_command, capture_output=True, text=True
            ).stdout.strip()
            checksum_target = subprocess.run(
                verify_target_command, capture_output=True, text=True
            ).stdout.strip()

            retries += 1

        if checksum_source != checksum_target:
            print(
                f"Failed to correctly sync {repo}:{tag} after {retry_limit} attempts."
            )
            exit()

# Stop timer and print summary
stop_timer = timeit.default_timer()
duration = round(stop_timer - start_timer, 2)
print(
    f"Registry sync from {source_registry} to {target_registry} completed in {duration:.0f} seconds!"
)
