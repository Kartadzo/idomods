<xsl:variable name="cena_przedpromocyjna">
         <xsl:choose>
            <xsl:when test="../../promotion/price/normal_retail_price/iaiext:site/iaiext:price_per_size[@id = $size_id]/@panel_name != '' and
                            ../../promotion/price/normal_retail_price/iaiext:site/iaiext:price_per_size[@id = $size_id]/@gross > price/@gross">
               <xsl:value-of select="../../promotion/price/normal_retail_price/iaiext:site/iaiext:price_per_size[@id = $size_id]/@gross" />
            </xsl:when>
            <xsl:when test="../../promotion/price/normal_retail_price and ../../promotion/price/normal_retail_price/@gross > price/@gross">
               <xsl:value-of select="../../promotion/price/normal_retail_price/@gross" />
            </xsl:when>
            <xsl:when test="promotion/price/normal_retail_price/iaiext:site/iaiext:price_per_size[@id = $size_id]/@panel_name != '' and
                            promotion/price/normal_retail_price/iaiext:site/iaiext:price_per_size[@id = $size_id]/@gross > price/@gross">
               <xsl:value-of select="promotion/price/normal_retail_price/iaiext:site/iaiext:price_per_size[@id = $size_id]/@gross" />
            </xsl:when>
            <xsl:when test="promotion/price/normal_retail_price and promotion/price/normal_retail_price/@gross > price/@gross">
               <xsl:value-of select="promotion/price/normal_retail_price/@gross" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:text>0</xsl:text>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>
