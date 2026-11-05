# -*- coding: utf-8 -*-
"""Gdzie leżą dane aplikacji.

Uruchomiona ze źródeł aplikacja trzyma wszystko w katalogu projektu. Zapakowana
w `.exe` rozpakowuje swoje zasoby do katalogu tymczasowego, który znika po
zamknięciu - dane użytkownika (profile, ustawienia, sesja, własne struktury)
muszą więc lądować obok pliku wykonywalnego, a nie w paczce.
"""

import os
import sys


def frozen():
    """Czy działamy jako spakowany plik wykonywalny."""
    return bool(getattr(sys, "frozen", False))


def app_dir():
    """Katalog na dane użytkownika: profile, ustawienia, sesja, struktury."""
    if frozen():
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_dir():
    """Katalog z zasobami dołączonymi do paczki - ikona, wzorcowe struktury."""
    return getattr(sys, "_MEIPASS", app_dir())


def data_path(*parts):
    return os.path.join(app_dir(), *parts)


def resource_path(*parts):
    return os.path.join(resource_dir(), *parts)
