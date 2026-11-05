# -*- coding: utf-8 -*-
"""Profile - zapisany komplet ustawień eksportu.

Powtarzalny eksport dla klienta ma być jednym kliknięciem, więc do profilu
trafia wszystko: źródło, granularność, język, sklep, kolumny, tryby parametrów
i zdjęć, reguły, filtry i opcje zapisu.
"""

import json
import os

from .paths import data_path
from .rules import RuleSet
from .structures import Structure

PROFILES_DIR = data_path("profiles")

FORMAT_VERSION = 1

# Pola konfiguracji zapisywane wprost.
SIMPLE_KEYS = [
    "source_path", "source_type", "lang", "site", "row_context", "output_path",
    "param_mode", "param_names", "param_separator", "param_max_pairs",
    "param_other_column", "param_order", "include_params",
    "image_kind", "image_mode", "image_count", "image_separator", "include_images",
    "image_base_name", "image_extra_name", "uppercase_names",
    "include_icons", "icon_kind", "icon_column_name", "icon_as_main_image",
    "csv_delimiter", "csv_encoding", "csv_quoting", "csv_header",
    "xml_root", "xml_item", "xml_keep_empty", "xml_cdata",
]


def to_dict(config):
    data = {"version": FORMAT_VERSION}
    for key in SIMPLE_KEYS:
        data[key] = getattr(config, key, None)
    data["structure"] = config.structure.to_dict() if config.structure else None
    data["ruleset"] = config.ruleset.to_dict() if config.ruleset else None
    return data


def apply_dict(config, data):
    for key in SIMPLE_KEYS:
        if key in data and data[key] is not None:
            setattr(config, key, data[key])
    if data.get("structure"):
        config.structure = Structure(data["structure"])
    if data.get("ruleset"):
        config.ruleset = RuleSet.from_dict(data["ruleset"])
    return config


def save(config, path):
    folder = os.path.dirname(os.path.abspath(path))
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(to_dict(config), handle, ensure_ascii=False, indent=2)
    return path


def load(config, path):
    with open(path, "r", encoding="utf-8") as handle:
        return apply_dict(config, json.load(handle))


def list_profiles(directory=None):
    directory = directory or PROFILES_DIR
    if not os.path.isdir(directory):
        return []
    names = [n for n in sorted(os.listdir(directory)) if n.endswith(".json")]
    return [(os.path.splitext(n)[0], os.path.join(directory, n)) for n in names]


def profile_path(name, directory=None):
    directory = directory or PROFILES_DIR
    safe = u"".join(ch for ch in name if ch.isalnum() or ch in u" _-").strip()
    return os.path.join(directory, (safe or u"profil") + ".json")


# -- sesja ------------------------------------------------------------------

SESSION_PATH = data_path("last_session.json")


def save_session(config, path=None):
    """Zapisuje bieżące ustawienia jako sesję, do odtworzenia przy starcie.

    To ten sam format co profil, tylko plik jest jeden i pisany automatycznie
    przy zamknięciu okna. Profile zostają do nazwanych, powtarzalnych układów.
    """
    path = path or SESSION_PATH
    data = to_dict(config)
    data["saved_at"] = _now()
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
    except IOError:
        # Brak prawa zapisu nie może przeszkodzić w zamknięciu aplikacji.
        return u""
    return path


def session_info(path=None):
    """Opis zapisanej sesji albo None, gdy jej nie ma lub jest nieczytelna."""
    path = path or SESSION_PATH
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (IOError, ValueError):
        return None
    structure = data.get("structure") or {}
    source = data.get("source_path") or u""
    return {
        "saved_at": data.get("saved_at", u""),
        "source_path": source,
        "source_exists": bool(source) and os.path.isfile(source),
        "structure": structure.get("label", u""),
        "columns": len(structure.get("columns", [])),
        "rules": len((data.get("ruleset") or {}).get("rules", [])),
        "path": path,
    }


def load_session(config, path=None):
    path = path or SESSION_PATH
    return load(config, path)


def _now():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# -- ustawienia aplikacji ---------------------------------------------------

SETTINGS_PATH = data_path("settings.json")

DEFAULT_SETTINGS = {
    "last_dir": u"",
    "last_profile": u"",
    "scan_limit": 2000,
    "preview_rows": 20,
}


def load_settings():
    settings = dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as handle:
            settings.update(json.load(handle))
    except (IOError, ValueError):
        pass
    return settings


def save_settings(settings):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as handle:
            json.dump(settings, handle, ensure_ascii=False, indent=2)
    except IOError:
        pass
