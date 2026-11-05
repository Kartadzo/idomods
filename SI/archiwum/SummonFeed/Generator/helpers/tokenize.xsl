<xsl:template name="tokenize">
      <xsl:param name="text" />
      <xsl:param name="delimiter" select="'.'" />
      <xsl:param name="depth" select="0" />
      <xsl:choose>
         <xsl:when test="contains($text, $delimiter) and $depth &lt; 1000">
            <xsl:value-of select="substring-before($text, $delimiter)" />
            <xsl:value-of select="$delimiter" />
            <xsl:call-template name="tokenize">
               <xsl:with-param name="text" select="substring-after($text, $delimiter)" />
               <xsl:with-param name="delimiter" select="$delimiter" />
               <xsl:with-param name="depth" select="$depth + 1" />
            </xsl:call-template>
         </xsl:when>
      </xsl:choose>
   </xsl:template>
