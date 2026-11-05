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