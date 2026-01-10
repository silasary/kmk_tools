import os
import sys
import random
import json
import textwrap
import typing
from typing import Any, Callable, Dict, List, Sequence, Union

import yaml
from traceback_with_variables import activate_by_import


sys.path.append("archipelago")
sys.path.append("../archipelago")

if typing.TYPE_CHECKING:
    from keymasters_keep.game_objective_template import GameObjectiveTemplate
    from keymasters_keep.game import Game

def converter(obj):
    if isinstance(obj, (set, frozenset)):
        return sorted(obj)

def main():
    import worlds
    source = worlds.WorldSource(os.path.abspath("keymasters_keep.apworld"), True, False)
    source.load()

    games = []
    gather_data(games)

    with open("objectives.json", "w", encoding="utf-8") as f:
        json.dump(games, f, indent=4, ensure_ascii=False, default=converter)

    write_docs(games)
    pass

def gather_data(games):
    import re
    from worlds.keymasters_keep.game import AutoGameRegister
    from worlds.keymasters_keep.world import KeymastersKeepOptions

    seed = random.Random()
    opt_dict = {option_key: option.from_any(option.default)
                    for option_key, option in KeymastersKeepOptions.type_hints.items()}
    with open("yaml_settings.yaml", "r", encoding="utf-8") as f:
        yaml_opts = yaml.safe_load(f)
        for key, value in yaml_opts.items():
            if key in opt_dict:
                if opt_dict[key].value == value:
                    print(f"Notice: Option '{key}' already set to {value}.")
                opt_dict[key].value = value
            else:
                print(f"Warning: Unknown option '{key}' in yaml_settings.yaml, ignoring.")

    opts = KeymastersKeepOptions(**opt_dict)

    for name, cls in AutoGameRegister.games.items():
        game = cls(random=seed, include_time_consuming_objectives=True, include_difficult_objectives=True, archipelago_options=opts)
        # print(f"Loaded game: {game.name} with options: {game.options_cls}")
        if not game.should_autoregister:
            print(f"Game {game.name} does not have auto-registration enabled, skipping.")
            continue
        gamedat = expand_objectives(game)
        gamedat['name'] = name
        gamedat['file'] = game.__module__.split(".")[-1].lower()
        yaml_keys = game.options_cls.__annotations__.keys()
        if yaml_keys:
            gopts = opts.as_dict(*yaml_keys)
            gamedat['yaml'] = yaml.dump(gopts)

        gamedat['doc'] = sys.modules[game.__module__].__doc__
        if game.__doc__ is not None:
            # Remove leading spaces in docstring to disable code block formatting by Markdown
            gamedat['gamedoc'] = re.sub(r"^ {4}", "", game.__doc__, flags=re.MULTILINE)
        gamedat['platforms'] = [game.platform.value]
        if game.platforms_other:
            gamedat['platforms'].extend([p.value for p in game.platforms_other])
        games.append(gamedat)

def write_docs(games):
    with open('sources.json', 'r', encoding='utf-8') as f:
        sources = json.load(f)
        sources = {os.path.splitext(k.lower())[0]: v for k, v in sources.items()}
    by_platform = {}
    os.makedirs("docs/games", exist_ok=True)
    for game in games:
        with open(os.path.join("docs", "games", f"{game['file']}.md"), "w", encoding="utf-8") as f:
            f.write(f"# {game['name']}\n\n")
            source = sources.get(game['file'], None)
            if source:
                f.write(f"Download: [{source}]({source})\n\n")
            # While interchangeable, the game docstring takes precedence over the file docstring, as the game docstring is more likely to describe the game (Archipelago standard) while the file docstring is more likely to describe the implementation
            if 'gamedoc' in game.keys():
                f.write(f"---\n\n{game['gamedoc']}\n\n")
            if game['doc'] is not None:
                f.write(f"---\n\n{game['doc']}\n\n")
            yaml_content = game.get('yaml', None)
            if yaml_content:
                f.write('??? "Default Yaml Options"\n\n')
                f.write("    Generated with the following options:\n")
                f.write("    ```yaml\n")
                f.write(textwrap.indent(yaml_content, "    "))
                f.write("    ```\n\n")
            f.write("## Objectives\n\n")
            for objective in game['objectives']:
                label = objective['label']
                is_difficult = objective['is_difficult']
                is_time_consuming = objective['is_time_consuming']
                for key, value in objective['data'].items():
                    label = label.replace(key, f"{key}[^{value}]")
                f.write(f"- {label}")
                if is_difficult:
                    f.write("⚠️")
                if is_time_consuming:
                    f.write("⏳")
                f.write("\n")

            f.write("\n")
            for key, dataset in game['datasets'].items():
                f.write(f'[^{key}]: {", ".join([str(i) for i in dataset])}\n')

        for platform in game['platforms']:
            by_platform.setdefault(platform, []).append(game)

    os.makedirs("docs/platforms", exist_ok=True)
    plat_names = get_comments_from_enums()
    for platform, games in by_platform.items():
        name = plat_names.get(platform, platform)
        header = f"# {name}\n\n"
        if os.path.exists(os.path.join("docs", "platforms", f"{platform}.md")):
            with open(os.path.join("docs", "platforms", f"{platform}.md"), "r", encoding="utf-8") as f:
                text = f.read()
                text = text.split("## Games")[0]  # Keep the header only
        with open(os.path.join("docs", "platforms", f"{platform}.md"), "w", encoding="utf-8") as f:
            f.write(header)
            f.write("## Games\n\n")
            for game in games:
                f.write(f"- [{game['name']}](../games/{game['file']}.md)\n")

def get_comments_from_enums() -> Dict[str, str]:
    plats = {}
    import tokenize
    with open('keymasters_keep/enums.py') as f:
        tokens = tokenize.generate_tokens(f.readline)
        key = None
        comment = None
        for tok in tokens:
            if tok.type == tokenize.STRING:
                key = tok.string.strip('"\'')
            elif tok.type == tokenize.COMMENT:
                comment = tok.string
                plats[key] = comment.lstrip('# ').strip()

    return plats

def expand_objectives(game: "Game"):
    objectives = []
    datasets = {}
    for o in game.game_objective_templates():
        objectives.append(expand_objective(o, datasets))
        pass

    data = {"game": game.name, "objectives": objectives, "datasets": datasets}
    return data

def expand_objective(o: "GameObjectiveTemplate", datasets: Dict[str, Any]) -> Dict[str, Any]:
    game_objective = o.label

    key: str
    collection: tuple[Callable[[], Union[List[Any], range]], Union[int, Sequence[int], Callable[[], int]]]
    data = {}
    for key, collection in o.data.items():
        # k: int

        # if isinstance(collection[1], Sequence):
        #     k = random.choice(collection[1])
        # elif callable(collection[1]):
        #     k = collection[1]()
        # else:
        #     k = collection[1]

        if isinstance(collection[0], range):
            evaluated_collection = list(collection[0])
        elif callable(collection[0]):
            evaluated_collection = collection[0]()
        else:
            evaluated_collection = collection[0]

        if not evaluated_collection:
            raise Exception(f"Collection for key '{key}' is empty or invalid.")
        # example = ", ".join(str(value) for value in random.sample(*(evaluated_collection, k)))
        if hasattr(collection[0], '__name__'):
            funcname = collection[0].__name__
        else:
            funcname = o.__class__.__name__ + "_" + key
        if funcname == "<lambda>":
            funcname = f"lambda_{collection[0].__code__.co_firstlineno}"
        data[key] = funcname
        datasets[funcname] = sorted(evaluated_collection)

    return {
            "label": game_objective,
            "is_difficult": o.is_difficult,
            "is_time_consuming": o.is_time_consuming,
            "data": data,
        }

if __name__ == "__main__":
    main()
