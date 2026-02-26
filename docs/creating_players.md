# Creating KMK Player Files

This document explores how to create and maintain a Keymaster's Keep (KMK) player file.

## Before You Start

- If you have no concept of player files, refer to the setup guides in the Archipelago section from [this linked webpage](https://archipelago.gg/tutorial/).
- If you've never manually customised a player file before, read the [Advanced YAML Guide](https://archipelago.gg/tutorial/Archipelago/advanced_settings_en) first.
- It is recommended to start with the template player file created by following the instructions in **[Installation](../installation/)**.
- When doing co-op runs or team races of Archipelago with KMK, it is advised to have one KMK player file per team of players, rather than a file for each player, as KMK often takes longer than other AP games. The means of maintaining such a player file are the same as solo play, though you may want to use a GitHub repository to collaborate on and share your player files.

## Games (Implementations)

As your KMK player file will revolve around the many game implementations you install and their objectives, the options that control them are central to how you adjust other options. They are listed below:

- `game_selection` - Add the names and platforms of the game implementations you would like to have a chance of playing in an AP run here. Names and platforms can be found at the top of the pages for each implementation in **this codex**. For example:
    ```yaml
    game_selection:
      - Custom (META)
      - Game Backlog (META)
      - Portal (PC + PS3, SW, X360)
    ```
- `game_selection_force_select` - If there are games that you always want to appear in KMK, add them to this list. This is great for meta-games, for example, **[Consumables (META)](../games/consumables/)**.
- `game_selection_bag_size` - Most of the time you'll leave this at `1`. If you like the possibility of a game appearing twice or more, set this to a higher number, or `0` to allow games to appear any number of times.
- `hints_reveal_objectives` - If you want game objectives to appear in KMK hints, set this to `true`. **Warning: This will spoil locked areas!**

### Objective Overrides

The above options are overridden by the following:

- `include_adult_only_or_unrated_games` - If this is `false`, no adult-only or unrated games will appear.
- `include_modern_console_games` - If this is `false`, no modern console games will appear.
- Difficult objectives (⚠️) are those that some players will struggle or not be able to complete. Their appearance is controlled by the following options:
    - `include_difficult_objectives` - If this is `false`, no difficult objectives will appear.
    - `excluded_games_difficult_objectives` - If you have set the above to `true`, game names and platforms here will not produce difficult objectives.
- Time consuming objectives (⌛) are those that take much longer to complete (i.e. more than 1 hour). Their appearance is controlled by the following options:
    - `include_time_consuming_objectives` - If this is `false`, no time-consuming objectives will appear.
    - `excluded_games_time_consuming_objectives` - If you have set the above to `true`, game names and platforms here will not produce time-consuming objectives.

## Keep Areas

Areas (and the trials within them) are the primary source of locations/checks in KMK. Each represents a single game implementation (in most cases). Some areas start unlocked, while others require *Magic Keys* to unlock. The following options are relevant for customising areas:

- `keep_areas` - The total number of areas KMK has. Set this to how many games you would like to play per AP run.
- `unlocked_areas` - The number of areas unlocked at the start of the game.
- Set these to how many objectives you would like to complete per game:
    - `area_trials_minimum` - The minimum number of trials in an area.
    - `area_trials_maximum` - The maximum number of trials in an area.
- There must be as many *Magic Keys* as locked areas or more, otherwise generation will fail:
    - `magic_keys_total` - The total number of *Magic Keys* in KMK.
    - `lock_magic_keys_minimum` - The minimum number of *Magic Keys* a locked area may require.
    - `lock_magic_keys_maximum` - The maximum number of *Magic Keys* a locked area may require.

### Special Areas

The below areas are special in KMK, for rather than becoming areas normally, there is a chance of them replacing areas.

#### Game Medley

**Game Medley** is a meta-implementation that mixes objectives from all available games together. It has the following options:

- `game_medley_mode` - Set this to `true` to enable **Game Medley** to appear.
- `game_medley_percentage_chance` - The chance that an area will be replaced by **Game Medley**. The more implementations you have, the lower this number needs to be for it to be equally weighted.
- `game_medley_game_selection` - See `game_selection`. For **Game Medley**, it is recommended to not include meta-games or those that are difficult to switch between.
- `game_medley_game_selection_bag_size` - See `game_selection_bag_size`.

#### Shops

*Shops* are areas that are located on a separate tab in KMK and require *Relics* in order to purchase their items. They can be thought of as unlocking areas, but for locations/checks instead. They have the following options:

- `shops_` - Set this to `true` to enable *Shops* to appear.
- `shops_percentage_chance` - The chance that an area will be replaced by a *Shop*.
- `shop_items_minimum` - The minimum number of items a *Shop* can sell.
- `shop_items_maximum` - The maximum number of items a *Shop* can sell.
- `shop_hints` - If you want items to create hints for what they will release, set this to `true`.
- `shop_items_progression_percentage_chance` - The chance that an item is a progression item, which is crucial for a player to progress through an AP run.

## Goal

The various KMK goals are the means by which a player can release all items uncollected in KMK, and the goals you pursue will affect how you fill out other options. Regardless of what goal is selected, *Magic Keys* unlock new areas (except for the *Keymaster's Challenge Chamber*).

- **Area Domination** - This goal is the simplest to explain: You are tasked with completing all trials in a certain percentage of areas (which give *Conquest Medallions*).
    - Use the `conquest_medallions_percentage_required` option to decide what percentage of available games you need to fully complete to finish the goal.
- **Magic Key Heist** - This goal is like **Area Domination**, but *Magic Keys* can be found in any trial, not just upon completing all trials in an area.
    - Use the `magic_keys_required` option to decide how many *Magic Keys* you need to acquire to finish the goal.
- **Keymaster's Challenge** - This goal introduces a new item, *Artifacts of Resolve*, which are the keys needed to unlock the *Keymaster's Challenge Chamber* area that must be fully completed.
    - Use the `artifacts_of_resolve_total` and `artifacts_of_resolve_required` options to decide how many *Artifacts of Resolve* you need to acquire to unlock the *Keymaster's Challenge Chamber* in order to finish the goal.

## Miscellaneous Options

Other KMK options are inherited from Archipelago, so refer to the [Advanced YAML Guide](https://archipelago.gg/tutorial/Archipelago/advanced_settings_en) for more information. Below are some tips on how to use them:

- `progression_balancing` - The higher this number is, the quicker you will reach your goal:
    - With all goals, you will acquire *Magic Keys* faster.
    - With the **Keymaster's Challenge** goal, you will unlock the *Keymaster's Challenge Chamber* faster.
- `accessibility` - It is advised to keep this option set to `full`, as KMK is all about random selection. If this is set to `minimal`, there is a chance that some of the randomly selected areas (and shop items) will be inaccessible.
- `non_local_items` - If you want to ensure other player files get just as much as attention as KMK, add item groups to this list. For example, add `Keys` so that areas only unlock via the actions of others.
- `local_items` - If you want to ensure KMK gets more attention, add item groups to this list. For example, add `Relics` so that shop items only unlock via your actions.
- At the start of an AP run:
    - `start_inventory` - Give yourself items from KMK item groups.
    - `start_hints` - Create hints for KMK items.
    - `start_location_hints` - Create hints for what items are contained within KMK locations/checks.
    - `exclude_locations` - Make KMK locations give unimportant items.
    - `priority_locations` - Make KMK locations give important items, such as those needed for progression.
    - `item_links` - Share KMK items between player files.
    - `plando_items` - Place KMK items in specific locations in the AP run multiworld, provided that items plando was enabled for the generator.

---

*Guide written by [Jack5](https://github.com/jack5github)*
