# -*- coding: utf-8 -*-
"""
Własna historia zmian sterowników XSLT w panelu IdoSell.

Panel nie zapisuje, kto i kiedy zmienił sterownik serwisu, a feed pokazuje
zmianę z opóźnieniem kilku godzin. Ten skrypt prowadzi historię po naszej
stronie: zrzuty hashy sterowników wszystkich serwisów, kopie treści do
przywrócenia, dziennik wdrożeń i kontrolę przed zamknięciem projektu.
Analiza i pułapki panelu: Zmiany_sterownikow/ANALIZA_historia_sterownikow.md.

Dane klienta: Zmiany_sterownikow/<klient>/
  _historia/<RRRR-MM-DD_GGMMSS>_<rodzaj>.json   zrzuty (do gita, same hashe)
  _historia/kopie/<shop>_<id>_<sha12>.xml        treści (poza gitem)
  _historia/_robocze/<sesja>/shop<n>.json        części od przeglądarki (poza gitem)
  _historia/wyjatki_duplikatow.json              [[id, id], ...] pary zamierzone
  dziennik_wdrozen.csv                           jeden wiersz na wgranie

Polecenia (bez argumentów: menu po dwukliku run_historia.bat):
  odbiornik [--port 8765]                 serwer na 127.0.0.1 dla zrzut_panel.js
  sesja --rodzaj <rodzaj>                 wypisuje nazwę nowej sesji zrzutu
  zloz --klient K --sesja S [--zadanie Z] składa zrzut z części i porównuje
  porownaj --klient K [--od P] [--do P]   porównanie dwóch zrzutów (domyślnie 2 ostatnie)
  dziennik --klient K --shop N --id ID --plik P --wgrywa Claude|użytkownik [--zadanie Z]
  kontrola --klient K [--od P]            przebieg kontrolny do /zamknij
  hash --plik P                           SHA-256 po normalizacji (jak w panelu)
  waliduj --plik P                        XML + kompilacja XSLT (lxml, gdy jest)
Wspólne: --baza <katalog> zamiast Zmiany_sterownikow (testy).

Kody wyjścia: 0 = OK, 1 = ostrzeżenia lub problemy, 2 = błąd wejścia.
"""

import argparse
import csv
import datetime
import glob
import hashlib
import json
import os
import re
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KATALOG_SKRYPTU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(KATALOG_SKRYPTU), "porownaj_sterownik"))
from porownaj_sterownik import normalizuj, skrot, czytaj_plik, wyglada_na_xslt  # noqa: E402

PORT = 8765
RODZAJE = ("start", "przed_wgraniem", "po_wgraniu", "zapis", "koniec", "reczny")
WGRYWA = ("Claude", "użytkownik")
KOLUMNY_DZIENNIKA = ["czas_wgrania", "wgrywa", "shop", "id_serwisu", "nazwa_serwisu",
                     "plik_lokalny", "sha256_przed", "sha256_po", "sha256_pliku",
                     "zgodne_po_zapisie", "zadanie"]
WZOR_NAZWY = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
LIMIT_TRESCI = 20 * 1024 * 1024
BAZA = os.path.dirname(os.path.dirname(KATALOG_SKRYPTU))  # Zmiany_sterownikow


# ---------------------------------------------------------------- ścieżki

def teraz():
    return datetime.datetime.now().astimezone().replace(microsecond=0)


def katalog_klienta(klient):
    if not WZOR_NAZWY.match(klient or ""):
        raise ValueError(f"niedozwolona nazwa klienta: {klient!r}")
    return os.path.join(BAZA, klient)


def katalog_historii(klient):
    return os.path.join(katalog_klienta(klient), "_historia")


def zapisz_json(sciezka, dane):
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    with open(sciezka, "w", encoding="utf-8", newline="\n") as plik:
        json.dump(dane, plik, ensure_ascii=False, indent=1)
        plik.write("\n")


def czytaj_json(sciezka):
    with open(sciezka, encoding="utf-8") as plik:
        return json.load(plik)


def zrzuty(klient):
    """Ścieżki zrzutów klienta od najstarszego."""
    return sorted(glob.glob(os.path.join(katalog_historii(klient), "20*_*.json")))


def sha_pliku(sciezka):
    tekst, _ = czytaj_plik(sciezka)
    return skrot(normalizuj(tekst))


# ---------------------------------------------------------------- odbiornik

class Odbiornik(BaseHTTPRequestHandler):
    """Przyjmuje dane z karty Chrome z panelem. Słucha tylko na 127.0.0.1."""

    def log_message(self, fmt, *args):
        print(f"[{teraz():%H:%M:%S}] {self.command} {self.path.split('?')[0]} {args[1] if len(args) > 1 else ''}")

    def _naglowki(self, kod, typ="text/plain; charset=utf-8"):
        self.send_response(kod)
        self.send_header("Content-Type", typ)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.end_headers()

    def _odpowiedz(self, kod, tekst, typ="text/plain; charset=utf-8"):
        self._naglowki(kod, typ)
        self.wfile.write(tekst.encode("utf-8"))

    def _parametry(self):
        return {k: v[0] for k, v in urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).items()}

    def do_OPTIONS(self):
        self._naglowki(204)

    def do_GET(self):
        sciezka = urllib.parse.urlparse(self.path).path
        p = self._parametry()
        try:
            if sciezka == "/ping":
                return self._odpowiedz(200, "OK historia_sterownikow")
            if sciezka == "/zrzut_panel.js":
                with open(os.path.join(KATALOG_SKRYPTU, "zrzut_panel.js"), encoding="utf-8") as plik:
                    return self._odpowiedz(200, plik.read(), "application/javascript; charset=utf-8")
            if sciezka == "/kopie":
                katalog = os.path.join(katalog_historii(p.get("klient", "")), "kopie")
                znane = []
                for nazwa in (os.listdir(katalog) if os.path.isdir(katalog) else []):
                    if nazwa.endswith(".xml"):
                        tekst, _ = czytaj_plik(os.path.join(katalog, nazwa))
                        znane.append(skrot(normalizuj(tekst)))
                return self._odpowiedz(200, json.dumps(sorted(set(znane))), "application/json")
        except Exception as blad:  # odpowiedź zamiast zerwanego połączenia
            return self._odpowiedz(400, f"BŁĄD {blad}")
        return self._odpowiedz(404, "BŁĄD nieznany adres")

    def do_POST(self):
        sciezka = urllib.parse.urlparse(self.path).path
        p = self._parametry()
        dlugosc = int(self.headers.get("Content-Length") or 0)
        if dlugosc > LIMIT_TRESCI:
            return self._odpowiedz(413, "BŁĄD za duże")
        tresc = self.rfile.read(dlugosc).decode("utf-8", errors="replace")
        try:
            if sciezka == "/kopia":
                shop, sid, sha = int(p["shop"]), int(p["id"]), p["sha"]
                if not re.fullmatch(r"[0-9a-f]{64}", sha):
                    return self._odpowiedz(400, "BŁĄD sha")
                linie = normalizuj(tresc)
                if skrot(linie) != sha:
                    return self._odpowiedz(400, "BŁĄD hash treści nie zgadza się")
                cel = os.path.join(katalog_historii(p["klient"]), "kopie", f"{shop}_{sid}_{sha[:12]}.xml")
                os.makedirs(os.path.dirname(cel), exist_ok=True)
                with open(cel, "w", encoding="utf-8", newline="\n") as plik:
                    plik.write("\n".join(linie) + "\n")
                return self._odpowiedz(200, f"OK {os.path.basename(cel)}")
            if sciezka == "/czesc":
                sesja, shop = p["sesja"], int(p["shop"])
                if not WZOR_NAZWY.match(sesja):
                    return self._odpowiedz(400, "BŁĄD sesja")
                dane = json.loads(tresc)
                cel = os.path.join(katalog_historii(p["klient"]), "_robocze", sesja, f"shop{shop}.json")
                zapisz_json(cel, dane)
                return self._odpowiedz(200, f"OK shop{shop}.json ({len(dane.get('serwisy', []))} serwisów)")
        except (KeyError, ValueError) as blad:
            return self._odpowiedz(400, f"BŁĄD {blad}")
        return self._odpowiedz(404, "BŁĄD nieznany adres")


def polecenie_odbiornik(args):
    serwer = ThreadingHTTPServer(("127.0.0.1", args.port), Odbiornik)
    print(f"Odbiornik historii sterowników: http://127.0.0.1:{args.port}  (baza: {BAZA})")
    print("W karcie Chrome z panelem:")
    print(f"  eval(await (await fetch('http://127.0.0.1:{args.port}/zrzut_panel.js')).text());")
    print("  await BM.zrzutSklepu({klient: '<klient>', sesja: '<sesja>'});")
    print("Ctrl+C kończy.")
    try:
        serwer.serve_forever()
    except KeyboardInterrupt:
        print("\nZatrzymano.")
    return 0


# ---------------------------------------------------------------- zrzut

def nowa_sesja(rodzaj):
    if rodzaj not in RODZAJE:
        raise ValueError(f"rodzaj spoza listy: {', '.join(RODZAJE)}")
    return f"{teraz():%Y-%m-%d_%H%M%S}_{rodzaj}"


def zloz(klient, sesja, zadanie=""):
    """Łączy części shop<n>.json w jeden zrzut. Zwraca (ścieżka, zrzut)."""
    katalog = os.path.join(katalog_historii(klient), "_robocze", sesja)
    czesci = sorted(glob.glob(os.path.join(katalog, "shop*.json")))
    if not czesci:
        raise ValueError(f"brak części zrzutu w {katalog}")
    rodzaj = sesja.split("_", 2)[2] if sesja.count("_") >= 2 else "reczny"
    serwisy, bledy, sklepy, hosty, czasy = {}, [], [], set(), []
    for sciezka in czesci:
        czesc = czytaj_json(sciezka)
        shop = int(czesc["shop"])
        try:  # czas odczytu w przeglądarce (UTC), nie czas składania
            czasy.append(datetime.datetime.fromisoformat(czesc["czas"].replace("Z", "+00:00")).astimezone())
        except (KeyError, ValueError):
            pass
        sklepy.append(shop)
        hosty.add(czesc.get("host", ""))
        bledy += [f"shop {shop}: {b}" for b in czesc.get("bledy", [])]
        for s in czesc.get("serwisy", []):
            sid = str(s["id"])
            rek = serwisy.setdefault(sid, {
                "id": s["id"], "nazwa": s["nazwa"], "sklepy": [], "aktywny": {}, "wygenerowany": {},
                "sterownik": s["sterownik"], "sha256": s["sha256"], "linie": s["linie"], "znacznik": s["znacznik"],
            })
            rek["sklepy"].append(shop)
            rek["aktywny"][str(shop)] = s["aktywny"]
            rek["wygenerowany"][str(shop)] = s["wygenerowany"]
            if s["sha256"] != rek["sha256"]:  # pułapka 2: sterownik jest per ID
                bledy.append(f"serwis {sid}: inny sterownik w sklepie {shop} niż w {rek['sklepy'][0]}")
    zrzut = {
        "klient": klient,
        "czas": (min(czasy).replace(microsecond=0) if czasy else teraz()).isoformat(),
        "czas_do": (max(czasy).replace(microsecond=0) if czasy else teraz()).isoformat(),
        "rodzaj": rodzaj, "sesja": sesja,
        "zadanie": zadanie, "host": sorted(hosty), "sklepy": sorted(sklepy),
        "serwisy": sorted(serwisy.values(), key=lambda x: int(x["id"])), "bledy": bledy,
    }
    cel = os.path.join(katalog_historii(klient), f"{sesja}.json")
    zapisz_json(cel, zrzut)
    return cel, zrzut


def wyjatki(klient):
    sciezka = os.path.join(katalog_historii(klient), "wyjatki_duplikatow.json")
    if not os.path.isfile(sciezka):
        return set()
    return {frozenset(str(x) for x in para) for para in czytaj_json(sciezka)}


def duplikaty(zrzut, klient):
    """{sha: [id, ...]} dla sterowników w więcej niż jednym ID (bez par z wyjątków)."""
    grupy = {}
    for s in zrzut["serwisy"]:
        if s["sterownik"]:
            grupy.setdefault(s["sha256"], []).append(str(s["id"]))
    znane = wyjatki(klient)
    wynik = {}
    for sha, ids in grupy.items():
        if len(ids) > 1 and not all(frozenset((a, b)) in znane for a in ids for b in ids if a < b):
            wynik[sha] = ids
    return wynik


def niezgodne_znaczniki(zrzut):
    wynik = []
    for s in zrzut["serwisy"]:
        z = s.get("znacznik") or {}
        if z.get("serwis_id") and int(z["serwis_id"]) != int(s["id"]):
            wynik.append(f"{s['id']} „{s['nazwa']}”: znacznik wskazuje ID {z['serwis_id']} ({z.get('nazwa')})")
        elif z.get("shop") and z["shop"] not in s["sklepy"]:
            wynik.append(f"{s['id']} „{s['nazwa']}”: znacznik wskazuje shop={z['shop']}, serwis jest w {s['sklepy']}")
    return wynik


def roznice(stary, nowy):
    """Lista (id, opis) zmian między zrzutami."""
    a = {str(s["id"]): s for s in stary["serwisy"]}
    b = {str(s["id"]): s for s in nowy["serwisy"]}
    wynik = []
    wspolne_sklepy = set(stary["sklepy"]) & set(nowy["sklepy"])
    for sid in sorted(set(a) | set(b), key=int):
        x, y = a.get(sid), b.get(sid)
        if x and not y:
            if set(x["sklepy"]) & wspolne_sklepy:
                wynik.append((sid, f"USUNIĘTY „{x['nazwa']}”"))
            continue
        if y and not x:
            if set(y["sklepy"]) & wspolne_sklepy:
                wynik.append((sid, f"NOWY „{y['nazwa']}” sterownik {'tak' if y['sterownik'] else 'nie'}"))
            continue
        if x["sha256"] != y["sha256"]:
            wynik.append((sid, f"STEROWNIK „{y['nazwa']}” {(x['sha256'] or '-')[:12]} → {(y['sha256'] or '-')[:12]}"
                               f" ({x['linie']} → {y['linie']} linii)"))
        for shop in sorted(set(x["aktywny"]) & set(y["aktywny"])):
            if x["aktywny"][shop] != y["aktywny"][shop]:
                wynik.append((sid, f"STATUS „{y['nazwa']}” shop={shop}: "
                                   f"{'aktywny' if x['aktywny'][shop] else 'wyłączony'} → "
                                   f"{'aktywny' if y['aktywny'][shop] else 'wyłączony'}"))
        if x["nazwa"] != y["nazwa"]:
            wynik.append((sid, f"NAZWA „{x['nazwa']}” → „{y['nazwa']}”"))
    return wynik


def wpisy_dziennika(klient, od_czasu=None):
    sciezka = os.path.join(katalog_klienta(klient), "dziennik_wdrozen.csv")
    if not os.path.isfile(sciezka):
        return []
    with open(sciezka, encoding="utf-8", newline="") as plik:
        wiersze = list(csv.DictReader(plik))
    if od_czasu:
        wiersze = [w for w in wiersze if w["czas_wgrania"] >= od_czasu]
    return wiersze


def raport_zrzutu(klient, zrzut, poprzedni):
    """Wypisuje stan zrzutu względem poprzedniego. Zwraca liczbę ostrzeżeń."""
    ostrzezenia = 0
    ster = sum(1 for s in zrzut["serwisy"] if s["sterownik"])
    print(f"Zrzut {zrzut['sesja']}: sklepy {zrzut['sklepy']}, serwisów {len(zrzut['serwisy'])}, ze sterownikiem {ster}")
    for b in zrzut["bledy"]:
        print(f"  BŁĄD ZRZUTU: {b}")
        ostrzezenia += 1
    if poprzedni:
        print(f"Porównanie z: {poprzedni['sesja']}")
        brak = sorted(set(poprzedni["sklepy"]) - set(zrzut["sklepy"]))
        if brak:
            print(f"  UWAGA: w tym zrzucie brak sklepów {brak} (były w poprzednim)")
            ostrzezenia += 1
        zmiany = roznice(poprzedni, zrzut)
        wpisy = {w["id_serwisu"]: w for w in wpisy_dziennika(klient, poprzedni["czas"])}
        bez_wpisu = ("  ← to wgranie? dopisz poleceniem dziennik" if zrzut["rodzaj"] == "po_wgraniu"
                     else "  ← brak wpisu w dzienniku (zmiana spoza naszych wdrożeń?)")
        for sid, opis in zmiany:
            dopisek = "" if sid in wpisy else bez_wpisu
            print(f"  {sid}: {opis}{dopisek}")
        if not zmiany:
            print("  bez zmian")
        if zrzut["rodzaj"] != "po_wgraniu":  # po wgraniu zmiana jest oczekiwana, dziennik dopiero po zrzucie
            ostrzezenia += sum(1 for sid, _ in zmiany if sid not in wpisy)
        stare_dup = set(duplikaty(poprzedni, klient))
    else:
        print("Pierwszy zrzut klienta, brak porównania.")
        stare_dup = set()
    for sha, ids in duplikaty(zrzut, klient).items():
        nowy = sha not in stare_dup
        print(f"  {'NOWY DUPLIKAT' if nowy else 'duplikat (znany)'}: ten sam sterownik w serwisach {', '.join(ids)}")
        ostrzezenia += 1 if nowy else 0
    for opis in niezgodne_znaczniki(zrzut):
        print(f"  ZNACZNIK: {opis}")
        ostrzezenia += 1
    return ostrzezenia


def polecenie_sesja(args):
    print(nowa_sesja(args.rodzaj))
    return 0


def polecenie_zloz(args):
    poprzednie = zrzuty(args.klient)
    cel, zrzut = zloz(args.klient, args.sesja, args.zadanie or "")
    poprzedni = czytaj_json(poprzednie[-1]) if poprzednie and poprzednie[-1] != cel else None
    print(f"Zapisano: {os.path.relpath(cel, BAZA)}")
    return 1 if raport_zrzutu(args.klient, zrzut, poprzedni) else 0


def polecenie_porownaj(args):
    lista = zrzuty(args.klient)
    do = args.do or (lista[-1] if lista else None)
    od = args.od or (lista[-2] if len(lista) > 1 else None)
    if not do:
        print("Brak zrzutów klienta.")
        return 2
    return 1 if raport_zrzutu(args.klient, czytaj_json(do), czytaj_json(od) if od else None) else 0


# ---------------------------------------------------------------- dziennik

def polecenie_dziennik(args):
    lista = zrzuty(args.klient)
    if len(lista) < 2:
        print("BŁĄD: potrzebne dwa zrzuty: przed_wgraniem i po_wgraniu.")
        return 2
    po, przed = czytaj_json(lista[-1]), czytaj_json(lista[-2])
    if po["rodzaj"] != "po_wgraniu":
        print(f"UWAGA: ostatni zrzut ma rodzaj „{po['rodzaj']}”, oczekiwany „po_wgraniu”.")
    if not os.path.isfile(args.plik):
        print(f"BŁĄD: brak pliku {args.plik}")
        return 2
    znajdz = lambda z: next((s for s in z["serwisy"] if int(s["id"]) == args.id), None)  # noqa: E731
    s_po, s_przed = znajdz(po), znajdz(przed)
    if not s_po:
        print(f"BŁĄD: serwisu {args.id} nie ma w zrzucie po wgraniu.")
        return 2
    plik_sha = sha_pliku(args.plik)
    zgodne = s_po["sha256"] == plik_sha
    wiersz = {
        "czas_wgrania": po["czas"], "wgrywa": args.wgrywa, "shop": args.shop, "id_serwisu": args.id,
        "nazwa_serwisu": s_po["nazwa"], "plik_lokalny": os.path.relpath(os.path.abspath(args.plik), BAZA),
        "sha256_przed": (s_przed or {}).get("sha256") or "", "sha256_po": s_po["sha256"] or "",
        "sha256_pliku": plik_sha, "zgodne_po_zapisie": "TAK" if zgodne else "NIE", "zadanie": args.zadanie or "",
    }
    sciezka = os.path.join(katalog_klienta(args.klient), "dziennik_wdrozen.csv")
    nowy = not os.path.isfile(sciezka)
    with open(sciezka, "a", encoding="utf-8", newline="") as plik:
        pisarz = csv.DictWriter(plik, fieldnames=KOLUMNY_DZIENNIKA)
        if nowy:
            pisarz.writeheader()
        pisarz.writerow(wiersz)
    print(f"Dziennik: {args.id} „{s_po['nazwa']}” ← {os.path.basename(args.plik)}: "
          f"{'ZGODNE' if zgodne else 'NIEZGODNE'} (panel {(s_po['sha256'] or '-')[:12]}, plik {plik_sha[:12]})")
    inne = [s["id"] for s in po["serwisy"] if s["sha256"] == plik_sha and int(s["id"]) != args.id]
    if inne:
        print(f"UWAGA: ten sam sterownik jest też w serwisach {inne}")
    return 0 if zgodne and not inne else 1


# ---------------------------------------------------------------- kontrola

def polecenie_kontrola(args):
    """Przebieg kontrolny do /zamknij: ostatni zrzut względem startu sesji."""
    lista = zrzuty(args.klient)
    if not lista:
        print("Brak zrzutów klienta.")
        return 2
    kon = czytaj_json(lista[-1])
    if args.od:
        ref = czytaj_json(args.od)
    else:
        starty = [p for p in lista[:-1] if p.endswith("_start.json")]
        if not starty:
            print("BŁĄD: brak zrzutu „start” przed ostatnim zrzutem. Podaj --od.")
            return 2
        ref = czytaj_json(starty[-1])
    problemy = []
    if kon["rodzaj"] != "koniec":
        problemy.append(f"ostatni zrzut ma rodzaj „{kon['rodzaj']}”, a nie „koniec”")
    problemy += [f"błąd zrzutu: {b}" for b in kon["bledy"]]
    brak = sorted(set(ref["sklepy"]) - set(kon["sklepy"]))
    if brak:
        problemy.append(f"zrzut końcowy nie obejmuje sklepów {brak}")

    wpisy = wpisy_dziennika(args.klient, ref["czas"])
    po_id = {}
    for w in wpisy:
        po_id.setdefault(w["id_serwisu"], []).append(w)
    teraz_sha = {str(s["id"]): s["sha256"] for s in kon["serwisy"]}
    zmienione = set()
    for sid, opis in roznice(ref, kon):
        zmienione.add(sid)
        if opis.startswith("STEROWNIK") or opis.startswith("NOWY") or opis.startswith("USUNIĘTY"):
            ost = (po_id.get(sid) or [None])[-1]
            if not ost:
                problemy.append(f"{sid}: {opis} — ZAPIS POZA PLANEM (brak wpisu w dzienniku)")
            elif ost["zgodne_po_zapisie"] != "TAK":
                problemy.append(f"{sid}: wgranie oznaczone jako NIEZGODNE w dzienniku")
            elif teraz_sha.get(sid) != ost["sha256_pliku"]:
                problemy.append(f"{sid}: sterownik zmienił się po wgraniu (inny niż wgrany plik)")
        else:
            problemy.append(f"{sid}: {opis}")
    for sid, ws in po_id.items():
        if sid not in zmienione and teraz_sha.get(sid) != ws[-1]["sha256_pliku"]:
            problemy.append(f"{sid}: wpis w dzienniku, ale w panelu jest inny sterownik niż wgrany plik")
    for sid, ws in po_id.items():
        inne = [str(s["id"]) for s in kon["serwisy"] if s["sha256"] == ws[-1]["sha256_pliku"] and str(s["id"]) != sid]
        if inne:
            problemy.append(f"{sid}: wgrany sterownik jest też w serwisach {', '.join(inne)} — ZAPIS W DWÓCH SERWISACH?")
    problemy += [f"znacznik: {z}" for z in niezgodne_znaczniki(kon)]

    print(f"Kontrola {args.klient}: {ref['sesja']} → {kon['sesja']}")
    print(f"Sklepy: {kon['sklepy']}, serwisów: {len(kon['serwisy'])}, wgrań w dzienniku: {len(wpisy)}, "
          f"zmienionych serwisów: {len(zmienione)}")
    if problemy:
        print("PROBLEMY (nie robić merge, procedura incydentu):")
        for p in problemy:
            print(f"  - {p}")
        return 1
    print("OK: każda zmiana ma zgodny wpis w dzienniku, brak zapisu w dwóch serwisach i niezgodnych znaczników.")
    return 0


# ---------------------------------------------------------------- pliki

def polecenie_hash(args):
    tekst, _ = czytaj_plik(args.plik)
    linie = normalizuj(tekst)
    print(f"{skrot(linie)}  {len(linie)} linii  {args.plik}")
    return 0


def polecenie_waliduj(args):
    tekst, surowe = czytaj_plik(args.plik)
    if not wyglada_na_xslt(tekst):
        print("BŁĄD: plik nie wygląda na XSLT.")
        return 2
    try:
        from lxml import etree
    except ImportError:
        import xml.dom.minidom
        try:
            xml.dom.minidom.parseString(surowe)
        except Exception as blad:
            print(f"NIEPOPRAWNY XML: {blad}")
            return 1
        print("XML poprawny (brak lxml: kompilacji XSLT nie sprawdzono).")
        return 0
    try:
        etree.XSLT(etree.fromstring(surowe))
    except Exception as blad:
        print(f"NIEPOPRAWNY: {blad}")
        return 1
    print("OK: XML poprawny, XSLT się kompiluje (lxml).")
    return 0


# ---------------------------------------------------------------- menu

def menu():
    klienci = sorted(k for k in os.listdir(BAZA)
                     if os.path.isdir(os.path.join(BAZA, k, "_historia")))
    print("Historia sterowników IdoSell")
    print("  1. Uruchom odbiornik (dla Claude in Chrome)")
    print("  2. Porównaj dwa ostatnie zrzuty klienta")
    print("  3. Kontrola przed zamknięciem projektu")
    print("  4. Lista zrzutów klienta")
    wybor = input("Wybierz 1-4 (Enter = 1): ").strip() or "1"
    if wybor == "1":
        return polecenie_odbiornik(argparse.Namespace(port=PORT))
    if not klienci:
        print("Brak klientów z historią.")
        return 2
    for i, k in enumerate(klienci, 1):
        print(f"  {i}. {k}")
    nr = input(f"Klient 1-{len(klienci)} (Enter = 1): ").strip() or "1"
    klient = klienci[int(nr) - 1] if nr.isdigit() and 1 <= int(nr) <= len(klienci) else klienci[0]
    if wybor == "2":
        return polecenie_porownaj(argparse.Namespace(klient=klient, od=None, do=None))
    if wybor == "3":
        return polecenie_kontrola(argparse.Namespace(klient=klient, od=None))
    for p in zrzuty(klient)[-30:]:
        print("  " + os.path.basename(p))
    return 0


def main():
    global BAZA
    parser = argparse.ArgumentParser(description="Historia zmian sterowników XSLT w panelu IdoSell.")
    parser.add_argument("--baza", help="katalog zamiast Zmiany_sterownikow (testy)")
    pod = parser.add_subparsers(dest="polecenie")
    p = pod.add_parser("odbiornik")
    p.add_argument("--port", type=int, default=PORT)
    p = pod.add_parser("sesja")
    p.add_argument("--rodzaj", required=True, choices=RODZAJE)
    p = pod.add_parser("zloz")
    p.add_argument("--klient", required=True)
    p.add_argument("--sesja", required=True)
    p.add_argument("--zadanie")
    p = pod.add_parser("porownaj")
    p.add_argument("--klient", required=True)
    p.add_argument("--od")
    p.add_argument("--do")
    p = pod.add_parser("dziennik")
    p.add_argument("--klient", required=True)
    p.add_argument("--shop", type=int, required=True)
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--plik", required=True)
    p.add_argument("--wgrywa", required=True, choices=WGRYWA)
    p.add_argument("--zadanie")
    p = pod.add_parser("kontrola")
    p.add_argument("--klient", required=True)
    p.add_argument("--od")
    for nazwa in ("hash", "waliduj"):
        p = pod.add_parser(nazwa)
        p.add_argument("--plik", required=True)
    args = parser.parse_args()
    if args.baza:
        BAZA = os.path.abspath(args.baza)
    if not args.polecenie:
        return menu()
    obsluga = {
        "odbiornik": polecenie_odbiornik, "sesja": polecenie_sesja, "zloz": polecenie_zloz,
        "porownaj": polecenie_porownaj, "dziennik": polecenie_dziennik, "kontrola": polecenie_kontrola,
        "hash": polecenie_hash, "waliduj": polecenie_waliduj,
    }[args.polecenie]
    try:
        return obsluga(args)
    except ValueError as blad:
        print(f"BŁĄD: {blad}")
        return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nPrzerwano.")
        sys.exit(2)
