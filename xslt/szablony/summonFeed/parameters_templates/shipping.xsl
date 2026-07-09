<xsl:element name="g:shipping">
  <xsl:element name="g:price">
    <xsl:choose>
      <xsl:when test="price/@gross >= $kwota_dla_darmowej_dostawy">
        <xsl:text><![CDATA[0]]></xsl:text>
      </xsl:when>
      <xsl:when test="$kwota_dla_wiekszych_zamowien != '' and price/@gross >= $kwota_dla_wiekszych_zamowien">
        <xsl:value-of select="$Koszt_dostawy_wiekszych_zamowien" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$Koszt_dostawy" />
      </xsl:otherwise>
    </xsl:choose>
    <xsl:text><![CDATA[ ]]></xsl:text>
    <xsl:value-of select="$product_currency" />
  </xsl:element>
  <xsl:element name="g:country">
    <xsl:value-of select="$Kraj_dostawy" />
  </xsl:element>
  <xsl:element name="g:min_handling_time">
    <xsl:value-of select="$Czas_obsługi_zamówienia_na_magazynie" />
  </xsl:element>
  <xsl:element name="g:max_handling_time">
    <xsl:value-of select="$Czas_obsługi_zamówienia_na_magazynie + ceiling(($Czas_obsługi_zamówienia_na_magazynie + 1) div 3)" />
  </xsl:element>
  <xsl:element name="g:min_transit_time">
    <xsl:value-of select="$Czas_dostawy_zamówienia" />
  </xsl:element>
  <xsl:element name="g:max_transit_time">
    <xsl:value-of select="$Czas_dostawy_zamówienia + ceiling(($Czas_dostawy_zamówienia + 1) div 3)" />
  </xsl:element>
  <xsl:element name="g:service">
    <xsl:value-of select="$Serwis_dostawy_zamówienia" />
  </xsl:element>
</xsl:element>