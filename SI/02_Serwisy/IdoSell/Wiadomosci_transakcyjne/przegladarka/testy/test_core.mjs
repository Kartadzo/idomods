import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

const require = createRequire(import.meta.url);
const WT = require('../panel_core.js');

test('crc32 — wektor standardowy', () => {
  assert.equal(WT.crc32(new TextEncoder().encode('123456789')), 0xCBF43926);
});

// Ten sam tekst i wynik co WEKTOR / WEKTOR_ODCISK w testy/test_icf.py.
const WEKTOR = '<contents message_type="mail"><content type="text_main_0"><![CDATA[<p>Ż & ]]]]><![CDATA[>]]></content>' +
  '<content type="title">A &amp; B</content><content type="active">y</content></contents>' +
  '<contents message_type="sms"><content type="text_main_0"> </content></contents>' +
  '<enclosures><enclosure id="0">QUJD</enclosure></enclosures>';

test('odcisk treści zgodny z Pythonem (wt.icf.odcisk)', async () => {
  assert.equal(await WT.odcisk(WEKTOR), 'df229c2e450ca6e63bc58fc5b6a9d8fd7bd676fe4703175521d59965cf1f7fea');
});

test('odcisk pomija flagi, ustawienia techniczne i formę zapisu', async () => {
  const inny = WEKTOR.replace('<content type="active">y</content>', '<content type="active">n</content><content type="disposition">n</content>')
    .replace('A &amp; B', '<![CDATA[A & B]]>');
  assert.equal(await WT.odcisk(inny), await WT.odcisk(WEKTOR));
  assert.notEqual(await WT.odcisk(WEKTOR.replace('QUJD', 'AAAA')), await WT.odcisk(WEKTOR));
});

test('parsujStan', () => {
  assert.deepEqual(WT.parsujStan(' tak '), { stan: 'tak', braki: null });
  assert.deepEqual(WT.parsujStan('nie dotyczy'), { stan: 'nie dotyczy', braki: null });
  assert.deepEqual(WT.parsujStan('takdo uzupełnienia szablony: (2 z 3)'), { stan: 'tak', braki: '2 z 3' });
  assert.deepEqual(WT.parsujStan('nie'), { stan: 'nie', braki: null });
  assert.deepEqual(WT.parsujStan(''), { stan: null, braki: null });
});

test('parametr z adresu', () => {
  const href = '/panel/config-messages.php?populate=edit&template=order_confirmation&shop=1';
  assert.equal(WT.parametr(href, 'template'), 'order_confirmation');
  assert.equal(WT.parametr(href, 'shop'), '1');
  assert.equal(WT.parametr(href, 'group'), null);
});

test('doJson odporny na Array#toJSON z Prototype.js', () => {
  Array.prototype.toJSON = function () { return 'ZEPSUTE'; };
  try {
    assert.equal(WT.doJson({ a: [1, 'ż'] }).replace(/\s/g, ''), '{"a":[1,"ż"]}');
    assert.equal(typeof Array.prototype.toJSON, 'function');   // przywrócone
  } finally {
    delete Array.prototype.toJSON;
  }
});

test('zbudujZip czytelny dla Pythona (zipfile)', () => {
  const zip = WT.zbudujZip([{ nazwa: 'manifest.json', dane: '{"wersja":1}' }, { nazwa: 'icf/ą__b/pol.icf', dane: '<x>żółć</x>' }]);
  const katalog = mkdtempSync(join(tmpdir(), 'wt-'));
  const sciezka = join(katalog, 'test.zip');
  writeFileSync(sciezka, zip);
  const py = spawnSync('python', ['-I', '-c',
    'import sys,zipfile;z=zipfile.ZipFile(sys.argv[1]);assert z.testzip() is None;' +
    'sys.stdout.buffer.write(z.read("icf/ą__b/pol.icf"))', sciezka]);
  assert.equal(py.status, 0, py.stderr.toString());
  assert.equal(py.stdout.toString('utf8'), '<x>żółć</x>');
});
