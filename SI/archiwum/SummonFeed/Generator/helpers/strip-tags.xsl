<xsl:template name="strip-tags">
   <xsl:param name="text" />
   <xsl:param name="open" select="'&lt;'" />
   <xsl:param name="close" select="'&gt;'" />
   <xsl:param name="depth" select="0" />
   <xsl:choose>
      <xsl:when test="contains($text, $open) and not(contains(substring-after($text, $open), $close))">
         <xsl:value-of select="normalize-space($text)" />
      </xsl:when>
      <xsl:when test="contains($text, $open) and $depth &lt; 1000">
         <xsl:value-of select="substring-before($text, $open)" />
         <xsl:text><![CDATA[ ]]></xsl:text>
         <xsl:call-template name="strip-tags">
            <xsl:with-param name="text" select="substring-after($text, $close)" />
            <xsl:with-param name="open" select="$open" />
            <xsl:with-param name="close" select="$close" />
            <xsl:with-param name="depth" select="$depth + 1" />
         </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
         <xsl:value-of select="normalize-space($text)" />
      </xsl:otherwise>
   </xsl:choose>
</xsl:template>
