#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARA v2 – graficzna aplikacja do cyklicznego generowania output.csv.

Cykl pracy:
  1. co N minut pobiera feed XML ze sklepu ARA,
  2. wyciąga zdeduplikowaną listę marek (synch_template_brands.xml),
  3. dla marek włączonych w konfiguracji generuje output.csv
     (synch_template.xml z podmienioną zmienną nazwa_marki_i_doliczany_marża).

Konfiguracja trzymana jest w config.json – szablony XSLT na dysku pozostają
nietknięte, zmienna podmieniana jest w drzewie w pamięci.
"""

import csv
import io
import json
import os
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

import requests
from lxml import etree

# --- stałe konfiguracyjne ---------------------------------------------------

# Po spakowaniu PyInstallerem (--onefile) __file__ wskazuje tymczasowy katalog
# rozpakowania (_MEIPASS), a nie folder z exe. Pliki danych – szablony XSLT,
# config.json i zapisywany output.csv – mają leżeć obok exe, dlatego w trybie
# "frozen" bazujemy na położeniu samego pliku wykonywalnego.
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

XML_URL = (
    'https://ara.waw.pl/wymiana/ara.xml'
    '?_gl=1*14loj5u*_ga*MjIwMDk5NDAuMTc1MjUwMTk4MQ..'
    '*_ga_2QRB642E1C*czE3NTI1MDE5ODAkbzEkZzEkdDE3NTI1MDIwNjUkajU5JGwwJGgxNzk4NjM0OTUw'
)

XSLT_MAIN = os.path.join(BASE_DIR, 'synch_template.xml')
XSLT_BRANDS = os.path.join(BASE_DIR, 'synch_template_brands.xml')
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
OUT_CSV = os.path.join(BASE_DIR, 'output.csv')

XSL_NS = 'http://www.w3.org/1999/XSL/Transform'
MARGIN_VAR = 'nazwa_marki_i_doliczany_marza'
RECORD_TAG = 'item'
CSV_DELIMITER = ','

DEFAULT_INTERVAL_MIN = 30
MIN_INTERVAL_MIN = 1
MAX_INTERVAL_MIN = 1440
HTTP_TIMEOUT = 60

# --- paleta -----------------------------------------------------------------

C_BG = '#f4f6f8'
C_CARD = '#ffffff'
C_LINE = '#dfe4ea'
C_TEXT = '#1f2933'
C_MUTED = '#6b7684'
C_ACCENT = '#0b6bcb'
C_NEW_BG = '#fff6e0'
C_NEW_FG = '#9a6700'
C_GONE_BG = '#fdeced'
C_GONE_FG = '#b3261e'
C_OK = '#1a7f4b'
C_ERR = '#b3261e'
C_ROW_ALT = '#fafbfc'


# ============================================================================
#  Warstwa danych
# ============================================================================

def _parser():
    return etree.XMLParser(encoding='utf-8', recover=True)


def fetch_feed():
    """Pobiera i parsuje feed XML. Zwraca drzewo lxml."""
    resp = requests.get(XML_URL, timeout=HTTP_TIMEOUT)
    resp.raise_for_status()
    return etree.parse(io.BytesIO(resp.content), _parser())


def extract_brands(xml_tree):
    """Zwraca posortowaną, zdeduplikowaną listę marek z feedu."""
    xslt = etree.parse(XSLT_BRANDS, _parser())
    result = etree.XSLT(xslt)(xml_tree)

    brands = set()
    for node in result.getroot().xpath('.//*[local-name()="marka"]'):
        name = (node.text or '').strip()
        # pionowa kreska jest separatorem w zmiennej XSLT – marka z tym
        # znakiem w nazwie zepsułaby dopasowanie, więc taki rekord pomijamy
        if name and '|' not in name:
            brands.add(name)
    return sorted(brands, key=lambda s: s.lower())


def build_margin_variable(enabled):
    """Składa treść zmiennej XSLT z par (marka, marża_procent)."""
    lines = ['']
    for brand, margin in enabled:
        lines.append('|{}|{:g}%|'.format(brand, margin))
    lines.append('')
    return '\n'.join(lines)


def build_main_transform(enabled):
    """Wczytuje główny szablon i podmienia zmienną z marżą w pamięci."""
    tree = etree.parse(XSLT_MAIN, _parser())

    target = None
    for el in tree.getroot():
        if el.tag == '{%s}variable' % XSL_NS and el.get('name') == MARGIN_VAR:
            target = el
            break
    if target is None:
        raise RuntimeError(
            'W szablonie {} nie znaleziono zmiennej "{}".'.format(
                os.path.basename(XSLT_MAIN), MARGIN_VAR)
        )

    for child in list(target):
        target.remove(child)
    target.text = build_margin_variable(enabled)

    return etree.XSLT(tree)


def write_csv(result_tree):
    """Zapisuje wynik transformacji do output.csv. Zwraca liczbę rekordów."""
    records = result_tree.getroot().xpath(
        './/*[local-name()="%s"]' % RECORD_TAG)

    if not records:
        with open(OUT_CSV, 'w', encoding='utf-8') as fh:
            fh.write('')
        return 0

    columns = []
    seen = set()
    for child in records[0]:
        col = child.tag.split('}', 1)[-1]
        if col not in seen:
            seen.add(col)
            columns.append(col)

    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh, delimiter=CSV_DELIMITER)
        writer.writerow(columns)
        for rec in records:
            row = []
            for col in columns:
                nodes = rec.xpath('./*[local-name()="%s"]' % col)
                el = nodes[0] if nodes else None
                row.append((el.text or '').strip() if el is not None else '')
            writer.writerow(row)

    return len(records)


def load_config():
    """Wczytuje config.json. Zwraca (interwał_w_minutach, {marka: {...}})."""
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_INTERVAL_MIN, {}
    try:
        with open(CONFIG_PATH, encoding='utf-8') as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return DEFAULT_INTERVAL_MIN, {}

    interval = data.get('interval_minutes', DEFAULT_INTERVAL_MIN)
    try:
        interval = int(interval)
    except (TypeError, ValueError):
        interval = DEFAULT_INTERVAL_MIN
    interval = max(MIN_INTERVAL_MIN, min(MAX_INTERVAL_MIN, interval))

    brands = {}
    for name, entry in (data.get('brands') or {}).items():
        if not isinstance(entry, dict):
            continue
        try:
            margin = float(entry.get('margin', 0))
        except (TypeError, ValueError):
            margin = 0.0
        brands[name] = {
            'enabled': bool(entry.get('enabled', False)),
            'margin': margin,
        }
    return interval, brands


def save_config(interval, brands):
    payload = {'interval_minutes': interval, 'brands': brands}
    with open(CONFIG_PATH, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)


# ============================================================================
#  Widgety pomocnicze
# ============================================================================

class ScrollFrame(ttk.Frame):
    """Pionowo przewijalny kontener – zawartość dodajemy do .body."""

    def __init__(self, master):
        super().__init__(master)

        self.canvas = tk.Canvas(self, bg=C_CARD, highlightthickness=0, bd=0)
        self.scrollbar = ttk.Scrollbar(
            self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)

        self.body = tk.Frame(self.canvas, bg=C_CARD)
        self._win = self.canvas.create_window(
            (0, 0), window=self.body, anchor='nw')

        self.body.bind('<Configure>', self._on_body_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.bind('<Enter>', self._bind_wheel)
        self.canvas.bind('<Leave>', self._unbind_wheel)

    def _on_body_configure(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self._win, width=event.width)

    def _bind_wheel(self, _event):
        self.canvas.bind_all('<MouseWheel>', self._on_wheel)

    def _unbind_wheel(self, _event):
        self.canvas.unbind_all('<MouseWheel>')

    def _on_wheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 120), 'units')

    def scroll_top(self):
        self.canvas.yview_moveto(0)

    def clear(self):
        for child in self.body.winfo_children():
            child.destroy()


class BrandRow(tk.Frame):
    """Wiersz listy: przełącznik + nazwa marki + marża w procentach."""

    def __init__(self, master, brand, enabled, margin, is_new, bg):
        super().__init__(master, bg=bg)
        self.brand = brand
        self.is_new = is_new

        self.var_enabled = tk.BooleanVar(value=enabled)
        self.var_margin = tk.StringVar(value='{:g}'.format(margin))

        self.columnconfigure(1, weight=1)

        tk.Checkbutton(
            self, variable=self.var_enabled, bg=bg, activebackground=bg,
            highlightthickness=0, bd=0, command=self._sync_state
        ).grid(row=0, column=0, padx=(12, 6), pady=7)

        self.lbl = tk.Label(
            self, text=brand, bg=bg, fg=C_TEXT, anchor='w',
            font=('Segoe UI', 10))
        self.lbl.grid(row=0, column=1, sticky='we')

        if is_new:
            tk.Label(
                self, text='NOWA', bg=C_NEW_BG, fg=C_NEW_FG,
                font=('Segoe UI', 8, 'bold'), padx=6, pady=1
            ).grid(row=0, column=2, padx=(0, 10))

        self.spin = ttk.Spinbox(
            self, from_=0, to=99, increment=5, width=6, justify='right',
            textvariable=self.var_margin)
        self.spin.grid(row=0, column=3, padx=(0, 2))

        tk.Label(self, text='%', bg=bg, fg=C_MUTED,
                 font=('Segoe UI', 10)).grid(row=0, column=4, padx=(0, 14))

        self._sync_state()

    def _sync_state(self):
        on = self.var_enabled.get()
        self.spin.state(['!disabled'] if on else ['disabled'])
        self.lbl.configure(fg=C_TEXT if on else C_MUTED)

    def margin_value(self):
        """Zwraca marża jako float; przy błędnym wpisie zwraca None."""
        raw = self.var_margin.get().strip().replace(',', '.').rstrip('%')
        if not raw:
            return 0.0
        try:
            value = float(raw)
        except ValueError:
            return None
        if value < 0 or value >= 100:
            return None
        return value


# ============================================================================
#  Aplikacja
# ============================================================================

class AraApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title('ARA – generator output.csv')
        self.geometry('760x640')
        self.minsize(640, 540)
        self.configure(bg=C_BG)

        self.interval_min, self.brands_cfg = load_config()

        self.available_brands = []   # marki z ostatniego udanego pobrania
        self.rows = []               # widgety BrandRow w trybie edycji
        self.next_run = None         # znacznik czasu następnego cyklu
        self.busy = False
        self.mode = 'edit'           # 'edit' albo 'running'
        self._closing = False
        self._rerun = False          # cykl zlecony w trakcie innego cyklu
        self._after_ids = {}         # nazwa -> uchwyt zaplanowanego callbacku

        # Jeden trwały wątek roboczy obsługuje wszystkie cykle. Osobny wątek
        # na cykl powodował zakleszczenie libxml2 przy trzeciej z kolei
        # transformacji XSLT, dlatego cała praca z lxml zostaje na tym
        # jednym wątku. Widgetów nie dotyka – wynik wraca kolejką results,
        # którą wątek główny odpytuje w _poll_queue.
        self.jobs = queue.Queue()
        self.results = queue.Queue()
        self.worker = threading.Thread(
            target=self._job_worker, daemon=True, name='ara-worker')
        self.worker.start()

        self.var_status = tk.StringVar(value='Gotowy.')
        self.var_countdown = tk.StringVar(value='--:--')
        self.var_interval = tk.StringVar(value=str(self.interval_min))
        self.var_search = tk.StringVar()
        self.var_search.trace_add('write', lambda *_: self._render_rows())

        self._setup_style()
        self._build_ui()

        self.protocol('WM_DELETE_WINDOW', self._on_close)

        self._schedule('start', 200, lambda: self._run_job(initial=True))
        self._schedule('poll', 100, self._poll_queue)
        self._schedule('tick', 1000, self._tick)

    # --- cykl życia okna ---------------------------------------------------

    def _schedule(self, key, delay_ms, callback):
        """after() z zapamiętaniem uchwytu, żeby dało się posprzątać.

        Uchwyt trzymamy pod stałym kluczem – cykliczne callbacki nadpisują
        swój poprzedni wpis, więc słownik nie puchnie przy długiej pracy.
        """
        if self._closing:
            return
        self._after_ids[key] = self.after(delay_ms, callback)

    def _on_close(self):
        """Zamyka aplikację całkowicie – zatrzymuje pętlę odświeżania.

        Wątki robocze są demonami, więc nie wstrzymają wyjścia z procesu;
        anulujemy tylko zaplanowane callbacki, żeby żaden nie odpalił się
        na zniszczonych już widgetach.
        """
        if self._closing:
            return
        self._closing = True
        for handle in self._after_ids.values():
            try:
                self.after_cancel(handle)
            except tk.TclError:
                pass
        self._after_ids.clear()
        self.jobs.put(None)          # wybudza wątek roboczy, by się zakończył
        self.quit()
        self.destroy()

    # --- budowa interfejsu -------------------------------------------------

    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        style.configure('TFrame', background=C_BG)
        style.configure('TButton', font=('Segoe UI', 10), padding=(14, 7))
        style.configure(
            'Accent.TButton', font=('Segoe UI', 10, 'bold'), padding=(18, 8),
            background=C_ACCENT, foreground='#ffffff', borderwidth=0)
        style.map(
            'Accent.TButton',
            background=[('active', '#0959ab'), ('disabled', '#a9c4e4')])

    def _build_ui(self):
        head = tk.Frame(self, bg=C_BG)
        head.pack(fill='x', padx=18, pady=(16, 10))

        tk.Label(head, text='Dostawca ARA', bg=C_BG, fg=C_TEXT,
                 font=('Segoe UI', 16, 'bold')).pack(side='left')

        self.lbl_mode = tk.Label(
            head, text='', bg=C_BG, fg=C_MUTED, font=('Segoe UI', 10))
        self.lbl_mode.pack(side='left', padx=(12, 0), pady=(6, 0))

        self.container = tk.Frame(self, bg=C_BG)
        self.container.pack(fill='both', expand=True, padx=18)

        self._build_edit_view()
        self._build_running_view()

        foot = tk.Frame(self, bg=C_BG)
        foot.pack(fill='x', padx=18, pady=(8, 14))

        self.lbl_status = tk.Label(
            foot, textvariable=self.var_status, bg=C_BG, fg=C_MUTED,
            font=('Segoe UI', 9), anchor='w')
        self.lbl_status.pack(side='left', fill='x', expand=True)

        self._show_edit(fetch=False)

    def _build_edit_view(self):
        self.view_edit = tk.Frame(self.container, bg=C_BG)

        bar = tk.Frame(self.view_edit, bg=C_BG)
        bar.pack(fill='x', pady=(0, 8))

        tk.Label(bar, text='Zaznacz marki i ustaw doliczaną marżę:',
                 bg=C_BG, fg=C_TEXT, font=('Segoe UI', 10)).pack(side='left')

        ttk.Entry(bar, textvariable=self.var_search, width=22).pack(side='right')
        tk.Label(bar, text='Szukaj:', bg=C_BG, fg=C_MUTED,
                 font=('Segoe UI', 9)).pack(side='right', padx=(0, 6))

        card = tk.Frame(self.view_edit, bg=C_CARD,
                        highlightbackground=C_LINE, highlightthickness=1)
        card.pack(fill='both', expand=True)

        self.scroll = ScrollFrame(card)
        self.scroll.pack(fill='both', expand=True)

        actions = tk.Frame(self.view_edit, bg=C_BG)
        actions.pack(fill='x', pady=(10, 0))

        self.lbl_counts = tk.Label(
            actions, text='', bg=C_BG, fg=C_MUTED, font=('Segoe UI', 9))
        self.lbl_counts.pack(side='left')

        ttk.Button(actions, text='Zapisz', style='Accent.TButton',
                   command=self._on_save).pack(side='right')

    def _build_running_view(self):
        self.view_run = tk.Frame(self.container, bg=C_BG)

        timer = tk.Frame(self.view_run, bg=C_CARD,
                         highlightbackground=C_LINE, highlightthickness=1)
        timer.pack(fill='x')

        inner = tk.Frame(timer, bg=C_CARD)
        inner.pack(fill='x', padx=16, pady=14)

        left = tk.Frame(inner, bg=C_CARD)
        left.pack(side='left')

        tk.Label(left, text='Do następnego odświeżenia', bg=C_CARD,
                 fg=C_MUTED, font=('Segoe UI', 9)).pack(anchor='w')
        tk.Label(left, textvariable=self.var_countdown, bg=C_CARD,
                 fg=C_ACCENT, font=('Consolas', 30, 'bold')).pack(anchor='w')

        right = tk.Frame(inner, bg=C_CARD)
        right.pack(side='right')

        row = tk.Frame(right, bg=C_CARD)
        row.pack(anchor='e')
        tk.Label(row, text='Interwał (min):', bg=C_CARD, fg=C_TEXT,
                 font=('Segoe UI', 10)).pack(side='left', padx=(0, 6))
        ttk.Spinbox(row, from_=MIN_INTERVAL_MIN, to=MAX_INTERVAL_MIN,
                    increment=5, width=6, justify='right',
                    textvariable=self.var_interval).pack(side='left')
        ttk.Button(row, text='Zastosuj', command=self._on_apply_interval).pack(
            side='left', padx=(6, 0))

        row2 = tk.Frame(right, bg=C_CARD)
        row2.pack(anchor='e', pady=(8, 0))
        ttk.Button(row2, text='Odśwież teraz',
                   command=lambda: self._run_job()).pack(side='left')

        tk.Label(self.view_run, text='Zapisana konfiguracja (tylko podgląd)',
                 bg=C_BG, fg=C_TEXT, font=('Segoe UI', 10)).pack(
            anchor='w', pady=(14, 6))

        card = tk.Frame(self.view_run, bg=C_CARD,
                        highlightbackground=C_LINE, highlightthickness=1)
        card.pack(fill='both', expand=True)

        self.tree_preview = ttk.Treeview(
            card, columns=('brand', 'margin'), show='headings',
            selectmode='none')
        self.tree_preview.heading('brand', text='Marka')
        self.tree_preview.heading('margin', text='Doliczana marża')
        self.tree_preview.column('brand', anchor='w', width=380)
        self.tree_preview.column('margin', anchor='e', width=140, stretch=False)

        sb = ttk.Scrollbar(card, orient='vertical',
                           command=self.tree_preview.yview)
        self.tree_preview.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        self.tree_preview.pack(fill='both', expand=True)

        actions = tk.Frame(self.view_run, bg=C_BG)
        actions.pack(fill='x', pady=(10, 0))

        self.lbl_last = tk.Label(
            actions, text='', bg=C_BG, fg=C_MUTED, font=('Segoe UI', 9))
        self.lbl_last.pack(side='left')

        ttk.Button(actions, text='Edytuj', style='Accent.TButton',
                   command=self._show_edit).pack(side='right')

    # --- przełączanie widoków ----------------------------------------------

    def _show_edit(self, fetch=True):
        """Przechodzi do konfiguracji; fetch=False tylko przy budowie okna,
        bo pierwsze pobranie startuje osobno tuż po otwarciu aplikacji."""
        self.mode = 'edit'
        self.view_run.pack_forget()
        self.view_edit.pack(fill='both', expand=True)
        self.lbl_mode.configure(text='– konfiguracja')
        self._render_rows()
        if fetch:
            # lista marek ma być świeża od razu po wejściu w edycję
            self._run_job()

    def _show_running(self):
        self.mode = 'running'
        self.view_edit.pack_forget()
        self.view_run.pack(fill='both', expand=True)
        self.lbl_mode.configure(text='– praca cykliczna')
        self._render_preview()

    # --- renderowanie listy marek ------------------------------------------

    def _render_rows(self):
        """Buduje listę: najpierw nowe marki, potem znane alfabetycznie."""
        if self.mode != 'edit':
            return

        # przepisz bieżące ustawienia z widgetów, zanim je zniszczymy
        self._harvest_rows(strict=False)

        self.scroll.clear()
        self.rows = []

        known = set(self.brands_cfg)
        available = list(self.available_brands)
        available_set = set(available)
        new_brands = [b for b in available if b not in known]
        old_brands = [b for b in available if b in known]
        gone = sorted((b for b in known if b not in available_set),
                      key=str.lower)

        needle = self.var_search.get().strip().lower()

        def visible(name):
            return not needle or needle in name.lower()

        body = self.scroll.body

        if not available:
            tk.Label(
                body, text='Pobieranie listy marek…',
                bg=C_CARD, fg=C_MUTED, font=('Segoe UI', 10), pady=30
            ).pack(fill='x')
            self.lbl_counts.configure(text='')
            return

        shown_new = [b for b in new_brands if visible(b)]
        shown_old = [b for b in old_brands if visible(b)]

        if shown_new:
            self._section(
                body,
                'Nowe marki od ostatniej konfiguracji ({})'.format(
                    len(shown_new)),
                C_NEW_BG, C_NEW_FG)
            for i, brand in enumerate(shown_new):
                self._add_row(body, brand, is_new=True, index=i)

        if gone and not needle:
            self._section(
                body,
                'Nieobecne w feedzie – zostaną zapomniane po zapisie ({})'
                .format(len(gone)),
                C_GONE_BG, C_GONE_FG)
            for brand in gone:
                tk.Label(
                    body, text='   {}'.format(brand), bg=C_CARD, fg=C_GONE_FG,
                    anchor='w', font=('Segoe UI', 10, 'overstrike'), pady=5
                ).pack(fill='x', padx=12)

        if shown_old:
            if shown_new or (gone and not needle):
                self._section(body, 'Znane marki ({})'.format(len(shown_old)),
                              '#eef1f5', C_MUTED)
            for i, brand in enumerate(shown_old):
                self._add_row(body, brand, is_new=False, index=i)

        if not shown_new and not shown_old:
            tk.Label(
                body, text='Brak marek pasujących do wyszukiwania.',
                bg=C_CARD, fg=C_MUTED, font=('Segoe UI', 10), pady=30
            ).pack(fill='x')

        self.lbl_counts.configure(
            text='Marek w feedzie: {}   |   nowych: {}   |   '
                 'do zapomnienia: {}'.format(
                     len(available), len(new_brands), len(gone)))
        self.scroll.scroll_top()

    def _section(self, parent, text, bg, fg):
        tk.Label(parent, text=text, bg=bg, fg=fg, anchor='w',
                 font=('Segoe UI', 9, 'bold'), padx=12, pady=5).pack(fill='x')

    def _add_row(self, parent, brand, is_new, index):
        cfg = self.brands_cfg.get(brand, {})
        row = BrandRow(
            parent, brand,
            enabled=bool(cfg.get('enabled', False)),
            margin=float(cfg.get('margin', 0)),
            is_new=is_new,
            bg=C_CARD if index % 2 == 0 else C_ROW_ALT)
        row.pack(fill='x')
        self.rows.append(row)

    def _harvest_rows(self, strict=True):
        """Przepisuje stan widgetów do self.brands_cfg.

        strict=True zwraca wiersz z niepoprawną marżą (używane przy zapisie),
        strict=False po cichu pomija błędny wpis (przy przerysowaniu listy).
        """
        for row in self.rows:
            margin = row.margin_value()
            if margin is None:
                if strict:
                    return row
                continue
            self.brands_cfg[row.brand] = {
                'enabled': bool(row.var_enabled.get()),
                'margin': margin,
            }
        return None

    def _render_preview(self):
        for item in self.tree_preview.get_children():
            self.tree_preview.delete(item)
        for brand, margin in self._enabled_pairs():
            self.tree_preview.insert(
                '', 'end', values=(brand, '{:g} %'.format(margin)))

    def _enabled_pairs(self):
        return [
            (name, entry['margin'])
            for name, entry in sorted(
                self.brands_cfg.items(), key=lambda kv: kv[0].lower())
            if entry.get('enabled')
        ]

    # --- akcje -------------------------------------------------------------

    def _on_save(self):
        bad = self._harvest_rows(strict=True)
        if bad is not None:
            messagebox.showerror(
                'Błędną marżą',
                'Marka „{}” ma niepoprawna marża.\n\n'
                'Podaj liczbę z zakresu od 0 do 99,99.'.format(bad.brand),
                parent=self)
            bad.spin.focus_set()
            return

        # zapomnij marki, których nie ma już w feedzie
        if self.available_brands:
            available = set(self.available_brands)
            self.brands_cfg = {
                name: entry for name, entry in self.brands_cfg.items()
                if name in available
            }

        if not self._enabled_pairs():
            if not messagebox.askyesno(
                    'Pusta konfiguracja',
                    'Nie zaznaczono żadnej marki – output.csv będzie pusty.'
                    '\n\nZapisać mimo to?', parent=self):
                return

        save_config(self.interval_min, self.brands_cfg)
        self._show_running()
        self._run_job()

    def _on_apply_interval(self):
        raw = self.var_interval.get().strip().replace(',', '.')
        try:
            value = int(float(raw))
        except ValueError:
            value = -1
        if not MIN_INTERVAL_MIN <= value <= MAX_INTERVAL_MIN:
            messagebox.showerror(
                'Błędny interwał',
                'Podaj liczbę minut z zakresu od {} do {}.'.format(
                    MIN_INTERVAL_MIN, MAX_INTERVAL_MIN), parent=self)
            self.var_interval.set(str(self.interval_min))
            return

        self.interval_min = value
        self.var_interval.set(str(value))
        save_config(self.interval_min, self.brands_cfg)
        self._schedule_next()
        self._status('Interwał ustawiony na {} min.'.format(value), C_OK)

    # --- cykl pracy --------------------------------------------------------

    def _run_job(self, initial=False):
        """Startuje cykl w wątku roboczym, żeby nie blokować interfejsu.

        W trybie edycji pobieramy sam feed (odświeżenie listy marek),
        w trybie pracy dodatkowo generujemy output.csv.
        """
        if self._closing:
            return
        if self.busy:
            # cykl już trwa – zlecamy powtórkę zaraz po jego zakończeniu,
            # żeby wejście w edycję nigdy nie zostało bez świeżej listy
            self._rerun = True
            return
        self.busy = True

        generate = self.mode == 'running'
        enabled = self._enabled_pairs() if generate else None

        self._status('Pobieranie feedu…', C_MUTED)
        self.jobs.put((generate, enabled, initial))

    def _job_worker(self):
        """Pętla trwałego wątku roboczego – zdejmuje zlecenia z self.jobs."""
        while True:
            job = self.jobs.get()
            if job is None:          # sentinel przy zamykaniu aplikacji
                return
            generate, enabled, initial = job
            try:
                tree = fetch_feed()
                brands = extract_brands(tree)
                rows = None
                if generate:
                    rows = write_csv(build_main_transform(enabled)(tree))
                self.results.put((brands, rows, initial, None))
            except Exception as exc:  # noqa: BLE001 – komunikat trafia do UI
                self.results.put((None, None, initial, exc))

    def _poll_queue(self):
        """Odbiera wyniki wątku roboczego w wątku głównym Tk."""
        if self._closing:
            return
        try:
            while True:
                self._job_done(*self.results.get_nowait())
        except queue.Empty:
            pass
        self._schedule('poll', 100, self._poll_queue)

    def _job_done(self, brands, rows, initial, error):
        self.busy = False
        self._schedule_next()

        if error is not None:
            self._status('Błąd: {}'.format(error), C_ERR)
            self._rerun_if_requested()
            return

        changed = brands != self.available_brands
        self.available_brands = brands
        stamp = time.strftime('%H:%M:%S')

        if rows is None:
            self._status('Pobrano feed – {} marek, o {}.'.format(
                len(brands), stamp), C_OK)
        else:
            self._status(
                'Zapisano output.csv – {} rekordów, {} marek w feedzie, '
                'o {}.'.format(rows, len(brands), stamp), C_OK)
            self.lbl_last.configure(
                text='Ostatni zapis: {} ({} rekordów)'.format(stamp, rows))

        # w trybie edycji przerysowujemy listę tylko wtedy, gdy zestaw marek
        # faktycznie się zmienił – inaczej odświeżanie w tle przestawiałoby
        # widok pod palcami użytkownika
        if self.mode == 'edit' and (changed or initial):
            self._render_rows()
            if initial and not self.brands_cfg:
                self._status(
                    'Pobrano {} marek. Zaznacz te, które mają trafić do CSV.'
                    .format(len(brands)), C_ACCENT)

        self._rerun_if_requested()

    def _rerun_if_requested(self):
        """Domyka cykl zlecony w trakcie poprzedniego (np. klik „Edytuj”)."""
        if self._rerun:
            self._rerun = False
            self._run_job()

    def _schedule_next(self):
        self.next_run = time.time() + self.interval_min * 60

    def _tick(self):
        if self._closing:
            return
        if self.next_run is not None:
            left = int(round(self.next_run - time.time()))
            if left <= 0:
                self.var_countdown.set('00:00')
                if not self.busy:
                    self._run_job()
            else:
                self.var_countdown.set(
                    '{:02d}:{:02d}'.format(left // 60, left % 60))
        self._schedule('tick', 1000, self._tick)

    def _status(self, text, color=C_MUTED):
        self.var_status.set(text)
        self.lbl_status.configure(fg=color)


def main():
    for path in (XSLT_MAIN, XSLT_BRANDS):
        if not os.path.exists(path):
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                'Brak pliku',
                'Nie znaleziono szablonu:\n{}\n\n'
                'Uruchom aplikację z katalogu, w którym leżą szablony XSLT.'
                .format(path))
            sys.exit(1)

    AraApp().mainloop()
    # wątki robocze są demonami – proces kończy się wraz z zamknięciem okna
    sys.exit(0)


if __name__ == '__main__':
    main()
