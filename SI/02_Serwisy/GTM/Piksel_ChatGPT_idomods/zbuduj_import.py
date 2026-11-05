# -*- coding: utf-8 -*-
"""Składa plik importu GTM (GTM_import_chatgpt_idomods.json) z kodu tagów w tagi/*.html.

Uruchomienie (z dowolnego miejsca): python zbuduj_import.py
Po zmianie kodu tagu w tagi/ uruchom ponownie i zaimportuj (Scal) albo wklej kod ręcznie w GTM.
"""
import json
import os
from datetime import datetime

KATALOG = os.path.dirname(os.path.abspath(__file__))
WYJSCIE = os.path.join(KATALOG, "GTM_import_chatgpt_idomods.json")

ACC = "0"
CON = "0"

# Wbudowane wyzwalacze GTM (stałe ID).
TRG_INITIALIZATION = "2147479573"  # Initialization - All Pages
TRG_ALL_PAGES = "2147479553"       # All Pages (Page View)

TRG_CMPLZ_MARKETING = "101"
TRG_KLIK_KONTAKT = "102"
TRG_DOM_READY = "103"
TRG_FORMULARZ = "104"

PIXEL_ID = "UZUPELNIJ_PIXEL_ID"

# Budowa pól jak w eksporcie z GTM (wzorzec: Integracje/MS/GTM_MSAds_v4.json).
FINGERPRINT = "1762128000000"


def tekst(wartosc):
    return {"type": "TEMPLATE", "key": "value", "value": wartosc}


def html_tagu(plik):
    with open(os.path.join(KATALOG, "tagi", plik), encoding="utf-8") as f:
        return f.read().strip() + "\n"


def tag(tag_id, nazwa, plik, wyzwalacze):
    t = {
        "accountId": ACC,
        "containerId": CON,
        "tagId": tag_id,
        "name": nazwa,
        "type": "html",
        "parameter": [
            {"type": "TEMPLATE", "key": "html", "value": html_tagu(plik)},
            {"type": "BOOLEAN", "key": "supportDocumentWrite", "value": "false"},
        ],
        "fingerprint": FINGERPRINT,
        "firingTriggerId": wyzwalacze,
        "tagFiringOption": "ONCE_PER_EVENT",
        "monitoringMetadata": {"type": "MAP"},
        "consentSettings": {"consentStatus": "NOT_SET"},
    }
    return t


def zdarzenie_niestandardowe(trigger_id, nazwa, zdarzenie):
    return {
        "accountId": ACC,
        "containerId": CON,
        "triggerId": trigger_id,
        "name": nazwa,
        "type": "CUSTOM_EVENT",
        "fingerprint": FINGERPRINT,
        "customEventFilter": [
            {
                "type": "EQUALS",
                "parameter": [
                    {"type": "TEMPLATE", "key": "arg0", "value": "{{_event}}"},
                    {"type": "TEMPLATE", "key": "arg1", "value": zdarzenie},
                ],
            }
        ],
    }


def main():
    wyzwalacze = [
        zdarzenie_niestandardowe(TRG_CMPLZ_MARKETING, "OpenAI - CE cmplz_event_marketing", "cmplz_event_marketing"),
        {
            "accountId": ACC,
            "containerId": CON,
            "triggerId": TRG_KLIK_KONTAKT,
            "name": "OpenAI - klik tel/mailto",
            "type": "LINK_CLICK",
            "fingerprint": FINGERPRINT,
            "filter": [
                {
                    "type": "MATCH_REGEX",
                    "parameter": [
                        {"type": "TEMPLATE", "key": "arg0", "value": "{{Click URL}}"},
                        {"type": "TEMPLATE", "key": "arg1", "value": "^(tel|mailto)"},
                        {"type": "BOOLEAN", "key": "ignore_case", "value": "true"},
                    ],
                }
            ],
            "waitForTags": {"type": "BOOLEAN", "value": "false"},
            "checkValidation": {"type": "BOOLEAN", "value": "false"},
            "waitForTagsTimeout": {"type": "TEMPLATE", "value": "2000"},
            "uniqueTriggerId": {"type": "TEMPLATE"},
        },
        {
            "accountId": ACC,
            "containerId": CON,
            "triggerId": TRG_DOM_READY,
            "name": "OpenAI - DOM Ready",
            "type": "DOM_READY",
            "fingerprint": FINGERPRINT,
        },
        zdarzenie_niestandardowe(TRG_FORMULARZ, "OpenAI - CE idm_formularz_wyslany", "idm_formularz_wyslany"),
    ]

    tagi = [
        tag("201", "OpenAI - 01 init", "01_init.html", [TRG_INITIALIZATION]),
        tag("202", "OpenAI - 02 zgoda i SDK", "02_zgoda_sdk.html", [TRG_CMPLZ_MARKETING]),
        tag("203", "OpenAI - 03 page_viewed", "03_page_viewed.html", [TRG_ALL_PAGES]),
        tag("204", "OpenAI - 04 kontakt", "04_kontakt.html", [TRG_KLIK_KONTAKT]),
        tag("205", "OpenAI - 05 nasluch formularza", "05_nasluch_formularza.html", [TRG_DOM_READY]),
        tag("206", "OpenAI - 06 wyslanieformularza", "06_wyslanieformularza.html", [TRG_FORMULARZ]),
    ]

    zmienne = [
        {
            "accountId": ACC,
            "containerId": CON,
            "variableId": "301",
            "name": "OpenAI - Pixel ID",
            "type": "c",
            "parameter": [tekst(PIXEL_ID)],
            "fingerprint": FINGERPRINT,
            "formatValue": {},
        }
    ]

    wbudowane = [
        {"accountId": ACC, "containerId": CON, "type": "CLICK_URL", "name": "Click URL"},
        {"accountId": ACC, "containerId": CON, "type": "EVENT", "name": "Event"},
    ]

    eksport = {
        "exportFormatVersion": 2,
        "exportTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "containerVersion": {
            "path": "accounts/0/containers/0/versions/0",
            "accountId": ACC,
            "containerId": CON,
            "containerVersionId": "0",
            "name": "OpenAI ChatGPT Ads - idomods.pl",
            "container": {
                "path": "accounts/0/containers/0",
                "accountId": ACC,
                "containerId": CON,
                "name": "idomods.pl - OpenAI ChatGPT Ads",
                "publicId": "GTM-W34PX5W",
                "usageContext": ["WEB"],
                "fingerprint": FINGERPRINT,
                "features": {
                    "supportUserPermissions": True,
                    "supportEnvironments": True,
                    "supportWorkspaces": True,
                    "supportGtagConfigs": False,
                    "supportBuiltInVariables": True,
                    "supportClients": False,
                    "supportFolders": True,
                    "supportTags": True,
                    "supportTemplates": True,
                    "supportTriggers": True,
                    "supportVariables": True,
                    "supportVersions": True,
                    "supportZones": True,
                    "supportTransformations": False,
                },
                "tagIds": ["GTM-W34PX5W"],
            },
            "tag": tagi,
            "trigger": wyzwalacze,
            "variable": zmienne,
            "builtInVariable": wbudowane,
            "fingerprint": FINGERPRINT,
        },
    }

    with open(WYJSCIE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(eksport, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Zapisano:", WYJSCIE)
    print("Tagi: %d, wyzwalacze: %d, zmienne: %d" % (len(tagi), len(wyzwalacze), len(zmienne)))


if __name__ == "__main__":
    main()
