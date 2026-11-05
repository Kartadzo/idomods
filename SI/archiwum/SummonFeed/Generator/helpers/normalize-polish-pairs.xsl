<xsl:template name="normalize-polish-pairs">
      <xsl:param name="text"/>
      
      <xsl:variable name="hasPair">
         <xsl:call-template name="has-polish-pair">
            <xsl:with-param name="tmp" select="$text"/>
         </xsl:call-template>
      </xsl:variable>
      
      <xsl:choose>
         <xsl:when test="$hasPair = 'true'">
            <xsl:value-of select="translate($text, 'ĄĆĘŁŃÓŚŹŻ', 'ACELNOSZZ')"/>
         </xsl:when>
         <xsl:otherwise>
            <xsl:value-of select="$text"/>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
