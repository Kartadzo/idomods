// Buduje strony testowe z dodatków: node build.js <folder_dodatkow> <folder_wyjscia>
const fs = require('fs');
const path = require('path');
const [dir, out] = process.argv.slice(2);
const sample = {
  itemcardpage_product_name: "Buty O'Neill \"test\"", itemcardpage_product_id: '1641',
  itemcardpage_product_price_gross_float: '4.9', product_id: '1641', product_count: '1.000',
  product_price_gross_float: '4.90', product_name: "Gąbka KAPS d'Or",
  client_email: ' Jan.Kowalski@Example.com ', client_phone_e164: '+48600100200',
  client_name: "Jan", client_lastname: "O'Kowalski-Łęcki", client_country_code: 'pl',
  client_city: 'Dęblin', client_province: 'lubelskie', client_zip: '08-530',
  order_worth_cpa2: '14.80', order_sn: '700001'
};
const render = s => s.replace(/\[iai:foreach_products_(begin|end)\]/g, '').replace(/\[iai:([a-z0-9_]+)\]/g, (m, k) => (k in sample ? sample[k] : m));
const read = f => render(fs.readFileSync(path.join(dir, f), 'utf8'));

// Przechwytywanie: nic nie wychodzi do OpenAI, treść ląduje w localStorage.__cap
const intercept = `<script>
(function(){
  function push(k,u,b){try{var a=JSON.parse(localStorage.getItem('__cap')||'[]');a.push({k:k,page:location.pathname,u:String(u).split('?')[0],b:b==null?null:String(b)});localStorage.setItem('__cap',JSON.stringify(a))}catch(e){}}
  var of=window.fetch;
  window.fetch=function(u,o){var url=String(u&&u.url||u);if(/bzr\\.openai\\.com\\/v1/.test(url)){push('fetch',url,o&&o.body);return Promise.resolve(new Response('{}',{status:200}))}return of.apply(this,arguments)};
  navigator.sendBeacon=function(u,d){if(/openai/.test(u)){push('beacon',u,d);return true}return false};
})();
</script>`;

// Symulacja IdoSell: init statycznie w head, reszta "dynamicznie" po chwili, w podanej kolejności
const dyn = (files, delay) => `<div id="dyn"></div><script>
var parts=${JSON.stringify(files.map(read)).replace(/<\//g, '<\\/')};
setTimeout(function(){parts.forEach(function(html){var box=document.createElement('div');box.innerHTML=html;
  Array.from(box.childNodes).forEach(function(n){if(n.tagName==='SCRIPT'){var s=document.createElement('script');s.text=n.text;document.body.appendChild(s)}else{document.body.appendChild(n)}})})},${delay});
</script>`;

const page = (title, dynFiles) => `<!doctype html><html><head><meta charset="utf-8"><title>${title}</title>${intercept}${read('01_chatgpt_init.html')}</head>
<body><h1>${title}</h1><a href="page2.html">dalej</a>${dyn(dynFiles, 300)}</body></html>`;

fs.mkdirSync(out, { recursive: true });
// strona wejścia: zdarzenia przed zgodą, consent na końcu
fs.writeFileSync(path.join(out, 'page1.html'), page('karta towaru', ['03_page_viewed.html', '04_contents_viewed.html', '02_consent.html']));
// kolejna strona (zamówienie): order_created przed consent
fs.writeFileSync(path.join(out, 'page2.html'), page('po zamowieniu', ['07_order_created.html', '03_page_viewed.html', '02_consent.html']));
// strona bez zgody: consent nie jest wstrzykiwany
fs.writeFileSync(path.join(out, 'page3.html'), page('bez zgody', ['03_page_viewed.html', '04_contents_viewed.html']));
console.log('OK', out);
