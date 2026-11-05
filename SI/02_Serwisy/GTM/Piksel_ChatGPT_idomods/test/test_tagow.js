// Makieta tagów GTM (bez przeglądarki): składnia, bufor przed zgodą, kolejność wywołań, formularz.
// Uruchomienie w folderze GTM: node test/test_tagow.js
const fs = require('fs');
const path = require('path');

const dir = path.join(__dirname, '..', 'tagi');
const PIXEL = process.argv[2] || 'TESTPIXEL123';
let bledy = 0;
const ok = (warunek, opis) => {
  console.log((warunek ? 'OK    ' : 'BŁĄD  ') + opis);
  if (!warunek) bledy += 1;
};

const kod = {};
for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.html')).sort()) {
  const html = fs.readFileSync(path.join(dir, f), 'utf8').replace(/\{\{OpenAI - Pixel ID\}\}/g, PIXEL);
  kod[f] = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
  try { new Function(kod[f]); ok(true, 'składnia ' + f); } catch (e) { ok(false, 'składnia ' + f + ': ' + e.message); }
  ok(!/=>|\b(let|const)\b|`/.test(kod[f]), 'ES5 (bez =>, let, const, `) ' + f);
}

// --- minimalny DOM: dwie karty formularza (jak na stronie głównej) ---
function el(id, attrs) {
  const a = Object.assign({}, attrs);
  return {
    id, value: '', className: '', parentNode: null, children: [],
    getAttribute: k => (k in a ? a[k] : null),
    setAttribute: (k, v) => { a[k] = String(v); },
    removeAttribute: k => { delete a[k]; },
    querySelector(sel) {
      const m = sel.match(/^\[id="([^"]+)"\]$/);
      return m ? this.children.find(c => c.id === m[1]) || null : null;
    }
  };
}
function karta(imie, email, tel) {
  const card = el('card');
  const pola = { idmCfFirstName: imie, idmCfEmail: email, idmCfPhone: tel };
  for (const id in pola) { const p = el(id); p.value = pola[id]; p.parentNode = card; card.children.push(p); }
  const sv = el('idmCfSuccessView'); sv.className = 'idm-cf-hidden'; sv.parentNode = card; card.children.push(sv);
  return { card, sv };
}
const karty = [karta('Jan', 'Jan.Kowalski@Example.com', '661 699 663'), karta('', 'b@example.com', '+48 500-000-000')];
const observers = [];
global.MutationObserver = function (cb) { this.observe = node => observers.push({ node, cb }); };
let sdk = 0;
global.window = global;
global.dataLayer = [];
global.document = {
  createElement: () => ({ setAttribute() {} }),
  getElementsByTagName: () => [{ parentNode: { insertBefore() { sdk += 1; } } }],
  querySelectorAll: sel => (sel === '[id="idmCfSuccessView"]' ? karty.map(k => k.sv) : []),
  querySelector(sel) {
    if (sel === 'script[data-oaiq-sdk]') return sdk ? {} : null;
    if (sel === '[id="idmCfSuccessView"][data-oaiq-pending]') return karty.map(k => k.sv).find(v => v.getAttribute('data-oaiq-pending')) || null;
    return null;
  }
};
const run = f => eval(kod[f]);
// GTM: zdarzenie z dataLayer → tag 06
const pokazSukces = k => {
  k.sv.className = '';
  observers.filter(o => o.node === k.sv).forEach(o => o.cb());
  while (dataLayer.length) { if (dataLayer.shift().event === 'idm_formularz_wyslany') run('06_wyslanieformularza.html'); }
};

// --- scenariusz: wejście bez zgody ---
run('01_init.html');
const stub = window.oaiq;
run('03_page_viewed.html');
run('05_nasluch_formularza.html');
run('05_nasluch_formularza.html'); // ponowny DOM Ready nie dubluje obserwatorów
ok(observers.length === 2, 'nasłuch: 2 karty, bez dubli obserwatorów');
run('04_kontakt.html');
pokazSukces(karty[0]);
pokazSukces(karty[0]); // ponowna zmiana klasy nie wysyła drugi raz
ok(stub.q.length === 0 && sdk === 0, 'przed zgodą: nic w kolejce SDK, SDK niewstawione');
ok(window.oaiqBuffer.length === 4, 'przed zgodą: 4 wywołania w buforze (page_viewed, kontakt, init user, formularz) — jest ' + window.oaiqBuffer.length);

// --- zgoda marketingowa (cmplz_event_marketing) ---
run('02_zgoda_sdk.html');
run('02_zgoda_sdk.html');
ok(sdk === 1, 'SDK wstawione raz');
ok(window.oaiqBuffer.length === 0, 'bufor opróżniony');
pokazSukces(karty[1]);

const calls = stub.q.map(a => JSON.parse(JSON.stringify(Array.from(a))));
console.log(JSON.stringify(calls, null, 1));
ok(calls[0][0] === 'init' && calls[0][1].pixelId === PIXEL, 'pierwsze: init z Pixel ID');
ok(calls[1][0] === 'consent' && calls[1][1] === true, 'drugie: consent true');
ok(!calls.some(c => c[0] === 'consent' && c[1] === false), 'brak consent false');
ok(calls.filter(c => c[0] === 'init' && c[1].pixelId).length === 1, 'init z Pixel ID tylko raz');
const users = calls.filter(c => c[0] === 'init' && c[1].user).map(c => c[1].user);
ok(users[0] && users[0].email_sha256 === 'jan.kowalski@example.com' && users[0].phone_number_sha256 === '+48661699663' && users[0].first_name_sha256 === 'Jan', 'karta 1: e-mail, telefon E.164, imię');
ok(users[1] && users[1].phone_number_sha256 === '+48500000000' && !('first_name_sha256' in users[1]), 'karta 2: +48 z myślnikami, puste imię pominięte');
const form = calls.map((c, i) => [c, i]).filter(([c]) => c[3] && c[3].custom_event_name === 'wyslanieformularza');
ok(form.length === 2, 'wyslanieformularza: 2 razy (po razie na kartę)');
ok(form.every(([, i]) => calls[i - 1][0] === 'init' && calls[i - 1][1].user), 'init user tuż przed każdym wyslanieformularza');
ok(calls.filter(c => c[3] && c[3].custom_event_name === 'kontakt').length === 1, 'kontakt: 1 raz');

// --- brak Pixel ID: tag 02 nic nie robi ---
const kod02 = fs.readFileSync(path.join(dir, '02_zgoda_sdk.html'), 'utf8').replace(/\{\{OpenAI - Pixel ID\}\}/g, 'UZUPELNIJ_PIXEL_ID');
window.oaiq = null; window.oaiqSafe = null; window.oaiqConsentGranted = false; window.oaiqBuffer = []; sdk = 0;
run('01_init.html');
run('03_page_viewed.html');
eval([...kod02.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n'));
ok(sdk === 0 && window.oaiq.q.length === 0 && window.oaiqBuffer.length === 1, 'bez Pixel ID: SDK niewstawione, zdarzenia zostają w buforze');

console.log(bledy ? '\nBŁĘDÓW: ' + bledy : '\nWszystko OK');
process.exit(bledy ? 1 : 0);
