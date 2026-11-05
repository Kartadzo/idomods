<!--
  ============================================================================
  Mapowanie kategorii sklepu -> kategoria Ceneo.  XSLT 1.0, kontekst <product>.
  Wygenerowane przez mapowanie_kategorii.py — nie edytować ręcznie,
  zmiany nanosić w tablicach REGULY / MENU w skrypcie i przegenerować.

  Zmienna $ceneo_cat zawiera pełną ścieżkę kategorii Ceneo albo pusty łańcuch.
  Zmienna $ceneo_cat_id zawiera identyfikator kategorii Ceneo.

  Użycie w <cat> (zachowuje dotychczasowe zachowanie tam, gdzie brak mapowania):
      <cat>
        <xsl:choose>
          <xsl:when test="$ceneo_cat != ''"><xsl:value-of select="$ceneo_cat"/></xsl:when>
          <xsl:otherwise><xsl:value-of select="translate(category/@name, '&gt;', '/')"/></xsl:otherwise>
        </xsl:choose>
      </cat>

  UWAGA: <cat> w formacie Ceneo to kategoria SKLEPU, nie pole na identyfikator
  kategorii Ceneo — podanie tu ścieżki ze słownika Ceneo tylko ułatwia serwisowi
  automatyczne dopasowanie. Właściwym odbiorcą $ceneo_cat_id jest warunkowanie
  atrybutów w bloku <attrs>, które w Ceneo są definiowane per kategoria.

  WERSJE ELEKTRONICZNE: mapowanie opiera się na kategorii sklepu, więc ebook
  dostanie kategorię książki papierowej. Jeśli w bloku <attrs> wyliczana jest
  zmienna $cp_wersja (sufiks code_producer), warto ją nałożyć przed tym blokiem:
      <xsl:variable name="ceneo_cat_id">
        <xsl:choose>
          <xsl:when test="$cp_wersja = '3'">3451</xsl:when>
          <xsl:when test="$cp_wersja = '1' or $cp_wersja = '2'">3453</xsl:when>
          ... dalej reguły poniżej ...
  gdzie 3451 = Księgarnia > E-booki > Pozostałe E-booki, 3453 = Księgarnia > Audiobooki.
  Dotyczy 202 produktów; przy większym wolumenie warto rozbić E-booki na
  podkategorie tematyczne (3439-3451) zamiast wrzucać wszystko do 3451.
  ============================================================================
-->
<xsl:variable name="iai_id" select="normalize-space(iai_category/@id)"/>
<xsl:variable name="menu_path" select="normalize-space(iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item/@textid)"/>

<xsl:variable name="ceneo_cat_id">
  <xsl:choose>
    <xsl:when test="$iai_id = '5663'">410</xsl:when><!-- 6648 szt. Media > Komiksy -->
    <xsl:when test="$iai_id = '5704'">403</xsl:when><!-- 6606 szt. Media > Książki > Książki dla dzieci i młodzieży > Beletrystyka, powieści -->
    <xsl:when test="$iai_id = '5718'">430</xsl:when><!-- 4796 szt. Media > Książki > Książki do nauki języka obcego > Angielski -->
    <xsl:when test="$iai_id = '5773'">425</xsl:when><!-- 4623 szt. Media > Książki > Literatura piękna, popularna i faktu > Literatura obyczajowa -->
    <xsl:when test="$iai_id = '5740'">409</xsl:when><!-- 4612 szt. Media > Książki > Książki naukowe i popularnonaukowe > Historia, archeologia -->
    <xsl:when test="$iai_id = '5750'">408</xsl:when><!-- 3748 szt. Media > Książki > Książki naukowe i popularnonaukowe > Psychologia, socjologia -->
    <xsl:when test="$iai_id = '5771'">414</xsl:when><!-- 3415 szt. Media > Książki > Literatura piękna, popularna i faktu > Kryminały -->
    <xsl:when test="$iai_id = '5774'">425</xsl:when><!-- 3398 szt. Media > Książki > Literatura piękna, popularna i faktu > Literatura piękna - proza polska -->
    <xsl:when test="$iai_id = '5780'">420</xsl:when><!-- 3316 szt. Media > Książki > Literatura piękna, popularna i faktu > Romanse -->
    <xsl:when test="$iai_id = '5779'">409</xsl:when><!-- 3240 szt. Media > Książki > Literatura piękna, popularna i faktu > Reportaż, literatura faktu -->
    <xsl:when test="$iai_id = '5713'">403</xsl:when><!-- 2700 szt. Media > Książki > Książki dla dzieci i młodzieży > Popularnonaukowe -->
    <xsl:when test="$iai_id = '5751'">445</xsl:when><!-- 2612 szt. Media > Książki > Książki naukowe i popularnonaukowe > Religioznawstwo, nauki teologiczne -->
    <xsl:when test="$iai_id = '5765'">2493</xsl:when><!-- 2554 szt. Media > Książki > Literatura piękna, popularna i faktu > Biografie, wspomnienia -->
    <xsl:when test="$iai_id = '5754'">413</xsl:when><!-- 2215 szt. Media > Książki > Książki naukowe i popularnonaukowe > Technika, nauki techniczne -->
    <xsl:when test="$iai_id = '5776'">418</xsl:when><!-- 2197 szt. Media > Książki > Literatura piękna, popularna i faktu > Poezja -->
    <xsl:when test="$iai_id = '5744'">422</xsl:when><!-- 1832 szt. Media > Książki > Książki naukowe i popularnonaukowe > Medycyna, nauki medyczne -->
    <xsl:when test="$iai_id = '5749'">401</xsl:when><!-- 1741 szt. Media > Książki > Książki naukowe i popularnonaukowe > Prawo, administracja -->
    <xsl:when test="$iai_id = '5746'">408</xsl:when><!-- 1688 szt. Media > Książki > Książki naukowe i popularnonaukowe > Pedagogika, resocjalizacja -->
    <xsl:when test="$iai_id = '5736'">408</xsl:when><!-- 1493 szt. Media > Książki > Książki naukowe i popularnonaukowe > Filologie, językoznawstwo -->
    <xsl:when test="$iai_id = '5837'">2701</xsl:when><!-- 1485 szt. Media > Książki > Poradniki i albumy > Moda, uroda -->
    <xsl:when test="$iai_id = '5702'">403</xsl:when><!-- 1462 szt. Media > Książki > Książki dla dzieci i młodzieży > Bajki i wierszyki -->
    <xsl:when test="$iai_id = '5841'">2701</xsl:when><!-- 1419 szt. Media > Książki > Poradniki i albumy > Pozostałe -->
    <xsl:when test="$iai_id = '5805'">412</xsl:when><!-- 1351 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Liceum > Przedmioty zawodowe -->
    <xsl:when test="$iai_id = '5769'">414</xsl:when><!-- 1314 szt. Media > Książki > Literatura piękna, popularna i faktu > Horrory -->
    <xsl:when test="$iai_id = '5737'">408</xsl:when><!-- 1277 szt. Media > Książki > Książki naukowe i popularnonaukowe > Filozofia, historia filozofii -->
    <xsl:when test="$iai_id = '5788'">399</xsl:when><!-- 1170 szt. Media > Książki > Mapy, przewodniki, książki podróżnicze > Przewodniki, książki krajoznawcze -->
    <xsl:when test="$iai_id = '5741'">398</xsl:when><!-- 1142 szt. Media > Książki > Książki naukowe i popularnonaukowe > Informatyka, internet -->
    <xsl:when test="$iai_id = '5767'">407</xsl:when><!-- 1110 szt. Media > Książki > Literatura piękna, popularna i faktu > Fantasy -->
    <xsl:when test="$iai_id = '5748'">2746</xsl:when><!-- 1093 szt. Media > Książki > Książki naukowe i popularnonaukowe > Pozostałe -->
    <xsl:when test="$iai_id = '5733'">400</xsl:when><!-- 1084 szt. Media > Książki > Książki naukowe i popularnonaukowe > Biznes, nauki ekonomiczne -->
    <xsl:when test="$iai_id = '5719'">432</xsl:when><!-- 1068 szt. Media > Książki > Książki do nauki języka obcego > Francuski -->
    <xsl:when test="$iai_id = '5747'">447</xsl:when><!-- 960 szt. Media > Książki > Książki naukowe i popularnonaukowe > Politologia, stos. Międzynarodowe -->
    <xsl:when test="$iai_id = '5753'">421</xsl:when><!-- 945 szt. Media > Książki > Książki naukowe i popularnonaukowe > Sztuka, kultura i etnologia -->
    <xsl:when test="$iai_id = '5764'">425</xsl:when><!-- 889 szt. Media > Książki > Literatura piękna, popularna i faktu -->
    <xsl:when test="$iai_id = '5830'">406</xsl:when><!-- 884 szt. Media > Książki > Poradniki i albumy > Ezoteryka, magia, UFO -->
    <xsl:when test="$iai_id = '5724'">434</xsl:when><!-- 861 szt. Media > Książki > Książki do nauki języka obcego > Niemiecki -->
    <xsl:when test="$iai_id = '5756'">724</xsl:when><!-- 840 szt. Media > Książki > Książki obcojęzyczne > Po angielsku -->
    <xsl:when test="$iai_id = '5855'">2701</xsl:when><!-- 826 szt. Media > Książki > Poradniki i albumy > Życie codzienne, obyczaje -->
    <xsl:when test="$iai_id = '5720'">433</xsl:when><!-- 800 szt. Media > Książki > Książki do nauki języka obcego > Hiszpański -->
    <xsl:when test="$iai_id = '5714'">403</xsl:when><!-- 797 szt. Media > Książki > Książki dla dzieci i młodzieży > Poradniki -->
    <xsl:when test="$iai_id = '5742'">408</xsl:when><!-- 795 szt. Media > Książki > Książki naukowe i popularnonaukowe > Literaturoznawstwo -->
    <xsl:when test="$iai_id = '5763'">724</xsl:when><!-- 762 szt. Media > Książki > Książki obcojęzyczne > Pozostałe -->
    <xsl:when test="$iai_id = '5715'">403</xsl:when><!-- 732 szt. Media > Książki > Książki dla dzieci i młodzieży > Pozostałe -->
    <xsl:when test="$iai_id = '5703'">403</xsl:when><!-- 731 szt. Media > Książki > Książki dla dzieci i młodzieży > Baśnie, podania i legendy -->
    <xsl:when test="$iai_id = '5768'">425</xsl:when><!-- 729 szt. Media > Książki > Literatura piękna, popularna i faktu > Historyczne -->
    <xsl:when test="$iai_id = '5840'">417</xsl:when><!-- 676 szt. Media > Książki > Poradniki i albumy > Muzyka, taniec, śpiew -->
    <xsl:when test="$iai_id = '5745'">409</xsl:when><!-- 625 szt. Media > Książki > Książki naukowe i popularnonaukowe > Militaria, broń, wojskowość -->
    <xsl:when test="$iai_id = '5782'">414</xsl:when><!-- 605 szt. Media > Książki > Literatura piękna, popularna i faktu > Thrillery, sensacyjne -->
    <xsl:when test="$iai_id = '5730'">2743</xsl:when><!-- 591 szt. Media > Książki > Książki naukowe i popularnonaukowe -->
    <xsl:when test="$iai_id = '5835'">411</xsl:when><!-- 557 szt. Media > Książki > Poradniki i albumy > Kuchnia, potrawy -->
    <xsl:when test="$iai_id = '5839'">419</xsl:when><!-- 478 szt. Media > Książki > Poradniki i albumy > Motywacja, rozwój osobisty -->
    <xsl:when test="$iai_id = '5828'">2701</xsl:when><!-- 452 szt. Media > Książki > Poradniki i albumy > Biznes, praca, prawo, finanse -->
    <xsl:when test="$iai_id = '5851'">426</xsl:when><!-- 447 szt. Media > Książki > Poradniki i albumy > Sztuka i architektura -->
    <xsl:when test="$iai_id = '5847'">2701</xsl:when><!-- 384 szt. Media > Książki > Poradniki i albumy > Rodzina, ciąża, wychowanie -->
    <xsl:when test="$iai_id = '5766'">418</xsl:when><!-- 383 szt. Media > Książki > Literatura piękna, popularna i faktu > Dramaty, utwory sceniczne -->
    <xsl:when test="$iai_id = '5786'">399</xsl:when><!-- 370 szt. Media > Książki > Mapy, przewodniki, książki podróżnicze > Mapy, atlasy, plany miast -->
    <xsl:when test="$iai_id = '5716'">403</xsl:when><!-- 365 szt. Media > Książki > Książki dla dzieci i młodzieży > Łamigłówki, zagadki i gry -->
    <xsl:when test="$iai_id = '5781'">407</xsl:when><!-- 361 szt. Media > Książki > Literatura piękna, popularna i faktu > Science fiction -->
    <xsl:when test="$iai_id = '5808'">412</xsl:when><!-- 359 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Przedszkole -->
    <xsl:when test="$iai_id = '5785'">399</xsl:when><!-- 326 szt. Media > Książki > Mapy, przewodniki, książki podróżnicze > Literatura podróżnicza -->
    <xsl:when test="$iai_id = '5729'">436</xsl:when><!-- 298 szt. Media > Książki > Książki do nauki języka obcego > Włoski -->
    <xsl:when test="$iai_id = '5790'">412</xsl:when><!-- 295 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Edukacja wczesnoszkolna -->
    <xsl:when test="$iai_id = '5833'">417</xsl:when><!-- 288 szt. Media > Książki > Poradniki i albumy > Hobby, kolekcjonerstwo -->
    <xsl:when test="$iai_id = '5801'">412</xsl:when><!-- 280 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Liceum > Matematyka -->
    <xsl:when test="$iai_id = '5775'">425</xsl:when><!-- 271 szt. Media > Książki > Literatura piękna, popularna i faktu > Literatura piękna - proza zagraniczna -->
    <xsl:when test="$iai_id = '5819'">412</xsl:when><!-- 253 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa > Matematyka -->
    <xsl:when test="$iai_id = '5850'">2592</xsl:when><!-- 249 szt. Media > Książki > Poradniki i albumy > Sport, forma fizyczna -->
    <xsl:when test="$iai_id = '5838'">453</xsl:when><!-- 222 szt. Media > Książki > Poradniki i albumy > Motoryzacja, transport -->
    <xsl:when test="$iai_id = '5735'">405</xsl:when><!-- 218 szt. Media > Książki > Książki naukowe i popularnonaukowe > Encyklopedie, słowniki, leksykony -->
    <xsl:when test="$iai_id = '5854'">424</xsl:when><!-- 210 szt. Media > Książki > Poradniki i albumy > Zwierzęta domowe i hodowlane -->
    <xsl:when test="$iai_id = '5772'">420</xsl:when><!-- 201 szt. Media > Książki > Literatura piękna, popularna i faktu > Literatura erotyczna -->
    <xsl:when test="$iai_id = '5777'">425</xsl:when><!-- 199 szt. Media > Książki > Literatura piękna, popularna i faktu > Pozostałe -->
    <xsl:when test="$iai_id = '5817'">412</xsl:when><!-- 182 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa > Język polski -->
    <xsl:when test="$iai_id = '5846'">426</xsl:when><!-- 167 szt. Media > Książki > Poradniki i albumy > Przyroda, krajobrazy -->
    <xsl:when test="$iai_id = '5778'">425</xsl:when><!-- 161 szt. Media > Książki > Literatura piękna, popularna i faktu > Przygodowe -->
    <xsl:when test="$iai_id = '5732'">2744</xsl:when><!-- 146 szt. Media > Książki > Książki naukowe i popularnonaukowe > Biologia, ekologia -->
    <xsl:when test="$iai_id = '5717'">431</xsl:when><!-- 143 szt. Media > Książki > Książki do nauki języka obcego -->
    <xsl:when test="$iai_id = '5793'">412</xsl:when><!-- 143 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Liceum > Chemia -->
    <xsl:when test="$iai_id = '2309'">2704</xsl:when><!-- 140 szt. Media > Gazety i czasopisma -->
    <xsl:when test="$iai_id = '5919'">2885</xsl:when><!-- 133 szt. Gry i zabawki > Zabawki > Zabawki edukacyjne > Zabawki naukowe > Globusy -->
    <xsl:when test="$iai_id = '5798'">412</xsl:when><!-- 132 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Liceum > Język polski -->
    <xsl:when test="$iai_id = '5728'">435</xsl:when><!-- 131 szt. Media > Książki > Książki do nauki języka obcego > Rosyjski -->
    <xsl:when test="$iai_id = '5792'">412</xsl:when><!-- 124 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Liceum > Biologia -->
    <xsl:when test="$iai_id = '5849'">2701</xsl:when><!-- 122 szt. Media > Książki > Poradniki i albumy > Seks, relacje partnerskie -->
    <xsl:when test="$iai_id = '5706'">403</xsl:when><!-- 115 szt. Media > Książki > Książki dla dzieci i młodzieży > Historie biblijne -->
    <xsl:when test="$iai_id = '1531'">2531</xsl:when><!-- 115 szt. Dzieci i niemowlęta -->
    <xsl:when test="$iai_id = '5755'">724</xsl:when><!-- 114 szt. Media > Książki > Książki obcojęzyczne -->
    <xsl:when test="$iai_id = '2103'">1069</xsl:when><!-- 111 szt. Gry i zabawki > Zabawki > Zabawki edukacyjne -->
    <xsl:when test="$iai_id = '5725'">431</xsl:when><!-- 106 szt. Media > Książki > Książki do nauki języka obcego > Polski dla obcokrajowców -->
    <xsl:when test="$iai_id = '5731'">413</xsl:when><!-- 100 szt. Media > Książki > Książki naukowe i popularnonaukowe > Architektura, budownictwo -->
    <xsl:when test="$iai_id = '5794'">412</xsl:when><!-- 100 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Liceum > Fizyka z astronomią -->
    <xsl:when test="$iai_id = '5743'">2744</xsl:when><!-- 98 szt. Media > Książki > Książki naukowe i popularnonaukowe > Matematyka, statystyka -->
    <xsl:when test="$iai_id = '5727'">431</xsl:when><!-- 97 szt. Media > Książki > Książki do nauki języka obcego > Pozostałe -->
    <xsl:when test="$iai_id = '5738'">2744</xsl:when><!-- 97 szt. Media > Książki > Książki naukowe i popularnonaukowe > Fizyka, astronomia -->
    <xsl:when test="$iai_id = '5734'">2744</xsl:when><!-- 94 szt. Media > Książki > Książki naukowe i popularnonaukowe > Chemia, biochemia -->
    <xsl:when test="$iai_id = '5818'">412</xsl:when><!-- 94 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa > Języki obce -->
    <xsl:when test="$iai_id = '5824'">412</xsl:when><!-- 93 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa > Religia, Etyka -->
    <xsl:when test="$iai_id = '5796'">412</xsl:when><!-- 91 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Liceum > Historia -->
    <xsl:when test="$iai_id = '5757'">724</xsl:when><!-- 90 szt. Media > Książki > Książki obcojęzyczne > Po francusku -->
    <xsl:when test="$iai_id = '6512'">1476</xsl:when><!-- 86 szt. Artykuły biurowe > Akcesoria biurowe > Piórniki -->
    <xsl:when test="$iai_id = '5804'">412</xsl:when><!-- 83 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Liceum > Pozostałe -->
    <xsl:when test="$iai_id = '5739'">2744</xsl:when><!-- 81 szt. Media > Książki > Książki naukowe i popularnonaukowe > Geografia, geologia, turystyka -->
    <xsl:when test="$iai_id = '5820'">412</xsl:when><!-- 75 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa > Muzyka -->
    <xsl:when test="$iai_id = '4404'">624</xsl:when><!-- 74 szt. Torby, walizki i akcesoria podróżne > Plecaki -->
    <xsl:when test="$iai_id = '5799'">412</xsl:when><!-- 71 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Liceum > Języki obce -->
    <xsl:when test="$iai_id = '5789'">412</xsl:when><!-- 71 szt. Media > Książki > Podręczniki do szkół podst. i średnich -->
    <xsl:when test="$iai_id = '2025'">1930</xsl:when><!-- 70 szt. Gry i zabawki > Gry > Gry planszowe -->
    <xsl:when test="$iai_id = '5795'">412</xsl:when><!-- 69 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Liceum > Geografia -->
    <xsl:when test="$iai_id = '5822'">412</xsl:when><!-- 60 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa > Pozostałe -->
    <xsl:when test="$iai_id = '5827'">2701</xsl:when><!-- 56 szt. Media > Książki > Poradniki i albumy -->
    <xsl:when test="$iai_id = '5770'">425</xsl:when><!-- 49 szt. Media > Książki > Literatura piękna, popularna i faktu > Humor, parodia, satyra -->
    <xsl:when test="$iai_id = '5752'">2745</xsl:when><!-- 48 szt. Media > Książki > Książki naukowe i popularnonaukowe > Rolnictwo, nauki rolnicze -->
    <xsl:when test="$iai_id = '5723'">431</xsl:when><!-- 46 szt. Media > Książki > Książki do nauki języka obcego > Języki skandynawskie -->
    <xsl:when test="$iai_id = '5701'">403</xsl:when><!-- 44 szt. Media > Książki > Książki dla dzieci i młodzieży -->
    <xsl:when test="$iai_id = '5709'">403</xsl:when><!-- 43 szt. Media > Książki > Książki dla dzieci i młodzieży > Książki z dodatkami -->
    <xsl:when test="$iai_id = '5815'">412</xsl:when><!-- 42 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa > Historia -->
    <xsl:when test="$iai_id = '2017'">3962</xsl:when><!-- 38 szt. Gry i zabawki > Gry -->
    <xsl:when test="$iai_id = '5759'">724</xsl:when><!-- 36 szt. Media > Książki > Książki obcojęzyczne > Po niemiecku -->
    <xsl:when test="$iai_id = '5797'">412</xsl:when><!-- 34 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Liceum > Informatyka, Technika -->
    <xsl:when test="$iai_id = '5813'">412</xsl:when><!-- 34 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa > Fizyka -->
    <xsl:when test="$iai_id = '5721'">431</xsl:when><!-- 33 szt. Media > Książki > Książki do nauki języka obcego > Języki klasyczne -->
    <xsl:when test="$iai_id = '5814'">412</xsl:when><!-- 33 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa > Geografia -->
    <xsl:when test="$iai_id = '5726'">431</xsl:when><!-- 32 szt. Media > Książki > Książki do nauki języka obcego > Portugalski -->
    <xsl:when test="$iai_id = '451'">2905</xsl:when><!-- 31 szt. Biznes i przemysł > Rolnictwo > Hodowla zwierząt -->
    <xsl:when test="$iai_id = '5823'">412</xsl:when><!-- 30 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa > Przyroda -->
    <xsl:when test="$iai_id = '5810'">412</xsl:when><!-- 29 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa > Biologia -->
    <xsl:when test="$iai_id = '5708'">403</xsl:when><!-- 28 szt. Media > Książki > Książki dla dzieci i młodzieży > Kolorowanki, malowanki i wycinanki -->
    <xsl:when test="$iai_id = '5848'">2701</xsl:when><!-- 27 szt. Media > Książki > Poradniki i albumy > Rękodzieło, biżuteria, szycie -->
    <xsl:when test="$iai_id = '5758'">724</xsl:when><!-- 27 szt. Media > Książki > Książki obcojęzyczne > Po hiszpańsku -->
    <xsl:when test="$iai_id = '5806'">412</xsl:when><!-- 25 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Liceum > Religia, Etyka -->
    <xsl:when test="$iai_id = '5700'">454</xsl:when><!-- 25 szt. Media > Książki > Kalendarze, gadżety i akcesoria > Pozostałe -->
    <xsl:when test="$iai_id = '5829'">2701</xsl:when><!-- 24 szt. Media > Książki > Poradniki i albumy > Dom i ogród -->
    <xsl:when test="$iai_id = '5811'">412</xsl:when><!-- 24 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa > Chemia -->
    <xsl:when test="$iai_id = '5800'">412</xsl:when><!-- 21 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Liceum > KOSS, WOS -->
    <xsl:when test="$iai_id = '5722'">431</xsl:when><!-- 20 szt. Media > Książki > Książki do nauki języka obcego > Języki orientalne -->
    <xsl:when test="$iai_id = '5821'">412</xsl:when><!-- 18 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa > Plastyka -->
    <xsl:when test="$iai_id = '6590'">1054</xsl:when><!-- 18 szt. Gry i zabawki > Zabawki > Dekoracje do zabawy > Klocki -->
    <xsl:when test="$iai_id = '5816'">412</xsl:when><!-- 16 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa > Informatyka -->
    <xsl:when test="$iai_id = '2071'">4256</xsl:when><!-- 16 szt. Gry i zabawki > Zabawki > Pojazdy do zabawy > Samochody -->
    <xsl:when test="$iai_id = '2183'">1159</xsl:when><!-- 15 szt. Gry i zabawki > Łamigłówki > Puzzle -->
    <xsl:when test="$iai_id = '143'">2341</xsl:when><!-- 14 szt. Artykuły biurowe > Artykuły różne > Artykuły papiernicze -->
    <xsl:when test="$iai_id = '5834'">2701</xsl:when><!-- 13 szt. Media > Książki > Poradniki i albumy > Internet, komputery -->
    <xsl:when test="$iai_id = '5762'">724</xsl:when><!-- 13 szt. Media > Książki > Książki obcojęzyczne > Po włosku -->
    <xsl:when test="$iai_id = '5761'">724</xsl:when><!-- 12 szt. Media > Książki > Książki obcojęzyczne > Po szwedzku -->
    <xsl:when test="$iai_id = '5787'">399</xsl:when><!-- 11 szt. Media > Książki > Mapy, przewodniki, książki podróżnicze > Pozostałe -->
    <xsl:when test="$iai_id = '6651'">1063</xsl:when><!-- 11 szt. Gry i zabawki > Zabawki > Maskotki -->
    <xsl:when test="$iai_id = '4160'">2186</xsl:when><!-- 10 szt. Sztuka i rozrywka > Hobby i sztuki piękne > Modelarstwo -->
    <xsl:when test="$iai_id = '5697'">454</xsl:when><!-- 10 szt. Media > Książki > Kalendarze, gadżety i akcesoria -->
    <xsl:when test="$iai_id = '4241'">3840</xsl:when><!-- 8 szt. Sztuka i rozrywka > Hobby i sztuki piękne > Rękodzieło i hobby > Materiały dla artystów i rękodzielników > Tekstylia -->
    <xsl:when test="$iai_id = '1591'">3813</xsl:when><!-- 8 szt. Dzieci i niemowlęta > Zabawki dla niemowląt -->
    <xsl:when test="$iai_id = '5698'">454</xsl:when><!-- 4 szt. Media > Książki > Kalendarze, gadżety i akcesoria > Adresowniki, pamiętniki -->
    <xsl:when test="$iai_id = '2162'">1201</xsl:when><!-- 4 szt. Gry i zabawki > Zabawki ogrodowe -->
    <xsl:when test="$iai_id = '5825'">412</xsl:when><!-- 4 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa > Wiedza o społeczeństwie -->
    <xsl:when test="$iai_id = '6607'">979</xsl:when><!-- 4 szt. Dzieci i niemowlęta > Karmienie > Termosy -->
    <xsl:when test="$iai_id = '692'">2068</xsl:when><!-- 3 szt. Dom i ogród > Artykuły gospodarstwa domowego > Przechowywanie i utrzymanie porządku > Przechowywanie zdjęć > Albumy na zdjęcia -->
    <xsl:when test="$iai_id = '1122'">5600</xsl:when><!-- 3 szt. Dom i ogród > Kuchnia i jadalnia > Transportery do żywności i napojów > Butelki na wodę -->
    <xsl:when test="$iai_id = '1335'">1176</xsl:when><!-- 3 szt. Dom i ogród > Parasole -->
    <xsl:when test="$iai_id = '6488'">3653</xsl:when><!-- 3 szt. Gry i zabawki > Prezenty -->
    <xsl:when test="$iai_id = '5809'">412</xsl:when><!-- 2 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa -->
    <xsl:when test="$iai_id = '5699'">454</xsl:when><!-- 2 szt. Media > Książki > Kalendarze, gadżety i akcesoria > Kalendarze ścienne -->
    <xsl:when test="$iai_id = '5791'">412</xsl:when><!-- 2 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Liceum -->
    <xsl:when test="$iai_id = '186'">5070</xsl:when><!-- 2 szt. Artykuły biurowe > Podkładki na biurko -->
    <xsl:when test="$iai_id = '2102'">2176</xsl:when><!-- 2 szt. Gry i zabawki > Zabawki > Zabawki do kąpieli -->
    <xsl:when test="$iai_id = '2024'">3957</xsl:when><!-- 2 szt. Gry i zabawki > Gry > Gry karciane -->
    <xsl:when test="$iai_id = '6650'">4624</xsl:when><!-- 2 szt. Dzieci i niemowlęta > Tekstylia dziecięce > Śpiworki -->
    <xsl:when test="$iai_id = '5812'">412</xsl:when><!-- 1 szt. Media > Książki > Podręczniki do szkół podst. i średnich > Szkoła podstawowa > Edukacja dla bezpieczeństwa -->
    <xsl:when test="$iai_id = '2321'">454</xsl:when><!-- 1 szt. Media > Książki -->
    <xsl:when test="$iai_id = '1148'">1249</xsl:when><!-- 1 szt. Dom i ogród > Kuchnia i jadalnia > Zastawy stołowe > Naczynia do napojów > Kubki -->
    <xsl:when test="$iai_id = '6188'">5065</xsl:when><!-- 1 szt. Dom i ogród > Ozdoby > Naklejki -->
    <xsl:when test="$iai_id = '5695'">2704</xsl:when><!-- 1 szt. Media > Gazety i czasopisma > Zbiory opowiadań -->
    <xsl:when test="$iai_id = '2035'">1066</xsl:when><!-- 1 szt. Gry i zabawki > Zabawki -->
    <!-- fallback: produkty bez iai_category (13851 szt.) — po ścieżce menu.
         Predykat na <item>, bo produkt bywa w kilku pozycjach menu naraz
         i pierwsza z nich bywa bezużyteczna ('Pozostałe'). -->
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki obcojęzyczne')]">724</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Fantastyka')]">407</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Science fiction')]">407</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Horror')]">414</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Kryminał')]">414</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Thriller')]">414</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Sensacja')]">414</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Romans')]">420</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Erotyka')]">420</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Poezja')]">418</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Biografie')]">2493</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Literatura faktu')]">409</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Historia')]">409</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Religijne')]">445</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Dla dzieci')]">403</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Dla młodzieży')]">403</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Komiksy')]">410</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Popularnonaukowe\Informatyka')]">398</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Popularnonaukowe\Prawo')]">401</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Popularnonaukowe\Medycyna')]">422</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Popularnonaukowe\Psychologia')]">408</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Popularnonaukowe\Filozofia')]">408</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Popularnonaukowe\Językoznawstwo')]">408</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Popularnonaukowe\Nauka i technika')]">413</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Popularnonaukowe')]">2743</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Podróże i turystyka')]">399</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Kultura i sztuka')]">421</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Zdrowie i uroda')]">2593</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Kulinaria')]">411</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Hobby')]">417</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Poradniki')]">2701</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki\Literatura piękna')]">425</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Podręczniki\Szkolne')]">412</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Podręczniki\Lektury')]">412</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Podręczniki')]">412</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Nauka języków obcych\Angielski')]">430</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Nauka języków obcych\Francuski')]">432</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Nauka języków obcych\Hiszpański')]">433</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Nauka języków obcych\Niemiecki')]">434</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Nauka języków obcych\Rosyjski')]">435</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Nauka języków obcych\Włoski')]">436</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Nauka języków obcych')]">431</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Ebooki')]">3451</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Audiobooki')]">3453</xsl:when>
    <xsl:when test="iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item[starts-with(@textid, 'Książki')]">454</xsl:when>
  </xsl:choose>
</xsl:variable>

<xsl:variable name="ceneo_cat">
  <xsl:choose>
    <xsl:when test="$ceneo_cat_id = '1054'">Dla dziecka/Zabawki/Klocki</xsl:when>
    <xsl:when test="$ceneo_cat_id = '1063'">Dla dziecka/Zabawki/Maskotki</xsl:when>
    <xsl:when test="$ceneo_cat_id = '1066'">Dla dziecka/Zabawki</xsl:when>
    <xsl:when test="$ceneo_cat_id = '1069'">Dla dziecka/Zabawki/Zabawki edukacyjne</xsl:when>
    <xsl:when test="$ceneo_cat_id = '1159'">Dla dziecka/Zabawki/Puzzle</xsl:when>
    <xsl:when test="$ceneo_cat_id = '1176'">Moda/Galanteria i dodatki/Parasole</xsl:when>
    <xsl:when test="$ceneo_cat_id = '1201'">Dla dziecka/Zabawki ogrodowe</xsl:when>
    <xsl:when test="$ceneo_cat_id = '1249'">Dom i wnętrze/Wyposażenie kuchni/Naczynia kuchenne/Kubki</xsl:when>
    <xsl:when test="$ceneo_cat_id = '1476'">Dla dziecka/Artykuły szkolne/Piórniki</xsl:when>
    <xsl:when test="$ceneo_cat_id = '1930'">Gry/Gry bez prądu/Gry planszowe</xsl:when>
    <xsl:when test="$ceneo_cat_id = '2068'">Fotografia/Ramki i albumy do zdjęć/Albumy na zdjęcia</xsl:when>
    <xsl:when test="$ceneo_cat_id = '2176'">Dla dziecka/Zabawki/Zabawki do kąpieli</xsl:when>
    <xsl:when test="$ceneo_cat_id = '2186'">Hobby i zwierzęta/Kolekcjonerstwo/Modelarstwo</xsl:when>
    <xsl:when test="$ceneo_cat_id = '2341'">Biuro i firma/Biuro/Akcesoria i wyposażenie biurowe/Artykuły papiernicze</xsl:when>
    <xsl:when test="$ceneo_cat_id = '2493'">Księgarnia/Książki/Biografie i dzienniki</xsl:when>
    <xsl:when test="$ceneo_cat_id = '2531'">Zdrowie/Leki bez recepty/Dzieci i niemowlęta</xsl:when>
    <xsl:when test="$ceneo_cat_id = '2592'">Księgarnia/Książki/Poradniki/Sport</xsl:when>
    <xsl:when test="$ceneo_cat_id = '2593'">Księgarnia/Książki/Poradniki/Zdrowie i diety</xsl:when>
    <xsl:when test="$ceneo_cat_id = '2701'">Księgarnia/Książki/Poradniki/Pozostałe poradniki</xsl:when>
    <xsl:when test="$ceneo_cat_id = '2704'">Księgarnia/Prasa i kalendarze/Gazety i czasopisma</xsl:when>
    <xsl:when test="$ceneo_cat_id = '2743'">Księgarnia/Książki/Literatura popularnonaukowa</xsl:when>
    <xsl:when test="$ceneo_cat_id = '2744'">Księgarnia/Książki/Podręczniki akademickie/Nauki przyrodnicze i matematyczne</xsl:when>
    <xsl:when test="$ceneo_cat_id = '2745'">Księgarnia/Książki/Podręczniki akademickie/Nauki rolnicze</xsl:when>
    <xsl:when test="$ceneo_cat_id = '2746'">Księgarnia/Książki/Podręczniki akademickie/Pozostałe podręczniki akademickie</xsl:when>
    <xsl:when test="$ceneo_cat_id = '2885'">Dom i wnętrze/Dekoracja domu/Globusy</xsl:when>
    <xsl:when test="$ceneo_cat_id = '2905'">Biuro i firma/Rolnictwo/Hodowla zwierząt</xsl:when>
    <xsl:when test="$ceneo_cat_id = '3451'">Księgarnia/E-booki/Pozostałe E-booki</xsl:when>
    <xsl:when test="$ceneo_cat_id = '3453'">Księgarnia/Audiobooki</xsl:when>
    <xsl:when test="$ceneo_cat_id = '3653'">Prezenty</xsl:when>
    <xsl:when test="$ceneo_cat_id = '3813'">Handmade/Dla dziecka/Zabawki/Zabawki dla niemowląt</xsl:when>
    <xsl:when test="$ceneo_cat_id = '3840'">Handmade/Dom i styl życia/Tekstylia</xsl:when>
    <xsl:when test="$ceneo_cat_id = '3957'">Gry/Gry bez prądu/Gry karciane</xsl:when>
    <xsl:when test="$ceneo_cat_id = '3962'">Dla dziecka/Zabawki/Gry</xsl:when>
    <xsl:when test="$ceneo_cat_id = '398'">Księgarnia/Książki/Informatyka</xsl:when>
    <xsl:when test="$ceneo_cat_id = '399'">Księgarnia/Książki/Literatura podróżnicza i przewodniki</xsl:when>
    <xsl:when test="$ceneo_cat_id = '400'">Księgarnia/Książki/Podręczniki akademickie/Ekonomia i biznes</xsl:when>
    <xsl:when test="$ceneo_cat_id = '401'">Księgarnia/Książki/Podręczniki akademickie/Prawo i administracja</xsl:when>
    <xsl:when test="$ceneo_cat_id = '403'">Księgarnia/Książki/Beletrystyka/Literatura dla dzieci i młodzieży</xsl:when>
    <xsl:when test="$ceneo_cat_id = '405'">Księgarnia/Książki/Encyklopedie i leksykony</xsl:when>
    <xsl:when test="$ceneo_cat_id = '406'">Księgarnia/Książki/Poradniki/Parapsychologia i ezoteryka</xsl:when>
    <xsl:when test="$ceneo_cat_id = '407'">Księgarnia/Książki/Beletrystyka/Fantastyka i fantasy</xsl:when>
    <xsl:when test="$ceneo_cat_id = '408'">Księgarnia/Książki/Podręczniki akademickie/Nauki humanistyczne i społeczne</xsl:when>
    <xsl:when test="$ceneo_cat_id = '409'">Księgarnia/Książki/Historia i literatura faktu</xsl:when>
    <xsl:when test="$ceneo_cat_id = '410'">Księgarnia/Książki/Komiksy</xsl:when>
    <xsl:when test="$ceneo_cat_id = '411'">Księgarnia/Książki/Poradniki/Kulinaria</xsl:when>
    <xsl:when test="$ceneo_cat_id = '412'">Księgarnia/Książki/Podręczniki szkolne</xsl:when>
    <xsl:when test="$ceneo_cat_id = '413'">Księgarnia/Książki/Podręczniki akademickie/Nauki techniczne</xsl:when>
    <xsl:when test="$ceneo_cat_id = '414'">Księgarnia/Książki/Beletrystyka/Literatura sensacyjna i grozy</xsl:when>
    <xsl:when test="$ceneo_cat_id = '417'">Księgarnia/Książki/Poradniki/Hobby, rozrywka</xsl:when>
    <xsl:when test="$ceneo_cat_id = '418'">Księgarnia/Książki/Poezja</xsl:when>
    <xsl:when test="$ceneo_cat_id = '419'">Księgarnia/Książki/Poradniki/Poradniki psychologiczne</xsl:when>
    <xsl:when test="$ceneo_cat_id = '420'">Księgarnia/Książki/Beletrystyka/Romanse</xsl:when>
    <xsl:when test="$ceneo_cat_id = '421'">Księgarnia/Książki/Podręczniki akademickie/Sztuka</xsl:when>
    <xsl:when test="$ceneo_cat_id = '422'">Księgarnia/Książki/Podręczniki akademickie/Nauki medyczne</xsl:when>
    <xsl:when test="$ceneo_cat_id = '424'">Księgarnia/Książki/Poradniki/Rośliny i zwierzęta</xsl:when>
    <xsl:when test="$ceneo_cat_id = '425'">Księgarnia/Książki/Beletrystyka/Powieści i opowiadania</xsl:when>
    <xsl:when test="$ceneo_cat_id = '4256'">Motoryzacja/Samochody</xsl:when>
    <xsl:when test="$ceneo_cat_id = '426'">Księgarnia/Książki/Albumy</xsl:when>
    <xsl:when test="$ceneo_cat_id = '430'">Księgarnia/Książki/Nauka języków obcych/Język angielski</xsl:when>
    <xsl:when test="$ceneo_cat_id = '431'">Księgarnia/Książki/Nauka języków obcych/Pozostałe języki</xsl:when>
    <xsl:when test="$ceneo_cat_id = '432'">Księgarnia/Książki/Nauka języków obcych/Język francuski</xsl:when>
    <xsl:when test="$ceneo_cat_id = '433'">Księgarnia/Książki/Nauka języków obcych/Język hiszpański</xsl:when>
    <xsl:when test="$ceneo_cat_id = '434'">Księgarnia/Książki/Nauka języków obcych/Język niemiecki</xsl:when>
    <xsl:when test="$ceneo_cat_id = '435'">Księgarnia/Książki/Nauka języków obcych/Język rosyjski</xsl:when>
    <xsl:when test="$ceneo_cat_id = '436'">Księgarnia/Książki/Nauka języków obcych/Język włoski</xsl:when>
    <xsl:when test="$ceneo_cat_id = '445'">Księgarnia/Książki/Religia</xsl:when>
    <xsl:when test="$ceneo_cat_id = '447'">Księgarnia/Książki/Podręczniki akademickie/Politologia</xsl:when>
    <xsl:when test="$ceneo_cat_id = '453'">Księgarnia/Książki/Poradniki/Samochody i motocykle</xsl:when>
    <xsl:when test="$ceneo_cat_id = '454'">Księgarnia/Książki/Pozostałe książki</xsl:when>
    <xsl:when test="$ceneo_cat_id = '4624'">Dla dziecka/Pielęgnacja i zdrowie dziecka/Śpiworki</xsl:when>
    <xsl:when test="$ceneo_cat_id = '5065'">Dla dziecka/Artykuły szkolne/Przybory i akcesoria szkolne/Szkolne artykuły papiernicze/Naklejki</xsl:when>
    <xsl:when test="$ceneo_cat_id = '5070'">Dla dziecka/Artykuły szkolne/Przybory i akcesoria szkolne/Szkolne artykuły papiernicze/Podkładki na biurko</xsl:when>
    <xsl:when test="$ceneo_cat_id = '5600'">Sport i rekreacja/Turystyka/Kuchnia turystyczna/Butelki na wodę</xsl:when>
    <xsl:when test="$ceneo_cat_id = '624'">Sport i rekreacja/Turystyka/Plecaki</xsl:when>
    <xsl:when test="$ceneo_cat_id = '724'">Księgarnia/Książki/Literatura obcojęzyczna</xsl:when>
    <xsl:when test="$ceneo_cat_id = '979'">Sport i rekreacja/Turystyka/Kuchnia turystyczna/Termosy</xsl:when>
  </xsl:choose>
</xsl:variable>
