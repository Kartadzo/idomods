# -*- coding: utf-8 -*-
"""
Porownywarka dwoch plikow XML (feedy produktowe).

Obsluguje dowolny format oparty o powtarzalny rekord produktu:
  - IOF / IdoSell        -> <offer>/<products>/<product> (takze zapakowane w <rss><channel>)
  - Google Shopping RSS  -> <rss>/<channel>/<item> z <g:id>
  - Facebook / Atom      -> <feed>/<entry>
  - Ceneo                -> <offers>/<o>
  - Heureka              -> <SHOP>/<SHOPITEM>
  - inne                 -> automatyczne wykrycie powtarzalnego elementu

Porownanie jest generyczne: kazdy rekord jest splaszczany do mapy
"sciezka -> wartosc" (wraz z atrybutami), wiec dziala niezaleznie od formatu.

Pliki czytane sa strumieniowo (iterparse), a szczegoly roznic trzymane sa
w tymczasowej bazie sqlite, wiec pliki rzedu setek MB nie mieszcza sie w RAM,
ale i tak zostana porownane.

Wynik: differences.csv + report.html
"""

import os
import sys
import csv
import json
import html
import hashlib
import sqlite3
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter, OrderedDict

CSV_OUT = "differences.csv"
HTML_OUT = "report.html"

# Domyslne limity raportu (uzytkownik moze zmienic w kreatorze)
DEFAULT_HTML_PRODUCTS = 300
DEFAULT_HTML_MISSING = 500

# Wartosc dluzsza niz ponizsza zostanie skrocona w raporcie HTML
MAX_VALUE_LEN = 400

# Znane formaty: (tag rekordu, nazwa formatu, kandydaci na identyfikator)
# Kandydat: ("attr", nazwa_atrybutu) albo ("child", sciezka_dziecka)
KNOWN_FORMATS = [
    ("product",  "IOF / IdoSell (product)",   [("attr", "id"), ("attr", "code_on_card"), ("child", "code")]),
    ("item",     "Google Shopping RSS (item)", [("child", "g:id"), ("child", "id"), ("attr", "id"), ("child", "guid")]),
    ("entry",    "Atom / Facebook (entry)",   [("child", "g:id"), ("child", "id")]),
    ("o",        "Ceneo (o)",                 [("attr", "id")]),
    ("SHOPITEM", "Heureka (SHOPITEM)",        [("child", "ITEM_ID"), ("attr", "id")]),
    ("offer",    "Generyczny (offer)",        [("attr", "id"), ("child", "id")]),
    ("oferta",   "Generyczny (oferta)",       [("attr", "id"), ("child", "id")]),
]

FALLBACK_ID_CANDIDATES = [("attr", "id"), ("child", "id"), ("child", "g:id"),
                          ("attr", "code"), ("child", "code"), ("attr", "sku")]

# Atrybuty uzywane jako klucz przy rozroznianiu powtarzajacego sie rodzenstwa
SIBLING_KEY_ATTRS = ["id", "size_id", "code", "name", "textId", "lang", "type"]


# ---------------------------------------------------------------------------
# Obsluga przestrzeni nazw
# ---------------------------------------------------------------------------

def read_namespaces(path):
    """Zwraca mape {uri: prefix} zadeklarowana w pliku (pierwsze deklaracje)."""
    prefixes = {}
    try:
        for event, data in ET.iterparse(path, events=("start-ns", "start")):
            if event == "start-ns":
                prefix, uri = data
                if uri not in prefixes:
                    prefixes[uri] = prefix or ""
            else:
                # deklaracje przestrzeni nazw sa emitowane przed pierwszym elementem
                break
    except ET.ParseError:
        pass
    return prefixes


def qname(tag, prefixes):
    """{uri}tag -> prefix:tag (albo sam tag, gdy brak przestrzeni nazw)."""
    if tag.startswith("{"):
        uri, local = tag[1:].split("}", 1)
        prefix = prefixes.get(uri, "")
        return "%s:%s" % (prefix, local) if prefix else local
    return tag


def local_name(tag):
    return tag.split("}", 1)[1] if tag.startswith("{") else tag


# ---------------------------------------------------------------------------
# Strumieniowe czytanie rekordow
# ---------------------------------------------------------------------------

def iter_records(path, record_local_tag):
    """Strumieniowo zwraca elementy o podanej nazwie lokalnej, czyszczac pamiec."""
    stack = []
    context = ET.iterparse(path, events=("start", "end"))
    for event, elem in context:
        if event == "start":
            stack.append(elem)
            continue
        stack.pop()
        if local_name(elem.tag) != record_local_tag:
            continue
        yield elem
        elem.clear()
        if stack:
            parent = stack[-1]
            # rekord jest juz przetworzony, usuwamy go z rodzica, zeby drzewo nie roslo
            try:
                parent.remove(elem)
            except ValueError:
                pass


def detect_format(path, scan_limit=30000):
    """Wykrywa tag rekordu. Zwraca (tag, nazwa_formatu, kandydaci_id)."""
    counts = Counter()
    depths = {}
    depth = 0
    scanned = 0
    for event, elem in ET.iterparse(path, events=("start", "end")):
        if event == "start":
            depth += 1
            continue
        tag = local_name(elem.tag)
        counts[tag] += 1
        if tag not in depths or depth < depths[tag]:
            depths[tag] = depth
        depth -= 1
        scanned += 1
        if scanned >= scan_limit:
            break
        elem.clear()

    # najpierw znane formaty - wygrywa ten, ktory lezy najplycej
    known_hits = [(depths[tag], idx, tag, name, ids)
                  for idx, (tag, name, ids) in enumerate(KNOWN_FORMATS)
                  if counts.get(tag, 0) >= 2]
    if known_hits:
        known_hits.sort()
        _, _, tag, name, ids = known_hits[0]
        return tag, name, ids

    # fallback: najplytszy powtarzalny element (pomijamy korzen i jego rodzica)
    repeated = [(depths[t], -c, t) for t, c in counts.items() if c >= 2 and depths[t] >= 2]
    if not repeated:
        return None, None, None
    repeated.sort()
    tag = repeated[0][2]
    return tag, "Wykryty automatycznie (<%s>)" % tag, FALLBACK_ID_CANDIDATES


# ---------------------------------------------------------------------------
# Splaszczanie rekordu do mapy sciezka -> wartosc
# ---------------------------------------------------------------------------

def norm_text(value):
    return " ".join(value.split()) if value else ""


def id_attr_value(elem):
    """Wartosc atrybutu identyfikujacego element wsrod rodzenstwa (albo None)."""
    for attr in SIBLING_KEY_ATTRS:
        for key, val in elem.attrib.items():
            if local_name(key) == attr and val.strip():
                return norm_text(val)
    return None


def is_simple_leaf(elem):
    """Element bez dzieci i bez atrybutow - czysta wartosc tekstowa."""
    return len(elem) == 0 and not elem.attrib


def flatten_record(record, prefixes):
    """Zwraca OrderedDict {sciezka: wartosc} dla calego rekordu.

    Zasady budowania sciezek (tak, zeby byly stabilne miedzy plikami):
      - atrybuty:                        sciezka/@nazwa
      - element z atrybutem id/code/...: tag[wartosc_id]/...
      - powtarzalne elementy bez id:     tag[1], tag[2], ...
      - powtarzalne czyste wartosci:     jedna sciezka, wartosci laczone " | "
    """
    out = OrderedDict()

    def walk_children(parent, prefix):
        groups = OrderedDict()
        for child in parent:
            groups.setdefault(qname(child.tag, prefixes), []).append(child)

        for name, group in groups.items():
            # lista prostych wartosci (np. additional_image_link) -> jedno pole
            if all(is_simple_leaf(c) for c in group):
                out[prefix + name] = " | ".join(norm_text(c.text) for c in group)
                continue
            for index, child in enumerate(group, 1):
                # klucz dodajemy tylko przy powtorzeniach - pojedynczy element
                # zostaje bez nawiasu, zeby sciezki byly czytelne
                if len(group) > 1:
                    key = id_attr_value(child) or str(index)
                    label = "%s[%s]" % (name, key)
                else:
                    label = name
                walk(child, prefix + label + "/")

    def walk(elem, prefix):
        for key, val in elem.attrib.items():
            out["%s@%s" % (prefix, qname(key, prefixes))] = norm_text(val)
        text = norm_text(elem.text)
        if text or (len(elem) == 0 and not elem.attrib):
            out[prefix.rstrip("/")] = text
        walk_children(elem, prefix)

    for key, val in record.attrib.items():
        out["@%s" % qname(key, prefixes)] = norm_text(val)
    text = norm_text(record.text)
    if text:
        out["#text"] = text
    walk_children(record, "")

    return out


def path_pattern(path):
    """Sciezka bez kluczy rodzenstwa: sizes/size[uniw]/@code -> sizes/size/@code."""
    out = []
    depth = 0
    for ch in path:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def extract_id(record, flat, id_candidates, prefixes):
    for kind, name in id_candidates:
        if kind == "attr":
            value = flat.get("@%s" % name)
        else:
            value = flat.get(name)
            if value is None:
                # dziecko moglo zostac zapisane z kluczem rodzenstwa
                for key, val in flat.items():
                    if path_pattern(key) == name:
                        value = val
                        break
        if value:
            return value
    return None


# ---------------------------------------------------------------------------
# Filtry pol
# ---------------------------------------------------------------------------

class FieldFilter(object):
    """Decyduje, ktore sciezki biora udzial w porownaniu."""

    def __init__(self, include=None, exclude=None):
        self.include = set(include) if include else None
        self.exclude = set(exclude) if exclude else set()

    def keep(self, path):
        pattern = path_pattern(path)
        if self.include is not None and pattern not in self.include:
            return False
        if pattern in self.exclude:
            return False
        return True

    def apply(self, flat):
        if self.include is None and not self.exclude:
            return flat
        return OrderedDict((k, v) for k, v in flat.items() if self.keep(k))


def collect_paths(path, record_tag, prefixes, limit=300):
    """Zbiera wzorce sciezek z pierwszych rekordow - do kreatora wyboru pol."""
    patterns = Counter()
    count = 0
    for record in iter_records(path, record_tag):
        for key in flatten_record(record, prefixes):
            patterns[path_pattern(key)] += 1
        count += 1
        if count >= limit:
            break
    return patterns


# ---------------------------------------------------------------------------
# Przebieg 1 - mapa id -> skrot
# ---------------------------------------------------------------------------

def hash_flat(flat):
    h = hashlib.md5()
    for key in sorted(flat):
        h.update(key.encode("utf-8", "replace"))
        h.update(b"\x00")
        h.update(flat[key].encode("utf-8", "replace"))
        h.update(b"\x01")
    return h.digest()


def build_hash_map(path, record_tag, id_candidates, prefixes, field_filter, label):
    """Zwraca (mapa id->skrot, liczba rekordow, liczba duplikatow, lista bez id)."""
    hashes = {}
    total = 0
    duplicates = 0
    no_id = 0
    for record in iter_records(path, record_tag):
        total += 1
        flat = flatten_record(record, prefixes)
        rid = extract_id(record, flat, id_candidates, prefixes)
        if not rid:
            no_id += 1
            continue
        if rid in hashes:
            duplicates += 1
        hashes[rid] = hash_flat(field_filter.apply(flat))
        if total % 5000 == 0:
            sys.stdout.write("\r  %s: przetworzono %d rekordow..." % (label, total))
            sys.stdout.flush()
    sys.stdout.write("\r  %s: przetworzono %d rekordow.        \n" % (label, total))
    return hashes, total, duplicates, no_id


# ---------------------------------------------------------------------------
# Przebieg 2 - szczegoly roznic
# ---------------------------------------------------------------------------

def store_details(path, record_tag, id_candidates, prefixes, field_filter, wanted, conn, label):
    """Zapisuje splaszczone rekordy o wskazanych ID do bazy tymczasowej."""
    cur = conn.cursor()
    done = 0
    batch = []
    for record in iter_records(path, record_tag):
        flat = flatten_record(record, prefixes)
        rid = extract_id(record, flat, id_candidates, prefixes)
        if not rid or rid not in wanted:
            continue
        batch.append((rid, json.dumps(field_filter.apply(flat), ensure_ascii=False)))
        done += 1
        if len(batch) >= 500:
            cur.executemany("INSERT OR REPLACE INTO recA VALUES (?,?)", batch)
            conn.commit()
            batch = []
            sys.stdout.write("\r  %s: zebrano %d rekordow..." % (label, done))
            sys.stdout.flush()
    if batch:
        cur.executemany("INSERT OR REPLACE INTO recA VALUES (?,?)", batch)
        conn.commit()
    sys.stdout.write("\r  %s: zebrano %d rekordow.        \n" % (label, done))


def diff_flat(flat_a, flat_b):
    """Lista (sciezka, wartosc_A, wartosc_B) dla roznicych sie pol."""
    diffs = []
    keys = list(flat_a.keys())
    keys += [k for k in flat_b.keys() if k not in flat_a]
    for key in keys:
        a = flat_a.get(key)
        b = flat_b.get(key)
        if a == b:
            continue
        diffs.append((key, "" if a is None else a, "" if b is None else b,
                      "brak w B" if b is None else ("brak w A" if a is None else "")))
    return diffs


# ---------------------------------------------------------------------------
# Raporty
# ---------------------------------------------------------------------------

def shorten(value):
    if len(value) > MAX_VALUE_LEN:
        return value[:MAX_VALUE_LEN] + " […]"
    return value


def esc(value):
    return html.escape(value, quote=False)


def generate_html_report(ctx):
    h = []
    add = h.append
    add("<!DOCTYPE html>")
    add("<html lang='pl'><head><meta charset='utf-8'>")
    add("<title>Porównanie XML</title>")
    add("""<style>
body { font-family: Arial, Helvetica, sans-serif; font-size: 14px; margin: 24px; color: #222; }
h1 { font-size: 22px; }
h2 { font-size: 18px; margin-top: 32px; border-bottom: 2px solid #ddd; padding-bottom: 4px; }
h3 { font-size: 15px; margin-top: 24px; margin-bottom: 6px; }
table { border-collapse: collapse; width: 100%; max-width: 1400px; margin-bottom: 18px; }
th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; vertical-align: top;
         word-break: break-word; }
th { background: #f2f2f2; font-weight: bold; }
tr:nth-child(even) { background: #fafafa; }
td.path { width: 24%; font-family: Consolas, monospace; font-size: 12px; }
td.val  { width: 38%; }
.diff td.val { background: #ffe6e6; }
.onlyA td.val { background: #e6f0ff; }
.onlyB td.val { background: #e8f8e8; }
.missing td { background: #fff3cd; }
.meta { color: #666; font-size: 12px; }
.summary td:first-child { width: 60%; }
.badge { display: inline-block; padding: 1px 6px; border-radius: 3px; background: #eee;
         font-size: 11px; color: #555; }
</style>""")
    add("</head><body>")

    add("<h1>Porównanie plików XML</h1>")
    add("<p><strong>Plik A:</strong> %s<br><strong>Plik B:</strong> %s</p>" %
        (esc(ctx["fileA"]), esc(ctx["fileB"])))
    add("<p class='meta'>Format A: %s &nbsp;|&nbsp; Format B: %s &nbsp;|&nbsp; "
        "element rekordu: <code>&lt;%s&gt;</code></p>" %
        (esc(ctx["formatA"]), esc(ctx["formatB"]), esc(ctx["record_tag"])))
    add("<p class='meta'>Zakres porównywanych pól: %s</p>" % esc(ctx["filter_desc"]))

    add("<h2>Podsumowanie</h2>")
    add("<table class='summary'>")
    rows = [
        ("Rekordów w pliku A", ctx["totalA"]),
        ("Rekordów w pliku B", ctx["totalB"]),
        ("Unikalnych ID w pliku A", ctx["uniqueA"]),
        ("Unikalnych ID w pliku B", ctx["uniqueB"]),
        ("ID tylko w pliku A", len(ctx["only_in_A"])),
        ("ID tylko w pliku B", len(ctx["only_in_B"])),
        ("Wspólnych ID", ctx["common"]),
        ("Produkty z różnicami", ctx["diff_count"]),
        ("Produkty identyczne", ctx["common"] - ctx["diff_count"]),
    ]
    if ctx["dupA"] or ctx["dupB"]:
        rows.append(("Zduplikowane ID (A / B)", "%d / %d" % (ctx["dupA"], ctx["dupB"])))
    if ctx["noidA"] or ctx["noidB"]:
        rows.append(("Rekordy bez identyfikatora (A / B)", "%d / %d" % (ctx["noidA"], ctx["noidB"])))
    for name, value in rows:
        add("<tr><td>%s</td><td><strong>%s</strong></td></tr>" % (name, value))
    add("</table>")

    add("<h2>Różnice wg pola</h2>")
    if not ctx["field_stats"]:
        add("<p>Brak różnic w polach.</p>")
    else:
        add("<table><tr><th>Pole (ścieżka)</th><th>Liczba produktów z różnicą</th></tr>")
        for path, count in ctx["field_stats"].most_common():
            add("<tr><td class='path'>%s</td><td>%d</td></tr>" % (esc(path), count))
        add("</table>")

    add("<h2>Brakujące ID</h2>")
    if not ctx["only_in_A"] and not ctx["only_in_B"]:
        add("<p>Oba pliki zawierają ten sam zestaw identyfikatorów.</p>")
    else:
        add("<table><tr><th>ID</th><th>Status</th></tr>")
        shown = 0
        for idv in ctx["only_in_A"]:
            if shown >= ctx["limit_missing"]:
                break
            add("<tr class='missing'><td>%s</td><td>Brak w pliku B</td></tr>" % esc(idv))
            shown += 1
        shown = 0
        for idv in ctx["only_in_B"]:
            if shown >= ctx["limit_missing"]:
                break
            add("<tr class='missing'><td>%s</td><td>Brak w pliku A</td></tr>" % esc(idv))
            shown += 1
        add("</table>")
        if len(ctx["only_in_A"]) > ctx["limit_missing"] or len(ctx["only_in_B"]) > ctx["limit_missing"]:
            add("<p class='meta'>Lista skrócona do %d pozycji na stronę. "
                "Pełny wykaz znajduje się w pliku %s.</p>" % (ctx["limit_missing"], CSV_OUT))

    add("<h2>Różnice w polach dla wspólnych ID</h2>")
    if not ctx["samples"]:
        add("<p><strong>Brak różnic w polach.</strong></p>")
    else:
        for idv, diffs in ctx["samples"]:
            add("<h3>ID: %s <span class='badge'>%d różnic</span></h3>" % (esc(idv), len(diffs)))
            add("<table>")
            add("<tr><th>Pole</th><th>Plik A</th><th>Plik B</th></tr>")
            for path, a, b, status in diffs:
                css = "diff"
                if status == "brak w B":
                    css = "onlyA"
                elif status == "brak w A":
                    css = "onlyB"
                add("<tr class='%s'><td class='path'>%s</td><td class='val'>%s</td>"
                    "<td class='val'>%s</td></tr>" %
                    (css, esc(path), esc(shorten(a)), esc(shorten(b))))
            add("</table>")
        if ctx["diff_count"] > len(ctx["samples"]):
            add("<p class='meta'>Pokazano %d z %d produktów z różnicami. "
                "Komplet znajduje się w pliku %s.</p>" %
                (len(ctx["samples"]), ctx["diff_count"], CSV_OUT))

    add("</body></html>")

    with open(HTML_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(h))


# ---------------------------------------------------------------------------
# Kreator (praca interaktywna)
# ---------------------------------------------------------------------------

def ask(prompt, default=""):
    try:
        value = input(prompt).strip()
    except EOFError:
        return default
    return value or default


def choose_files():
    files = sorted(f for f in os.listdir(".") if f.lower().endswith(".xml"))
    if len(files) < 2:
        print("W folderze muszą znajdować się co najmniej 2 pliki XML.")
        print("Znaleziono:", files if files else "brak")
        return None, None

    if len(files) == 2:
        print("Znalezione pliki XML:")
        print("  A: %s (%s)" % (files[0], human_size(files[0])))
        print("  B: %s (%s)" % (files[1], human_size(files[1])))
        answer = ask("Porównać te pliki? [Enter = tak, z = zamień A z B]: ").lower()
        if answer.startswith("z"):
            return files[1], files[0]
        return files[0], files[1]

    print("Znalezione pliki XML:")
    for i, name in enumerate(files, 1):
        print("  %2d. %s (%s)" % (i, name, human_size(name)))
    a = ask("Numer pliku A [1]: ", "1")
    b = ask("Numer pliku B [2]: ", "2")
    try:
        return files[int(a) - 1], files[int(b) - 1]
    except (ValueError, IndexError):
        print("Nieprawidłowy wybór.")
        return None, None


def human_size(path):
    size = os.path.getsize(path)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return "%.1f %s" % (size, unit)
        size /= 1024.0


def choose_fields(patterns):
    """Zwraca (FieldFilter, opis)."""
    print("\nZakres porównywanych pól:")
    print("  1. wszystkie pola (domyślnie)")
    print("  2. tylko wybrane pola")
    print("  3. wszystkie oprócz wybranych")
    mode = ask("Wybór [1]: ", "1")

    if mode not in ("2", "3"):
        return FieldFilter(), "wszystkie pola"

    ordered = [p for p, _ in patterns.most_common()]
    print("\nWykryte pola (na podstawie pierwszych rekordów):")
    for i, path in enumerate(ordered, 1):
        print("  %3d. %s" % (i, path))
    raw = ask("\nPodaj numery po przecinku (np. 1,4,7) lub fragmenty nazw: ")
    selected = resolve_selection(raw, ordered)
    if not selected:
        print("Nic nie wybrano — porównuję wszystkie pola.")
        return FieldFilter(), "wszystkie pola"

    print("Wybrano %d pól." % len(selected))
    if mode == "2":
        return FieldFilter(include=selected), "tylko wybrane pola (%d)" % len(selected)
    return FieldFilter(exclude=selected), "wszystkie pola oprócz %d wykluczonych" % len(selected)


def resolve_selection(raw, ordered):
    """Zamienia wpis uzytkownika (numery lub fragmenty tekstu) na liste sciezek."""
    selected = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(ordered):
                selected.append(ordered[idx])
        else:
            needle = part.lower()
            selected.extend(p for p in ordered if needle in p.lower())
    # usuwamy duplikaty, zachowujac kolejnosc
    return list(OrderedDict.fromkeys(selected))


def ask_int(prompt, default):
    raw = ask(prompt, str(default))
    try:
        return max(0, int(raw))
    except ValueError:
        return default


# ---------------------------------------------------------------------------
# Glowny przebieg
# ---------------------------------------------------------------------------

def main():
    print("=== Porównywanie dwóch plików XML (feedy produktowe) ===\n")

    fileA, fileB = choose_files()
    if not fileA:
        return

    print("\nPlik A: %s" % fileA)
    print("Plik B: %s" % fileB)

    print("\nWykrywanie formatu...")
    tagA, formatA, idsA_spec = detect_format(fileA)
    tagB, formatB, idsB_spec = detect_format(fileB)

    if not tagA or not tagB:
        print("Nie udało się wykryć powtarzalnego elementu produktu w plikach.")
        return

    if tagA != tagB:
        print("  Plik A: %s" % formatA)
        print("  Plik B: %s" % formatB)
        print("UWAGA: pliki mają różne formaty — porównanie nie będzie miarodajne.")
        if not ask("Kontynuować mimo to? [t/N]: ", "n").lower().startswith("t"):
            return

    record_tag = tagA
    id_candidates = idsA_spec
    print("  Format: %s (element <%s>)" % (formatA, record_tag))

    prefixesA = read_namespaces(fileA)
    prefixesB = read_namespaces(fileB)
    prefixes = dict(prefixesB)
    prefixes.update(prefixesA)

    print("Skanowanie dostępnych pól...")
    patterns = collect_paths(fileA, record_tag, prefixes)
    print("  Wykryto %d różnych pól." % len(patterns))

    field_filter, filter_desc = choose_fields(patterns)

    limit_products = ask_int("\nIle produktów z różnicami pokazać w raporcie HTML [%d]: "
                             % DEFAULT_HTML_PRODUCTS, DEFAULT_HTML_PRODUCTS)
    limit_missing = ask_int("Ile brakujących ID pokazać w raporcie HTML [%d]: "
                            % DEFAULT_HTML_MISSING, DEFAULT_HTML_MISSING)

    print("\n--- Etap 1/3: wczytywanie identyfikatorów ---")
    hashesA, totalA, dupA, noidA = build_hash_map(fileA, record_tag, id_candidates,
                                                  prefixes, field_filter, "plik A")
    hashesB, totalB, dupB, noidB = build_hash_map(fileB, record_tag, id_candidates,
                                                  prefixes, field_filter, "plik B")

    idsA = set(hashesA)
    idsB = set(hashesB)
    only_in_A = sorted(idsA - idsB)
    only_in_B = sorted(idsB - idsA)
    common = idsA & idsB
    diff_ids = set(i for i in common if hashesA[i] != hashesB[i])

    uniqueA, uniqueB, common_count = len(idsA), len(idsB), len(common)
    del hashesA, hashesB, idsA, idsB, common

    print("  Wspólnych ID: %d, z różnicami: %d" % (common_count, len(diff_ids)))
    print("  Tylko w A: %d, tylko w B: %d" % (len(only_in_A), len(only_in_B)))

    field_stats = Counter()
    samples = []
    diff_count = 0

    tmp_db = os.path.join(tempfile.gettempdir(), "compare_xml_%d.sqlite" % os.getpid())
    if os.path.exists(tmp_db):
        os.remove(tmp_db)
    conn = sqlite3.connect(tmp_db)
    conn.execute("CREATE TABLE recA (id TEXT PRIMARY KEY, data TEXT)")
    conn.execute("PRAGMA synchronous=OFF")

    try:
        with open(CSV_OUT, "w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(["ID", "Typ", "Pole", "Plik A", "Plik B"])

            for idv in only_in_A:
                writer.writerow([idv, "tylko w A", "", "", ""])
            for idv in only_in_B:
                writer.writerow([idv, "tylko w B", "", "", ""])

            if diff_ids:
                print("\n--- Etap 2/3: zbieranie szczegółów z pliku A ---")
                store_details(fileA, record_tag, id_candidates, prefixes,
                              field_filter, diff_ids, conn, "plik A")

                print("--- Etap 3/3: porównywanie z plikiem B ---")
                cur = conn.cursor()
                processed = 0
                for record in iter_records(fileB, record_tag):
                    flat_b = flatten_record(record, prefixes)
                    rid = extract_id(record, flat_b, id_candidates, prefixes)
                    if not rid or rid not in diff_ids:
                        continue
                    row = cur.execute("SELECT data FROM recA WHERE id=?", (rid,)).fetchone()
                    if not row:
                        continue
                    flat_a = json.loads(row[0])
                    diffs = diff_flat(flat_a, field_filter.apply(flat_b))
                    if not diffs:
                        continue
                    diff_count += 1
                    for path, a, b, status in diffs:
                        field_stats[path_pattern(path)] += 1
                        if status == "brak w B":
                            typ = "pole tylko w A"
                        elif status == "brak w A":
                            typ = "pole tylko w B"
                        else:
                            typ = "różnica"
                        writer.writerow([rid, typ, path, a, b])
                    if len(samples) < limit_products:
                        samples.append((rid, diffs))
                    processed += 1
                    if processed % 500 == 0:
                        sys.stdout.write("\r  porównano %d / %d produktów..."
                                         % (processed, len(diff_ids)))
                        sys.stdout.flush()
                sys.stdout.write("\r  porównano %d produktów.            \n" % processed)
    finally:
        conn.close()
        try:
            os.remove(tmp_db)
        except OSError:
            pass

    generate_html_report({
        "fileA": fileA, "fileB": fileB,
        "formatA": formatA, "formatB": formatB,
        "record_tag": record_tag,
        "filter_desc": filter_desc,
        "totalA": totalA, "totalB": totalB,
        "uniqueA": uniqueA, "uniqueB": uniqueB,
        "dupA": dupA, "dupB": dupB,
        "noidA": noidA, "noidB": noidB,
        "only_in_A": only_in_A, "only_in_B": only_in_B,
        "common": common_count,
        "diff_count": diff_count,
        "field_stats": field_stats,
        "samples": samples,
        "limit_missing": limit_missing,
    })

    print("\n=== Gotowe ===")
    print("Rekordów: A = %d, B = %d" % (totalA, totalB))
    print("Brak w %s: %d" % (fileB, len(only_in_A)))
    print("Brak w %s: %d" % (fileA, len(only_in_B)))
    print("Produkty z różnicami: %d" % diff_count)
    if field_stats:
        print("Najczęściej różniące się pola:")
        for path, count in field_stats.most_common(10):
            print("  %-45s %d" % (path, count))
    print("\nWynik zapisany w %s oraz %s" % (CSV_OUT, HTML_OUT))


if __name__ == "__main__":
    main()
