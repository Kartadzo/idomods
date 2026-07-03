
   <!-- magazyny sprzedaży, identyfikator otoczony '|' -->
   <xsl:variable name="sales_stocks" select="'|-3|-2|-1|0|1|2|3|4|5|6|7|8|9|10|11|12|'"/>
   
      <xsl:variable name="sell_by">
         <xsl:choose>
            <xsl:when test="../../iaiext:sell_by/iaiext:retail and ../../iaiext:sell_by/iaiext:retail/@quantity &gt; 0">
               <xsl:value-of select="../../iaiext:sell_by/iaiext:retail/@quantity" />
            </xsl:when>
            <xsl:when test="iaiext:sell_by/iaiext:retail and iaiext:sell_by/iaiext:retail/@quantity &gt; 0">
               <xsl:value-of select="iaiext:sell_by/iaiext:retail/@quantity" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:text>1</xsl:text>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>

      <!-- dla google -->
      <!-- 2026.01.13 - MD -->
      <!-- Dostępność -->
      <xsl:variable name="stocksGobalCheck">
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
      </xsl:variable>
      <xsl:variable name="avail">
         <xsl:choose>
            <xsl:when test="contains($stocksGobalCheck,'-1')">
               <xsl:text>999999</xsl:text>
            </xsl:when>
            <xsl:when test="string-length($stocksGobalCheck) = 0">
               <xsl:text>0</xsl:text>
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="sum(stock[contains($sales_stocks, concat('|',@id,'|'))]/@available_stock_quantity)"/>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>
      <xsl:element name="g:availability">
         <xsl:choose>
            <xsl:when test="@available = 'on_order' and $avail &gt;= $sell_by">
               <xsl:text disable-output-escaping="yes">&lt;![CDATA[in stock]]&gt;</xsl:text>
            </xsl:when>
            <xsl:when test="@available = 'in_stock' and $avail &gt;= $sell_by">
               <xsl:text disable-output-escaping="yes">&lt;![CDATA[in stock]]&gt;</xsl:text>
            </xsl:when>
            <xsl:otherwise>
               <xsl:text disable-output-escaping="yes">&lt;![CDATA[out of stock]]&gt;</xsl:text>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:element>
