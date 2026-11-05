# Zewnętrzne maszyny SI

Miejsce na zewnętrzne maszyny SI (agenci, serwery, narzędzia z osobnych repozytoriów), które będą podłączone do Domino przez git.

## Plan (do ustalenia przy pierwszej maszynie)

- Jedna maszyna = jeden folder `03_Zewnetrzne_SI/<nazwa>/`.
- Podłączenie: **submoduł git** (`git submodule add <url> SI/03_Zewnetrzne_SI/<nazwa>`) — wersja przypięta do commita, aktualizacja `git submodule update --remote`. Alternatywa: osobny klon wykluczony w `Domino\.gitignore`.
- Każda maszyna ma `README.md`: do czego służy, adres repozytorium, jak uruchomić, skąd bierze klucze (klucze nigdy w repo).
- Wpis w tabeli projektów w `SI/README.md`.
