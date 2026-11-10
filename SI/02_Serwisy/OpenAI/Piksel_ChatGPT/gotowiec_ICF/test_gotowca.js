// Test gotowca ICF: node test_gotowca.js [plik.xml]
// Wyciąga dodatki z ICF, podstawia przykładowe zmienne kampanii i uruchamia ../test/test_dodatkow.js.
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const icf = process.argv[2] || path.join(__dirname, 'piksel_chatgpt_ads.xml');
const xml = fs.readFileSync(icf, 'utf8');
const pliki = ['01_chatgpt_init', '02_consent', '03_page_viewed', '04_contents_viewed',
  '05_items_added', '06_checkout_started', '07_order_created'];
const kody = [...xml.matchAll(/<content type="text_main_0"><!\[CDATA\[([\s\S]*?)\]\]><\/content>/g)].map(m => m[1]);
const ustawienia = [...xml.matchAll(/<setting type="config" name="([^"]+)"/g)].map(m => m[1]);
let bledy = 0;
const sprawdz = (warunek, opis) => { console.log((warunek ? 'OK    ' : 'BŁĄD  ') + opis); if (!warunek) bledy += 1; };

sprawdz(kody.length === pliki.length, `liczba dodatków ${kody.length}`);
const uzyte = new Set(kody.join('\n').match(/\[config:([a-z_]+)\]/g).map(s => s.slice(8, -1)));
sprawdz([...uzyte].every(n => ustawienia.includes(n)), `każde [config:…] ma <setting>: ${[...uzyte].join(', ')}`);
sprawdz(ustawienia.every(n => uzyte.has(n)), 'każdy <setting> jest użyty');
sprawdz(!/HxtQ|currency: 'PLN'|consent', false/.test(kody.join('\n')), 'brak Pixel ID butyolivier, PLN na sztywno i consent false');

function uruchom(opis, config) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'oaiq-'));
  kody.forEach((kod, i) => {
    let kodTest = kod.replace(/\[config:([a-z_]+)\]/g, (m, k) => (k in config ? config[k] : m))
      .replace(/\[iai:products_worth_cpa2\]/g, config._towary || '9.90');
    // cena / ilość towaru na stronie po zamówieniu (abczoo.gr: cena = wartość zamówienia)
    if (i === 6 && config._towar) kodTest = kodTest.replace(/\[iai:product_price_gross_float\]/g, config._towar);
    if (i === 6 && config._ilosc) kodTest = kodTest.replace(/\[iai:product_count\]/g, config._ilosc);
    fs.writeFileSync(path.join(dir, pliki[i] + '.html'), kodTest);
  });
  const out = execFileSync('node', [path.join(__dirname, '..', 'test', 'test_dodatkow.js'), dir], { encoding: 'utf8' });
  fs.rmSync(dir, { recursive: true, force: true });
  console.log(`\n--- ${opis}`);
  const calls = JSON.parse(out.slice(out.indexOf('[')));
  const linie = out.slice(0, out.indexOf('[')).trim();
  console.log(linie);
  return { calls, linie };
}

const sumaTowarow = z => z[2].contents.reduce((s, p) => s + p.amount * p.quantity, 0);

// 1. konfiguracja typowa; towary 2 × 4,90 = 9,80, wartość towarów z IdoSell 9,90 (dostawa 4,90 pominięta)
let r = uruchom('pixel_id ustawiony, PLN', { pixel_id: 'TestPixel12345', currency: 'PLN' });
const init = r.calls.find(c => c[0] === 'init' && c[1].pixelId);
sprawdz(init && init[1].pixelId === 'TestPixel12345', 'init z pixelId ze zmiennej');
sprawdz(!/BŁĄD/.test(r.linie), 'składnia wszystkich dodatków');
let zakup = r.calls.find(c => c[1] === 'order_created');
sprawdz(zakup && zakup[2].amount === 990 && zakup[2].currency === 'PLN', `order_created = wartość towarów bez dostawy: ${zakup && zakup[2].amount} ${zakup && zakup[2].currency}`);
sprawdz(zakup && sumaTowarow(zakup) === 990, `ceny towarów przeskalowane do wartości towarów: suma ${zakup && sumaTowarow(zakup)}`);
sprawdz(zakup && zakup[3].event_id === 'order_685311', 'event_id order_<numer>');

// 2. inna waluta; cena towaru zawyżona jak na abczoo.gr (13,91 przy wartości towarów 8,01)
r = uruchom('EUR (małe litery), cena towaru = wartość zamówienia', { pixel_id: 'TestPixel12345', currency: ' eur ', _towar: '13.91', _ilosc: '1.000', _towary: '8.01' });
zakup = r.calls.find(c => c[1] === 'order_created');
sprawdz(zakup && zakup[2].amount === 801 && zakup[2].contents[0].amount === 801 && zakup[2].currency === 'EUR', `order_created 801 EUR, towar ${zakup && zakup[2].contents[0].amount}`);
sprawdz(r.calls.filter(c => c[0] === 'measure').every(c => c[2].currency === 'EUR' && (c[2].contents || []).every(p => p.currency === 'EUR')), 'waluta EUR we wszystkich zdarzeniach i towarach');

// 3. ceny poprawne → bez zmian
r = uruchom('ceny towarów zgodne z wartością towarów', { pixel_id: 'TestPixel12345', currency: 'PLN', _towary: '9.80' });
zakup = r.calls.find(c => c[1] === 'order_created');
sprawdz(zakup && zakup[2].contents[0].amount === 490 && zakup[2].amount === 980, 'ceny poprawne → bez skalowania');

// 4. brak Pixel ID (pole puste po imporcie) albo zmienna niepodstawiona
for (const [opis, pid] of [['pusty pixel_id', ''], ['niepodstawione [config:pixel_id]', '[config:pixel_id]']]) {
  r = uruchom(opis, { pixel_id: pid, currency: 'PLN' });
  sprawdz(/po zgodzie — SDK wstawione: 0 \|/.test(r.linie) && !r.calls.some(c => c[0] === 'init' && c[1].pixelId), `${opis}: SDK się nie ładuje, brak init`);
}
// 5. waluta niepoprawna → PLN
r = uruchom('waluta niepoprawna', { pixel_id: 'TestPixel12345', currency: 'złote' });
sprawdz(r.calls.find(c => c[1] === 'order_created')[2].currency === 'PLN', 'niepoprawna waluta → PLN');

// 6. oppref ze strony wejścia (document.referrer) — dodatek consent w izolowanym kontekście
const vm = require('vm');
const consentKod = kody[1].replace(/\[config:pixel_id\]/g, 'TestPixel12345').match(/<script>([\s\S]*?)<\/script>/)[1];
function consent({ search = '', cookie = '', referrer = '' }) {
  const q = []; const stub = function () { q.push(Array.from(arguments)); }; stub.q = [];
  const ctx = {
    window: {}, location: { search, host: 'sklep.pl' }, URL, URLSearchParams,
    document: { cookie, referrer, querySelector: () => null, createElement: () => ({ setAttribute() {} }), getElementsByTagName: () => [{ parentNode: { insertBefore() {} } }] }
  };
  ctx.window = ctx; ctx.oaiq = stub; ctx.oaiqBuffer = [];
  vm.runInNewContext(consentKod, ctx);
  return q;
}
const kolejnosc = q => q.map(c => c[0] + (c[1] && c[1].oppref ? '(oppref=' + c[1].oppref + ')' : c[1] && c[1].pixelId ? '(pixelId)' : '')).join(' → ');
let q = consent({ referrer: 'https://sklep.pl/?oppref=klik123&x=1' });
sprawdz(kolejnosc(q) === 'init(pixelId) → consent → init(oppref=klik123)', `referrer z oppref: ${kolejnosc(q)}`);
q = consent({ search: '?oppref=nowy', referrer: 'https://sklep.pl/?oppref=klik123' });
sprawdz(!q.some(c => c[1] && c[1].oppref), 'oppref w adresie bieżącej strony → bez drugiego init (SDK weźmie z adresu)');
q = consent({ cookie: 'a=1; __oppref=stary', referrer: 'https://sklep.pl/?oppref=klik123' });
sprawdz(!q.some(c => c[1] && c[1].oppref), 'jest cookie __oppref → bez drugiego init');
q = consent({ referrer: 'https://chatgpt.com/?oppref=obcy' });
sprawdz(!q.some(c => c[1] && c[1].oppref), 'referrer z innej domeny → ignorowany');
q = consent({ referrer: 'nie-adres' });
sprawdz(kolejnosc(q) === 'init(pixelId) → consent', 'zły referrer → bez błędu, bez drugiego init');

console.log(bledy ? `\n${bledy} BŁĘDÓW` : '\nWSZYSTKO OK');
process.exit(bledy ? 1 : 0);
