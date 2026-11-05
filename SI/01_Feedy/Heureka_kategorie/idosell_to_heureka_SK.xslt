<?xml version="1.0" encoding="UTF-8"?>
<!--
  Mapowanie: ID kategorii sklepu IdoSell -> ID kategorii Heureka (SK)
  Plik wygenerowany skryptem app.py. Nie edytować ręcznie.
  Wpisów: 46 z 205 kategorii źródłowych.
  Metody dopasowania: fuzzy_high: 14, fuzzy_review: 18, nazwa_przodka: 14.
  Szczegóły i wpisy do przeglądu: patrz raport CSV obok tego pliku.

  Użycie:
    <xsl:call-template name="category-to-heureka">
      <xsl:with-param name="category_id" select="..."/>
    </xsl:call-template>
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template name="category-to-heureka">
    <xsl:param name="category_id"/>
    <xsl:choose>
      <xsl:when test="$category_id = '1214553968'">2863</xsl:when><!-- Hojdačka Bocianie hniezdo -> Záhradné hojdačky -->
      <xsl:when test="$category_id = '1214553984'">2493</xsl:when><!-- Závažia a činky -> Závažia k činkám -->
      <xsl:when test="$category_id = '1214553985'">8449</xsl:when><!-- Hula Hop -> Hula hoop -->
      <xsl:when test="$category_id = '1214553988'">4978</xsl:when><!-- Podložky na cvičenie -> Podložky na cvičenie -->
      <xsl:when test="$category_id = '1214553991'">8483</xsl:when><!-- Tréningové kužele -> Tréningové méty a kužele -->
      <xsl:when test="$category_id = '1214553997'">4886</xsl:when><!-- Švihadlá -> Švihadlá -->
      <xsl:when test="$category_id = '1214553998'">2476</xsl:when><!-- Step mostíky -> Step mostíky -->
      <xsl:when test="$category_id = '1214554011'">1024</xsl:when><!-- Masážne pištole -> Masážne prístroje -->
      <xsl:when test="$category_id = '1214554012'">1024</xsl:when><!-- Masážne prístroje na krk -> Masážne prístroje -->
      <xsl:when test="$category_id = '1214554015'">1137</xsl:when><!-- Jednotlivé loptičky -> Golfové loptičky -->
      <xsl:when test="$category_id = '1214554027'">5303</xsl:when><!-- Kettlebell -> Kettlebell -->
      <xsl:when test="$category_id = '1214554028'">1319</xsl:when><!-- Činky -> Činky -->
      <xsl:when test="$category_id = '1214554035'">8448</xsl:when><!-- Gymnastické kruhy -> Gymnastické kruhy -->
      <xsl:when test="$category_id = '1214554073'">1024</xsl:when><!-- Lymfodrenážne prístroje -> Masážne prístroje -->
      <xsl:when test="$category_id = '1214554075'">1401</xsl:when><!-- Elektrostimulačné zariadenia -> Istiace zariadenia -->
      <xsl:when test="$category_id = '1214554084'">5420</xsl:when><!-- Podložky na jogu -> Popruhy na jogu -->
      <xsl:when test="$category_id = '1214554085'">5420</xsl:when><!-- Popruhy na jogu -> Popruhy na jogu -->
      <xsl:when test="$category_id = '1214554086'">5420</xsl:when><!-- Obruče na jogu -> Popruhy na jogu -->
      <xsl:when test="$category_id = '1214554152'">2378</xsl:when><!-- Čelovky -> Čelovky -->
      <xsl:when test="$category_id = '1214554163'">1024</xsl:when><!-- Masážne prístroje na ruky -> Masážne prístroje -->
      <xsl:when test="$category_id = '1214554165'">1317</xsl:when><!-- Elektrické bežecké pásy -> Bežecké pásy -->
      <xsl:when test="$category_id = '1214554171'">5993</xsl:when><!-- Otužovacie vane -> Umývacie stoly a vane -->
      <xsl:when test="$category_id = '1214554178'">1051</xsl:when><!-- Senzorické deky -> Elektrické deky -->
      <xsl:when test="$category_id = '1214554180'">1024</xsl:when><!-- Masážne podložky do kresla -> Masážne prístroje -->
      <xsl:when test="$category_id = '1214554187'">1024</xsl:when><!-- Drevené masážne prístroje -> Masážne prístroje -->
      <xsl:when test="$category_id = '1214554189'">1024</xsl:when><!-- Masážne prístroje na krk -> Masážne prístroje -->
      <xsl:when test="$category_id = '1214554196'">5544</xsl:when><!-- Masážne stoličky -> Masážne stoly a stoličky -->
      <xsl:when test="$category_id = '1214554203'">5485</xsl:when><!-- Súpravy masážnych valcov -> Masážne valce -->
      <xsl:when test="$category_id = '1214554204'">5485</xsl:when><!-- Hladké valce -> Masážne valce -->
      <xsl:when test="$category_id = '1214554205'">5485</xsl:when><!-- Valce s hrotmi -> Masážne valce -->
      <xsl:when test="$category_id = '1214554206'">5485</xsl:when><!-- Mini valčeky -> Masážne valce -->
      <xsl:when test="$category_id = '1214554217'">1051</xsl:when><!-- Elektrické vyhrievacie deky -> Elektrické deky -->
      <xsl:when test="$category_id = '1214554228'">2199</xsl:when><!-- Inhalátory -> Inhalátory -->
      <xsl:when test="$category_id = '1214554241'">1024</xsl:when><!-- Masážne prístroje na nohy -> Masážne prístroje -->
      <xsl:when test="$category_id = '1214554247'">4173</xsl:when><!-- Termofory -> Termofory -->
      <xsl:when test="$category_id = '1214554265'">5306</xsl:when><!-- Záťažové vesty -> Záťažové vesty -->
      <xsl:when test="$category_id = '1214554266'">4887</xsl:when><!-- Nastaviteľné stojany na činky -> Stojany na činky -->
      <xsl:when test="$category_id = '1214554274'">1465</xsl:when><!-- Plavecké čiapky -> Plavecké čiapky -->
      <xsl:when test="$category_id = '1214554275'">1440</xsl:when><!-- Plavecké okuliare -> Plavecké okuliare -->
      <xsl:when test="$category_id = '1214554279'">1438</xsl:when><!-- Plavecká obuv -> Topánky do vody -->
      <xsl:when test="$category_id = '1214554281'">2047</xsl:when><!-- Návleky na topánky -> Návleky na topánky -->
      <xsl:when test="$category_id = '1214554291'">8564</xsl:when><!-- Plážový stan -> Plážové stany -->
      <xsl:when test="$category_id = '1214554321'">1024</xsl:when><!-- Vibračné plošiny -> Masážne prístroje -->
      <xsl:when test="$category_id = '1214554328'">1094</xsl:when><!-- Pingpongové stoly -> Stoly na stolný tenis -->
      <xsl:when test="$category_id = '1214554329'">4978</xsl:when><!-- Motýlik na cvičenie -> Podložky na cvičenie -->
      <xsl:when test="$category_id = '1214554331'">4908</xsl:when><!-- Masážne príslušenstvo -> Biliardové príslušenstvo -->
      <xsl:otherwise/><!-- brak odpowiednika w taksonomii Heureka -->
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
