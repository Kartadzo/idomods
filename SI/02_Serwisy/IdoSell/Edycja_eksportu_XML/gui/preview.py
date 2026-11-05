# -*- coding: utf-8 -*-
"""Podgląd wyniku - kilkanaście pierwszych wierszy, odświeżane na żądanie.

Czytanie przerywa się zaraz po zebraniu próbki, więc podgląd jest tak samo
szybki przy pliku z czterema produktami, jak przy pliku z setką tysięcy.
"""

import tkinter as tk
from tkinter import ttk

from core.pipeline import Pipeline
from .state import FIELDS_CHANGED, OUTPUT_CHANGED, RULES_CHANGED, SOURCE_CHANGED
from .worker import BackgroundTask


class PreviewPanel(ttk.Frame):

    def __init__(self, master, state):
        ttk.Frame.__init__(self, master, padding=(8, 4))
        self.state = state
        self._busy = False
        self._stale = True
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, sticky="ew")
        ttk.Label(bar, text=u"Podgląd wyniku").pack(side="left")
        self.refresh_button = ttk.Button(bar, text=u"Odśwież", command=self.refresh)
        self.refresh_button.pack(side="left", padx=8)
        self.auto = tk.BooleanVar(value=True)
        ttk.Checkbutton(bar, text=u"odświeżaj automatycznie",
                        variable=self.auto).pack(side="left")
        ttk.Label(bar, text=u"wierszy:").pack(side="left", padx=(12, 2))
        self.rows_var = tk.StringVar(value=u"%d" % self.state.settings.get("preview_rows", 20))
        ttk.Spinbox(bar, from_=5, to=200, width=5,
                    textvariable=self.rows_var).pack(side="left")
        self.status = ttk.Label(bar, text=u"", foreground="#666666")
        self.status.pack(side="right")

        holder = ttk.Frame(self)
        holder.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        holder.columnconfigure(0, weight=1)
        holder.rowconfigure(0, weight=1)
        self.table = ttk.Treeview(holder, show="headings", height=8)
        self.table.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(holder, orient="vertical", command=self.table.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(holder, orient="horizontal", command=self.table.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.table.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)

    # -- odświeżanie -------------------------------------------------------

    def refresh(self):
        config = self.state.config
        if self._busy or not config.source_path or not config.structure:
            return
        if config.structure.mode == "tree":
            self._show_message(u"Przycięty IOF zachowuje oryginalne drzewo - "
                               u"podgląd tabelaryczny nie ma tu zastosowania.")
            return
        try:
            limit = max(1, int(self.rows_var.get() or 20))
        except ValueError:
            limit = 20
        self.state.settings["preview_rows"] = limit

        self._busy = True
        self.refresh_button.configure(state="disabled")
        self.status.configure(text=u"czytam…")

        pipeline = Pipeline(config, self.state.registry)
        columns = pipeline.columns()

        def work(emit, cancelled):
            return list(pipeline.iter_rows(limit=limit))

        BackgroundTask(self, work,
                       on_done=lambda rows: self._show(columns, rows),
                       on_error=self._failed).start()

    def _failed(self, error):
        self._busy = False
        self.refresh_button.configure(state="normal")
        self._show_message(u"Nie udało się zbudować podglądu: %s" % error)

    def _show(self, columns, rows):
        self._busy = False
        self._stale = False
        self.refresh_button.configure(state="normal")
        self.table.delete(*self.table.get_children())
        self.table.configure(columns=columns)
        for name in columns:
            self.table.heading(name, text=name)
            self.table.column(name, width=max(90, min(260, 9 * len(name) + 60)),
                              stretch=False)
        for row in rows:
            values = []
            for name in columns:
                value = row.get(name, u"")
                if isinstance(value, list):
                    value = u", ".join([v for v in value if v])
                value = (u"%s" % value).replace(u"\n", u" ⏎ ")
                values.append(value[:200])
            self.table.insert("", "end", values=values)
        self.status.configure(text=u"%d wierszy, %d kolumn" % (len(rows), len(columns)))

    def _show_message(self, text):
        self._busy = False
        self.refresh_button.configure(state="normal")
        self.table.delete(*self.table.get_children())
        self.table.configure(columns=("info",))
        self.table.heading("info", text=u"Podgląd")
        self.table.column("info", width=900, stretch=True)
        self.table.insert("", "end", values=(text,))
        self.status.configure(text=u"")

    def on_event(self, event):
        if event in (SOURCE_CHANGED, FIELDS_CHANGED, RULES_CHANGED, OUTPUT_CHANGED):
            self._stale = True
            if self.auto.get():
                # Zbieramy serie zdarzeń w jedno odświeżenie.
                self.after_idle(self._maybe_refresh)

    def _maybe_refresh(self):
        if self._stale and not self._busy:
            self.refresh()
