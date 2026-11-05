#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SummonFeed XSLT Generator — graficzny kreator (tkinter).

Nakładka GUI na istniejący silnik ``SummonFeedGenerator`` z ``summonFeed_generator.py``.
Nie duplikuje logiki składania XSLT — reużywa jej, a tylko wymienia sposób pobierania
danych od użytkownika (okna zamiast pytań w terminalu).

Przepływ okien (każde ma w prawym górnym rogu przyciski „Kontynuuj” i „Cofnij”):
  1. wybór języka          6. generowanie skryptu (przy przejściu z kroku 5)
  2. krok pośredni         7. zapis konfiguracji do pliku
  3. wczytanie konfiguracji 8. powrót do kroku 3
  4. wybór struktury + parametrów
  5. konfiguracja wybranych parametrów (nazwa / wartości / przełącznik)

Uruchomienie:  python summonFeed_gui.py
"""

import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime

from summonFeed_generator import SummonFeedGenerator


# =============================================================================
#  SILNIK Z KONFIGURACJĄ Z GUI
# =============================================================================

class GuiGenerator(SummonFeedGenerator):
    """Silnik generatora, który wartości ``configVars`` pobiera z zebranych w GUI
    danych zamiast z ``input()``. Wartości wstawiamy do ``_gui_config_values``
    przed wywołaniem ``_build_xslt_structure()``."""

    def __init__(self):
        super().__init__()
        self._gui_config_values = {}

    def _ask_single_config_var(self, var):
        name = var['name']
        return self._gui_config_values.get(name, var.get('default', ''))

    def _ask_for_config_vars(self, config_vars):
        # bez wypisywania nagłówka na stdout — wszystko obsługuje GUI
        return {v['name']: self._ask_single_config_var(v) for v in config_vars}


# =============================================================================
#  POMOCNICZE — PLACEHOLDERY I PRZEWIJANIE
# =============================================================================

GREY = "#8a8a8a"
BLACK = "#000000"


def _entry_show_placeholder(entry, placeholder):
    entry.delete(0, 'end')
    entry.insert(0, placeholder)
    entry.config(fg=GREY)
    entry._is_ph = True


def add_entry_placeholder(entry, placeholder, value=""):
    """Jednoliniowe pole z wyszarzonym placeholderem. ``value`` = wstępne wypełnienie."""
    entry._placeholder = placeholder
    entry._is_ph = False
    if value:
        entry.delete(0, 'end')
        entry.insert(0, value)
        entry.config(fg=BLACK)
    else:
        _entry_show_placeholder(entry, placeholder)

    def on_in(_):
        if entry._is_ph:
            entry.delete(0, 'end')
            entry.config(fg=BLACK)
            entry._is_ph = False

    def on_out(_):
        if not entry.get():
            _entry_show_placeholder(entry, placeholder)

    entry.bind('<FocusIn>', on_in)
    entry.bind('<FocusOut>', on_out)


def read_entry(entry):
    """Rzeczywista wartość pola (pusta, gdy pokazany placeholder)."""
    return '' if getattr(entry, '_is_ph', False) else entry.get().strip()


def _text_show_placeholder(text, placeholder):
    text.delete('1.0', 'end')
    text.insert('1.0', placeholder)
    text.config(fg=GREY)
    text._is_ph = True


def add_text_placeholder(text, placeholder, value=""):
    """Wieloliniowe pole (Text) z wyszarzonym placeholderem."""
    text._placeholder = placeholder
    text._is_ph = False
    if value:
        text.delete('1.0', 'end')
        text.insert('1.0', value)
        text.config(fg=BLACK)
    else:
        _text_show_placeholder(text, placeholder)

    def on_in(_):
        if text._is_ph:
            text.delete('1.0', 'end')
            text.config(fg=BLACK)
            text._is_ph = False

    def on_out(_):
        if not text.get('1.0', 'end').strip():
            _text_show_placeholder(text, placeholder)

    text.bind('<FocusIn>', on_in)
    text.bind('<FocusOut>', on_out)


def read_text(text):
    """Zawartość pola (pusta, gdy placeholder), bez końcowych pustych linii."""
    if getattr(text, '_is_ph', False):
        return ''
    return text.get('1.0', 'end').rstrip('\n')


def read_text_lines(text):
    """Niepuste linie pola wieloliniowego (wartości parametru 5b)."""
    return [ln.strip() for ln in read_text(text).splitlines() if ln.strip()]


def make_scrollable(parent):
    """Zwróć wewnętrzną ramkę osadzoną w pionowo przewijanym Canvas."""
    canvas = tk.Canvas(parent, highlightthickness=0)
    scroll = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
    inner = tk.Frame(canvas)
    inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
    win = canvas.create_window((0, 0), window=inner, anchor='nw')
    canvas.bind('<Configure>', lambda e: canvas.itemconfig(win, width=e.width))
    canvas.configure(yscrollcommand=scroll.set)
    canvas.pack(side='left', fill='both', expand=True)
    scroll.pack(side='right', fill='y')

    def _wheel(e):
        canvas.yview_scroll(int(-e.delta / 120), 'units')

    canvas.bind_all('<MouseWheel>', _wheel)
    return inner


# =============================================================================
#  APLIKACJA — KREATOR
# =============================================================================

class SummonFeedGUI:
    """Kreator okienkowy sterujący silnikiem ``GuiGenerator``."""

    def __init__(self):
        self.engine = GuiGenerator()
        self.root = tk.Tk()
        self.root.title(self.t('app_title'))
        self.root.geometry("860x680")
        self.root.minsize(720, 560)

        self.container = tk.Frame(self.root)
        self.container.pack(fill='both', expand=True)
        self.current_frame = None

        # --- stan kreatora ---
        self.loaded_config = None          # konfiguracja wczytana z pliku (tymczasowe domyślne)
        self.selected_structure_name = None
        self.structure_var = None
        self.param_checkvars = {}          # {param_name: BooleanVar} — wybór w kroku 4
        self.param_widgets = {}            # {param_name: {...}} — pola w kroku 5
        self.prefix_var = None
        self.current_config = None         # konfiguracja zebrana przy generowaniu (do zapisu)
        self.last_output_file = None

        self.show_language()

    # -- skróty --------------------------------------------------------------
    def t(self, key, **kw):
        return self.engine.t(key, **kw)

    # -----------------------------------------------------------------------
    #  BUDOWA POJEDYNCZEGO OKNA (KROKU)
    # -----------------------------------------------------------------------
    def _new_step(self, title, on_continue, on_back,
                  back_enabled=True, continue_enabled=True):
        """Zbuduj szkielet okna: pasek z tytułem i przyciskami, zwróć ramkę-treść."""
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.root.unbind_all('<MouseWheel>')

        frame = tk.Frame(self.container)
        frame.pack(fill='both', expand=True)
        self.current_frame = frame

        top = tk.Frame(frame)
        top.pack(fill='x', padx=14, pady=(12, 6))
        tk.Label(top, text=title, font=('Segoe UI', 15, 'bold')).pack(side='left')

        cont = ttk.Button(top, text=self.t('btn_continue'), command=on_continue)
        cont.pack(side='right', padx=(8, 0))
        back = ttk.Button(top, text=self.t('btn_back'), command=on_back)
        back.pack(side='right')
        if not back_enabled:
            back.state(['disabled'])
        if not continue_enabled:
            cont.state(['disabled'])

        ttk.Separator(frame, orient='horizontal').pack(fill='x', padx=14, pady=(0, 8))

        body = tk.Frame(frame)
        body.pack(fill='both', expand=True, padx=14, pady=(0, 12))
        return body

    # -----------------------------------------------------------------------
    #  KROK 1 — JĘZYK
    # -----------------------------------------------------------------------
    def show_language(self):
        body = self._new_step(self.t('header_lang'),
                              on_continue=self._language_continue,
                              on_back=self.root.destroy,
                              back_enabled=False)

        codes = list(self.engine.languages.keys())
        if not codes:
            tk.Label(body, text=self.t('no_languages')).pack(anchor='w')
            self._lang_var = None
            return

        self._lang_var = tk.StringVar(value=self.engine.lang if self.engine.lang in codes else codes[0])
        for code in codes:
            name = self.engine.languages[code].get('_name', code)
            ttk.Radiobutton(body, text=f"{name}  ({code})",
                            variable=self._lang_var, value=code).pack(anchor='w', pady=3)

    def _language_continue(self):
        if getattr(self, '_lang_var', None) is not None:
            self.engine.lang = self._lang_var.get()
        self.root.title(self.t('app_title'))
        self.show_idle()

    # -----------------------------------------------------------------------
    #  KROK 2 — KROK POŚREDNI (PLACEHOLDER)
    # -----------------------------------------------------------------------
    def show_idle(self):
        body = self._new_step(self.t('header_idle'),
                              on_continue=self.show_load_config,
                              on_back=self.show_language)
        tk.Label(body, text=self.t('idle_placeholder'),
                 wraplength=760, justify='left').pack(anchor='w', pady=6)

    # -----------------------------------------------------------------------
    #  KROK 3 — WCZYTANIE KONFIGURACJI
    # -----------------------------------------------------------------------
    def show_load_config(self):
        body = self._new_step(self.t('header_load_config'),
                              on_continue=self._load_config_continue,
                              on_back=self.show_idle)

        self._load_choice = tk.IntVar(value=2)  # domyślnie: nowa konfiguracja
        ttk.Radiobutton(body, text=self.t('load_opt_from_file'),
                        variable=self._load_choice, value=1).pack(anchor='w', pady=4)
        ttk.Radiobutton(body, text=self.t('load_opt_fresh'),
                        variable=self._load_choice, value=2).pack(anchor='w', pady=4)
        ttk.Radiobutton(body, text=self.t('load_opt_quit'),
                        variable=self._load_choice, value=3).pack(anchor='w', pady=4)

        self._load_info = tk.Label(body, text="", fg="#2a7a2a")
        self._load_info.pack(anchor='w', pady=(10, 0))
        if self.loaded_config is not None:
            name = self.loaded_config.get('_source', '')
            if name:
                self._load_info.config(text=self.t('loaded_config_info', name=name))

    def _load_config_continue(self):
        choice = self._load_choice.get()
        if choice == 3:
            self.root.destroy()
            return
        if choice == 1:
            path = filedialog.askopenfilename(
                title=self.t('load_config_dialog'),
                initialdir=str(self.engine.base_path),
                filetypes=[("JSON", "*.json"), ("All files", "*.*")])
            if not path:
                return  # anulowano — zostań na oknie
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                cfg['_source'] = Path(path).name
                self.loaded_config = cfg
            except (OSError, json.JSONDecodeError) as e:
                messagebox.showerror(self.t('header_load_config'),
                                     self.t('load_error', e=e))
                return
        else:  # choice == 2 — świeża konfiguracja
            self.loaded_config = None

        self.show_structure()

    # -----------------------------------------------------------------------
    #  KROK 4 — STRUKTURA + WYBÓR PARAMETRÓW
    # -----------------------------------------------------------------------
    def show_structure(self):
        body = self._new_step(self.t('header_structure'),
                              on_continue=self._structure_continue,
                              on_back=self.show_load_config)

        tk.Label(body, text=self.t('structure_hint'),
                 wraplength=760, justify='left').pack(anchor='w', pady=(0, 8))

        structures = list(self.engine.structures.keys())
        if not structures:
            tk.Label(body, text=self.t('no_structures_gui')).pack(anchor='w')
            self.structure_var = None
            return

        # wstępny wybór: z wczytanej konfiguracji, poprzedni, albo pierwszy
        default_struct = None
        if self.loaded_config and self.loaded_config.get('structure') in structures:
            default_struct = self.loaded_config['structure']
        elif self.selected_structure_name in structures:
            default_struct = self.selected_structure_name
        else:
            default_struct = structures[0]

        self.structure_var = tk.StringVar(value=default_struct)
        struct_bar = tk.Frame(body)
        struct_bar.pack(fill='x', pady=(0, 8))
        for name in structures:
            desc = self.engine._desc(self.engine.structures[name]['data'])
            ttk.Radiobutton(struct_bar, text=f"{name} — {desc}",
                            variable=self.structure_var, value=name,
                            command=self._refresh_param_checklist).pack(anchor='w', pady=2)

        ttk.Separator(body, orient='horizontal').pack(fill='x', pady=6)

        # kontener na przewijaną listę parametrów
        self._params_area = tk.Frame(body)
        self._params_area.pack(fill='both', expand=True)
        self._refresh_param_checklist()

    def _refresh_param_checklist(self):
        """Odśwież listę checkboxów parametrów dla aktualnie wybranej struktury."""
        for child in self._params_area.winfo_children():
            child.destroy()

        structure_name = self.structure_var.get()
        available = self.engine._filter_parameters_for_structure(structure_name)

        if not available:
            tk.Label(self._params_area, text=self.t('no_params_hint')).pack(anchor='w')
            self.param_checkvars = {}
            return

        inner = make_scrollable(self._params_area)
        self.param_checkvars = {}

        # domyślne zaznaczenia z wczytanej konfiguracji (jeśli dotyczą tej struktury)
        cfg_params = {}
        if self.loaded_config and self.loaded_config.get('structure') == structure_name:
            cfg_params = self.loaded_config.get('params', {})

        # parametry wykluczające się wzajemnie: z grupy zaznaczony jest najwyżej jeden,
        # a przy świeżej konfiguracji — ten zalecany dla wybranej struktury
        groups = self.engine._exclusive_groups(structure_name)
        group_of = {}
        for group, members in groups.items():
            recommended = self.engine._exclusive_default(members, structure_name)
            for m in members:
                group_of[m] = (group, m == recommended)

        for context in sorted(available.keys()):
            tk.Label(inner, text=self.t('context', context=context),
                     font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(8, 2))
            for param_name in available[context]:
                data = self.engine.parameters[param_name]['data']
                if param_name in cfg_params:
                    default_on = cfg_params[param_name].get('enabled', True)
                elif cfg_params:
                    default_on = False  # wczytana konfiguracja bez tego parametru → odznacz
                elif param_name in group_of:
                    default_on = group_of[param_name][1]  # tylko zalecany z grupy
                else:
                    default_on = True   # świeża konfiguracja → domyślnie zaznaczone
                var = tk.BooleanVar(value=default_on)
                self.param_checkvars[param_name] = var
                label = f"{param_name} — {self.engine._desc(data)}"
                if param_name in group_of:
                    label += "   " + self.t('exclusive_tag', group=group_of[param_name][0])
                    cb = ttk.Checkbutton(
                        inner, text=label, variable=var,
                        command=lambda n=param_name: self._enforce_exclusive(n))
                else:
                    cb = ttk.Checkbutton(inner, text=label, variable=var)
                cb.pack(anchor='w', padx=12)

        # wczytana konfiguracja mogła mieć zaznaczone dwa parametry z jednej grupy
        for group, members in groups.items():
            picked = [m for m in members
                      if m in self.param_checkvars and self.param_checkvars[m].get()]
            for extra in picked[1:]:
                self.param_checkvars[extra].set(False)

    def _enforce_exclusive(self, param_name):
        """Zaznaczenie parametru z grupy wykluczającej odznacza pozostałe z tej grupy.
        Odznaczenie nie zaznacza niczego — grupa może zostać pusta."""
        if not self.param_checkvars.get(param_name) or not self.param_checkvars[param_name].get():
            return
        structure_name = self.structure_var.get()
        data = self.engine.parameters[param_name]['data']
        group = data.get('exclusiveGroup')
        if not group:
            return
        for other in self.engine._exclusive_groups(structure_name).get(group, []):
            if other != param_name and other in self.param_checkvars:
                self.param_checkvars[other].set(False)

    def _structure_continue(self):
        if self.structure_var is None:
            messagebox.showwarning(self.t('header_structure'),
                                   self.t('must_pick_structure'))
            return
        self.selected_structure_name = self.structure_var.get()
        self.show_params()

    # -----------------------------------------------------------------------
    #  KROK 5 — KONFIGURACJA WYBRANYCH PARAMETRÓW
    # -----------------------------------------------------------------------
    def show_params(self):
        body = self._new_step(self.t('header_params'),
                              on_continue=self._params_continue,
                              on_back=self.show_structure)

        tk.Label(body, text=self.t('params_config_hint'),
                 wraplength=800, justify='left').pack(anchor='w', pady=(0, 6))

        # globalny prefiks elementów
        prefix_bar = tk.Frame(body)
        prefix_bar.pack(fill='x', pady=(0, 8))
        tk.Label(prefix_bar, text=self.t('prefix_label')).pack(side='left')
        self.prefix_var = tk.StringVar()
        if self.loaded_config and self.loaded_config.get('prefix'):
            self.prefix_var.set(self.loaded_config['prefix'])
        pref_entry = tk.Entry(prefix_bar, textvariable=self.prefix_var, width=10)
        pref_entry.pack(side='left', padx=6)

        ttk.Separator(body, orient='horizontal').pack(fill='x', pady=4)

        inner = make_scrollable(body)
        self.param_widgets = {}

        cfg_params = {}
        if self.loaded_config and self.loaded_config.get('structure') == self.selected_structure_name:
            cfg_params = self.loaded_config.get('params', {})

        # tylko parametry zaznaczone w kroku 4
        selected = [name for name, var in self.param_checkvars.items() if var.get()]

        # configVary współdzielone przez parametry (np. sales_stocks) silnik deduplikuje
        # po nazwie — edytujemy je tylko przy pierwszym parametrze; kolejne → komentarz.
        seen_configvars = {}  # {cv_name: param_name (pierwszy właściciel)}

        for param_name in selected:
            data = self.engine.parameters[param_name]['data']
            saved = cfg_params.get(param_name, {})

            block = tk.LabelFrame(inner, text=param_name, padx=10, pady=8)
            block.pack(fill='x', expand=True, padx=4, pady=6)

            # 5c — przełącznik „dołącz do feedu” (domyślnie włączony)
            enabled_var = tk.BooleanVar(value=saved.get('enabled', True))
            ttk.Checkbutton(block, text=self.t('param_enabled'),
                            variable=enabled_var).pack(anchor='w')
            tk.Label(block, text=self.engine._desc(data),
                     fg=GREY, wraplength=760, justify='left').pack(anchor='w', pady=(0, 4))

            # 5a — nowa nazwa elementu (placeholder = domyślne z 'output')
            name_row = tk.Frame(block)
            name_row.pack(fill='x', pady=2)
            tk.Label(name_row, text=self.t('param_name_label'), width=16, anchor='w').pack(side='left')
            name_entry = tk.Entry(name_row)
            name_entry.pack(side='left', fill='x', expand=True)
            default_out = data.get('output', '')
            add_entry_placeholder(name_entry, default_out, value=saved.get('name_override', ''))

            # 5b — pole wartości dla każdego configVar (1 linia bez separatora,
            #      6 linii z suwakiem przy separatorze). Duplikat → komentarz.
            config_vars = data.get('configVars', [])
            cv_texts = {}
            if not config_vars:
                tk.Label(block, text=self.t('no_configvars'), fg=GREY).pack(anchor='w', pady=(4, 0))
            else:
                saved_cv = saved.get('config_values', {})
                for var in config_vars:
                    cv_name = var['name']
                    if cv_name in seen_configvars:
                        # configVar już edytowany przy innym parametrze — tylko informacja
                        tk.Label(block,
                                 text=self.t('configvar_shared', name=cv_name,
                                             owner=seen_configvars[cv_name]),
                                 fg=GREY, wraplength=760, justify='left').pack(
                            anchor='w', pady=(6, 0))
                        continue
                    seen_configvars[cv_name] = param_name
                    tk.Label(block, text=cv_name, font=('Segoe UI', 9, 'bold')).pack(
                        anchor='w', pady=(6, 0))
                    txt = self._make_value_field(block, var)
                    placeholder = var.get('default', '')
                    add_text_placeholder(txt, placeholder, value=saved_cv.get(cv_name, ''))
                    cv_texts[cv_name] = txt

            self.param_widgets[param_name] = {
                'enabled': enabled_var,
                'name_entry': name_entry,
                'cv_texts': cv_texts,
                'context': data.get('context', 'unknown'),
            }

    def _make_value_field(self, parent, var):
        """Pole wartości configVar. Z separatorem → Text 6 linii + suwak (lista wartości);
        bez separatora → Text 1 linii (pojedyncza wartość)."""
        if var.get('delimeter'):
            holder = tk.Frame(parent)
            holder.pack(fill='x')
            txt = tk.Text(holder, height=6, wrap='word')
            scroll = ttk.Scrollbar(holder, orient='vertical', command=txt.yview)
            txt.configure(yscrollcommand=scroll.set)
            txt.pack(side='left', fill='x', expand=True)
            scroll.pack(side='right', fill='y')
            return txt
        txt = tk.Text(parent, height=1, wrap='none')
        txt.pack(fill='x')
        return txt

    def _params_continue(self):
        """Krok 6 — zbierz stan, wygeneruj XSLT, przejdź do kroku 7."""
        self._collect_config()
        try:
            self._generate()
        except Exception as e:  # noqa: BLE001 — pokaż każdy błąd użytkownikowi
            messagebox.showerror(self.t('header_params'), self.t('generate_error', e=e))
            return
        self.show_save_config()

    def _collect_config(self):
        """Zbierz aktualny stan pól i zapamiętaj do generowania oraz zapisu."""
        prefix_raw = self.prefix_var.get().strip()
        params = {}
        for param_name, w in self.param_widgets.items():
            cv_values = {cv: read_text(txt) for cv, txt in w['cv_texts'].items()}
            params[param_name] = {
                'enabled': w['enabled'].get(),
                'name_override': read_entry(w['name_entry']),
                'config_values': cv_values,
                'context': w['context'],
            }
        self.current_config = {
            'lang': self.engine.lang,
            'prefix': prefix_raw,
            'structure': self.selected_structure_name,
            'params': params,
        }

    def _generate(self):
        """Przełóż zebraną konfigurację na stan silnika i zbuduj plik XSLT."""
        cfg = self.current_config
        engine = self.engine
        engine.selected_structure = engine.structures[cfg['structure']]

        # prefiks: '' (pusty) → g; '-' → brak; inny → nowy
        engine.prefix_override = None
        if cfg['prefix'] == '-':
            engine.prefix_override = ''
        elif cfg['prefix']:
            new_prefix = cfg['prefix'].rstrip(':')
            if new_prefix and new_prefix != 'g':
                engine.prefix_override = new_prefix

        # selected_params + nadpisania nazw + wartości configVars
        selected_params = {}
        engine.output_overrides = {}
        engine._gui_config_values = {}

        for param_name, p in cfg['params'].items():
            if not p['enabled']:
                continue
            context = p['context']
            selected_params.setdefault(context, []).append(param_name)

            if p['name_override']:
                default_out = engine.parameters[param_name]['data'].get('output', '')
                if p['name_override'] != default_out:
                    engine.output_overrides[param_name] = p['name_override']

            data = engine.parameters[param_name]['data']
            cv_meta = {v['name']: v for v in data.get('configVars', [])}
            for cv_name, raw in p['config_values'].items():
                # współdzielony configVar konfigurujemy raz — pierwszy wpis wygrywa
                if cv_name in engine._gui_config_values:
                    continue
                var = cv_meta.get(cv_name, {})
                engine._gui_config_values[cv_name] = self._format_config_value(var, raw)

        engine.selected_params = selected_params

        xslt = engine._build_xslt_structure()

        structure_name = engine.selected_structure['data']['name']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = engine.output_path / f"{structure_name}_generated_{timestamp}.xsl"
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(xslt)
        self.last_output_file = out_file

    @staticmethod
    def _format_config_value(var, raw):
        """Złóż wartość configVar z pola wieloliniowego wg jego separatora.
        Puste → domyślne. Z separatorem → linie otoczone separatorem
        (nowe linie stają się separatorami zmiennej). Bez separatora → pierwsza linia."""
        default = var.get('default', '')
        delimeter = var.get('delimeter', '')
        lines = [ln.strip() for ln in (raw or '').splitlines() if ln.strip()]
        if not lines:
            return default
        if delimeter:
            return delimeter + delimeter.join(lines) + delimeter
        return lines[0]

    # -----------------------------------------------------------------------
    #  KROK 7 — ZAPIS KONFIGURACJI, POWRÓT DO KROKU 3
    # -----------------------------------------------------------------------
    def show_save_config(self):
        body = self._new_step(self.t('header_save_config'),
                              on_continue=self.show_load_config,
                              on_back=self.show_params)

        if self.last_output_file is not None:
            tk.Label(body, text=self.t('generated_info', name=self.last_output_file.name),
                     fg="#2a7a2a", wraplength=780, justify='left').pack(anchor='w', pady=(0, 12))

        tk.Label(body, text=self.t('save_config_question'),
                 wraplength=780, justify='left').pack(anchor='w', pady=(0, 8))
        ttk.Button(body, text=self.t('save_config_btn'),
                   command=self._save_config_dialog).pack(anchor='w')

        self._save_info = tk.Label(body, text="", fg="#2a7a2a")
        self._save_info.pack(anchor='w', pady=(10, 0))

    def _save_config_dialog(self):
        structure = (self.current_config or {}).get('structure', 'config')
        default_name = f"{structure}_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = filedialog.asksaveasfilename(
            title=self.t('save_config_dialog'),
            initialdir=str(self.engine.base_path),
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            to_save = dict(self.current_config or {})
            to_save.pop('_source', None)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(to_save, f, ensure_ascii=False, indent=2)
            self._save_info.config(text=self.t('config_saved', name=Path(path).name))
        except OSError as e:
            messagebox.showerror(self.t('header_save_config'),
                                 self.t('save_config_error', e=e))

    # -----------------------------------------------------------------------
    def run(self):
        self.root.mainloop()


def main():
    app = SummonFeedGUI()
    app.run()


if __name__ == "__main__":
    main()
