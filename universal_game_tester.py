#!/usr/bin/env python3
"""
Universal Game Tester for Keymaster's Keep Implementations

A comprehensive testing framework that can validate ANY Keymaster's Keep game implementation
regardless of structure, option types, or complexity. This tool automatically discovers,
loads, and tests game modules with full compatibility for:

- Standard option types (Toggle, Choice, Range, OptionSet, etc.)
- Custom OptionSet-based types with class-level defaults
- Complex dataclass structures and relative imports
- Dynamic objective generation with authentic weighted selection
- Comprehensive analysis and metrics reporting
- KeymastersKeepGamePlatforms enum with 130+ gaming platforms

Key Features:
[+] Universal compatibility - works with any game implementation
[+] Authentic simulation - reproduces Keep's weighted objective selection
[+] Robust error handling - gracefully handles missing dependencies
[+] Interactive testing - menu-driven interface for easy use
[+] Comprehensive analysis - detailed metrics and feature detection
[+] Optimized enum support - includes only the enums actually used by implementations

Usage:
    python universal_game_tester.py                    # Interactive menu
    python universal_game_tester.py <game_file.py>     # Test specific game
    python universal_game_tester.py creative_challenges # Test with partial name

Technical Architecture:
- Mock Environment: Creates universal compatibility layer with essential enum support
- Dynamic Loading: Resolves imports and string type annotations
- Smart Options: Intelligently instantiates any option type
- Weighted Selection: Simulates authentic Keep objective selection
- Analysis Engine: Provides detailed implementation metrics

This tool is essential for validating game implementations before deployment
and ensures compatibility with the Keymaster's Keep ecosystem.
"""

import os
import sys
import importlib.util
import inspect
import types
import re
import random
from typing import List, Dict, Optional
from dataclasses import dataclass


def create_option_class(class_name):
    """Dynamic class creation for any possible option type."""

    class UniversalOption:
        def __init__(self, value=None):
            if value is None:
                # Smart default based on class name
                class_name_lower = class_name.lower()
                if "selection" in class_name_lower:
                    self.value = {"default_selection"}
                elif "actions" in class_name_lower:
                    self.value = {"default_action"}
                elif "range" in class_name_lower:
                    self.value = 50
                elif "toggle" in class_name_lower:
                    self.value = True
                else:
                    self.value = {"default"}
            else:
                self.value = value

    return type(class_name, (UniversalOption,), {})


def create_comprehensive_mocks():
    """Create comprehensive mock environment for any game implementation."""

    # Mock all possible Options classes
    class Toggle:
        def __init__(self, value=True):
            self.value = value

    class Choice:
        def __init__(self, value="default"):
            self.value = value

    class Range:
        def __init__(self, start=1, stop=10, step=1):
            self.start = start
            self.stop = stop
            self.step = step
            # Add value attribute that archipelago Range options use
            self.value = (start + stop) // 2  # Use middle value as default

    class OptionSet:
        def __init__(self, value=set()):
            self.value = value if isinstance(value, set) else set(value) if hasattr(value, "__iter__") else {value}

    class DefaultOnToggle:
        def __init__(self, value=True):
            self.value = value

    class PercentageRange:
        def __init__(self, value=50):
            self.value = value

    class NamedRange:
        def __init__(self, value=1):
            self.value = value

    class OptionList:
        def __init__(self, value=None):
            self.value = value if value is not None else []

    class OptionDict:
        """Mock OptionDict for games requiring it."""

        def __init__(self, value=None):
            self.value = value if value is not None else {}

        def __getitem__(self, key):
            return self.value.get(key)

        def __setitem__(self, key, value):
            self.value[key] = value

        def __contains__(self, key):
            return key in self.value

        def keys(self):
            return self.value.keys()

        def items(self):
            return self.value.items()

    # Mock core game classes
    @dataclass
    class GameObjectiveTemplate:
        label: str
        data: dict
        is_time_consuming: bool = False
        is_difficult: bool = False
        weight: int = 1

    class Game:
        def __init__(self, archipelago_options=None):
            self.archipelago_options = archipelago_options

    # Mock all possible enums - only include the ones actually used by implementations
    class KeymastersKeepGamePlatforms:
        _32X = "32X"  # Sega 32X
        _3DO = "3D0"  # 3DO Multiplayer
        _3DS = "3DS"  # Nintendo 3DS
        A2 = "A2"  # Apple II
        A26 = "A26"  # Atari 2600
        A2GS = "A2GS"  # Apple IIGS
        A52 = "A52"  # Atari 5200
        A78 = "A78"  # Atari 7800
        A8 = "A8"  # Atari 8-bit: 400, 800, XL, XE
        ADV = "ADV"  # Entex AdventureVision
        AMI = "AMI"  # Commodore Amiga
        AND = "AND"  # Android OS
        ARC = "ARC"  # Arcade
        ARCH = "ARCH"  # Acorn Archimedes
        AST = "AST"  # Atari ST
        BA = "BA"  # Bally Astrocade
        BB = "BB"  # BlackBerry
        BBCM = "BBCM"  # BBC Micro
        BOARD = "BOARD"  # Board Game (Physical)
        BREW = "BREW"  # Qualcomm BREW
        C64 = "C64"  # Commodore 64
        C128 = "C128"  # Commodore 128
        CARD = "CARD"  # Card Game (Physical)
        CD32 = "CD32"  # Amiga CD32
        CDI = "CDI"  # Philips CD-i
        CDTV = "CDTV"  # Commodore CDTV
        CHF = "CHF"  # Fairchild Channel F
        CP4 = "CP4"  # Commodore 116, 16, Plus/4
        CPC = "CPC"  # Amstrad CPC 464, CPC664, CPC6128
        CV = "CV"  # ColecoVision
        DC = "DC"  # Sega Dreamcast
        DOS = "DOS"  # MS-DOS
        ELEC = "ELEC"  # Acorn Electron
        EXEN = "EXEN"  # In-Fusion ExEn
        FAL = "FAL"  # Atari Falcon030
        FC = "FC"  # Nintendo Famicom
        FDS = "FDS"  # Nintendo Famicom Disk System
        FIRE = "FIRE"  # Amazon Fire OS
        FM7 = "FM7"  # Fujitsu FM-7
        FMT = "FMT"  # Fujitsu FM Towns
        GB = "GB"  # Nintendo Game Boy
        GBA = "GBA"  # Nintendo Game Boy Advance
        GBC = "GBC"  # Nintendo Game Boy Color
        GC = "GC"  # Nintendo GameCube
        GCOM = "GCOM"  # Tiger Game.com
        GEN = "GEN"  # Sega Genesis
        GG = "GG"  # Sega Game Gear
        GIZ = "GIZ"  # Tiger Gizmondo
        GW = "GW"  # Nintendo Game & Watch
        GX4 = "GX4"  # Amstrad GX4000
        IMOD = "IMOD"  # NTT DoCoMo i-mode
        INTV = "INTV"  # Intellivision, Intellivision II
        IOS = "IOS"  # Apple iOS: iPad, iPod, iPhone
        J2ME = "J2ME"  # Sun Java 2 Micro Edition
        JAG = "JAG"  # Atari Jaguar
        JCD = "JCD"  # Atari Jaguar CD
        LASR = "LASR"  # Pioneer LaserActive
        LYNX = "LYNX"  # Atari Lynx
        MART = "MART"  # Fujitsu FM Towns Marty
        MCD = "MCD"  # Sega Mega CD
        META = "META"  # Metagame
        MOD = "MOD"  # Modded Game
        MSX = "MSX"  # MSX
        MSX2 = "MSX2"  # MSX2, MSX2+, MSX TurboR
        N64 = "N64"  # Nintendo 64
        NDS = "NDS"  # Nintendo DS
        NES = "NES"  # Nintendo Entertainment System
        NG = "NG"  # SNK Neo Geo
        NGAGE = "NGAGE"  # Nokia N-GAGE
        NGCD = "NGCD"  # SNK Neo Geo CD
        NGP = "NGP"  # SNK Neo Geo Pocket
        NGPC = "NGPC"  # SNK Neo Geo Pocket Color
        ODY2 = "ODY2"  # Magnavox Odyssey 2
        OUYA = "OUYA"  # Ouya
        PALM = "PALM"  # Palm OS
        PBL = "PBL"  # Pinball
        PC = "PC"  # PC
        PC10 = "PC10"  # Nintendo PlayChoice-10
        PC88 = "PC88"  # NEC PC-8801
        PC98 = "PC98"  # NEC PC-9801
        PCB = "PCB"  # PC Boot Loader
        PCCD = "PCCD"  # NEC PC Engine CD-ROM
        PCE = "PCE"  # NEC PC Engine
        PCED = "PCED"  # NEC PC Engine Duo
        PICO = "PICO"  # Sega Pico / Kids Computer Pico
        PICO8 = "PICO8"  # PICO-8 Fantasy Console
        PPC = "PPC"  # Microsoft Pocket PC
        PS1 = "PS1"  # Sony PlayStation 1
        PS2 = "PS2"  # Sony PlayStation 2
        PS3 = "PS3"  # Sony PlayStation 3
        PS4 = "PS4"  # Sony PlayStation 4
        PS5 = "PS5"  # Sony PlayStation 5
        PSP = "PSP"  # Sony PlayStation Portable
        QL = "QL"  # Sinclair Quantum Leap
        SAM = "SAM"  # Sam Coupe
        SAT = "SAT"  # Sega Saturn
        SCD = "SCD"  # Sega CD
        SFC = "SFC"  # Nintendo Super Famicom
        SLOT = "SLOT"  # Slot Machine
        SM3 = "SM3"  # Sega Mark III
        SMD = "SMD"  # Sega Mega Drive
        SMS = "SMS"  # Sega Master System
        SNES = "SNES"  # Super Nintendo Entertainment System
        SW = "SW"  # Nintendo Switch
        SYM = "SYM"  # Symbian
        TD = "TD"  # NEC TurboDuo
        TG16 = "TG16"  # NEC TurboGrafx-16
        TGCD = "TGCD"  # NEC TurboGrafx CD-ROM
        TMO = "TMO"  # Thomson MO
        TRS = "TRS"  # Radio Shack TRS-80
        TRSC = "TRSC"  # Radio Shack TRS-80 Color Computer
        TTO = "TTO"  # Thomson TO
        VB = "VB"  # Nintendo Virtual Boy
        VECT = "VECT"  # General Consumer Electric Vectrex
        VIC = "VIC"  # Commodore VIC 20
        VITA = "VITA"  # Sony PlayStation Vita
        VR = "VR"  # Virtual Reality
        VS = "VS"  # Nintendo VS. System
        VVS = "VVS"  # V-Tech V-Smile
        VSP = "VSP"  # V-Tech V-Smile Pocket
        W16 = "W16"  # 16-bit Microsoft Windows: 1, 2, 3, 3.1, 3.11
        WCE = "WCE"  # Microsoft Windows CE
        WEB = "WEB"  # Web Browser
        WII = "WII"  # Nintendo Wii
        WIIU = "WIIU"  # Nintendo Wii U
        WMOB = "WMOB"  # Windows Mobile: 2003, 2003 SE, 5, 6, 6.1, 6.5
        WPH = "WPH"  # Windows Phone
        WS = "WS"  # Bandai WonderSwan
        WSC = "WSC"  # Bandai WonderSwan Color
        X1 = "X1"  # Sharp X1
        X360 = "X360"  # Microsoft Xbox 360
        X68 = "X68"  # Sharp X68000
        XBOX = "XBOX"  # Microsoft Xbox
        XEGS = "XEGS"  # Atari XEGS
        XONE = "XONE"  # Microsoft Xbox One
        XSX = "XSX"  # Microsoft Xbox Series X
        ZEBO = "ZEBO"  # Zeebo Zeebo
        ZOD = "ZOD"  # Tapwave Zodiac
        ZXS = "ZXS"  # Sinclair ZX Spectrum

    # Create the modules with proper hierarchy for relative imports

    # Create the main package modules that relative imports will reference
    package_modules = {
        "keymasters_keep_root.game": {"Game": Game},
        "keymasters_keep_root.game_objective_template": {"GameObjectiveTemplate": GameObjectiveTemplate},
        "keymasters_keep_root.enums": {"KeymastersKeepGamePlatforms": KeymastersKeepGamePlatforms},
        "Options": {
            "Toggle": Toggle,
            "Choice": Choice,
            "Range": Range,
            "OptionSet": OptionSet,
            "DefaultOnToggle": DefaultOnToggle,
            "PercentageRange": PercentageRange,
            "NamedRange": NamedRange,
            "OptionList": OptionList,
            "OptionDict": OptionDict,
        },
    }

    # Create and register all mock modules
    for module_name, exports in package_modules.items():
        if module_name not in sys.modules:
            mock_module = types.ModuleType(module_name)
            for name, obj in exports.items():
                setattr(mock_module, name, obj)
            sys.modules[module_name] = mock_module

    # Also create the package roots
    if "keymasters_keep_root" not in sys.modules:
        root_module = types.ModuleType("keymasters_keep_root")
        root_module.__path__ = []  # Mark it as a package
        sys.modules["keymasters_keep_root"] = root_module

    if "keymasters_keep_root.keymasters_keep" not in sys.modules:
        parent_module = types.ModuleType("keymasters_keep_root.keymasters_keep")
        parent_module.__path__ = []  # Mark it as a package
        sys.modules["keymasters_keep_root.keymasters_keep"] = parent_module

    return (Toggle, Choice, Range, GameObjectiveTemplate, Game, KeymastersKeepGamePlatforms, OptionSet, DefaultOnToggle, PercentageRange, NamedRange, OptionList, OptionDict)


def discover_all_game_implementations():
    """Discover ALL game implementation files regardless of naming convention."""
    implementations = []

    # Look for any Python file that might contain a game implementation
    for file in os.listdir("."):
        if (
            file.endswith(".py")
            and file != "universal_game_demo.py"
            and file != "universal_game_tester.py"
            and not file.startswith("__")
            and file != "game_demo.py"
            and file != "universal_game_tester_fixed.py"
        ):
            # Quick scan of the file content to see if it looks like a game implementation
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Look for game implementation patterns
                patterns = [r"class \w*Game\(", r'name\s*=\s*["\'].*["\']', r"game_objective_templates", r"KeymastersKeepGamePlatforms", r"archipelago_options"]

                matches = sum(1 for pattern in patterns if re.search(pattern, content))

                if matches >= 2:  # If it matches at least 2 patterns, it's likely a game
                    implementations.append({"file": file, "confidence": matches, "name": file[:-3].replace("_", " ").title()})

            except Exception:
                continue

    # Sort by confidence (most likely games first)
    implementations.sort(key=lambda x: x["confidence"], reverse=True)
    return implementations


def load_game_from_file(file_path: str) -> Optional[Dict]:
    """Load a game implementation from any Python file with robust import handling."""
    try:
        module_name = os.path.basename(file_path)[:-3]  # Remove .py

        # Set up proper package hierarchy for relative imports (need 2 levels for .. imports)
        root_package = "keymasters_keep_root"
        package_name = "keymasters_keep"

        # Ensure the root package exists in sys.modules
        if root_package not in sys.modules:
            root_module = types.ModuleType(root_package)
            root_module.__path__ = [os.path.dirname(os.path.dirname(file_path))]
            sys.modules[root_package] = root_module

        # Ensure the parent package exists in sys.modules
        full_package_name = f"{root_package}.{package_name}"
        if full_package_name not in sys.modules:
            parent_module = types.ModuleType(full_package_name)
            parent_module.__path__ = [os.path.dirname(file_path)]
            sys.modules[full_package_name] = parent_module

        # Create the full module name with package hierarchy
        full_module_name = f"{full_package_name}.{module_name}"

        # Load the module using importlib with proper package context
        spec = importlib.util.spec_from_file_location(full_module_name, file_path)
        if spec is None:
            return None

        module = importlib.util.module_from_spec(spec)

        # Set up the module's package context for relative imports
        module.__package__ = full_package_name

        # Add the module to sys.modules before executing to support relative imports
        sys.modules[full_module_name] = module

        # Execute the module
        spec.loader.exec_module(module)

        # Collect all classes defined in this module
        loaded_classes = {}
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                loaded_classes[name] = obj

        # Add universal option classes to the module for any undefined types
        for name in dir(module):
            obj = getattr(module, name)
            if inspect.isclass(obj) and hasattr(obj, "__annotations__"):
                # This might be an options class, add all possible option types
                for field_name, field_type in getattr(obj, "__annotations__", {}).items():
                    if hasattr(field_type, "__name__") and field_type.__name__ not in dir(module):
                        # Create a universal option class for this type
                        universal_class = create_option_class(field_type.__name__)
                        setattr(module, field_type.__name__, universal_class)
                        loaded_classes[field_type.__name__] = universal_class
                        # Also add it to the mock modules so it can be imported
                        for mock_module_name in ["Options", "game", "game_objective_template", "enums"]:
                            if mock_module_name in sys.modules:
                                setattr(sys.modules[mock_module_name], field_type.__name__, universal_class)

        # Find game classes
        game_classes = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and (name.endswith("Game") or hasattr(obj, "game_objective_templates")) and hasattr(obj, "name"):
                game_classes.append(
                    {
                        "module_name": module_name,
                        "class_name": name,
                        "game_name": getattr(obj, "name", name),
                        "class_obj": obj,
                        "file_path": file_path,
                        "loaded_classes": loaded_classes,  # Include all loaded classes
                    }
                )

        return game_classes[0] if game_classes else None

    except Exception as e:
        print(f"Warning: Could not load {file_path}: {e}")
        return None


def create_smart_options(game_class, Toggle, Choice, Range, OptionSet=None, DefaultOnToggle=None, PercentageRange=None, NamedRange=None, OptionList=None, OptionDict=None, loaded_classes=None):
    """Intelligently create default options for any game class."""
    try:
        if not hasattr(game_class, "options_cls"):
            return None

        options_cls = game_class.options_cls

        if not hasattr(options_cls, "__dataclass_fields__"):
            return None

        if loaded_classes is None:
            loaded_classes = {}

        options_dict = {}

        for field_name, field in options_cls.__dataclass_fields__.items():
            field_type = field.type

            # If field_type is a string, try to resolve it from loaded_classes
            if isinstance(field_type, str) and field_type in loaded_classes:
                field_type = loaded_classes[field_type]
                # Silently resolve string types to actual classes

            # Handle different option types intelligently
            if hasattr(field_type, "__name__"):
                type_name = field_type.__name__

                if "Toggle" in type_name:
                    options_dict[field_name] = Toggle(True)
                elif "Choice" in type_name:
                    # Find default or first option
                    if hasattr(field_type, "default"):
                        options_dict[field_name] = Choice(field_type.default)
                    else:
                        # Look for option_ attributes
                        for attr_name in dir(field_type):
                            if attr_name.startswith("option_"):
                                default_value = getattr(field_type, attr_name)
                                options_dict[field_name] = Choice(default_value)
                                break
                        else:
                            options_dict[field_name] = Choice("default")
                elif "Range" in type_name:
                    # For Range types, use the class's specific range parameters if available
                    try:
                        start = getattr(field_type, "range_start", 1)
                        end = getattr(field_type, "range_end", 10)
                        getattr(field_type, "default", start)
                        options_dict[field_name] = Range(start, end, 1)
                        # Set the value to the class's default if available
                        if hasattr(field_type, "default"):
                            options_dict[field_name].value = field_type.default
                    except Exception as e:
                        print(f"Warning: Could not create {type_name} with specific range: {e}")
                        options_dict[field_name] = Range(1, 10, 1)
                elif "OptionSet" in type_name and OptionSet:
                    options_dict[field_name] = OptionSet(set())
                elif "DefaultOnToggle" in type_name and DefaultOnToggle:
                    options_dict[field_name] = DefaultOnToggle(True)
                elif "PercentageRange" in type_name and PercentageRange:
                    options_dict[field_name] = PercentageRange(50)
                elif "NamedRange" in type_name and NamedRange:
                    options_dict[field_name] = NamedRange(1)
                elif "OptionList" in type_name and OptionList:
                    options_dict[field_name] = OptionList([])
                elif hasattr(field_type, "default"):
                    # This is likely a custom option class with a default
                    try:
                        default_value = field_type.default

                        # Check if this is a Range subclass
                        if hasattr(field_type, "range_start") and hasattr(field_type, "range_end"):
                            # This is a custom Range subclass
                            start = getattr(field_type, "range_start", 1)
                            end = getattr(field_type, "range_end", 10)
                            options_dict[field_name] = Range(start, end, 1)
                            options_dict[field_name].value = default_value
                        elif isinstance(default_value, (list, tuple)):
                            options_dict[field_name] = field_type(set(default_value))
                        elif isinstance(default_value, set):
                            options_dict[field_name] = field_type(default_value)
                        elif isinstance(default_value, (int, float)):
                            # For numeric defaults, create appropriate option type
                            if PercentageRange and hasattr(field_type, "__name__") and "percentage" in field_type.__name__.lower():
                                options_dict[field_name] = PercentageRange(default_value)
                            elif NamedRange and hasattr(field_type, "__name__") and "namedrange" in field_type.__name__.lower():
                                options_dict[field_name] = NamedRange(default_value)
                            else:
                                # Default to Range for numeric values
                                options_dict[field_name] = Range(1, 100, 1)
                                options_dict[field_name].value = default_value
                        else:
                            options_dict[field_name] = field_type({default_value})
                        # Silently create custom option types with defaults
                    except Exception as e:
                        print(f"Warning: Could not create {type_name} with default value: {e}")
                        # Better fallback based on what we know about the field type
                        if hasattr(field_type, "range_start") and hasattr(field_type, "range_end"):
                            start = getattr(field_type, "range_start", 1)
                            end = getattr(field_type, "range_end", 10)
                            options_dict[field_name] = Range(start, end, 1)
                        else:
                            options_dict[field_name] = OptionSet({"default"}) if OptionSet else Toggle(True)
                else:
                    # Generic fallback - try to create with appropriate default
                    try:
                        # If it looks like a selection type, try with a set
                        if "selection" in type_name.lower():
                            # Use the dynamically created class with proper default
                            options_dict[field_name] = field_type({"default_option"})
                        elif "actions" in type_name.lower():
                            # Use the dynamically created class with proper default
                            options_dict[field_name] = field_type({"default_action"})
                        elif "range" in type_name.lower():
                            options_dict[field_name] = field_type(50)
                        elif "toggle" in type_name.lower():
                            options_dict[field_name] = field_type(True)
                        else:
                            # Try to instantiate with a sensible default
                            options_dict[field_name] = field_type({"default"})
                    except Exception as creation_error:
                        # If the custom class creation fails, fall back to Toggle
                        print(f"Warning: Could not create {type_name} with default value, using Toggle: {creation_error}")
                        options_dict[field_name] = Toggle(True)
            else:
                options_dict[field_name] = Toggle(True)

        return options_cls(**options_dict)

    except Exception as e:
        print(f"Warning: Could not create options: {e}")
        return None


def analyze_implementation(game_instance) -> Dict:
    """Comprehensive analysis of any game implementation."""
    analysis = {"total_objectives": 0, "weight_distribution": {}, "features": [], "categories": [], "special_methods": [], "data_sources": set(), "complexity_score": 0}

    try:
        # Analyze objectives
        templates = game_instance.game_objective_templates()

        # Handle case where templates might not be a list
        if not isinstance(templates, (list, tuple)):
            print(f"Warning: game_objective_templates() returned {type(templates)}, expected list")
            templates = []

        analysis["total_objectives"] = len(templates)

        # Weight distribution and data analysis
        for template in templates:
            try:
                weight = getattr(template, "weight", 1)
                analysis["weight_distribution"][weight] = analysis["weight_distribution"].get(weight, 0) + 1

                # Analyze data sources safely
                if hasattr(template, "data") and isinstance(template.data, dict):
                    for placeholder, data_info in template.data.items():
                        try:
                            if isinstance(data_info, (list, tuple)) and len(data_info) >= 1:
                                data_source = data_info[0]
                                if callable(data_source):
                                    analysis["data_sources"].add(data_source.__name__)
                                else:
                                    analysis["data_sources"].add(str(type(data_source).__name__))
                        except Exception:
                            continue
            except Exception:
                continue

        # Look for special features and methods
        for attr_name in dir(game_instance):
            if not attr_name.startswith("_"):
                try:
                    attr = getattr(game_instance, attr_name)

                    if "relationship" in attr_name.lower():
                        analysis["features"].append("Relationship System")
                    elif "preferred" in attr_name.lower():
                        analysis["features"].append("Dynamic Preferences")
                    elif "difficulty" in attr_name.lower():
                        analysis["features"].append("Difficulty Scaling")
                    elif "cursed" in attr_name.lower():
                        analysis["features"].append("Cursed/Challenge Mode")
                    elif callable(attr) and attr_name.endswith("_templates"):
                        analysis["special_methods"].append(attr_name)
                except Exception:
                    continue

        # Analyze option categories
        if hasattr(game_instance, "archipelago_options"):
            try:
                options = game_instance.archipelago_options
                if options:
                    for attr_name in dir(options):
                        if not attr_name.startswith("_"):
                            try:
                                attr_value = getattr(options, attr_name, None)
                                if hasattr(attr_value, "value"):
                                    category = attr_name.replace("_", " ").title()
                                    if len(category) > 10:  # Don't include very long names
                                        category = category[:10] + "..."
                                    analysis["categories"].append(category)
                            except Exception:
                                continue
            except Exception:
                pass

        # Calculate complexity score
        analysis["complexity_score"] = len(templates) + len(analysis["data_sources"]) * 2 + len(analysis["features"]) * 3 + len(analysis["categories"])

        # Remove duplicates from features
        analysis["features"] = list(set(analysis["features"]))

    except Exception as e:
        print(f"Error analyzing implementation: {e}")
        import traceback

        traceback.print_exc()

    return analysis


def generate_dynamic_objectives(game_instance, count=6) -> List[Dict]:
    """Generate objectives using dynamic weighted selection like the actual Keep."""
    try:
        templates = game_instance.game_objective_templates()

        # Handle case where templates might not be a list
        if not isinstance(templates, (list, tuple)):
            print(f"Warning: game_objective_templates() returned {type(templates)}, expected list")
            return []

        if not templates:
            return []

        # Create weighted selection pool (simulating Keep's selection process)
        weighted_pool = []
        for template in templates:
            try:
                weight = getattr(template, "weight", 1)
                # Add each template to the pool multiple times based on its weight
                # This simulates the Keep's weighted random selection
                for _ in range(weight):
                    weighted_pool.append(template)
            except Exception:
                continue

        if not weighted_pool:
            return []

        selected_objectives = []
        used_templates = set()  # Prevent immediate duplicates

        attempts = 0
        max_attempts = count * 10  # Prevent infinite loops

        while len(selected_objectives) < count and attempts < max_attempts:
            attempts += 1

            # Randomly select from weighted pool (like Keep's selection)
            selected_template = random.choice(weighted_pool)

            # Skip if we just used this template (add some variety)
            template_id = id(selected_template)
            if template_id in used_templates and len(used_templates) < len(templates):
                continue

            # Populate the template with actual data
            populated_label = getattr(selected_template, "label", "Unknown Objective")
            populated_successfully = True

            # Dynamic template population (like actual objective generation)
            template_data = getattr(selected_template, "data", {})
            if isinstance(template_data, dict):
                for placeholder, data_info in template_data.items():
                    try:
                        # Handle different data formats
                        if isinstance(data_info, (list, tuple)) and len(data_info) >= 1:
                            data_source = data_info[0]
                        else:
                            data_source = data_info

                        if callable(data_source):
                            values = data_source()
                            if hasattr(values, "__iter__") and not isinstance(values, str):
                                # Randomly select from available values (like Keep does)
                                if hasattr(values, "__getitem__") and len(values) > 0:
                                    value = random.choice(list(values))
                                elif hasattr(values, "__next__"):
                                    value_list = list(values)
                                    value = random.choice(value_list) if value_list else "VALUE"
                                else:
                                    value = str(values)
                            else:
                                value = str(values)
                        else:
                            value = str(data_source)

                        populated_label = populated_label.replace(placeholder, str(value))
                    except Exception:
                        # If we can't populate, mark as failed and try another
                        populated_successfully = False
                        break

            if populated_successfully:
                selected_objectives.append(
                    {
                        "label": populated_label,
                        "weight": getattr(selected_template, "weight", 1),
                        "time_consuming": getattr(selected_template, "is_time_consuming", False),
                        "difficult": getattr(selected_template, "is_difficult", False),
                        "original_label": getattr(selected_template, "label", ""),
                        "data_complexity": len(template_data),
                        "selection_weight": getattr(selected_template, "weight", 1),  # Show actual selection weight
                    }
                )

                used_templates.add(template_id)

                # Clear used templates occasionally to allow repeats (like Keep does)
                if len(used_templates) >= min(len(templates), count // 2):
                    used_templates.clear()

        return selected_objectives

    except Exception as e:
        print(f"Error generating dynamic objectives: {e}")
        return []


def test_implementation(impl_info: Dict, Toggle, Choice, Range, OptionSet=None, DefaultOnToggle=None, PercentageRange=None, NamedRange=None, OptionList=None, OptionDict=None):
    """Test any game implementation comprehensively."""
    print(f"\n{'='*60}")
    print(f"TESTING: {impl_info['game_name']}")
    print(f"File: {impl_info['file_path']}")
    print(f"Class: {impl_info['class_name']}")
    print(f"{'='*60}")

    try:
        # Create options
        loaded_classes = impl_info.get("loaded_classes", {})
        options = create_smart_options(impl_info["class_obj"], Toggle, Choice, Range, OptionSet, DefaultOnToggle, PercentageRange, NamedRange, OptionList, OptionDict, loaded_classes)
        if options is None:
            print("WARNING: No options class found, using None")

        # Create game instance
        game_instance = impl_info["class_obj"](archipelago_options=options)

        # Comprehensive analysis
        analysis = analyze_implementation(game_instance)

        print("\nIMPLEMENTATION ANALYSIS:")
        print(f"   - Total Objectives: {analysis['total_objectives']}")
        print(f"   - Complexity Score: {analysis['complexity_score']}")

        if analysis["weight_distribution"]:
            print("   - Weight Distribution:")
            for weight in sorted(analysis["weight_distribution"].keys(), reverse=True):
                count = analysis["weight_distribution"][weight]
                bar = "=" * min(count, 20)  # Visual bar
                print(f"     - Weight {weight}: {count} objectives {bar}")

        if analysis["features"]:
            print(f"   - Features: {', '.join(analysis['features'][:5])}")
            if len(analysis["features"]) > 5:
                print(f"     + {len(analysis['features']) - 5} more...")

        if analysis["categories"]:
            print(f"   - Categories: {len(analysis['categories'])} options available")

        if analysis["data_sources"]:
            print(f"   - Data Sources: {len(analysis['data_sources'])} unique types")

        # Generate and display dynamic objectives (simulating Keep's selection)
        samples = generate_dynamic_objectives(game_instance, 6)

        if samples:
            print("\nDYNAMIC OBJECTIVE SELECTION (simulating Keep's weighted selection):")
            for i, obj in enumerate(samples, 1):
                # Smart indicators
                weight_indicator = "[HIGH]" if obj["weight"] >= 10 else "[MED]" if obj["weight"] >= 8 else "[LOW]" if obj["weight"] >= 5 else "[MIN]"
                difficulty = "[HARD]" if obj["difficult"] else "[EASY]"
                time = "[LONG]" if obj["time_consuming"] else "[QUICK]"
                complexity = f"[DATA x{obj['data_complexity']}]" if obj["data_complexity"] > 0 else ""
                selection_info = f"[WEIGHT {obj['selection_weight']}]" if "selection_weight" in obj else ""

                print(f"   {i}. {weight_indicator} {obj['label']}")
                print(f"      -> Weight: {obj['weight']} | {difficulty} | {time} {complexity} {selection_info}")

            # Show multiple rounds to demonstrate dynamic selection
            print("\nDEMONSTRATING DYNAMIC SELECTION (3 more rounds):")
            for round_num in range(1, 4):
                round_samples = generate_dynamic_objectives(game_instance, 3)
                if round_samples:
                    print(f"   Round {round_num}: ", end="")
                    round_labels = [f"W{obj['weight']}:{obj['label'][:30]}..." if len(obj["label"]) > 30 else f"W{obj['weight']}:{obj['label']}" for obj in round_samples]
                    print(" | ".join(round_labels))

        else:
            print("\nWARNING: No objectives could be generated dynamically")

        # Test constraints if available
        if hasattr(game_instance, "optional_game_constraint_templates"):
            try:
                constraints = game_instance.optional_game_constraint_templates()
                if constraints:
                    print(f"\nCONSTRAINT SYSTEM: {len(constraints)} templates")
                    for constraint in constraints[:3]:
                        print(f"   - {constraint.label}")
                    if len(constraints) > 3:
                        print(f"   ... and {len(constraints) - 3} more")
            except Exception as e:
                print(f"\nWARNING: Constraint system error: {e}")

        # Calculate and display metrics
        if analysis["total_objectives"] > 0:
            avg_weight = sum(w * c for w, c in analysis["weight_distribution"].items()) / analysis["total_objectives"]
            print("\nMETRICS:")
            print(f"   - Average Weight: {avg_weight:.1f}")
            print(f"   - Feature Richness: {len(analysis['features'])}/10")
            print(f"   - Customization: {len(analysis['categories'])} options")

        print("\n[SUCCESS] Testing completed successfully!")

    except Exception as e:
        print(f"\n[ERROR] Error testing implementation: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Universal game implementation testing system."""
    print("KEYMASTERS KEEP - UNIVERSAL IMPLEMENTATION TESTER")
    print("=" * 60)
    print("Works with ANY game implementation file!")

    # Set up comprehensive mock environment
    print("Setting up universal mock environment...")
    (Toggle, Choice, Range, GameObjectiveTemplate, Game, KeymastersKeepGamePlatforms, OptionSet, DefaultOnToggle, PercentageRange, NamedRange, OptionList, OptionDict) = create_comprehensive_mocks()

    # Check for command line arguments
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        if not target_file.endswith(".py"):
            target_file += ".py"

        if os.path.exists(target_file):
            print(f"Testing specific file: {target_file}")
            game_info = load_game_from_file(target_file)
            if game_info:
                test_implementation(game_info, Toggle, Choice, Range, OptionSet, DefaultOnToggle, PercentageRange, NamedRange, OptionList, OptionDict)
                return
            else:
                print(f"[ERROR] Could not load {target_file} as a game implementation")
                return
        else:
            print(f"[ERROR] File not found: {target_file}")
            print(f"Usage: python {sys.argv[0]} <game_file.py>")
            return

    # Discover all possible implementations
    print("Scanning for game implementations...")
    implementations = discover_all_game_implementations()

    if not implementations:
        print("[ERROR] No game implementation files found!")
        print("   This tool looks for .py files with game-like patterns")
        return

    print(f"Found {len(implementations)} potential implementation(s):")
    for i, impl in enumerate(implementations, 1):
        confidence_stars = "*" * min(impl["confidence"], 5)
        print(f"   {i}. {impl['name']} ({impl['file']}) {confidence_stars}")

    while True:
        print(f"\n{'='*40}")
        print("UNIVERSAL TESTING MENU:")
        print("   0. Exit")
        for i, impl in enumerate(implementations, 1):
            print(f"   {i}. Test {impl['name']}")
        print(f"   {len(implementations) + 1}. Test All Implementations")
        print(f"   {len(implementations) + 2}. Rescan for New Files")

        try:
            choice = input(f"\nSelect option (0-{len(implementations) + 2}): ").strip()

            if choice == "0":
                print("Goodbye!")
                break
            elif choice == str(len(implementations) + 1):
                print("\nTesting all implementations...")
                for impl in implementations:
                    game_info = load_game_from_file(impl["file"])
                    if game_info:
                        test_implementation(game_info, Toggle, Choice, Range, OptionSet, DefaultOnToggle, PercentageRange, NamedRange, OptionList, OptionDict)
                    else:
                        print(f"[ERROR] Could not load {impl['file']}")
            elif choice == str(len(implementations) + 2):
                print("Rescanning...")
                implementations = discover_all_game_implementations()
                print(f"Found {len(implementations)} implementation(s)")
            elif choice.isdigit() and 1 <= int(choice) <= len(implementations):
                impl_index = int(choice) - 1
                impl = implementations[impl_index]
                game_info = load_game_from_file(impl["file"])
                if game_info:
                    test_implementation(game_info, Toggle, Choice, Range, OptionSet, DefaultOnToggle, PercentageRange, NamedRange, OptionList, OptionDict)
                else:
                    print(f"[ERROR] Could not load {impl['file']}")
            else:
                print("[ERROR] Invalid choice. Please try again.")

        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"[ERROR] Error: {e}")


if __name__ == "__main__":
    main()
