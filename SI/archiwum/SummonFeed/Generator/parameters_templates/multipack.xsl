<!-- 2026-05-07 - MD -->
      <xsl:choose>
         <xsl:when test="bundled/product/@quantity > 1 and count(bundled/product) = 1">
            <xsl:element name="g:multipack">
               <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
               <xsl:value-of select="format-number(bundled/product/@quantity, '#')"/>
               <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
            </xsl:element>
         </xsl:when>
         <xsl:when test="@type='regular' and iaiext:sell_by/iaiext:retail and iaiext:sell_by/iaiext:retail/@quantity > 1">
            <xsl:element name="g:multipack">
               <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
               <xsl:value-of select="format-number(iaiext:sell_by/iaiext:retail/@quantity, '#')"/>
               <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
            </xsl:element>
         </xsl:when>
      </xsl:choose>