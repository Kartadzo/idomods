<xsl:template name="throwLastNode">
      <xsl:param name="text" />
      <xsl:param name="delimiter" select="'\'" />
      <xsl:choose>
         <xsl:when test="not(contains($text, $delimiter))">
            <xsl:value-of select="$text" />
         </xsl:when>
         <xsl:otherwise>
            <xsl:call-template name="throwLastNode">
               <xsl:with-param name="text" select="substring-after($text, $delimiter)" tunnel="yes" />
               <xsl:with-param name="delimiter" select="$delimiter" tunnel="yes" />
            </xsl:call-template>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
