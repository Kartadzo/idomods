<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <xsl:variable name="cat_id" select="category_idosell/@id"/>
    <xsl:choose>
      <xsl:when test="$cat_id = '5359'">
        <xsl:value-of select='1529' />
      </xsl:when>
      <xsl:when test="$cat_id = '5088'">
        <xsl:value-of select='1868' />
      </xsl:when>
      <xsl:when test="$cat_id = '5087'">
        <xsl:value-of select='2073' />
      </xsl:when>
      <xsl:when test="$cat_id = '5086'">
        <xsl:value-of select='415' />
      </xsl:when>
      <xsl:when test="$cat_id = '5353'">
        <xsl:value-of select='4943' />
      </xsl:when>
      <xsl:when test="$cat_id = '5332'">
        <xsl:value-of select='4947' />
      </xsl:when>
      <xsl:when test="$cat_id = '493'">
        <xsl:value-of select='5099' />
      </xsl:when>
      <xsl:when test="$cat_id = '1019'">
        <xsl:value-of select='7149' />
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>No match</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>