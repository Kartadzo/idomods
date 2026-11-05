<xsl:template name="string-replace-all">
      <xsl:param name="text" />
      <xsl:param name="replace" />
      <xsl:param name="by" />
      <xsl:param name="depth" select="0" />
      <xsl:choose>
         <xsl:when test="contains($text, $replace) and $depth &lt; 1000">
            <xsl:value-of select="substring-before($text,$replace)" />
            <xsl:value-of select="$by" />
            <xsl:call-template name="string-replace-all">
               <xsl:with-param name="text" select="substring-after($text,$replace)" />
               <xsl:with-param name="replace" select="$replace" />
               <xsl:with-param name="by" select="$by" />
               <xsl:with-param name="depth" select="$depth + 1" />
            </xsl:call-template>
         </xsl:when>
         <xsl:otherwise>
            <xsl:value-of select="$text" />
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
