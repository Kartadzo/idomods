/* Wiadomości transakcyjne IdoSell — rdzeń przeglądarkowy.
 * Działa na stronie /panel/config-messages.php na sesji zalogowanego użytkownika (bookmarklet, skill)
 * oraz w Node (testy czystych funkcji).
 * UWAGA: panel ładuje Prototype.js — tylko zwykłe pętle for, bez Array.from / for..of na Set / filter / map;
 * JSON wyłącznie przez WT.doJson().
 */
(function (root) {
  'use strict';
  var WT = {};
  var SCIEZKA = '/panel/config-messages.php';
  var ODSTEP_MS = 200;
  WT.BLAD_SESJI = 'SESJA_WYGASLA';

  // ---------- czyste funkcje ----------

  var TABLICA_CRC = null;
  WT.crc32 = function (bajty) {
    if (!TABLICA_CRC) {
      TABLICA_CRC = [];
      for (var n = 0; n < 256; n++) {
        var c = n;
        for (var k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
        TABLICA_CRC[n] = c >>> 0;
      }
    }
    var crc = 0xFFFFFFFF;
    for (var i = 0; i < bajty.length; i++) crc = TABLICA_CRC[(crc ^ bajty[i]) & 0xFF] ^ (crc >>> 8);
    return (crc ^ 0xFFFFFFFF) >>> 0;
  };

  function utf8(tekst) { return new TextEncoder().encode(tekst); }

  // ZIP bez kompresji (metoda 0 „store"), nazwy plików w UTF-8 (bit 11), data 1980-01-01.
  WT.zbudujZip = function (pliki) {
    var czesci = [], centralne = [], przesuniecie = 0;
    for (var i = 0; i < pliki.length; i++) {
      var nazwa = utf8(pliki[i].nazwa);
      var dane = typeof pliki[i].dane === 'string' ? utf8(pliki[i].dane) : pliki[i].dane;
      var crc = WT.crc32(dane);
      var lok = new DataView(new ArrayBuffer(30));
      lok.setUint32(0, 0x04034b50, true); lok.setUint16(4, 20, true); lok.setUint16(6, 0x0800, true);
      lok.setUint16(8, 0, true); lok.setUint16(10, 0, true); lok.setUint16(12, 0x21, true);
      lok.setUint32(14, crc, true); lok.setUint32(18, dane.length, true); lok.setUint32(22, dane.length, true);
      lok.setUint16(26, nazwa.length, true); lok.setUint16(28, 0, true);
      czesci.push(new Uint8Array(lok.buffer), nazwa, dane);
      var cen = new DataView(new ArrayBuffer(46));
      cen.setUint32(0, 0x02014b50, true); cen.setUint16(4, 20, true); cen.setUint16(6, 20, true);
      cen.setUint16(8, 0x0800, true); cen.setUint16(10, 0, true); cen.setUint16(12, 0, true);
      cen.setUint16(14, 0x21, true); cen.setUint32(16, crc, true); cen.setUint32(20, dane.length, true);
      cen.setUint32(24, dane.length, true); cen.setUint16(28, nazwa.length, true);
      cen.setUint32(42, przesuniecie, true);
      centralne.push(new Uint8Array(cen.buffer), nazwa);
      przesuniecie += 30 + nazwa.length + dane.length;
    }
    var rozmiarCen = 0;
    for (var j = 0; j < centralne.length; j++) { czesci.push(centralne[j]); rozmiarCen += centralne[j].length; }
    var kon = new DataView(new ArrayBuffer(22));
    kon.setUint32(0, 0x06054b50, true); kon.setUint16(8, pliki.length, true); kon.setUint16(10, pliki.length, true);
    kon.setUint32(12, rozmiarCen, true); kon.setUint32(16, przesuniecie, true);
    czesci.push(new Uint8Array(kon.buffer));
    var dlugosc = 0;
    for (var a = 0; a < czesci.length; a++) dlugosc += czesci[a].length;
    var wynik = new Uint8Array(dlugosc), poz = 0;
    for (var b = 0; b < czesci.length; b++) { wynik.set(czesci[b], poz); poz += czesci[b].length; }
    return wynik;
  };

  var POLA_TRESCI = ['title', 'text_main_0'];
  var ENCJE = [['&lt;', '<'], ['&gt;', '>'], ['&quot;', '"'], ['&apos;', "'"], ['&amp;', '&']];

  // Tekst pola niezależnie od zapisu: sekcje CDATA albo encje XML; sama spacja = puste (jak wt.icf._wartosc_pola).
  function wartoscPola(surowa) {
    var czesci = surowa.split(/(<!\[CDATA\[[\s\S]*?\]\]>)/), wynik = '';
    for (var i = 0; i < czesci.length; i++) {
      var c = czesci[i];
      if (c.indexOf('<![CDATA[') === 0) { wynik += c.slice(9, -3); continue; }
      for (var e = 0; e < ENCJE.length; e++) c = c.split(ENCJE[e][0]).join(ENCJE[e][1]);
      wynik += c;
    }
    return wynik.trim() ? wynik : '';
  }

  // Kanoniczny tekst TREŚCI: tytuł i HTML maila, tekst SMS, załączniki — bez id, daty eksportu, flag active
  // i ustawień technicznych (zgodnie z wt.icf.odcisk).
  WT.trescIcf = function (xml) {
    var linie = [], bloki = /<contents message_type="(\w+)">([\s\S]*?)<\/contents>/g, b;
    while ((b = bloki.exec(xml)) !== null) {
      var pola = /<content type="(\w+)">([\s\S]*?)<\/content>/g, p;
      while ((p = pola.exec(b[2])) !== null) {
        if (POLA_TRESCI.indexOf(p[1]) >= 0) linie.push(b[1] + '.' + p[1] + '\u0000' + wartoscPola(p[2]));
      }
    }
    var z = xml.match(/<enclosures>([\s\S]*?)<\/enclosures>/);
    linie.push('enclosures\u0000' + (z ? z[1].trim() : ''));
    return linie.join('\u0001');
  };

  WT.odcisk = function (xml) {
    return crypto.subtle.digest('SHA-256', utf8(WT.trescIcf(xml))).then(function (bufor) {
      var b = new Uint8Array(bufor), s = '';
      for (var i = 0; i < b.length; i++) s += (b[i] < 16 ? '0' : '') + b[i].toString(16);
      return s;
    });
  };

  WT.parsujStan = function (tekst) {
    var t = (tekst || '').replace(/\s+/g, ' ').trim();
    var braki = t.match(/do uzupełnienia szablony:\s*\((\d+ z \d+)\)/);
    var stan = /^nie dotyczy/.test(t) ? 'nie dotyczy' : /^tak/.test(t) ? 'tak' : /^nie/.test(t) ? 'nie' : null;
    return { stan: stan, braki: braki ? braki[1] : null };
  };

  WT.parametr = function (href, nazwa) {
    var m = (href || '').match(new RegExp('[?&]' + nazwa + '=([^&#]*)'));
    return m ? decodeURIComponent(m[1]) : null;
  };

  // Prototype.js dodaje Array#toJSON / String#toJSON, co psuje JSON.stringify — zdejmujemy je na czas serializacji.
  WT.doJson = function (obiekt) {
    var a = Array.prototype.toJSON, s = String.prototype.toJSON;
    delete Array.prototype.toJSON; delete String.prototype.toJSON;
    try { return JSON.stringify(obiekt, null, 2); }
    finally { if (a) Array.prototype.toJSON = a; if (s) String.prototype.toJSON = s; }
  };

  function dwa(n) { return (n < 10 ? '0' : '') + n; }
  WT.terazIso = function () {
    var d = new Date();
    return d.getFullYear() + '-' + dwa(d.getMonth() + 1) + '-' + dwa(d.getDate()) + 'T' +
      dwa(d.getHours()) + ':' + dwa(d.getMinutes()) + ':' + dwa(d.getSeconds());
  };

  // ---------- odczyt panelu ----------

  function czekaj(ms) { return new Promise(function (ok) { setTimeout(ok, ms); }); }
  function html(tekst) { return new DOMParser().parseFromString(tekst, 'text/html'); }
  function tekstEl(e) { return ((e && e.textContent) || '').replace(/\s+/g, ' ').trim(); }
  WT.tekstEl = tekstEl;

  function bladSesji() {
    var e = new Error('Sesja panelu wygasła — zaloguj się i uruchom ponownie.');
    e.kod = WT.BLAD_SESJI;
    return e;
  }

  WT.pobierzTekst = async function (url) {
    for (var proba = 1; ; proba++) {
      var r = await fetch(url, { credentials: 'include' });
      var t = await r.text();
      if ((r.status === 429 || r.status >= 500) && proba < 3) { await czekaj(2000 * proba); continue; }
      if (r.status >= 400) throw new Error('HTTP ' + r.status + ' dla ' + url.split('?')[0]);
      if (/<title>\s*Logowanie u/.test(t)) throw bladSesji();
      await czekaj(ODSTEP_MS);
      return t;
    }
  };

  WT.shopZAdresu = function () {
    return parseInt(WT.parametr(location.search, 'shop') || '1', 10);
  };

  WT.pobierzGrupy = async function (shop) {
    var d = html(await WT.pobierzTekst(SCIEZKA + '?populate=types&shop=' + shop));
    var linki = d.querySelectorAll('a[href*="populate=list"]'), wynik = [], byly = {};
    for (var i = 0; i < linki.length; i++) {
      var g = WT.parametr(linki[i].getAttribute('href'), 'group');
      if (!g || byly[g]) continue;
      byly[g] = true;
      var wiersz = linki[i].closest('tr');
      wynik.push({ grupa: g, nazwa: tekstEl(wiersz ? wiersz.querySelector('td') : linki[i]) });
    }
    return wynik;
  };

  function naglowekSekcji(tabela) {
    for (var e = tabela; e && e.tagName !== 'BODY'; e = e.parentElement) {
      for (var s = e.previousElementSibling; s; s = s.previousElementSibling) {
        if (/^H[1-6]$/.test(s.tagName)) return tekstEl(s);
        if (s.tagName === 'TABLE') break;
      }
    }
    return '';
  }

  function wierszeTabeli(tabela) {
    return tabela.querySelectorAll(':scope > tr, :scope > tbody > tr, :scope > thead > tr');
  }

  WT.pobierzListe = async function (grupa, shop) {
    var d = html(await WT.pobierzTekst(SCIEZKA + '?populate=list&group=' + encodeURIComponent(grupa) + '&shop=' + shop));
    var tabele = d.querySelectorAll('table'), wynik = [], byly = {};
    var kanaly = ['sms', 'mail', 'webpush'];
    for (var i = 0; i < tabele.length; i++) {
      var wiersze = wierszeTabeli(tabele[i]);
      if (!wiersze.length) continue;
      var naglowki = wiersze[0].querySelectorAll('th, td'), kol = {};
      for (var k = 0; k < naglowki.length; k++) {
        var h = tekstEl(naglowki[k]);
        if (/SMS/.test(h)) kol.sms = k; else if (/Web Push/i.test(h)) kol.webpush = k; else if (/e-mail/i.test(h)) kol.mail = k;
      }
      if (kol.mail === undefined && kol.sms === undefined) continue;
      var sekcja = naglowekSekcji(tabele[i]);
      for (var r = 1; r < wiersze.length; r++) {
        var a = wiersze[r].querySelector('a[href*="template="]');
        if (!a) continue;
        var template = WT.parametr(a.getAttribute('href'), 'template');
        if (!template || byly[template]) continue;
        byly[template] = true;
        var komorki = wiersze[r].querySelectorAll('td'), stan = { braki: null };
        for (var c = 0; c < kanaly.length; c++) {
          var idx = kol[kanaly[c]];
          if (idx === undefined || !komorki[idx]) { stan[kanaly[c]] = null; continue; }
          var s = WT.parsujStan(tekstEl(komorki[idx]));
          stan[kanaly[c]] = s.stan;
          if (s.braki) stan.braki = s.braki;
        }
        wynik.push({ grupa: grupa, sekcja: sekcja, template: template, nazwa: tekstEl(komorki[0]),
          edytowalna: /Edytuj/.test(tekstEl(a)), stan_listy: stan });
      }
    }
    return wynik;
  };

  WT.pobierzEdycje = async function (template, shop) {
    var d = html(await WT.pobierzTekst(SCIEZKA + '?populate=edit&template=' + encodeURIComponent(template) + '&shop=' + shop));
    var jezyki = [], formularz = { mail: {}, sms: null, webpush: {} };
    var pola = d.querySelectorAll('input[name]');
    for (var i = 0; i < pola.length; i++) {
      var n = pola[i].getAttribute('name');
      var m = n.match(/^(mail|sms|webpush)_lang\[([a-z]{3})\]/);
      if (m && jezyki.indexOf(m[2]) < 0) jezyki.push(m[2]);
      if (pola[i].type !== 'radio' || !pola[i].hasAttribute('checked')) continue;
      var v = pola[i].getAttribute('value');
      var mm = n.match(/^mail_lang\[([a-z]{3})\]\[active_mail\]$/);
      if (mm) formularz.mail[mm[1]] = v;
      if (n === 'sms_lang[active]') formularz.sms = v;
      var mw = n.match(/^webpush_lang\[([a-z]{3})\]\[active\]$/);
      if (mw) formularz.webpush[mw[1]] = v;
    }
    var ostatnia = null, komorki = d.querySelectorAll('td, th');
    for (var k = 0; k < komorki.length; k++) {
      if (tekstEl(komorki[k]) !== 'Data modyfikacji') continue;
      var wiersz = komorki[k].closest('tr'), nast = wiersz ? wiersz.nextElementSibling : null;
      var td = nast ? nast.querySelectorAll('td') : [];
      if (td.length >= 2 && /^\d{4}-\d{2}-\d{2}/.test(tekstEl(td[1]))) ostatnia = { autor: tekstEl(td[0]), data: tekstEl(td[1]) };
      break;
    }
    return { jezyki: jezyki, formularz: formularz, ostatnia_edycja: ostatnia };
  };

  WT.adresIcf = function (template, shop, jezyk) {
    return SCIEZKA + '?populate=edit&template=' + encodeURIComponent(template) + '&shop=' + shop +
      '&story_id=&action=exportIDF&language=' + jezyk;
  };

  WT.pobierzIcf = async function (template, shop, jezyk) {
    var t = await WT.pobierzTekst(WT.adresIcf(template, shop, jezyk));
    if (t.indexOf('file_format="ICF"') < 0) throw new Error('Odpowiedź nie jest plikiem ICF');
    return t;
  };

  WT.pobierzPlik = function (nazwa, bajty) {
    var url = URL.createObjectURL(new Blob([bajty], { type: 'application/zip' }));
    var a = document.createElement('a');
    a.href = url; a.download = nazwa;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 10000);
  };

  WT.eksportuj = async function (opcje) {
    var shop = opcje.shop, filtr = opcje.templates || null, postep = opcje.onPostep || function () {};
    var rodzaj = opcje.rodzaj || 'eksport';
    var manifest = { wersja: 1, rodzaj: rodzaj, domena: location.hostname, shop_id: shop, data_eksportu: WT.terazIso(),
      niekompletny: false, pozostale: [], jezyki: [], wiadomosci: [] };
    // np. flagi_przed_importem z WT.zastosujPlan — weryfikacja porównuje flagi z nimi, nie z eksportu.
    if (opcje.dodatki) for (var klucz in opcje.dodatki) if (Object.prototype.hasOwnProperty.call(opcje.dodatki, klucz)) manifest[klucz] = opcje.dodatki[klucz];
    var pliki = [], lista = [];
    var grupy = await WT.pobierzGrupy(shop);
    for (var g = 0; g < grupy.length; g++) {
      postep('Lista: ' + grupy[g].nazwa);
      var wiersze = await WT.pobierzListe(grupy[g].grupa, shop);
      for (var i = 0; i < wiersze.length; i++) {
        wiersze[i].grupa_nazwa = grupy[g].nazwa;
        if (!filtr || filtr.indexOf(wiersze[i].template) >= 0) lista.push(wiersze[i]);
      }
    }
    for (var n = 0; n < lista.length; n++) {
      var w = lista[n];
      w.formularz = null; w.ostatnia_edycja = null; w.pliki = {}; w.bledy = [];
      try {
        if (w.edytowalna) {
          postep((n + 1) + '/' + lista.length + ': ' + w.nazwa);
          var e = await WT.pobierzEdycje(w.template, shop);
          w.formularz = e.formularz; w.ostatnia_edycja = e.ostatnia_edycja;
          for (var j = 0; j < e.jezyki.length; j++) {
            var jez = e.jezyki[j];
            if (manifest.jezyki.indexOf(jez) < 0) manifest.jezyki.push(jez);
            try {
              var xml = await WT.pobierzIcf(w.template, shop, jez);
              var sciezka = 'icf/' + w.grupa + '__' + w.template + '/' + jez + '.icf';
              pliki.push({ nazwa: sciezka, dane: xml });
              w.pliki[jez] = sciezka;
            } catch (bladJ) {
              if (bladJ.kod === WT.BLAD_SESJI) throw bladJ;
              w.bledy.push(jez + ': ' + bladJ.message);
            }
          }
        }
      } catch (blad) {
        if (blad.kod !== WT.BLAD_SESJI) { w.bledy.push(blad.message); manifest.wiadomosci.push(w); continue; }
        manifest.niekompletny = true;
        for (var r = n; r < lista.length; r++) manifest.pozostale.push(lista[r].template);
        postep('Sesja wygasła — zapisuję eksport częściowy (' + n + '/' + lista.length + ').');
        break;
      }
      manifest.wiadomosci.push(w);
    }
    pliki.unshift({ nazwa: 'manifest.json', dane: WT.doJson(manifest) });
    var nazwa = rodzaj + '_' + location.hostname.split('.')[0] + '_shop' + shop + '_' +
      manifest.data_eksportu.replace(/[-:]/g, '').replace('T', '-') + '.zip';
    WT.pobierzPlik(nazwa, WT.zbudujZip(pliki));
    postep('Gotowe: ' + nazwa + (manifest.niekompletny ? ' (NIEKOMPLETNY)' : ''));
    return { nazwa: nazwa, manifest: manifest };
  };

  // ---------- zapis w panelu (tylko bookmarklet: ukryta ramka iframe z formularzami panelu) ----------

  WT.ramka = function () {
    var f = document.getElementById('wt-ramka');
    if (!f) {
      f = document.createElement('iframe');
      f.id = 'wt-ramka';
      f.style.cssText = 'position:fixed;left:-5000px;top:0;width:1300px;height:900px;border:0;';
      document.body.appendChild(f);
    }
    return f;
  };
  function dok() { var f = WT.ramka(); return f.contentDocument; }

  async function czekajNa(warunek, ms, opis) {
    var koniec = Date.now() + (ms || 20000);
    while (Date.now() < koniec) {
      var w = null;
      try { w = warunek(); } catch (e) { w = null; }
      if (w) return w;
      await czekaj(200);
    }
    throw new Error('Panel nie odpowiedział: ' + (opis || 'element'));
  }

  function widocznyZTekstem(d, selektor, wzor) {
    if (!d) return null;
    var e = d.querySelectorAll(selektor);
    for (var i = 0; i < e.length; i++) {
      var t = tekstEl(e[i]) || e[i].value || '';
      if (wzor.test(t) && e[i].offsetParent !== null) return e[i];
    }
    return null;
  }

  function sprawdzSesje(d) {
    if (d && /^\s*Logowanie u/.test(d.title || '')) throw bladSesji();
  }

  async function zaladuj(url) {
    var f = WT.ramka(), stary = f.contentDocument;
    f.src = url;
    var d = await czekajNa(function () {
      var n = dok();
      return n && n !== stary && n.readyState === 'complete' && n.location.href !== 'about:blank' ? n : null;
    }, 60000, 'wczytanie strony');
    sprawdzSesje(d);
    return d;
  }

  function adresEdycji(template, shop) {
    return SCIEZKA + '?populate=edit&template=' + encodeURIComponent(template) + '&shop=' + shop;
  }

  WT.importujIcf = async function (p) {
    var d = await zaladuj(adresEdycji(p.template, p.shop));
    var link = widocznyZTekstem(d, 'a', /^Import ICF$/);
    if (!link) throw new Error('Brak linku „Import ICF" (wiadomość wycofywana?)');
    // Panel bywa jeszcze w trakcie wczytywania i ignoruje pierwsze kliknięcie (ANALIZA §11) — ponawiamy do 3 razy.
    var pole = null;
    for (var proba = 0; proba < 3 && !pole; proba++) {
      link.click();
      try { pole = await czekajNa(function () { return dok().querySelector('input[type=file][name=idf_file]'); }, 5000, 'okno importu'); }
      catch (e) { if (proba === 2) throw e; }
    }
    var dt = new DataTransfer();
    dt.items.add(new File([p.xml], p.nazwaPliku, { type: 'text/xml' }));
    pole.files = dt.files;
    (await czekajNa(function () { return widocznyZTekstem(dok(), 'button, input[type=submit], input[type=button]', /^Wgraj plik$/); },
      15000, 'przycisk „Wgraj plik"')).click();
    var radio = await czekajNa(function () {
      return dok().querySelector('input[type=radio][name=lang][value="' + p.jezyk + '"]');
    }, 30000, 'wybór języka ' + p.jezyk);
    radio.click();
    (await czekajNa(function () { return widocznyZTekstem(dok(), 'button, input[type=submit], input[type=button]', /^Wybierz$/); },
      15000, 'przycisk „Wybierz"')).click();
    (await czekajNa(function () { return widocznyZTekstem(dok(), 'button, input[type=submit], input[type=button]', /^Tak$/); },
      30000, 'potwierdzenie „Tak"')).click();
    var komunikat = await czekajNa(function () {
      var t = tekstEl(dok().body);
      var m = t.match(/Import przebiegł pomyślnie[^.]*\./);
      return m ? m[0] : null;
    }, 30000, 'komunikat po imporcie');
    return komunikat;
  };

  WT.zapiszFlagi = async function (p) {
    var d = await zaladuj(adresEdycji(p.template, p.shop));
    function ustaw(nazwa, wartosc) {
      var r = d.querySelector('input[type=radio][name="' + nazwa + '"][value="' + wartosc + '"]');
      if (!r) throw new Error('Brak pola ' + nazwa + ' w formularzu ' + p.template);
      r.click();
    }
    for (var j in p.mail) if (Object.prototype.hasOwnProperty.call(p.mail, j)) ustaw('mail_lang[' + j + '][active_mail]', p.mail[j]);
    if (p.sms) ustaw('sms_lang[active]', p.sms);
    var zapisz = widocznyZTekstem(d, 'input[type=submit], button', /^Zapisz zmiany$/);
    if (!zapisz) throw new Error('Brak przycisku „Zapisz zmiany"');
    zapisz.click();
    await czekajNa(function () {
      var n = dok();
      return n !== d && n.readyState === 'complete' && /Zmiany zostały zapisane/.test(tekstEl(n.body)) ? n : null;
    }, 60000, 'potwierdzenie zapisu');
  };

  async function aktualny(template, shop, kopie) {
    for (var jezyk in kopie) {
      if (!Object.prototype.hasOwnProperty.call(kopie, jezyk)) continue;
      if (await WT.odcisk(await WT.pobierzIcf(template, shop, jezyk)) !== kopie[jezyk].odcisk) return jezyk;
    }
    return null;
  }

  WT.zastosujPlan = async function (plan, mapa, opcje) {
    var shop = opcje.shop, loguj = opcje.loguj || function () {};
    var innyCel = plan.domena !== location.hostname || String(plan.shop_id) !== String(shop);
    var wynik = { wykonane: 0, pominiete: 0, reczne: [], templates: [], bledy: [] };
    var flagiPrzed = {};   // flagi odczytane z panelu tuż przed pierwszym importem danej wiadomości

    function dodajDoWeryfikacji(template) { if (wynik.templates.indexOf(template) < 0) wynik.templates.push(template); }
    async function plik(nazwa) {
      if (!mapa[nazwa]) throw new Error('W wybranym folderze brakuje pliku ' + nazwa);
      return await mapa[nazwa].text();
    }

    // Import ICF zawsze wyłącza mail w importowanym języku (ANALIZA §11). Flagi przywracamy do stanu panelu
    // sprzed importu (nie z eksportu — przy migracji pochodzi z innego sklepu), także gdy import się przerwie.
    async function importujBezpiecznie(template, jezyk, nazwaPliku, xml) {
      var przed = (await WT.pobierzEdycje(template, shop)).formularz;
      if (!flagiPrzed[template]) flagiPrzed[template] = { mail: Object.assign({}, przed.mail), sms: przed.sms };
      var komunikat = null, bladImportu = null;
      try {
        komunikat = await WT.importujIcf({ shop: shop, template: template, jezyk: jezyk, nazwaPliku: nazwaPliku, xml: xml });
      } catch (e) {
        bladImportu = e;
      } finally {
        try {
          var po = (await WT.pobierzEdycje(template, shop)).formularz, mail = {}, zmiana = false, sms = null;
          if (przed.mail[jezyk] && po.mail[jezyk] !== przed.mail[jezyk]) { mail[jezyk] = przed.mail[jezyk]; zmiana = true; }
          if (przed.sms && po.sms !== przed.sms) sms = przed.sms;
          if (zmiana || sms) {
            await WT.zapiszFlagi({ shop: shop, template: template, mail: mail, sms: sms });
            loguj('Przywrócono flagi sprzed importu (import ICF wyłącza wysyłkę): ' + template + ' ' + jezyk);
          }
        } catch (bladFlag) {
          loguj('UWAGA: mail ' + jezyk + ' w ' + template + ' może być WYŁĄCZONY — sprawdź w panelu (' + bladFlag.message + ')');
          if (!bladImportu) bladImportu = bladFlag;
        }
      }
      if (bladImportu) throw bladImportu;
      // Zapis formularzem potrafi przepisać HTML (ANALIZA §9) — sprawdzamy, czy wgrana treść przetrwała.
      if (await WT.odcisk(await WT.pobierzIcf(template, shop, jezyk)) !== await WT.odcisk(xml)) {
        loguj('UWAGA: treść ' + jezyk + ' w ' + template + ' po zapisie flag różni się od wgranej — sprawdź w weryfikacji');
      }
      return komunikat;
    }

    // Błąd jednej pozycji nie przerywa planu (ANALIZA §6) — poza wygasłą sesją.
    async function pozycja(template, nazwa, opis, krok) {
      try {
        await krok();
      } catch (e) {
        if (e.kod === WT.BLAD_SESJI) throw e;
        wynik.bledy.push(nazwa + ' (' + template + ')' + (opis ? ' ' + opis : '') + ': ' + e.message);
        loguj('BŁĄD ' + nazwa + (opis ? ' ' + opis : '') + ': ' + e.message + ' — kontynuuję plan');
        dodajDoWeryfikacji(template);
      }
    }

    try {
      if (plan.rodzaj === 'konfiguracja') {
        if (innyCel) throw new Error('Plan konfiguracji pochodzi z ' + plan.domena + ' sklep ' + plan.shop_id + ' — wykonuj go tylko tam.');
        for (var i = 0; i < plan.zmiany.length; i++) {
          var z = plan.zmiany[i];
          await pozycja(z.template, z.nazwa, '', async function () {
            var zmieniony = await aktualny(z.template, shop, z.kopie);
            if (zmieniony) { wynik.pominiete++; loguj('POMINIĘTO ' + z.nazwa + ': treść ' + zmieniony + ' zmieniona w panelu po eksporcie'); return; }
            var jestFlag = false;
            for (var k in z.mail) if (Object.prototype.hasOwnProperty.call(z.mail, k)) jestFlag = true;
            if (jestFlag || z.sms) {
              dodajDoWeryfikacji(z.template);
              await WT.zapiszFlagi({ shop: shop, template: z.template, mail: z.mail, sms: z.sms });
              loguj('Zapisano flagi: ' + z.nazwa);
            }
            for (var jezyk in z.kopie) {
              if (!Object.prototype.hasOwnProperty.call(z.kopie, jezyk)) continue;
              if (await WT.odcisk(await WT.pobierzIcf(z.template, shop, jezyk)) === z.kopie[jezyk].odcisk) continue;
              await importujBezpiecznie(z.template, jezyk, z.kopie[jezyk].plik, await plik(z.kopie[jezyk].plik));
              loguj('Przywrócono treść ' + jezyk + ' (zapis formularzem ją zmienił): ' + z.nazwa);
            }
            if (z.reset) wynik.reczne.push(z.nazwa + ' (' + z.template + '): „Wczytaj treść z szablonu domyślnego"');
            wynik.wykonane++; dodajDoWeryfikacji(z.template);
          });
        }
      } else if (plan.rodzaj === 'import') {
        if (innyCel) {
          // Import nadpisuje treść nieodwracalnie i nie zostawia historii — najpierw kopia sklepu docelowego.
          var docelowe = [];
          for (var d = 0; d < plan.pozycje.length; d++) if (docelowe.indexOf(plan.pozycje[d].template) < 0) docelowe.push(plan.pozycje[d].template);
          var kopia = await WT.eksportuj({ shop: shop, templates: docelowe, rodzaj: 'eksport', onPostep: function () {} });
          loguj('Kopia sklepu docelowego przed migracją: ' + kopia.nazwa);
        }
        for (var p = 0; p < plan.pozycje.length; p++) {
          var poz = plan.pozycje[p];
          await pozycja(poz.template, poz.nazwa, poz.jezyk, async function () {
            if (!innyCel) {
              var obecny = await WT.odcisk(await WT.pobierzIcf(poz.template, shop, poz.jezyk));
              if (obecny !== poz.odcisk_oryginalu) { wynik.pominiete++; loguj('POMINIĘTO ' + poz.nazwa + ' ' + poz.jezyk + ': zmieniona w panelu po eksporcie'); return; }
            }
            dodajDoWeryfikacji(poz.template);
            var komunikat = await importujBezpiecznie(poz.template, poz.jezyk, poz.plik, await plik(poz.plik));
            loguj('Zaimportowano ' + poz.nazwa + ' ' + poz.jezyk + ': ' + komunikat);
            wynik.wykonane++;
          });
        }
      } else {
        throw new Error('Nieznany rodzaj planu: ' + plan.rodzaj);
      }
    } finally {
      if (wynik.templates.length) {
        loguj('Eksport weryfikacyjny…');
        await WT.eksportuj({ shop: shop, templates: wynik.templates, rodzaj: 'weryfikacja', onPostep: loguj,
          dodatki: { flagi_przed_importem: flagiPrzed } });
      }
    }
    return wynik;
  };

  root.WT = WT;
})(typeof window !== 'undefined' ? window : globalThis);

/* Menu bookmarkletu: Eksport / Eksport wybranych / Zastosuj plan. Wymaga WT z panel_core.js. */
(function (root) {
  'use strict';
  var WTUI = {};

  function el(tag, styl, tekst) {
    var e = document.createElement(tag);
    if (styl) e.style.cssText = styl;
    if (tekst) e.textContent = tekst;
    return e;
  }

  WTUI.pokaz = function () {
    if (!/\/panel\/config-messages\.php/.test(location.pathname)) {
      alert('Otwórz w panelu: Administracja → Konfiguracja wiadomości transakcyjnych, wybierz sklep i uruchom zakładkę ponownie.');
      return;
    }
    var stare = document.getElementById('wt-menu');
    if (stare) stare.remove();
    var okno = el('div', 'position:fixed;top:20px;right:20px;width:460px;max-height:85vh;overflow:auto;z-index:2147483647;' +
      'background:#fff;border:2px solid #1a7f4b;border-radius:8px;padding:14px;font:13px/1.4 Arial,sans-serif;color:#222;' +
      'box-shadow:0 6px 24px rgba(0,0,0,.25)');
    okno.id = 'wt-menu';
    okno.appendChild(el('div', 'font-weight:bold;font-size:15px;margin-bottom:8px', 'Wiadomości transakcyjne'));
    var shopWiersz = el('div', 'margin-bottom:8px', 'Sklep (shop): ');
    var shop = el('input', 'width:50px');
    shop.value = String(WT.shopZAdresu());
    shopWiersz.appendChild(shop);
    okno.appendChild(shopWiersz);
    var log = el('pre', 'white-space:pre-wrap;background:#f4f4f4;padding:8px;max-height:300px;overflow:auto;margin:8px 0 0');
    function loguj(t) { log.textContent += t + '\n'; log.scrollTop = log.scrollHeight; }
    function przycisk(tekst, akcja) {
      var b = el('button', 'margin:0 6px 6px 0;padding:6px 10px;cursor:pointer', tekst);
      b.onclick = async function () {
        var wszystkie = okno.querySelectorAll('button');
        for (var i = 0; i < wszystkie.length; i++) wszystkie[i].disabled = true;
        try { await akcja(); } catch (e) { loguj('BŁĄD: ' + e.message); }
        finally { for (var j = 0; j < wszystkie.length; j++) wszystkie[j].disabled = false; }
      };
      okno.appendChild(b);
      return b;
    }
    var nr = function () { return parseInt(shop.value, 10) || 1; };
    przycisk('Eksport wszystkich', function () { return WT.eksportuj({ shop: nr(), onPostep: loguj }); });
    przycisk('Eksport wybranych…', function () {
      var t = prompt('Kody wiadomości (template), oddzielone przecinkami:', '');
      if (!t) return Promise.resolve();
      var lista = t.split(','), templates = [];
      for (var i = 0; i < lista.length; i++) if (lista[i].trim()) templates.push(lista[i].trim());
      return WT.eksportuj({ shop: nr(), templates: templates, onPostep: loguj });
    });
    var wybor = el('input');
    wybor.type = 'file'; wybor.webkitdirectory = true; wybor.multiple = true; wybor.style.display = 'none';
    okno.appendChild(wybor);
    przycisk('Zastosuj plan…', function () {
      return new Promise(function (ok) {
        wybor.value = '';
        wybor.onchange = async function () {
          try { await zastosuj(wybor.files); } catch (e) { loguj('BŁĄD: ' + e.message); }
          ok();
        };
        wybor.click();
      });
    });
    przycisk('Zamknij', function () { okno.remove(); return Promise.resolve(); });
    okno.appendChild(log);
    document.body.appendChild(okno);

    async function zastosuj(pliki) {
      var mapa = {};
      for (var i = 0; i < pliki.length; i++) mapa[pliki[i].name] = pliki[i];
      var nazwa = mapa['plan_importu.json'] ? 'plan_importu.json' : (mapa['plan_konfiguracji.json'] ? 'plan_konfiguracji.json' : null);
      if (!nazwa) throw new Error('W folderze nie ma plan_importu.json ani plan_konfiguracji.json');
      var plan = JSON.parse(await mapa[nazwa].text());
      var opis = [];
      if (plan.rodzaj === 'import') for (var p = 0; p < plan.pozycje.length; p++) opis.push('• ' + plan.pozycje[p].nazwa + ' — ' + plan.pozycje[p].jezyk);
      else for (var z = 0; z < plan.zmiany.length; z++) opis.push('• ' + plan.zmiany[z].nazwa);
      var innyCel = plan.domena !== location.hostname || String(plan.shop_id) !== String(nr());
      var pytanie = (plan.rodzaj === 'import' ? 'Import treści' : 'Zmiany konfiguracji') + ' (' + opis.length + '):\n' +
        opis.slice(0, 30).join('\n') + (opis.length > 30 ? '\n…' : '') + '\n\nWykonać?';
      if (innyCel) {
        var wpis = prompt('UWAGA: plan pochodzi z ' + plan.domena + ' (sklep ' + plan.shop_id + '), a jesteś w ' +
          location.hostname + ' (sklep ' + nr() + ').\nŻeby wgrać tutaj, wpisz domenę docelową: ' + location.hostname);
        if (wpis !== location.hostname) { loguj('Anulowano (inny sklep).'); return; }
      }
      if (!confirm(pytanie)) { loguj('Anulowano.'); return; }
      var wynik = await WT.zastosujPlan(plan, mapa, { shop: nr(), loguj: loguj });
      loguj('Wykonane: ' + wynik.wykonane + ', pominięte: ' + wynik.pominiete);
      for (var r = 0; r < wynik.reczne.length; r++) loguj('RĘCZNIE: ' + wynik.reczne[r]);
      loguj('Zweryfikuj: run_wiadomosci.bat → „Weryfikacja po wykonaniu planu".');
    }
  };

  root.WTUI = WTUI;
})(window);

WTUI.pokaz();
