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
    if os.path.exists('keymasters_keep'):
        shutil.rmtree('keymasters_keep')

if not os.path.exists('keymasters_keep'):
    zipfile.ZipFile('keymasters_keep.apworld').extractall('.')

for repo in config['game_repos']:
    repo_config = {
        'glob': '*.py',
        'skip': [],
    }
    if isinstance(repo, dict):
        repo_config.update(repo)
        repo = repo_config.pop('url')

    folder = repo.split('/')[-2] + '_' + repo.split('/')[-1]
    if not os.path.exists(folder):
        print(f"Cloning {repo} into {folder}")
        git(['clone', repo, folder], cwd='.')
    else:
        print(f"Updating {folder}")
        git_output(['pull'], cwd=folder)
    games = glob.glob(repo_config['glob'], root_dir=folder)
    for game in games:
        base_name = os.path.basename(game)
        if base_name in repo_config['skip']:
            print(f"Skipping {base_name} as per configuration")
            continue
        dest = os.path.join('keymasters_keep', 'games', base_name)
        if os.path.exists(dest):
            print(f"Updating {base_name} from {folder}")
            os.remove(dest)

        # We modify the game file to include the source repo at the top
        with open(os.path.join(folder, game), 'r', encoding='utf-8') as f:
            content = f.read()
        content = f"# Source: {repo}\n" + content
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(content)

added_games = []
shutil.copy('keymasters_keep.apworld', 'keymasters_keep-bundled.apworld')
with zipfile.ZipFile('keymasters_keep-bundled.apworld', 'a') as zipf:
    for game in glob.glob('*.py', root_dir='keymasters_keep/games'):
        path = f'keymasters_keep/games/{game}'
        if path in zipf.namelist():
            print(f"Game {path} already exists in the archive, skipping.")
            continue

        zipf.write(path, path)
        added_games.append(game)

print(f"Bundling complete. {len(added_games)} games are now bundled.")
with open('output.txt', 'w') as f:
    for game in added_games:
        f.write(f"{game}\n")
