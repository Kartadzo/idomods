"""Eksport z panelu (ZIP: manifest.json + ICF) -> folder per wiadomość z plikami do edycji."""

import json
import os
import zipfile
from typing import Dict, List, Optional, Tuple

from . import icf, wspolne


class BladEksportu(Exception):
    """ZIP nie jest eksportem narzędzia albo operacja zagraża plikom użytkownika."""


def wczytaj_zip(sciezka: str) -> Tuple[Dict, Dict[str, str]]:
    nazwa = os.path.basename(sciezka)
    try:
        with zipfile.ZipFile(sciezka) as archiwum:
            try:
                manifest = json.loads(archiwum.read("manifest.json").decode("utf-8"))
            except KeyError:
                raise BladEksportu("%s: brak manifest.json - to nie jest eksport narzędzia" % nazwa)
            pliki = {n: archiwum.read(n).decode("utf-8") for n in archiwum.namelist() if n.endswith(".icf")}
    except zipfile.BadZipFile:
        raise BladEksportu("%s: plik nie jest poprawnym archiwum ZIP (niedokończone pobieranie?)" % nazwa)
    if manifest.get("wersja") != 1:
        raise BladEksportu("%s: nieobsługiwana wersja manifestu: %r" % (nazwa, manifest.get("wersja")))
    return manifest, pliki


def scal(czesci: List[Tuple[Dict, Dict[str, str]]]) -> Tuple[Dict, Dict[str, str]]:
    """Łączy eksporty częściowe jednego sklepu; późniejsza część wygrywa dla tej samej wiadomości."""
    pierwszy = czesci[0][0]
    for manifest, _ in czesci[1:]:
        if (manifest["domena"], manifest["shop_id"]) != (pierwszy["domena"], pierwszy["shop_id"]):
            raise BladEksportu("Eksporty z różnych sklepów (%s/%s i %s/%s) - nie scalam"
                               % (pierwszy["domena"], pierwszy["shop_id"], manifest["domena"], manifest["shop_id"]))
    wiadomosci, pliki, jezyki = {}, {}, []
    for manifest, pliki_czesci in czesci:
        for w in manifest["wiadomosci"]:
            wiadomosci[w["template"]] = w
        pliki.update(pliki_czesci)
        for j in manifest["jezyki"]:
            if j not in jezyki:
                jezyki.append(j)
    wynik = dict(czesci[-1][0])
    wynik["wiadomosci"] = list(wiadomosci.values())
    wynik["jezyki"] = jezyki
    wynik["pozostale"] = [t for t in czesci[-1][0].get("pozostale", []) if t not in wiadomosci]
    wynik["niekompletny"] = bool(wynik["pozostale"])
    wynik["data_eksportu"] = pierwszy["data_eksportu"]
    return wynik, pliki


def katalog_eksportu(manifest: Dict) -> str:
    return os.path.join(wspolne.FOLDER_TRESCI, wspolne.id_sklepu(manifest["domena"], manifest["shop_id"]),
                        wspolne.znacznik_daty(manifest["data_eksportu"]))


def nazwa_folderu(wiadomosc: Dict) -> str:
    # Sam template (unikalny w sklepie) - z prefiksem grupy ścieżki przekraczały limit 260 znaków Windows.
    return wiadomosc["template"]


def folder_wiadomosci(katalog: str, wiadomosc: Dict) -> str:
    stary = os.path.join(katalog, wiadomosc["grupa"] + "__" + wiadomosc["template"])
    if os.path.isdir(stary):   # eksport rozpakowany wcześniejszą wersją programu
        return stary
    return os.path.join(katalog, nazwa_folderu(wiadomosc))


def wczytaj_eksport(katalog: str) -> Dict:
    return wspolne.czytaj_json(os.path.join(katalog, "manifest.json"))


def _zapisz_wiadomosc(cel: str, manifest: Dict, w: Dict, pliki: Dict[str, str]) -> None:
    folder = folder_wiadomosci(cel, w)
    tytuly = {}
    for jezyk, sciezka in w["pliki"].items():
        if sciezka not in pliki:
            w["bledy"].append("%s: brak pliku %s w ZIP" % (jezyk, sciezka))
            continue
        xml = pliki[sciezka]
        try:
            dane = icf.wczytaj(xml)
        except icf.BladIcf as blad:
            w["bledy"].append("%s: %s" % (jezyk, blad))
            continue
        wspolne.zapisz_tekst(os.path.join(folder, jezyk + ".icf"), xml)
        if "mail" in dane["kanaly"]:
            wspolne.zapisz_tekst(os.path.join(folder, jezyk + "_mail.html"), dane["kanaly"]["mail"].get("text_main_0", ""))
            tytuly[jezyk] = dane["kanaly"]["mail"].get("title", "")
        if "sms" in dane["kanaly"]:
            wspolne.zapisz_tekst(os.path.join(folder, jezyk + "_sms.txt"), dane["kanaly"]["sms"].get("text_main_0", ""))
    meta = {k: w.get(k) for k in ("nazwa", "grupa", "grupa_nazwa", "sekcja", "template", "ostatnia_edycja")}
    meta.update({"domena": manifest["domena"], "shop_id": manifest["shop_id"],
                 "data_eksportu": manifest["data_eksportu"], "tytuly": tytuly})
    wspolne.zapisz_json(os.path.join(folder, "meta.json"), meta)


def rozpakuj(sciezki_zip: List[str], katalog_docelowy: Optional[str] = None,
             nadpisz: bool = False) -> Tuple[str, Dict]:
    czesci = [wczytaj_zip(s) for s in sciezki_zip]
    manifest, pliki = scal(czesci) if len(czesci) > 1 else czesci[0]
    cel = katalog_docelowy or katalog_eksportu(manifest)
    if os.path.exists(os.path.join(cel, "manifest.json")) and not nadpisz:
        raise BladEksportu("Folder %s zawiera już rozpakowany eksport (być może z Twoimi zmianami). "
                           "Nie nadpisuję." % cel)
    for w in manifest["wiadomosci"]:
        if w.get("pliki"):
            _zapisz_wiadomosc(cel, manifest, w, pliki)
    wspolne.zapisz_json(os.path.join(cel, "manifest.json"), manifest)
    return cel, manifest
