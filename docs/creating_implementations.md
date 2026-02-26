# Creating KMK Implementations

This document is intended teach you how to create a basic game implementation for Keymaster's Keep (KMK).

## Things to Know Before Getting Started

- I (deyoungbryce) am by no means an expert on Keymaster's Keep, nor Python coding in general. I have, however, been successful in creating multiple working KMK implementations and this my way of sharing that knowledge.
- This guide is **NOT** intended to teach the ins and outs of Python coding and will require some outside learning to achieve anything beyond the scope of what is shared in the template project.
- There are a plethora of playable game implementations, all of which can be found through the various repositories linked in **this codex** and the [KMK Discord thread](https://discord.com/channels/731205301247803413/1321323711676284939), that can be used as a point of reference for creating your own implementation. When worst comes to worst, just look at how someone else did it.
- This guide is intended to be able to teach you how to create an implementation from scratch, but a [template implementation](https://github.com/deyoungbryce/KeymastersKeepGames/blob/main/template/template_game.py) has been provided and will be referenced throughout the guide as well.

## Materials Required

- IDE capable of linting Python code
    - Recommended: [Visual Studio Code](https://code.visualstudio.com/) w/ [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) or [PyCharm](https://www.jetbrains.com/pycharm/)
- [Github](https://github.com/) account
    - Only needed if you want to share your implementations publicly.
    - This guide will not go over how to create a Github repo and/or how to share your implementations on said repo.

## Getting Started

This section will go over the layout and basic setup of an implementation. It will follow in order of how the template is laid out.

### Imports

As with any project, KMK implementations have a few necessary imports:

```python
from __future__ import annotations
from dataclasses import dataclass
import functools
from Options import Toggle, OptionSet
from typing import List, Dict, Set
from ..enums import KeymastersKeepGamePlatforms
from ..game import Game
from ..game_objective_template import GameObjectiveTemplate
```

I'm not going to go into detail on what these are all used for (you'll kinda get to seeing them as we go), but just know that they are all necessary or, at the very least, useful.

??? "Import warnings?"
    Some of these imports will get flagged as bad imports because they are importing from a file that is part of core KMK or Archipelago codebases. This is normal. (You can use the [BasedPyright extension](https://marketplace.visualstudio.com/items?itemName=detachhead.basedpyright) to add comments that ignore these warnings.)

### Options Dataclass

This is a dataclass consisting of all of the Archipelago Options that are specific to your game implementation. Example from the template:

```python
@dataclass
class TemplateArchipelagoOptions:
    template_include_hard_levels: TemplateIncludeHardLevels
    template_dlc_owned: TemplateDLCOwned
```

In the above example, we have a class that is set up for Archipelago Options for the game "Template" and a couple of options which we will go over later.

??? "No Archipelago options?"
    If your game has **NO** Archipelago options, you **STILL** need an options dataclass, but you can just put `pass` in place of options.

### Main Class

The main class for the project is declared as the following, where `Template` is replaced with your game's name.

```python
class TemplateGame(Game):
```

There are a few necessary variables that need to be defined at the start of this class to give KMK some basic info about your game:

- `name` - The name of your game.
- `platform` - The main platform that you used to base your implementation off of.
- `platforms_other` - A list of any other platforms that the game is playable on.
- `is_adult_only_or_unrated` - Whether or not the game is adult-only or unrated.
- `options_cls` - Defined as your options dataclass.

Example from the template:

```python
name = "Template"
platform = KeymastersKeepGamePlatforms.PC
platforms_other = [
    KeymastersKeepGamePlatforms.AND,
    KeymastersKeepGamePlatforms.IOS,
    KeymastersKeepGamePlatforms.PS4,
    KeymastersKeepGamePlatforms.PS5,
    KeymastersKeepGamePlatforms.SW,
    KeymastersKeepGamePlatforms.SW2,
    KeymastersKeepGamePlatforms.XONE,
    KeymastersKeepGamePlatforms.XSX,
]
is_adult_only_or_unrated = False
options_cls = TemplateArchipelagoOptions
```

I've included some of the most common platform codes in the template, but a full list of platform codes can be found in [`enums.py`](https://github.com/silasary/Archipelago/blob/keymasters_keep/worlds/keymasters_keep/enums.py).

The main class is also where we will have basic methods for creating objectives and the data to pull from to create those objectives.

- Datasets - The actual datasets that the game objective templates will pull from to create objectives.
- Game Objective Templates - The templates that all of the objectives for your game will be created off of.
    ```python
    def game_objective_templates(self) -> List[GameObjectiveTemplate]:
        return [
            # Game objective templates go here
        ]
    ```
- Optional Game Constraints - When objectives are generated for your game, these optional constraints can be placed on all of the objectives within a given keep area. A random one appears above the objectives.
    ```python
    def optional_game_constraint_templates(self) -> List[GameObjectiveTemplate]:
        return [
            # Game constraint templates go here
        ]
    ```

### Individual Options Classes

Each individual Archipelago option that your game has must also have its own class associated with it.

The options classes are set up with a name and option type, and contain a description, display name, and any other necessary variables for that option type. Example from the template:

```python
class TemplateIncludeHardLevels(Toggle):
    """
    Indicates whether to include hard levels when generating Template objectives.
    """
    display_name = "Template Include Hard Levels"
```

In the above example we have a class for the "Template" game option "Template Include Hard Levels" with the option type `Toggle`.

The docstring within the `"""` block is what will be presented in the YAML as the option description.

These option classes are then used to define each option within the options dataclass explained earlier in this document.

Option class types (such as the `Toggle` seen above) are a core Archipelago function, and thus, more information can be found within the Archipelago documentation. The option types can be found in [this document detailing the Archipelago Options API](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/options%20api.md).

This guide will just be going over the `Toggle` option type, however, the template includes the use of an `OptionSet`, another one of the more common option types.

## Datasets

Datasets are the lists of various weapons, characters, levels, etc. within your game that will be pulled from to plug into the game objective templates that you create. We will go over two types of datasets in this document: *static methods* and *cached properties*.

### Static Methods

Static methods are basic methods that return a list of data. Example from the template:

```python
@staticmethod
def upgrades() -> List[str]:
    return ["Upgrade 1", "Upgrade 2", "Upgrade 3"]
```

The above example shows a method named `upgrades()` which returns a list of strings with the names of upgrades.

### Cached Properties

These are a bit more complicated and are used when we need to combine lists based on whether or not an option is selected. Example from the template:

```python
@functools.cached_property
def levels_base(self) -> List[str]:
    return ["Level 1", "Level 2", "Level 3",]

@functools.cached_property
def hard_levels(self) -> List[str]:
    return ["Hard Level 1", "Hard Level 2", "Hard Level 3"]
```

Above we see two properties that look quite similar to the static method example: one for normal levels (`levels_base()`) and one for hard levels (`hard_levels()`).

Before we get to combining these two lists, we need an property that holds the value of what the necessary option is set to. For this example, we will use the aforementioned "Include Hard Levels" option:

```python
@property
def include_hard_levels(self) -> bool:
    return bool(self.archipelago_options.template_include_hard_levels.value)
```

Above we have the property for `include_hard_levels` which returns the boolean value of the `template_include_hard_levels` option as defined in the options dataclass.

Now we can create a new method that combines the lists, provided that the option is set to `true`.

```python
def levels(self) -> List[str]:
    levels: List[str] = self.levels_base[:]
    # Check if hard levels are included, and include them if so
    if self.include_hard_levels:
        levels.extend(self.hard_levels[:])
    return sorted(levels)
```

In the example above, we have the method `levels()` which returns a sorted list of the levels. Within the method, we initialize the variable `levels` as the list `levels_base`. We can then check if the option to include hard levels is set to true and extend `levels` with the list `hard_levels`.

Now any time we call the method `levels()`, it will be looking through the full list of levels, whether we included the hard levels or not.

## Game Objective Templates

Game objective templates are set up with the following properties:

- `label` - How you want the objective to read out within the KMK client.
- `data` - What datasets to pull from, where to plug the data in, and how much data to pull.
- `is_time_consuming` - Whether or not the objective is time-consuming (⌛).
- `is_difficult` - Whether or not the objective is difficult (⚠️).
- `weight` - How much weight each individual objective in the pool of this game's objectives has. This has no bearing on how many of this game's objectives show up in KMK, only how likely the objective is to show up when this game is selected to pull from.

To begin, we can create a `GameObjectiveTemplate` within the method we created earlier. We can then start to fill out the above information. I will provide an example of a full game objective template and then explain each part based off of the example:

```python
def game_objective_templates(self) -> List[GameObjectiveTemplate]:
    return [
        GameObjectiveTemplate(
            label="Beat the following levels: LEVELS",
            data={
                "LEVELS": (self.levels, 2),
            },
            is_time_consuming=False,
            is_difficult=False,
            weight=3,
        ),
    ]
```

- The `label` contains the actual objective "Beat the following levels:" and an identifying word "LEVELS". This word can be whatever you want it to be, but I typically like to make it the same as whatever dataset is being pulled from, in all caps.
- Within `data`, we set the identifying word from the label to be replaced with a certain quantity of data from a certain dataset. Basically, the setup goes `"Identifier": (self.dataset, quantity)`. The datasets that we pull from here **MUST** be functions that can be called to pull data from, such as those static methods and functions that combine multiple lists.
- `is_time_consuming` and `is_difficult` just get set to `True` or `False`, rather intuitively.
- `weight`, in this instance, is set to `3`. The higher the weight, the more likely you are to see that type of objective when this game's objectives are used in KMK.

Objective templates can also contain multiple types of data pulled from different datasets and placed at different locations in the label.

Here's an example of an objective with two different pieces of data pulled from two different datasets:

```python
GameObjectiveTemplate(
    label="Beat LEVEL with CHARACTER",
    data={
        "LEVEL": (self.levels, 1),
        "CHARACTER": (self.characters, 1),
    },
    is_time_consuming=False,
    is_difficult=False,
    weight=3,
),
```

## Optional Game Constraints

Optional game constraints are set up very similarly to game objective templates. Within the `optional_game_constraint_templates()` method, you can create a `GameObjectiveTemplate`, however these only require a label and data. Example from the template:

```python
def optional_game_constraint_templates(self) -> List[GameObjectiveTemplate]:
    return [
        GameObjectiveTemplate(
            label="Cannot take UPGRADE",
            data={
                "UPGRADE": (self.upgrades, 1),
            },
        ),
    ]
```

Above we can see the optional game constraint "Cannot take UPGRADE." If a keep area generated for this game, the area could have this constraint to keep players from using a random upgrade when attempting to complete their objectives.

??? "No optional constraints?"
    If you don't want to add any game constraint templates, you can just return `list()`.

---

*Guide written by [deyoungbryce](https://github.com/deyoungbryce) (with minor edits by [Jack5](https://github.com/jack5github))*
