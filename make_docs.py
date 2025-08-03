from collections.abc import Sequence
import os
import sys
import shutil
import random
import json
import typing
from typing import Any, Callable, Dict, List, Sequence, Tuple, Union


sys.path.append("archipelago")
sys.path.append("../archipelago")

if typing.TYPE_CHECKING:
    from keymasters_keep.game_objective_template import GameObjectiveTemplateData, GameObjectiveTemplate
    from keymasters_keep.game import Game

def converter(obj):
    if isinstance(obj, (set, frozenset)):
        return sorted(obj)

def main():
    import worlds
    source = worlds.WorldSource(os.path.abspath("keymasters_keep.apworld"), True, False)
    loaded = source.load()
    from worlds.keymasters_keep.game import AutoGameRegister
    from worlds.keymasters_keep.world import KeymastersKeepOptions

    games = []

    seed = random.Random()
    opts = KeymastersKeepOptions(**{option_key: option.from_any(option.default)
                                                 for option_key, option in KeymastersKeepOptions.type_hints.items()})
    for name, cls in AutoGameRegister.games.items():
        game = cls(random=seed, include_time_consuming_objectives=True, include_difficult_objectives=True, archipelago_options=opts)
        # print(f"Loaded game: {game.name} with options: {game.options_cls}")
        gamedat = expand_objectives(game)
        gamedat['name'] = name
        gamedat['file'] = game.__module__.split(".")[-1]
        games.append(gamedat)

    with open("objectives.json", "w", encoding="utf-8") as f:
        json.dump(games, f, indent=4, ensure_ascii=False, default=converter)
    os.makedirs("docs/games", exist_ok=True)
    for game in games:
        with open(os.path.join("docs", "games", f"{game['file']}.md"), "w", encoding="utf-8") as f:
            f.write(f"# {game['name']}\n\n")
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
                # f.write(f"  - Is Difficult: {objective['is_difficult']}\n")
                # f.write(f"  - Is Time Consuming: {objective['is_time_consuming']}\n")
            f.write("\n")
            for key, dataset in game['datasets'].items():
                f.write(f'[^{key}]: {", ".join([str(i) for i in dataset])}\n')
            pass
    pass

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
