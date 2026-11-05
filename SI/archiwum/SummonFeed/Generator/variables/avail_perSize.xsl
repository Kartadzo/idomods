<xsl:variable name="avail_perSize">
   <xsl:choose>
      <xsl:when test="contains($stocksGobalCheck_perSize,'-1')">
         <xsl:text>999999</xsl:text>
      </xsl:when>
      <xsl:when test="string-length($stocksGobalCheck_perSize) = 0">
         <xsl:text>0</xsl:text>
      </xsl:when>
      <xsl:otherwise>
         <xsl:value-of select="sum(stock[contains($sales_stocks, concat('|',@id,'|'))]/@available_stock_quantity)"/>
      </xsl:otherwise>
   </xsl:choose>
</xsl:variable>