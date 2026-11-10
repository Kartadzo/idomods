// Historia sterowników IdoSell: fragment do Claude in Chrome (javascript_tool).
// Ładowany z lokalnego odbiornika (historia.py odbiornik):
//   eval(await (await fetch('http://127.0.0.1:8765/zrzut_panel.js')).text());
//   await BM.zrzutSklepu({klient: 'ezebra', sesja: '2026-11-10_1005_start'});
//
// Tylko odczyt (GET) z wyjątkiem BM.zapisz(), który klika „Zapisz” w oknie serwisu.
// Pułapki panelu (test zooart6 2026-11-10) opisane w ANALIZA_historia_sterownikow.md.

window.BM = (() => {
  const ODBIORNIK = 'http://127.0.0.1:8765';
  const czekaj = (ms) => new Promise((r) => setTimeout(r, ms));

  // Ta sama normalizacja co porownaj_sterownik.normalizuj(): bez BOM, LF,
  // bez spacji/tabulatorów na końcach linii i bez końcowych pustych linii.
  const normalizuj = (s) => {
    const linie = s.replace(/^﻿/, '').replace(/\r\n?/g, '\n').split('\n')
      .map((l) => l.replace(/[ \t]+$/, ''));
    while (linie.length && linie[linie.length - 1] === '') linie.pop();
    return linie;
  };
  const sha = async (tekst) => [...new Uint8Array(
    await crypto.subtle.digest('SHA-256', new TextEncoder().encode(tekst)))]
    .map((b) => b.toString(16).padStart(2, '0')).join('');

  const znacznik = (tekst) => {
    const s = tekst.slice(0, 4000);
    const m = s.match(/BM-SERWIS:\s*shop=(\d+)\s*\|\s*ID\s*(\d+)\s*\|\s*([^|]*?)\s*\|\s*plik\s+(\S+)/);
    const e = s.match(/BM-EDYCJA:\s*([^|]*?)\s*(?:\|\s*(.*?))?\s*-->/);
    if (!m && !e) return null;
    return {
      shop: m ? +m[1] : null, serwis_id: m ? +m[2] : null, nazwa: m ? m[3] : null,
      plik: m ? m[4] : null, edycja: e ? e[1] : null, opis: e && e[2] ? e[2] : null,
    };
  };

  const linkUstawien = (tr) => [...tr.querySelectorAll('a')]
    .find((a) => a.innerText.trim() === 'Ustawienia');
  const adresUstawien = (a) => {
    const m = (a.getAttribute('onclick') || '').match(/`([^`]*\.php[^`]*)`/);
    return m ? new URL(m[1], location.href) : null;
  };

  // Pułapka 1: lista ładowana skryptem po wczytaniu strony.
  const wiersze = async (limitMs = 25000) => {
    const start = Date.now();
    while (Date.now() - start < limitMs) {
      const tab = document.querySelector('#table_pricecomparersList');
      const w = tab ? [...tab.querySelectorAll('tr')]
        .filter((tr) => tr.querySelectorAll('tr').length === 0 && linkUstawien(tr)) : [];
      if (w.length) { await czekaj(500); return w; }
      await czekaj(500);
    }
    return [];
  };

  const wiersz = (rows, id) => rows.find((tr) => {
    const u = adresUstawien(linkUstawien(tr));
    return u && u.searchParams.get('pricecomparerId') === String(id);
  });

  async function zrzutSklepu({ klient, sesja, kopie = true, odbiornik = ODBIORNIK } = {}) {
    if (!klient || !sesja) throw new Error('podaj klient i sesja');
    if (!/config-pricecomparers\.php/.test(location.pathname)) {
      return 'BŁĄD: otwórz /panel/config-pricecomparers.php?shop=<n>';
    }
    const shop = +new URL(location.href).searchParams.get('shop') || 1;
    const rows = await wiersze();
    const bledy = [];
    if (!rows.length) bledy.push('lista serwisów pusta (nie załadowała się albo wylogowano)');
    const serwisy = [];
    const tresci = {};
    for (const tr of rows) {
      const u = adresUstawien(linkUstawien(tr));
      if (!u) { bledy.push('wiersz bez adresu ustawień'); continue; }
      const id = +u.searchParams.get('pricecomparerId');
      const komorki = tr.innerText.split(/\t|\n/).map((x) => x.trim()).filter(Boolean);
      const rek = {
        id, nazwa: komorki[0] || '', aktywny: /Aktywna/.test(tr.innerText),
        wygenerowany: (tr.innerText.match(/wygenerowany o godzinie\s+([\d-]+ [\d:]+)/) || [])[1] || null,
        sterownik: false, sha256: null, linie: 0, znacznik: null,
      };
      let odp; let tekst;
      try {
        odp = await fetch(u, { credentials: 'include' });
        tekst = await odp.text();
      } catch (e) { bledy.push(`${id}: ${e}`); continue; }
      // Pułapka 3: brak 200 lub formularza to błąd, nie „brak sterownika”.
      const dok = new DOMParser().parseFromString(tekst, 'text/html');
      const form = dok.querySelector('form');
      if (odp.status !== 200 || !form || dok.querySelector('input[type=password]')) {
        bledy.push(`${id}: odpowiedź ${odp.status}${form ? '' : ', brak formularza'}`);
        continue;
      }
      const ta = dok.querySelector('textarea[name=driver_body]');
      if (ta && ta.value.trim()) {
        const linie = normalizuj(ta.value);
        const zn = linie.join('\n');
        rek.sterownik = true;
        rek.sha256 = await sha(zn);
        rek.linie = linie.length;
        rek.znacznik = znacznik(zn);
        tresci[rek.sha256] = zn;
      }
      serwisy.push(rek);
    }

    let noweKopie = 0;
    if (kopie && Object.keys(tresci).length) {
      let mam = [];
      try {
        mam = await (await fetch(`${odbiornik}/kopie?klient=${encodeURIComponent(klient)}`)).json();
      } catch (e) { bledy.push(`odbiornik /kopie: ${e}`); }
      for (const s of serwisy.filter((x) => x.sterownik)) {
        if (mam.includes(s.sha256)) continue;
        const q = new URLSearchParams({ klient, shop, id: s.id, sha: s.sha256 });
        try {
          const r = await fetch(`${odbiornik}/kopia?${q}`, {
            method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: tresci[s.sha256],
          });
          if ((await r.text()).startsWith('OK')) { noweKopie += 1; mam.push(s.sha256); }
          else bledy.push(`kopia ${s.id}: odrzucona`);
        } catch (e) { bledy.push(`kopia ${s.id}: ${e}`); }
      }
    }

    const czesc = { shop, host: location.host, czas: new Date().toISOString(), serwisy, bledy };
    const q = new URLSearchParams({ klient, sesja, shop });
    let zapis = '';
    try {
      zapis = await (await fetch(`${odbiornik}/czesc?${q}`, {
        method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(czesc),
      })).text();
    } catch (e) { zapis = `BŁĄD odbiornika: ${e}`; }
    return `shop ${shop}: ${serwisy.length} serwisów (ze sterownikiem ${serwisy.filter((x) => x.sterownik).length}), `
      + `nowe kopie ${noweKopie}, błędy ${bledy.length}${bledy.length ? ` [${bledy.slice(0, 3).join('; ')}]` : ''}; odbiornik: ${zapis}`;
  }

  // Pułapka 4 i 5: tylko widoczne pole, którego formularz ma elements['id'] = ID serwisu.
  const poleSerwisu = (id) => [...document.querySelectorAll('textarea[name=driver_body]')]
    .find((t) => t.offsetParent && t.form && t.form.elements.id && t.form.elements.id.value === String(id));

  async function otworz(id) {
    const rows = await wiersze();
    const tr = wiersz(rows, id);
    if (!tr) return { ok: false, blad: `brak serwisu ${id} na liście tego sklepu` };
    linkUstawien(tr).click();
    for (let i = 0; i < 40; i += 1) {
      const ta = poleSerwisu(id);
      if (ta) {
        const f = ta.form;
        return {
          ok: true, id, shopId: f.elements.shopId ? f.elements.shopId.value : null,
          nazwa: f.elements.name ? f.elements.name.value : null,
          sha256: await sha(normalizuj(ta.value).join('\n')),
        };
      }
      await czekaj(500);
    }
    return { ok: false, blad: `okno serwisu ${id} się nie otworzyło` };
  }

  // Kontrola tuż przed kliknięciem „Zapisz” (po wklejeniu ctrl+v).
  async function sprawdz(id, shaOczekiwany) {
    const ta = poleSerwisu(id);
    if (!ta) return { ok: false, blad: `brak widocznego okna serwisu ${id}` };
    const h = await sha(normalizuj(ta.value).join('\n'));
    return { ok: h === shaOczekiwany, sha256: h, oczekiwany: shaOczekiwany };
  }

  // Pułapki 6 i 7: wynik oceniamy dopiero zrzutem po wgraniu; tu tylko stan okna.
  async function zapisz(id, shaOczekiwany) {
    const s = await sprawdz(id, shaOczekiwany);
    if (!s.ok) return { zapisano: false, ...s };
    const ta = poleSerwisu(id);
    const btn = [...ta.form.querySelectorAll('button')]
      .find((b) => b.innerText.trim() === 'Zapisz' && b.offsetParent);
    if (!btn) return { zapisano: false, blad: 'brak przycisku Zapisz w formularzu serwisu' };
    btn.click();
    await czekaj(8000);
    const otwarte = !!poleSerwisu(id);
    const kom = [...document.querySelectorAll('div')]
      .filter((e) => e.offsetParent && e.childElementCount < 6 && /niepoprawną strukturę/.test(e.innerText))
      .map((e) => e.innerText.replace(/\s+/g, ' ').trim()).sort((a, b) => a.length - b.length)[0] || null;
    return {
      klikniete: true, okno_otwarte: otwarte,
      ocena: otwarte ? 'ODRZUCONE (okno nadal otwarte)' : 'okno zamknięte - potwierdź zrzutem po_wgraniu',
      komunikat: otwarte ? kom : null,
      uwaga: 'przed kolejnym serwisem przeładuj stronę',
    };
  }

  return { zrzutSklepu, otworz, sprawdz, zapisz, normalizuj, sha };
})();
'BM gotowe: zrzutSklepu, otworz, sprawdz, zapisz';
