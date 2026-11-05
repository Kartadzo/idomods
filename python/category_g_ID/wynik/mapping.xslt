<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <xsl:variable name="cat_id" select="category_idosell/@id"/>
    <xsl:choose>
      <xsl:when test="$cat_id = '4390'">
        <xsl:value-of select='110' />
      </xsl:when>
      <xsl:when test="$cat_id = '2016'">
        <xsl:value-of select='1239' />
      </xsl:when>
      <xsl:when test="$cat_id = '2111'">
        <xsl:value-of select='1261' />
      </xsl:when>
      <xsl:when test="$cat_id = '1'">
        <xsl:value-of select='141' />
      </xsl:when>
      <xsl:when test="$cat_id = '16'">
        <xsl:value-of select='143' />
      </xsl:when>
      <xsl:when test="$cat_id = '1723'">
        <xsl:value-of select='1763' />
      </xsl:when>
      <xsl:when test="$cat_id = '2'">
        <xsl:value-of select='2096' />
      </xsl:when>
      <xsl:when test="$cat_id = '1612'">
        <xsl:value-of select='222' />
      </xsl:when>
      <xsl:when test="$cat_id = '1809'">
        <xsl:value-of select='234' />
      </xsl:when>
      <xsl:when test="$cat_id = '1751'">
        <xsl:value-of select='275' />
      </xsl:when>
      <xsl:when test="$cat_id = '3'">
        <xsl:value-of select='2911' />
      </xsl:when>
      <xsl:when test="$cat_id = '1792'">
        <xsl:value-of select='3306' />
      </xsl:when>
      <xsl:when test="$cat_id = '2881'">
        <xsl:value-of select='4714' />
      </xsl:when>
      <xsl:when test="$cat_id = '33'">
        <xsl:value-of select='499998' />
      </xsl:when>
      <xsl:when test="$cat_id = '6055'">
        <xsl:value-of select='505771' />
      </xsl:when>
      <xsl:when test="$cat_id = '4'">
        <xsl:value-of select='5588' />
      </xsl:when>
      <xsl:when test="$cat_id = '547'">
        <xsl:value-of select='618' />
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>No match</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>