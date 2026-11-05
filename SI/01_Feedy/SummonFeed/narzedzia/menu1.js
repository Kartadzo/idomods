// Odczyt węzłów Menu 1 z /panel/navigation.php?action=menuTree&shop=<id>&tree=1&lang=pol
// Wklejany do javascript_tool (Claude in Chrome) na stronie drzewa menu. Tylko odczyt —
// klika wyłącznie „showChildren” (rozwinięcie gałęzi).
// Wynik: window.__menu1 = ["<id>|<ścieżka>", ...], window.__menu1_trafienia = {zmienna: "|id|nazwa|..."}
// ID węzła = li.menu_li_item#m<ID>, ścieżka = .showoptions[data-path] (nazwy rodziców rozdzielone " \ ").
// Słowa kluczowe dopasowuję do całej ścieżki, więc węzły podrzędne dziedziczą trafienie rodzica.
(async () => {
  const zbierz = () => [...document.querySelectorAll('li.menu_li_item')].map(li => {
    const d = li.querySelector('.showoptions');
    return li.id.replace(/^m/, '') + '|' + (d ? d.dataset.path : '?');
  });
  for (let r = 0; r < 6; r++) {
    const t = [...document.querySelectorAll('li.menu_li_item .showChildren')].filter(a => !a.dataset.__k);
    t.forEach(a => { a.dataset.__k = 1; a.click(); });
    if (!t.length) break;
    await new Promise(res => setTimeout(res, 1500));
  }
  window.__menu1 = zbierz();
  // słowa kluczowe — uzupełnić o nazwy sklepu (np. „Dla Panów”); kolejność age_group: od najmłodszych
  const slowa = {
    gender_male_id_menu: /męsk|mężczy|dla pan(a|ów)|chłop/i,
    gender_female_id_menu: /damsk|kobie|dla pa(ni|ń)|dziewcz/i,
    gender_unisex_id_menu: /unisex/i,
    age_group_newborn_id_menu: /noworod/i,
    age_group_infant_id_menu: /niemowl/i,
    age_group_toddler_id_menu: /maluch|przedszkol/i,
    age_group_kids_id_menu: /dzieci|dziecię|chłopię|dziewczę|junior/i,
    age_group_adult_id_menu: /dorosł|senior/i,
  };
  window.__menu1_trafienia = {};
  for (const [zmienna, wzorzec] of Object.entries(slowa)) {
    const trafione = window.__menu1.filter(w => wzorzec.test(w.split('|')[1]));
    // zapis |id|nazwa węzła| (nazwa = ostatni człon ścieżki, czytelna dla człowieka)
    window.__menu1_trafienia[zmienna] = '|' + trafione.map(w => {
      const [id, sciezka] = w.split('|');
      return id + '|' + sciezka.split(' \\ ').pop().trim();
    }).join('|') + (trafione.length ? '|' : '');
  }
  window.__menu1_wspoldzielone_komunikat = /współdzieli swoje ustawienia z/.test(document.body.innerText);
  return [window.__menu1.length, window.__menu1_trafienia];
})()
