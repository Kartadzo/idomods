<!-- Default XSLT loaded by quantity_to_sell_on_facebook.json -->
<!-- Copy of the current quantity_to_sell_on_facebook fragment code -->
      <!-- Dostępność -->
      <xsl:variable name="stocksGobalCheck">
         <xsl:for-each select="../size">
            <xsl:for-each select="stock[contains($sales_stocks, concat('|',@id,'|'))]">
               <xsl:choose>
                  <xsl:when test="@available_stock_quantity &gt; 0">
                     <xsl:value-of select="@available_stock_quantity"></xsl:value-of>
                     <xsl:text>/</xsl:text>
                  </xsl:when>
                  <xsl:when test="@available_stock_quantity = -1 ">
                     <xsl:value-of select="@available_stock_quantity"></xsl:value-of>
                     <xsl:text>/</xsl:text>
                  </xsl:when>
               </xsl:choose>
            </xsl:for-each>
         </xsl:for-each>
      </xsl:variable>
      <xsl:variable name="avail">
         <xsl:choose>
            <xsl:when test="contains($stocksGobalCheck,'-1')">
               <xsl:text>9999</xsl:text>
            </xsl:when>
            <xsl:when test="string-length($stocksGobalCheck) = 0">
               <xsl:text>0</xsl:text>
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="sum(../size/stock[contains($sales_stocks, concat('|',@id,'|'))]/@available_stock_quantity)" />
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>
      <quantity_to_sell_on_facebook>
         <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
         <xsl:value-of select="format-number($avail, '#')"/>
         <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
      </quantity_to_sell_on_facebook>
