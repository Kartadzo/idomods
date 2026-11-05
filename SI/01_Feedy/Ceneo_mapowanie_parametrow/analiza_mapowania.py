# -*- coding: utf-8 -*-
"""Analiza mapowania parametrow CSV -> atrybuty Ceneo (galaz Ksiegarnia).

Wejscie (z katalogu skryptu):
  export_parametrów.csv  - eksport IdoSell: @id ; /parameters/parameter@textid[pol]
  atrybuty.xml           - drzewo kategorii + atrybutow Ceneo

Wyjscie:
  raport_mapowania.md    - tabela zbiorcza, probki wartosci, luki pokrycia
"""
import csv, collections, random, re, io, os

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "raport_mapowania.md")
csv.field_size_limit(10 ** 9)
random.seed(20260818)

PROBKA = 36     # ile losowych wartosci pokazac na parametr
K = 400         # rozmiar rezerwuaru probkowania

# ---------- 1. CSV: czestosc parametrow + probki wartosci ----------
names = collections.Counter()
values = collections.defaultdict(list)
seen = collections.Counter()
razem_z_produktem = collections.Counter()   # wspolwystepowanie par (do wykrycia duplikatow)

with open(os.path.join(BASE, "export_parametrów.csv"), encoding="utf-8", newline="") as f:
    r = csv.reader(f)
    next(r)
    products = 0
    for row in r:
        products += 1
        if len(row) < 2:
            continue
        w_produkcie = set()
        for line in row[1].split("\n"):
            line = line.strip()
            if not line or "\\" not in line:
                continue
            n, v = line.split("\\", 1)
            n, v = n.strip(), v.strip()
            if not v:
                continue
            names[n] += 1
            seen[n] += 1
            w_produkcie.add(n)
            buf = values[n]
            if len(buf) < K:
                buf.append(v)
            else:
                j = random.randrange(seen[n])
                if j < K:
                    buf[j] = v
        for a in ("Strony", "Elementy", "Autorzy", "Redakcja"):
            if a in w_produkcie:
                razem_z_produktem[a] += 1
        if {"Strony", "Elementy"} <= w_produkcie:
            razem_z_produktem["Strony+Elementy"] += 1
        if {"Autorzy", "Redakcja"} <= w_produkcie:
            razem_z_produktem["Autorzy+Redakcja"] += 1
        if "Redakcja" in w_produkcie and "Autorzy" not in w_produkcie:
            razem_z_produktem["Redakcja bez Autorzy"] += 1

TOP = [n for n, _ in names.most_common()]     # wszystkie 49 nazw

# ---------- 2. Ceneo: atrybuty w galezi Ksiegarnia ----------
import xml.etree.ElementTree as ET
root = ET.parse(os.path.join(BASE, "atrybuty.xml")).getroot()

ceneo = {}            # atrybuty w galezi Ksiegarnia
ceneo_all = {}        # cale drzewo Ceneo

def walk(node, path):
    for c in node:
        if c.tag != "Category":
            continue
        nm, cid = c.findtext("Name"), c.findtext("Id")
        p = path + [nm]
        sub = c.find("Subcategories")
        if sub is None:
            continue
        a = sub.find("Attributes")
        if a is not None:
            for x in a:
                an = (x.findtext("Name") or "").strip()
                av = (x.findtext("Value") or "").strip()
                ak = x.findtext("IsKeyAttribute") == "True"
                stores = [ceneo_all] + ([ceneo] if p and p[0] == "Księgarnia" else [])
                for store in stores:
                    d = store.setdefault(an, {"sample": set(), "cats": []})
                    if av:
                        d["sample"].add(av)
                    d["cats"].append((cid, " > ".join(p), ak))
        walk(sub, p)

walk(root, [])

# ---------- 3. klasyfikacja typu ----------
RE_INT   = re.compile(r"^\d+$")
RE_DEC   = re.compile(r"^\d+[.,]\d+$")
RE_YEAR  = re.compile(r"^(1[5-9]\d{2}|20\d{2})$")
RE_DATE  = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_UNIT  = re.compile(r"^\d+([.,]\d+)?\s*(mm|cm|m|g|kg|ml|l|szt|str|GB|MB)\.?$", re.I)
RE_DIM   = re.compile(r"^\d+([.,]\d+)?\s*[x×]\s*\d+([.,]\d+)?(\s*[x×]\s*\d+([.,]\d+)?)?\s*(mm|cm|m)?$", re.I)
RE_ISBN  = re.compile(r"^[\d\-xX]{10,17}$")
RE_WIEK  = re.compile(r"^\d+\s*(m|lat|lata)?\s*\+$|^\d+\s*-\s*\d+$", re.I)
BOOL = {"tak", "nie", "true", "false", "t", "n"}

def kind(v):
    lv = v.lower()
    if lv in BOOL:        return "bool"
    if RE_DATE.match(v):  return "data"
    if RE_YEAR.match(v):  return "rok"
    if RE_INT.match(v):   return "int"
    if RE_DEC.match(v):   return "dec"
    if RE_DIM.match(v):   return "wymiar"
    if RE_UNIT.match(v):  return "liczba+jednostka"
    if RE_WIEK.match(v):  return "przedział wieku"
    if RE_ISBN.match(v):  return "isbn"
    if len(v) > 60:       return "tekst długi"
    return "tekst"

def profile(vals):
    c = collections.Counter(kind(v) for v in vals)
    tot = sum(c.values())
    return [(k, n, round(100 * n / tot)) for k, n in c.most_common()]

# ---------- 4. dopasowanie nazw ----------
def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower()
                  .replace("ą","a").replace("ć","c").replace("ę","e").replace("ł","l")
                  .replace("ń","n").replace("ó","o").replace("ś","s")
                  .replace("ź","z").replace("ż","z"))

# reczne synonimy CSV -> Ceneo; ustalenia z uzytkownikiem:
#  - Oprawa zawsze jako "Okładka" (nie rozstrzygamy po nosniku)
#  - Redakcja -> Autor tylko jako fallback, gdy produkt nie ma "Autorzy"
SYN = {
    "Autorzy": "Autor",
    "Redakcja": "Autor",
    "Strony": "Ilość stron",
    "Elementy": "Ilość stron",
    "Liczba elementów": "Ilość stron",
    "Ilość stron": "Ilość stron",
    "Oprawa": "Okładka",
    "Język publikacji": "Język",
    "Język nauczany": "Język",
    "Nośnik": "Format",
    "Format pliku": "Format",
    "Długość audio": "Format",
    "Grupa wiekowa": "Wiek",
    "Minimalny wiek": "Wiek",
    "Liczba tomów": "Zestaw",
    "Producent": "Wydawnictwo",
}

ceneo_norm = {norm(k): k for k in ceneo}
ceneo_all_norm = {norm(k): k for k in ceneo_all}

import difflib

rows = []
for n in TOP:
    vals = values[n]
    smp = random.sample(vals, min(PROBKA, len(vals)))
    prof = profile(vals)

    # synonim ma pierwszenstwo przed nazwa wlasna: "Oprawa" ma isc do "Okładka",
    # a nie do istniejacego (pustego) atrybutu "Oprawa" z E-bookow/Audiobookow
    match, how = None, ""
    if n in SYN and norm(SYN[n]) in ceneo_norm:
        match, how = ceneo_norm[norm(SYN[n])], "synonim (Księgarnia)"
    elif norm(n) in ceneo_norm:
        match, how = ceneo_norm[norm(n)], "dokładne (Księgarnia)"
    elif norm(n) in ceneo_all_norm:
        match, how = ceneo_all_norm[norm(n)], "poza Księgarnią"
    elif n in SYN and norm(SYN[n]) in ceneo_all_norm:
        match, how = ceneo_all_norm[norm(SYN[n])], "synonim, poza Księgarnią"

    blisko = ""
    if not match:
        cand = difflib.get_close_matches(norm(n), list(ceneo_norm), n=2, cutoff=0.7)
        blisko = ", ".join(ceneo_norm[c] for c in cand)

    ce_sample, ce_cats, ce_kinds = [], [], []
    if match:
        d = (ceneo if match in ceneo else ceneo_all)[match]
        ce_sample = sorted(d["sample"])
        ce_cats = d["cats"]
        ce_kinds = sorted({kind(v) for v in ce_sample})

    if not match:
        verd = "❌ brak w Ceneo"
    elif "poza" in how:
        verd = "⚠️ nie w Księgarni"
    elif not ce_kinds:
        verd = "➖ brak próbki Ceneo"
    elif prof[0][0] in ce_kinds:
        verd = "✅ typ zgodny"
    else:
        verd = "⚠️ typ różny"

    rows.append(dict(param=n, cnt=names[n], uniq=len(set(vals)), prof=prof, sample=smp,
                     match=match, how=how, ce_sample=ce_sample, ce_kinds=ce_kinds,
                     ce_cats=ce_cats, verd=verd, blisko=blisko))

pokryte = {r_["match"] for r_ in rows if r_["match"] and "poza" not in r_["how"]}

# ---------- 5. raport ----------
with io.open(OUT, "w", encoding="utf-8") as o:
    w = o.write
    w("# Analiza mapowania parametrów CSV → atrybuty Ceneo\n\n")
    w("Produktów w CSV: **%d** · par parametr\\wartość: **%d** · "
      "unikalnych nazw parametrów: **%d** (mniej niż żądane 60 — to komplet)\n\n"
      % (products, sum(names.values()), len(names)))
    w("Atrybutów Ceneo w gałęzi `Księgarnia`: **%d** unikalnych nazw w %d kategoriach.\n\n"
      % (len(ceneo), len({c for d in ceneo.values() for c, _, _ in d["cats"]})))

    w("## Współwystępowanie (rozstrzyga kolejność w XSLT)\n\n")
    for k in ("Strony", "Elementy", "Strony+Elementy", "Autorzy", "Redakcja",
              "Autorzy+Redakcja", "Redakcja bez Autorzy"):
        w("- `%s` — %d produktów\n" % (k, razem_z_produktem[k]))
    w("\n")

    w("## Tabela zbiorcza — wszystkie %d parametrów\n\n" % len(rows))
    w("| # | Parametr CSV | Wystąpień | Unikalnych | Typ w CSV | Atrybut Ceneo | Dopasowanie | "
      "Typ w Ceneo | Werdykt | Podobne w Ceneo |\n")
    w("|---|---|---:|---:|---|---|---|---|---|---|\n")
    for i, r_ in enumerate(rows, 1):
        pk = ", ".join("%s %d%%" % (k, p) for k, _, p in r_["prof"][:3])
        w("| %d | %s | %d | %d | %s | %s | %s | %s | %s | %s |\n" %
          (i, r_["param"], r_["cnt"], r_["uniq"], pk, r_["match"] or "—",
           r_["how"] or "—", ", ".join(r_["ce_kinds"]) or "—", r_["verd"], r_["blisko"] or "—"))

    w("\n## Luka pokrycia — atrybuty Księgarni, których nie zasila żaden parametr CSV\n\n")
    w("| Atrybut Ceneo | Kategorii | Kluczowy w | Wzorcowe wartości |\n|---|---:|---:|---|\n")
    for k in sorted(set(ceneo) - pokryte,
                    key=lambda x: -sum(1 for _, _, y in ceneo[x]["cats"] if y)):
        d = ceneo[k]
        w("| %s | %d | %d | %s |\n" % (k, len(d["cats"]), sum(1 for _, _, y in d["cats"] if y),
          ", ".join(sorted(d["sample"])[:6]) or "—"))

    w("\n## Szczegóły — %d losowych wartości na parametr\n\n" % PROBKA)
    for i, r_ in enumerate(rows, 1):
        w("### %d. `%s` — %d wystąpień, %d unikalnych wartości\n\n"
          % (i, r_["param"], r_["cnt"], r_["uniq"]))
        w("- **Profil typu:** %s\n" % ", ".join("`%s` %d%%" % (k, p) for k, _, p in r_["prof"]))
        if r_["match"]:
            cats = r_["ce_cats"]
            w("- **Atrybut Ceneo:** `%s` (%s) — w %d kategoriach, kluczowy w %d\n"
              % (r_["match"], r_["how"], len(cats), sum(1 for _, _, y in cats if y)))
            w("- **Wzorcowe wartości Ceneo:** %s\n"
              % (", ".join("`%s`" % v for v in r_["ce_sample"][:12]) or "_brak (pusty Value)_"))
            w("- **Przykładowe kategorie:** %s\n" % "; ".join("%s (%s)" % (p, c) for c, p, _ in cats[:3]))
        else:
            w("- **Atrybut Ceneo:** brak odpowiednika%s\n"
              % (" (najbliższe nazwy: %s)" % r_["blisko"] if r_["blisko"] else ""))
        w("- **Wszystkie unikalne wartości:** %s\n" % (
            ", ".join("`%s`" % v for v in sorted(set(values[r_["param"]]))[:25])
            if r_["uniq"] <= 25 else "_(%d różnych — poniżej losowa próbka)_" % r_["uniq"]))
        w("- **%d losowych wartości z CSV:** %s\n\n"
          % (PROBKA, ", ".join("`%s`" % v.replace("|", "\\|")[:50] for v in r_["sample"])))

    w("\n## Atrybuty Ceneo w gałęzi Księgarnia — pełna lista\n\n")
    w("| Atrybut | Kategorii | Kluczowy w | Zasilany z CSV | Wzorcowe wartości |\n|---|---:|---:|---|---|\n")
    for k in sorted(ceneo):
        d = ceneo[k]
        src = ", ".join(r_["param"] for r_ in rows if r_["match"] == k and "poza" not in r_["how"])
        w("| %s | %d | %d | %s | %s |\n" % (k, len(d["cats"]),
          sum(1 for _, _, y in d["cats"] if y), src or "—",
          ", ".join(sorted(d["sample"])[:8]) or "—"))

print("OK ->", OUT)
