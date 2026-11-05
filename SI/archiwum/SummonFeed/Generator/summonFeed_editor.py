#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
summonFeed — edytor parametrów i struktur (GUI).

Kreator siedmiu kroków tworzący i aktualizujący pliki bazy summonFeed:
parametry, struktury oraz towarzyszące im zmienne i helpery wraz z wpisami
w rejestrach. Każde okno ma w prawym górnym rogu przyciski „Kontynuuj" i „Cofnij".

Cała logika zapisu siedzi w ``summonFeed_editor_model.EditorModel`` — ten plik
odpowiada wyłącznie za interfejs.

Uruchomienie:  python summonFeed_editor.py
"""

import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from summonFeed_editor_model import EditorModel
from summonFeed_gui import make_scrollable

BASE = Path(__file__).parent
ERROR_BG = "#ffd6d6"
OK_BG = "#ffffff"
GREY = "#8a8a8a"


def _text_widget(parent, height, width=None):
    frame = tk.Frame(parent)
    text = tk.Text(frame, height=height, wrap='word', undo=True,
                   **({'width': width} if width else {}))
    scroll = ttk.Scrollbar(frame, orient='vertical', command=text.yview)
    text.configure(yscrollcommand=scroll.set)
    text.pack(side='left', fill='both', expand=True)
    scroll.pack(side='right', fill='y')
    return frame, text


def _lines(text_widget):
    return [ln.strip() for ln in text_widget.get('1.0', 'end').splitlines() if ln.strip()]


def _csv(entry):
    return [p.strip() for p in entry.get().split(',') if p.strip()]


class EditorApp:
    """Okno kreatora. Stan trzymany w atrybutach, kroki rysowane od nowa."""

    def __init__(self):
        self.model = EditorModel(BASE)
        self.languages = self._load_languages()
        self.lang = 'pl' if 'pl' in self.languages else next(iter(self.languages), 'en')

        self.root = tk.Tk()
        self.root.title(self.t('app_title'))
        self.root.geometry("980x740")
        self.root.minsize(820, 600)
        self.container = tk.Frame(self.root)
        self.container.pack(fill='both', expand=True)
        self.current_frame = None
        self.continue_btn = None

        # --- stan kreatora ---
        self.kind = 'parameter'
        self.mode = 'new'
        self.picked_file = None
        self.loaded_form = None     # konfiguracja wczytana z pliku (tymczasowe domyślne)
        self.form = None            # wartości zebrane z formularza
        self.plan = None
        self.save_report = None

        self.show_language()

    # ------------------------------------------------------------------
    #  TŁUMACZENIA
    # ------------------------------------------------------------------

    def _load_languages(self):
        langs = {}
        for path in sorted((BASE / "lang").glob("editor_*.json")):
            code = path.stem.replace('editor_', '')
            try:
                langs[code] = json.loads(path.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, OSError):
                continue
        return langs

    def t(self, key, **kw):
        """Tekst w wybranym języku; brak klucza → angielski, dalej → sama nazwa klucza."""
        text = self.languages.get(self.lang, {}).get(key)
        if text is None:
            text = self.languages.get('en', {}).get(key, key)
        try:
            return text.format(**kw) if kw else text
        except (KeyError, IndexError):
            return text

    # ------------------------------------------------------------------
    #  SZKIELET KROKU
    # ------------------------------------------------------------------

    def _new_step(self, title, on_continue, on_back,
                  back_enabled=True, continue_enabled=True, continue_text=None):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.root.unbind_all('<MouseWheel>')

        frame = tk.Frame(self.container)
        frame.pack(fill='both', expand=True)
        self.current_frame = frame

        top = tk.Frame(frame)
        top.pack(fill='x', padx=14, pady=(12, 6))
        tk.Label(top, text=title, font=('Segoe UI', 15, 'bold')).pack(side='left')

        self.continue_btn = ttk.Button(top, text=continue_text or self.t('btn_continue'),
                                       command=on_continue)
        self.continue_btn.pack(side='right', padx=(8, 0))
        if not continue_enabled:
            self.continue_btn.state(['disabled'])
        back = ttk.Button(top, text=self.t('btn_back'), command=on_back)
        back.pack(side='right')
        if not back_enabled:
            back.state(['disabled'])

        ttk.Separator(frame, orient='horizontal').pack(fill='x', padx=14)
        body = tk.Frame(frame)
        body.pack(fill='both', expand=True, padx=14, pady=10)
        return body

    def _quit(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()

    # ------------------------------------------------------------------
    #  KROK 1 — JĘZYK
    # ------------------------------------------------------------------

    def show_language(self):
        body = self._new_step(self.t('step_lang'),
                              on_continue=self._language_continue,
                              on_back=self._quit)
        tk.Label(body, text=self.t('lang_hint'), wraplength=820,
                 justify='left').pack(anchor='w', pady=(0, 10))

        self._lang_var = tk.StringVar(value=self.lang)
        for code, data in self.languages.items():
            ttk.Radiobutton(body, text=data.get('_name', code),
                            variable=self._lang_var, value=code).pack(anchor='w', pady=2)

    def _language_continue(self):
        self.lang = self._lang_var.get()
        self.root.title(self.t('app_title'))
        self.show_scope()

    # ------------------------------------------------------------------
    #  KROK 2 — ZAKRES OPERACJI
    # ------------------------------------------------------------------

    def show_scope(self):
        body = self._new_step(self.t('step_scope'),
                              on_continue=self._scope_continue,
                              on_back=self.show_language)
        tk.Label(body, text=self.t('scope_hint'), wraplength=820,
                 justify='left').pack(anchor='w', pady=(0, 10))

        tk.Label(body, text=self.t('scope_kind'),
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(4, 2))
        self._kind_var = tk.StringVar(value=self.kind)
        for value, key in (('parameter', 'kind_parameter'), ('structure', 'kind_structure')):
            ttk.Radiobutton(body, text=self.t(key), variable=self._kind_var,
                            value=value, command=self._scope_recheck).pack(anchor='w', padx=12)

        ttk.Separator(body, orient='horizontal').pack(fill='x', pady=10)

        tk.Label(body, text=self.t('scope_mode'),
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        self._mode_var = tk.StringVar(value=self.mode)
        for value, key in (('new', 'mode_new'), ('update', 'mode_update'), ('quit', 'mode_quit')):
            ttk.Radiobutton(body, text=self.t(key), variable=self._mode_var,
                            value=value, command=self._scope_recheck).pack(anchor='w', padx=12)

        picker = tk.Frame(body)
        picker.pack(fill='x', padx=12, pady=(6, 0))
        ttk.Button(picker, text=self.t('btn_browse'),
                   command=self._pick_file).pack(side='left')
        self._file_label = tk.Label(picker, text=self.t('no_file'), fg=GREY)
        self._file_label.pack(side='left', padx=10)

        self._scope_msg = tk.Label(body, text="", fg="#c00000", wraplength=820, justify='left')
        self._scope_msg.pack(anchor='w', pady=(10, 0))
        self._scope_recheck()

    def _pick_file(self):
        path = filedialog.askopenfilename(
            title=self.t('mode_update'),
            initialdir=str(self.model.target_dir(self._kind_var.get())),
            filetypes=[("JSON", "*.json")])
        if not path:
            return
        self.picked_file = Path(path)
        self._file_label.config(text=self.t('picked_file', path=self.picked_file.name), fg="#000000")
        self._mode_var.set('update')
        self._scope_recheck()

    def _scope_recheck(self):
        """Sprawdź zgodność wskazanego pliku z wybranym typem; wynik steruje 'Kontynuuj'."""
        mode = self._mode_var.get()
        if mode != 'update':
            self._scope_msg.config(text="")
            self.continue_btn.state(['!disabled'])
            return

        if not self.picked_file:
            self._scope_msg.config(text=self.t('must_pick_file'))
            self.continue_btn.state(['disabled'])
            return

        found = self.model.detect_kind(self.picked_file)
        expected = self._kind_var.get()
        if found is None:
            self._scope_msg.config(text=self.t('kind_unknown'))
            self.continue_btn.state(['disabled'])
        elif found != expected:
            self._scope_msg.config(text=self.t(
                'kind_mismatch',
                found=self.t('kind_structure' if found == 'structure' else 'kind_parameter'),
                expected=self.t('kind_structure' if expected == 'structure' else 'kind_parameter')))
            self.continue_btn.state(['disabled'])
        else:
            self._scope_msg.config(text="")
            self.continue_btn.state(['!disabled'])

    def _scope_continue(self):
        self.kind = self._kind_var.get()
        self.mode = self._mode_var.get()
        if self.mode == 'quit':
            self._quit()
            return
        if self.mode == 'update':
            try:
                self.loaded_form = self.model.load_form(self.picked_file)
            except (OSError, ValueError) as exc:
                messagebox.showerror(self.t('step_scope'), self.t('load_failed', error=exc))
                return
        else:
            self.loaded_form = None
        self.form = None
        self.show_form()

    # ------------------------------------------------------------------
    #  KROK 3 — FORMULARZ
    # ------------------------------------------------------------------

    def _initial(self, key, fallback=''):
        """Wartość startowa pola: z formularza (powrót), z wczytanego pliku, albo domyślna."""
        for source in (self.form, self.loaded_form):
            if source and key in source and source[key] not in (None, ''):
                return source[key]
        return fallback

    def show_form(self):
        is_struct = self.kind == 'structure'
        body = self._new_step(self.t('step_form_struct' if is_struct else 'step_form_param'),
                              on_continue=self._form_continue,
                              on_back=self.show_scope)
        inner = make_scrollable(body)
        self._widgets = {}

        # --- name z walidacją na żywo ---
        tk.Label(inner, text=self.t('field_name'),
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        self._name_entry = tk.Entry(inner)
        self._name_entry.insert(0, self._initial('name'))
        self._name_entry.pack(fill='x', pady=(0, 2))
        self._name_msg = tk.Label(inner, text="", fg="#c00000", anchor='w')
        self._name_msg.pack(fill='x', pady=(0, 8))
        self._name_entry.bind('<KeyRelease>', lambda e: self._check_name())

        self._field(inner, 'field_description', 'description')
        self._field(inner, 'field_description_pl', 'description_pl')

        if is_struct:
            self._field(inner, 'field_output', 'output', fallback='rss/channel/item')
            self._build_structure_extras(inner)
        else:
            self._field(inner, 'field_output', 'output',
                        fallback=self._initial('name'))
            self._build_parameter_extras(inner)

        self._check_name()

    def _field(self, parent, label_key, name, fallback='', width=None):
        tk.Label(parent, text=self.t(label_key)).pack(anchor='w')
        entry = tk.Entry(parent, **({'width': width} if width else {}))
        entry.insert(0, self._initial(name, fallback))
        entry.pack(fill='x', pady=(0, 8))
        self._widgets[name] = entry
        return entry

    def _text_field(self, parent, label_key, name, height=8, fallback=''):
        tk.Label(parent, text=self.t(label_key)).pack(anchor='w')
        frame, text = _text_widget(parent, height)
        value = self._initial(name, fallback)
        if isinstance(value, list):
            value = "\n".join(value)
        text.insert('1.0', value)
        frame.pack(fill='both', expand=True, pady=(0, 8))
        self._widgets[name] = text
        return text

    def _check_name(self):
        """Waliduj nazwę na żywo: puste/niepoprawne/zajęte → czerwone pole i blokada."""
        name = self._name_entry.get().strip()
        original = (self.loaded_form or {}).get('original_name')
        problem = self.model.validate_name(name)
        conflict = None if problem else self.model.name_conflict(self.kind, name, original)

        if problem:
            self._name_entry.config(bg=ERROR_BG)
            self._name_msg.config(text=self.t(problem))
            self.continue_btn.state(['disabled'])
        elif conflict:
            self._name_entry.config(bg=ERROR_BG)
            self._name_msg.config(text=self.t('name_taken', path=conflict.name))
            self.continue_btn.state(['disabled'])
        else:
            self._name_entry.config(bg=OK_BG)
            self._name_msg.config(text="")
            self.continue_btn.state(['!disabled'])

    # --- pola specyficzne dla struktury ---------------------------------

    def _build_structure_extras(self, parent):
        self._text_field(parent, 'field_notes', 'notes', height=3)
        self._text_field(parent, 'field_xsl_struct', 'xsl', height=16)

    # --- pola specyficzne dla parametru ---------------------------------

    def _build_parameter_extras(self, parent):
        structures = self.model.list_structures()

        tk.Label(parent, text=self.t('field_structure'),
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(4, 2))
        chosen = self._initial('structure', [])
        self._struct_vars = {}
        row = tk.Frame(parent)
        row.pack(fill='x', padx=12)
        for name in structures:
            var = tk.BooleanVar(value=name in chosen)
            self._struct_vars[name] = var
            ttk.Checkbutton(row, text=name, variable=var,
                            command=self._refresh_exclusive_defaults).pack(side='left', padx=(0, 14))

        tk.Label(parent, text=self.t('field_context'),
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(10, 2))
        self._context_var = tk.StringVar(value=self._initial('context', 'product'))
        ctx_row = tk.Frame(parent)
        ctx_row.pack(fill='x', padx=12, pady=(0, 8))
        for ctx in self.model.list_contexts():
            ttk.Radiobutton(ctx_row, text=ctx, variable=self._context_var,
                            value=ctx).pack(side='left', padx=(0, 14))

        # --- exclusiveGroup + exclusiveDefaultFor ---
        tk.Label(parent, text=self.t('field_exclusive_group')).pack(anchor='w')
        groups = [''] + self.model.list_exclusive_groups()
        self._group_var = tk.StringVar(value=self._initial('exclusiveGroup', ''))
        self._group_box = ttk.Combobox(parent, textvariable=self._group_var, values=groups)
        self._group_box.pack(fill='x', pady=(0, 6))
        self._group_var.trace_add('write', lambda *a: self._refresh_exclusive_defaults())

        tk.Label(parent, text=self.t('field_exclusive_default')).pack(anchor='w')
        self._excl_area = tk.Frame(parent)
        self._excl_area.pack(fill='x', padx=12, pady=(0, 8))
        self._excl_vars = {}
        self._refresh_exclusive_defaults()

        self._text_field(parent, 'field_xpath', 'xpathCandidates', height=3)
        self._text_field(parent, 'field_param_contexts', 'parameterContexts', height=2)

        # --- configVars ---
        tk.Label(parent, text=self.t('field_configvars'),
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(6, 2))
        self._cfg_area = tk.Frame(parent)
        self._cfg_area.pack(fill='x')
        self._cfg_rows = []
        for row_data in self._initial('configVars', []):
            self._add_config_row(row_data)
        self._add_config_row()

        # --- globals ---
        tk.Label(parent, text=self.t('field_globals'),
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(10, 2))
        self._globals_on = tk.BooleanVar(value=bool(self._initial('globals', [])))
        ttk.Checkbutton(parent, text=self.t('field_globals'), variable=self._globals_on,
                        command=self._toggle_globals).pack(anchor='w', padx=12)
        self._globals_area = tk.Frame(parent)
        self._globals_area.pack(fill='x', padx=24)
        self._global_vars = {}
        self._toggle_globals()

        # --- helpers ---
        tk.Label(parent, text=self.t('field_helpers'),
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(10, 2))
        self._helper_area = tk.Frame(parent)
        self._helper_area.pack(fill='x')
        self._helper_rows = []
        for row_data in self._initial('helpers', []):
            self._add_helper_row(row_data)
        self._add_helper_row()

        self._text_field(parent, 'field_notes', 'notes', height=3)
        self._text_field(parent, 'field_xsl_param', 'xsl', height=14)

    def _refresh_exclusive_defaults(self):
        """Lista struktur do 'exclusiveDefaultFor' — tylko te zaznaczone w 'structure'."""
        if not hasattr(self, '_excl_area'):
            return
        previous = {n: v.get() for n, v in self._excl_vars.items()}
        for child in self._excl_area.winfo_children():
            child.destroy()
        self._excl_vars = {}

        if not self._group_var.get().strip():
            tk.Label(self._excl_area, text="—", fg=GREY).pack(anchor='w')
            return

        preset = previous or {n: True for n in self._initial('exclusiveDefaultFor', [])}
        for name, var in self._struct_vars.items():
            if not var.get():
                continue
            chosen = tk.BooleanVar(value=bool(preset.get(name, False)))
            self._excl_vars[name] = chosen
            ttk.Checkbutton(self._excl_area, text=name, variable=chosen).pack(side='left', padx=(0, 14))

    def _toggle_globals(self):
        for child in self._globals_area.winfo_children():
            child.destroy()
        if not self._globals_on.get():
            self._global_vars = {}
            return
        chosen = self._initial('globals', [])
        self._global_vars = {}
        for name in self.model.list_global_variables():
            var = tk.BooleanVar(value=name in chosen)
            self._global_vars[name] = var
            ttk.Checkbutton(self._globals_area, text=name, variable=var).pack(anchor='w')

    # --- dorastające zestawy configVars ---------------------------------

    def _add_config_row(self, data=None):
        data = data or {}
        box = tk.LabelFrame(self._cfg_area, text=f"#{len(self._cfg_rows) + 1}", padx=8, pady=6)
        box.pack(fill='x', pady=4)

        head = tk.Frame(box)
        head.pack(fill='x')
        widgets = {}
        for key, label_key, width in (('name', 'cfg_name', 22),
                                      ('default', 'cfg_default', 22),
                                      ('delimeter', 'cfg_delimeter', 8)):
            cell = tk.Frame(head)
            cell.pack(side='left', padx=(0, 10))
            tk.Label(cell, text=self.t(label_key)).pack(anchor='w')
            entry = tk.Entry(cell, width=width)
            entry.insert(0, data.get(key, ''))
            entry.pack()
            widgets[key] = entry

        extract = tk.BooleanVar(value=bool(data.get('extract')))
        widgets['extract'] = extract
        extra = tk.Frame(box)
        ttk.Checkbutton(head, text=self.t('cfg_extract'), variable=extract,
                        command=lambda: self._toggle_extract(extra, extract)).pack(side='left',
                                                                                   pady=(14, 0))

        scope = tk.StringVar(value=data.get('scope', 'local'))
        widgets['scope'] = scope
        scope_row = tk.Frame(extra)
        scope_row.pack(fill='x', pady=(6, 2))
        tk.Label(scope_row, text=self.t('cfg_scope')).pack(side='left', padx=(0, 8))
        ttk.Radiobutton(scope_row, text=self.t('cfg_scope_global'), variable=scope,
                        value='global').pack(side='left', padx=(0, 10))
        ttk.Radiobutton(scope_row, text=self.t('cfg_scope_local'), variable=scope,
                        value='local').pack(side='left')

        meta_row = tk.Frame(extra)
        meta_row.pack(fill='x', pady=2)
        for key, label_key, width in (('order', 'cfg_order', 8), ('uses', 'cfg_uses', 40)):
            cell = tk.Frame(meta_row)
            cell.pack(side='left', padx=(0, 10))
            tk.Label(cell, text=self.t(label_key)).pack(anchor='w')
            entry = tk.Entry(cell, width=width)
            value = data.get(key, '')
            entry.insert(0, ", ".join(value) if isinstance(value, list) else str(value))
            entry.pack()
            widgets[key] = entry

        tk.Label(extra, text=self.t('cfg_xsl')).pack(anchor='w', pady=(4, 0))
        frame, text = _text_widget(extra, 4)
        text.insert('1.0', data.get('xsl', ''))
        frame.pack(fill='x')
        widgets['xsl'] = text

        self._cfg_rows.append(widgets)
        self._toggle_extract(extra, extract)
        widgets['name'].bind('<KeyRelease>', lambda e: self._ensure_trailing_config_row())

    @staticmethod
    def _toggle_extract(extra_frame, var):
        if var.get():
            extra_frame.pack(fill='x', pady=(4, 0))
        else:
            extra_frame.pack_forget()

    def _ensure_trailing_config_row(self):
        """Po wypełnieniu ostatniego 'name' dołóż kolejny pusty zestaw."""
        if self._cfg_rows and self._cfg_rows[-1]['name'].get().strip():
            self._add_config_row()

    # --- dorastające zestawy helperów -----------------------------------

    def _add_helper_row(self, data=None):
        data = data or {}
        box = tk.LabelFrame(self._helper_area, text=f"#{len(self._helper_rows) + 1}",
                            padx=8, pady=6)
        box.pack(fill='x', pady=4)
        widgets = {}

        head = tk.Frame(box)
        head.pack(fill='x')
        for key, label_key, width in (('name', 'helper_name', 24),
                                      ('uses', 'helper_uses', 30),
                                      ('globals', 'helper_globals', 30)):
            cell = tk.Frame(head)
            cell.pack(side='left', padx=(0, 10))
            tk.Label(cell, text=self.t(label_key)).pack(anchor='w')
            entry = tk.Entry(cell, width=width)
            value = data.get(key, '')
            entry.insert(0, ", ".join(value) if isinstance(value, list) else str(value))
            entry.pack()
            widgets[key] = entry

        tk.Label(box, text=self.t('helper_xsl')).pack(anchor='w', pady=(4, 0))
        frame, text = _text_widget(box, 5)
        text.insert('1.0', data.get('xsl', ''))
        frame.pack(fill='x')
        widgets['xsl'] = text

        self._helper_rows.append(widgets)
        widgets['name'].bind('<KeyRelease>', lambda e: self._ensure_trailing_helper_row())

    def _ensure_trailing_helper_row(self):
        if self._helper_rows and self._helper_rows[-1]['name'].get().strip():
            self._add_helper_row()

    # --- zebranie formularza --------------------------------------------

    def _collect_form(self):
        form = {
            'kind': self.kind,
            'original_name': (self.loaded_form or {}).get('original_name'),
            'name': self._name_entry.get().strip(),
            'description': self._widgets['description'].get().strip(),
            'description_pl': self._widgets['description_pl'].get().strip(),
            'output': self._widgets['output'].get().strip(),
            'notes': self._widgets['notes'].get('1.0', 'end').strip(),
            'xsl': self._widgets['xsl'].get('1.0', 'end').rstrip() + "\n",
        }
        if self.kind == 'structure':
            return form

        form.update({
            'structure': [n for n, v in self._struct_vars.items() if v.get()],
            'context': self._context_var.get(),
            # zmienne deklarowane wprost w .xsl (parametr legacy) — nieedytowalne tutaj,
            # ale muszą przetrwać zapis, bo bez nich JSON straciłby createVars
            'inlineCreateVars': list(self._initial('inlineCreateVars', [])),
            'exclusiveGroup': self._group_var.get().strip(),
            'exclusiveDefaultFor': [n for n, v in self._excl_vars.items() if v.get()],
            'xpathCandidates': _lines(self._widgets['xpathCandidates']),
            'parameterContexts': _lines(self._widgets['parameterContexts']),
            'globals': [n for n, v in self._global_vars.items() if v.get()],
            'configVars': [{
                'name': w['name'].get().strip(),
                'default': w['default'].get(),
                'delimeter': w['delimeter'].get(),
                'extract': w['extract'].get(),
                'scope': w['scope'].get(),
                'order': w['order'].get().strip(),
                'uses': _csv(w['uses']),
                'xsl': w['xsl'].get('1.0', 'end').strip(),
            } for w in self._cfg_rows if w['name'].get().strip()],
            'helpers': [{
                'name': w['name'].get().strip(),
                'uses': _csv(w['uses']),
                'globals': _csv(w['globals']),
                'xsl': w['xsl'].get('1.0', 'end').strip(),
            } for w in self._helper_rows if w['name'].get().strip()],
        })
        return form

    def _form_continue(self):
        form = self._collect_form()
        if self.kind == 'parameter' and not form['structure']:
            messagebox.showwarning(self.t('step_form_param'), self.t('structure_required'))
            return
        if not form['xsl'].strip():
            messagebox.showwarning(self.t('step_form_param'), self.t('xsl_required'))
            return
        self.form = form
        self.plan = self.model.plan_writes(form)
        self.show_decisions()

    # ------------------------------------------------------------------
    #  KROK 4 — DECYZJE
    # ------------------------------------------------------------------

    def show_decisions(self):
        body = self._new_step(self.t('step_decisions'),
                              on_continue=self._decisions_continue,
                              on_back=self.show_form)
        inner = make_scrollable(body)

        if self.plan.warnings:
            tk.Label(inner, text=self.t('warn_header'),
                     font=('Segoe UI', 10, 'bold'), fg="#b06000").pack(anchor='w')
            for key, params in self.plan.warnings:
                tk.Label(inner, text="• " + self.t(key, **params), fg="#b06000",
                         wraplength=880, justify='left').pack(anchor='w', padx=12, pady=2)
            ttk.Separator(inner, orient='horizontal').pack(fill='x', pady=8)

        conflicts = self.plan.conflicts
        if not conflicts:
            tk.Label(inner, text=self.t('decisions_none')).pack(anchor='w', pady=6)
            return

        tk.Label(inner, text=self.t('decisions_hint'), wraplength=880,
                 justify='left').pack(anchor='w', pady=(0, 8))
        self._decision_vars = {}
        for write in conflicts:
            box = tk.LabelFrame(inner, text=write.label, padx=8, pady=6)
            box.pack(fill='x', pady=6)

            choice = tk.StringVar(value='overwrite')
            self._decision_vars[write.label] = choice
            ttk.Radiobutton(box, text=self.t('decision_overwrite'), variable=choice,
                            value='overwrite').pack(anchor='w')
            ttk.Radiobutton(box, text=self.t('decision_keep'), variable=choice,
                            value='keep').pack(anchor='w')

            compare = tk.Frame(box)
            compare.pack(fill='both', expand=True, pady=(6, 0))
            for label_key, content in (('existing_content', write.existing or ''),
                                       ('new_content', write.content)):
                col = tk.Frame(compare)
                col.pack(side='left', fill='both', expand=True, padx=4)
                tk.Label(col, text=self.t(label_key), fg=GREY).pack(anchor='w')
                frame, text = _text_widget(col, 10)
                text.insert('1.0', content)
                text.config(state='disabled')
                frame.pack(fill='both', expand=True)

    def _decisions_continue(self):
        for write in self.plan.conflicts:
            var = getattr(self, '_decision_vars', {}).get(write.label)
            write.overwrite = (var.get() == 'overwrite') if var else True
        self.show_save()

    # ------------------------------------------------------------------
    #  KROK 5 — KOPIA ZAPASOWA I ZAPIS
    # ------------------------------------------------------------------

    def show_save(self):
        body = self._new_step(self.t('step_save'),
                              on_continue=self._do_save,
                              on_back=self.show_decisions)
        inner = make_scrollable(body)

        to_apply = self.plan.to_apply()
        skipped = [w for w in self.plan.writes if w not in to_apply]

        tk.Label(inner, text=self.t('save_plan'),
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        if to_apply:
            for write in to_apply:
                tk.Label(inner, text=f"• {write.label}").pack(anchor='w', padx=12)
        else:
            tk.Label(inner, text=self.t('save_nothing'), fg=GREY).pack(anchor='w', padx=12)

        if skipped:
            tk.Label(inner, text=self.t('save_skipped'),
                     font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(10, 0))
            for write in skipped:
                tk.Label(inner, text=f"• {write.label}", fg=GREY).pack(anchor='w', padx=12)

    def _do_save(self):
        try:
            saved, backup = self.model.apply(self.plan)
        except OSError as exc:
            messagebox.showerror(self.t('step_save'), self.t('save_failed', error=exc))
            return
        self.save_report = (saved, backup)
        self.show_validate()

    # ------------------------------------------------------------------
    #  KROK 6 — WALIDACJA
    # ------------------------------------------------------------------

    def show_validate(self):
        body = self._new_step(self.t('step_validate'),
                              on_continue=self.show_next,
                              on_back=self.show_form)
        saved, backup = self.save_report or ([], None)

        tk.Label(body, text=self.t('save_done', count=len(saved)),
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        if backup:
            tk.Label(body, text=self.t('save_backup', path=str(backup)),
                     fg=GREY).pack(anchor='w', pady=(0, 8))

        code, output = self.model.run_validator()
        summary = (self.t('validate_exit_ok') if code == 0
                   else self.t('validate_exit_err', code=code))
        tk.Label(body, text=summary, fg=("#006000" if code == 0 else "#c00000"),
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(6, 4))

        frame, text = _text_widget(body, 20)
        text.insert('1.0', output)
        text.config(state='disabled')
        frame.pack(fill='both', expand=True)

    # ------------------------------------------------------------------
    #  KROK 7 — CO DALEJ
    # ------------------------------------------------------------------

    def show_next(self):
        body = self._new_step(self.t('step_next'),
                              on_continue=self._next_continue,
                              on_back=self.show_validate)
        tk.Label(body, text=self.t('next_hint'), wraplength=820,
                 justify='left').pack(anchor='w', pady=(0, 10))
        self._next_var = tk.StringVar(value='continue')
        for value, key in (('continue', 'next_continue'), ('quit', 'next_quit')):
            ttk.Radiobutton(body, text=self.t(key), variable=self._next_var,
                            value=value).pack(anchor='w', padx=12, pady=2)

    def _next_continue(self):
        if self._next_var.get() == 'quit':
            self._quit()
            return
        self.loaded_form = None
        self.form = None
        self.plan = None
        self.save_report = None
        self.picked_file = None
        self.show_scope()


def main():
    EditorApp().run()


if __name__ == '__main__':
    main()
