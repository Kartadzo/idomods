"""Weryfikacja planu po wykonaniu w panelu: porównanie eksportu weryfikacyjnego z oczekiwanym stanem."""

import os
from typing import Dict, List, Optional

from . import eksport, icf, tresci, wspolne

OK = "OK"
BEZ_ZMIAN = "nie zmieniło się"
INACZEJ = "zmieniło się inaczej"
BRAK = "brak w eksporcie weryfikacyjnym"


def _icf_po(katalog_po: str, wiadomosc: Optional[Dict], jezyk: str) -> Optional[str]:
    if wiadomosc is None:
        return None
    sciezka = os.path.join(eksport.folder_wiadomosci(katalog_po, wiadomosc), jezyk + ".icf")
    return wspolne.czytaj_tekst(sciezka) if os.path.exists(sciezka) else None


def _wynik(template, nazwa, jezyk, co, wynik, szczegoly=""):
    return {"template": template, "nazwa": nazwa, "jezyk": jezyk, "co": co, "wynik": wynik, "szczegoly": szczegoly}


def _flagi(template, nazwa, oczekiwane: Dict, wiadomosc: Optional[Dict], zmienione: Dict) -> List[Dict]:
    """zmienione: {jezyk: flaga} zamówione w planie - dla nich BEZ_ZMIAN zamiast INACZEJ, gdy panel ich nie przyjął."""
    wyniki = []
    formularz = (wiadomosc or {}).get("formularz") or {}
    for jezyk, flaga in sorted(oczekiwane.get("mail", {}).items()):
        jest = (formularz.get("mail") or {}).get(jezyk)
        if jest == flaga:
            wynik = OK
        else:
            wynik = BEZ_ZMIAN if jezyk in zmienione else INACZEJ
        wyniki.append(_wynik(template, nazwa, jezyk, "flaga mail " + jezyk, wynik, "oczekiwano %s, jest %s" % (flaga, jest)))
    if oczekiwane.get("sms") is not None:
        jest = formularz.get("sms")
        wynik = OK if jest == oczekiwane["sms"] else (BEZ_ZMIAN if "sms" in zmienione else INACZEJ)
        wyniki.append(_wynik(template, nazwa, "*", "flaga sms", wynik, "oczekiwano %s, jest %s" % (oczekiwane["sms"], jest)))
    return wyniki


def weryfikuj(plan: Dict, manifest_po: Dict, katalog_po: str) -> List[Dict]:
    po = {w["template"]: w for w in manifest_po["wiadomosci"]}
    wyniki = []
    if plan["rodzaj"] == "import":
        for p in plan["pozycje"]:
            xml = _icf_po(katalog_po, po.get(p["template"]), p["jezyk"])
            if xml is None:
                wyniki.append(_wynik(p["template"], p["nazwa"], p["jezyk"], "plik ICF", BRAK))
                continue
            dane = icf.wczytaj(xml)
            for klucz, oczekiwana in p["oczekiwane"].items():
                kanal, pole = klucz.split(".", 1)
                jest = tresci.bez_cr(icf.wartosc(dane, kanal, pole) or "")
                if jest == tresci.bez_cr(oczekiwana):
                    wynik = OK
                elif jest == tresci.bez_cr(p["przed"].get(klucz, "")):
                    wynik = BEZ_ZMIAN
                else:
                    wynik = INACZEJ
                wyniki.append(_wynik(p["template"], p["nazwa"], p["jezyk"], klucz, wynik,
                                     "" if wynik == OK else "jest: %s" % jest[:120]))
        # Import ICF wyłącza mail, a narzędzie przywraca flagi sprzed importu - wzorcem jest więc odczyt
        # z panelu tuż przed importem (zapisany w eksporcie weryfikacyjnym), a nie stan z eksportu źródłowego.
        przed_importem = manifest_po.get("flagi_przed_importem") or {}
        inny_sklep = (manifest_po["domena"], manifest_po["shop_id"]) != (plan["domena"], plan["shop_id"])
        for template, oczekiwane in plan["oczekiwane_flagi"].items():
            nazwa = (po.get(template) or {}).get("nazwa", template)
            if template in przed_importem:
                oczekiwane = przed_importem[template]
            elif inny_sklep:
                wyniki.append(_wynik(template, nazwa, "*", "flagi", BRAK,
                                     "migracja: brak odczytu flag sprzed importu - sprawdź włączniki wysyłki w panelu"))
                continue
            wyniki += [w for w in _flagi(template, nazwa, oczekiwane, po.get(template), {}) if w["wynik"] != OK]
    else:
        for z in plan["zmiany"]:
            w_po = po.get(z["template"])
            zmienione = dict(z["mail"])
            if z["sms"] is not None:
                zmienione["sms"] = z["sms"]
            wyniki += _flagi(z["template"], z["nazwa"], z["oczekiwane"], w_po, zmienione)
            for jezyk, kopia in sorted(z["kopie"].items()):
                xml = _icf_po(katalog_po, w_po, jezyk)
                if xml is None:
                    wyniki.append(_wynik(z["template"], z["nazwa"], jezyk, "treść", BRAK))
                    continue
                zgodna = icf.odcisk(xml) == kopia["odcisk"]
                wyniki.append(_wynik(z["template"], z["nazwa"], jezyk, "treść", OK if zgodna else INACZEJ,
                                     "" if zgodna else "treść różni się od kopii sprzed zmiany"))
            if z["reset"]:
                wyniki.append(_wynik(z["template"], z["nazwa"], "*", "reset do treści domyślnej", BEZ_ZMIAN,
                                     "krok ręczny - sprawdź w panelu"))
    return wyniki


def nazwa_raportu(plan: Dict) -> str:
    return "%s_%s.md" % ("import" if plan["rodzaj"] == "import" else "konfiguracja",
                         wspolne.znacznik_daty(wspolne.teraz_iso()))


def raport(plan: Dict, wyniki: List[Dict]) -> str:
    problemy = [w for w in wyniki if w["wynik"] != OK]
    linie = ["# Weryfikacja: %s — %s, sklep %s" % ("import treści" if plan["rodzaj"] == "import" else "zmiany konfiguracji",
                                                  plan["domena"], plan["shop_id"]), "",
             "Sprawdzono: %s · OK: %d · Problemy: %d" % (wspolne.teraz_iso(), len(wyniki) - len(problemy), len(problemy)), "",
             "| Wiadomość | Język | Co | Wynik | Szczegóły |", "| --- | --- | --- | --- | --- |"]
    for w in sorted(wyniki, key=lambda x: (x["wynik"] == OK, x["template"], x["jezyk"], x["co"])):
        linie.append("| %s (`%s`) | %s | %s | %s | %s |" % (
            w["nazwa"].replace("|", "\\|"), w["template"], w["jezyk"], w["co"],
            "**%s**" % w["wynik"] if w["wynik"] != OK else w["wynik"], w["szczegoly"].replace("|", "\\|")))
    return "\n".join(linie) + "\n"
