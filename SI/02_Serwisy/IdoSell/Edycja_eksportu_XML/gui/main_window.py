# -*- coding: utf-8 -*-
"""Okno główne: cztery zakładki, podgląd pod spodem, profile w menu."""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from core import profile as profile_mod
from core.paths import resource_path
from core.structures import save as save_structure
from .preview import PreviewPanel
from .state import AppState, FIELDS_CHANGED, OUTPUT_CHANGED, SOURCE_CHANGED
from .tab_fields import FieldsTab
from .tab_output import OutputTab
from .tab_rules import RulesTab
from .tab_source import SourceTab

TITLE = u"Edycja eksportu produktów IdoSell"


class MainWindow(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self.title(TITLE)
        self.geometry("1180x820")
        self.minsize(960, 640)
        self._set_icon()

        self.state_obj = AppState()
        self._build_menu()
        self._build_body()
        self.state_obj.subscribe(self._dispatch)
        # Zamknięcie okna zapisuje sesję, start pyta, czy ją odtworzyć.
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(150, self._ask_restore_session)

    def _set_icon(self):
        """Ikona okna i paska zadań. Brak pliku nie jest powodem do awarii."""
        icon = resource_path("app.ico")
        if not os.path.isfile(icon):
            return
        try:
            self.iconbitmap(default=icon)
        except tk.TclError:
            pass

    # -- budowa ------------------------------------------------------------

    def _build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=u"Otwórz plik źródłowy…", command=self._open_source)
        file_menu.add_separator()
        file_menu.add_command(label=u"Wczytaj ustawienia z poprzedniej sesji",
                              command=self.load_session)
        file_menu.add_separator()
        file_menu.add_command(label=u"Wczytaj profil…", command=self.load_profile)
        file_menu.add_command(label=u"Zapisz profil", command=self.save_profile)
        file_menu.add_command(label=u"Zapisz profil jako…", command=self.save_profile_as)
        file_menu.add_separator()
        file_menu.add_command(label=u"Zakończ", command=self.destroy)
        menubar.add_cascade(label=u"Plik", menu=file_menu)

        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label=u"Zapisz obecny układ jako strukturę…",
                               command=self.save_as_structure)
        tools_menu.add_command(label=u"Odśwież podgląd", command=lambda: self.preview.refresh())
        menubar.add_cascade(label=u"Narzędzia", menu=tools_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=u"O programie", command=self._about)
        menubar.add_cascade(label=u"Pomoc", menu=help_menu)

        self.configure(menu=menubar)

    def _build_body(self):
        paned = ttk.PanedWindow(self, orient="vertical")
        paned.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(paned)
        paned.add(self.notebook, weight=3)

        self.tab_source = SourceTab(self.notebook, self.state_obj)
        self.tab_fields = FieldsTab(self.notebook, self.state_obj)
        self.tab_rules = RulesTab(self.notebook, self.state_obj)
        self.tab_output = OutputTab(self.notebook, self.state_obj)

        self.notebook.add(self.tab_source, text=u"1. Źródło")
        self.notebook.add(self.tab_fields, text=u"2. Pola")
        self.notebook.add(self.tab_rules, text=u"3. Reguły")
        self.notebook.add(self.tab_output, text=u"4. Wyjście")

        self.preview = PreviewPanel(paned, self.state_obj)
        paned.add(self.preview, weight=2)

        self.status = ttk.Label(self, text=u"Wybierz plik źródłowy, żeby zacząć.",
                                relief="sunken", anchor="w", padding=(8, 3))
        self.status.pack(fill="x", side="bottom")

    # -- zdarzenia ---------------------------------------------------------

    def _dispatch(self, event):
        for widget in (self.tab_source, self.tab_fields, self.tab_rules,
                       self.tab_output, self.preview):
            handler = getattr(widget, "on_event", None)
            if handler is not None:
                handler(event)
        if event == SOURCE_CHANGED:
            self._update_status()

    def _update_status(self):
        config = self.state_obj.config
        if not config.source_path:
            self.status.configure(text=u"Wybierz plik źródłowy, żeby zacząć.")
            return
        scan = self.state_obj.scan
        parts = [os.path.basename(config.source_path)]
        if config.source_type:
            parts.append(config.source_type.upper())
        if scan:
            parts.append(scan.summary())
        self.status.configure(text=u"  |  ".join(parts))

    # -- akcje menu --------------------------------------------------------

    def _open_source(self):
        self.notebook.select(self.tab_source)
        self.tab_source.choose()

    def load_profile(self):
        initial = profile_mod.PROFILES_DIR
        path = filedialog.askopenfilename(
            title=u"Wczytaj profil", initialdir=initial,
            filetypes=[(u"Profil", "*.json"), (u"Wszystkie pliki", "*.*")])
        if not path:
            return
        try:
            profile_mod.load(self.state_obj.config, path)
        except (IOError, ValueError) as error:
            messagebox.showerror(u"Profil", u"Nie udało się wczytać: %s" % error,
                                 parent=self)
            return
        self.state_obj.profile_path = path
        self.state_obj.settings["last_profile"] = path
        self.state_obj.save_settings()
        config = self.state_obj.config
        if config.source_path and os.path.isfile(config.source_path):
            self.tab_source.set_path(config.source_path)
        else:
            self.state_obj.notify(SOURCE_CHANGED)
            self.state_obj.notify(FIELDS_CHANGED)
            self.state_obj.notify(OUTPUT_CHANGED)
        self.status.configure(text=u"Wczytano profil: %s" % os.path.basename(path))

    def save_profile(self):
        if not self.state_obj.profile_path:
            return self.save_profile_as()
        self._write_profile(self.state_obj.profile_path)

    def save_profile_as(self):
        name = simpledialog.askstring(u"Zapisz profil", u"Nazwa profilu:", parent=self)
        if not name:
            return
        path = profile_mod.profile_path(name)
        self._write_profile(path)

    def _write_profile(self, path):
        self.tab_output._collect()
        try:
            profile_mod.save(self.state_obj.config, path)
        except IOError as error:
            messagebox.showerror(u"Profil", u"Nie udało się zapisać: %s" % error,
                                 parent=self)
            return
        self.state_obj.profile_path = path
        self.state_obj.settings["last_profile"] = path
        self.state_obj.save_settings()
        self.status.configure(text=u"Zapisano profil: %s" % os.path.basename(path))

    def save_as_structure(self):
        structure = self.state_obj.config.structure
        if structure is None:
            return
        name = simpledialog.askstring(u"Nowa struktura",
                                      u"Nazwa struktury:", parent=self,
                                      initialvalue=structure.label)
        if not name:
            return
        copy = structure.copy()
        copy.label = name
        copy.id = _slug(name)
        copy.path = None
        try:
            path = save_structure(copy)
        except IOError as error:
            messagebox.showerror(u"Struktura", u"Nie udało się zapisać: %s" % error,
                                 parent=self)
            return
        self.state_obj.structures.append(copy)
        messagebox.showinfo(u"Struktura",
                            u"Zapisano: %s\n\nBędzie widoczna po ponownym "
                            u"uruchomieniu aplikacji." % path, parent=self)

    # -- sesja -------------------------------------------------------------

    def _ask_restore_session(self):
        """Pytanie przy starcie - ustawienia wracają tylko na wyraźną zgodę."""
        info = profile_mod.session_info()
        if not info:
            return
        if not messagebox.askyesno(TITLE, _session_question(info), parent=self,
                                   default="yes"):
            self.status.configure(text=u"Start z ustawieniami domyślnymi. "
                                       u"Poprzednią sesję wczytasz z menu Plik.")
            return
        self._apply_session(info)

    def load_session(self):
        info = profile_mod.session_info()
        if not info:
            messagebox.showinfo(TITLE, u"Nie ma jeszcze zapisanej sesji - powstaje "
                                       u"przy zamknięciu aplikacji.", parent=self)
            return
        self._apply_session(info)

    def _apply_session(self, info):
        try:
            profile_mod.load_session(self.state_obj.config)
        except (IOError, ValueError) as error:
            messagebox.showerror(TITLE, u"Nie udało się wczytać poprzedniej sesji: %s"
                                        % error, parent=self)
            return
        config = self.state_obj.config
        if info["source_exists"]:
            self.tab_source.set_path(config.source_path)
        else:
            # Ustawienia zostają, znika tylko wskazanie na nieistniejący plik.
            config.source_path = u""
            self.state_obj.notify(SOURCE_CHANGED)
            self.state_obj.notify(FIELDS_CHANGED)
            self.state_obj.notify(OUTPUT_CHANGED)
        message = u"Wczytano ustawienia z sesji %s" % info["saved_at"]
        if info["source_path"] and not info["source_exists"]:
            message += u"  |  plik %s już nie istnieje - wskaż źródło na nowo" % (
                os.path.basename(info["source_path"]))
        self.status.configure(text=message)

    def _on_close(self):
        self._save_session()
        self.destroy()

    def _save_session(self):
        try:
            self.tab_output._collect()
        except Exception:
            # Zamknięcie ma się udać nawet wtedy, gdy któryś widget już nie żyje.
            pass
        profile_mod.save_session(self.state_obj.config)

    def _about(self):
        messagebox.showinfo(
            TITLE,
            u"Edycja eksportu produktów IdoSell\n\n"
            u"Wczytuje eksport IOF (XML) albo tabelaryczny (CSV) z panelu, pozwala "
            u"wybrać dane, nałożyć reguły i zapisać wynik jako płaski CSV, prosty XML "
            u"dla arkuszy albo przycięty IOF.\n\n"
            u"Python 3 i biblioteka standardowa - bez zależności zewnętrznych.",
            parent=self)


def _session_question(info):
    lines = [u"Wczytać ustawienia z poprzedniej sesji?", u""]
    if info["saved_at"]:
        lines.append(u"Zapisane: %s" % info["saved_at"])
    if info["source_path"]:
        name = os.path.basename(info["source_path"])
        lines.append(u"Plik: %s%s" % (name, u"" if info["source_exists"]
                                      else u"   (już go nie ma)"))
    if info["structure"]:
        lines.append(u"Struktura: %s, kolumn: %d" % (info["structure"], info["columns"]))
    if info["rules"]:
        lines.append(u"Reguły: %d" % info["rules"])
    lines.append(u"")
    lines.append(u"„Nie” zaczyna od ustawień domyślnych - zapis sesji zostaje "
                 u"nietknięty.")
    return u"\n".join(lines)


def _slug(name):
    text = u"".join(ch if ch.isalnum() else u"_" for ch in name.lower())
    while u"__" in text:
        text = text.replace(u"__", u"_")
    return text.strip(u"_") or u"struktura"


def run():
    window = MainWindow()
    window.mainloop()
