<xsl:variable name="cena_serwis">
         <xsl:choose>
            <xsl:when test="../../iaiext:pricecomparator_price/iaiext:site">
               <xsl:value-of select="../../iaiext:pricecomparator_price/iaiext:site/@gross" />
            </xsl:when>
            <xsl:when test="iaiext:pricecomparator_price/iaiext:site">
               <xsl:value-of select="iaiext:pricecomparator_price/iaiext:site/@gross" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:text>0</xsl:text>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>
