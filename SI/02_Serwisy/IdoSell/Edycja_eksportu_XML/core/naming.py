# -*- coding: utf-8 -*-
"""Nazwy kolumn i elementów wyniku.

Jedno miejsce, które decyduje, jak wygląda nagłówek w pliku wyjściowym.
Nazwa ustawiona przez użytkownika jest źródłem prawdy - przełącznik pisowni
zmienia tylko jej wielkość liter, więc da się go cofnąć bez utraty nazw.
"""


def output_name(name, uppercase=False):
    """Nazwa kolumny albo elementu w postaci, w jakiej trafi do pliku."""
    if not uppercase or not name:
        return name
    return name.upper()


def output_names(names, uppercase=False):
    """To samo dla listy - z zachowaniem kolejności i bez duplikatów."""
    result = []
    for name in names:
        converted = output_name(name, uppercase)
        if converted not in result:
            result.append(converted)
    return result
