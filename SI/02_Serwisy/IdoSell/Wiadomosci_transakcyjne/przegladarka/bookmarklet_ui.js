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
