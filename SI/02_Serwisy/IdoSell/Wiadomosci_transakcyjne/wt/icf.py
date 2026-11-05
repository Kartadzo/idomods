"""Pliki ICF panelu IdoSell: odczyt pól, podmiana pojedynczego pola z zachowaniem reszty pliku, odcisk."""

import hashlib
import re
import xml.etree.ElementTree as ET
from typing import Dict, Optional


class BladIcf(Exception):
    """Plik nie jest poprawnym ICF albo brakuje w nim wskazanego kanału/pola."""


def wczytaj(xml: str) -> Dict:
    try:
        korzen = ET.fromstring(xml.encode("utf-8"))
    except ET.ParseError as blad:
        raise BladIcf("Niepoprawny XML ICF: %s" % blad)
    if korzen.tag != "repository" or korzen.get("file_format") != "ICF":
        raise BladIcf("To nie jest plik ICF (korzeń <%s>)" % korzen.tag)
    element = korzen.find("element")
    if element is None:
        raise BladIcf("Plik ICF bez elementu <element>")
    ustawienia = {s.get("type"): s.get("value") for s in element.findall("settings/setting")}
    kanaly = {}
    for blok in element.findall("contents"):
        pola = {}
        for pole in blok.findall("content"):
            tekst = pole.text or ""
            pola[pole.get("type")] = tekst if tekst.strip() else ""
        kanaly[blok.get("message_type")] = pola
    return {
        "template": ustawienia.get("template"),
        "jezyk": ustawienia.get("language"),
        "nazwa": (element.findtext("meta/title") or "").strip(),
        "kanaly": kanaly,
        "zalaczniki": len(element.findall("enclosures/enclosure")),
    }


def wartosc(dane: Dict, kanal: str, pole: str) -> Optional[str]:
    return dane["kanaly"].get(kanal, {}).get(pole)


def _cdata(tekst: str) -> str:
    if tekst == "":
        return " "   # panel zapisuje puste pole jako pojedynczą spację
    return "<![CDATA[" + tekst.replace("]]>", "]]]]><![CDATA[>") + "]]>"


def podmien(xml: str, kanal: str, pole: str, wartosc_nowa: str) -> str:
    """Zmienia jedno pole w bloku kanału; reszta pliku (załączniki, nieznane pola) zostaje bajt w bajt."""
    blok = re.search(r'(<contents message_type="%s">)(.*?)(</contents>)' % re.escape(kanal), xml, re.S)
    if not blok:
        raise BladIcf("Brak kanału '%s' w ICF" % kanal)
    wnetrze = blok.group(2)
    wzor = re.compile(r'(<content type="%s">)(.*?)(</content>)' % re.escape(pole), re.S)
    if not wzor.search(wnetrze):
        raise BladIcf("Brak pola '%s' w kanale '%s'" % (pole, kanal))
    nowe_wnetrze = wzor.sub(lambda m: m.group(1) + _cdata(wartosc_nowa) + m.group(3), wnetrze, count=1)
    return xml[:blok.start(2)] + nowe_wnetrze + xml[blok.end(2):]


POLA_TRESCI = ("title", "text_main_0")
_ENCJE = (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'"), ("&amp;", "&"))


def _wartosc_pola(surowa: str) -> str:
    """Tekst pola niezależnie od zapisu: sekcje CDATA albo encje XML; sama spacja = puste."""
    wynik = []
    for czesc in re.split(r"(<!\[CDATA\[.*?\]\]>)", surowa, flags=re.S):
        if czesc.startswith("<![CDATA["):
            wynik.append(czesc[9:-3])
        else:
            for encja, znak in _ENCJE:
                czesc = czesc.replace(encja, znak)
            wynik.append(czesc)
    tekst = "".join(wynik)
    return tekst if tekst.strip() else ""


def odcisk(xml: str) -> str:
    """SHA-256 samej TREŚCI: tytuł i HTML maila, tekst SMS, załączniki.

    Pomija wszystko, co panel zmienia bez zmiany treści (id elementu, data eksportu, włączniki active,
    ustawienia techniczne jak disposition, CDATA kontra encje). Zgodny z WT.odcisk w JS.
    """
    linie = []
    for kanal, wnetrze in re.findall(r'<contents message_type="(\w+)">(.*?)</contents>', xml, re.S):
        for pole, surowa in re.findall(r'<content type="(\w+)">(.*?)</content>', wnetrze, re.S):
            if pole in POLA_TRESCI:
                linie.append("%s.%s\x00%s" % (kanal, pole, _wartosc_pola(surowa)))
    zalaczniki = re.search(r"<enclosures>(.*?)</enclosures>", xml, re.S)
    linie.append("enclosures\x00" + (zalaczniki.group(1).strip() if zalaczniki else ""))
    return hashlib.sha256("\x01".join(linie).encode("utf-8")).hexdigest()
