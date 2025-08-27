import subprocess
import requests
import yaml


def download_file(url: str, dest: str) -> None:
    """Download a file from a URL to a destination path."""
    print(f"Downloading {url} to {dest}")
    response = requests.get(url)
    if response.status_code == 200:
        with open(dest, 'wb') as file:
            file.write(response.content)
    else:
        raise Exception(f"Failed to download {url}: {response.status_code}")


def git(args: list[str], cwd: str) -> int:
    """Run a git command."""
    print(f"Running git {' '.join(args)} in {cwd}")
    try:
        subprocess.run(["git", *args], cwd=cwd, check=True)
        return 0
    except subprocess.CalledProcessError as e:
        return e.returncode


def git_output(args: list[str], cwd: str) -> str:
    """Run a git command and return its output."""
    # print(f"Running git {' '.join(args)} in {cwd}")
    try:
        result = subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(f"Git command failed: {e}")


with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
