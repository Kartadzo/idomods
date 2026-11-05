const fs = require('fs');
const dir = process.argv[2];
const sample = {
  itemcardpage_product_name: "Buty O'Neill \"test\"", itemcardpage_product_id: '1641',
  itemcardpage_product_price_gross_float: '249.90', product_id: '1641', product_count: '2.000',
  product_price_gross_float: '4.90', product_name: "Gąbka KAPS d'Or",
  client_email: 'Jan.Kowalski@example.com', client_phone_e164: '', client_name: 'Jan',
  client_lastname: "O'Kowalski", client_country_code: 'pl', client_city: "Dęblin",
  client_province: 'lubelskie', client_zip: '08-530', order_worth_cpa2: '14.80', order_sn: '685311'
};
const render = s => s.replace(/\[iai:foreach_products_(begin|end)\]/g, '').replace(/\[iai:([a-z0-9_]+)\]/g, (m, k) => (k in sample ? sample[k] : m));
// minimalny DOM: templates i spany z kontenerów
const nodes = {};
function buildDom(html) {
  for (const m of html.matchAll(/<template id="([^"]+)">([\s\S]*?)<\/template>/g)) nodes['#' + m[1]] = { content: { textContent: m[2] } };
  for (const m of html.matchAll(/<div id="([^"]+)" hidden>([\s\S]*?)<\/div>/g)) {
    const spans = [...m[2].matchAll(/<span data-oaiq-id="([^"]*)" data-oaiq-qty="([^"]*)" data-oaiq-price="([^"]*)">([\s\S]*?)<\/span>/g)]
      .map(s => ({ getAttribute: a => ({ 'data-oaiq-id': s[1], 'data-oaiq-qty': s[2], 'data-oaiq-price': s[3] })[a], textContent: s[4] }));
    nodes['#' + m[1]] = { querySelectorAll: () => spans };
  }
}
let sdkInserted = 0;
global.window = global;
global.document = {
  createElement: () => ({ setAttribute() {} }),
  getElementsByTagName: () => [{ parentNode: { insertBefore() { sdkInserted += 1; } } }],
  querySelector: sel => (sel === 'script[data-oaiq-sdk]' ? (sdkInserted ? {} : null) : nodes[sel] || null)
};
const files = fs.readdirSync(dir).filter(f => f.endsWith('.html')).sort();
const scripts = {};
for (const f of files) {
  const html = render(fs.readFileSync(dir + '/' + f, 'utf8'));
  buildDom(html);
  scripts[f] = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
  try { new Function(scripts[f]); console.log('składnia OK  ', f); } catch (e) { console.log('BŁĄD składni', f, e.message); }
}
// init: tylko kolejka (stub), bez SDK i bez consent false
eval(scripts['01_chatgpt_init.html']);
const stub = window.oaiq;
// zdarzenia PRZED zgodą (losowa kolejność dodatków dynamicznych)
eval(scripts['04_contents_viewed.html']);
eval(scripts['07_order_created.html']);
console.log('przed zgodą — w kolejce SDK:', stub.q.length, '| w buforze:', window.oaiqBuffer.length, '| SDK wstawione:', sdkInserted);
eval(scripts['02_consent.html']);
eval(scripts['02_consent.html']); // drugi raz: bez dubli init/SDK
eval(scripts['06_checkout_started.html']);
console.log('po zgodzie — SDK wstawione:', sdkInserted, '| w buforze:', window.oaiqBuffer.length);
const calls = stub.q.map(a => Array.from(a));
console.log('consent false w kolejce:', calls.some(c => c[0] === 'consent' && c[1] === false));
console.log(JSON.stringify(calls, null, 1));
