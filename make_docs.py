import os
import sys
import random
import json
import textwrap
import typing
from typing import Any, Callable, Dict, List, Sequence, Union

import yaml


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
    from worlds.keymasters_keep.game import AutoGameRegister
    from worlds.keymasters_keep.world import KeymastersKeepOptions

    seed = random.Random()
    opts = KeymastersKeepOptions(**{option_key: option.from_any(option.default)
                                                 for option_key, option in KeymastersKeepOptions.type_hints.items()})

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
        games.append(gamedat)

def write_docs(games):
    with open('sources.json', 'r', encoding='utf-8') as f:
        sources = json.load(f)
        sources = {os.path.splitext(k.lower())[0]: v for k, v in sources.items()}
    os.makedirs("docs/games", exist_ok=True)
    for game in games:
        with open(os.path.join("docs", "games", f"{game['file']}.md"), "w", encoding="utf-8") as f:
            f.write(f"# {game['name']}\n\n")
            source = sources.get(game['file'], None)
            if source:
                f.write(f"Download: [{source}]({source})\n\n")
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

        evaluated_collection = collection[0]()
        if not evaluated_collection:
            raise Exception(f"Collection for key '{key}' is empty or invalid.")
        # example = ", ".join(str(value) for value in random.sample(*(evaluated_collection, k)))
        funcname = collection[0].__name__
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
