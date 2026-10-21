<xsl:variable name="stocksGobalCheck_perProduct">
   <xsl:for-each select="../size">
      <xsl:for-each select="stock[contains($sales_stocks, concat('|',@id,'|'))]">
         <xsl:choose>
            <xsl:when test="@available_stock_quantity &gt; 0">
               <xsl:value-of select="@available_stock_quantity"/>
               <xsl:text>/</xsl:text>
            </xsl:when>
            <xsl:when test="@available_stock_quantity = -1 ">
               <xsl:value-of select="@available_stock_quantity"/>
               <xsl:text>/</xsl:text>
            </xsl:when>
         </xsl:choose>
      </xsl:for-each>
   </xsl:for-each>
</xsl:variable>