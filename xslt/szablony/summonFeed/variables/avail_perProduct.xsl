<xsl:variable name="avail_perProduct">
   <xsl:choose>
      <xsl:when test="contains($stocksGobalCheck_perProduct,'-1')">
         <xsl:text>9999</xsl:text>
      </xsl:when>
      <xsl:when test="string-length($stocksGobalCheck_perProduct) = 0">
         <xsl:text>0</xsl:text>
      </xsl:when>
      <xsl:otherwise>
         <xsl:value-of select="sum(../size/stock[contains($sales_stocks, concat('|',@id,'|'))]/@available_stock_quantity)" />
      </xsl:otherwise>
   </xsl:choose>
</xsl:variable>