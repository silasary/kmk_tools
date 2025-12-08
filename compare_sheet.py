import csv
import requests
import yaml

url = "https://docs.google.com/spreadsheets/d/1qhmvUi4UEN5M2zH3SVUOgDkW6jZL2icZ2VcIf123z9Q/export?format=csv"

sheet = requests.get(url, allow_redirects=True)
data = csv.reader(sheet.text.splitlines())


sheet_repos = set()

for row in data:
    if (repo := row[1]).startswith("https://github.com/"):
        if "/tree/" in repo:
            repo = repo.split("/tree/")[0]
        if "/blob/" in repo:
            repo = repo.split("/blob/")[0]
        sheet_repos.add(repo.strip().rstrip("/"))


with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

config_repos = set()

for repo in config["game_repos"]:
    if isinstance(repo, dict):
        repo = repo.pop("url")

    repo = repo.strip().rstrip("/")
    config_repos.add(repo)


if sheet_repos != config_repos:
    print("Repositories in the sheet do not match those in config.yaml")
    print("Repositories missing in config.yaml:")
    for repo in sheet_repos - config_repos:
        print(f"  {repo}")
    print("Repositories missing in the sheet:")
    for repo in config_repos - sheet_repos:
        print(f"  {repo}")
else:
    print("Repositories in the sheet match those in config.yaml")
    print("All repositories are accounted for.")
