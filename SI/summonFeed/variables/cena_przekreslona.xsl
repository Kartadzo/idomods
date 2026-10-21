<xsl:variable name="cena_przekreslona">
         <xsl:choose>
            <xsl:when test="sizes/size/strikethrough_retail_price">
               <xsl:value-of select="sizes/size/strikethrough_retail_price/@gross" />
            </xsl:when>
            <xsl:when test="strikethrough_retail_price">
               <xsl:value-of select="strikethrough_retail_price/@gross" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:text>0</xsl:text>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>
