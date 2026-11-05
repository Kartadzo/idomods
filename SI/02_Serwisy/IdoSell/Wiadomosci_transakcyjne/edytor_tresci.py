"""Edytor treści wiadomości transakcyjnych - okno dla osób nietechnicznych.

Tytuł i HTML maila po polsku pogrupowane jak w panelu, podgląd w przeglądarce, „Usuń mail” (wykluczenie z importu)
i przygotowanie paczki do „Zastosuj plan”. Logika w wt/edytor.py; uruchom run_edytor.bat albo „Edytor treści.exe”.
"""

import os
import pathlib
import sys
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

from wt import edytor, wspolne

TYTUL_OKNA = "Edytor treści — wiadomości transakcyjne IdoSell"
CZCIONKA = ("Segoe UI", 10)
CZCIONKA_KODU = ("Consolas", 10)
KOLOR_ZNACZNIKA = "#1f5fbf"
TLO_ZMIENNEJ = "#fff3b0"


class Edytor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(TYTUL_OKNA)
        self.geometry("1280x800")
        self.minsize(960, 600)
        self.option_add("*Font", CZCIONKA)
        ttk.Style(self).configure("Treeview", rowheight=24)
        self.eksport = None          # edytor.Eksport
        self.wiadomosc = None        # bieżąca wiadomość (dict z manifestu)
        self.jezyk = tk.StringVar()
        self.wczytane = None         # (tytuł, HTML) w polach po wczytaniu/zapisie - do wykrycia niezapisanych zmian
        self._podswietl_po = None
        self._szukaj_po = None
        self._buduj()
        self.protocol("WM_DELETE_WINDOW", self._zamknij)
        self.bind("<Control-s>", lambda e: self._zapisz())
        self._wczytaj_liste_eksportow()

    # ---------- układ okna ----------

    def _buduj(self):
        gora = ttk.Frame(self, padding=(10, 8))
        gora.pack(fill="x")
        ttk.Label(gora, text="Eksport:").pack(side="left")
        self.wybor_eksportu = ttk.Combobox(gora, state="readonly", width=48)
        self.wybor_eksportu.pack(side="left", padx=6)
        self.wybor_eksportu.bind("<<ComboboxSelected>>", lambda e: self._zmien_eksport())
        self.opis_eksportu = ttk.Label(gora, foreground="#5a6b80")
        self.opis_eksportu.pack(side="left", padx=8)
        ttk.Button(gora, text="Otwórz folder eksportu", command=self._otworz_folder_eksportu).pack(side="right")

        podzial = ttk.PanedWindow(self, orient="horizontal")
        podzial.pack(fill="both", expand=True, padx=10)

        lewa = ttk.Frame(podzial)
        szukaj = ttk.Frame(lewa)
        szukaj.pack(fill="x", pady=(0, 6))
        ttk.Label(szukaj, text="Szukaj:").pack(side="left")
        self.fraza = tk.StringVar()
        self.fraza.trace_add("write", lambda *a: self._szukaj_z_opoznieniem())
        ttk.Entry(szukaj, textvariable=self.fraza).pack(side="left", fill="x", expand=True, padx=6)
        self.tylko_zmienione = tk.BooleanVar()
        ttk.Checkbutton(lewa, text="tylko zmienione i usunięte", variable=self.tylko_zmienione,
                        command=self._wypelnij_drzewo).pack(anchor="w", pady=(0, 6))
        ramka_drzewa = ttk.Frame(lewa)
        ramka_drzewa.pack(fill="both", expand=True)
        self.drzewo = ttk.Treeview(ramka_drzewa, show="tree", selectmode="browse")
        przewijak = ttk.Scrollbar(ramka_drzewa, orient="vertical", command=self.drzewo.yview)
        self.drzewo.configure(yscrollcommand=przewijak.set)
        self.drzewo.pack(side="left", fill="both", expand=True)
        przewijak.pack(side="right", fill="y")
        self.drzewo.bind("<<TreeviewSelect>>", lambda e: self._wybierz_wiadomosc())
        ttk.Label(lewa, text="✎ zmieniony   ⊘ usunięty z importu", foreground="#5a6b80").pack(anchor="w", pady=4)
        podzial.add(lewa, weight=1)

        prawa = ttk.Frame(podzial, padding=(12, 0, 0, 0))
        self.naglowek = ttk.Label(prawa, font=("Segoe UI", 13, "bold"), wraplength=760, justify="left")
        self.naglowek.pack(anchor="w")
        self.podtytul = ttk.Label(prawa, foreground="#5a6b80")
        self.podtytul.pack(anchor="w", pady=(0, 6))
        self.jezyki_ramka = ttk.Frame(prawa)
        self.jezyki_ramka.pack(fill="x")
        self.stan_jezyka = ttk.Label(prawa)
        self.stan_jezyka.pack(anchor="w", pady=(4, 8))

        ttk.Label(prawa, text="Tytuł maila (temat):").pack(anchor="w")
        self.tytul = ttk.Entry(prawa, font=CZCIONKA)
        self.tytul.pack(fill="x", pady=(2, 8))
        ttk.Label(prawa, text="Treść maila (kod HTML) — zmiennych w nawiasach [iai:…] nie tłumacz i nie usuwaj:").pack(anchor="w")
        ramka_kodu = ttk.Frame(prawa)
        ramka_kodu.pack(fill="both", expand=True, pady=(2, 8))
        self.kod = tk.Text(ramka_kodu, wrap="word", font=CZCIONKA_KODU, undo=True, maxundo=-1)
        przewijak_kodu = ttk.Scrollbar(ramka_kodu, orient="vertical", command=self.kod.yview)
        self.kod.configure(yscrollcommand=przewijak_kodu.set)
        self.kod.pack(side="left", fill="both", expand=True)
        przewijak_kodu.pack(side="right", fill="y")
        self.kod.tag_configure("znacznik", foreground=KOLOR_ZNACZNIKA)
        self.kod.tag_configure("zmienna", background=TLO_ZMIENNEJ)
        self.kod.bind("<<Modified>>", self._po_zmianie_kodu)

        przyciski = ttk.Frame(prawa)
        przyciski.pack(fill="x")
        self.p_zapisz = ttk.Button(przyciski, text="Zapisz  (Ctrl+S)", command=self._zapisz)
        self.p_podglad = ttk.Button(przyciski, text="Podgląd w przeglądarce", command=self._podglad)
        self.p_cofnij = ttk.Button(przyciski, text="Cofnij zmiany (treść ze sklepu)", command=self._cofnij)
        self.p_usun = ttk.Button(przyciski, text="Usuń mail z importu", command=self._usun_lub_przywroc)
        for p in (self.p_zapisz, self.p_podglad, self.p_cofnij):
            p.pack(side="left", padx=(0, 6))
        self.p_usun.pack(side="right")
        podzial.add(prawa, weight=3)

        dol = ttk.Frame(self, padding=(10, 8))
        dol.pack(fill="x")
        self.licznik = ttk.Label(dol)
        self.licznik.pack(side="left")
        ttk.Button(dol, text="Przygotuj paczkę do importu", command=self._przygotuj_paczke).pack(side="right")
        self.ostrzezenie = ttk.Label(self, foreground="#a15c00", padding=(10, 0, 10, 6), wraplength=1200)
        katalog = wspolne.pokaz(wspolne.KATALOG_GLOWNY)
        if len(katalog) > wspolne.LIMIT_KATALOGU:
            self.ostrzezenie.configure(text="Folder programu leży głęboko (%d znaków) — część plików może się nie otwierać "
                                            "w Notatniku i Chrome. Najlepiej przenieś cały folder np. do "
                                            "C:\\Wiadomosci_transakcyjne." % len(katalog))
            self.ostrzezenie.pack(fill="x")
        self._ustaw_edycje(False)

    # ---------- eksport i lista wiadomości ----------

    def _wczytaj_liste_eksportow(self):
        self.eksporty = edytor.lista_eksportow()
        if not self.eksporty:
            self.naglowek.configure(text="Brak rozpakowanych eksportów")
            self.podtytul.configure(text="Uruchom „Wiadomości transakcyjne.exe” → 1) Rozpakuj eksport, potem otwórz edytor ponownie.")
            return
        self.wybor_eksportu.configure(values=[e[0] for e in self.eksporty])
        self.wybor_eksportu.current(0)
        self._zmien_eksport()

    def _zmien_eksport(self):
        if not self._pozwol_porzucic():
            return
        katalog = self.eksporty[self.wybor_eksportu.current()][1]
        try:
            self.eksport = edytor.Eksport(katalog)
        except Exception as blad:
            messagebox.showerror(TYTUL_OKNA, "Nie da się otworzyć eksportu:\n%s" % wspolne.pokaz(blad))
            return
        self.opis_eksportu.configure(text=self.eksport.opis)
        self.wiadomosc = None
        self._pokaz_puste()
        self._wypelnij_drzewo()

    def _szukaj_z_opoznieniem(self):
        if self._szukaj_po:
            self.after_cancel(self._szukaj_po)
        self._szukaj_po = self.after(350, self._wypelnij_drzewo)

    def _znacznik(self, w):
        jezyki = self.eksport.jezyki(w)
        if any(self.eksport.wykluczony(w, j) for j in jezyki):
            return "  ⊘"
        if any(self.eksport.zmieniony(w, j) for j in jezyki):
            return "  ✎"
        return ""

    def _wypelnij_drzewo(self):
        self._szukaj_po = None
        if not self.eksport:
            return
        self.drzewo.delete(*self.drzewo.get_children())
        fraza = self.fraza.get().strip().lower()
        grupy = {}
        for w in self.eksport.wiadomosci():
            znacznik = self._znacznik(w)
            if fraza and fraza not in w["nazwa"].lower() and fraza not in (w.get("grupa_nazwa") or "").lower():
                continue
            if self.tylko_zmienione.get() and not znacznik:
                continue
            grupa = w.get("grupa_nazwa") or w["grupa"]
            if grupa not in grupy:
                grupy[grupa] = self.drzewo.insert("", "end", text=grupa, open=bool(fraza or self.tylko_zmienione.get()))
            self.drzewo.insert(grupy[grupa], "end", iid="w:" + w["template"], text=w["nazwa"] + znacznik)
        if self.wiadomosc and self.drzewo.exists("w:" + self.wiadomosc["template"]):
            iid = "w:" + self.wiadomosc["template"]
            self.drzewo.see(iid)
            self.drzewo.selection_set(iid)
        self.licznik.configure(text="Zmienione maile (trafią do paczki importu): %d" % self.eksport.liczba_zmian())

    def _odswiez_znacznik(self):
        iid = "w:" + self.wiadomosc["template"]
        if self.drzewo.exists(iid):
            self.drzewo.item(iid, text=self.wiadomosc["nazwa"] + self._znacznik(self.wiadomosc))
        self.licznik.configure(text="Zmienione maile (trafią do paczki importu): %d" % self.eksport.liczba_zmian())

    # ---------- wiadomość i język ----------

    def _wybierz_wiadomosc(self):
        zaznaczone = self.drzewo.selection()
        if not zaznaczone or not zaznaczone[0].startswith("w:"):
            return
        template = zaznaczone[0][2:]
        if self.wiadomosc and template == self.wiadomosc["template"]:
            return
        if not self._pozwol_porzucic():
            self.drzewo.selection_set("w:" + self.wiadomosc["template"])
            return
        self.wiadomosc = next(w for w in self.eksport.wiadomosci() if w["template"] == template)
        self.naglowek.configure(text=self.wiadomosc["nazwa"])
        self.podtytul.configure(text="%s · kod: %s" % (self.wiadomosc.get("grupa_nazwa") or self.wiadomosc["grupa"],
                                                       self.wiadomosc["template"]))
        for dziecko in self.jezyki_ramka.winfo_children():
            dziecko.destroy()
        jezyki = self.eksport.jezyki(self.wiadomosc)
        ttk.Label(self.jezyki_ramka, text="Język:").pack(side="left", padx=(0, 6))
        for j in jezyki:
            ttk.Radiobutton(self.jezyki_ramka, text=wspolne.nazwa_jezyka(j), value=j, variable=self.jezyk,
                            command=self._zmien_jezyk).pack(side="left", padx=(0, 10))
        poprzedni = self.jezyk.get()
        self.jezyk.set(poprzedni if poprzedni in jezyki else ("pol" if "pol" in jezyki else jezyki[0]))
        self._wczytaj_jezyk()

    def _zmien_jezyk(self):
        if self.wczytane and self.jezyk.get() != self._jezyk_w_polach and not self._pozwol_porzucic():
            self.jezyk.set(self._jezyk_w_polach)
            return
        self._wczytaj_jezyk()

    def _wczytaj_jezyk(self):
        w, j = self.wiadomosc, self.jezyk.get()
        self._jezyk_w_polach = j
        wykluczony = self.eksport.wykluczony(w, j)
        tytul, kod = self.eksport.oryginal(w, j) if wykluczony else self.eksport.tresc(w, j)
        self._ustaw_edycje(True)
        self.tytul.delete(0, "end")
        self.tytul.insert(0, tytul)
        self.kod.delete("1.0", "end")
        self.kod.insert("1.0", kod)
        self.kod.edit_reset()
        self.kod.edit_modified(False)
        self._podswietl()
        self.wczytane = (tytul, kod)
        self._pokaz_stan_jezyka()

    def _pokaz_stan_jezyka(self):
        w, j = self.wiadomosc, self.jezyk.get()
        wykluczony = self.eksport.wykluczony(w, j)
        wysylka = "wysyłka w sklepie: " + ("włączona" if self.eksport.wysylka(w, j) else "wyłączona")
        if self.eksport.pusty_w_sklepie(w, j):
            self.stan_jezyka.configure(text="Ten mail jest w sklepie pusty (nigdy nie był wypełniony) — import nie potrafi "
                                            "utworzyć nowej treści. Wypełnij go najpierw w panelu IdoSell i zrób nowy eksport.",
                                       foreground="#a15c00")
            self._ustaw_edycje(True, tylko_odczyt=True)
            self.p_usun.configure(state="disabled")
            return
        if wykluczony:
            self.stan_jezyka.configure(text="⊘ Usunięty z importu — przy „Zastosuj plan” ten mail zostanie w sklepie bez zmian. "
                                            "Poniżej treść ze sklepu (tylko do odczytu).   " + wysylka, foreground="#a12b2b")
        elif self.eksport.zmieniony(w, j):
            self.stan_jezyka.configure(text="✎ Zmieniony — trafi do paczki importu.   " + wysylka, foreground="#1f6b2f")
        else:
            self.stan_jezyka.configure(text="Bez zmian.   " + wysylka, foreground="#5a6b80")
        self._ustaw_edycje(True, tylko_odczyt=wykluczony)
        self.p_usun.configure(text="Przywróć mail do importu" if wykluczony else "Usuń mail z importu")

    def _pokaz_puste(self):
        self.naglowek.configure(text="Wybierz wiadomość z listy po lewej")
        self.podtytul.configure(text="")
        self.stan_jezyka.configure(text="")
        for dziecko in self.jezyki_ramka.winfo_children():
            dziecko.destroy()
        self.tytul.configure(state="normal")
        self.tytul.delete(0, "end")
        self.kod.configure(state="normal")
        self.kod.delete("1.0", "end")
        self.wczytane = None
        self._ustaw_edycje(False)

    def _ustaw_edycje(self, aktywne, tylko_odczyt=False):
        edycja = "normal" if aktywne and not tylko_odczyt else "disabled"
        self.tytul.configure(state=edycja)
        self.kod.configure(state=edycja, background="#ffffff" if edycja == "normal" else "#f3f3f3")
        for p in (self.p_zapisz, self.p_cofnij):
            p.configure(state=edycja)
        for p in (self.p_podglad, self.p_usun):
            p.configure(state="normal" if aktywne else "disabled")

    # ---------- podświetlanie kodu ----------

    def _po_zmianie_kodu(self, _zdarzenie=None):
        if self.kod.edit_modified():
            self.kod.edit_modified(False)
            if self._podswietl_po:
                self.after_cancel(self._podswietl_po)
            self._podswietl_po = self.after(300, self._podswietl)

    def _podswietl(self):
        self._podswietl_po = None
        tekst = self.kod.get("1.0", "end-1c")
        for tag in ("znacznik", "zmienna"):
            self.kod.tag_remove(tag, "1.0", "end")
        for wzor, tag in ((edytor._ZNACZNIK, "znacznik"), (edytor.status.WZOR_ZMIENNEJ, "zmienna")):
            for m in wzor.finditer(tekst):
                self.kod.tag_add(tag, "1.0+%dc" % m.start(), "1.0+%dc" % m.end())

    # ---------- akcje ----------

    def _pola(self):
        return self.tytul.get(), self.kod.get("1.0", "end-1c")

    def _niezapisane(self):
        if not self.wczytane or self.eksport.wykluczony(self.wiadomosc, self._jezyk_w_polach):
            return False
        return self._pola() != self.wczytane

    def _pozwol_porzucic(self):
        """True, gdy można zmienić wiadomość/język/eksport (zapisano albo użytkownik porzucił zmiany)."""
        if not self._niezapisane():
            return True
        odp = messagebox.askyesnocancel(TYTUL_OKNA, "Masz niezapisane zmiany w „%s” (%s). Zapisać?"
                                        % (self.wiadomosc["nazwa"], wspolne.nazwa_jezyka(self._jezyk_w_polach)))
        if odp is None:
            return False
        return self._zapisz() if odp else True

    def _tylko_odczyt(self):
        w, j = self.wiadomosc, self._jezyk_w_polach
        return self.eksport.wykluczony(w, j) or self.eksport.pusty_w_sklepie(w, j)

    def _zapisz(self):
        if not self.wczytane or self._tylko_odczyt():
            return False
        w, j = self.wiadomosc, self._jezyk_w_polach
        tytul, kod = self._pola()
        t0, h0 = self.eksport.oryginal(w, j)
        brak_t, nadm_t = edytor.roznica_zmiennych(t0, tytul)
        brak_h, nadm_h = edytor.roznica_zmiennych(h0, kod)
        uwagi = []
        if brak_t or brak_h:
            uwagi.append("Brakuje zmiennych, które są w treści ze sklepu:\n  " + ", ".join(brak_t + brak_h))
        if nadm_t or nadm_h:
            uwagi.append("Nowe zmienne, których nie było w treści ze sklepu:\n  " + ", ".join(nadm_t + nadm_h))
        if uwagi and not messagebox.askyesno(TYTUL_OKNA, "\n\n".join(uwagi) + "\n\nZmienne panel podstawia przy wysyłce "
                                             "(numer zamówienia, nazwa sklepu…). Zapisać mimo to?", icon="warning"):
            return False
        try:
            self.eksport.zapisz(w, j, tytul, kod)
        except OSError as blad:
            messagebox.showerror(TYTUL_OKNA, "Nie udało się zapisać:\n%s" % wspolne.pokaz(blad))
            return False
        self.wczytane = (tytul, kod)
        self._pokaz_stan_jezyka()
        self._odswiez_znacznik()
        return True

    def _podglad(self):
        if not self.wczytane:
            return
        tytul, kod = self._pola()
        opis = "%s (%s)" % (self.wiadomosc["nazwa"], wspolne.nazwa_jezyka(self._jezyk_w_polach))
        sciezka = edytor.plik_podgladu(tytul, kod, opis)
        webbrowser.open(pathlib.Path(wspolne.pokaz(sciezka)).as_uri())

    def _cofnij(self):
        if not self.wczytane:
            return
        if not messagebox.askyesno(TYTUL_OKNA, "Przywrócić tytuł i treść ze sklepu (z chwili eksportu)?\n"
                                               "Twoje zmiany w tym języku przepadną."):
            return
        self.eksport.cofnij(self.wiadomosc, self._jezyk_w_polach)
        self._wczytaj_jezyk()
        self._odswiez_znacznik()

    def _usun_lub_przywroc(self):
        w, j = self.wiadomosc, self._jezyk_w_polach
        nazwa = "„%s” (%s)" % (w["nazwa"], wspolne.nazwa_jezyka(j))
        if self.eksport.wykluczony(w, j):
            self.eksport.przywroc(w, j)
        else:
            if not messagebox.askyesno(TYTUL_OKNA, "Usunąć mail %s z importu?\n\nPrzy „Zastosuj plan” ten mail zostanie "
                                                   "w sklepie bez zmian. W sklepie nic nie jest kasowane, a mail możesz "
                                                   "później przywrócić tym samym przyciskiem." % nazwa):
                return
            self.eksport.wyklucz(w, j)
        self._wczytaj_jezyk()
        self._odswiez_znacznik()

    def _przygotuj_paczke(self):
        if not self.eksport or not self._pozwol_porzucic():
            return
        roznice = edytor.tresci.roznice_tresci(self.eksport.katalog, self.eksport.manifest)
        if not roznice:
            messagebox.showinfo(TYTUL_OKNA, "Brak zmienionych maili — nie ma czego importować.")
            return
        po_nazwie = {w["template"]: w["nazwa"] for w in self.eksport.manifest["wiadomosci"]}
        lista = "\n".join("  • %s (%s)" % (po_nazwie.get(r["template"], r["template"]), wspolne.nazwa_jezyka(r["jezyk"]))
                          for r in roznice[:25])
        if len(roznice) > 25:
            lista += "\n  … i %d więcej" % (len(roznice) - 25)
        if not messagebox.askyesno(TYTUL_OKNA, "Liczba maili w paczce importu: %d\n\n%s\n\nPrzygotować paczkę?"
                                               % (len(roznice), lista)):
            return
        try:
            katalog_planu, _ = self.eksport.przygotuj_paczke()
        except Exception as blad:
            messagebox.showerror(TYTUL_OKNA, "Nie udało się przygotować paczki:\n%s" % wspolne.pokaz(blad))
            return
        folder = wspolne.pokaz(katalog_planu)
        self.clipboard_clear()
        self.clipboard_append(folder)
        if messagebox.askyesno(TYTUL_OKNA, "Paczka gotowa:\n%s\n\n(ścieżka skopiowana do schowka)\n\nW panelu IdoSell: "
                                           "zakładka → „Zastosuj plan…” → wskaż ten folder.\n\nOtworzyć folder teraz?" % folder):
            self._otworz(katalog_planu)

    def _otworz_folder_eksportu(self):
        if self.eksport:
            self._otworz(self.eksport.katalog)

    def _otworz(self, sciezka):
        try:
            os.startfile(wspolne.pokaz(sciezka))
        except OSError as blad:
            messagebox.showerror(TYTUL_OKNA, "Nie udało się otworzyć folderu:\n%s" % wspolne.pokaz(blad))

    def _zamknij(self):
        if self._pozwol_porzucic():
            self.destroy()


def main():
    try:
        Edytor().mainloop()
    except Exception as blad:   # w .exe bez konsoli błąd musi być widoczny
        messagebox.showerror(TYTUL_OKNA, "Nieoczekiwany błąd programu:\n%s" % wspolne.pokaz(blad))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
