import os
import shutil
import subprocess
import yaml
import requests
import zipfile
import glob

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

if not os.path.exists('keymasters_keep.apworld'):
    print("Downloading keymasters_keep.apworld")
    download_file(config['apworld'], 'keymasters_keep.apworld')

if not os.path.exists('keymasters_keep'):
    zipfile.ZipFile('keymasters_keep.apworld').extractall('.')

for repo in config['game_repos']:
    folder = repo.split('/')[-2] + '_' + repo.split('/')[-1]
    if not os.path.exists(folder):
        print(f"Cloning {repo} into {folder}")
        git(['clone', repo, folder], cwd='.')
    else:
        print(f"Updating {folder}")
        git_output(['pull'], cwd=folder)
    games = glob.glob('*.py', root_dir=folder)
    for game in games:
        dest = os.path.join('keymasters_keep', 'games', game)
        if os.path.exists(dest):
            print(f"Updating {game} from {folder}")
            os.remove(dest)
        shutil.copy(os.path.join(folder, game), dest)

added_games = []
with zipfile.ZipFile('keymasters_keep.apworld', 'a') as zipf:
    for game in glob.glob('*.py', root_dir='keymasters_keep/games'):
        path = f'keymasters_keep/games/{game}'
        if path in zipf.namelist():
            print(f"Game {path} already exists in the archive, skipping.")
            continue

        zipf.write(path, path)
        added_games.append(game)

print(f"Bundling complete. {len(added_games)} games are now bundled.")
with open('bundled_games.txt', 'w') as f:
    for game in added_games:
        f.write(f"{game}\n")
