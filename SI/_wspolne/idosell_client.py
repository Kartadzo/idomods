"""Minimalny klient REST API panelu IdoSell (Admin API v8+).

Bez zależności zewnętrznych - tylko biblioteka standardowa, żeby skrypty
w podfolderach uruchamiały się po dwukliku pliku .bat na czystym Pythonie.

Użycie:
    from idosell_client import IdoSellClient, wczytaj_konfiguracje

    cfg = wczytaj_konfiguracje()
    api = IdoSellClient(cfg["domena"], cfg["api_key"])
    status, dane = api.get("orders/orders")
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

SCIEZKA_KONFIGURACJI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# Kody, przy których ponawiamy żądanie (throttling / chwilowy błąd serwera).
KODY_DO_PONOWIENIA = (429, 500, 502, 503, 504)
LICZBA_PROB = 3
PRZERWA_MIEDZY_PROBAMI_S = 2.0


class BladApiIdoSell(Exception):
    """Błąd komunikacji z API, którego nie da się sensownie kontynuować."""


class IdoSellClient:
    """Klient bramek REST panelu administracyjnego IdoSell."""

    def __init__(self, domena: str, api_key: str, wersja: int = 8, timeout: int = 60) -> None:
        self.domena = self._normalizuj_domene(domena)
        self.api_key = api_key.strip()
        self.wersja = wersja
        self.timeout = timeout
        self.base_url = f"https://{self.domena}/api/admin/v{self.wersja}"

    @staticmethod
    def _normalizuj_domene(domena: str) -> str:
        """Przyjmuje 'clientXXX.idosell.com', 'https://clientXXX.idosell.com/' itp."""
        d = domena.strip()
        d = d.replace("https://", "").replace("http://", "")
        d = d.split("/")[0]
        return d.strip().rstrip(".")

    @staticmethod
    def _zbuduj_query(parametry: Optional[Dict[str, Any]]) -> str:
        """Listy skleja przecinkami: a=1,2,3.

        Tak wynika ze specyfikacji OpenAPI sklepu - parametry tablicowe mają
        `style: form, explode: false`. Powtórzony klucz (`a=1&a=2`) NIE działa:
        backend bierze wtedy wyłącznie ostatnią wartość i po cichu gubi resztę.
        """
        if not parametry:
            return ""
        pary: List[Tuple[str, str]] = []
        for klucz, wartosc in parametry.items():
            if wartosc is None:
                continue
            if isinstance(wartosc, (list, tuple, set)):
                elementy = [str(e) for e in wartosc]
                if elementy:
                    pary.append((klucz, ",".join(elementy)))
            elif isinstance(wartosc, bool):
                pary.append((klucz, "true" if wartosc else "false"))
            else:
                pary.append((klucz, str(wartosc)))
        return urllib.parse.urlencode(pary)

    def zbuduj_url(self, sciezka: str, parametry: Optional[Dict[str, Any]] = None) -> str:
        """Zwraca pełny URL żądania - przydatne do logowania w raportach."""
        query = self._zbuduj_query(parametry)
        url = f"{self.base_url}/{sciezka.lstrip('/')}"
        return f"{url}?{query}" if query else url

    def get(
        self, sciezka: str, parametry: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Any]:
        """Wykonuje GET i zwraca (kod_http, sparsowane_json_lub_tekst)."""
        url = self.zbuduj_url(sciezka, parametry)
        ostatni_blad: Optional[Exception] = None

        for proba in range(1, LICZBA_PROB + 1):
            zadanie = urllib.request.Request(url, method="GET")
            zadanie.add_header("X-API-KEY", self.api_key)
            zadanie.add_header("Accept", "application/json")
            zadanie.add_header("User-Agent", "IdoMods-API-Tools/1.0")
            try:
                with urllib.request.urlopen(zadanie, timeout=self.timeout) as odpowiedz:
                    surowa = odpowiedz.read().decode("utf-8", errors="replace")
                    return odpowiedz.getcode(), self._parsuj(surowa)
            except urllib.error.HTTPError as blad:
                surowa = blad.read().decode("utf-8", errors="replace")
                if blad.code in KODY_DO_PONOWIENIA and proba < LICZBA_PROB:
                    ostatni_blad = blad
                    time.sleep(PRZERWA_MIEDZY_PROBAMI_S * proba)
                    continue
                # 4xx/207 to nadal sensowna odpowiedź merytoryczna - zwracamy ją.
                return blad.code, self._parsuj(surowa)
            except urllib.error.URLError as blad:
                ostatni_blad = blad
                if proba < LICZBA_PROB:
                    time.sleep(PRZERWA_MIEDZY_PROBAMI_S * proba)
                    continue

        raise BladApiIdoSell(f"Nie udało się wykonać GET {url}: {ostatni_blad}")

    @staticmethod
    def _parsuj(surowa: str) -> Any:
        try:
            return json.loads(surowa)
        except json.JSONDecodeError:
            return {"_surowa_odpowiedz": surowa}


def wczytaj_konfiguracje(interaktywnie: bool = True) -> Dict[str, str]:
    """Wczytuje config.json; przy braku pyta o dane i zapisuje je na przyszłość."""
    if os.path.exists(SCIEZKA_KONFIGURACJI):
        try:
            with open(SCIEZKA_KONFIGURACJI, encoding="utf-8") as plik:
                cfg = json.load(plik)
            if cfg.get("domena") and cfg.get("api_key"):
                return cfg
            print("[!] config.json istnieje, ale brakuje w nim 'domena' lub 'api_key'.")
        except (OSError, json.JSONDecodeError) as blad:
            print(f"[!] Nie udało się odczytać {SCIEZKA_KONFIGURACJI}: {blad}")

    if not interaktywnie:
        raise BladApiIdoSell("Brak poprawnego config.json, a tryb nieinteraktywny.")

    print("\n--- Konfiguracja dostępu do API IdoSell ---")
    print("Domena panelu, np. client71.idosell.com (bez https:// i bez /api/...)")
    domena = input("Domena panelu: ").strip()
    api_key = input("Klucz API (nagłówek X-API-KEY): ").strip()
    if not domena or not api_key:
        raise BladApiIdoSell("Domena i klucz API są wymagane.")

    cfg = {"domena": domena, "api_key": api_key, "wersja_api": 8}
    try:
        with open(SCIEZKA_KONFIGURACJI, "w", encoding="utf-8") as plik:
            json.dump(cfg, plik, ensure_ascii=False, indent=2)
        print(f"[OK] Zapisano konfigurację: {SCIEZKA_KONFIGURACJI}")
        print("     (plik jest w .gitignore - nie trafi do repozytorium)")
    except OSError as blad:
        print(f"[!] Nie udało się zapisać konfiguracji: {blad}")
    return cfg


if __name__ == "__main__":
    # Szybki test połączenia: python idosell_client.py
    konfiguracja = wczytaj_konfiguracje()
    klient = IdoSellClient(konfiguracja["domena"], konfiguracja["api_key"])
    kod, tresc = klient.get("clients/balance", {"resultsLimit": 1})
    print(f"HTTP {kod}")
    print(json.dumps(tresc, ensure_ascii=False, indent=2)[:1500])
    sys.exit(0 if kod < 400 else 1)
