// Logika WT.zastosujPlan na symulowanym panelu (zachowanie z ANALIZA §11: import ICF zawsze wyłącza mail języka).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const DOMENA = 'zooart6.yourtechnicaldomain.com';
globalThis.location = { hostname: DOMENA };

function swiezyWT() {
  delete require.cache[require.resolve('../panel_core.js')];
  return require('../panel_core.js');
}

const icf = (tytul) => '<contents message_type="mail"><content type="title"><![CDATA[' + tytul + ']]></content>' +
  '<content type="active">y</content></contents>';

// stan: { mail: {pol, eng}, sms, tresc: {pol, eng}, importBlad, przepiszPoZapisie }
function sztucznyPanel(WT, stan) {
  const wywolania = [];
  WT.pobierzEdycje = async () => ({ jezyki: Object.keys(stan.mail),
    formularz: { mail: Object.assign({}, stan.mail), sms: stan.sms, webpush: {} }, ostatnia_edycja: null });
  WT.pobierzIcf = async (t, s, j) => stan.tresc[j];
  WT.importujIcf = async (p) => {
    wywolania.push('import ' + p.jezyk);
    stan.mail[p.jezyk] = 'n';                       // panel wyłącza mail już przy wgraniu
    if (stan.importBlad) throw new Error('Panel nie odpowiedział: komunikat po imporcie');
    stan.tresc[p.jezyk] = p.xml;
    return 'Import przebiegł pomyślnie.';
  };
  WT.zapiszFlagi = async (p) => {
    wywolania.push('flagi ' + JSON.stringify(p.mail) + ' sms=' + p.sms);
    Object.assign(stan.mail, p.mail);
    if (p.sms) stan.sms = p.sms;
    if (stan.przepiszPoZapisie) stan.tresc.eng = icf('PRZEPISANE');
  };
  WT.eksportuj = async (o) => { wywolania.push('eksport ' + o.rodzaj + ' ' + o.templates.join(',')); wywolania.dodatki = o.dodatki; return { nazwa: 'x.zip' }; };
  return wywolania;
}

async function planImportu(WT, stan, flagiZPlanu, opcje) {
  return {
    wersja: 1, rodzaj: 'import', domena: (opcje && opcje.domena) || DOMENA, shop_id: 1,
    pozycje: [{ template: 't', nazwa: 'T', jezyk: 'eng', plik: 't__eng.icf', odcisk_oryginalu: await WT.odcisk(stan.tresc.eng) }],
    oczekiwane_flagi: { t: { mail: flagiZPlanu, sms: 'n' } },
  };
}

const mapa = { 't__eng.icf': { text: async () => icf('Nowy') } };

test('po imporcie przywraca flagi sprzed importu, nie z eksportu (mail włączony w panelu, w planie wyłączony)', async () => {
  const WT = swiezyWT();
  const stan = { mail: { pol: 'y', eng: 'y' }, sms: 'n', tresc: { pol: icf('P'), eng: icf('Stary') } };
  sztucznyPanel(WT, stan);
  const plan = await planImportu(WT, stan, { pol: 'y', eng: 'n' });
  await WT.zastosujPlan(plan, mapa, { shop: 1 });
  assert.equal(stan.mail.eng, 'y');
});

test('nie włącza wysyłki, której w panelu nie było (w planie włączona)', async () => {
  const WT = swiezyWT();
  const stan = { mail: { pol: 'y', eng: 'n' }, sms: 'n', tresc: { pol: icf('P'), eng: icf('Stary') } };
  sztucznyPanel(WT, stan);
  const plan = await planImportu(WT, stan, { pol: 'y', eng: 'y' });
  await WT.zastosujPlan(plan, mapa, { shop: 1 });
  assert.equal(stan.mail.eng, 'n');
});

test('przerwany import: flagi przywrócone, błąd w wyniku, weryfikacja z flagami sprzed importu', async () => {
  const WT = swiezyWT();
  const stan = { mail: { pol: 'y', eng: 'y' }, sms: 'n', tresc: { pol: icf('P'), eng: icf('Stary') }, importBlad: true };
  const wywolania = sztucznyPanel(WT, stan);
  const log = [];
  const plan = await planImportu(WT, stan, { pol: 'y', eng: 'y' });
  const wynik = await WT.zastosujPlan(plan, mapa, { shop: 1, loguj: (t) => log.push(t) });
  assert.equal(stan.mail.eng, 'y');
  assert.equal(wynik.bledy.length, 1);
  assert.ok(wywolania.includes('eksport weryfikacja t'));
  assert.deepEqual(wywolania.dodatki.flagi_przed_importem.t.mail, { pol: 'y', eng: 'y' });
});

test('migracja do innego sklepu: najpierw kopia sklepu docelowego', async () => {
  const WT = swiezyWT();
  const stan = { mail: { pol: 'y', eng: 'y' }, sms: 'n', tresc: { pol: icf('P'), eng: icf('Stary') } };
  const wywolania = sztucznyPanel(WT, stan);
  const plan = await planImportu(WT, stan, { pol: 'y', eng: 'y' }, { domena: 'inny.iai-shop.com' });
  await WT.zastosujPlan(plan, mapa, { shop: 1 });
  assert.equal(wywolania[0], 'eksport eksport t');
  assert.ok(wywolania.indexOf('import eng') > 0);
});

test('ostrzega, gdy zapis formularza po imporcie zmienił wgraną treść', async () => {
  const WT = swiezyWT();
  const stan = { mail: { pol: 'y', eng: 'y' }, sms: 'n', tresc: { pol: icf('P'), eng: icf('Stary') }, przepiszPoZapisie: true };
  sztucznyPanel(WT, stan);
  const log = [];
  const plan = await planImportu(WT, stan, { pol: 'y', eng: 'y' });
  await WT.zastosujPlan(plan, mapa, { shop: 1, loguj: (t) => log.push(t) });
  assert.ok(log.some((l) => /UWAGA.*treść/.test(l)), log.join('\n'));
});
