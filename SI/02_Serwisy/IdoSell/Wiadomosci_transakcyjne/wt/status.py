"""Raport Status: stan wysyłki, braki, ostatnia edycja i kontrola jakości treści (.md + .csv do Excela)."""

import csv
import io
import os
import re
import unicodedata
from typing import Dict, List, Tuple

from . import eksport, icf, wspolne

WZOR_ZMIENNEJ = re.compile(r"\[iai:[^\]\s]+\]")
# Podstawowy alfabet GSM 03.38 - spoza niego SMS idzie w UCS-2 (70 znaków na segment).
GSM7 = set("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?¡"
           "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà")
POLA = (("mail", "title", "tytuł maila"), ("mail", "text_main_0", "treść maila"), ("sms", "text_main_0", "treść SMS"))
IDENTYCZNY = {"tytuł maila": "identyczny", "treść maila": "identyczna", "treść SMS": "identyczna"}
ETYKIETY = {"kopia": "Kopie tłumaczeń (treść identyczna z PL lub EN)", "zmienne": "Niezgodne zmienne [iai:…]",
            "pusta": "Pusta treść przy włączonej wysyłce", "sms": "SMS dłuższy niż jeden segment"}


def _norm(tekst) -> str:
    return re.sub(r"\s+", " ", tekst or "").strip()


def zmienne(tekst) -> set:
    return set(WZOR_ZMIENNEJ.findall(tekst or ""))


def _na_ascii(tekst: str) -> str:
    tekst = tekst.replace("ł", "l").replace("Ł", "L")
    return unicodedata.normalize("NFKD", tekst).encode("ascii", "ignore").decode("ascii")


def dlugosc_sms(tekst: str, only_ascii) -> Tuple[int, int]:
    """Długość bez zmiennych [iai:…] - panel podmienia je przed wysyłką, ich długości nie znamy."""
    tekst = WZOR_ZMIENNEJ.sub("", tekst)
    tekst = _na_ascii(tekst) if only_ascii == "y" else tekst
    limit = 160 if all(znak in GSM7 for znak in tekst) else 70
    return len(tekst), limit


def _wzorce_kopii(jezyk: str) -> Tuple[str, ...]:
    if jezyk == "pol":
        return ()
    if jezyk == "eng":
        return ("pol",)
    return ("pol", "eng")


def kontrola(manifest: Dict, katalog: str) -> List[Dict]:
    problemy = []
    for w in manifest["wiadomosci"]:
        if not w["edytowalna"] or not w.get("pliki"):
            continue
        folder = eksport.folder_wiadomosci(katalog, w)
        tresci = {}
        for jezyk in w["pliki"]:
            sciezka = os.path.join(folder, jezyk + ".icf")
            if os.path.exists(sciezka):
                tresci[jezyk] = icf.wczytaj(wspolne.czytaj_tekst(sciezka))

        def dodaj(jezyk, rodzaj, opis):
            problemy.append({"template": w["template"], "nazwa": w["nazwa"], "jezyk": jezyk, "rodzaj": rodzaj, "opis": opis})

        wzorzec_zmiennych = "pol" if "pol" in tresci else (sorted(tresci)[0] if tresci else None)
        for jezyk, dane in tresci.items():
            for wzorzec in _wzorce_kopii(jezyk):
                if wzorzec not in tresci:
                    continue
                for kanal, pole, etykieta in POLA:
                    a = _norm(icf.wartosc(dane, kanal, pole))
                    if a and a == _norm(icf.wartosc(tresci[wzorzec], kanal, pole)):
                        dodaj(jezyk, "kopia", "%s: %s z %s" % (etykieta, IDENTYCZNY[etykieta], wzorzec))
            if jezyk != wzorzec_zmiennych:
                for kanal, pole, etykieta in POLA:
                    if kanal not in dane["kanaly"]:
                        continue
                    wzor = zmienne(icf.wartosc(tresci[wzorzec_zmiennych], kanal, pole))
                    jest = zmienne(icf.wartosc(dane, kanal, pole))
                    if wzor - jest:
                        dodaj(jezyk, "zmienne", "%s: brakuje %s (są w %s)" % (etykieta, ", ".join(sorted(wzor - jest)), wzorzec_zmiennych))
                    if jest - wzor:
                        dodaj(jezyk, "zmienne", "%s: nadmiarowe %s (nie ma ich w %s)" % (etykieta, ", ".join(sorted(jest - wzor)), wzorzec_zmiennych))
            formularz = w["formularz"] or {}
            if formularz.get("mail", {}).get(jezyk) == "y" and "mail" in dane["kanaly"]:
                for pole, etykieta in (("title", "tytuł maila"), ("text_main_0", "treść maila")):
                    if not _norm(icf.wartosc(dane, "mail", pole)):
                        dodaj(jezyk, "pusta", "mail włączony, %s pusta" % etykieta)
            if "sms" in dane["kanaly"]:
                tekst_sms = icf.wartosc(dane, "sms", "text_main_0") or ""
                if formularz.get("sms") == "y" and not _norm(tekst_sms):
                    dodaj(jezyk, "pusta", "SMS włączony, treść SMS pusta")
                if formularz.get("sms") == "y" and _norm(tekst_sms):   # tylko SMS-y faktycznie wysyłane
                    dlugosc, limit = dlugosc_sms(tekst_sms, icf.wartosc(dane, "sms", "only_ascii"))
                    if dlugosc > limit:
                        dodaj(jezyk, "sms", "%d znaków > %d (więcej niż 1 SMS; bez rozwinięcia zmiennych)" % (dlugosc, limit))
    return problemy


def _kom(tekst) -> str:
    return str(tekst if tekst is not None else "").replace("|", "\\|")


def _flaga(wartosc) -> str:
    return {"y": "tak", "n": "nie"}.get(wartosc, "n.d.")


def raport(manifest: Dict, katalog: str) -> str:
    jezyki = manifest["jezyki"]
    wszystkie = manifest["wiadomosci"]
    edytowalne = [w for w in wszystkie if w["edytowalna"] and w.get("formularz")]
    problemy = kontrola(manifest, katalog)
    linie = ["# Status wiadomości transakcyjnych — %s, sklep %s" % (manifest["domena"], manifest["shop_id"]), "",
             "Eksport: %s · Raport: %s" % (manifest["data_eksportu"], wspolne.teraz_iso()), ""]
    if manifest.get("niekompletny"):
        linie += ["> **Uwaga:** eksport niekompletny — brakuje %d wiadomości (sesja wygasła). "
                  "Uruchom eksport ponownie i rozpakuj obie części razem." % len(manifest.get("pozostale", [])), ""]
    linie += ["## Podsumowanie", "", "| | Liczba |", "| --- | --- |",
              "| Wiadomości ogółem | %d |" % len(wszystkie),
              "| Edytowalne | %d |" % len(edytowalne),
              "| Wycofywane (tylko podgląd) | %d |" % (len(wszystkie) - len([w for w in wszystkie if w["edytowalna"]]))]
    for j in jezyki:
        linie.append("| Mail włączony — %s | %d |" % (j, sum(1 for w in edytowalne if w["formularz"]["mail"].get(j) == "y")))
    linie.append("| SMS włączony | %d |" % sum(1 for w in edytowalne if w["formularz"].get("sms") == "y"))
    for j in jezyki:
        linie.append("| Web Push włączony — %s | %d |" % (j, sum(1 for w in edytowalne if (w["formularz"].get("webpush") or {}).get(j) == "y")))
    linie += ["| Z brakami szablonów | %d |" % sum(1 for w in wszystkie if w["stan_listy"].get("braki")),
              "| Problemy kontroli jakości | %d |" % len(problemy), "",
              "## Wiadomości", "",
              "| Grupa | Wiadomość | " + " | ".join("Mail " + j for j in jezyki) + " | SMS | Web Push | Braki | Ostatnia edycja |",
              "| --- | --- | " + " | ".join("---" for _ in jezyki) + " | --- | --- | --- | --- |"]
    for w in wszystkie:
        f = w.get("formularz") or {}
        nazwa = _kom(w["nazwa"]) + ("" if w["edytowalna"] else " _(wycofywana)_")
        maile = [_flaga((f.get("mail") or {}).get(j)) if f else _kom(w["stan_listy"].get("mail")) for j in jezyki]
        webpush = ", ".join(j for j, v in sorted((f.get("webpush") or {}).items()) if v == "y") or "—"
        edycja = w.get("ostatnia_edycja")
        linie.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            _kom(w.get("grupa_nazwa") or w["grupa"]), nazwa, " | ".join(maile),
            _flaga(f.get("sms")) if f else _kom(w["stan_listy"].get("sms")), webpush,
            _kom(w["stan_listy"].get("braki") or "—"),
            "%s (%s)" % (_kom(edycja["data"]), _kom(edycja["autor"])) if edycja else "—"))
    linie += ["", "> Import ICF nie zostawia wpisu w historii zmian panelu — data ostatniej edycji pomija importy.",
              "", "## Kontrola jakości", ""]
    if not problemy:
        linie.append("Brak problemów.")
    for rodzaj in ("kopia", "zmienne", "pusta", "sms"):
        grupa = [p for p in problemy if p["rodzaj"] == rodzaj]
        if not grupa:
            continue
        linie += ["### %s (%d)" % (ETYKIETY[rodzaj], len(grupa)), ""]
        linie += ["- **%s** (`%s`), %s: %s" % (_kom(p["nazwa"]), p["template"], p["jezyk"], p["opis"]) for p in grupa]
        linie.append("")
    bledy = [(w, b) for w in wszystkie for b in w.get("bledy", [])]
    if bledy:
        linie += ["## Błędy eksportu", ""] + ["- **%s** (`%s`): %s" % (_kom(w["nazwa"]), w["template"], b) for w, b in bledy]
    return "\n".join(linie) + "\n"


def _flaga_csv(wartosc) -> str:
    return {"y": "tak", "n": "nie"}.get(wartosc, "nie dotyczy")


def _opis_problemu(problem: Dict, jezyki: List[str]) -> str:
    """'ger', 'tytuł maila: identyczny z pol' -> 'niemiecki: tytuł maila: identyczny jak w wersji: polski'."""
    opis = problem["opis"]
    for kod in jezyki:
        nazwa = wspolne.nazwa_jezyka(kod)
        opis = re.sub(r"\bz %s\b" % re.escape(kod), "jak w wersji: " + nazwa, opis)
        opis = re.sub(r"\bw %s\b" % re.escape(kod), "w wersji: " + nazwa, opis)
    return "%s: %s" % (wspolne.nazwa_jezyka(problem["jezyk"]), opis)


def wiersze_csv(manifest: Dict, katalog: str) -> List[List]:
    """Dwie części: status ogólny zgrupowany do grup panelu, pusta linia, tabela wiadomości."""
    jezyki = manifest["jezyki"]
    wszystkie = manifest["wiadomosci"]
    problemy = kontrola(manifest, katalog)
    po_template = {}
    for p in problemy:
        po_template.setdefault(p["template"], []).append(p)
    grupy = {}
    for w in wszystkie:
        grupy.setdefault(w.get("grupa_nazwa") or w["grupa"], []).append(w)

    def podsumuj(nazwa, lista):
        edytowalne = [w for w in lista if w["edytowalna"] and w.get("formularz")]
        return ([nazwa, len(lista), len(edytowalne), sum(1 for w in lista if not w["edytowalna"])]
                + [sum(1 for w in edytowalne if w["formularz"]["mail"].get(j) == "y") for j in jezyki]
                + [sum(1 for w in edytowalne if w["formularz"].get("sms") == "y"),
                   sum(1 for w in edytowalne if "y" in (w["formularz"].get("webpush") or {}).values()),
                   sum(1 for w in lista if w["stan_listy"].get("braki")),
                   sum(len(po_template.get(w["template"], [])) for w in lista)])

    wiersze = [["Status wiadomości transakcyjnych", "%s, sklep %s" % (manifest["domena"], manifest["shop_id"]),
                "eksport z %s" % manifest["data_eksportu"].replace("T", " ")]]
    if manifest.get("niekompletny"):
        wiersze.append(["UWAGA", "eksport niekompletny - brakuje %d wiadomości" % len(manifest.get("pozostale", []))])
    wiersze += [[], ["STATUS OGÓLNY (wg grup)"],
                ["Grupa", "Wiadomości", "Edytowalne", "Wycofywane"]
                + ["Mail %s włączony" % wspolne.nazwa_jezyka(j) for j in jezyki]
                + ["SMS włączony", "Web Push włączony", "Z brakami szablonów", "Problemy kontroli jakości"]]
    wiersze += [podsumuj(nazwa, lista) for nazwa, lista in grupy.items()]
    wiersze += [podsumuj("RAZEM", wszystkie), [], ["WIADOMOŚCI"],
                ["Grupa", "Wiadomość"] + ["Mail %s" % wspolne.nazwa_jezyka(j) for j in jezyki]
                + ["SMS", "Web Push", "Wycofywana", "Braki szablonów", "Ostatnia edycja", "Kto edytował",
                   "Problemy (liczba)", "Problemy (opis)", "Kod wiadomości"]]
    for w in wszystkie:
        f = w.get("formularz") or {}
        maile = [_flaga_csv((f.get("mail") or {}).get(j)) if f else (w["stan_listy"].get("mail") or "") for j in jezyki]
        webpush = ", ".join(wspolne.nazwa_jezyka(j) for j, v in sorted((f.get("webpush") or {}).items()) if v == "y")
        edycja = w.get("ostatnia_edycja") or {}
        lista = po_template.get(w["template"], [])
        wiersze.append([w.get("grupa_nazwa") or w["grupa"], w["nazwa"]] + maile
                       + [_flaga_csv(f.get("sms")) if f else (w["stan_listy"].get("sms") or ""), webpush or "nie",
                          "nie" if w["edytowalna"] else "tak", w["stan_listy"].get("braki") or "",
                          edycja.get("data", ""), edycja.get("autor", ""), len(lista),
                          "; ".join(_opis_problemu(p, jezyki) for p in lista), w["template"]])
    return wiersze


def raport_csv(manifest: Dict, katalog: str) -> str:
    bufor = io.StringIO()
    csv.writer(bufor, delimiter=";", lineterminator="\r\n").writerows(wiersze_csv(manifest, katalog))
    return "\ufeff" + bufor.getvalue()   # BOM: Excel otwiera dwuklikiem z polskimi znakami


def sciezka_raportu(manifest: Dict, rozszerzenie: str = ".md") -> str:
    return os.path.join(wspolne.FOLDER_STATUS, wspolne.id_sklepu(manifest["domena"], manifest["shop_id"]),
                        "status_" + wspolne.znacznik_daty(manifest["data_eksportu"]) + rozszerzenie)


def zapisz_raport(manifest: Dict, katalog: str) -> Tuple[str, str]:
    """Zapisuje raport .md i .csv; zwraca obie ścieżki."""
    sciezka_md, sciezka_csv = sciezka_raportu(manifest), sciezka_raportu(manifest, ".csv")
    wspolne.zapisz_tekst(sciezka_md, raport(manifest, katalog))
    wspolne.zapisz_tekst(sciezka_csv, raport_csv(manifest, katalog))
    return sciezka_md, sciezka_csv
