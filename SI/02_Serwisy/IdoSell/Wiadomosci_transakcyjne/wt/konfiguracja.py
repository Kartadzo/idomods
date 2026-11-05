"""Edycja działania: CSV z bieżącym stanem wysyłki, porównanie z poprawionym CSV, plan zmian dla panelu."""

import csv
import io
import os
import shutil
from typing import Dict, Iterator, List, Tuple

from . import eksport, icf, wspolne

TAK, NIE, ND = "tak", "nie", "nie dotyczy"


class BladKonfiguracji(Exception):
    """CSV nie da się odczytać jako plik konfiguracji tego eksportu."""


def kolumny(manifest: Dict) -> List[str]:
    return ["grupa", "template", "nazwa"] + ["mail_" + j for j in manifest["jezyki"]] + ["sms", "reset_domyslna"]


def _tekst(flaga: str) -> str:
    return TAK if flaga == "y" else NIE


def wiersze(manifest: Dict) -> Iterator[Dict[str, str]]:
    for w in manifest["wiadomosci"]:
        if not w["edytowalna"] or not w.get("formularz"):
            continue
        formularz, stan = w["formularz"], w["stan_listy"]
        wiersz = {"grupa": w["grupa"], "template": w["template"], "nazwa": w["nazwa"]}
        for j in manifest["jezyki"]:
            if stan.get("mail") == ND or j not in formularz["mail"]:
                wiersz["mail_" + j] = ND
            else:
                wiersz["mail_" + j] = _tekst(formularz["mail"][j])
        wiersz["sms"] = ND if (stan.get("sms") == ND or formularz.get("sms") is None) else _tekst(formularz["sms"])
        wiersz["reset_domyslna"] = NIE
        yield wiersz


def sciezka_csv(manifest: Dict) -> str:
    return os.path.join(wspolne.FOLDER_EDYCJA, wspolne.id_sklepu(manifest["domena"], manifest["shop_id"]),
                        "konfiguracja_" + wspolne.znacznik_daty(manifest["data_eksportu"]) + ".csv")


def zapisz_csv(manifest: Dict, sciezka: str) -> None:
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    with open(sciezka, "w", encoding="utf-8-sig", newline="") as plik:
        pisarz = csv.DictWriter(plik, fieldnames=kolumny(manifest), delimiter=";")
        pisarz.writeheader()
        for wiersz in wiersze(manifest):
            pisarz.writerow(wiersz)


def _wczytaj_csv(manifest: Dict, sciezka: str) -> csv.DictReader:
    try:
        with open(sciezka, encoding="utf-8-sig", newline="") as plik:
            tresc = plik.read()
    except UnicodeDecodeError:
        # Polski Excel: „CSV (rozdzielany średnikami)” zapisuje w cp1250; wartości tak/nie i kody są w ASCII.
        with open(sciezka, encoding="cp1250", errors="replace", newline="") as plik:
            tresc = plik.read()
    naglowek = tresc.split("\n", 1)[0]
    if ";" not in naglowek:
        raise BladKonfiguracji("Nagłówek CSV nie zawiera średnika - zapisz plik w Excelu jako "
                               "'CSV UTF-8 (rozdzielany przecinkami)' z separatorem średnik albo popraw separator.")
    czytnik = csv.DictReader(io.StringIO(tresc), delimiter=";")
    brak = [c for c in kolumny(manifest) if c not in (czytnik.fieldnames or [])]
    if brak:
        raise BladKonfiguracji("Brak kolumn w CSV: " + ", ".join(brak))
    return czytnik


def roznice(manifest: Dict, sciezka: str) -> Tuple[List[Dict], List[str]]:
    stan = {w["template"]: w for w in wiersze(manifest)}
    zmiany, bledy, widziane = [], [], set()
    for nr, wiersz in enumerate(_wczytaj_csv(manifest, sciezka), start=2):
        template = (wiersz.get("template") or "").strip()
        if not template:
            continue
        if template not in stan:
            bledy.append("wiersz %d: nieznana lub nieedytowalna wiadomość '%s'" % (nr, template))
            continue
        if template in widziane:
            bledy.append("wiersz %d: wiadomość '%s' powtórzona - liczy się pierwsze wystąpienie" % (nr, template))
            continue
        widziane.add(template)
        przed = stan[template]
        zmiana = {"template": template, "nazwa": przed["nazwa"], "grupa": przed["grupa"],
                  "mail": {}, "sms": None, "reset": False}
        for kolumna in kolumny(manifest)[3:]:
            surowa = wiersz.get(kolumna) or ""
            nowa, stara = surowa.strip().lower(), przed[kolumna]
            if kolumna == "reset_domyslna":
                if nowa not in (TAK, NIE, ""):
                    bledy.append("wiersz %d (%s): reset_domyslna = '%s' - dozwolone: tak / nie" % (nr, template, surowa))
                zmiana["reset"] = nowa == TAK
                continue
            if nowa == stara:
                continue
            if stara == ND:
                bledy.append("wiersz %d (%s): %s = 'nie dotyczy' w panelu - nie da się zmienić" % (nr, template, kolumna))
                continue
            if nowa not in (TAK, NIE):
                bledy.append("wiersz %d (%s): %s = '%s' - dozwolone: tak / nie" % (nr, template, kolumna, surowa))
                continue
            flaga = "y" if nowa == TAK else "n"
            if kolumna == "sms":
                zmiana["sms"] = flaga
            else:
                zmiana["mail"][kolumna[len("mail_"):]] = flaga
        if zmiana["mail"] or zmiana["sms"] is not None or zmiana["reset"]:
            zmiany.append(zmiana)
    return zmiany, bledy


def zapisz_plan(manifest: Dict, katalog_eksportu: str, zmiany: List[Dict], katalog_planu: str) -> str:
    po_template = {w["template"]: w for w in manifest["wiadomosci"]}
    plan = {"wersja": 1, "rodzaj": "konfiguracja", "domena": manifest["domena"], "shop_id": manifest["shop_id"],
            "data_eksportu": manifest["data_eksportu"], "zmiany": []}
    for zmiana in zmiany:
        w = po_template[zmiana["template"]]
        oczekiwane = {"mail": dict(w["formularz"]["mail"]), "sms": w["formularz"].get("sms")}
        oczekiwane["mail"].update(zmiana["mail"])
        if zmiana["sms"] is not None:
            oczekiwane["sms"] = zmiana["sms"]
        kopie = {}
        if not zmiana["reset"]:
            for jezyk in w["pliki"]:
                zrodlo = os.path.join(eksport.folder_wiadomosci(katalog_eksportu, w), jezyk + ".icf")
                if not os.path.exists(zrodlo):
                    continue
                nazwa = "%s__%s.icf" % (zmiana["template"], jezyk)
                os.makedirs(os.path.join(katalog_planu, "kopie"), exist_ok=True)
                shutil.copyfile(zrodlo, os.path.join(katalog_planu, "kopie", nazwa))
                kopie[jezyk] = {"plik": nazwa, "odcisk": icf.odcisk(wspolne.czytaj_tekst(zrodlo))}
        pozycja = dict(zmiana)
        pozycja.update({"oczekiwane": oczekiwane, "kopie": kopie})
        plan["zmiany"].append(pozycja)
    sciezka = os.path.join(katalog_planu, "plan_konfiguracji.json")
    wspolne.zapisz_json(sciezka, plan)
    return sciezka
