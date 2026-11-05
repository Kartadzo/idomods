# -*- coding: utf-8 -*-
"""Zakładka 2: pola i kolumny wyniku.

Po lewej pełne drzewo pól - także tych, których nie ma w wybranym pliku.
Pole niedostępne w źródle zostaje na liście, tylko wyszarzone z adnotacją,
żeby było widać pełen zakres możliwości, a nie część wspólną obu formatów.

Po prawej kolumny wyniku: nazwa docelowa, kolejność, usuwanie. Pod spodem tryby
rozbicia parametrów i zdjęć, bo tylko one mają zmienną liczbę wartości.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from core.expanders import (ICON_KIND_LABELS, IMAGE_COLUMNS, IMAGE_MODE_LABELS,
                            ImageExpander, PARAM_COLUMN, PARAM_MODE_LABELS,
                            PARAM_PAIRS)
from core.naming import output_name
from core.schema import HIDDEN_GROUPS, KIND_PARAMS
from core.structures import Column
from .state import FIELDS_CHANGED, OUTPUT_CHANGED, SOURCE_CHANGED

# Zdjęcia produktowe. Ikony (aukcyjna, grupy, miniatura karty) to nie są zdjęcia
# produktu i w feedach nie mają zastosowania, więc nie ma ich na liście.
IMAGE_KINDS = [
    (u"large", u"duże"),
    (u"medium", u"średnie"),
    (u"small", u"małe"),
    (u"originals", u"oryginalne"),
]

# Które typy zdjęć w ogóle występują w danym źródle.
IMAGE_SOURCES = {
    u"large": ("xml", "csv"),
    u"medium": ("xml",), u"small": ("xml",), u"originals": ("xml",),
}

# Ikony ma i XML, i CSV - w obu rozbite na trzy rodzaje.
ICON_SOURCES = {
    u"icons": ("xml", "csv"),
    u"auction_icon": ("xml", "csv"),
    u"group_icon": ("xml", "csv"),
}


class FieldsTab(ttk.Frame):

    def __init__(self, master, state):
        ttk.Frame.__init__(self, master, padding=8)
        self.state = state
        self._field_by_item = {}
        self._build()
        self.refresh()

    def _build(self):
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=4)
        self.rowconfigure(0, weight=1)

        # -- drzewo pól ---------------------------------------------------
        left = ttk.LabelFrame(self, text=u"Dostępne pola", padding=6)
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(left, columns=("note",), show="tree headings",
                                 selectmode="extended")
        self.tree.heading("#0", text=u"Pole")
        self.tree.heading("note", text=u"Uwaga")
        self.tree.column("#0", width=280, stretch=True)
        self.tree.column("note", width=150, stretch=False)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.tag_configure("unavailable", foreground="#9a9a9a")
        self.tree.bind("<Double-1>", lambda e: self.add_selected())

        # -- przyciski ----------------------------------------------------
        middle = ttk.Frame(self)
        middle.grid(row=0, column=1, sticky="ns", padx=6)
        ttk.Button(middle, text=u"Dodaj →", command=self.add_selected).pack(pady=(40, 4))
        ttk.Button(middle, text=u"← Usuń", command=self.remove_selected).pack(pady=4)
        ttk.Separator(middle, orient="horizontal").pack(fill="x", pady=10)
        ttk.Button(middle, text=u"Zmień nazwę", command=self.rename_selected).pack(pady=4)
        ttk.Button(middle, text=u"▲", width=4, command=lambda: self.move(-1)).pack(pady=(10, 2))
        ttk.Button(middle, text=u"▼", width=4, command=lambda: self.move(1)).pack(pady=2)

        # -- kolumny wyniku ------------------------------------------------
        right = ttk.LabelFrame(self, text=u"Kolumny wyniku", padding=6)
        right.grid(row=0, column=2, sticky="nsew")
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self.columns_view = ttk.Treeview(right, columns=("field",), show="tree headings")
        self.columns_view.heading("#0", text=u"Nazwa docelowa")
        self.columns_view.heading("field", text=u"Źródło")
        self.columns_view.column("#0", width=200)
        self.columns_view.column("field", width=200)
        self.columns_view.grid(row=0, column=0, sticky="nsew")
        column_scroll = ttk.Scrollbar(right, orient="vertical",
                                      command=self.columns_view.yview)
        column_scroll.grid(row=0, column=1, sticky="ns")
        self.columns_view.configure(yscrollcommand=column_scroll.set)
        self.columns_view.bind("<Double-1>", lambda e: self.rename_selected())
        self.columns_view.tag_configure("unavailable", foreground="#b45f06")

        self.uppercase = tk.BooleanVar(value=self.state.config.uppercase_names)
        ttk.Checkbutton(right, text=u"nazwy kolumn i elementów WIELKIMI LITERAMI",
                        variable=self.uppercase,
                        command=self._uppercase_changed).grid(row=1, column=0,
                                                              columnspan=2,
                                                              sticky="w", pady=(6, 0))

        # -- parametry i zdjęcia -------------------------------------------
        bottom = ttk.Frame(self)
        bottom.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=1)
        bottom.columnconfigure(2, weight=1)
        self._build_params(bottom)
        self._build_images(bottom)
        self._build_icons(bottom)

    def _build_params(self, master):
        box = ttk.LabelFrame(master, text=u"Parametry", padding=6)
        box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        config = self.state.config
        self.params_on = tk.BooleanVar(value=config.include_params)
        ttk.Checkbutton(box, text=u"dołącz parametry", variable=self.params_on,
                        command=self._params_changed).grid(row=0, column=0,
                                                           columnspan=3, sticky="w")
        self.param_mode = tk.StringVar(value=config.param_mode)
        row = 1
        for value, label in PARAM_MODE_LABELS:
            ttk.Radiobutton(box, text=label, value=value, variable=self.param_mode,
                            command=self._params_changed).grid(row=row, column=0,
                                                               columnspan=2, sticky="w")
            row += 1

        self.param_pick = ttk.Button(box, text=u"Wybierz parametry…",
                                     command=self.choose_params)
        self.param_pick.grid(row=1, column=2, sticky="e", padx=4)

        ttk.Label(box, text=u"maks. par:").grid(row=3, column=2, sticky="e")
        self.param_pairs = tk.StringVar(value=u"%d" % config.param_max_pairs)
        pairs = ttk.Spinbox(box, from_=1, to=99, width=5, textvariable=self.param_pairs,
                            command=self._params_changed)
        pairs.grid(row=3, column=3, sticky="w", padx=4)
        pairs.bind("<FocusOut>", lambda e: self._params_changed())

        self.param_count_label = ttk.Label(box, text=u"", foreground="#666666")
        self.param_count_label.grid(row=4, column=0, columnspan=4, sticky="w", pady=(4, 0))

    def _build_icons(self, master):
        box = ttk.LabelFrame(master, text=u"Ikony", padding=6)
        box.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
        box.columnconfigure(1, weight=1)

        config = self.state.config
        self.icons_on = tk.BooleanVar(value=config.include_icons)
        ttk.Checkbutton(box, text=u"dołącz ikonę", variable=self.icons_on,
                        command=self._icons_changed).grid(row=0, column=0, columnspan=2,
                                                          sticky="w")

        ttk.Label(box, text=u"rodzaj:").grid(row=1, column=0, sticky="w")
        self.icon_kind = tk.StringVar(value=config.icon_kind)
        self.icon_combo = ttk.Combobox(box, textvariable=self.icon_kind, width=22,
                                       state="readonly")
        self.icon_combo.grid(row=1, column=1, sticky="ew", padx=4)
        self.icon_combo.bind("<<ComboboxSelected>>", lambda e: self._icons_changed())

        ttk.Label(box, text=u"nazwa kolumny:").grid(row=2, column=0, sticky="w",
                                                    pady=(4, 0))
        self.icon_column_name = tk.StringVar(value=config.icon_column_name)
        entry = ttk.Entry(box, textvariable=self.icon_column_name, width=22)
        entry.grid(row=2, column=1, sticky="ew", padx=4, pady=(4, 0))
        entry.bind("<FocusOut>", lambda e: self._icons_changed())

        self.icon_as_main = tk.BooleanVar(value=config.icon_as_main_image)
        ttk.Checkbutton(box, text=u"użyj także jako zdjęcia głównego",
                        variable=self.icon_as_main,
                        command=self._icons_changed).grid(row=3, column=0, columnspan=2,
                                                          sticky="w", pady=(4, 0))

        self.icon_note = ttk.Label(box, text=u"", foreground="#666666", wraplength=260)
        self.icon_note.grid(row=4, column=0, columnspan=2, sticky="w", pady=(4, 0))

    def _refresh_icons(self):
        source_type = self.state.source_type
        found = self.state.scan.image_kinds if self.state.scan else {}
        labels = []
        self._icon_values = []
        for kind, label in ICON_KIND_LABELS:
            text = label
            if found.get(kind):
                text += u" (jest)"
            elif source_type and source_type not in ICON_SOURCES.get(kind, ()):
                text += u" — brak w tym źródle"
            labels.append(text)
            self._icon_values.append(kind)
        self.icon_combo.configure(values=labels)
        config = self.state.config
        if config.icon_kind in self._icon_values:
            self.icon_combo.current(self._icon_values.index(config.icon_kind))
        elif labels:
            self.icon_combo.current(0)
            config.icon_kind = self._icon_values[0]

        if config.icon_as_main_image:
            self.icon_note.configure(
                text=u"Ikona wejdzie na pierwsze miejsce w kolumnie „%s”, a zdjęcia "
                     u"przesuną się o jedno dalej." % output_name(
                         config.image_base_name, config.uppercase_names))
        elif not found.get(config.icon_kind) and self.state.scan:
            self.icon_note.configure(text=u"W przeskanowanej części pliku nie ma "
                                          u"takiej ikony.")
        else:
            self.icon_note.configure(text=u"Ikona zajmuje własną kolumnę, obok zdjęć.")

    def _icons_changed(self):
        config = self.state.config
        config.include_icons = bool(self.icons_on.get())
        index = self.icon_combo.current()
        if 0 <= index < len(self._icon_values):
            config.icon_kind = self._icon_values[index]
        config.icon_column_name = self.icon_column_name.get().strip() or u"icon"
        config.icon_as_main_image = bool(self.icon_as_main.get())
        self._refresh_icons()
        self._refresh_images()
        self.state.notify(FIELDS_CHANGED)

    def _build_images(self, master):
        box = ttk.LabelFrame(master, text=u"Zdjęcia", padding=6)
        box.grid(row=0, column=1, sticky="nsew")

        config = self.state.config
        self.images_on = tk.BooleanVar(value=config.include_images)
        ttk.Checkbutton(box, text=u"dołącz zdjęcia", variable=self.images_on,
                        command=self._images_changed).grid(row=0, column=0,
                                                           columnspan=3, sticky="w")

        ttk.Label(box, text=u"typ:").grid(row=1, column=0, sticky="w")
        self.image_kind = tk.StringVar(value=config.image_kind)
        self.image_combo = ttk.Combobox(box, textvariable=self.image_kind, width=22,
                                        state="readonly")
        self.image_combo.grid(row=1, column=1, sticky="w", padx=4)
        self.image_combo.bind("<<ComboboxSelected>>", lambda e: self._images_changed())

        self.image_mode = tk.StringVar(value=config.image_mode)
        row = 2
        for value, label in IMAGE_MODE_LABELS:
            ttk.Radiobutton(box, text=label, value=value, variable=self.image_mode,
                            command=self._images_changed).grid(row=row, column=0,
                                                               columnspan=2, sticky="w")
            row += 1

        ttk.Label(box, text=u"maks. zdjęć:").grid(row=2, column=2, sticky="e")
        self.image_count = tk.StringVar(value=u"%d" % config.image_count)
        spin = ttk.Spinbox(box, from_=1, to=50, width=5, textvariable=self.image_count,
                           command=self._images_changed)
        spin.grid(row=2, column=3, sticky="w", padx=4)
        spin.bind("<FocusOut>", lambda e: self._images_changed())

        # Nazwy kolumn (w XML: elementów) - inne narzędzia wymagają konkretnych,
        # np. `image_link` i `additional_image_link` w Google Shopping.
        ttk.Label(box, text=u"nazwa pierwszego:").grid(row=5, column=0, sticky="w",
                                                       pady=(6, 0))
        self.image_base_name = tk.StringVar(value=config.image_base_name)
        base_entry = ttk.Entry(box, textvariable=self.image_base_name, width=24)
        base_entry.grid(row=5, column=1, columnspan=3, sticky="ew", padx=4, pady=(6, 0))
        base_entry.bind("<FocusOut>", lambda e: self._images_changed())

        ttk.Label(box, text=u"nazwa kolejnych:").grid(row=6, column=0, sticky="w")
        self.image_extra_name = tk.StringVar(value=config.image_extra_name)
        self.extra_entry = ttk.Entry(box, textvariable=self.image_extra_name, width=24)
        self.extra_entry.grid(row=6, column=1, columnspan=3, sticky="ew", padx=4)
        self.extra_entry.bind("<FocusOut>", lambda e: self._images_changed())

        self.image_names_hint = ttk.Label(
            box, text=u"", foreground="#666666", wraplength=320)
        self.image_names_hint.grid(row=7, column=0, columnspan=4, sticky="w")

        self.image_note = ttk.Label(box, text=u"", foreground="#666666", wraplength=320)
        self.image_note.grid(row=8, column=0, columnspan=4, sticky="w", pady=(4, 0))
        box.columnconfigure(1, weight=1)

    # -- odświeżanie ------------------------------------------------------

    def refresh(self):
        self._sync_from_config()
        self._fill_tree()
        self._fill_columns()
        self._refresh_images()
        self._refresh_icons()
        self._refresh_params()

    def _sync_from_config(self):
        """Wczytany profil zmienia konfigurację - kontrolki muszą za nią nadążyć."""
        config = self.state.config
        self.uppercase.set(config.uppercase_names)
        self.params_on.set(config.include_params)
        self.param_mode.set(config.param_mode)
        self.images_on.set(config.include_images)
        self.image_mode.set(config.image_mode)
        self.image_base_name.set(config.image_base_name)
        self.image_extra_name.set(config.image_extra_name)
        self.icons_on.set(config.include_icons)
        self.icon_column_name.set(config.icon_column_name)
        self.icon_as_main.set(config.icon_as_main_image)

    def _fill_tree(self):
        self.tree.delete(*self.tree.get_children())
        self._field_by_item = {}
        source_type = self.state.source_type
        for group, fields in self.state.registry.groups():
            # Zdjęcia i parametry mają własne sekcje pod spodem - na liście pól
            # byłyby drugim, uboższym sposobem na to samo.
            if group in HIDDEN_GROUPS:
                continue
            node = self.tree.insert("", "end", text=group, open=(group != u"Nierozpoznane"))
            for field in fields:
                if field.kind == KIND_PARAMS:
                    continue
                available = source_type is None or field.available_in(source_type)
                note = field.note
                if not available:
                    other = u"CSV" if source_type == "xml" else u"XML"
                    note = u"tylko w %s" % other
                item = self.tree.insert(node, "end", text=field.label, values=(note,),
                                        tags=() if available else ("unavailable",))
                self._field_by_item[item] = field

    def _fill_columns(self):
        self.columns_view.delete(*self.columns_view.get_children())
        source_type = self.state.source_type
        structure = self.state.config.structure
        if structure is None:
            return
        uppercase = self.state.config.uppercase_names
        for column in structure.columns:
            field = self.state.registry.get(column.field)
            label = field.label if field else column.field
            tags = ()
            if field is not None and source_type and not field.available_in(source_type):
                label += u"  (brak w tym źródle)"
                tags = ("unavailable",)
            # Pokazujemy nazwę taką, jaka trafi do pliku - z uwzględnieniem pisowni.
            self.columns_view.insert("", "end", text=output_name(column.out, uppercase),
                                     values=(label,), tags=tags)

    def _refresh_params(self):
        scan = self.state.scan
        names = [n for _, n in (scan.params if scan else [])]
        config = self.state.config
        if not config.param_names and names:
            config.param_names = list(names)
        mode = self.param_mode.get()
        self.param_pick.configure(
            state="normal" if mode == PARAM_COLUMN and names else "disabled")
        if mode == PARAM_COLUMN:
            self.param_count_label.configure(
                text=u"kolumny: %d z %d wykrytych" % (len(config.param_names), len(names)))
        elif mode == PARAM_PAIRS:
            self.param_count_label.configure(
                text=u"wykrytych parametrów: %d (maks. w produkcie decyduje o liczbie par)"
                     % len(names))
        else:
            self.param_count_label.configure(text=u"jedna kolumna z wartościami jak w źródle")

    def _refresh_images(self):
        source_type = self.state.source_type
        scan = self.state.scan
        found = scan.image_kinds if scan else {}
        labels = []
        self._image_values = []
        for kind, label in IMAGE_KINDS:
            available = source_type is None or source_type in IMAGE_SOURCES.get(kind, ())
            count = found.get(kind)
            text = label
            if count:
                text += u" (maks. %d)" % count
            elif not available:
                other = u"CSV" if source_type == "xml" else u"XML"
                text += u" — tylko w %s" % other
            labels.append(text)
            self._image_values.append(kind)
        self.image_combo.configure(values=labels)
        config = self.state.config
        current = config.image_kind
        if current in self._image_values:
            self.image_combo.current(self._image_values.index(current))
        elif labels:
            # Profil z nieistniejącym już typem (np. ikoną) - wracamy do zdjęć dużych.
            self.image_combo.current(0)
            config.image_kind = self._image_values[0]

        per_column = config.image_mode == IMAGE_COLUMNS
        self.extra_entry.configure(state="normal" if per_column else "disabled")
        if per_column:
            expander = ImageExpander(mode=IMAGE_COLUMNS, count=max(2, config.image_count),
                                     base_name=config.image_base_name,
                                     extra_name=config.image_extra_name)
            names = expander.columns()
            uppercase = config.uppercase_names
            preview = u", ".join(output_name(n, uppercase) for n in names[:3])
            self.image_names_hint.configure(
                text=u"Gwiazdka w nazwie kolejnych zastępuje numer. Wyjdzie: %s…"
                     % preview)
        else:
            self.image_names_hint.configure(
                text=u"Ten tryb daje jedną kolumnę - liczy się tylko nazwa pierwszego.")

        maximum = found.get(config.image_kind)
        self.image_note.configure(
            text=u"W pliku najwięcej zdjęć na produkt: %d." % maximum if maximum else u"")

    # -- akcje -------------------------------------------------------------

    def add_selected(self):
        structure = self.state.config.structure
        if structure is None:
            return
        added = 0
        for item in self.tree.selection():
            field = self._field_by_item.get(item)
            if field is None:
                continue
            name = _unique_name(field.label, [c.out for c in structure.columns])
            structure.columns.append(Column(name, field.id))
            added += 1
        if added:
            self._fill_columns()
            self.state.notify(FIELDS_CHANGED)

    def remove_selected(self):
        structure = self.state.config.structure
        selection = self.columns_view.selection()
        if not structure or not selection:
            return
        indexes = sorted((self.columns_view.index(i) for i in selection), reverse=True)
        for index in indexes:
            if 0 <= index < len(structure.columns):
                del structure.columns[index]
        self._fill_columns()
        self.state.notify(FIELDS_CHANGED)

    def rename_selected(self):
        structure = self.state.config.structure
        selection = self.columns_view.selection()
        if not structure or not selection:
            return
        index = self.columns_view.index(selection[0])
        column = structure.columns[index]
        uppercase = self.state.config.uppercase_names
        new_name = simpledialog.askstring(
            u"Nazwa kolumny", u"Nazwa docelowa:",
            initialvalue=output_name(column.out, uppercase), parent=self)
        if not new_name:
            return
        others = [c.out for i, c in enumerate(structure.columns) if i != index]
        if new_name in others:
            messagebox.showwarning(u"Nazwa zajęta",
                                   u"Kolumna o tej nazwie już istnieje.", parent=self)
            return
        column.out = new_name
        self._fill_columns()
        self.state.notify(FIELDS_CHANGED)

    def move(self, delta):
        structure = self.state.config.structure
        selection = self.columns_view.selection()
        if not structure or not selection:
            return
        index = self.columns_view.index(selection[0])
        target = index + delta
        if target < 0 or target >= len(structure.columns):
            return
        structure.columns[index], structure.columns[target] = (
            structure.columns[target], structure.columns[index])
        self._fill_columns()
        children = self.columns_view.get_children()
        if target < len(children):
            self.columns_view.selection_set(children[target])
        self.state.notify(FIELDS_CHANGED)

    def choose_params(self):
        scan = self.state.scan
        if not scan or not scan.params:
            messagebox.showinfo(u"Parametry",
                                u"Najpierw zeskanuj plik - lista parametrów bierze się "
                                u"ze skanu.", parent=self)
            return
        dialog = ParamPicker(self, [n for _, n in scan.params],
                             self.state.config.param_names)
        self.wait_window(dialog)
        if dialog.result is not None:
            self.state.config.param_names = dialog.result
            self._refresh_params()
            self.state.notify(FIELDS_CHANGED)

    def _params_changed(self):
        config = self.state.config
        config.include_params = bool(self.params_on.get())
        config.param_mode = self.param_mode.get()
        try:
            config.param_max_pairs = max(1, int(self.param_pairs.get() or 10))
        except ValueError:
            config.param_max_pairs = 10
        self._refresh_params()
        self.state.notify(FIELDS_CHANGED)

    def _images_changed(self):
        config = self.state.config
        config.include_images = bool(self.images_on.get())
        index = self.image_combo.current()
        if 0 <= index < len(self._image_values):
            config.image_kind = self._image_values[index]
        config.image_mode = self.image_mode.get()
        try:
            config.image_count = max(1, int(self.image_count.get() or 1))
        except ValueError:
            config.image_count = 1
        config.image_base_name = self.image_base_name.get().strip() or u"image"
        config.image_extra_name = (self.image_extra_name.get().strip()
                                   or u"image_extra_*")
        self._refresh_images()
        self.state.notify(FIELDS_CHANGED)

    def _uppercase_changed(self):
        self.state.config.uppercase_names = bool(self.uppercase.get())
        self._fill_columns()
        self._refresh_images()
        self._refresh_icons()
        self.state.notify(FIELDS_CHANGED)

    def on_event(self, event):
        if event in (SOURCE_CHANGED, OUTPUT_CHANGED):
            self.refresh()


def _unique_name(base, existing):
    name = base
    suffix = 2
    while name in existing:
        name = u"%s_%d" % (base, suffix)
        suffix += 1
    return name


class ParamPicker(tk.Toplevel):
    """Wybór parametrów, które dostaną własną kolumnę."""

    def __init__(self, master, available, selected):
        tk.Toplevel.__init__(self, master)
        self.title(u"Parametry jako kolumny")
        self.result = None
        self.transient(master)
        self.grab_set()

        frame = ttk.Frame(self, padding=8)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=u"Zaznacz parametry, które mają dostać własną kolumnę. "
                              u"Kolejność zaznaczenia wyznacza kolejność kolumn."
                  ).pack(anchor="w", pady=(0, 6))

        self.listbox = tk.Listbox(frame, selectmode="extended", width=48, height=16,
                                  exportselection=False)
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.listbox.yview)
        scroll.pack(side="left", fill="y")
        self.listbox.configure(yscrollcommand=scroll.set)

        self.available = list(available)
        chosen = set(selected or [])
        for index, name in enumerate(self.available):
            self.listbox.insert("end", name)
            if name in chosen:
                self.listbox.selection_set(index)

        buttons = ttk.Frame(self, padding=(8, 0, 8, 8))
        buttons.pack(fill="x")
        ttk.Button(buttons, text=u"Zaznacz wszystkie",
                   command=lambda: self.listbox.selection_set(0, "end")).pack(side="left")
        ttk.Button(buttons, text=u"Wyczyść",
                   command=lambda: self.listbox.selection_clear(0, "end")).pack(side="left",
                                                                                padx=4)
        ttk.Button(buttons, text=u"Anuluj", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text=u"OK", command=self._accept).pack(side="right", padx=4)

    def _accept(self):
        self.result = [self.available[i] for i in self.listbox.curselection()]
        self.destroy()
