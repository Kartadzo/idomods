# -*- coding: utf-8 -*-
"""Edycja eksportu produktów IdoSell - uruchomienie aplikacji graficznej.

    python app.py [plik_zrodlowy]

Ścieżka w argumencie jest tylko skrótem - bez niej plik wybiera się w oknie.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    try:
        import tkinter  # noqa: F401
    except ImportError:
        sys.stderr.write(
            "Brak modulu tkinter. Zainstaluj Pythona z opcja 'tcl/tk and IDLE'.\n")
        return 2

    from gui.main_window import MainWindow

    window = MainWindow()
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        window.after(150, lambda: window.tab_source.set_path(sys.argv[1]))
    window.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
