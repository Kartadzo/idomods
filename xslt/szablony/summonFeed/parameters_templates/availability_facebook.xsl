<xsl:element name="g:availability">
   <xsl:choose>
      <xsl:when test="@available = 'on_order' and $avail_perProduct &gt;= $sell_by">
         <xsl:text disable-output-escaping="yes">&lt;![CDATA[in stock]]&gt;</xsl:text>
      </xsl:when>
      <xsl:when test="@available = 'in_stock' and $avail_perProduct &gt;= $sell_by">
         <xsl:text disable-output-escaping="yes">&lt;![CDATA[in stock]]&gt;</xsl:text>
      </xsl:when>
      <xsl:otherwise>
         <xsl:text disable-output-escaping="yes">&lt;![CDATA[out of stock]]&gt;</xsl:text>
      </xsl:otherwise>
   </xsl:choose>
</xsl:element>