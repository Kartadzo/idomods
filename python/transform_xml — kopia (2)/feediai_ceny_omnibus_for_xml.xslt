<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml"
  version="1.0"
  exclude-result-prefixes="iaiext">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <!-- =========================
       USTAWIENIA (STEROWNIK)
       ========================= -->
  <xsl:param name="currency" select="'PLN'"/>
  <xsl:param name="language" select="'pol'"/>
  <xsl:param name="vatRate" select="23"/>
  <!-- ID magazynu z IdoSell (MUSI odpowiadać magazynowi aktualizowanemu w Downloaderze) -->
  <xsl:param name="stockWarehouseId" select="'0'"/>
  <!-- Multistore/site (zwykle 1) -->
  <xsl:param name="siteId" select="'1'"/>

  <!-- =========================
       POMOCNICZE
       ========================= -->
  <xsl:template name="priceNode">
    <xsl:param name="gross"/>
    <xsl:variable name="g" select="number(translate(normalize-space($gross), ',', '.'))"/>
    <xsl:variable name="net" select="$g div (1 + ($vatRate div 100))"/>
    <price>
      <xsl:attribute name="gross"><xsl:value-of select="format-number($g, '0.00')"/></xsl:attribute>
      <xsl:attribute name="net"><xsl:value-of select="format-number($net, '0.00')"/></xsl:attribute>
    </price>
  </xsl:template>

  <xsl:template name="sizeNameFromSymbol">
    <xsl:param name="sym"/>
    <xsl:choose>
      <xsl:when test="contains($sym, '#')">
        <xsl:value-of select="substring-after($sym, '#')"/>
      </xsl:when>
      <xsl:otherwise>UNI</xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- =========================
       ROOT (IOF 3.0)
       ========================= -->
  <xsl:template match="/">
    <offer xmlns:iof="http://www.iai-shop.com/developers/iof.phtml"
           xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml"
           file_format="IOF" version="3.0">
      <products>
        <xsl:attribute name="currency"><xsl:value-of select="$currency"/></xsl:attribute>
        <xsl:attribute name="language"><xsl:value-of select="$language"/></xsl:attribute>

        <!-- ŹRÓDŁO: /produkty/produkt -->
        <xsl:apply-templates select="/produkty/produkt"/>
      </products>
    </offer>
  </xsl:template>

  <!-- =========================
       PRODUKT (MINIMAL: ID + SIZES(CENA+STAN))
       ========================= -->
  <xsl:template match="produkt">
    <product>
      <!-- Klucz główny produktu -->
      <xsl:attribute name="id"><xsl:value-of select="normalize-space(id)"/></xsl:attribute>

      <!-- Minimalne atrybuty zgodności -->
      <xsl:attribute name="type">regular</xsl:attribute>
      <xsl:attribute name="vat"><xsl:value-of select="format-number($vatRate, '0.0')"/></xsl:attribute>
      <xsl:attribute name="site"><xsl:value-of select="$siteId"/></xsl:attribute>

      <!-- (opcjonalnie, ale często przydatne do diagnostyki/mapowania) -->
      <xsl:attribute name="code_on_card"><xsl:value-of select="normalize-space(symbol)"/></xsl:attribute>

      <!-- CENA bazowa (gdy brak wariantów) -->
      <xsl:variable name="grossBase" select="number(translate(normalize-space(cena_brutto_detal), ',', '.'))"/>

      <sizes>
        <xsl:choose>
          <!-- Są warianty -->
          <xsl:when test="number(normalize-space(ilosc_wariantow)) &gt; 0 and warianty/wariant">
            <xsl:for-each select="warianty/wariant">
              <xsl:variable name="sname">
                <xsl:call-template name="sizeNameFromSymbol">
                  <xsl:with-param name="sym" select="normalize-space(symbol)"/>
                </xsl:call-template>
              </xsl:variable>

              <xsl:variable name="eanVal">
                <xsl:choose>
                  <xsl:when test="normalize-space(ean) != ''">
                    <xsl:value-of select="normalize-space(ean)"/>
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:value-of select="normalize-space(../../ean)"/>
                  </xsl:otherwise>
                </xsl:choose>
              </xsl:variable>

              <size>
                <!-- Klucz wariantu -->
                <xsl:attribute name="id"><xsl:value-of select="normalize-space(id)"/></xsl:attribute>

                <!-- Pomocnicze -->
                <xsl:attribute name="name"><xsl:value-of select="$sname"/></xsl:attribute>
                <xsl:attribute name="panel_name"><xsl:value-of select="$sname"/></xsl:attribute>
                <xsl:attribute name="code"><xsl:value-of select="normalize-space(symbol)"/></xsl:attribute>

                <!-- EAN jako code_producer (opcjonalnie) -->
                <xsl:if test="normalize-space($eanVal) != ''">
                  <xsl:attribute name="code_producer"><xsl:value-of select="$eanVal"/></xsl:attribute>
                </xsl:if>

                <!-- CENA wariantu -->
                <xsl:variable name="grossVar" select="number(translate(normalize-space(cena_brutto_detal), ',', '.'))"/>
                <xsl:call-template name="priceNode">
                  <xsl:with-param name="gross" select="$grossVar"/>
                </xsl:call-template>

                <!-- STAN wariantu -->
                <stock>
                  <xsl:attribute name="id"><xsl:value-of select="$stockWarehouseId"/></xsl:attribute>
                  <xsl:attribute name="quantity"><xsl:value-of select="normalize-space(na_magazynie)"/></xsl:attribute>
                </stock>
              </size>
            </xsl:for-each>
          </xsl:when>

          <!-- Brak wariantów -->
          <xsl:otherwise>
            <size>
              <xsl:attribute name="id"><xsl:value-of select="normalize-space(id)"/></xsl:attribute>
              <xsl:attribute name="name">UNI</xsl:attribute>
              <xsl:attribute name="panel_name">UNI</xsl:attribute>
              <xsl:attribute name="code"><xsl:value-of select="normalize-space(symbol)"/></xsl:attribute>

              <xsl:if test="normalize-space(ean) != ''">
                <xsl:attribute name="code_producer"><xsl:value-of select="normalize-space(ean)"/></xsl:attribute>
              </xsl:if>

              <xsl:call-template name="priceNode">
                <xsl:with-param name="gross" select="$grossBase"/>
              </xsl:call-template>

              <stock>
                <xsl:attribute name="id"><xsl:value-of select="$stockWarehouseId"/></xsl:attribute>
                <xsl:attribute name="quantity"><xsl:value-of select="normalize-space(na_magazynie)"/></xsl:attribute>
              </stock>
            </size>
          </xsl:otherwise>
        </xsl:choose>
      </sizes>
    </product>
  </xsl:template>

</xsl:stylesheet>