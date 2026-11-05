"""Eksport i Import Treści: które pliki użytkownik zmienił i złożenie z nich ICF do importu."""

import os
from typing import Dict, List

from . import eksport, icf, wspolne

ND = "nie dotyczy"


def bez_cr(tekst: str) -> str:
    return tekst.replace("\r\n", "\n")


def _jak_oryginal(nowa: str, stara: str) -> str:
    """Zachowuje styl końców linii z panelu - edytor użytkownika mógł zamienić \\n na \\r\\n."""
    return nowa if "\r\n" in stara else bez_cr(nowa)


def roznice_tresci(katalog_eksportu: str, manifest: Dict) -> List[Dict]:
    wynik = []
    for w in manifest["wiadomosci"]:
        if not w["edytowalna"] or not w.get("pliki"):
            continue
        folder = eksport.folder_wiadomosci(katalog_eksportu, w)
        sciezka_meta = os.path.join(folder, "meta.json")
        meta = wspolne.czytaj_json(sciezka_meta) if os.path.exists(sciezka_meta) else {}
        tytuly = meta.get("tytuly", {})
        for jezyk in w["pliki"]:
            sciezka_icf = os.path.join(folder, jezyk + ".icf")
            # Wykluczony w edytorze („Usuń mail”) - przy „Zastosuj plan” ten język zostaje w sklepie bez zmian.
            if not os.path.exists(sciezka_icf) or jezyk in meta.get("wykluczone", []):
                continue
            dane = icf.wczytaj(wspolne.czytaj_tekst(sciezka_icf))
            pola, przed = {}, {}
            kandydaci = (("mail", "text_main_0", jezyk + "_mail.html"), ("sms", "text_main_0", jezyk + "_sms.txt"))
            for kanal, pole, nazwa_pliku in kandydaci:
                plik = os.path.join(folder, nazwa_pliku)
                if kanal not in dane["kanaly"] or w["stan_listy"].get(kanal) == ND or not os.path.exists(plik):
                    continue
                # BOM z edytora („UTF-8 z BOM”) nie jest treścią - nie zgłaszamy go jako zmiany i nie wgrywamy.
                nowa, stara = wspolne.czytaj_tekst(plik).lstrip("﻿"), dane["kanaly"][kanal].get(pole, "")
                if bez_cr(nowa) != bez_cr(stara):
                    pola[kanal + "." + pole] = _jak_oryginal(nowa, stara)
                    przed[kanal + "." + pole] = stara
            if "mail" in dane["kanaly"] and w["stan_listy"].get("mail") != ND and jezyk in tytuly:
                stary_tytul = dane["kanaly"]["mail"].get("title", "")
                if tytuly[jezyk] != stary_tytul:
                    pola["mail.title"] = tytuly[jezyk]
                    przed["mail.title"] = stary_tytul
            brak = [k for k in pola if k.split(".", 1)[1] not in dane["kanaly"][k.split(".", 1)[0]]]
            if brak:
                # Kanał bez pól (<contents message_type="mail"></contents>) - nigdy nie wypełniony w panelu;
                # import podmienia istniejące pola, nowej treści nie utworzy. Nie pomijamy zmiany po cichu.
                raise icf.BladIcf("„%s” (%s): ten %s jest w sklepie pusty (nigdy nie był wypełniony) - importem nie da się "
                                  "go utworzyć. Wypełnij go najpierw w panelu IdoSell albo cofnij zmianę w pliku %s."
                                  % (w["nazwa"], wspolne.nazwa_jezyka(jezyk), "SMS" if brak[0].startswith("sms") else "mail",
                                     os.path.join(os.path.basename(folder), jezyk + ("_sms.txt" if brak[0].startswith("sms") else "_mail.html"))))
            if pola:
                wynik.append({"template": w["template"], "nazwa": w["nazwa"], "grupa": w["grupa"], "jezyk": jezyk,
                              "icf": sciezka_icf, "pola": pola, "przed": przed})
    return wynik


def zloz(manifest: Dict, roznice: List[Dict], katalog_planu: str) -> str:
    po_template = {w["template"]: w for w in manifest["wiadomosci"]}
    plan = {"wersja": 1, "rodzaj": "import", "domena": manifest["domena"], "shop_id": manifest["shop_id"],
            "data_eksportu": manifest["data_eksportu"], "pozycje": [], "oczekiwane_flagi": {}}
    for r in roznice:
        oryginal = wspolne.czytaj_tekst(r["icf"])
        nowy = oryginal
        for klucz, wartosc in r["pola"].items():
            kanal, pole = klucz.split(".", 1)
            nowy = icf.podmien(nowy, kanal, pole, wartosc)
        nazwa = "%s__%s.icf" % (r["template"], r["jezyk"])
        wspolne.zapisz_tekst(os.path.join(katalog_planu, nazwa), nowy)
        plan["pozycje"].append({"template": r["template"], "nazwa": r["nazwa"], "jezyk": r["jezyk"], "plik": nazwa,
                                "odcisk_oryginalu": icf.odcisk(oryginal), "oczekiwane": r["pola"], "przed": r["przed"]})
        formularz = po_template[r["template"]]["formularz"]
        plan["oczekiwane_flagi"][r["template"]] = {"mail": dict(formularz["mail"]), "sms": formularz.get("sms")}
    sciezka = os.path.join(katalog_planu, "plan_importu.json")
    wspolne.zapisz_json(sciezka, plan)
    return sciezka
