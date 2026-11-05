"""Dane testowe: syntetyczne ICF i manifesty w formacie panelu IdoSell."""

import json
import zipfile


def icf_xml(template="order_confirmation", jezyk="pol", nazwa="Potwierdzenie wpłynięcia zamówienia",
            tytul="[iai:shop_name] – Zamówienie nr [iai:order_sn]",
            html="<p>Dziękujemy, zamówienie [iai:order_sn] przyjęte.</p>", mail_active="y",
            sms="Przyjęliśmy zamówienie [iai:order_id]. [iai:shop_name]", sms_active="n", only_ascii="y",
            z_mailem=True, z_sms=True, element_id="1791889368", opis=" 2026.10.13 13:02:48"):
    czesci = [
        '<?xml version="1.0" encoding="UTF-8"?>\n<repository file_format="ICF" version="1.0">'
        '<element id="%s">\n' % element_id,
        '<meta><title>%s</title><description>%s</description><icon encoding="base64"></icon>'
        '<language name="%s"/></meta>\n' % (nazwa, opis, jezyk),
        '<classification><type name="message_email"/></classification>\n',
        '<settings><setting type="template" value="%s"/><setting type="language" value="%s"/></settings>\n'
        % (template, jezyk),
    ]
    if z_mailem:
        czesci.append(
            '<contents message_type="mail"><content type="text_main_0"><![CDATA[%s]]></content>'
            '<content type="title"><![CDATA[%s]]></content><content type="contenttype">html</content>'
            '<content type="disposition"> </content><content type="bcc"> </content><content type="css"> </content>'
            '<content type="account"> </content><content type="default">n</content>'
            '<content type="active">%s</content><content type="additional_config"> </content></contents>\n'
            % (html, tytul, mail_active))
    if z_sms:
        czesci.append(
            '<contents message_type="sms"><content type="branding">Twoj eSklep</content>'
            '<content type="text_main_0"><![CDATA[%s]]></content><content type="name"> </content>'
            '<content type="only_ascii">%s</content><content type="type_sms">2</content>'
            '<content type="active">%s</content></contents>\n' % (sms, only_ascii, sms_active))
    czesci.append('<enclosures><enclosure id="0" name="000.png" encoding="base64">iVBORw0KGgo=</enclosure>'
                  '</enclosures>\n</element>\n</repository>')
    return "".join(czesci)


def wiadomosc(template="order_confirmation", nazwa="Potwierdzenie wpłynięcia zamówienia", grupa="make_order",
              jezyki=("pol", "eng", "ukr"), edytowalna=True, mail=None, sms="n", stan_listy=None,
              ostatnia_edycja=None):
    if not edytowalna:
        return {"grupa": grupa, "grupa_nazwa": "Złożenie zamówienia", "sekcja": "Zamówienia",
                "template": template, "nazwa": nazwa, "edytowalna": False,
                "stan_listy": stan_listy or {"sms": "nie", "mail": "tak", "webpush": "nie", "braki": None},
                "formularz": None, "ostatnia_edycja": None, "pliki": {}, "bledy": []}
    mail = mail if mail is not None else {j: "y" for j in jezyki}
    return {
        "grupa": grupa, "grupa_nazwa": "Złożenie zamówienia", "sekcja": "Zamówienia",
        "template": template, "nazwa": nazwa, "edytowalna": True,
        "stan_listy": stan_listy or {"sms": "nie" if sms == "n" else "tak", "mail": "tak", "webpush": "nie",
                                     "braki": None},
        "formularz": {"mail": dict(mail), "sms": sms, "webpush": {j: "n" for j in jezyki}},
        "ostatnia_edycja": ostatnia_edycja or {"autor": "Jan Testowy", "data": "2026-07-17 12:10:52"},
        "pliki": {j: "icf/%s__%s/%s.icf" % (grupa, template, j) for j in jezyki},
        "bledy": [],
    }


def manifest(wiadomosci=None, jezyki=("pol", "eng", "ukr")):
    return {
        "wersja": 1, "rodzaj": "eksport", "domena": "zooart6.yourtechnicaldomain.com", "shop_id": 1,
        "data_eksportu": "2026-10-13T13:05:09", "niekompletny": False, "pozostale": [],
        "jezyki": list(jezyki),
        "wiadomosci": wiadomosci if wiadomosci is not None else [wiadomosc(jezyki=jezyki)],
    }


def zbuduj_zip(sciezka, manifest_dane, pliki):
    """pliki: {sciezka_w_zip: tekst_icf}"""
    with zipfile.ZipFile(sciezka, "w") as archiwum:
        archiwum.writestr("manifest.json", json.dumps(manifest_dane, ensure_ascii=False))
        for nazwa, tresc in pliki.items():
            archiwum.writestr(nazwa, tresc.encode("utf-8"))
