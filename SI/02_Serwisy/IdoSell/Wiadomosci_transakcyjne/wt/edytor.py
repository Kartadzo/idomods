"""Edytor treści - logika bez okna: lista wiadomości, tytuł i HTML maila, cofnij, wyklucz z importu, podgląd."""

import glob
import html
import os
import re
import shutil
import tempfile
from typing import Dict, List, Optional, Tuple

from . import eksport, icf, status, tresci, wspolne

ND = tresci.ND
FOLDER_USUNIETYCH = "_usuniete"
PLIKI_TRESCI = ("_mail.html", "_sms.txt")   # .icf zostaje - to oryginał dla Edycji działania i raportu Status


def lista_eksportow() -> List[Tuple[str, str]]:
    """[(etykieta, katalog)] - najnowsze najpierw, jak w menu programu."""
    pliki = sorted(glob.glob(os.path.join(wspolne.FOLDER_TRESCI, "*", "*", "manifest.json")), reverse=True)
    return [(os.path.relpath(os.path.dirname(p), wspolne.FOLDER_TRESCI).replace(os.sep, " · "), os.path.dirname(p))
            for p in pliki]


class Eksport:
    def __init__(self, katalog: str):
        self.katalog = katalog
        self.manifest = eksport.wczytaj_eksport(katalog)
        self._oryginaly = {}   # ICF z eksportu się nie zmienia - parsujemy raz (z załącznikami bywa duży)

    @property
    def opis(self) -> str:
        return "%s, sklep %s · eksport z %s" % (self.manifest["domena"], self.manifest["shop_id"],
                                                self.manifest["data_eksportu"].replace("T", " ")[:16])

    def wiadomosci(self) -> List[Dict]:
        """Wiadomości, w których jest co najmniej jeden mail do edycji - w kolejności z panelu."""
        return [w for w in self.manifest["wiadomosci"]
                if w["edytowalna"] and w.get("pliki") and w["stan_listy"].get("mail") != ND and self.jezyki(w)]

    def jezyki(self, w: Dict) -> List[str]:
        """Języki z kanałem mail (wykluczone też - żeby dało się je przywrócić)."""
        folder = self.folder(w)
        return [j for j in w["pliki"] if os.path.exists(os.path.join(folder, j + ".icf"))
                and "mail" in self._oryginal(w, j)["kanaly"]]

    def folder(self, w: Dict) -> str:
        return eksport.folder_wiadomosci(self.katalog, w)

    def _folder_usunietych(self, w: Dict) -> str:
        return os.path.join(self.katalog, FOLDER_USUNIETYCH, os.path.basename(self.folder(w)))

    def _oryginal(self, w: Dict, jezyk: str) -> Dict:
        klucz = (w["template"], jezyk)
        if klucz not in self._oryginaly:
            self._oryginaly[klucz] = icf.wczytaj(wspolne.czytaj_tekst(os.path.join(self.folder(w), jezyk + ".icf")))
        return self._oryginaly[klucz]

    def _meta(self, w: Dict) -> Dict:
        sciezka = os.path.join(self.folder(w), "meta.json")
        return wspolne.czytaj_json(sciezka) if os.path.exists(sciezka) else {}

    def wysylka(self, w: Dict, jezyk: str) -> bool:
        return ((w.get("formularz") or {}).get("mail") or {}).get(jezyk) == "y"

    def pusty_w_sklepie(self, w: Dict, jezyk: str) -> bool:
        """Mail nigdy niewypełniony w panelu (kanał bez pól) - import nie utworzy treści, edycja nie ma sensu."""
        return "text_main_0" not in self._oryginal(w, jezyk)["kanaly"]["mail"]

    def wykluczony(self, w: Dict, jezyk: str) -> bool:
        return jezyk in self._meta(w).get("wykluczone", [])

    def oryginal(self, w: Dict, jezyk: str) -> Tuple[str, str]:
        """(tytuł, HTML) w sklepie w chwili eksportu."""
        mail = self._oryginal(w, jezyk)["kanaly"]["mail"]
        return mail.get("title", ""), mail.get("text_main_0", "")

    def tresc(self, w: Dict, jezyk: str) -> Tuple[str, str]:
        """(tytuł, HTML) po zmianach użytkownika - z meta.json i pliku _mail.html."""
        tytul, kod = self.oryginal(w, jezyk)
        tytul = self._meta(w).get("tytuly", {}).get(jezyk, tytul)
        plik = os.path.join(self.folder(w), jezyk + "_mail.html")
        if os.path.exists(plik):
            kod = wspolne.czytaj_tekst(plik).lstrip("﻿")
        return tytul, kod

    def zmieniony(self, w: Dict, jezyk: str) -> bool:
        if self.wykluczony(w, jezyk):
            return False
        (t0, h0), (t1, h1) = self.oryginal(w, jezyk), self.tresc(w, jezyk)
        return t0 != t1 or tresci.bez_cr(h0) != tresci.bez_cr(h1)

    def zapisz(self, w: Dict, jezyk: str, tytul: str, kod: str) -> None:
        folder = self.folder(w)
        meta = self._meta(w)
        meta.setdefault("tytuly", {})[jezyk] = tytul
        wspolne.zapisz_json(os.path.join(folder, "meta.json"), meta)
        wspolne.zapisz_tekst(os.path.join(folder, jezyk + "_mail.html"), kod)

    def cofnij(self, w: Dict, jezyk: str) -> Tuple[str, str]:
        tytul, kod = self.oryginal(w, jezyk)
        self.zapisz(w, jezyk, tytul, kod)
        return tytul, kod

    def wyklucz(self, w: Dict, jezyk: str) -> None:
        """„Usuń mail”: przy Zastosuj plan ten język zostaje w sklepie bez zmian; pliki treści do _usuniete."""
        folder, kosz = self.folder(w), self._folder_usunietych(w)
        for koncowka in PLIKI_TRESCI:
            zrodlo = os.path.join(folder, jezyk + koncowka)
            if os.path.exists(zrodlo):
                os.makedirs(kosz, exist_ok=True)
                cel = os.path.join(kosz, jezyk + koncowka)
                if os.path.exists(cel):
                    os.remove(cel)
                shutil.move(zrodlo, cel)
        meta = self._meta(w)
        if jezyk not in meta.get("wykluczone", []):
            meta.setdefault("wykluczone", []).append(jezyk)
        wspolne.zapisz_json(os.path.join(folder, "meta.json"), meta)

    def przywroc(self, w: Dict, jezyk: str) -> None:
        folder, kosz = self.folder(w), self._folder_usunietych(w)
        for koncowka in PLIKI_TRESCI:
            zrodlo = os.path.join(kosz, jezyk + koncowka)
            if os.path.exists(zrodlo) and not os.path.exists(os.path.join(folder, jezyk + koncowka)):
                shutil.move(zrodlo, os.path.join(folder, jezyk + koncowka))
        meta = self._meta(w)
        meta["wykluczone"] = [j for j in meta.get("wykluczone", []) if j != jezyk]
        wspolne.zapisz_json(os.path.join(folder, "meta.json"), meta)

    def liczba_zmian(self) -> int:
        return sum(1 for w in self.wiadomosci() for j in self.jezyki(w) if self.zmieniony(w, j))

    def przygotuj_paczke(self) -> Tuple[Optional[str], List[Dict]]:
        """Jak pozycja menu „Treści: różnice i ICF do importu” - zwraca (folder planu albo None, różnice)."""
        roznice = tresci.roznice_tresci(self.katalog, self.manifest)
        if not roznice:
            return None, []
        katalog_planu = os.path.join(self.katalog, "do_importu_" + wspolne.znacznik_daty(wspolne.teraz_iso()))
        tresci.zloz(self.manifest, roznice, katalog_planu)
        return katalog_planu, roznice


def roznica_zmiennych(oryginal: str, nowy: str) -> Tuple[List[str], List[str]]:
    """(brakujące, nadmiarowe) zmienne [iai:…] względem oryginału - najczęstszy błąd przy tłumaczeniu."""
    przed, po = status.zmienne(oryginal), status.zmienne(nowy)
    return sorted(przed - po), sorted(po - przed)


_ZNACZNIK = re.compile(r"(<[^>]*>)")


def _podswietl_zmienne(kod: str) -> str:
    """Zmienne [iai:…] w tekście (nie w atrybutach znaczników) na żółtym tle - panel podstawia je dopiero przy wysyłce."""
    czesci = _ZNACZNIK.split(kod)
    for i in range(0, len(czesci), 2):
        czesci[i] = status.WZOR_ZMIENNEJ.sub(
            lambda m: '<span style="background:#fff3b0;color:#7a5b00">%s</span>' % m.group(0), czesci[i])
    return "".join(czesci)


def plik_podgladu(tytul: str, kod: str, opis: str) -> str:
    """Zapisuje HTML do podglądu w przeglądarce (folder tymczasowy) i zwraca jego ścieżkę."""
    naglowek = ('<div style="font:14px Segoe UI,Arial,sans-serif;background:#eef2f7;border-bottom:1px solid #c9d3e0;'
                'padding:10px 14px;margin:-8px -8px 12px">'
                '<div style="color:#5a6b80">Podgląd: %s · zmienne <span style="background:#fff3b0">[iai:…]</span> '
                'panel podstawi przy wysyłce</div><div style="font-size:16px;margin-top:4px"><b>Temat:</b> %s</div></div>'
                % (html.escape(opis), html.escape(tytul)))
    tresc = _podswietl_zmienne(kod)
    if re.search(r"<body[^>]*>", tresc, re.I):
        strona = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + naglowek, tresc, count=1, flags=re.I)
    else:
        strona = ('<!DOCTYPE html><html><head><meta charset="utf-8"><title>%s</title></head><body>%s%s</body></html>'
                  % (html.escape(tytul), naglowek, tresc))
    if not re.search(r"<meta[^>]+charset", strona, re.I):
        strona = '<meta charset="utf-8">' + strona
    sciezka = os.path.join(tempfile.gettempdir(), "wiadomosci_podglad.html")
    wspolne.zapisz_tekst(sciezka, strona)
    return sciezka
