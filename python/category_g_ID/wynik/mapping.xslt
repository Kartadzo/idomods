<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <xsl:variable name="cat_id" select="category_idosell/@id"/>
    <xsl:choose>
      <xsl:when test="$cat_id = '2205'">
        <xsl:value-of select='443' />
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>No match</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>