<xsl:template name="extract-node">
      <xsl:param name="text"/>
      <xsl:param name="index"/>
      <xsl:param name="counter" select="1"/>
      
      <xsl:choose>
         <xsl:when test="not(contains($text,'\'))">
            <xsl:if test="$counter = $index">
               <xsl:value-of select="$text"/>
            </xsl:if>
         </xsl:when>
         <xsl:otherwise>
            <xsl:variable name="head">
               <xsl:choose> 
                  <xsl:when test="contains($text,' \ ')"> 
                     <xsl:value-of select="substring-before($text,' \ ')"/>
                  </xsl:when> 
                  <xsl:otherwise>
                     <xsl:value-of select="substring-before($text,'\')"/>
                  </xsl:otherwise> 
               </xsl:choose>
            </xsl:variable>
            <xsl:variable name="tail">
               <xsl:choose> 
                  <xsl:when test="contains($text,' \ ')"> 
                     <xsl:value-of select="substring-after($text,' \ ')"/>
                  </xsl:when> 
                  <xsl:otherwise>
                     <xsl:value-of select="substring-after($text,'\')"/>
                  </xsl:otherwise> 
               </xsl:choose>
            </xsl:variable>
            
            <xsl:if test="$counter = $index">
               <xsl:value-of select="$head"/>
            </xsl:if>
            
            <xsl:call-template name="extract-node">
               <xsl:with-param name="text"     select="$tail"/>
               <xsl:with-param name="index"    select="$index"/>
               <xsl:with-param name="counter"  select="$counter + 1"/>
            </xsl:call-template>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
