# -*- coding: utf-8 -*-
"""Zakładka 3: reguły i filtry.

Reguła zmienia wartość jednej kolumny, filtr odrzuca cały wiersz. Oba korzystają
z tego samego edytora warunków, bo to ten sam mechanizm - różni się tylko to,
co się dzieje, gdy warunek jest spełniony.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from core.naming import output_name
from core.rules import (ACTIONS, ACTION_LABELS, Condition, ConditionGroup,
                        OPERATORS, OPERATOR_LABELS, RecordFilter, Rule)
from .state import FIELDS_CHANGED, RULES_CHANGED

# Pola formularza dla każdej akcji: (klucz, etykieta, typ).
ACTION_PARAMS = {
    "set": [("value", u"Wartość", "text")],
    "map": [("mapping", u"Lista zamian", "map"),
            ("keep_unmapped", u"Zostaw wartości spoza listy", "bool"),
            ("default", u"Wartość domyślna", "text")],
    "regex_replace": [("pattern", u"Czego szukać", "text"),
                      ("replacement", u"Czym zastąpić", "text"),
                      ("case_sensitive", u"Rozróżniaj wielkie i małe litery", "bool")],
    "prefix": [("value", u"Tekst na początku", "text")],
    "suffix": [("value", u"Tekst na końcu", "text")],
    "template": [("template", u"Wzorzec", "text")],
    "fallback": [("fields", u"Kolumny zapasowe", "list"),
                 ("default", u"Wartość domyślna", "text")],
    "truncate": [("length", u"Maksymalna długość", "int"),
                 ("on_word", u"Tnij na granicy słowa", "bool"),
                 ("ellipsis", u"Dopisek na końcu", "text")],
    "case": [("style", u"Styl", "choice:lower=małe,upper=WIELKIE,"
                                u"title=Każde Słowo,sentence=Jak zdanie")],
    "number": [("multiply", u"Pomnóż przez", "text"),
               ("add", u"Dodaj", "text"),
               ("decimals", u"Miejsc po przecinku", "text"),
               ("decimal_separator", u"Separator dziesiętny", "text")],
    "date_format": [("input_format", u"Format w źródle", "text"),
                    ("output_format", u"Format w wyniku", "text")],
    "pick": [("index", u"Numer wartości", "int"),
             ("separator", u"Co rozdziela wartości", "text")],
    "join": [("glue", u"Łącznik", "text"),
             ("separator", u"Co rozdziela wartości", "text")],
    "strip_html": [], "collapse_ws": [], "blank": [],
}

# Co robi akcja - pełnym zdaniem, bez żargonu. Widoczne nad ustawieniami.
ACTION_HELP = {
    "set": u"Wpisuje tę samą wartość w każdym wierszu, niezależnie od tego, co było "
           u"w kolumnie wcześniej.",
    "map": u"Podmienia konkretne wartości na inne według listy - np. nazwy kolorów "
           u"na angielskie albo „tak/nie” na „1/0”. Wartości spoza listy możesz "
           u"zostawić bez zmian.",
    "regex_replace": u"Znajduje fragment tekstu i zastępuje go innym. Działa jak "
                     u"szukaj-zamień w edytorze, a dodatkowo rozumie zapis wzorców, "
                     u"jeśli go potrzebujesz.",
    "prefix": u"Dokłada tekst na początku wartości - np. adres sklepu przed ścieżką "
              u"zdjęcia.",
    "suffix": u"Dokłada tekst na końcu wartości - np. dopisek o wysyłce po nazwie "
              u"produktu.",
    "template": u"Buduje nową wartość z kilku kolumn naraz. Nazwy kolumn wpisujesz "
                u"w klamrach, resztę zwykłym tekstem.",
    "fallback": u"Gdy kolumna jest pusta, bierze wartość z pierwszej niepustej kolumny "
                u"z podanej listy - np. brak opisu skróconego uzupełnia pełnym.",
    "truncate": u"Skraca zbyt długi tekst do zadanej liczby znaków - przydatne, gdy "
                u"porównywarka ma limit długości tytułu albo opisu.",
    "strip_html": u"Usuwa znaczniki HTML (<b>, <p>, <br>) i zostawia sam tekst. "
                  u"Ta akcja nie ma ustawień.",
    "collapse_ws": u"Zamienia ciągi spacji, tabulatorów i przejść do nowej linii na "
                   u"pojedynczą spację - porządkuje opisy sklejone z panelu. "
                   u"Ta akcja nie ma ustawień.",
    "case": u"Zmienia wielkość liter w całej wartości - np. nazwy pisane KAPITALIKAMI "
            u"na normalne.",
    "number": u"Przelicza liczbę: mnoży, dodaje, zaokrągla i ustawia znak dziesiętny - "
              u"np. cenę netto na brutto albo przecinek na kropkę.",
    "date_format": u"Zmienia zapis daty z jednego formatu na inny, np. 2026-08-28 na "
                   u"28.08.2026.",
    "pick": u"Z kilku wartości w jednej komórce (np. listy zdjęć) bierze jedną, "
            u"wskazaną numerem.",
    "join": u"Skleja wszystkie wartości z komórki w jeden tekst, wstawiając między nie "
            u"wybrany łącznik.",
    "blank": u"Czyści kolumnę - zostaje pusta. Przydatne, gdy kolumna ma być w pliku, "
             u"ale bez danych. Ta akcja nie ma ustawień.",
}

# Podpowiedź pod konkretnym polem: (akcja, klucz) -> tekst.
PARAM_HELP = {
    ("set", "value"): u"Tekst wpisywany w każdym wierszu. Może zostać pusty.",
    ("map", "mapping"): u"Po jednej parze w linii: wartość ze źródła, znak równości, "
                        u"wartość docelowa. Przykład:  Czerwony=Red",
    ("map", "keep_unmapped"): u"Zaznaczone: wartość, której nie ma na liście, zostaje "
                              u"bez zmian. Odznaczone: zastępuje ją wartość domyślna.",
    ("map", "default"): u"Używana tylko wtedy, gdy opcja powyżej jest odznaczona.",
    ("regex_replace", "pattern"): u"Zwykły tekst działa jak szukaj-zamień. Zapis "
                                  u"zaawansowany: \\d to cyfra, .* dowolny ciąg, "
                                  u"^ początek, $ koniec wartości.",
    ("regex_replace", "replacement"): u"Puste pole usuwa znaleziony fragment.",
    ("regex_replace", "case_sensitive"): u"Zaznaczone: „Czarny” i „czarny” są "
                                         u"traktowane jako co innego.",
    ("prefix", "value"): u"Przykład: https://sklep.pl przed ścieżką zdjęcia.",
    ("suffix", "value"): u"Przykład:  - wysyłka w 24h  po nazwie produktu.",
    ("template", "template"): u"Nazwy kolumn w klamrach, reszta zwykłym tekstem. "
                              u"Przykład:  {nazwa} {kolor}, rozmiar {rozmiar}. Nazwa "
                              u"musi być dokładnie taka jak na liście kolumn.",
    ("fallback", "fields"): u"Kolumny sprawdzane po kolei, oddzielone przecinkami. "
                            u"Wygrywa pierwsza, która nie jest pusta.",
    ("fallback", "default"): u"Wpisywana, gdy wszystkie kolumny okażą się puste.",
    ("truncate", "length"): u"Maksymalna liczba znaków. Dla przykładu: tytuł w Google "
                            u"Shopping to 150 znaków, opis 5000.",
    ("truncate", "on_word"): u"Zaznaczone: tekst urwie się po ostatnim całym słowie, "
                             u"a nie w środku wyrazu.",
    ("truncate", "ellipsis"): u"Dopisek na końcu skróconego tekstu, np. …  Wlicza się "
                              u"do limitu znaków.",
    ("case", "style"): u"małe - wszystko małymi literami. WIELKIE - same wielkie. "
                       u"Każde Słowo - wielka litera w każdym wyrazie. Jak zdanie - "
                       u"wielka tylko na początku.",
    ("number", "multiply"): u"Mnożnik, np. 1.23 dla doliczenia 23% VAT. Puste pole - "
                            u"bez mnożenia.",
    ("number", "add"): u"Liczba dodawana po pomnożeniu, np. 15 za wysyłkę. Może być "
                       u"ujemna.",
    ("number", "decimals"): u"Ile cyfr po przecinku zostawić, zwykle 2. Puste pole - "
                            u"tyle, ile wyjdzie z obliczenia.",
    ("number", "decimal_separator"): u"Znak dziesiętny w wyniku: kropka dla feedów "
                                     u"i importerów, przecinek dla polskiego Excela.",
    ("date_format", "input_format"): u"Jak data wygląda w źródle. %Y rok, %m miesiąc, "
                                     u"%d dzień, %H:%M:%S godzina. Puste pole - "
                                     u"rozpoznanie automatyczne.",
    ("date_format", "output_format"): u"Jak ma wyglądać w wyniku. Przykład: %d.%m.%Y "
                                      u"da 28.08.2026.",
    ("pick", "index"): u"Numer liczony od 1. Przy trzech zdjęciach wpisanie 2 wybierze "
                       u"drugie.",
    ("pick", "separator"): u"Znak rozdzielający wartości w komórce. Puste pole oznacza "
                           u"nową linię - tak panel skleja wielokrotności.",
    ("join", "glue"): u"Wstawiany między łączone wartości, np. przecinek ze spacją.",
    ("join", "separator"): u"Po czym rozpoznać osobne wartości w źródle. Puste pole "
                           u"oznacza nową linię.",
}


class RulesTab(ttk.Frame):

    def __init__(self, master, state):
        ttk.Frame.__init__(self, master, padding=8)
        self.state = state
        self._build()
        self.refresh()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=2)

        rules_box = ttk.LabelFrame(self, text=u"Reguły", padding=6)
        rules_box.grid(row=0, column=0, sticky="nsew")
        rules_box.columnconfigure(0, weight=1)
        rules_box.rowconfigure(0, weight=1)

        self.rules_view = ttk.Treeview(rules_box, columns=("desc",), show="tree headings")
        self.rules_view.heading("#0", text=u"Aktywna")
        self.rules_view.heading("desc", text=u"Reguła")
        self.rules_view.column("#0", width=80, stretch=False)
        self.rules_view.column("desc", width=700)
        self.rules_view.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(rules_box, orient="vertical", command=self.rules_view.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.rules_view.configure(yscrollcommand=scroll.set)
        self.rules_view.bind("<Double-1>", lambda e: self.edit_rule())

        buttons = ttk.Frame(rules_box)
        buttons.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(buttons, text=u"Dodaj", command=self.add_rule).pack(side="left")
        ttk.Button(buttons, text=u"Edytuj", command=self.edit_rule).pack(side="left", padx=4)
        ttk.Button(buttons, text=u"Usuń", command=self.delete_rule).pack(side="left")
        ttk.Button(buttons, text=u"Włącz/wyłącz",
                   command=self.toggle_rule).pack(side="left", padx=4)
        ttk.Button(buttons, text=u"▲", width=4,
                   command=lambda: self.move_rule(-1)).pack(side="left", padx=(12, 2))
        ttk.Button(buttons, text=u"▼", width=4,
                   command=lambda: self.move_rule(1)).pack(side="left")

        filters_box = ttk.LabelFrame(self, text=u"Filtry rekordów", padding=6)
        filters_box.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        filters_box.columnconfigure(0, weight=1)
        filters_box.rowconfigure(0, weight=1)

        self.filters_view = ttk.Treeview(filters_box, columns=("desc",),
                                         show="tree headings")
        self.filters_view.heading("#0", text=u"Aktywny")
        self.filters_view.heading("desc", text=u"Filtr")
        self.filters_view.column("#0", width=80, stretch=False)
        self.filters_view.column("desc", width=700)
        self.filters_view.grid(row=0, column=0, sticky="nsew")
        filter_scroll = ttk.Scrollbar(filters_box, orient="vertical",
                                      command=self.filters_view.yview)
        filter_scroll.grid(row=0, column=1, sticky="ns")
        self.filters_view.configure(yscrollcommand=filter_scroll.set)
        self.filters_view.bind("<Double-1>", lambda e: self.edit_filter())

        filter_buttons = ttk.Frame(filters_box)
        filter_buttons.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(filter_buttons, text=u"Dodaj", command=self.add_filter).pack(side="left")
        ttk.Button(filter_buttons, text=u"Edytuj",
                   command=self.edit_filter).pack(side="left", padx=4)
        ttk.Button(filter_buttons, text=u"Usuń", command=self.delete_filter).pack(side="left")
        ttk.Button(filter_buttons, text=u"Włącz/wyłącz",
                   command=self.toggle_filter).pack(side="left", padx=4)

    # -- dane --------------------------------------------------------------

    @property
    def ruleset(self):
        return self.state.config.ruleset

    def column_names(self):
        """Kolumny w takiej pisowni, w jakiej trafią do pliku - reguła ma
        wskazywać to samo, co użytkownik zobaczy w wyniku."""
        config = self.state.config
        structure = config.structure
        names = [c.out for c in structure.columns] if structure else []
        if config.include_images:
            from core.expanders import ImageExpander
            names += ImageExpander(kind=config.image_kind, mode=config.image_mode,
                                   count=config.image_count,
                                   base_name=config.image_base_name,
                                   extra_name=config.image_extra_name).columns()
        if config.include_icons:
            from core.expanders import IconExpander
            names += IconExpander(kind=config.icon_kind,
                                  column_name=config.icon_column_name).columns()
        if config.include_params:
            from core.expanders import ParamExpander
            names += ParamExpander(mode=config.param_mode, names=config.param_names,
                                   max_pairs=config.param_max_pairs,
                                   other_column=config.param_other_column).columns()
        return [output_name(n, config.uppercase_names) for n in names]

    def refresh(self):
        self.rules_view.delete(*self.rules_view.get_children())
        for rule in self.ruleset.rules:
            self.rules_view.insert("", "end", text=u"tak" if rule.enabled else u"nie",
                                   values=(rule.describe(),))
        self.filters_view.delete(*self.filters_view.get_children())
        for record_filter in self.ruleset.filters:
            self.filters_view.insert("", "end",
                                     text=u"tak" if record_filter.enabled else u"nie",
                                     values=(record_filter.describe(),))

    # -- reguły ------------------------------------------------------------

    def add_rule(self):
        columns = self.column_names()
        if not columns:
            messagebox.showinfo(u"Reguły", u"Najpierw dodaj kolumny w zakładce Pola.",
                                parent=self)
            return
        dialog = RuleDialog(self, columns, None)
        self.wait_window(dialog)
        if dialog.result:
            self.ruleset.rules.append(dialog.result)
            self._changed()

    def edit_rule(self):
        index = self._selected(self.rules_view)
        if index is None:
            return
        dialog = RuleDialog(self, self.column_names(), self.ruleset.rules[index])
        self.wait_window(dialog)
        if dialog.result:
            self.ruleset.rules[index] = dialog.result
            self._changed()

    def delete_rule(self):
        index = self._selected(self.rules_view)
        if index is None:
            return
        del self.ruleset.rules[index]
        self._changed()

    def toggle_rule(self):
        index = self._selected(self.rules_view)
        if index is None:
            return
        rule = self.ruleset.rules[index]
        rule.enabled = not rule.enabled
        self._changed()

    def move_rule(self, delta):
        index = self._selected(self.rules_view)
        if index is None:
            return
        target = index + delta
        if target < 0 or target >= len(self.ruleset.rules):
            return
        rules = self.ruleset.rules
        rules[index], rules[target] = rules[target], rules[index]
        self._changed()
        children = self.rules_view.get_children()
        if target < len(children):
            self.rules_view.selection_set(children[target])

    # -- filtry ------------------------------------------------------------

    def add_filter(self):
        columns = self.column_names()
        if not columns:
            messagebox.showinfo(u"Filtry", u"Najpierw dodaj kolumny w zakładce Pola.",
                                parent=self)
            return
        dialog = FilterDialog(self, columns, None)
        self.wait_window(dialog)
        if dialog.result:
            self.ruleset.filters.append(dialog.result)
            self._changed()

    def edit_filter(self):
        index = self._selected(self.filters_view)
        if index is None:
            return
        dialog = FilterDialog(self, self.column_names(), self.ruleset.filters[index])
        self.wait_window(dialog)
        if dialog.result:
            self.ruleset.filters[index] = dialog.result
            self._changed()

    def delete_filter(self):
        index = self._selected(self.filters_view)
        if index is None:
            return
        del self.ruleset.filters[index]
        self._changed()

    def toggle_filter(self):
        index = self._selected(self.filters_view)
        if index is None:
            return
        record_filter = self.ruleset.filters[index]
        record_filter.enabled = not record_filter.enabled
        self._changed()

    # -- pomocnicze --------------------------------------------------------

    def _selected(self, view):
        selection = view.selection()
        if not selection:
            return None
        return view.index(selection[0])

    def _changed(self):
        self.refresh()
        self.state.notify(RULES_CHANGED)

    def on_event(self, event):
        if event in (FIELDS_CHANGED,):
            self.refresh()


class ConditionEditor(ttk.LabelFrame):
    """Lista warunków ze spójnikiem - wspólna dla reguł i filtrów."""

    def __init__(self, master, columns, group):
        ttk.LabelFrame.__init__(self, master, text=u"Warunek", padding=6)
        self.columns = columns
        self.group = group or ConditionGroup()
        self.rows = []

        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text=u"Łącz warunki:").pack(side="left")
        self.mode = tk.StringVar(value=self.group.mode)
        ttk.Radiobutton(top, text=u"wszystkie (ORAZ)", value="and",
                        variable=self.mode).pack(side="left", padx=4)
        ttk.Radiobutton(top, text=u"dowolny (LUB)", value="or",
                        variable=self.mode).pack(side="left")
        ttk.Button(top, text=u"Dodaj warunek",
                   command=self.add_row).pack(side="right")

        ttk.Label(self, wraplength=680, justify="left", foreground="#666666",
                  text=u"Warunek sprawdza wartość wybranej kolumny w tym samym "
                       u"wierszu - może to być inna kolumna niż ta, którą reguła "
                       u"zmienia. Bez warunku reguła zadziała na każdym wierszu."
                  ).pack(anchor="w", pady=(4, 0))

        self.body = ttk.Frame(self)
        self.body.pack(fill="both", expand=True, pady=(6, 0))

        for condition in self.group.conditions:
            self.add_row(condition)
        if not self.group.conditions:
            ttk.Label(self.body, text=u"Brak warunków - reguła zadziała zawsze.",
                      foreground="#666666").pack(anchor="w")

    def add_row(self, condition=None):
        for child in self.body.winfo_children():
            if isinstance(child, ttk.Label):
                child.destroy()
        row = ttk.Frame(self.body)
        row.pack(fill="x", pady=2)

        field = tk.StringVar(value=(condition.field if condition else
                                    (self.columns[0] if self.columns else u"")))
        operator = tk.StringVar(value=OPERATOR_LABELS.get(
            condition.op if condition else "not_empty"))
        value = tk.StringVar(value=(condition.value if condition else u""))

        ttk.Combobox(row, textvariable=field, values=self.columns, width=22,
                     state="readonly").pack(side="left")
        ttk.Combobox(row, textvariable=operator, width=20, state="readonly",
                     values=[label for _, label in OPERATORS]).pack(side="left", padx=4)
        ttk.Entry(row, textvariable=value, width=26).pack(side="left", fill="x", expand=True)
        entry = {"frame": row, "field": field, "op": operator, "value": value}
        ttk.Button(row, text=u"×", width=3,
                   command=lambda: self._remove(entry)).pack(side="left", padx=(4, 0))
        self.rows.append(entry)

    def _remove(self, entry):
        entry["frame"].destroy()
        if entry in self.rows:
            self.rows.remove(entry)

    def result(self):
        conditions = []
        reverse = dict((label, key) for key, label in OPERATORS)
        for row in self.rows:
            op = reverse.get(row["op"].get(), "not_empty")
            conditions.append(Condition(row["field"].get(), op, row["value"].get()))
        return ConditionGroup(self.mode.get(), conditions)


class RuleDialog(tk.Toplevel):

    def __init__(self, master, columns, rule):
        tk.Toplevel.__init__(self, master)
        self.title(u"Reguła")
        self.result = None
        self.columns = columns
        self.transient(master)
        self.grab_set()
        self._param_widgets = {}

        rule = rule or Rule(columns[0] if columns else u"", "set", {})

        head = ttk.Frame(self, padding=8)
        head.pack(fill="x")
        ttk.Label(head, text=u"Kolumna:").grid(row=0, column=0, sticky="w")
        self.field = tk.StringVar(value=rule.field)
        ttk.Combobox(head, textvariable=self.field, values=columns, width=28,
                     state="readonly").grid(row=0, column=1, sticky="w", padx=6)

        ttk.Label(head, text=u"Akcja:").grid(row=0, column=2, sticky="e", padx=(12, 0))
        self.action_label = tk.StringVar(value=ACTION_LABELS.get(rule.action, rule.action))
        action_combo = ttk.Combobox(head, textvariable=self.action_label, width=26,
                                    state="readonly",
                                    values=[label for _, label in ACTIONS])
        action_combo.grid(row=0, column=3, sticky="w", padx=6)
        action_combo.bind("<<ComboboxSelected>>", lambda e: self._rebuild_params())

        self.action_help = ttk.Label(self, text=u"", wraplength=700, justify="left",
                                     foreground="#444444")
        self.action_help.pack(fill="x", padx=8)

        self.params_box = ttk.LabelFrame(self, text=u"Ustawienia akcji", padding=8)
        self.params_box.pack(fill="x", padx=8, pady=4)

        self.conditions = ConditionEditor(self, columns, rule.condition)
        self.conditions.pack(fill="both", expand=True, padx=8, pady=4)

        buttons = ttk.Frame(self, padding=8)
        buttons.pack(fill="x")
        ttk.Button(buttons, text=u"Anuluj", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text=u"Zapisz", command=self._accept).pack(side="right", padx=4)

        self.minsize(760, 560)
        self._current_params = dict(rule.params)
        self._rebuild_params()

    def _action_key(self):
        reverse = dict((label, key) for key, label in ACTIONS)
        return reverse.get(self.action_label.get(), "set")

    def _rebuild_params(self):
        for child in self.params_box.winfo_children():
            child.destroy()
        self._param_widgets = {}
        action = self._action_key()
        self.action_help.configure(text=ACTION_HELP.get(action, u""))
        specs = ACTION_PARAMS.get(action, [])
        if not specs:
            return
        for key, label, kind in specs:
            row = ttk.Frame(self.params_box)
            row.pack(fill="x", pady=(2, 6))
            row.columnconfigure(1, weight=1)
            current = self._current_params.get(key)
            if kind == "bool":
                variable = tk.BooleanVar(value=bool(current) if current is not None else True)
                ttk.Checkbutton(row, text=label, variable=variable).grid(
                    row=0, column=0, columnspan=2, sticky="w")
                self._param_widgets[key] = ("bool", variable)
                self._add_help(row, action, key)
                continue
            # Etykieta zawija się zamiast znikać - opisy bywają dłuższe niż pole.
            ttk.Label(row, text=label, width=22, wraplength=160,
                      justify="left").grid(row=0, column=0, sticky="nw", padx=(0, 6))
            if kind == "map":
                text = tk.Text(row, height=6, width=40, wrap="word")
                if isinstance(current, dict):
                    text.insert("1.0", u"\n".join(u"%s=%s" % (k, v)
                                                  for k, v in current.items()))
                text.grid(row=0, column=1, sticky="ew")
                self._param_widgets[key] = ("map", text)
                self._add_help(row, action, key)
                continue
            if kind.startswith("choice:"):
                options = [p.split("=") for p in kind.split(":", 1)[1].split(",")]
                labels = [o[1] for o in options]
                variable = tk.StringVar()
                for value, text_label in options:
                    if value == current:
                        variable.set(text_label)
                if not variable.get():
                    variable.set(labels[0])
                ttk.Combobox(row, textvariable=variable, values=labels, width=22,
                             state="readonly").grid(row=0, column=1, sticky="w")
                self._param_widgets[key] = ("choice", (variable, options))
                self._add_help(row, action, key)
                continue
            variable = tk.StringVar(value=u"" if current is None else u"%s" % current)
            if kind == "list" and isinstance(current, list):
                variable.set(u", ".join(current))
            ttk.Entry(row, textvariable=variable).grid(row=0, column=1, sticky="ew")
            self._param_widgets[key] = (kind, variable)
            self._add_help(row, action, key)

    def _add_help(self, row, action, key):
        """Podpowiedź pod polem - to ona tłumaczy ustawienie osobie nietechnicznej."""
        text = PARAM_HELP.get((action, key))
        if not text:
            return
        ttk.Label(row, text=text, foreground="#666666", wraplength=500,
                  justify="left").grid(row=1, column=1, sticky="w", pady=(2, 0))

    def _collect_params(self):
        params = {}
        for key, (kind, widget) in self._param_widgets.items():
            if kind == "bool":
                params[key] = bool(widget.get())
            elif kind == "map":
                mapping = {}
                for line in widget.get("1.0", "end").splitlines():
                    if "=" in line:
                        left, right = line.split("=", 1)
                        if left.strip():
                            mapping[left.strip()] = right.strip()
                params[key] = mapping
            elif kind == "choice":
                variable, options = widget
                for value, label in options:
                    if label == variable.get():
                        params[key] = value
            elif kind == "list":
                params[key] = [p.strip() for p in widget.get().split(",") if p.strip()]
            elif kind == "int":
                try:
                    params[key] = int(widget.get() or 0)
                except ValueError:
                    params[key] = 0
            else:
                params[key] = widget.get()
        return params

    def _accept(self):
        if not self.field.get():
            messagebox.showwarning(u"Reguła", u"Wybierz kolumnę.", parent=self)
            return
        self.result = Rule(self.field.get(), self._action_key(), self._collect_params(),
                           self.conditions.result())
        self.destroy()


class FilterDialog(tk.Toplevel):

    def __init__(self, master, columns, record_filter):
        tk.Toplevel.__init__(self, master)
        self.title(u"Filtr rekordów")
        self.result = None
        self.transient(master)
        self.grab_set()

        record_filter = record_filter or RecordFilter()
        self.minsize(760, 340)

        head = ttk.Frame(self, padding=8)
        head.pack(fill="x")
        ttk.Label(head, text=u"Co zrobić, gdy warunek jest spełniony:").pack(side="left")
        self.mode = tk.StringVar(value=record_filter.mode)
        ttk.Radiobutton(head, text=u"pomiń wiersz", value="skip",
                        variable=self.mode).pack(side="left", padx=6)
        ttk.Radiobutton(head, text=u"zostaw tylko taki", value="keep",
                        variable=self.mode).pack(side="left")

        ttk.Label(self, padding=(8, 0), wraplength=700, justify="left",
                  foreground="#666666",
                  text=u"Filtr działa na całym wierszu: „pomiń wiersz” wyrzuca "
                       u"pasujące z wyniku (np. produkty bez stanu), „zostaw tylko "
                       u"taki” zostawia wyłącznie pasujące (np. jedną kategorię)."
                  ).pack(fill="x")

        self.conditions = ConditionEditor(self, columns, record_filter.condition)
        self.conditions.pack(fill="both", expand=True, padx=8, pady=4)

        buttons = ttk.Frame(self, padding=8)
        buttons.pack(fill="x")
        ttk.Button(buttons, text=u"Anuluj", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text=u"Zapisz", command=self._accept).pack(side="right", padx=4)

    def _accept(self):
        group = self.conditions.result()
        if not group.conditions:
            messagebox.showwarning(u"Filtr", u"Dodaj przynajmniej jeden warunek.",
                                   parent=self)
            return
        self.result = RecordFilter(group, self.mode.get())
        self.destroy()
