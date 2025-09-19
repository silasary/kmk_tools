import hashlib
import json
import os
import shutil
import zipfile
import glob

from common import config, download_file, git, git_output

if not os.path.exists('keymasters_keep_unmodified.apworld'):
    print("Downloading keymasters_keep.apworld")
    download_file(config['apworld'], 'keymasters_keep_unmodified.apworld')
    if os.path.exists('keymasters_keep'):
        shutil.rmtree('keymasters_keep')

if not os.path.exists('keymasters_keep'):
    zipfile.ZipFile('keymasters_keep_unmodified.apworld').extractall('.')

sources: dict[str, str] = {}
skipped = {}

use_submodules = config.get('use_submodules', True)

def should_skip_base_name(repo_config, game, folder) -> bool:
    base_name = os.path.basename(game)
    if isinstance(repo_config['skip'], list):
        return base_name in repo_config['skip']
    elif isinstance(repo_config['skip'], dict):
        skip_hash = repo_config['skip'].get(base_name)
        if skip_hash is True:
            return True
        with open(os.path.join(folder, base_name), 'rb') as f:
            file_hash = str(hashlib.sha256(f.read()).hexdigest())
        if skip_hash == file_hash:
            return True
    return False

for repo in config['game_repos']:
    repo_config = {
        'glob': '*.py',
        'skip': [],
    }
    if isinstance(repo, dict):
        repo_config.update(repo)
        repo = repo_config.pop('url')

    repo = repo.strip().rstrip('/')
    folder = os.path.join('submodules', repo.split('/')[-2].lower() + '_' + repo.split('/')[-1].lower())
    if not os.path.exists(folder):
        print(f"Cloning {repo} into {folder}")
        if use_submodules:
            git(['submodule', 'add', repo, folder], cwd='.')
        else:
            git(['clone', repo, folder], cwd='.')
    elif not use_submodules:
        # If we're not using submodules to lock to specific commits, grab the latest commit
        print(f"Updating {folder}")
        git_output(['pull'], cwd=folder)

    games = glob.glob(repo_config['glob'], root_dir=folder)
    if not games:
        raise Exception(f"No games found in {folder} matching {repo_config['glob']}")
    for game in games:
        base_name = os.path.basename(game)
        dest = os.path.join('keymasters_keep', 'games', base_name)

        if should_skip_base_name(repo_config, game, folder):
            if repo != 'https://github.com/SerpentAI/KeymastersKeepGameArchive':
                print(f"Skipping {base_name} as per configuration")
                with open(os.path.join(folder, game), 'rb') as f:
                    file_hash = str(hashlib.sha256(f.read()).hexdigest())
                skipped[base_name] = file_hash
            if os.path.exists(dest):
                os.unlink(dest)
            continue
        if os.path.exists(dest):
            old_source = sources.get(base_name, None)
            if old_source and old_source != "https://github.com/SerpentAI/KeymastersKeepGameArchive":
                print(f"WARNING: Game {base_name} already exists from {old_source}, cannot overwrite with {repo}")
            # print(f"Updating {base_name} from {folder} (was {old_source})")
            os.remove(dest)
        sources[base_name] = repo

        # We modify the game file to include the source repo at the top
        with open(os.path.join(folder, game), 'r', encoding='utf-8') as f:
            content = f.read()
        content = f"# Source: {repo}\n" + content
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(content)

    with open('sources.json', 'w', encoding='utf-8') as f:
        json.dump(sources, f, indent=4, ensure_ascii=False)

added_games = []
shutil.copy('keymasters_keep_unmodified.apworld', 'keymasters_keep.apworld')
with zipfile.ZipFile('keymasters_keep.apworld', 'a') as zipf:
    for game in glob.glob('*.py', root_dir='keymasters_keep/games'):
        path = f'keymasters_keep/games/{game}'
        if path in zipf.namelist():
            print(f"Game {path} already exists in the archive, skipping.")
            continue

        zipf.write(path, path)
        added_games.append(game)

print(f"Bundling complete. {len(added_games)} games are now bundled.")
with open('output.txt', 'w') as f:
    f.write("Bundled Games:\n")
    for game in added_games:
        f.write(f"{game}\n")
    f.write("\n")
    f.write(f"Total games bundled: {len(added_games)}\n")
    if skipped:
        f.write("\n\nSkipped Games:\n")
        for game, file_hash in skipped.items():
            f.write(f"{game} (hash: {file_hash})\n")
        f.write(f"\nTotal games skipped: {len(skipped)}\n")
