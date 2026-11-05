<?xml version="1.0" encoding="UTF-8"?>
<!--
  Mapowanie: ID kategorii Google Shopping -> ID kategorii Heureka (CZ)
  Plik wygenerowany skryptem app.py. Nie edytować ręcznie.
  Wpisów: 1186 z 5595 kategorii źródłowych.
  Metody dopasowania: fuzzy_high: 496, fuzzy_review: 684, nazwa_przodka: 2, inherited: 172.
  Szczegóły i wpisy do przeglądu: patrz raport CSV obok tego pliku.

  Użycie:
    <xsl:call-template name="google-to-heureka">
      <xsl:with-param name="google_id" select="..."/>
    </xsl:call-template>
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template name="google-to-heureka">
    <xsl:param name="google_id"/>
    <xsl:choose>
      <xsl:when test="$google_id = '37'">1854</xsl:when><!-- Zmenšené modely -> Sběratelské modely -->
      <xsl:when test="$google_id = '49'">3409</xsl:when><!-- Nitě -> Nitě -->
      <xsl:when test="$google_id = '59'">2015</xsl:when><!-- Paličky a metličky -> Příslušenství pro bicí -->
      <xsl:when test="$google_id = '67'">1546</xsl:when><!-- Lesní rohy -> Lesní rohy -->
      <xsl:when test="$google_id = '72'">1537</xsl:when><!-- Tuby -> Tuby -->
      <xsl:when test="$google_id = '78'">2020</xsl:when><!-- Kontrabasy -> Kontrabasy -->
      <xsl:when test="$google_id = '79'">2019</xsl:when><!-- Violoncella -> Violoncella -->
      <xsl:when test="$google_id = '80'">2003</xsl:when><!-- Kytary -> Baskytary -->
      <xsl:when test="$google_id = '85'">1555</xsl:when><!-- Violy -> Violy -->
      <xsl:when test="$google_id = '88'">1543</xsl:when><!-- Klarinety -> Klarinety -->
      <xsl:when test="$google_id = '89'">2919</xsl:when><!-- Flétny -> Panovy flétny -->
      <xsl:when test="$google_id = '90'">1550</xsl:when><!-- Zobcové flétny -> Zobcové flétny -->
      <xsl:when test="$google_id = '91'">1541</xsl:when><!-- Saxofony -> Saxofony -->
      <xsl:when test="$google_id = '100'">997</xsl:when><!-- Batohy -> Batohy -->
      <xsl:when test="$google_id = '104'">2169</xsl:when><!-- Ledvinky -> Ledvinky -->
      <xsl:when test="$google_id = '108'">1098</xsl:when><!-- Toaletní tašky -> Tenisové tašky -->
      <xsl:when test="$google_id = '113'">4979</xsl:when><!-- Hnojiva -> Hnojiva -->
      <xsl:when test="$google_id = '124'">3100</xsl:when><!-- Okna -> Okna -->
      <xsl:when test="$google_id = '146'">822</xsl:when><!-- Adaptéry pro paměťové karty -> Paměťové karty -->
      <xsl:when test="$google_id = '147'">865</xsl:when><!-- Filtry na objektivy -> Filtry k objektivům -->
      <xsl:when test="$google_id = '148'">669</xsl:when><!-- Blesky k fotoaparátům -> Blesky k fotoaparátům -->
      <xsl:when test="$google_id = '152'">665</xsl:when><!-- Digitální fotoaparáty -> Digitální fotoaparáty -->
      <xsl:when test="$google_id = '154'">666</xsl:when><!-- Klasické fotoaparáty -> Klasické fotoaparáty -->
      <xsl:when test="$google_id = '157'">679</xsl:when><!-- Binokuláry -> Okuláry -->
      <xsl:when test="$google_id = '169'">2466</xsl:when><!-- Opasky -> Pásky -->
      <xsl:when test="$google_id = '173'">2464</xsl:when><!-- Klobouky -> Klobouky -->
      <xsl:when test="$google_id = '175'">3070</xsl:when><!-- Přívěsky na klíče -> Přívěsky na klíče -->
      <xsl:when test="$google_id = '176'">1589</xsl:when><!-- Kravaty -> Kravaty -->
      <xsl:when test="$google_id = '178'">2711</xsl:when><!-- Sluneční brýle -> Sluneční brýle -->
      <xsl:when test="$google_id = '180'">6304</xsl:when><!-- Spony do kravat -> Spony na kravatu -->
      <xsl:when test="$google_id = '181'">5035</xsl:when><!-- Paruky -> Paruky -->
      <xsl:when test="$google_id = '191'">1258</xsl:when><!-- Náramky -> Náramky -->
      <xsl:when test="$google_id = '192'">1512</xsl:when><!-- Přívěsky -> Přívěsky -->
      <xsl:when test="$google_id = '193'">2713</xsl:when><!-- Manžetové knoflíčky -> Manžetové knoflíčky -->
      <xsl:when test="$google_id = '194'">1260</xsl:when><!-- Náušnice -> Náušnice -->
      <xsl:when test="$google_id = '196'">1257</xsl:when><!-- Náhrdelníky -> Náhrdelníky -->
      <xsl:when test="$google_id = '200'">1259</xsl:when><!-- Prsteny -> Prsteny -->
      <xsl:when test="$google_id = '201'">976</xsl:when><!-- Hodinky -> Hodinky -->
      <xsl:when test="$google_id = '204'">1578</xsl:when><!-- Kalhoty -> Kalhotky -->
      <xsl:when test="$google_id = '209'">6611</xsl:when><!-- Ponožky -> Ponožkoboty -->
      <xsl:when test="$google_id = '214'">1579</xsl:when><!-- Podprsenky -> Podprsenky -->
      <xsl:when test="$google_id = '225'">707</xsl:when><!-- Radiomagnetofony -> Radiomagnetofony -->
      <xsl:when test="$google_id = '226'">1940</xsl:when><!-- CD přehrávače -> CD přehrávače -->
      <xsl:when test="$google_id = '230'">783</xsl:when><!-- Karaoke systémy -> Operační systémy -->
      <xsl:when test="$google_id = '233'">1940</xsl:when><!-- MP3 přehrávače -> CD přehrávače -->
      <xsl:when test="$google_id = '234'">710</xsl:when><!-- Mikrofony -> Mikrofony -->
      <xsl:when test="$google_id = '235'">6022</xsl:when><!-- Minidiskové přehrávače a rekordéry -> DVD přehrávače a rekordéry -->
      <xsl:when test="$google_id = '236'">2034</xsl:when><!-- Mixážní pulty -> Mixážní pulty -->
      <xsl:when test="$google_id = '241'">804</xsl:when><!-- AV přijímače -> AV přijímače -->
      <xsl:when test="$google_id = '243'">6022</xsl:when><!-- Kazetové přehrávače a rekordéry -> DVD přehrávače a rekordéry -->
      <xsl:when test="$google_id = '245'">1998</xsl:when><!-- Samplery -> Samplery -->
      <xsl:when test="$google_id = '247'">767</xsl:when><!-- Efektové procesory -> Procesory -->
      <xsl:when test="$google_id = '249'">5949</xsl:when><!-- Reproduktory -> Sloupové reproduktory -->
      <xsl:when test="$google_id = '252'">936</xsl:when><!-- Systémy domácího kina -> Domácí kina -->
      <xsl:when test="$google_id = '256'">801</xsl:when><!-- Gramofony -> Gramofony -->
      <xsl:when test="$google_id = '269'">903</xsl:when><!-- Telefonní karty -> Satelitní karty -->
      <xsl:when test="$google_id = '271'">733</xsl:when><!-- Šňůrové telefony -> Bezdrátové telefony -->
      <xsl:when test="$google_id = '272'">733</xsl:when><!-- Bezšňůrové telefony -> Bezdrátové telefony -->
      <xsl:when test="$google_id = '273'">3237</xsl:when><!-- Obousměrné vysílačky -> Baterie pro vysílačky -->
      <xsl:when test="$google_id = '284'">6247</xsl:when><!-- Skenery – příslušenství -> Tampery a příslušenství -->
      <xsl:when test="$google_id = '286'">908</xsl:when><!-- Zvukové karty -> Zvukové karty -->
      <xsl:when test="$google_id = '289'">769</xsl:when><!-- Základní desky -> Základní desky -->
      <xsl:when test="$google_id = '292'">767</xsl:when><!-- Počítačové procesory -> Procesory -->
      <xsl:when test="$google_id = '297'">771</xsl:when><!-- Grafické karty -> Grafické karty -->
      <xsl:when test="$google_id = '300'">4207</xsl:when><!-- Dokovací stanice k notebookům -> Baterie k notebookům -->
      <xsl:when test="$google_id = '302'">752</xsl:when><!-- Grafické tablety -> Grafické tablety -->
      <xsl:when test="$google_id = '303'">763</xsl:when><!-- Počítačové klávesnice -> Klávesnice -->
      <xsl:when test="$google_id = '306'">760</xsl:when><!-- Skenery -> Skenery -->
      <xsl:when test="$google_id = '315'">5015</xsl:when><!-- Kompilátory a vývojářské nástroje -> CAD software -->
      <xsl:when test="$google_id = '317'">907</xsl:when><!-- Výukový software -> Vypalovací software -->
      <xsl:when test="$google_id = '318'">5015</xsl:when><!-- Software pro handheldy a PDA -> CAD software -->
      <xsl:when test="$google_id = '321'">783</xsl:when><!-- Operační systémy -> Operační systémy -->
      <xsl:when test="$google_id = '325'">748</xsl:when><!-- Stolní počítače -> Stolní počítače -->
      <xsl:when test="$google_id = '328'">750</xsl:when><!-- Notebooky -> Notebooky -->
      <xsl:when test="$google_id = '331'">2121</xsl:when><!-- Počítačové servery -> Print servery -->
      <xsl:when test="$google_id = '341'">869</xsl:when><!-- Dálková ovládání -> Dálkové ovladače -->
      <xsl:when test="$google_id = '343'">774</xsl:when><!-- Modemy -> Modemy -->
      <xsl:when test="$google_id = '360'">731</xsl:when><!-- Domovní telefony -> Mobilní telefony -->
      <xsl:when test="$google_id = '377'">3253</xsl:when><!-- Optické jednotky -> Zapékací jednotky -->
      <xsl:when test="$google_id = '385'">3253</xsl:when><!-- Páskové jednotky -> Zapékací jednotky -->
      <xsl:when test="$google_id = '388'">1940</xsl:when><!-- Přehrávače DVD -> CD přehrávače -->
      <xsl:when test="$google_id = '394'">837</xsl:when><!-- Náhradní lampy do projektorů -> Lampy pro projektory -->
      <xsl:when test="$google_id = '395'">698</xsl:when><!-- Projekční plátna -> Projekční plátna -->
      <xsl:when test="$google_id = '397'">699</xsl:when><!-- Multimediální projektory -> Projektory -->
      <xsl:when test="$google_id = '398'">699</xsl:when><!-- Dataprojektory -> Projektory -->
      <xsl:when test="$google_id = '399'">699</xsl:when><!-- Projektory pro prezentace -> Projektory -->
      <xsl:when test="$google_id = '401'">2189</xsl:when><!-- Satelitní přijímače -> Satelitní přijímače -->
      <xsl:when test="$google_id = '404'">2873</xsl:when><!-- Televize -> Televize -->
      <xsl:when test="$google_id = '418'">3809</xsl:when><!-- Mléko -> Mléka -->
      <xsl:when test="$google_id = '424'">6879</xsl:when><!-- Chléb a pečivo -> Čajové pečivo -->
      <xsl:when test="$google_id = '429'">3848</xsl:when><!-- Sýr -> Sýry -->
      <xsl:when test="$google_id = '438'">1723</xsl:when><!-- Sedací vaky a pytle -> Sedací vaky a pytle -->
      <xsl:when test="$google_id = '456'">6978</xsl:when><!-- Lenošky -> Lenošky -->
      <xsl:when test="$google_id = '460'">5099</xsl:when><!-- Pohovky -> Pohovky -->
      <xsl:when test="$google_id = '462'">1715</xsl:when><!-- Noční stolky -> Noční stolky -->
      <xsl:when test="$google_id = '463'">5839</xsl:when><!-- Kartotéky -> Kartotéky -->
      <xsl:when test="$google_id = '465'">1656</xsl:when><!-- Knihovny -> Knihovny -->
      <xsl:when test="$google_id = '488'">3368</xsl:when><!-- Natáčky na vlasy -> Natáčky na vlasy -->
      <xsl:when test="$google_id = '510'">4017</xsl:when><!-- Příruční lékárničky -> Lékárničky -->
      <xsl:when test="$google_id = '523'">2748</xsl:when><!-- Bandáže a ortézy -> Zdravotní bandáže a ortézy -->
      <xsl:when test="$google_id = '527'">4859</xsl:when><!-- Zubní kartáčky -> Mezizubní kartáčky -->
      <xsl:when test="$google_id = '529'">2734</xsl:when><!-- Vody po holení -> Vody po holení -->
      <xsl:when test="$google_id = '550'">3743</xsl:when><!-- Koše na plenky -> Koše na pleny -->
      <xsl:when test="$google_id = '563'">3090</xsl:when><!-- Kojenecká mléka -> Kojenecká mléka -->
      <xsl:when test="$google_id = '564'">2421</xsl:when><!-- Kojenecké lahve -> Kojenecké láhve -->
      <xsl:when test="$google_id = '568'">1310</xsl:when><!-- Dětské kočárky -> Kočárky -->
      <xsl:when test="$google_id = '576'">1608</xsl:when><!-- Osušky a žínky -> Ručníky -->
      <xsl:when test="$google_id = '578'">5256</xsl:when><!-- Kroužky na sprchové závěsy -> Sprchové závěsy -->
      <xsl:when test="$google_id = '580'">5256</xsl:when><!-- Sprchové závěsy -> Sprchové závěsy -->
      <xsl:when test="$google_id = '582'">1606</xsl:when><!-- Mýdelníky -> Mýdlenky -->
      <xsl:when test="$google_id = '584'">3062</xsl:when><!-- Držáky na toaletní papír -> Držáky a zásobníky na toaletní papír -->
      <xsl:when test="$google_id = '587'">5821</xsl:when><!-- Zarážky na knihy -> Zarážky na knihy -->
      <xsl:when test="$google_id = '588'">5330</xsl:when><!-- Svíčky -> Svíčky -->
      <xsl:when test="$google_id = '595'">5329</xsl:when><!-- Zrcadla -> Zrcadla -->
      <xsl:when test="$google_id = '597'">3925</xsl:when><!-- Rámy na obrazy -> Obrazy -->
      <xsl:when test="$google_id = '602'">3958</xsl:when><!-- Vázy -> Vázy -->
      <xsl:when test="$google_id = '605'">1044</xsl:when><!-- Klimatizace -> Klimatizace -->
      <xsl:when test="$google_id = '606'">5953</xsl:when><!-- Čističky vzduchu -> Filtry k čističkám vzduchu -->
      <xsl:when test="$google_id = '610'">1053</xsl:when><!-- Drtiče odpadu -> Drtiče odpadu -->
      <xsl:when test="$google_id = '618'">6247</xsl:when><!-- Vysavače – příslušenství -> Tampery a příslušenství -->
      <xsl:when test="$google_id = '619'">943</xsl:when><!-- Vysavače -> Vysavače -->
      <xsl:when test="$google_id = '621'">1564</xsl:when><!-- Ohřívače vody, bojlery -> Bojlery a ohřívače vody -->
      <xsl:when test="$google_id = '633'">3000</xsl:when><!-- Žehlicí prkna -> Žehlicí prkna -->
      <xsl:when test="$google_id = '634'">1605</xsl:when><!-- Koše na prádlo -> Koše na prádlo -->
      <xsl:when test="$google_id = '637'">1604</xsl:when><!-- Popelnice a odpadkové koše -> Odpadkové koše -->
      <xsl:when test="$google_id = '639'">3059</xsl:when><!-- Zástěry -> Zástěry -->
      <xsl:when test="$google_id = '650'">5009</xsl:when><!-- Karafy -> Karafy -->
      <xsl:when test="$google_id = '655'">4875</xsl:when><!-- Zapékací mísy -> Pekáče a zapékací mísy -->
      <xsl:when test="$google_id = '656'">2195</xsl:when><!-- Napařovací hrnce -> Zavařovací hrnce -->
      <xsl:when test="$google_id = '659'">1724</xsl:when><!-- Konvice na kamna -> Krbová kamna -->
      <xsl:when test="$google_id = '660'">2195</xsl:when><!-- Tlakové a zavařovací hrnce -> Zavařovací hrnce -->
      <xsl:when test="$google_id = '661'">1201</xsl:when><!-- Pánve -> Pánve -->
      <xsl:when test="$google_id = '663'">1206</xsl:when><!-- Polévkové hrnce -> Tlakové hrnce -->
      <xsl:when test="$google_id = '665'">1202</xsl:when><!-- Kuchyňské nože -> Kuchyňské nože -->
      <xsl:when test="$google_id = '667'">4876</xsl:when><!-- Boxy na potraviny -> Dózy na potraviny -->
      <xsl:when test="$google_id = '671'">4028</xsl:when><!-- Piknikové koše -> Piknikové koše -->
      <xsl:when test="$google_id = '679'">1958</xsl:when><!-- Vařiče -> Vařiče -->
      <xsl:when test="$google_id = '680'">966</xsl:when><!-- Myčky nádobí -> Myčky nádobí -->
      <xsl:when test="$google_id = '681'">959</xsl:when><!-- Mrazničky -> Mrazáky -->
      <xsl:when test="$google_id = '683'">6356</xsl:when><!-- Trouby -> Mini trouby -->
      <xsl:when test="$google_id = '684'">963</xsl:when><!-- Digestoře -> Digestoře -->
      <xsl:when test="$google_id = '685'">960</xsl:when><!-- Sporáky -> Sporáky -->
      <xsl:when test="$google_id = '687'">2826</xsl:when><!-- Udírny -> Udírny -->
      <xsl:when test="$google_id = '690'">1969</xsl:when><!-- Kompost -> Kompostéry -->
      <xsl:when test="$google_id = '695'">5366</xsl:when><!-- Koše a nosiče na dřevo -> Koše na dřevo -->
      <xsl:when test="$google_id = '706'">3766</xsl:when><!-- Poštovní schránky -> Poštovní schránky -->
      <xsl:when test="$google_id = '709'">6320</xsl:when><!-- Okapové řetězy -> Pilové řetězy -->
      <xsl:when test="$google_id = '717'">1454</xsl:when><!-- Hamaky a houpací sítě -> Houpací sítě -->
      <xsl:when test="$google_id = '718'">1653</xsl:when><!-- Houpací křesla -> Houpací křesla -->
      <xsl:when test="$google_id = '732'">955</xsl:when><!-- Domácí pekárny -> Domácí pekárny -->
      <xsl:when test="$google_id = '733'">3279</xsl:when><!-- Otvíráky na konzervy -> Otvíráky na konzervy -->
      <xsl:when test="$google_id = '734'">1595</xsl:when><!-- Mlýnky na kávu -> Mlýnky na kávu -->
      <xsl:when test="$google_id = '737'">2495</xsl:when><!-- Pomalé hrnce -> Parní hrnce -->
      <xsl:when test="$google_id = '738'">949</xsl:when><!-- Fritézy -> Fritézy -->
      <xsl:when test="$google_id = '743'">1006</xsl:when><!-- Sušičky potravin -> Sušičky potravin -->
      <xsl:when test="$google_id = '748'">1699</xsl:when><!-- Zmrzlinovače -> Zmrzlinovače -->
      <xsl:when test="$google_id = '749'">5027</xsl:when><!-- Drtiče ledu -> Drtiče ledu -->
      <xsl:when test="$google_id = '750'">954</xsl:when><!-- Odšťavňovače -> Odšťavňovače -->
      <xsl:when test="$google_id = '751'">947</xsl:when><!-- Rychlovarné konvice -> Rychlovarné konvice -->
      <xsl:when test="$google_id = '753'">942</xsl:when><!-- Mikrovlnné trouby -> Mikrovlnné trouby -->
      <xsl:when test="$google_id = '759'">950</xsl:when><!-- Sendvičovače -> Sendvičovače -->
      <xsl:when test="$google_id = '760'">2495</xsl:when><!-- Parní hrnce -> Parní hrnce -->
      <xsl:when test="$google_id = '761'">6356</xsl:when><!-- Opékací trouby -> Mini trouby -->
      <xsl:when test="$google_id = '762'">951</xsl:when><!-- Topinkovače -> Topinkovače -->
      <xsl:when test="$google_id = '764'">2435</xsl:when><!-- Vaflovače -> Vaflovače -->
      <xsl:when test="$google_id = '765'">948</xsl:when><!-- Vodní filtry -> Vodní filtry -->
      <xsl:when test="$google_id = '766'">6467</xsl:when><!-- Jogurtovače -> Jogurtovače -->
      <xsl:when test="$google_id = '774'">2062</xsl:when><!-- Erotické prádlo -> Pánské erotické prádlo -->
      <xsl:when test="$google_id = '943'">5024</xsl:when><!-- Ořezávátka -> Ořezávátka -->
      <xsl:when test="$google_id = '947'">1886</xsl:when><!-- Sešívačky -> Sešívačky -->
      <xsl:when test="$google_id = '953'">1792</xsl:when><!-- Skartovačky -> Skartovače -->
      <xsl:when test="$google_id = '955'">928</xsl:when><!-- Psací stroje -> Psací stroje -->
      <xsl:when test="$google_id = '957'">1868</xsl:when><!-- Vizitky -> Vizitkáře -->
      <xsl:when test="$google_id = '958'">4681</xsl:when><!-- Obálky -> Obálky -->
      <xsl:when test="$google_id = '961'">5023</xsl:when><!-- Záznamníky a poznámkové bloky -> Poznámkové bloky -->
      <xsl:when test="$google_id = '971'">2938</xsl:when><!-- Bílé tabule -> Tabule -->
      <xsl:when test="$google_id = '975'">3192</xsl:when><!-- Balicí páska -> Barvící pásky -->
      <xsl:when test="$google_id = '984'">3928</xsl:when><!-- Květiny -> Květiny -->
      <xsl:when test="$google_id = '992'">2357</xsl:when><!-- Eliptické trenažery -> Eliptické trenažéry -->
      <xsl:when test="$google_id = '994'">1325</xsl:when><!-- Rotopedy -> Rotopedy -->
      <xsl:when test="$google_id = '995'">1324</xsl:when><!-- Veslařské trenažéry -> Veslovací trenažéry -->
      <xsl:when test="$google_id = '997'">2357</xsl:when><!-- Běžecké trenažéry -> Eliptické trenažéry -->
      <xsl:when test="$google_id = '1015'">942</xsl:when><!-- Kempinkové trouby -> Mikrovlnné trouby -->
      <xsl:when test="$google_id = '1022'">987</xsl:when><!-- Stany -> Stany -->
      <xsl:when test="$google_id = '1026'">1000</xsl:when><!-- Jízdní kola -> Jízdní kola -->
      <xsl:when test="$google_id = '1030'">3870</xsl:when><!-- Jednokolky -> Jednokolky -->
      <xsl:when test="$google_id = '1045'">1137</xsl:when><!-- Golfové míčky -> Golfové míčky -->
      <xsl:when test="$google_id = '1058'">1147</xsl:when><!-- Inline brusle -> Kolečkové brusle -->
      <xsl:when test="$google_id = '1077'">1322</xsl:when><!-- Odpalovací stroje -> Posilovací stroje -->
      <xsl:when test="$google_id = '1082'">1075</xsl:when><!-- Basketbalové koše -> Basketbalové koše -->
      <xsl:when test="$google_id = '1083'">1076</xsl:when><!-- Basketbalové míče -> Basketbalové míče -->
      <xsl:when test="$google_id = '1094'">3899</xsl:when><!-- Míče na americký fotbal -> Míče na americký fotbal -->
      <xsl:when test="$google_id = '1098'">3899</xsl:when><!-- Přilby na americký fotbal -> Míče na americký fotbal -->
      <xsl:when test="$google_id = '1112'">1126</xsl:when><!-- Fotbalové míče -> Fotbalové míče -->
      <xsl:when test="$google_id = '1114'">1368</xsl:when><!-- Fotbalové holenní chrániče -> Fotbalové chrániče -->
      <xsl:when test="$google_id = '1116'">1101</xsl:when><!-- Volejbalové míče -> Volejbalové míče -->
      <xsl:when test="$google_id = '1117'">1102</xsl:when><!-- Volejbalové sítě -> Volejbalové sítě -->
      <xsl:when test="$google_id = '1128'">1426</xsl:when><!-- Záchranné vesty -> Záchranné vesty -->
      <xsl:when test="$google_id = '1129'">1428</xsl:when><!-- Pádla a vesla -> Pádla a vesla -->
      <xsl:when test="$google_id = '1138'">1437</xsl:when><!-- Suché obleky -> Suché obleky -->
      <xsl:when test="$google_id = '1140'">1431</xsl:when><!-- Potápěčské a šnorchlovací masky -> Potápěčské masky -->
      <xsl:when test="$google_id = '1142'">1432</xsl:when><!-- Šnorchly -> Šnorchly -->
      <xsl:when test="$google_id = '1158'">989</xsl:when><!-- Sjezdové lyže -> Sjezdové lyže -->
      <xsl:when test="$google_id = '1162'">1121</xsl:when><!-- Vázání na snowboard -> Vázání na snowboard -->
      <xsl:when test="$google_id = '1163'">1119</xsl:when><!-- Boty na snowboard -> Boty na snowboard -->
      <xsl:when test="$google_id = '1164'">1120</xsl:when><!-- Snowboardy -> Snowboardy -->
      <xsl:when test="$google_id = '1171'">1171</xsl:when><!-- Sekery -> Sekery -->
      <xsl:when test="$google_id = '1179'">3647</xsl:when><!-- Páčidla -> Páčidla -->
      <xsl:when test="$google_id = '1187'">1026</xsl:when><!-- Hoblíky -> Hoblíky -->
      <xsl:when test="$google_id = '1195'">3392</xsl:when><!-- Nástrčné šroubováky -> Klasické šroubováky -->
      <xsl:when test="$google_id = '1198'">3068</xsl:when><!-- Úhloměry -> Měřicí úhloměry -->
      <xsl:when test="$google_id = '1203'">3392</xsl:when><!-- Šroubováky -> Klasické šroubováky -->
      <xsl:when test="$google_id = '1205'">3606</xsl:when><!-- Úhelníky -> Úhelníky -->
      <xsl:when test="$google_id = '1216'">1181</xsl:when><!-- Stojanové vrtačky -> Vrtačky -->
      <xsl:when test="$google_id = '1219'">1025</xsl:when><!-- Brusky -> Brusky -->
      <xsl:when test="$google_id = '1220'">1027</xsl:when><!-- Horkovzdušné pistole -> Horkovzdušné pistole -->
      <xsl:when test="$google_id = '1221'">5103</xsl:when><!-- Rázové utahováky -> Rázové utahováky -->
      <xsl:when test="$google_id = '1223'">3934</xsl:when><!-- Vyžínače -> Vypínače -->
      <xsl:when test="$google_id = '1236'">4141</xsl:when><!-- Pájky -> Páječky -->
      <xsl:when test="$google_id = '1238'">6003</xsl:when><!-- Svařovací pistole -> Vytlačovací pistole -->
      <xsl:when test="$google_id = '1257'">1480</xsl:when><!-- Panenky -> Panenky -->
      <xsl:when test="$google_id = '1258'">1736</xsl:when><!-- Loutky -> Loutky -->
      <xsl:when test="$google_id = '1259'">1845</xsl:when><!-- Plyšové hračky -> Plechové hračky -->
      <xsl:when test="$google_id = '1279'">5015</xsl:when><!-- Software pro videohry -> CAD software -->
      <xsl:when test="$google_id = '1294'">835</xsl:when><!-- Herní konzole -> Herní konzole -->
      <xsl:when test="$google_id = '1301'">5828</xsl:when><!-- Disketové jednotky -> Centrální jednotky -->
      <xsl:when test="$google_id = '1302'">2433</xsl:when><!-- Ovládání postřikovačů -> Příslušenství k postýlkám -->
      <xsl:when test="$google_id = '1348'">1906</xsl:when><!-- UPS -> UPS -->
      <xsl:when test="$google_id = '1360'">1803</xsl:when><!-- Zubní pasty -> Zubní pasty -->
      <xsl:when test="$google_id = '1367'">1181</xsl:when><!-- Nebozezy -> Vrtačky -->
      <xsl:when test="$google_id = '1371'">5282</xsl:when><!-- Pozvánky -> Párty pozvánky -->
      <xsl:when test="$google_id = '1387'">4354</xsl:when><!-- Hořčice -> Hořčice -->
      <xsl:when test="$google_id = '1388'">6708</xsl:when><!-- Překapávací kávovary -> Pákové kávovary -->
      <xsl:when test="$google_id = '1395'">1714</xsl:when><!-- Konferenční stolky -> Konferenční stolky -->
      <xsl:when test="$google_id = '1434'">2374</xsl:when><!-- Hasicí přístroje -> Hasicí přístroje -->
      <xsl:when test="$google_id = '1436'">2890</xsl:when><!-- Nouzové osvětlení -> LED osvětlení -->
      <xsl:when test="$google_id = '1450'">3566</xsl:when><!-- Spárovačky -> Spárovačky -->
      <xsl:when test="$google_id = '1463'">1655</xsl:when><!-- Barové židle -> Barové židle -->
      <xsl:when test="$google_id = '1465'">1181</xsl:when><!-- Dlabačky -> Vrtačky -->
      <xsl:when test="$google_id = '1480'">2772</xsl:when><!-- Síťové kabely -> Síťové kabely -->
      <xsl:when test="$google_id = '1487'">903</xsl:when><!-- Televizní karty -> Satelitní karty -->
      <xsl:when test="$google_id = '1530'">6462</xsl:when><!-- Krbové nářadí -> Krbové nářadí -->
      <xsl:when test="$google_id = '1534'">4327</xsl:when><!-- Popcorn -> Popcorn -->
      <xsl:when test="$google_id = '1540'">8583</xsl:when><!-- Vrtáky -> Vrtáky -->
      <xsl:when test="$google_id = '1541'">1166</xsl:when><!-- Sněhové frézy -> Sněhové frézy -->
      <xsl:when test="$google_id = '1546'">6540</xsl:when><!-- Reflektory -> Reflektory -->
      <xsl:when test="$google_id = '1548'">2132</xsl:when><!-- Expozimetry -> Expozimetry -->
      <xsl:when test="$google_id = '1549'">6899</xsl:when><!-- Odkládací stolky -> Odkládací stolky -->
      <xsl:when test="$google_id = '1562'">2123</xsl:when><!-- Přepínače KVM -> KVM přepínače -->
      <xsl:when test="$google_id = '1564'">4207</xsl:when><!-- Baterie do notebooků -> Baterie k notebookům -->
      <xsl:when test="$google_id = '1568'">4306</xsl:when><!-- Majonéza -> Majonézy -->
      <xsl:when test="$google_id = '1578'">4139</xsl:when><!-- Tvarovací prádlo -> Pánské stahovací prádlo -->
      <xsl:when test="$google_id = '1584'">4980</xsl:when><!-- Závitovací stroje -> Zametací stroje -->
      <xsl:when test="$google_id = '1602'">1713</xsl:when><!-- Úzké stolky -> TV stolky -->
      <xsl:when test="$google_id = '1625'">1893</xsl:when><!-- Laminátory -> Laminátory -->
      <xsl:when test="$google_id = '1632'">2324</xsl:when><!-- Klíče -> Klíče -->
      <xsl:when test="$google_id = '1647'">5204</xsl:when><!-- Moka konvice -> Moka konvice -->
      <xsl:when test="$google_id = '1662'">3159</xsl:when><!-- Čelenky -> Čelenky -->
      <xsl:when test="$google_id = '1663'">4258</xsl:when><!-- Soustruhy -> Soustruhy -->
      <xsl:when test="$google_id = '1665'">768</xsl:when><!-- Mezipaměť -> Paměti -->
      <xsl:when test="$google_id = '1671'">5863</xsl:when><!-- Gin -> Giny -->
      <xsl:when test="$google_id = '1709'">1564</xsl:when><!-- Odvod spalin z ohřívače vody -> Bojlery a ohřívače vody -->
      <xsl:when test="$google_id = '1718'">1923</xsl:when><!-- Antény -> WiFi antény -->
      <xsl:when test="$google_id = '1733'">768</xsl:when><!-- RAM -> Paměti -->
      <xsl:when test="$google_id = '1744'">1564</xsl:when><!-- Díly pro ohřívače vody -> Bojlery a ohřívače vody -->
      <xsl:when test="$google_id = '1745'">739</xsl:when><!-- Baterie do mobilních telefonů -> Baterie pro mobilní telefony -->
      <xsl:when test="$google_id = '1763'">2771</xsl:when><!-- Systémové a napájecí kabely -> Napájecí kabely -->
      <xsl:when test="$google_id = '1767'">768</xsl:when><!-- Grafická paměť -> Paměti -->
      <xsl:when test="$google_id = '1786'">6331</xsl:when><!-- Kukly -> Kukly -->
      <xsl:when test="$google_id = '1802'">1266</xsl:when><!-- Autoalarmy -> Autoalarmy -->
      <xsl:when test="$google_id = '1803'">1888</xsl:when><!-- Váhy na papír -> Řezačky na papír -->
      <xsl:when test="$google_id = '1817'">2362</xsl:when><!-- Výčepní zařízení -> Výčepní zařízení -->
      <xsl:when test="$google_id = '1835'">1564</xsl:when><!-- Ochranné desky pod ohřívače vody -> Bojlery a ohřívače vody -->
      <xsl:when test="$google_id = '1841'">1332</xsl:when><!-- Frézky -> Frézky -->
      <xsl:when test="$google_id = '1855'">6359</xsl:when><!-- Tvaroh -> Tvarohy -->
      <xsl:when test="$google_id = '1866'">2392</xsl:when><!-- Lešení -> Lešení -->
      <xsl:when test="$google_id = '1868'">6794</xsl:when><!-- Káva -> Mletá káva -->
      <xsl:when test="$google_id = '1880'">3238</xsl:when><!-- Baterie do bezdrátových telefonů -> Baterie pro bezdrátové telefony -->
      <xsl:when test="$google_id = '1897'">3936</xsl:when><!-- Termostaty -> Termostaty -->
      <xsl:when test="$google_id = '1924'">731</xsl:when><!-- Satelitní telefony -> Mobilní telefony -->
      <xsl:when test="$google_id = '1926'">5867</xsl:when><!-- Whisky -> Whisky -->
      <xsl:when test="$google_id = '1927'">3257</xsl:when><!-- Nášivky -> Nášivky -->
      <xsl:when test="$google_id = '1948'">3369</xsl:when><!-- Spony a jehlice do vlasů -> Spony do vlasů -->
      <xsl:when test="$google_id = '1954'">3854</xsl:when><!-- Jogurt -> Jogurty -->
      <xsl:when test="$google_id = '1958'">8621</xsl:when><!-- Kleště -> Kleště -->
      <xsl:when test="$google_id = '1985'">4854</xsl:when><!-- Deky -> Deky -->
      <xsl:when test="$google_id = '1993'">8577</xsl:when><!-- Podložky pod myš -> Podložky pod myš -->
      <xsl:when test="$google_id = '1994'">1181</xsl:when><!-- Pneumatické vrtačky -> Vrtačky -->
      <xsl:when test="$google_id = '2015'">2889</xsl:when><!-- Kompresory -> Kompresory -->
      <xsl:when test="$google_id = '2045'">2395</xsl:when><!-- Kancelářské židle -> Kancelářské židle -->
      <xsl:when test="$google_id = '2053'">8288</xsl:when><!-- Čističe potrubí -> Izolace potrubí -->
      <xsl:when test="$google_id = '2058'">3538</xsl:when><!-- Základní barvy -> Fasádní barvy -->
      <xsl:when test="$google_id = '2060'">2070</xsl:when><!-- Topná tělesa -> Topná tělesa -->
      <xsl:when test="$google_id = '2065'">5015</xsl:when><!-- Fotografie pro fotobanky a videa pro videobanky -> CAD software -->
      <xsl:when test="$google_id = '2080'">6974</xsl:when><!-- Řezačky trubek -> Řezačky trubek -->
      <xsl:when test="$google_id = '2081'">2145</xsl:when><!-- Koupelnové stolky -> Toaletní stolky -->
      <xsl:when test="$google_id = '2107'">5870</xsl:when><!-- Vodka -> Vodky -->
      <xsl:when test="$google_id = '2126'">4345</xsl:when><!-- Kuchyňské oleje -> Kuchyňské oleje -->
      <xsl:when test="$google_id = '2130'">768</xsl:when><!-- ROM -> Paměti -->
      <xsl:when test="$google_id = '2160'">1584</xsl:when><!-- Podvazkové pásy -> Korzety a podvazkové pásy -->
      <xsl:when test="$google_id = '2161'">3937</xsl:when><!-- Pohybová čidla -> Pohybová čidla -->
      <xsl:when test="$google_id = '2181'">3567</xsl:when><!-- Zednické lžíce -> Zednické lžíce -->
      <xsl:when test="$google_id = '2188'">4329</xsl:when><!-- Džemy a marmelády -> Džemy a marmelády -->
      <xsl:when test="$google_id = '2198'">3754</xsl:when><!-- Pracovní nože -> Pracovní nože -->
      <xsl:when test="$google_id = '2208'">2702</xsl:when><!-- Ruční kladiva -> Ruční kladiva -->
      <xsl:when test="$google_id = '2220'">5873</xsl:when><!-- Tequila -> Tequily -->
      <xsl:when test="$google_id = '2229'">4323</xsl:when><!-- Sušenky -> Sušenky -->
      <xsl:when test="$google_id = '2242'">6533</xsl:when><!-- Kreslicí stoly -> Kreslicí a rýsovací stoly -->
      <xsl:when test="$google_id = '2246'">5820</xsl:when><!-- Glukometry -> Glukometry -->
      <xsl:when test="$google_id = '2249'">1663</xsl:when><!-- Lustry -> Svítidla -->
      <xsl:when test="$google_id = '2250'">3688</xsl:when><!-- Prachovky -> Prachovky -->
      <xsl:when test="$google_id = '2271'">3156</xsl:when><!-- Šaty -> Šátky -->
      <xsl:when test="$google_id = '2302'">1583</xsl:when><!-- Župany -> Dámské župany -->
      <xsl:when test="$google_id = '2305'">3115</xsl:when><!-- Míchačky -> Míchačky -->
      <xsl:when test="$google_id = '2313'">1187</xsl:when><!-- Zahradní hadice -> Zahradní hadice -->
      <xsl:when test="$google_id = '2314'">1611</xsl:when><!-- Prostěradla -> Prostěradla -->
      <xsl:when test="$google_id = '2334'">2941</xsl:when><!-- Tapety -> Tapety -->
      <xsl:when test="$google_id = '2337'">3564</xsl:when><!-- Hladítka -> Hladítka -->
      <xsl:when test="$google_id = '2364'">5874</xsl:when><!-- Brandy -> Brandy -->
      <xsl:when test="$google_id = '2365'">2147</xsl:when><!-- Krbové zástěny -> Sprchové zástěny -->
      <xsl:when test="$google_id = '2374'">6140</xsl:when><!-- Pytle na odpadky -> Pytle na odpadky -->
      <xsl:when test="$google_id = '2376'">2323</xsl:when><!-- Bidety -> Bity -->
      <xsl:when test="$google_id = '2380'">6256</xsl:when><!-- Průmyslové sponky -> Průmyslové spony -->
      <xsl:when test="$google_id = '2387'">3076</xsl:when><!-- Dámské hygienické vložky -> Hygienické vložky -->
      <xsl:when test="$google_id = '2408'">3244</xsl:when><!-- Hřebíky -> Hřebíky -->
      <xsl:when test="$google_id = '2455'">2123</xsl:when><!-- Rozbočovače a přepínače -> KVM přepínače -->
      <xsl:when test="$google_id = '2494'">5553</xsl:when><!-- Pevné střechy vozidel -> Plachty na auto -->
      <xsl:when test="$google_id = '2499'">1731</xsl:when><!-- Domečky pro panenky -> Domečky pro panenky -->
      <xsl:when test="$google_id = '2507'">3936</xsl:when><!-- Termotašky -> Termostaty -->
      <xsl:when test="$google_id = '2513'">6191</xsl:when><!-- Kapaliny do posilovačů řízení -> Kapaliny do posilovačů řízení -->
      <xsl:when test="$google_id = '2515'">8346</xsl:when><!-- Tamburíny -> Tamburíny -->
      <xsl:when test="$google_id = '2518'">1532</xsl:when><!-- Bicí soupravy -> Akustické bicí soupravy -->
      <xsl:when test="$google_id = '2524'">1663</xsl:when><!-- Stropní svítidla -> Svítidla -->
      <xsl:when test="$google_id = '2535'">6445</xsl:when><!-- Stolní a sloupové ventilátory -> Stropní ventilátory -->
      <xsl:when test="$google_id = '2547'">1198</xsl:when><!-- Prostírání -> Prostírání -->
      <xsl:when test="$google_id = '2549'">962</xsl:when><!-- Pračky -> Pračky -->
      <xsl:when test="$google_id = '2562'">3153</xsl:when><!-- Spodní prádlo -> Dětské spodní prádlo -->
      <xsl:when test="$google_id = '2564'">1627</xsl:when><!-- Tampóny -> Šampony -->
      <xsl:when test="$google_id = '2572'">4351</xsl:when><!-- Směsi na pečení -> Přísady na pečení -->
      <xsl:when test="$google_id = '2580'">1582</xsl:when><!-- Pyžama -> Dámská pyžama -->
      <xsl:when test="$google_id = '2587'">5274</xsl:when><!-- Balónky -> Balónky -->
      <xsl:when test="$google_id = '2589'">5885</xsl:when><!-- Konturovací tužky na rty -> Tužky na rty -->
      <xsl:when test="$google_id = '2590'">5796</xsl:when><!-- Přípravky na mytí auta -> Přípravky na mytí aut -->
      <xsl:when test="$google_id = '2596'">5114</xsl:when><!-- Špunty do uší -> Špunty do uší -->
      <xsl:when test="$google_id = '2605'">5840</xsl:when><!-- Rum -> Rumy -->
      <xsl:when test="$google_id = '2610'">3040</xsl:when><!-- Stěrky -> Utěrky -->
      <xsl:when test="$google_id = '2614'">4886</xsl:when><!-- Švihadla -> Švihadla -->
      <xsl:when test="$google_id = '2620'">1804</xsl:when><!-- Zubní nitě -> Zubní nitě -->
      <xsl:when test="$google_id = '2621'">4790</xsl:when><!-- Záclonky -> Záclony -->
      <xsl:when test="$google_id = '2627'">677</xsl:when><!-- Sluneční clony -> Sluneční clony -->
      <xsl:when test="$google_id = '2629'">1181</xsl:when><!-- Ruční vrtačky -> Vrtačky -->
      <xsl:when test="$google_id = '2639'">5366</xsl:when><!-- Kamna na dřevo -> Koše na dřevo -->
      <xsl:when test="$google_id = '2650'">7053</xsl:when><!-- Vývojnice -> Vývojnice -->
      <xsl:when test="$google_id = '2658'">5098</xsl:when><!-- Kroužkový papír -> Krepové papíry -->
      <xsl:when test="$google_id = '2668'">4893</xsl:when><!-- Peněženky a sponky na peníze -> Spony na peníze -->
      <xsl:when test="$google_id = '2669'">3407</xsl:when><!-- Příze -> Příze -->
      <xsl:when test="$google_id = '2675'">5037</xsl:when><!-- Rohožky -> Rohožky -->
      <xsl:when test="$google_id = '2677'">1707</xsl:when><!-- Sušáky na prádlo -> Sušáky na prádlo -->
      <xsl:when test="$google_id = '2683'">4489</xsl:when><!-- Laky na nehty -> Laky na nehty -->
      <xsl:when test="$google_id = '2684'">1717</xsl:when><!-- Zahradní stoly -> Zahradní stoly -->
      <xsl:when test="$google_id = '2686'">6922</xsl:when><!-- Tužky na obočí -> Tužky na obočí -->
      <xsl:when test="$google_id = '2690'">2050</xsl:when><!-- Zářivky -> Žárovky -->
      <xsl:when test="$google_id = '2696'">1718</xsl:when><!-- Matrace -> Matrace -->
      <xsl:when test="$google_id = '2700'">1612</xsl:when><!-- Polštáře -> Polštáře -->
      <xsl:when test="$google_id = '2712'">1199</xsl:when><!-- Skleničky -> Sklenice -->
      <xsl:when test="$google_id = '2735'">5851</xsl:when><!-- Převodový olej -> Převodové oleje -->
      <xsl:when test="$google_id = '2742'">1710</xsl:when><!-- Papírové ručníky -> Papírové ručníky -->
      <xsl:when test="$google_id = '2743'">1484</xsl:when><!-- Pískoviště -> Pískoviště -->
      <xsl:when test="$google_id = '2753'">2431</xsl:when><!-- Elektrická vozítka -> Dětská elektrická vozítka -->
      <xsl:when test="$google_id = '2754'">3664</xsl:when><!-- Prací prášky -> Prací prášky -->
      <xsl:when test="$google_id = '2761'">5620</xsl:when><!-- Umělé řasy -> Umělé řasy -->
      <xsl:when test="$google_id = '2765'">6404</xsl:when><!-- Podkladové make-upy a korektory -> Make-upy -->
      <xsl:when test="$google_id = '2775'">3838</xsl:when><!-- Mouka -> Mouky -->
      <xsl:when test="$google_id = '2780'">3368</xsl:when><!-- Natáčky na řasy -> Natáčky na vlasy -->
      <xsl:when test="$google_id = '2781'">3080</xsl:when><!-- Konfety -> Kornety -->
      <xsl:when test="$google_id = '2784'">3364</xsl:when><!-- Svícny -> Svícny -->
      <xsl:when test="$google_id = '2795'">6220</xsl:when><!-- Klepadla -> Klepadla -->
      <xsl:when test="$google_id = '2807'">5959</xsl:when><!-- Oční linky -> Oční linky -->
      <xsl:when test="$google_id = '2809'">1663</xsl:when><!-- Nábytkové osvětlení -> Svítidla -->
      <xsl:when test="$google_id = '2810'">1506</xsl:when><!-- Bazény -> Bazény -->
      <xsl:when test="$google_id = '2814'">1634</xsl:when><!-- Barvení vlasů -> Barvy na vlasy -->
      <xsl:when test="$google_id = '2828'">5906</xsl:when><!-- Kleště na nehty -> Kleštičky na nehty -->
      <xsl:when test="$google_id = '2834'">5956</xsl:when><!-- Řasenky -> Řasenky -->
      <xsl:when test="$google_id = '2835'">3756</xsl:when><!-- Svorky a svěráky -> Svěráky a svorky -->
      <xsl:when test="$google_id = '2837'">1147</xsl:when><!-- Trekové brusle -> Kolečkové brusle -->
      <xsl:when test="$google_id = '2844'">1632</xsl:when><!-- Ochrana proti slunci -> Ochrana vlasů proti slunci -->
      <xsl:when test="$google_id = '2858'">5884</xsl:when><!-- Lesky na rty -> Lesky na rty -->
      <xsl:when test="$google_id = '2860'">5913</xsl:when><!-- Bazénová lehátka -> Dílenská lehátka -->
      <xsl:when test="$google_id = '2867'">1482</xsl:when><!-- Skluzavky -> Skluzavky -->
      <xsl:when test="$google_id = '2875'">5910</xsl:when><!-- Mycí houby a žínky -> Mycí houby a žínky -->
      <xsl:when test="$google_id = '2876'">3749</xsl:when><!-- Koupelové kartáče -> Úklidové kartáče -->
      <xsl:when test="$google_id = '2887'">3806</xsl:when><!-- Džus -> Džusy -->
      <xsl:when test="$google_id = '2904'">1647</xsl:when><!-- Oční stíny -> Oční stíny -->
      <xsl:when test="$google_id = '2919'">5308</xsl:when><!-- Elektrická masážní křesla -> Masážní křesla -->
      <xsl:when test="$google_id = '2923'">1793</xsl:when><!-- Kontaktní čočky -> Kontaktní čočky -->
      <xsl:when test="$google_id = '2933'">5872</xsl:when><!-- Likéry -> Likéry -->
      <xsl:when test="$google_id = '2934'">5096</xsl:when><!-- Vatové tyčinky -> Vatové tyčinky -->
      <xsl:when test="$google_id = '2943'">6190</xsl:when><!-- Kapaliny do ostřikovačů -> Vody do ostřikovačů -->
      <xsl:when test="$google_id = '2944'">2050</xsl:when><!-- Žárovky -> Žárovky -->
      <xsl:when test="$google_id = '2951'">1199</xsl:when><!-- Sklenice -> Sklenice -->
      <xsl:when test="$google_id = '2966'">5223</xsl:when><!-- Plovací desky -> Plavecké desky -->
      <xsl:when test="$google_id = '2972'">2897</xsl:when><!-- Domovní zvonky -> Domovní zvonky -->
      <xsl:when test="$google_id = '2980'">6404</xsl:when><!-- Pudry -> Make-upy -->
      <xsl:when test="$google_id = '2985'">2184</xsl:when><!-- Zahradní grily -> Zahradní grily -->
      <xsl:when test="$google_id = '2991'">3162</xsl:when><!-- Krycí matrace -> Chrániče na matrace -->
      <xsl:when test="$google_id = '3019'">1808</xsl:when><!-- Přípravky na bělení zubů -> Přípravky na bělení zubů -->
      <xsl:when test="$google_id = '3021'">1648</xsl:when><!-- Rtěnky -> Rtěnky -->
      <xsl:when test="$google_id = '3032'">1468</xsl:when><!-- Kabelky -> Kabelky -->
      <xsl:when test="$google_id = '3043'">1530</xsl:when><!-- Činely -> Činely -->
      <xsl:when test="$google_id = '3044'">5850</xsl:when><!-- Motorové oleje -> Motorové oleje -->
      <xsl:when test="$google_id = '3051'">2922</xsl:when><!-- Brzdové kapaliny -> Brzdové kapaliny -->
      <xsl:when test="$google_id = '3055'">715</xsl:when><!-- Pouzdra na MP3 přehrávače -> MP3 a MP4 přehrávače -->
      <xsl:when test="$google_id = '3063'">3893</xsl:when><!-- Hledí přileb na americký fotbal -> Helmy na americký fotbal -->
      <xsl:when test="$google_id = '3064'">2686</xsl:when><!-- Sněžnice -> Sněžnice -->
      <xsl:when test="$google_id = '3070'">4908</xsl:when><!-- Jednokolky – příslušenství -> Kulečníkové příslušenství -->
      <xsl:when test="$google_id = '3071'">1173</xsl:when><!-- Rycí vidle -> Vidle -->
      <xsl:when test="$google_id = '3082'">2326</xsl:when><!-- Kotle -> Kotle -->
      <xsl:when test="$google_id = '3084'">5133</xsl:when><!-- Jezdecké rukavice -> Jezdecké rukavice -->
      <xsl:when test="$google_id = '3086'">4279</xsl:when><!-- Stěrky do mís -> Kuchyňské stěrky -->
      <xsl:when test="$google_id = '3090'">3893</xsl:when><!-- Masky na americký fotbal -> Helmy na americký fotbal -->
      <xsl:when test="$google_id = '3091'">3415</xsl:when><!-- Kuchyňské teploměry -> Kuchyňské teploměry -->
      <xsl:when test="$google_id = '3106'">6845</xsl:when><!-- Golfová týčka -> Golfová týčka -->
      <xsl:when test="$google_id = '3107'">1774</xsl:when><!-- Badmintonové sítě -> Badmintonové sítě -->
      <xsl:when test="$google_id = '3109'">2307</xsl:when><!-- Násady na šipky -> Násadky na šipky -->
      <xsl:when test="$google_id = '3120'">1176</xsl:when><!-- Nůžky na živé ploty -> Nůžky na živý plot -->
      <xsl:when test="$google_id = '3135'">4906</xsl:when><!-- Kulečníkové koule -> Kulečníkové koule -->
      <xsl:when test="$google_id = '3139'">4905</xsl:when><!-- Kulečníkové stoly -> Kulečníkové stoly -->
      <xsl:when test="$google_id = '3141'">1367</xsl:when><!-- Brankářské rukavice -> Brankářské rukavice -->
      <xsl:when test="$google_id = '3144'">3005</xsl:when><!-- Slavnostní dekorace -> Vánoční dekorace -->
      <xsl:when test="$google_id = '3163'">1482</xsl:when><!-- Kuličkové skluzavky -> Skluzavky -->
      <xsl:when test="$google_id = '3164'">1319</xsl:when><!-- Činky -> Činky -->
      <xsl:when test="$google_id = '3178'">2179</xsl:when><!-- Kytarové struny -> Struny -->
      <xsl:when test="$google_id = '3188'">3153</xsl:when><!-- Cyklistické šortky a spodní prádlo -> Dětské spodní prádlo -->
      <xsl:when test="$google_id = '3196'">3274</xsl:when><!-- Obracečky -> Obracečky -->
      <xsl:when test="$google_id = '3206'">6557</xsl:when><!-- Kuchyňské kráječe -> Ruční kuchyňské kráječe -->
      <xsl:when test="$google_id = '3208'">8550</xsl:when><!-- Tekuté mýdlo -> Tekutá mýdla -->
      <xsl:when test="$google_id = '3216'">1000</xsl:when><!-- Kola na jízdní kola -> Jízdní kola -->
      <xsl:when test="$google_id = '3219'">1460</xsl:when><!-- Bowlingové koule -> Bowlingové koule -->
      <xsl:when test="$google_id = '3238'">2154</xsl:when><!-- Akvária -> Akvária -->
      <xsl:when test="$google_id = '3246'">1245</xsl:when><!-- Cyklistické rukavice -> Cyklistické rukavice -->
      <xsl:when test="$google_id = '3247'">3895</xsl:when><!-- Chrániče brady na americký fotbal -> Chrániče na americký fotbal -->
      <xsl:when test="$google_id = '3248'">3352</xsl:when><!-- Paličky na maso -> Paličky na maso -->
      <xsl:when test="$google_id = '3250'">5105</xsl:when><!-- Hroty na šipky -> Hroty na šipky -->
      <xsl:when test="$google_id = '3263'">1845</xsl:when><!-- Padákové hračky -> Plechové hračky -->
      <xsl:when test="$google_id = '3268'">3358</xsl:when><!-- Odkapávače nádobí -> Odkapávače nádobí -->
      <xsl:when test="$google_id = '3270'">2013</xsl:when><!-- Elektronické ladičky -> Ladičky -->
      <xsl:when test="$google_id = '3283'">5015</xsl:when><!-- Mapová data a software GPS -> CAD software -->
      <xsl:when test="$google_id = '3284'">2520</xsl:when><!-- Sušené maso -> Sušené maso -->
      <xsl:when test="$google_id = '3292'">1237</xsl:when><!-- Sedla kol -> Sedla na kolo -->
      <xsl:when test="$google_id = '3295'">1096</xsl:when><!-- Průchodky na tenisové rakety -> Tenisové rakety -->
      <xsl:when test="$google_id = '3297'">4375</xsl:when><!-- Boxovací pytle -> Bivakovací pytle -->
      <xsl:when test="$google_id = '3300'">3760</xsl:when><!-- Vertikální frézky -> Příslušenství k frézkám -->
      <xsl:when test="$google_id = '3304'">5629</xsl:when><!-- Plavecké rukavice -> Horolezecké rukavice -->
      <xsl:when test="$google_id = '3314'">2347</xsl:when><!-- Lezecké helmy -> Jezdecké helmy -->
      <xsl:when test="$google_id = '3319'">1747</xsl:when><!-- Stroje na cukrovou vatu -> Stroje na cukrovou vatu -->
      <xsl:when test="$google_id = '3324'">2016</xsl:when><!-- Klávesové pedály -> Příslušenství pro klávesové nástroje -->
      <xsl:when test="$google_id = '3326'">2085</xsl:when><!-- Startovací kabely -> Startovací kabely -->
      <xsl:when test="$google_id = '3331'">984</xsl:when><!-- Běžecké lyže -> Běžecké lyže -->
      <xsl:when test="$google_id = '3337'">3344</xsl:when><!-- Chlebníky -> Chlebníky -->
      <xsl:when test="$google_id = '3339'">1109</xsl:when><!-- Kriketové rukavice -> Hokejové rukavice -->
      <xsl:when test="$google_id = '3343'">3899</xsl:when><!-- Vycpávky přileb na americký fotbal -> Míče na americký fotbal -->
      <xsl:when test="$google_id = '3345'">1094</xsl:when><!-- Stoly na stolní tenis -> Stoly na stolní tenis -->
      <xsl:when test="$google_id = '3358'">6899</xsl:when><!-- Skládací židle a stolky -> Odkládací stolky -->
      <xsl:when test="$google_id = '3375'">1090</xsl:when><!-- Pálky a sady na stolní tenis -> Doplňky na stolní tenis -->
      <xsl:when test="$google_id = '3378'">4063</xsl:when><!-- Modely kluzáků -> Pletací háčky -->
      <xsl:when test="$google_id = '3385'">2638</xsl:when><!-- Lisy na česnek -> Lisy na česnek -->
      <xsl:when test="$google_id = '3387'">822</xsl:when><!-- Paměťové karty Flash -> Paměťové karty -->
      <xsl:when test="$google_id = '3388'">1973</xsl:when><!-- Hrábě -> Hrábě -->
      <xsl:when test="$google_id = '3403'">1096</xsl:when><!-- Pásky a gripy na tenisové rakety -> Tenisové rakety -->
      <xsl:when test="$google_id = '3412'">2004</xsl:when><!-- Snímače na elektrické kytary -> Elektrické kytary -->
      <xsl:when test="$google_id = '3416'">3334</xsl:when><!-- Vývojové desky -> Odrazné desky -->
      <xsl:when test="$google_id = '3419'">4279</xsl:when><!-- Široké stěrky -> Kuchyňské stěrky -->
      <xsl:when test="$google_id = '3421'">3778</xsl:when><!-- Nože na pizzu -> Pece na pizzu -->
      <xsl:when test="$google_id = '3425'">1834</xsl:when><!-- Tiskové servery -> Servery -->
      <xsl:when test="$google_id = '3442'">3899</xsl:when><!-- Rukavice na americký fotbal -> Míče na americký fotbal -->
      <xsl:when test="$google_id = '3450'">948</xsl:when><!-- Kávové filtry -> Vodní filtry -->
      <xsl:when test="$google_id = '3452'">3129</xsl:when><!-- Kotevní řetězy -> Moto řetězy -->
      <xsl:when test="$google_id = '3460'">4063</xsl:when><!-- Draci -> Pletací háčky -->
      <xsl:when test="$google_id = '3461'">2770</xsl:when><!-- Kabely KVM -> KVM kabely -->
      <xsl:when test="$google_id = '3466'">8555</xsl:when><!-- Káči -> Káči -->
      <xsl:when test="$google_id = '3467'">3269</xsl:when><!-- Válečky -> Vařečky -->
      <xsl:when test="$google_id = '3487'">6844</xsl:when><!-- Ragbyové rukavice -> Golfové rukavice -->
      <xsl:when test="$google_id = '3491'">1163</xsl:when><!-- Ventily postřikovačů -> Postřikovače -->
      <xsl:when test="$google_id = '3492'">3895</xsl:when><!-- Brány na americký fotbal -> Chrániče na americký fotbal -->
      <xsl:when test="$google_id = '3497'">3895</xsl:when><!-- Krční chrániče na americký fotbal -> Chrániče na americký fotbal -->
      <xsl:when test="$google_id = '3505'">4437</xsl:when><!-- Kuše -> Kuše -->
      <xsl:when test="$google_id = '3508'">6403</xsl:when><!-- Chemické ohřívače rukou -> Ohřívače rukou -->
      <xsl:when test="$google_id = '3509'">6404</xsl:when><!-- Odstranitelná tetování -> Make-upy -->
      <xsl:when test="$google_id = '3510'">3893</xsl:when><!-- Vnitřní kalhoty na americký fotbal -> Helmy na americký fotbal -->
      <xsl:when test="$google_id = '3517'">5846</xsl:when><!-- Pokosové pily -> Pokosové pily -->
      <xsl:when test="$google_id = '3518'">1720</xsl:when><!-- Úchyty pro horolezecké stěny -> Horolezecké stěny -->
      <xsl:when test="$google_id = '3521'">3278</xsl:when><!-- Škrabky a vykrajovátka -> Vykrajovátka -->
      <xsl:when test="$google_id = '3522'">2890</xsl:when><!-- Časovače osvětlení -> LED osvětlení -->
      <xsl:when test="$google_id = '3528'">8559</xsl:when><!-- Terče na sportovní střelbu -> Terče na střelbu -->
      <xsl:when test="$google_id = '3535'">6844</xsl:when><!-- Bowlingové rukavice -> Golfové rukavice -->
      <xsl:when test="$google_id = '3536'">1081</xsl:when><!-- Lakrosové míčky -> Florbalové míčky -->
      <xsl:when test="$google_id = '3539'">2839</xsl:when><!-- Čtečky elektronických knih -> Čtečky knih -->
      <xsl:when test="$google_id = '3541'">2772</xsl:when><!-- Telefonní kabely -> Síťové kabely -->
      <xsl:when test="$google_id = '3544'">5091</xsl:when><!-- Baseballové a softballové mety -> Baseballové/softballové sety -->
      <xsl:when test="$google_id = '3546'">1094</xsl:when><!-- Roboty na stolní tenis -> Stoly na stolní tenis -->
      <xsl:when test="$google_id = '3553'">2880</xsl:when><!-- Talíře -> Talíře -->
      <xsl:when test="$google_id = '3559'">6945</xsl:when><!-- Terče na šipky -> Toulce na šípy -->
      <xsl:when test="$google_id = '3573'">1044</xsl:when><!-- Filtry do klimatizací -> Klimatizace -->
      <xsl:when test="$google_id = '3575'">5442</xsl:when><!-- Čepice na vodní pólo -> Míče na vodní pólo -->
      <xsl:when test="$google_id = '3580'">877</xsl:when><!-- Čtečky paměťových karet -> Čtečky paměťových karet -->
      <xsl:when test="$google_id = '3582'">5847</xsl:when><!-- Pásové pily -> Pásové pily -->
      <xsl:when test="$google_id = '3588'">6642</xsl:when><!-- Klávesové stojany -> Klávesové stojany -->
      <xsl:when test="$google_id = '3594'">1174</xsl:when><!-- Ruční pily -> Ruční pily -->
      <xsl:when test="$google_id = '3596'">1322</xsl:when><!-- Plavací přístroje -> Posilovací stroje -->
      <xsl:when test="$google_id = '3610'">1683</xsl:when><!-- Řetězové pily -> Řetězové pily -->
      <xsl:when test="$google_id = '3615'">1108</xsl:when><!-- Hokejové kalhoty -> Hokejové kalhoty -->
      <xsl:when test="$google_id = '3620'">3273</xsl:when><!-- Naběračky -> Naběračky -->
      <xsl:when test="$google_id = '3621'">3895</xsl:when><!-- Ramenní chrániče na americký fotbal -> Chrániče na americký fotbal -->
      <xsl:when test="$google_id = '3627'">1848</xsl:when><!-- Dětské zbraně -> Dětské zbraně -->
      <xsl:when test="$google_id = '3633'">6746</xsl:when><!-- Škrabky na gril -> Obaly na gril -->
      <xsl:when test="$google_id = '3638'">1096</xsl:when><!-- Brašny na tenisové rakety -> Tenisové rakety -->
      <xsl:when test="$google_id = '3639'">1254</xsl:when><!-- Rámy kol -> Rámy na kolo -->
      <xsl:when test="$google_id = '3667'">5953</xsl:when><!-- Filtry do čističek vzduchu -> Filtry k čističkám vzduchu -->
      <xsl:when test="$google_id = '3673'">3759</xsl:when><!-- Frézy -> Frézy -->
      <xsl:when test="$google_id = '3678'">5442</xsl:when><!-- Branky na vodní pólo -> Míče na vodní pólo -->
      <xsl:when test="$google_id = '3696'">1738</xsl:when><!-- Starožitné hodiny -> Hodiny -->
      <xsl:when test="$google_id = '3698'">1460</xsl:when><!-- Tašky na bowlingové koule -> Bowlingové koule -->
      <xsl:when test="$google_id = '3699'">1197</xsl:when><!-- Jídelní hůlky -> Příbory -->
      <xsl:when test="$google_id = '3706'">5844</xsl:when><!-- Stolní pily -> Stolní pily -->
      <xsl:when test="$google_id = '3712'">834</xsl:when><!-- USB flash disky -> USB flash disky -->
      <xsl:when test="$google_id = '3725'">5845</xsl:when><!-- Přímočaré pily -> Přímočaré pily -->
      <xsl:when test="$google_id = '3730'">1909</xsl:when><!-- Sekačky -> Sekačky -->
      <xsl:when test="$google_id = '3746'">1402</xsl:when><!-- Karabiny -> Karabiny -->
      <xsl:when test="$google_id = '3755'">1109</xsl:when><!-- Kulečníkové rukavice -> Hokejové rukavice -->
      <xsl:when test="$google_id = '3764'">2770</xsl:when><!-- Svorky na kabely -> KVM kabely -->
      <xsl:when test="$google_id = '3766'">2306</xsl:when><!-- Letky na šipky -> Letky na šipky -->
      <xsl:when test="$google_id = '3774'">8448</xsl:when><!-- Gymnastické kruhy -> Gymnastické kruhy -->
      <xsl:when test="$google_id = '3775'">2002</xsl:when><!-- Snímače na akustické kytary -> Akustické kytary -->
      <xsl:when test="$google_id = '3779'">5139</xsl:when><!-- Cvičební koně -> Čištění na koně -->
      <xsl:when test="$google_id = '3790'">1388</xsl:when><!-- Baseballové pálky -> Baseballové/softballové pálky -->
      <xsl:when test="$google_id = '3794'">5442</xsl:when><!-- Míče na vodní pólo -> Míče na vodní pólo -->
      <xsl:when test="$google_id = '3800'">3936</xsl:when><!-- Termosky -> Termostaty -->
      <xsl:when test="$google_id = '3805'">5465</xsl:when><!-- Stavebnice -> Stavebnice LaQ -->
      <xsl:when test="$google_id = '3807'">1465</xsl:when><!-- Plavecké čepice -> Plavecké čepice -->
      <xsl:when test="$google_id = '3819'">4399</xsl:when><!-- Trezory -> Trezory -->
      <xsl:when test="$google_id = '3821'">1400</xsl:when><!-- Jezdecké přilby -> Horolezecké přilby -->
      <xsl:when test="$google_id = '3838'">6202</xsl:when><!-- Filtry do kávovarů -> Filtry do kávovarů -->
      <xsl:when test="$google_id = '3839'">1450</xsl:when><!-- Jednotlivé šipky a sady šipek -> Šipky -->
      <xsl:when test="$google_id = '3840'">1738</xsl:when><!-- Nástěnné hodiny -> Hodiny -->
      <xsl:when test="$google_id = '3841'">1175</xsl:when><!-- Zahradnické nůžky -> Zahradní nůžky -->
      <xsl:when test="$google_id = '3844'">1197</xsl:when><!-- Stolní nože -> Příbory -->
      <xsl:when test="$google_id = '3868'">2357</xsl:when><!-- Cyklistické trenažéry -> Eliptické trenažéry -->
      <xsl:when test="$google_id = '3871'">5295</xsl:when><!-- Pohlednice -> Pohlednice -->
      <xsl:when test="$google_id = '3874'">3026</xsl:when><!-- Bublifuky -> Bublifuky -->
      <xsl:when test="$google_id = '3878'">8511</xsl:when><!-- Štafetové kolíky -> Stanové kolíky -->
      <xsl:when test="$google_id = '3880'">8464</xsl:when><!-- Vrhací kladiva -> Posilovací kladiva -->
      <xsl:when test="$google_id = '3881'">5332</xsl:when><!-- Ragbyové branky -> Fotbalové branky -->
      <xsl:when test="$google_id = '3898'">3683</xsl:when><!-- Osvěžovače vzduchu -> Osvěžovače vzduchu -->
      <xsl:when test="$google_id = '3906'">1096</xsl:when><!-- Tenisové rakety -> Tenisové rakety -->
      <xsl:when test="$google_id = '3907'">1073</xsl:when><!-- Badmintonové míčky -> Badmintonové míčky -->
      <xsl:when test="$google_id = '3929'">3873</xsl:when><!-- Joja -> Joja -->
      <xsl:when test="$google_id = '3932'">3570</xsl:when><!-- Krumpáče -> Krumpáče -->
      <xsl:when test="$google_id = '3938'">5080</xsl:when><!-- Medicinbaly -> Medicinbaly -->
      <xsl:when test="$google_id = '3939'">2324</xsl:when><!-- Lžíce -> Klíče -->
      <xsl:when test="$google_id = '3943'">1478</xsl:when><!-- Hokejové hračky -> Dřevěné hračky -->
      <xsl:when test="$google_id = '3945'">6602</xsl:when><!-- Mikrofonní předzesilovače -> WiFi zesilovače -->
      <xsl:when test="$google_id = '3950'">1074</xsl:when><!-- Badmintonové rakety -> Badmintonové rakety -->
      <xsl:when test="$google_id = '3957'">1450</xsl:when><!-- Ochranná deska za terč na šipky -> Šipky -->
      <xsl:when test="$google_id = '3961'">1097</xsl:when><!-- Tenisové sítě -> Tenisové sítě -->
      <xsl:when test="$google_id = '3964'">1090</xsl:when><!-- Míčky na stolní tenis -> Doplňky na stolní tenis -->
      <xsl:when test="$google_id = '3966'">4063</xsl:when><!-- Vzdušné a vodní rakety -> Pletací háčky -->
      <xsl:when test="$google_id = '3970'">6670</xsl:when><!-- Lakrosové branky -> Hokejové branky -->
      <xsl:when test="$google_id = '4015'">1197</xsl:when><!-- Vidličky -> Příbory -->
      <xsl:when test="$google_id = '4043'">6789</xsl:when><!-- Headcovery -> Golfové headcovery -->
      <xsl:when test="$google_id = '4044'">5747</xsl:when><!-- Přívěsné a skříňové vozíky -> Přívěsné vozíky -->
      <xsl:when test="$google_id = '4050'">1075</xsl:when><!-- Stojany na basketbalové koše -> Basketbalové koše -->
      <xsl:when test="$google_id = '4057'">1512</xsl:when><!-- Příčesky -> Přívěsky -->
      <xsl:when test="$google_id = '4080'">6899</xsl:when><!-- Skládací stoly -> Odkládací stolky -->
      <xsl:when test="$google_id = '4081'">2280</xsl:when><!-- Vodováhy -> Vodováhy -->
      <xsl:when test="$google_id = '4082'">2391</xsl:when><!-- Popelníky -> Popelnice -->
      <xsl:when test="$google_id = '4089'">1381</xsl:when><!-- Basketbalové desky -> Basketbalové dresy -->
      <xsl:when test="$google_id = '4102'">4144</xsl:when><!-- Náhradní displeje k notebookům -> Displeje pro notebooky -->
      <xsl:when test="$google_id = '4105'">2862</xsl:when><!-- Opalovací lehátka -> Zahradní lehátka -->
      <xsl:when test="$google_id = '4106'">5905</xsl:when><!-- Houbičky na make-up -> Houbičky na make-up -->
      <xsl:when test="$google_id = '4111'">5239</xsl:when><!-- Kytarová trsátka -> Trsátka -->
      <xsl:when test="$google_id = '4126'">1608</xsl:when><!-- Plážové osušky -> Ručníky -->
      <xsl:when test="$google_id = '4142'">2968</xsl:when><!-- Stojany na noty -> Stojany na noty -->
      <xsl:when test="$google_id = '4143'">2785</xsl:when><!-- Ubrusy -> Ubrusy -->
      <xsl:when test="$google_id = '4164'">679</xsl:when><!-- Monokuláry -> Okuláry -->
      <xsl:when test="$google_id = '4174'">3410</xsl:when><!-- Zipy -> Zipy -->
      <xsl:when test="$google_id = '4199'">1187</xsl:when><!-- Držáky zahradních hadic -> Zahradní hadice -->
      <xsl:when test="$google_id = '4214'">3347</xsl:when><!-- Ozdobné louskáčky -> Louskáčky -->
      <xsl:when test="$google_id = '4226'">3412</xsl:when><!-- Knoflíky -> Knoflíky -->
      <xsl:when test="$google_id = '4248'">4176</xsl:when><!-- Berle -> Zdravotní berle -->
      <xsl:when test="$google_id = '4257'">1608</xsl:when><!-- Kuchyňské ručníky -> Ručníky -->
      <xsl:when test="$google_id = '4270'">750</xsl:when><!-- Šasi notebooků -> Notebooky -->
      <xsl:when test="$google_id = '4283'">2084</xsl:when><!-- Pokladny a pokladní zásuvky -> Pokladní zásuvky -->
      <xsl:when test="$google_id = '4292'">2146</xsl:when><!-- Ohřívací stoly -> Servírovací stolky -->
      <xsl:when test="$google_id = '4295'">5100</xsl:when><!-- Prasátka a pokladničky -> Pokladničky -->
      <xsl:when test="$google_id = '4301'">4679</xsl:when><!-- Náhradní klávesnice k notebookům -> Náhradní klávesnice pro notebooky -->
      <xsl:when test="$google_id = '4303'">1894</xsl:when><!-- Vazačky -> Vazače -->
      <xsl:when test="$google_id = '4317'">1662</xsl:when><!-- Jednací stoly -> Jídelní stoly -->
      <xsl:when test="$google_id = '4332'">6473</xsl:when><!-- Hnětače těsta -> Hnětače těsta -->
      <xsl:when test="$google_id = '4355'">1662</xsl:when><!-- Kuchyňské a jídelní stoly -> Jídelní stoly -->
      <xsl:when test="$google_id = '4366'">5006</xsl:when><!-- Koupací polštářky -> Dekorační polštáře -->
      <xsl:when test="$google_id = '4416'">675</xsl:when><!-- Telekonvertory -> Telekonvertory -->
      <xsl:when test="$google_id = '4418'">5997</xsl:when><!-- Smetana do kávy -> Smetany do kávy -->
      <xsl:when test="$google_id = '4420'">1658</xsl:when><!-- Povlaky na matrace -> Nafukovací matrace -->
      <xsl:when test="$google_id = '4433'">8569</xsl:when><!-- Pelechy pro kočky -> Pelíšky pro kočky -->
      <xsl:when test="$google_id = '4434'">2245</xsl:when><!-- Pelechy pro psy -> Pelíšky pro psy -->
      <xsl:when test="$google_id = '4441'">867</xsl:when><!-- Pouzdra na objektivy -> Pouzdra na objektivy -->
      <xsl:when test="$google_id = '4450'">3237</xsl:when><!-- Námořní vysílačky -> Baterie pro vysílačky -->
      <xsl:when test="$google_id = '4453'">6622</xsl:when><!-- Polštářky na křesla a pohovky -> Dětská křesla a pohovky -->
      <xsl:when test="$google_id = '4454'">1612</xsl:when><!-- Polštářky -> Polštáře -->
      <xsl:when test="$google_id = '4458'">5241</xsl:when><!-- Držáky na televize a monitory -> Držáky a stojany na TV a monitory -->
      <xsl:when test="$google_id = '4463'">4206</xsl:when><!-- Audio a video adaptéry a kabelové spojky -> AC adaptéry -->
      <xsl:when test="$google_id = '4466'">6844</xsl:when><!-- Golfové rukavice -> Golfové rukavice -->
      <xsl:when test="$google_id = '4485'">1490</xsl:when><!-- Ventilátory -> Epilátory -->
      <xsl:when test="$google_id = '4510'">5757</xsl:when><!-- Epilátory -> Respirátory -->
      <xsl:when test="$google_id = '4512'">763</xsl:when><!-- Numerické klávesnice -> Klávesnice -->
      <xsl:when test="$google_id = '4513'">6790</xsl:when><!-- Zahradní pohovky -> Dětský zahradní nábytek -->
      <xsl:when test="$google_id = '4528'">6776</xsl:when><!-- Čajovary -> Čajovary -->
      <xsl:when test="$google_id = '4539'">6988</xsl:when><!-- Chladničky na víno -> Chladící nádoby na víno -->
      <xsl:when test="$google_id = '4540'">1548</xsl:when><!-- Fagoty -> Fagoty -->
      <xsl:when test="$google_id = '4541'">1544</xsl:when><!-- Hoboje -> Hoboje -->
      <xsl:when test="$google_id = '4544'">4200</xsl:when><!-- Okapy – příslušenství -> Brusky - příslušenství -->
      <xsl:when test="$google_id = '4546'">2029</xsl:when><!-- Budíky -> Budíky -->
      <xsl:when test="$google_id = '4550'">731</xsl:when><!-- Přívěsky a popruhy na mobilní telefony -> Mobilní telefony -->
      <xsl:when test="$google_id = '4552'">6514</xsl:when><!-- Rozprašovače -> Rozjasňovače -->
      <xsl:when test="$google_id = '4570'">698</xsl:when><!-- Stojany na projekční plátna -> Projekční plátna -->
      <xsl:when test="$google_id = '4572'">1000</xsl:when><!-- Duše na jízdní kola -> Jízdní kola -->
      <xsl:when test="$google_id = '4574'">6688</xsl:when><!-- Brzdové třmeny na kola -> Brzdové třmeny na kolo -->
      <xsl:when test="$google_id = '4592'">1000</xsl:when><!-- Kliky na jízdní kola -> Jízdní kola -->
      <xsl:when test="$google_id = '4631'">2015</xsl:when><!-- Paličky k bicím nástrojům -> Příslušenství pro bicí -->
      <xsl:when test="$google_id = '4646'">1683</xsl:when><!-- Řetězy pro řetězové pily -> Řetězové pily -->
      <xsl:when test="$google_id = '4647'">1683</xsl:when><!-- Lišty pro řetězové pily -> Řetězové pily -->
      <xsl:when test="$google_id = '4654'">1006</xsl:when><!-- Přihrádky do sušiček potravin -> Sušičky potravin -->
      <xsl:when test="$google_id = '4655'">1006</xsl:when><!-- Listy do sušiček potravin -> Sušičky potravin -->
      <xsl:when test="$google_id = '4656'">6822</xsl:when><!-- Podložky a potahy na žehlicí prkna -> Potahy na žehlicí prkna -->
      <xsl:when test="$google_id = '4657'">3667</xsl:when><!-- Odstraňovače skvrn -> Odstraňovače skvrn -->
      <xsl:when test="$google_id = '4659'">6642</xsl:when><!-- Pilové stojany -> Klávesové stojany -->
      <xsl:when test="$google_id = '4666'">731</xsl:when><!-- Konferenční telefony -> Mobilní telefony -->
      <xsl:when test="$google_id = '4669'">8354</xsl:when><!-- Podložky pod cvičební stroje -> Podložky pod fitness stroje -->
      <xsl:when test="$google_id = '4682'">3849</xsl:when><!-- Rýže -> Rýže -->
      <xsl:when test="$google_id = '4689'">4315</xsl:when><!-- Cereálie a müsli -> Cereálie a müsli -->
      <xsl:when test="$google_id = '4697'">2808</xsl:when><!-- Nábytkové podložky kování -> Nábytkové kování -->
      <xsl:when test="$google_id = '4698'">2808</xsl:when><!-- Nábytkové západky -> Nábytkové kování -->
      <xsl:when test="$google_id = '4699'">2808</xsl:when><!-- Nábytková dvířka -> Nábytkové kování -->
      <xsl:when test="$google_id = '4700'">2808</xsl:when><!-- Nábytkové úchytky a madla -> Nábytkové kování -->
      <xsl:when test="$google_id = '4709'">4200</xsl:when><!-- Generátory – příslušenství -> Brusky - příslušenství -->
      <xsl:when test="$google_id = '4738'">6261</xsl:when><!-- Pouzdra na čtečky elektronických knih -> Pouzdra na čtečky knih -->
      <xsl:when test="$google_id = '4743'">1551</xsl:when><!-- Harmoniky -> Foukací harmoniky -->
      <xsl:when test="$google_id = '4745'">3021</xsl:when><!-- Tablety -> Tablety -->
      <xsl:when test="$google_id = '4746'">3357</xsl:when><!-- Formy na led -> Formy na led -->
      <xsl:when test="$google_id = '4755'">3605</xsl:when><!-- Měřiče vlhkosti -> Měřiče teploty a vlhkosti -->
      <xsl:when test="$google_id = '4757'">3069</xsl:when><!-- Hlukoměry -> Hloubkoměry -->
      <xsl:when test="$google_id = '4760'">2874</xsl:when><!-- 3D brýle -> 3D brýle -->
      <xsl:when test="$google_id = '4762'">6993</xsl:when><!-- Mlýnky na koření -> Mlýnky na koření -->
      <xsl:when test="$google_id = '4763'">4200</xsl:when><!-- Mlýnky – příslušenství -> Brusky - příslušenství -->
      <xsl:when test="$google_id = '4764'">3360</xsl:when><!-- Sady na pečení -> Provázky na pečení -->
      <xsl:when test="$google_id = '4765'">6843</xsl:when><!-- Sady kuchyňského náčiní -> Sady kuchyňského náčíní -->
      <xsl:when test="$google_id = '4766'">1630</xsl:when><!-- Přípravky proti vypadávání vlasů -> Přípravky proti vypadávání vlasů -->
      <xsl:when test="$google_id = '4779'">6404</xsl:when><!-- Kostýmový a divadelní make-up -> Make-upy -->
      <xsl:when test="$google_id = '4788'">4200</xsl:when><!-- Mlýnky na koření – příslušenství -> Brusky - příslušenství -->
      <xsl:when test="$google_id = '4810'">2017</xsl:when><!-- Kufry a pouzdra na fagoty -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4812'">2017</xsl:when><!-- Fagotové strojky -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4813'">2017</xsl:when><!-- Stojany na fagot -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4814'">1548</xsl:when><!-- Popruhy pro fagot -> Fagoty -->
      <xsl:when test="$google_id = '4815'">1548</xsl:when><!-- Vytěráky na fagot -> Fagoty -->
      <xsl:when test="$google_id = '4816'">1548</xsl:when><!-- Esa pro fagot -> Fagoty -->
      <xsl:when test="$google_id = '4819'">2017</xsl:when><!-- Kufry a pouzdra na klarinety -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4820'">2017</xsl:when><!-- Ligatury a kloboučky pro klarinety -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4823'">2017</xsl:when><!-- Podpěry a stojany na klarinet -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4824'">2017</xsl:when><!-- Klarinetové plátky -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4825'">1543</xsl:when><!-- Popruhy na klarinet -> Klarinety -->
      <xsl:when test="$google_id = '4827'">1543</xsl:when><!-- Vytěráky pro klarinety -> Klarinety -->
      <xsl:when test="$google_id = '4828'">1543</xsl:when><!-- Štětičky pro klarinety -> Klarinety -->
      <xsl:when test="$google_id = '4829'">1543</xsl:when><!-- Soudky pro klarinet -> Klarinety -->
      <xsl:when test="$google_id = '4830'">1543</xsl:when><!-- Korpusy pro klarinet -> Klarinety -->
      <xsl:when test="$google_id = '4831'">1543</xsl:when><!-- Hubičky pro klarinet -> Klarinety -->
      <xsl:when test="$google_id = '4834'">2017</xsl:when><!-- Kufry a pouzdra na flétny -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4837'">2017</xsl:when><!-- Podpěry a stojany na flétnu -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4840'">2919</xsl:when><!-- Vytěráky pro flétny -> Panovy flétny -->
      <xsl:when test="$google_id = '4844'">2017</xsl:when><!-- Kufry a pouzdra na hoboje -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4846'">2017</xsl:when><!-- Podpěry a stojany na hoboj -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4847'">2017</xsl:when><!-- Hobojové strojky -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4848'">1544</xsl:when><!-- Popruhy pro hoboje -> Hoboje -->
      <xsl:when test="$google_id = '4850'">1544</xsl:when><!-- Vytěráky pro hoboj -> Hoboje -->
      <xsl:when test="$google_id = '4853'">2017</xsl:when><!-- Kufry a pouzdra na saxofony -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4854'">2017</xsl:when><!-- Ligatury a kloboučky pro saxofony -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4857'">2017</xsl:when><!-- Podpěry a stojany na saxofon -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4858'">2017</xsl:when><!-- Saxofonové plátky -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4859'">1541</xsl:when><!-- Popruhy pro saxofony -> Saxofony -->
      <xsl:when test="$google_id = '4862'">1541</xsl:when><!-- Vytěráky pro saxofony -> Saxofony -->
      <xsl:when test="$google_id = '4866'">2017</xsl:when><!-- Vazelína na korková těsnění -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4867'">2017</xsl:when><!-- Čisticí utěrky na dřevěné dechové nástroje -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4922'">6012</xsl:when><!-- Přehrávače CD pro DJ -> CD přehrávače pro DJ -->
      <xsl:when test="$google_id = '4923'">712</xsl:when><!-- DJ systémy -> Hi-Fi systémy -->
      <xsl:when test="$google_id = '4928'">2973</xsl:when><!-- Víceúčelové baterie -> Olověné baterie -->
      <xsl:when test="$google_id = '4939'">2017</xsl:when><!-- Nože na plátky dřevěných dechových nástrojů -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4947'">4330</xsl:when><!-- Med -> Medy -->
      <xsl:when test="$google_id = '4949'">5059</xsl:when><!-- Publikační software pro domácnost -> Multimediální software -->
      <xsl:when test="$google_id = '4950'">5059</xsl:when><!-- Software pro úpravu animací -> Multimediální software -->
      <xsl:when test="$google_id = '4951'">5059</xsl:when><!-- Software pro grafický design a kreslení -> Multimediální software -->
      <xsl:when test="$google_id = '4952'">5059</xsl:when><!-- Software na úpravu zvuku -> Multimediální software -->
      <xsl:when test="$google_id = '4953'">5059</xsl:when><!-- Software pro střih videa -> Multimediální software -->
      <xsl:when test="$google_id = '4954'">5059</xsl:when><!-- Software pro navrhování webových stránek -> Multimediální software -->
      <xsl:when test="$google_id = '4956'">1551</xsl:when><!-- Pouzdra na foukací harmoniky -> Foukací harmoniky -->
      <xsl:when test="$google_id = '4957'">2017</xsl:when><!-- Pouzdra na plátky dřevěných dechových nástrojů -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '4975'">3702</xsl:when><!-- Prostředky na mytí nádobí -> Prostředky na ruční mytí nádobí -->
      <xsl:when test="$google_id = '4990'">2024</xsl:when><!-- Krmivo pro ptáky -> Krmivo pro ptáky -->
      <xsl:when test="$google_id = '4992'">2253</xsl:when><!-- Hračky pro ptáky -> Hračky pro ptáky -->
      <xsl:when test="$google_id = '4997'">8472</xsl:when><!-- Nábytek pro kočky -> Paštiky pro kočky -->
      <xsl:when test="$google_id = '4999'">2249</xsl:when><!-- Stelivo pro kočky -> Steliva pro kočky -->
      <xsl:when test="$google_id = '5000'">2249</xsl:when><!-- Nádoby na stelivo pro kočky -> Steliva pro kočky -->
      <xsl:when test="$google_id = '5001'">2247</xsl:when><!-- Hračky pro kočky -> Hračky pro kočky -->
      <xsl:when test="$google_id = '5002'">8473</xsl:when><!-- Pamlsky pro kočky -> Pamlsky pro kočky -->
      <xsl:when test="$google_id = '5004'">3110</xsl:when><!-- Oblečky pro psy -> Obojky pro psy -->
      <xsl:when test="$google_id = '5010'">2239</xsl:when><!-- Hračky pro psy -> Hračky pro psy -->
      <xsl:when test="$google_id = '5011'">3120</xsl:when><!-- Pamlsky pro psy -> Pamlsky pro psy -->
      <xsl:when test="$google_id = '5014'">2668</xsl:when><!-- Stelivo pro drobná zvířata -> Krmiva pro terarijní zvířata -->
      <xsl:when test="$google_id = '5015'">2025</xsl:when><!-- Krmivo pro drobná zvířata -> Krmivo pro hospodářská zvířata -->
      <xsl:when test="$google_id = '5019'">2155</xsl:when><!-- Dekorace do akvárií -> Dekorace do akvárií -->
      <xsl:when test="$google_id = '5024'">2023</xsl:when><!-- Krmení pro ryby -> Krmivo pro ryby -->
      <xsl:when test="$google_id = '5034'">5015</xsl:when><!-- Počítačové ikony -> CAD software -->
      <xsl:when test="$google_id = '5035'">5015</xsl:when><!-- Tapety na plochu -> CAD software -->
      <xsl:when test="$google_id = '5036'">5015</xsl:when><!-- Písma -> CAD software -->
      <xsl:when test="$google_id = '5044'">6790</xsl:when><!-- Venkovní lavičky -> Dětský zahradní nábytek -->
      <xsl:when test="$google_id = '5046'">1551</xsl:when><!-- Držáky na foukací harmoniky -> Foukací harmoniky -->
      <xsl:when test="$google_id = '5065'">6202</xsl:when><!-- Vodní filtry do kávovarů -> Filtry do kávovarů -->
      <xsl:when test="$google_id = '5082'">8473</xsl:when><!-- Oblečky pro kočky -> Pamlsky pro kočky -->
      <xsl:when test="$google_id = '5084'">6550</xsl:when><!-- Prací koule -> Prací koule -->
      <xsl:when test="$google_id = '5089'">6247</xsl:when><!-- Větráky – příslušenství -> Tampery a příslušenství -->
      <xsl:when test="$google_id = '5096'">5059</xsl:when><!-- Software pro skládání hudby -> Multimediální software -->
      <xsl:when test="$google_id = '5106'">2228</xsl:when><!-- Motocyklové brýle -> Moto brýle -->
      <xsl:when test="$google_id = '5123'">2258</xsl:when><!-- Náhradní pásky k hodinkám -> Řemínky k hodinkám -->
      <xsl:when test="$google_id = '5127'">5015</xsl:when><!-- Slovníkový a překladový software -> CAD software -->
      <xsl:when test="$google_id = '5138'">944</xsl:when><!-- Parní žehličky -> Žehličky -->
      <xsl:when test="$google_id = '5140'">6516</xsl:when><!-- Parní žehlicí lisy -> Parní žehlicí lisy -->
      <xsl:when test="$google_id = '5141'">1049</xsl:when><!-- Sušiče rukou -> Vysoušeče rukou -->
      <xsl:when test="$google_id = '5157'">3345</xsl:when><!-- Bloky a stojany na nože -> Bloky na nože -->
      <xsl:when test="$google_id = '5159'">6677</xsl:when><!-- Žehličky – příslušenství -> Příslušenství pro žehličky -->
      <xsl:when test="$google_id = '5166'">5481</xsl:when><!-- Chodítka -> Zdravotní chodítka -->
      <xsl:when test="$google_id = '5193'">2456</xsl:when><!-- Kostýmy -> Dámské kostýmy -->
      <xsl:when test="$google_id = '5194'">2466</xsl:when><!-- Masky -> Pásky -->
      <xsl:when test="$google_id = '5250'">1573</xsl:when><!-- Kombinézy -> Dětské kombinézy -->
      <xsl:when test="$google_id = '5251'">3414</xsl:when><!-- Kuchyňské nůžky -> Kuchyňské nůžky -->
      <xsl:when test="$google_id = '5257'">3255</xsl:when><!-- Držáky projektorů -> Držáky k projektorům -->
      <xsl:when test="$google_id = '5259'">795</xsl:when><!-- Válce do tiskáren -> Tiskárny -->
      <xsl:when test="$google_id = '5260'">795</xsl:when><!-- Pásky do tiskáren -> Tiskárny -->
      <xsl:when test="$google_id = '5261'">856</xsl:when><!-- Tiskové hlavy -> Stativové hlavy -->
      <xsl:when test="$google_id = '5266'">795</xsl:when><!-- Filtry do tiskáren -> Tiskárny -->
      <xsl:when test="$google_id = '5272'">1907</xsl:when><!-- Disková pole -> Disková pole -->
      <xsl:when test="$google_id = '5273'">2315</xsl:when><!-- Patch panely -> Patch panely -->
      <xsl:when test="$google_id = '5286'">6708</xsl:when><!-- Vakuové kávovary -> Pákové kávovary -->
      <xsl:when test="$google_id = '5287'">6470</xsl:when><!-- Ohřívače nápojů -> Ohřívače a dávkovače nápojů -->
      <xsl:when test="$google_id = '5299'">5015</xsl:when><!-- Antivirový a bezpečnostní software -> CAD software -->
      <xsl:when test="$google_id = '5300'">5015</xsl:when><!-- Pracovní a produktivní software -> CAD software -->
      <xsl:when test="$google_id = '5301'">5015</xsl:when><!-- Softwarové nástroje a údržba počítačů -> CAD software -->
      <xsl:when test="$google_id = '5302'">5015</xsl:when><!-- Síťový software -> CAD software -->
      <xsl:when test="$google_id = '5303'">5015</xsl:when><!-- Kancelářský software -> CAD software -->
      <xsl:when test="$google_id = '5304'">2073</xsl:when><!-- Finanční, daňový a účetní software -> Účetní a ekonomický software -->
      <xsl:when test="$google_id = '5308'">5746</xsl:when><!-- Stylusy -> Stylusy -->
      <xsl:when test="$google_id = '5338'">1641</xsl:when><!-- Samoopalovací přípravky -> Samoopalovací přípravky -->
      <xsl:when test="$google_id = '5339'">1755</xsl:when><!-- Opalovací oleje -> Pleťové oleje -->
      <xsl:when test="$google_id = '5359'">5380</xsl:when><!-- Adventní kalendáře -> Adventní kalendáře -->
      <xsl:when test="$google_id = '5363'">1179</xsl:when><!-- Lopaty na sníh -> Hrabla na sníh -->
      <xsl:when test="$google_id = '5367'">2186</xsl:when><!-- Kapodastry -> Kapodastry -->
      <xsl:when test="$google_id = '5368'">8541</xsl:when><!-- Slide pro kytary -> Rezofonické kytary -->
      <xsl:when test="$google_id = '5378'">900</xsl:when><!-- Boxerské šortky -> Dámské šortky -->
      <xsl:when test="$google_id = '5380'">2283</xsl:when><!-- Přepěťové ochrany -> Přepěťové ochrany -->
      <xsl:when test="$google_id = '5381'">805</xsl:when><!-- Zesilovače -> Zesilovače -->
      <xsl:when test="$google_id = '5385'">4830</xsl:when><!-- Návleky na boty -> Vložky do bot -->
      <xsl:when test="$google_id = '5387'">2456</xsl:when><!-- Boty ke kostýmům -> Dámské kostýmy -->
      <xsl:when test="$google_id = '5409'">3752</xsl:when><!-- Dětské a kojenecké plavky -> Kojenecké plavky -->
      <xsl:when test="$google_id = '5423'">4172</xsl:when><!-- Dětské ponožky a punčocháče -> Dětské punčocháče -->
      <xsl:when test="$google_id = '5424'">1571</xsl:when><!-- Dětské šaty -> Dětské šaty -->
      <xsl:when test="$google_id = '5432'">5961</xsl:when><!-- Softboxy -> Softboxy -->
      <xsl:when test="$google_id = '5446'">5216</xsl:when><!-- Svatební závoje -> Svatební závoje -->
      <xsl:when test="$google_id = '5459'">795</xsl:when><!-- Stojany na tiskárny -> Tiskárny -->
      <xsl:when test="$google_id = '5467'">5300</xsl:when><!-- Privátní filtry -> Privátní a antireflexní filtry -->
      <xsl:when test="$google_id = '5481'">1551</xsl:when><!-- Foukací klávesové harmoniky -> Foukací harmoniky -->
      <xsl:when test="$google_id = '5494'">3954</xsl:when><!-- Stojany na deštníky -> Stojany na deštníky -->
      <xsl:when test="$google_id = '5503'">799</xsl:when><!-- Set-top boxy -> Set-top boxy -->
      <xsl:when test="$google_id = '5504'">5557</xsl:when><!-- Podložky pod vánoční stromky -> Vánoční stromky -->
      <xsl:when test="$google_id = '5512'">2910</xsl:when><!-- Tašky a nosiče na motorky -> Nosiče na motokufry -->
      <xsl:when test="$google_id = '5513'">1588</xsl:when><!-- Noční košile -> Pánské košile -->
      <xsl:when test="$google_id = '5532'">678</xsl:when><!-- Dálková ovládání fotoaparátů -> Dálkové ovládání k fotoaparátům -->
      <xsl:when test="$google_id = '5533'">3639</xsl:when><!-- Měniče napětí -> Solární měniče napětí -->
      <xsl:when test="$google_id = '5537'">1203</xsl:when><!-- Sady nádobí -> Sady nádobí -->
      <xsl:when test="$google_id = '5540'">4908</xsl:when><!-- Cyklopočítače – příslušenství -> Kulečníkové příslušenství -->
      <xsl:when test="$google_id = '5552'">2341</xsl:when><!-- Lovecké a taktické kalhoty -> Pánské klasické kalhoty -->
      <xsl:when test="$google_id = '5566'">731</xsl:when><!-- Držáky na mobilní telefony -> Mobilní telefony -->
      <xsl:when test="$google_id = '5567'">4830</xsl:when><!-- Vložky do bot -> Vložky do bot -->
      <xsl:when test="$google_id = '5570'">4200</xsl:when><!-- Jogurtovače – příslušenství -> Brusky - příslušenství -->
      <xsl:when test="$google_id = '5571'">2295</xsl:when><!-- Gola sady -> Gola sady -->
      <xsl:when test="$google_id = '5580'">5340</xsl:when><!-- Kiteboardy -> Kiteboards -->
      <xsl:when test="$google_id = '5589'">825</xsl:when><!-- Antiradary -> Antiviry -->
      <xsl:when test="$google_id = '5597'">783</xsl:when><!-- Ozvučovací systémy -> Operační systémy -->
      <xsl:when test="$google_id = '5623'">2479</xsl:when><!-- Dětské pásky -> Dětské plavky -->
      <xsl:when test="$google_id = '5647'">1197</xsl:when><!-- Příborové sady -> Příbory -->
      <xsl:when test="$google_id = '5651'">6629</xsl:when><!-- Visačky na zavazadla -> Váhy na zavazadla -->
      <xsl:when test="$google_id = '5654'">4841</xsl:when><!-- Vytápění bazénů -> Zastřešení bazénů -->
      <xsl:when test="$google_id = '5658'">8511</xsl:when><!-- Stanové tyčky a kolíky -> Stanové kolíky -->
      <xsl:when test="$google_id = '5687'">2466</xsl:when><!-- Obi pásy -> Pásky -->
      <xsl:when test="$google_id = '5690'">4180</xsl:when><!-- Naslouchátka -> Naslouchátka -->
      <xsl:when test="$google_id = '5693'">2030</xsl:when><!-- Stopky -> Stopky -->
      <xsl:when test="$google_id = '5696'">731</xsl:when><!-- Rušičky mobilních telefonů -> Mobilní telefony -->
      <xsl:when test="$google_id = '5704'">1708</xsl:when><!-- Kolíčky na prádlo -> Kolíčky na prádlo -->
      <xsl:when test="$google_id = '5706'">5092</xsl:when><!-- Ušní svíčky -> Ušní svíce -->
      <xsl:when test="$google_id = '5716'">5750</xsl:when><!-- Stojany na oblečení -> Stojany na oblečení -->
      <xsl:when test="$google_id = '5723'">3805</xsl:when><!-- Iontové a energetické nápoje -> Energetické nápoje -->
      <xsl:when test="$google_id = '5750'">4314</xsl:when><!-- Sladké pečivo -> Sladké pečivo -->
      <xsl:when test="$google_id = '5759'">3837</xsl:when><!-- Omáčka na těstoviny -> Těstoviny -->
      <xsl:when test="$google_id = '5762'">4355</xsl:when><!-- Masové omáčky -> Omáčky -->
      <xsl:when test="$google_id = '5763'">4355</xsl:when><!-- Rybí omáčka -> Omáčky -->
      <xsl:when test="$google_id = '5771'">5998</xsl:when><!-- Škrob na vaření -> Smetany na vaření -->
      <xsl:when test="$google_id = '5775'">4351</xsl:when><!-- Přísady a extrakty na pečení -> Přísady na pečení -->
      <xsl:when test="$google_id = '5794'">4355</xsl:when><!-- Ovocné omáčky -> Omáčky -->
      <xsl:when test="$google_id = '5798'">4339</xsl:when><!-- Konzervovaná a sterilovaná zelenina -> Konzervovaná a nakládaná zelenina -->
      <xsl:when test="$google_id = '5799'">4338</xsl:when><!-- Konzervované a sterilované ovoce -> Konzervované ovoce -->
      <xsl:when test="$google_id = '5825'">3708</xsl:when><!-- Čistící a leštící prostředky na nábytek -> Čistící prostředky na nábytek -->
      <xsl:when test="$google_id = '5826'">1044</xsl:when><!-- Kryty klimatizací -> Klimatizace -->
      <xsl:when test="$google_id = '5838'">4826</xsl:when><!-- Dárkové tašky -> Dárkové tašky -->
      <xsl:when test="$google_id = '5847'">4899</xsl:when><!-- Vonné oleje -> Vonné oleje -->
      <xsl:when test="$google_id = '5869'">4978</xsl:when><!-- Pásky na cvičení -> Podložky na cvičení -->
      <xsl:when test="$google_id = '5873'">5965</xsl:when><!-- Zvedací magnety -> Zvedací magnety -->
      <xsl:when test="$google_id = '5880'">5864</xsl:when><!-- Sušičky nehtů -> Sušičky na nehty -->
      <xsl:when test="$google_id = '5886'">1664</xsl:when><!-- Kuchyňské a jídelní židle -> Jídelní židle -->
      <xsl:when test="$google_id = '5911'">1693</xsl:when><!-- Plážové podložky -> Bazénové podložky -->
      <xsl:when test="$google_id = '5914'">2411</xsl:when><!-- Korunky -> Korunky -->
      <xsl:when test="$google_id = '5915'">3367</xsl:when><!-- Věnečky do vlasů -> Gumičky do vlasů -->
      <xsl:when test="$google_id = '5922'">3002</xsl:when><!-- Pamětní vitríny -> Vitríny -->
      <xsl:when test="$google_id = '5928'">6916</xsl:when><!-- Flambovací pistole -> Flambovací pistole -->
      <xsl:when test="$google_id = '5935'">5015</xsl:when><!-- Virtuální měna -> CAD software -->
      <xsl:when test="$google_id = '5938'">1695</xsl:when><!-- Úložné a šatní skříňky -> Šatní skříně -->
      <xsl:when test="$google_id = '5979'">6426</xsl:when><!-- Tělové barvy a podkladové báze -> Podkladové báze -->
      <xsl:when test="$google_id = '5981'">3368</xsl:when><!-- Třpytky na tělo a vlasy -> Natáčky na vlasy -->
      <xsl:when test="$google_id = '5992'">3389</xsl:when><!-- Šicí jehly -> Šicí jehly -->
      <xsl:when test="$google_id = '6027'">5015</xsl:when><!-- CAD software -> CAD software -->
      <xsl:when test="$google_id = '6028'">5059</xsl:when><!-- Software pro přehrávání médií -> Multimediální software -->
      <xsl:when test="$google_id = '6029'">5059</xsl:when><!-- Software pro navrhování domů a interiérů -> Multimediální software -->
      <xsl:when test="$google_id = '6053'">1634</xsl:when><!-- Odstraňovače barvy na vlasy -> Barvy na vlasy -->
      <xsl:when test="$google_id = '6055'">5332</xsl:when><!-- Potřeby pro fotbalové branky -> Fotbalové branky -->
      <xsl:when test="$google_id = '6057'">5829</xsl:when><!-- Loutková divadla -> Loutková divadla -->
      <xsl:when test="$google_id = '6069'">2729</xsl:when><!-- Kosmetické sady -> Kosmetické sady -->
      <xsl:when test="$google_id = '6072'">6866</xsl:when><!-- Fixátory make-upu -> Fixace make-upu -->
      <xsl:when test="$google_id = '6073'">1663</xsl:when><!-- Uchycení nástěnných svítidel -> Svítidla -->
      <xsl:when test="$google_id = '6074'">6670</xsl:when><!-- Hokejové branky -> Hokejové branky -->
      <xsl:when test="$google_id = '6076'">1115</xsl:when><!-- Hokejky -> Hokejky -->
      <xsl:when test="$google_id = '6077'">6673</xsl:when><!-- Hokejové míčky a puky -> Hokejové puky -->
      <xsl:when test="$google_id = '6078'">1109</xsl:when><!-- Hokejové rukavice -> Hokejové rukavice -->
      <xsl:when test="$google_id = '6084'">5807</xsl:when><!-- Příslušenství k autoalarmům -> Příslušenství autokosmetiky -->
      <xsl:when test="$google_id = '6087'">1573</xsl:when><!-- Cyklistické kombinézy -> Dětské kombinézy -->
      <xsl:when test="$google_id = '6093'">972</xsl:when><!-- Automobilové pneumatiky -> Osobní pneumatiky -->
      <xsl:when test="$google_id = '6101'">4065</xsl:when><!-- Spínací špendlíky -> Špendlíky a zavírací špendlíky -->
      <xsl:when test="$google_id = '6104'">2825</xsl:when><!-- Tělové oleje -> Tělové oleje -->
      <xsl:when test="$google_id = '6127'">4063</xsl:when><!-- Pletací háčky -> Pletací háčky -->
      <xsl:when test="$google_id = '6139'">4064</xsl:when><!-- Pletací jehlice -> Pletací jehlice -->
      <xsl:when test="$google_id = '6145'">3410</xsl:when><!-- Suché zipy -> Zipy -->
      <xsl:when test="$google_id = '6150'">4086</xsl:when><!-- Krejčovské panny -> Krejčovské panny -->
      <xsl:when test="$google_id = '6168'">4063</xsl:when><!-- Vázací háčky -> Pletací háčky -->
      <xsl:when test="$google_id = '6180'">1860</xsl:when><!-- Vozíky na pořadače -> Šanony a pořadače -->
      <xsl:when test="$google_id = '6183'">5020</xsl:when><!-- Síťky na vlasy -> Tape in vlasy -->
      <xsl:when test="$google_id = '6189'">1805</xsl:when><!-- Ústní sprej -> Ústní spreje -->
      <xsl:when test="$google_id = '6228'">2450</xsl:when><!-- Dlouhé sukně -> Dámské sukně -->
      <xsl:when test="$google_id = '6258'">1909</xsl:when><!-- Tažené sekačky -> Sekačky -->
      <xsl:when test="$google_id = '6262'">1754</xsl:when><!-- Pleťové masky -> Pleťové masky -->
      <xsl:when test="$google_id = '6263'">3688</xsl:when><!-- Náhradní prachovky -> Prachovky -->
      <xsl:when test="$google_id = '6271'">2733</xsl:when><!-- Houpačky a dětská hřiště -> Dětská hřiště -->
      <xsl:when test="$google_id = '6278'">3778</xsl:when><!-- Domácí pece na pizzu -> Pece na pizzu -->
      <xsl:when test="$google_id = '6288'">4782</xsl:when><!-- Paddleboardy -> Paddleboardy -->
      <xsl:when test="$google_id = '6289'">776</xsl:when><!-- Záložní zdroje -> Zdroje -->
      <xsl:when test="$google_id = '6304'">6514</xsl:when><!-- Rozjasňovače -> Rozjasňovače -->
      <xsl:when test="$google_id = '6305'">6865</xsl:when><!-- Tvářenky a bronzery -> Bronzery -->
      <xsl:when test="$google_id = '6306'">6404</xsl:when><!-- Lesky na rty a tváře -> Make-upy -->
      <xsl:when test="$google_id = '6308'">787</xsl:when><!-- Brašny na fotoaparáty a videokamery -> Brašny a pouzdra pro videokamery -->
      <xsl:when test="$google_id = '6312'">4908</xsl:when><!-- Kajaky – příslušenství -> Kulečníkové příslušenství -->
      <xsl:when test="$google_id = '6314'">4908</xsl:when><!-- Kánoe – příslušenství -> Kulečníkové příslušenství -->
      <xsl:when test="$google_id = '6324'">1744</xsl:when><!-- Kroužky na ubrousky -> Ubrousky -->
      <xsl:when test="$google_id = '6334'">3766</xsl:when><!-- Sloupky na poštovní schránky -> Poštovní schránky -->
      <xsl:when test="$google_id = '6340'">6404</xsl:when><!-- Přípravky pro růst řas a obočí -> Make-upy -->
      <xsl:when test="$google_id = '6341'">4488</xsl:when><!-- Brusné bloky na nehty -> Brusky na nehty -->
      <xsl:when test="$google_id = '6351'">5622</xsl:when><!-- Hrací stoly -> Herní stoly -->
      <xsl:when test="$google_id = '6360'">2145</xsl:when><!-- Toaletní stolky do ložnice -> Toaletní stolky -->
      <xsl:when test="$google_id = '6367'">6790</xsl:when><!-- Sady venkovního nábytku -> Dětský zahradní nábytek -->
      <xsl:when test="$google_id = '6372'">1207</xsl:when><!-- Nástěnné poličky a římsy -> Poklice -->
      <xsl:when test="$google_id = '6378'">4201</xsl:when><!-- Ostřiče vrtáků -> Příslušenství k vrtačkám -->
      <xsl:when test="$google_id = '6394'">1748</xsl:when><!-- Ohrádky a dětské postýlky -> Dětské postýlky -->
      <xsl:when test="$google_id = '6396'">5921</xsl:when><!-- Skákací hrady -> Skákací hrady -->
      <xsl:when test="$google_id = '6403'">2023</xsl:when><!-- Krmítka pro ryby -> Krmivo pro ryby -->
      <xsl:when test="$google_id = '6407'">2141</xsl:when><!-- Houpací koně -> Houpací koně -->
      <xsl:when test="$google_id = '6416'">750</xsl:when><!-- Panty pro notebooky -> Notebooky -->
      <xsl:when test="$google_id = '6419'">3676</xsl:when><!-- Ochranné prostředky na textil a čalounění -> Čisticí prostředky na koberce a čalounění -->
      <xsl:when test="$google_id = '6428'">4894</xsl:when><!-- Stojany na květiny -> Stojany na květiny -->
      <xsl:when test="$google_id = '6436'">1969</xsl:when><!-- Kompostéry -> Kompostéry -->
      <xsl:when test="$google_id = '6439'">4200</xsl:when><!-- Jídelní hůlky – příslušenství -> Brusky - příslušenství -->
      <xsl:when test="$google_id = '6441'">4856</xsl:when><!-- Škrabky na jazyk -> Škrabky na jazyk -->
      <xsl:when test="$google_id = '6442'">1229</xsl:when><!-- Obaly na kolo -> Pedály na kolo -->
      <xsl:when test="$google_id = '6446'">5218</xsl:when><!-- Zavírače dveří -> Zavírače dveří -->
      <xsl:when test="$google_id = '6449'">2329</xsl:when><!-- Tašky na víno -> Stojany na víno -->
      <xsl:when test="$google_id = '6487'">2948</xsl:when><!-- Organizéry do kuchyňské linky -> Kuchyňské linky -->
      <xsl:when test="$google_id = '6492'">5257</xsl:when><!-- Vitrážové panely -> Vanové panely -->
      <xsl:when test="$google_id = '6508'">6314</xsl:when><!-- Napájecí zdroje a rozbočovače -> Zesilovače a rozbočovače -->
      <xsl:when test="$google_id = '6509'">1793</xsl:when><!-- Roztoky na kontaktní čočky -> Kontaktní čočky -->
      <xsl:when test="$google_id = '6510'">1793</xsl:when><!-- Pouzdra na kontaktní čočky -> Kontaktní čočky -->
      <xsl:when test="$google_id = '6526'">6969</xsl:when><!-- Nádoby na olej a ocet -> Nádoby na olej a ocet -->
      <xsl:when test="$google_id = '6555'">8522</xsl:when><!-- Šablony na obočí -> Vosky na obočí -->
      <xsl:when test="$google_id = '6559'">5113</xsl:when><!-- Ušní kapky -> Ušní spreje a kapky -->
      <xsl:when test="$google_id = '6603'">5557</xsl:when><!-- Stojánky na vánoční stromky -> Vánoční stromky -->
      <xsl:when test="$google_id = '6616'">4354</xsl:when><!-- Asijská hořčice -> Hořčice -->
      <xsl:when test="$google_id = '6641'">3808</xsl:when><!-- Limonela -> Limonády -->
      <xsl:when test="$google_id = '6663'">3852</xsl:when><!-- Pastinák -> Paštiky -->
      <xsl:when test="$google_id = '6721'">1993</xsl:when><!-- Irské flétny -> Příčné flétny -->
      <xsl:when test="$google_id = '6727'">5981</xsl:when><!-- Odpařovací ochlazovače vzduchu -> Ochlazovače vzduchu -->
      <xsl:when test="$google_id = '6761'">6006</xsl:when><!-- Cidery -> Cidery -->
      <xsl:when test="$google_id = '6783'">6357</xsl:when><!-- Tatarská omáčka -> Tatarské omáčky -->
      <xsl:when test="$google_id = '6792'">2363</xsl:when><!-- Krby -> Krby -->
      <xsl:when test="$google_id = '6800'">5621</xsl:when><!-- Hrací křesla -> Herní křesla -->
      <xsl:when test="$google_id = '6806'">4201</xsl:when><!-- Pily děrovky -> Příslušenství k vrtačkám -->
      <xsl:when test="$google_id = '6807'">3929</xsl:when><!-- Rozvaděče -> Rozvaděče -->
      <xsl:when test="$google_id = '6822'">6790</xsl:when><!-- Venkovní otomany -> Dětský zahradní nábytek -->
      <xsl:when test="$google_id = '6828'">6790</xsl:when><!-- Venkovní židle -> Dětský zahradní nábytek -->
      <xsl:when test="$google_id = '6834'">5361</xsl:when><!-- Sudy na dešťovou vodu -> Sudy na vodu -->
      <xsl:when test="$google_id = '6848'">5288</xsl:when><!-- Instantní nápoje -> Instantní nápoje -->
      <xsl:when test="$google_id = '6858'">6821</xsl:when><!-- Sady koupelnových doplňků -> Sady koupelnových doplňků -->
      <xsl:when test="$google_id = '6865'">5632</xsl:when><!-- 3D tiskárny -> 3D tiskárny -->
      <xsl:when test="$google_id = '6868'">1026</xsl:when><!-- Hoblovky -> Hoblíky -->
      <xsl:when test="$google_id = '6870'">6704</xsl:when><!-- Natahovací klíčky k hodinkám -> Natahovače hodinek -->
      <xsl:when test="$google_id = '6886'">706</xsl:when><!-- Radiopřijímače -> Radiopřijímače -->
      <xsl:when test="$google_id = '6892'">6790</xsl:when><!-- Venkovní postele -> Dětský zahradní nábytek -->
      <xsl:when test="$google_id = '6893'">4484</xsl:when><!-- Lepidla na nehty -> Lepidla na nehty -->
      <xsl:when test="$google_id = '6897'">1613</xsl:when><!-- Nouzové přikrývky -> Přikrývky -->
      <xsl:when test="$google_id = '6898'">5140</xsl:when><!-- Deky a přikrývky na koně -> Deky na koně -->
      <xsl:when test="$google_id = '6905'">4355</xsl:when><!-- Kari omáčka -> Omáčky -->
      <xsl:when test="$google_id = '6910'">6594</xsl:when><!-- Stolní desky -> Stolové desky -->
      <xsl:when test="$google_id = '6912'">1738</xsl:when><!-- Hodiny na stůl a polici -> Hodiny -->
      <xsl:when test="$google_id = '6914'">5154</xsl:when><!-- Jezdecké kalhoty -> Jezdecké kalhoty -->
      <xsl:when test="$google_id = '6920'">2821</xsl:when><!-- Kryty na zubní kartáčky -> Manuální zubní kartáčky -->
      <xsl:when test="$google_id = '6936'">3928</xsl:when><!-- Sušené květiny -> Květiny -->
      <xsl:when test="$google_id = '6956'">1171</xsl:when><!-- Šejkry -> Sekery -->
      <xsl:when test="$google_id = '6972'">2702</xsl:when><!-- Reflexní kladívka -> Ruční kladiva -->
      <xsl:when test="$google_id = '6985'">2713</xsl:when><!-- Ozdobné knoflíky -> Manžetové knoflíčky -->
      <xsl:when test="$google_id = '6997'">5379</xsl:when><!-- Sběratelské karty -> Sběratelské karty -->
      <xsl:when test="$google_id = '7003'">5936</xsl:when><!-- Motorkářské kalhoty -> Těhotenské kalhoty -->
      <xsl:when test="$google_id = '7004'">3596</xsl:when><!-- Schodiště -> Schodiště -->
      <xsl:when test="$google_id = '7018'">5518</xsl:when><!-- Rolery na péči o pokožku -> Speciální péče o pokožku -->
      <xsl:when test="$google_id = '7031'">5553</xsl:when><!-- Měkké střechy vozidel -> Plachty na auto -->
      <xsl:when test="$google_id = '7057'">2752</xsl:when><!-- Hlavy kladiva -> Aku kladiva -->
      <xsl:when test="$google_id = '7061'">1408</xsl:when><!-- Šrouby do ledu -> Šrouby do ledu -->
      <xsl:when test="$google_id = '7065'">6648</xsl:when><!-- Nýtovací pistole -> Nýtovací pistole -->
      <xsl:when test="$google_id = '7080'">1894</xsl:when><!-- Vazbovače -> Vazače -->
      <xsl:when test="$google_id = '7089'">5277</xsl:when><!-- Jednorázové servírovací tácy -> Jednorázové nádobí -->
      <xsl:when test="$google_id = '7093'">6821</xsl:when><!-- Držáky na koupelnové doplňky -> Sady koupelnových doplňků -->
      <xsl:when test="$google_id = '7100'">2015</xsl:when><!-- Pouzdra na činely a bubny -> Příslušenství pro bicí -->
      <xsl:when test="$google_id = '7101'">6616</xsl:when><!-- Pedály k bubnům -> Pedály pro bubny -->
      <xsl:when test="$google_id = '7102'">2015</xsl:when><!-- Hardware pro bicí sady -> Příslušenství pro bicí -->
      <xsl:when test="$google_id = '7103'">2015</xsl:when><!-- Beatery k basovým bubnům -> Příslušenství pro bicí -->
      <xsl:when test="$google_id = '7127'">4890</xsl:when><!-- Potravinářské barvivo -> Potravinářské barvy a barviva -->
      <xsl:when test="$google_id = '7131'">3360</xsl:when><!-- Váhy na pečení -> Provázky na pečení -->
      <xsl:when test="$google_id = '7132'">6305</xsl:when><!-- Overaly -> Dámské overaly -->
      <xsl:when test="$google_id = '7135'">5925</xsl:when><!-- Cestovní adaptéry -> Cestovní adaptéry -->
      <xsl:when test="$google_id = '7136'">2707</xsl:when><!-- Obkladačky -> Řezačky obkladů -->
      <xsl:when test="$google_id = '7140'">4201</xsl:when><!-- Nástavce na vrtáky -> Příslušenství k vrtačkám -->
      <xsl:when test="$google_id = '7151'">2015</xsl:when><!-- Obaly a držáky na paličky a metličky -> Příslušenství pro bicí -->
      <xsl:when test="$google_id = '7152'">2015</xsl:when><!-- Klíče na bubny -> Příslušenství pro bicí -->
      <xsl:when test="$google_id = '7153'">2015</xsl:when><!-- Blány na bubny -> Příslušenství pro bicí -->
      <xsl:when test="$google_id = '7159'">4321</xsl:when><!-- Chlebové tyčinky -> Čokoládové tyčinky -->
      <xsl:when test="$google_id = '7172'">5745</xsl:when><!-- Lapače snů -> Lapače snů -->
      <xsl:when test="$google_id = '7177'">3766</xsl:when><!-- Čelní desky k poštovním schránkám -> Poštovní schránky -->
      <xsl:when test="$google_id = '7182'">4206</xsl:when><!-- Karty rozhraní USB -> AC adaptéry -->
      <xsl:when test="$google_id = '7184'">1717</xsl:when><!-- Zahradní pracovní stoly -> Zahradní stoly -->
      <xsl:when test="$google_id = '7186'">1644</xsl:when><!-- Spermicidní přípravky -> Zpevňující přípravky -->
      <xsl:when test="$google_id = '7197'">5568</xsl:when><!-- Závěsná křesla -> Závěsná křesla -->
      <xsl:when test="$google_id = '7202'">3124</xsl:when><!-- Příslušenství k dětským vozítkům -> Příslušenství pro vozítka -->
      <xsl:when test="$google_id = '7206'">2897</xsl:when><!-- Dekorativní zvonky -> Domovní zvonky -->
      <xsl:when test="$google_id = '7224'">1144</xsl:when><!-- Vaky na lyže a snowboardy -> Vaky na snowboardy -->
      <xsl:when test="$google_id = '7225'">5015</xsl:when><!-- Disky pro obnovení systému -> CAD software -->
      <xsl:when test="$google_id = '7231'">2015</xsl:when><!-- Tlumítka činelů a bubnů -> Příslušenství pro bicí -->
      <xsl:when test="$google_id = '7236'">5936</xsl:when><!-- Kuchařské kalhoty -> Těhotenské kalhoty -->
      <xsl:when test="$google_id = '7237'">3151</xsl:when><!-- Kuchařské čepice -> Dětské čepice -->
      <xsl:when test="$google_id = '7250'">2919</xsl:when><!-- Panovy flétny a dudy -> Panovy flétny -->
      <xsl:when test="$google_id = '7256'">5624</xsl:when><!-- Lepidla na umělé řasy -> Lepidla na umělé řasy -->
      <xsl:when test="$google_id = '7274'">6654</xsl:when><!-- Boudy a výběhy pro psy -> Boudy pro psy -->
      <xsl:when test="$google_id = '7275'">3933</xsl:when><!-- Elektromotory -> Elektroměry -->
      <xsl:when test="$google_id = '7278'">2968</xsl:when><!-- Sponky na noty -> Stojany na noty -->
      <xsl:when test="$google_id = '7279'">2968</xsl:when><!-- Obaly pro stojany na noty -> Stojany na noty -->
      <xsl:when test="$google_id = '7280'">2968</xsl:when><!-- Lampičky pro stojany na noty -> Stojany na noty -->
      <xsl:when test="$google_id = '7283'">2015</xsl:when><!-- Vaky a obaly na ruční perkuse -> Příslušenství pro bicí -->
      <xsl:when test="$google_id = '7284'">2015</xsl:when><!-- Stojany a držáky na ruční perkuse -> Příslušenství pro bicí -->
      <xsl:when test="$google_id = '7297'">8327</xsl:when><!-- Cajony -> Cajony -->
      <xsl:when test="$google_id = '7300'">1533</xsl:when><!-- Rámové bubny -> Jednotlivé bubny -->
      <xsl:when test="$google_id = '7308'">2015</xsl:when><!-- Stojany na perkuse -> Příslušenství pro bicí -->
      <xsl:when test="$google_id = '7310'">6790</xsl:when><!-- Venkovní skladovací boxy -> Dětský zahradní nábytek -->
      <xsl:when test="$google_id = '7330'">3729</xsl:when><!-- Univerzální čisticí prostředky -> Univerzální čisticí prostředky -->
      <xsl:when test="$google_id = '7338'">5788</xsl:when><!-- Stojany na lampy -> Stojací lampy -->
      <xsl:when test="$google_id = '7339'">3766</xsl:when><!-- Náhradní dvířka k poštovním schránkám -> Poštovní schránky -->
      <xsl:when test="$google_id = '7347'">4249</xsl:when><!-- Náhradní díly pro mobilní telefony -> Náhradní mikrofony pro mobilní telefony -->
      <xsl:when test="$google_id = '7357'">2016</xsl:when><!-- Obaly a kufry na klávesnice -> Příslušenství pro klávesové nástroje -->
      <xsl:when test="$google_id = '7360'">2139</xsl:when><!-- Dudlíky -> Dudlíky -->
      <xsl:when test="$google_id = '7363'">1793</xsl:when><!-- Sady péče o kontaktní čočky -> Kontaktní čočky -->
      <xsl:when test="$google_id = '7396'">2668</xsl:when><!-- Krém proti slunci pro domácí zvířata -> Krmiva pro terarijní zvířata -->
      <xsl:when test="$google_id = '7398'">8334</xsl:when><!-- Prolézačky pro ptáky -> Přepravky pro ptáky -->
      <xsl:when test="$google_id = '7400'">2619</xsl:when><!-- Zahradní lampy -> Zahradní lampy -->
      <xsl:when test="$google_id = '7401'">5551</xsl:when><!-- Přízemní osvětlení -> Vánoční osvětlení -->
      <xsl:when test="$google_id = '7406'">6302</xsl:when><!-- Pohlcovače vlhkosti -> Pohlcovače vlhkosti -->
      <xsl:when test="$google_id = '7422'">2861</xsl:when><!-- Ozdobné hlavice -> Zahradní lavice -->
      <xsl:when test="$google_id = '7427'">4321</xsl:when><!-- Sezamové tyčinky -> Čokoládové tyčinky -->
      <xsl:when test="$google_id = '7445'">4489</xsl:when><!-- Ředidla laků na nehty -> Laky na nehty -->
      <xsl:when test="$google_id = '7455'">2015</xsl:when><!-- Bicí zvukové moduly -> Příslušenství pro bicí -->
      <xsl:when test="$google_id = '7461'">6434</xsl:when><!-- Lovecké a střelecké rukavice -> Army a lovecké rukavice -->
      <xsl:when test="$google_id = '7467'">1763</xsl:when><!-- Sady na čištění pleti -> Přípravky na čištění pleti -->
      <xsl:when test="$google_id = '7471'">6960</xsl:when><!-- Nálepky a obtisky na hodinky -> Kazety a stojany na hodinky -->
      <xsl:when test="$google_id = '7490'">4488</xsl:when><!-- Brusky na nehty -> Brusky na nehty -->
      <xsl:when test="$google_id = '7493'">5624</xsl:when><!-- Aplikátory na umělé řasy -> Lepidla na umělé řasy -->
      <xsl:when test="$google_id = '7521'">5222</xsl:when><!-- Obaly na batohy -> Pláštěnky na batohy -->
      <xsl:when test="$google_id = '7527'">1038</xsl:when><!-- Ruční ventilátory -> Domácí ventilátory -->
      <xsl:when test="$google_id = '7539'">987</xsl:when><!-- Sáňky -> Stany -->
      <xsl:when test="$google_id = '7550'">4678</xsl:when><!-- Kalíšky na vajíčka -> Kráječe na vajíčka -->
      <xsl:when test="$google_id = '7556'">5996</xsl:when><!-- Mazací pistole -> Mazací lisy a pistole -->
      <xsl:when test="$google_id = '7563'">4200</xsl:when><!-- Nůžky na trávu – příslušenství -> Brusky - příslušenství -->
      <xsl:when test="$google_id = '7568'">1199</xsl:when><!-- Pivní sklenice -> Sklenice -->
      <xsl:when test="$google_id = '8021'">1731</xsl:when><!-- Papírové a magnetické panenky -> Domečky pro panenky -->
      <xsl:when test="$google_id = '8022'">5015</xsl:when><!-- Šablony dokumentů -> CAD software -->
      <xsl:when test="$google_id = '8029'">1754</xsl:when><!-- Instantní pleťové masky -> Pleťové masky -->
      <xsl:when test="$google_id = '8042'">6247</xsl:when><!-- Závěsy a záclony – příslušenství -> Tampery a příslušenství -->
      <xsl:when test="$google_id = '8043'">3676</xsl:when><!-- Čističe látek a čalounění -> Čisticí prostředky na koberce a čalounění -->
      <xsl:when test="$google_id = '8046'">6619</xsl:when><!-- Závaží a svorky na ubrusy -> Závaží a spony na ubrusy -->
      <xsl:when test="$google_id = '8047'">811</xsl:when><!-- Obaly na stojany pro reproduktory -> Stojany a držáky na reproduktory -->
      <xsl:when test="$google_id = '8049'">811</xsl:when><!-- Stojany a držáky pro reproduktory -> Stojany a držáky na reproduktory -->
      <xsl:when test="$google_id = '8061'">3135</xsl:when><!-- Cyklistické chrániče -> Cyklistické chrániče -->
      <xsl:when test="$google_id = '8065'">4905</xsl:when><!-- Krycí potahy na kulečníkové stoly -> Kulečníkové stoly -->
      <xsl:when test="$google_id = '8066'">1322</xsl:when><!-- Vibrační posilovací stroje -> Posilovací stroje -->
      <xsl:when test="$google_id = '8074'">1365</xsl:when><!-- Vosky na lyže a snowboardy -> Vosky na snowboard -->
      <xsl:when test="$google_id = '8075'">2635</xsl:when><!-- Povlaky na kojicí polštáře -> Těhotenské a kojící polštáře -->
      <xsl:when test="$google_id = '8087'">1955</xsl:when><!-- Příslušenství k digestořím -> Příslušenství k digestořím -->
      <xsl:when test="$google_id = '8090'">6445</xsl:when><!-- Nástěnné ventilátory -> Stropní ventilátory -->
      <xsl:when test="$google_id = '8122'">3077</xsl:when><!-- Menstruační kalíšky -> Menstruační kalíšky -->
      <xsl:when test="$google_id = '8132'">8567</xsl:when><!-- Hlavice na kartáčky na čištění pleti -> Kartáčky a houbičky na čištění pleti -->
      <xsl:when test="$google_id = '8145'">3336</xsl:when><!-- Krytky na tažná zařízení -> Tažná zařízení -->
      <xsl:when test="$google_id = '8160'">4207</xsl:when><!-- Digitizéry na displeje notebooků -> Baterie k notebookům -->
      <xsl:when test="$google_id = '8217'">5886</xsl:when><!-- Podkladové báze na rty -> Podkladové báze na rty -->
      <xsl:when test="$google_id = '8218'">5886</xsl:when><!-- Podkladové báze na tvář -> Podkladové báze na rty -->
      <xsl:when test="$google_id = '8219'">5886</xsl:when><!-- Podkladové báze na řasy -> Podkladové báze na rty -->
      <xsl:when test="$google_id = '8220'">6404</xsl:when><!-- Podkladové přípravky na oční víčka -> Make-upy -->
      <xsl:when test="$google_id = '8228'">3336</xsl:when><!-- Tažná zařízení -> Tažná zařízení -->
      <xsl:when test="$google_id = '8271'">707</xsl:when><!-- Cívkové magnetofony -> Radiomagnetofony -->
      <xsl:when test="$google_id = '8275'">4201</xsl:when><!-- Stojany na vrtačku -> Příslušenství k vrtačkám -->
      <xsl:when test="$google_id = '8276'">4201</xsl:when><!-- Sklíčidla pro vrtačky -> Příslušenství k vrtačkám -->
      <xsl:when test="$google_id = '8306'">5553</xsl:when><!-- Plachty na golfová vozítka -> Plachty na auto -->
      <xsl:when test="$google_id = '8308'">5553</xsl:when><!-- Plachty na valníková vozidla -> Plachty na auto -->
      <xsl:when test="$google_id = '8310'">5553</xsl:when><!-- Plachty pro skladování automobilů -> Plachty na auto -->
      <xsl:when test="$google_id = '8311'">5553</xsl:when><!-- Plachty pro skladování rekreačních vozidel -> Plachty na auto -->
      <xsl:when test="$google_id = '8312'">5553</xsl:when><!-- Plachty pro skladování lodí -> Plachty na auto -->
      <xsl:when test="$google_id = '8313'">5553</xsl:when><!-- Plachty pro skladování motocyklů -> Plachty na auto -->
      <xsl:when test="$google_id = '8314'">5553</xsl:when><!-- Plachty pro skladování golfových vozíků -> Plachty na auto -->
      <xsl:when test="$google_id = '8316'">5553</xsl:when><!-- Ochranné kryty na čelní skla vozidel -> Plachty na auto -->
      <xsl:when test="$google_id = '8450'">8608</xsl:when><!-- Autolaky -> Autolaky -->
      <xsl:when test="$google_id = '8473'">5948</xsl:when><!-- Námořní reproduktory -> Bluetooth reproduktory -->
      <xsl:when test="$google_id = '43616'">4248</xsl:when><!-- Náhradní reproduktory k televizím -> Náhradní reproduktory pro mobilní telefony -->
      <xsl:when test="$google_id = '43617'">8609</xsl:when><!-- Náhradní reproduktory k notebookům -> Náhradní ventilátory pro notebooky -->
      <xsl:when test="$google_id = '232167'">2808</xsl:when><!-- Ozdobné štítky klíčových dírek na skřínky a nábytek -> Nábytkové kování -->
      <xsl:when test="$google_id = '298420'">665</xsl:when><!-- Digitální stěny k fotoaparátům -> Digitální fotoaparáty -->
      <xsl:when test="$google_id = '326120'">7020</xsl:when><!-- Návleky na bezpečnostní pásy vozidel -> Návleky na bezpečnostní pásy -->
      <xsl:when test="$google_id = '499685'">1000</xsl:when><!-- Lanka pro jízdní kola -> Jízdní kola -->
      <xsl:when test="$google_id = '499688'">2007</xsl:when><!-- Popruhy ke kytarám -> Příslušenství ke kytarám -->
      <xsl:when test="$google_id = '499691'">6629</xsl:when><!-- Stojany na zavazadla -> Váhy na zavazadla -->
      <xsl:when test="$google_id = '499709'">5146</xsl:when><!-- Vodítka pro koně -> Udidla pro koně -->
      <xsl:when test="$google_id = '499722'">8604</xsl:when><!-- Chrániče hlavy na box a bojové sporty -> Chrániče kolen pro bojové sporty -->
      <xsl:when test="$google_id = '499723'">8601</xsl:when><!-- Chrániče těla na box a bojové sporty -> Chrániče na tělo pro bojové sporty -->
      <xsl:when test="$google_id = '499725'">8603</xsl:when><!-- Chrániče rukou a předloktí na box a bojové sporty -> Chrániče loktů pro bojové sporty -->
      <xsl:when test="$google_id = '499729'">5630</xsl:when><!-- Kapitánské pásky -> Kapitánské pásky -->
      <xsl:when test="$google_id = '499756'">1112</xsl:when><!-- Hokejové chrániče loktů -> Hokejové chrániče loktů -->
      <xsl:when test="$google_id = '499760'">1147</xsl:when><!-- Díly na kolečkové brusle -> Kolečkové brusle -->
      <xsl:when test="$google_id = '499779'">3900</xsl:when><!-- Figuríny a sledy na americký fotbal -> Doplňky na americký fotbal -->
      <xsl:when test="$google_id = '499785'">1143</xsl:when><!-- Míče na házenou -> Míče na házenou -->
      <xsl:when test="$google_id = '499789'">5082</xsl:when><!-- Volejbalové chrániče kolen -> Volejbalové chrániče -->
      <xsl:when test="$google_id = '499794'">2494</xsl:when><!-- Objímky pro činky -> Bezpečnostní objímky pro činky -->
      <xsl:when test="$google_id = '499795'">1321</xsl:when><!-- Posilovací lavice -> Posilovací lavice -->
      <xsl:when test="$google_id = '499801'">6675</xsl:when><!-- Sportovní chrániče zubů -> Hokejové chrániče zubů -->
      <xsl:when test="$google_id = '499804'">5557</xsl:when><!-- Háčky na vánoční stromek -> Vánoční stromky -->
      <xsl:when test="$google_id = '499816'">5629</xsl:when><!-- Horolezecké rukavice -> Horolezecké rukavice -->
      <xsl:when test="$google_id = '499826'">4908</xsl:when><!-- Luky a kuše – příslušenství -> Kulečníkové příslušenství -->
      <xsl:when test="$google_id = '499847'">8517</xsl:when><!-- Míčky na pickleball -> Míčky na pickleball -->
      <xsl:when test="$google_id = '499848'">8517</xsl:when><!-- Pálky na pickleball -> Míčky na pickleball -->
      <xsl:when test="$google_id = '499865'">6247</xsl:when><!-- Trezory – příslušenství -> Tampery a příslušenství -->
      <xsl:when test="$google_id = '499868'">1000</xsl:when><!-- Sady na jízdní kola -> Jízdní kola -->
      <xsl:when test="$google_id = '499876'">3646</xsl:when><!-- Spárovací hmoty -> Spárovací hmoty -->
      <xsl:when test="$google_id = '499900'">3120</xsl:when><!-- Plenky pro psy -> Pamlsky pro psy -->
      <xsl:when test="$google_id = '499907'">3582</xsl:when><!-- Markýzy -> Markýzy -->
      <xsl:when test="$google_id = '499912'">1357</xsl:when><!-- Posilovací věže -> Posilovací věže -->
      <xsl:when test="$google_id = '499927'">5562</xsl:when><!-- Svářečské kukly -> Svářečské kukly -->
      <xsl:when test="$google_id = '499930'">6822</xsl:when><!-- Háčky a věšáky na žehlicí prkna -> Potahy na žehlicí prkna -->
      <xsl:when test="$google_id = '499975'">1110</xsl:when><!-- Hokejové šle a pásky -> Hokejové tašky -->
      <xsl:when test="$google_id = '499985'">5847</xsl:when><!-- Panelové pily -> Pásové pily -->
      <xsl:when test="$google_id = '500000'">2997</xsl:when><!-- Sady koupelnového nábytku -> Koupelnový nábytek -->
      <xsl:when test="$google_id = '500002'">4939</xsl:when><!-- Chytré brýle -> Chytré brýle -->
      <xsl:when test="$google_id = '500003'">5551</xsl:when><!-- Plovoucí osvětlení -> Vánoční osvětlení -->
      <xsl:when test="$google_id = '500016'">4980</xsl:when><!-- Zametací kartáčové stroje -> Zametací stroje -->
      <xsl:when test="$google_id = '500029'">5232</xsl:when><!-- Kolečkové lyže -> Kolečkové lyže -->
      <xsl:when test="$google_id = '500038'">7001</xsl:when><!-- Potřeby pro čištění akvárií -> Potřeby na čištění akvárií -->
      <xsl:when test="$google_id = '500046'">5015</xsl:when><!-- Digitální výtvarná díla -> CAD software -->
      <xsl:when test="$google_id = '500055'">3267</xsl:when><!-- Závitové tyče -> Závitové tyče -->
      <xsl:when test="$google_id = '500063'">1564</xsl:when><!-- Expanzní nádoby pro ohřívače vody -> Bojlery a ohřívače vody -->
      <xsl:when test="$google_id = '500065'">3672</xsl:when><!-- Odstraňovače vodního kamene -> Odstraňovače vodního kamene -->
      <xsl:when test="$google_id = '500066'">947</xsl:when><!-- Příslušenství pro rychlovarné konvice -> Rychlovarné konvice -->
      <xsl:when test="$google_id = '500076'">4362</xsl:when><!-- Nakládané ovoce a zelenina -> Mražené ovoce a zelenina -->
      <xsl:when test="$google_id = '500081'">4850</xsl:when><!-- Ultrazvukové čističky -> Ultrazvukové čističky -->
      <xsl:when test="$google_id = '500085'">6035</xsl:when><!-- Příslušenství k pračkám a sušičkám -> Příslušenství k pračkám a sušičkám -->
      <xsl:when test="$google_id = '500097'">1151</xsl:when><!-- Čerpadla pro zavlažovače a postřikovače a pomocná čerpadla -> Čerpadla -->
      <xsl:when test="$google_id = '500098'">1151</xsl:when><!-- Čerpadla pro bazény, fontány a rybníčky -> Čerpadla -->
      <xsl:when test="$google_id = '500099'">1151</xsl:when><!-- Čerpadla pro domácí spotřebiče -> Čerpadla -->
      <xsl:when test="$google_id = '500100'">1151</xsl:when><!-- Domácí vodárny -> Čerpadla -->
      <xsl:when test="$google_id = '500101'">1151</xsl:when><!-- Ostatní čerpadla -> Čerpadla -->
      <xsl:when test="$google_id = '500102'">1151</xsl:when><!-- Čerpadla pro jímky a odpady -> Čerpadla -->
      <xsl:when test="$google_id = '500103'">2882</xsl:when><!-- Vložky do organizérů na nářadí -> Kufry a organizéry na nářadí -->
      <xsl:when test="$google_id = '500111'">6790</xsl:when><!-- Prvky sestav zahradních pohovek -> Dětský zahradní nábytek -->
      <xsl:when test="$google_id = '500112'">811</xsl:when><!-- Pouzdra, kryty a tašky na reproduktory -> Stojany a držáky na reproduktory -->
      <xsl:when test="$google_id = '500120'">5949</xsl:when><!-- Sady a součásti reproduktorů -> Sloupové reproduktory -->
      <xsl:when test="$google_id = '502978'">6802</xsl:when><!-- Vázací dráty -> Svářecí dráty -->
      <xsl:when test="$google_id = '502987'">5939</xsl:when><!-- Těhotenské a podpůrné pásy -> Těhotenské pásy -->
      <xsl:when test="$google_id = '503000'">6348</xsl:when><!-- Přesýpací hodiny -> Přesýpací hodiny -->
      <xsl:when test="$google_id = '503003'">763</xsl:when><!-- Klávesy do klávesnic -> Klávesnice -->
      <xsl:when test="$google_id = '503004'">8545</xsl:when><!-- Náušníky ke sluchátkům -> Náušníky a špunty pro sluchátka -->
      <xsl:when test="$google_id = '503005'">3359</xsl:when><!-- Trychtýře -> Trychtýře -->
      <xsl:when test="$google_id = '503034'">2021</xsl:when><!-- Struny pro koncertní smyčcové nástroje -> Pouzdra na smyčcové nástroje -->
      <xsl:when test="$google_id = '503035'">2021</xsl:when><!-- Stojany na koncertní smyčcové nástroje -> Pouzdra na smyčcové nástroje -->
      <xsl:when test="$google_id = '503036'">2021</xsl:when><!-- Snímače pro koncertní smyčcové nástroje -> Pouzdra na smyčcové nástroje -->
      <xsl:when test="$google_id = '503037'">2021</xsl:when><!-- Dusítka na koncertní smyčcové nástroje -> Pouzdra na smyčcové nástroje -->
      <xsl:when test="$google_id = '503039'">2021</xsl:when><!-- Pouzdra na koncertní smyčcové nástroje -> Pouzdra na smyčcové nástroje -->
      <xsl:when test="$google_id = '503734'">3853</xsl:when><!-- Cukr a sladidla -> Sladidla -->
      <xsl:when test="$google_id = '503748'">1550</xsl:when><!-- Pouzdra na zobcové flétny -> Zobcové flétny -->
      <xsl:when test="$google_id = '503749'">2017</xsl:when><!-- Péče o zobcové flétny a čištění -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '503750'">2017</xsl:when><!-- Náhradní díly k zobcovým flétnám -> Příslušenství pro dechové nástroje -->
      <xsl:when test="$google_id = '503755'">2167</xsl:when><!-- Riser karty -> Střihové karty -->
      <xsl:when test="$google_id = '503762'">2434</xsl:when><!-- Chrániče a vložky do podprsenky -> Vložky do podprsenky -->
      <xsl:when test="$google_id = '503772'">2700</xsl:when><!-- Navijáky -> Navijáky -->
      <xsl:when test="$google_id = '503774'">2336</xsl:when><!-- Zapalovače a zápalky -> Zapalovače -->
      <xsl:when test="$google_id = '505304'">8432</xsl:when><!-- Držáky plenek pro psy -> Klece pro psy -->
      <xsl:when test="$google_id = '505310'">2021</xsl:when><!-- Pouzdra a koncertní tašky k žesťovým nástrojům -> Pouzdra na smyčcové nástroje -->
      <xsl:when test="$google_id = '505365'">2014</xsl:when><!-- Metronomy -> Metronomy -->
      <xsl:when test="$google_id = '505366'">2703</xsl:when><!-- Příslušenství k odsávačkám mateřského mléka -> Odsávačky mateřského mléka -->
      <xsl:when test="$google_id = '505412'">4067</xsl:when><!-- Stuhy a lemovky -> Prýmky, stuhy, mašle, lemovky -->
      <xsl:when test="$google_id = '505669'">2199</xsl:when><!-- Parní inhalátory -> Inhalátory -->
      <xsl:when test="$google_id = '505761'">5877</xsl:when><!-- Absint -> Absinthy -->
      <xsl:when test="$google_id = '505769'">1546</xsl:when><!-- Altové a barytonové lesní rohy -> Lesní rohy -->
      <xsl:when test="$google_id = '505770'">3080</xsl:when><!-- Trubky a kornety -> Kornety -->
      <xsl:when test="$google_id = '543512'">731</xsl:when><!-- Předplacené mobilní telefony -> Mobilní telefony -->
      <xsl:when test="$google_id = '543513'">731</xsl:when><!-- Mobilní telefony s tarifem -> Mobilní telefony -->
      <xsl:when test="$google_id = '543514'">731</xsl:when><!-- Odemčené mobilní telefony -> Mobilní telefony -->
      <xsl:when test="$google_id = '543515'">731</xsl:when><!-- Předplacené karty do mobilních telefonů -> Mobilní telefony -->
      <xsl:when test="$google_id = '543517'">927</xsl:when><!-- Grafové kalkulačky -> Kalkulačky -->
      <xsl:when test="$google_id = '543518'">927</xsl:when><!-- Základní kalkulačky -> Kalkulačky -->
      <xsl:when test="$google_id = '543519'">927</xsl:when><!-- Finanční kalkulačky -> Kalkulačky -->
      <xsl:when test="$google_id = '543520'">927</xsl:when><!-- Vědecké kalkulačky -> Kalkulačky -->
      <xsl:when test="$google_id = '543521'">927</xsl:when><!-- Kalkulačky pro stavebnictví -> Kalkulačky -->
      <xsl:when test="$google_id = '543537'">6932</xsl:when><!-- Mražené koktejlové směsi -> Kořenící směsi -->
      <xsl:when test="$google_id = '543541'">1469</xsl:when><!-- Zvukové knihy -> Knihy -->
      <xsl:when test="$google_id = '543542'">3006</xsl:when><!-- Elektronické knihy -> E-book elektronické knihy -->
      <xsl:when test="$google_id = '543543'">1469</xsl:when><!-- Tištěné knihy -> Knihy -->
      <xsl:when test="$google_id = '543573'">5883</xsl:when><!-- Balzám na rty -> Balzámy na rty -->
      <xsl:when test="$google_id = '543586'">3156</xsl:when><!-- Šátky -> Šátky -->
      <xsl:when test="$google_id = '543587'">3405</xsl:when><!-- Šátky na péči o vlasy -> Příčesky do vlasů -->
      <xsl:when test="$google_id = '543588'">813</xsl:when><!-- Joysticky -> Joysticky -->
      <xsl:when test="$google_id = '543589'">812</xsl:when><!-- Gamepady -> Gamepady -->
      <xsl:when test="$google_id = '543590'">869</xsl:when><!-- Dálkové herní ovladače -> Dálkové ovladače -->
      <xsl:when test="$google_id = '543591'">814</xsl:when><!-- Herní volanty -> Volanty -->
      <xsl:when test="$google_id = '543598'">1636</xsl:when><!-- Deodorant -> Deodoranty a antiperspiranty -->
      <xsl:when test="$google_id = '543599'">1636</xsl:when><!-- Antiperspirant -> Deodoranty a antiperspiranty -->
      <xsl:when test="$google_id = '543608'">1875</xsl:when><!-- Popisovače -> Popisovače -->
      <xsl:when test="$google_id = '543609'">1876</xsl:when><!-- Zvýrazňovače -> Zvýrazňovače -->
      <xsl:when test="$google_id = '543610'">8462</xsl:when><!-- Fitness schody -> Fitness schody -->
      <xsl:when test="$google_id = '543611'">4978</xsl:when><!-- Schody na cvičení -> Podložky na cvičení -->
      <xsl:when test="$google_id = '543612'">2376</xsl:when><!-- Podložky na hraní -> Hrací podložky -->
      <xsl:when test="$google_id = '543613'">2376</xsl:when><!-- Konstrukce na hraní -> Hrací podložky -->
      <xsl:when test="$google_id = '543615'">1627</xsl:when><!-- Šampon -> Šampony -->
      <xsl:when test="$google_id = '543626'">709</xsl:when><!-- Sluchátka -> Sluchátka -->
      <xsl:when test="$google_id = '543628'">2333</xsl:when><!-- Modelína -> Modelíny -->
      <xsl:when test="$google_id = '543638'">4075</xsl:when><!-- Náprstky na šití -> Kazety na šití -->
      <xsl:when test="$google_id = '543639'">4075</xsl:when><!-- Kryty dlaně na šití -> Kazety na šití -->
      <xsl:when test="$google_id = '543645'">3366</xsl:when><!-- Skřipce do vlasů -> Skřipce do vlasů -->
      <xsl:when test="$google_id = '543646'">3369</xsl:when><!-- Sponky do vlasů -> Spony do vlasů -->
      <xsl:when test="$google_id = '543647'">2081</xsl:when><!-- Registrační pokladny -> Elektronické registrační pokladny -->
      <xsl:when test="$google_id = '543648'">2106</xsl:when><!-- Prodejní terminály -> Pokladní terminály -->
      <xsl:when test="$google_id = '543651'">2128</xsl:when><!-- Müsli tyčinky -> Müsli tyčinky -->
      <xsl:when test="$google_id = '543652'">4321</xsl:when><!-- Granolové tyčinky -> Čokoládové tyčinky -->
      <xsl:when test="$google_id = '543659'">1806</xsl:when><!-- Adstringentní vody -> Ústní vody -->
      <xsl:when test="$google_id = '543664'">4807</xsl:when><!-- Dětské dečky -> Dětské deky -->
      <xsl:when test="$google_id = '543665'">2443</xsl:when><!-- Zavinovací přikrývky -> Zavinovačky -->
      <xsl:when test="$google_id = '543673'">3155</xsl:when><!-- Šály -> Šály -->
      <xsl:when test="$google_id = '543674'">3156</xsl:when><!-- Velké šátky -> Šátky -->
      <xsl:otherwise/><!-- brak odpowiednika w taksonomii Heureka -->
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
