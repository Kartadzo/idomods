<g:custom_label_1>
         <xsl:if test="iaiext:hotspots/iaiext:site/flag[@type = 'newproduct']/@visible='yes'">
            <xsl:text>|Nowość|</xsl:text>
         </xsl:if>
         <xsl:if test="iaiext:hotspots/iaiext:site/flag[@type = 'bestseller']/@visible='yes'">
            <xsl:text>|Bestseller|</xsl:text>
         </xsl:if>
         <xsl:if test="iaiext:hotspots/iaiext:site/flag[@type = 'promotion']/@visible='yes'">
            <xsl:text>|Promocja|</xsl:text>
         </xsl:if>
         <xsl:if test="iaiext:hotspots/iaiext:site/flag[@type = 'distinguished']/@visible='yes'">
            <xsl:text>|Wyróżniony|</xsl:text>
         </xsl:if>
      </g:custom_label_1>
