
<!-- Marka -->
<xsl:if test="producer/@name != 'producent niezdefiniowany'">
   <xsl:element name="g:brand">
      <xsl:value-of select="normalize-space(producer/@name)" />
   </xsl:element>
</xsl:if>
