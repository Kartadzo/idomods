<xsl:template name="searchGoogleCategory">
      <xsl:param name="cat_id" />
      <xsl:choose>
         <xsl:when test="$cat_id = '6675'">
            <xsl:value-of select="'1604'" />
         </xsl:when>
         <xsl:when test="$cat_id = '4571'">
            <xsl:value-of select="'2271'" />
         </xsl:when>
         <xsl:when test="$cat_id = '5977'">
            <xsl:value-of select="'187'" />
         </xsl:when>
         <xsl:otherwise>
            <xsl:text>0</xsl:text>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
