<xsl:template name="throwNode">
      <xsl:param name="pos" select="1"/>
      <xsl:param name="index" />
      <xsl:param name="prev" select="''"/>
      <xsl:param name="border" select="'\'"/>
      
      <xsl:variable name="items" select="iaiext:priority_menu/site[1]/menu[1]/item[contains(@textId,$border)]"/>
      <xsl:variable name="total" select="count($items)"/>
      
      <xsl:choose>
         <xsl:when test="$pos &gt; $total">
            <xsl:if test="string-length($prev) > 2">
               <xsl:value-of select="$prev"/>
            </xsl:if>
         </xsl:when>
         <xsl:otherwise>
            <xsl:variable name="node">
               <xsl:call-template name="extract-node">
                  <xsl:with-param name="text"  select="$items[$pos]/@textId"/>
                  <xsl:with-param name="index" select="$index"/>
               </xsl:call-template>
            </xsl:variable>
            
            <xsl:variable name="nodeNorm" select="normalize-space($node)"/>
            
            <xsl:variable name="result">
               <xsl:value-of select="$prev"/>
               <xsl:if test="string-length($nodeNorm) > 0 
                  and not(contains(concat(';', $prev, ';'),concat('; ', $nodeNorm, ';')) 
                     or contains(concat(';', $prev, ';'),concat(';', $nodeNorm, ';')))">
                  <xsl:value-of select="$nodeNorm"/>
                  <xsl:text>; </xsl:text>
               </xsl:if>
            </xsl:variable>
            <xsl:call-template name="throwNode">
               <xsl:with-param name="pos"      select="$pos +1"/>
               <xsl:with-param name="index"    select="$index"/>
               <xsl:with-param name="prev"     select="$result"/>	
               <xsl:with-param name="border"   select="$border"/>
            </xsl:call-template>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
