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
        objectives = expand_objectives(game)
        games.append({"game": name, "objectives": objectives})

    with open("objectives.json", "w", encoding="utf-8") as f:
        json.dump(games, f, indent=4, ensure_ascii=False)
    pass

def expand_objectives(game: "Game"):
    objectives = []
    for o in game.game_objective_templates():
        objectives.append(expand_objective(o))
        pass


    return objectives

def expand_objective(o: "GameObjectiveTemplate"):
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
        data[key] = sorted(evaluated_collection)
        assert isinstance(data[key], list), f"Data for key '{key}' is not a list: {data[key]}"

    return {
            "label": game_objective,
            "is_difficult": o.is_difficult,
            "is_time_consuming": o.is_time_consuming,
            "data": data,
        }

if __name__ == "__main__":
    main()
