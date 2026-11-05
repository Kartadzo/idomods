<xsl:template name="extract-measure">
      <xsl:param name="str"/>
      
      <xsl:variable name="token" select="substring-before(concat($str,' '),' ')"/>
      <xsl:variable name="rest"  select="substring-after($str,' ')"/>
      
      <xsl:variable name="clean" select="translate($token,'*%&amp;;\/-+()','')"/>
      
      <xsl:choose>
         <!-- 1) format: 500ml, 1,5l, 1.5l -->
         <xsl:when test="
            translate($clean,'0123456789.,','') != '' and
            contains($unitsList, concat('|', translate($clean,'0123456789.,',''), '|')) and
            string-length(translate($clean,'0123456789.,','')) &gt; 0 and
            string-length(translate($clean,'0123456789.,','')) &lt; 4 and
            string-length(translate($clean,'0123456789','')) &lt; string-length($clean)
                     ">
            <xsl:value-of select="$clean"/>
         </xsl:when>
         <!-- 2) format: 500 ml, 1,5 l, 1.5 l, 15 kg -->
         <xsl:when test="
            translate($clean,'0123456789.,','') = '' and
            string-length($clean) &gt; 0 and
            string-length(translate($clean,'0123456789','')) &lt; string-length($clean) and
            contains($unitsList, concat('|', substring-before(concat($rest,' '),' '), '|')) and
            not(contains($unitsList, concat('|', $clean, '|')))
                     ">
            <xsl:value-of select="concat($clean, ' ', substring-before(concat($rest,' '),' '))"/>
         </xsl:when>
         <!-- 3) format: 4x500ml, 4x1,5l, 4x1.5l -->
         <xsl:when test="
            contains($clean,'x') and
            translate(substring-before($clean,'x'),'0123456789.,','') = '' and
            translate(substring-after($clean,'x'),'0123456789.,','') != '' and
            contains($unitsList, concat('|', translate(substring-after($clean,'x'),'0123456789.,',''), '|'))
                     ">
            <xsl:value-of select="$clean"/>
         </xsl:when>
         <!-- 4) format: 4 x 500ml, 4 x 1,5l, 4 x 1.5l -->
         <xsl:when test="
            translate($clean,'0123456789.,','') = '' and
            substring($rest,2,1) = 'x'
                     ">
            <xsl:variable name="afterX" select="substring($rest,3)"/>
            <xsl:if test="
               translate($afterX,'0123456789.,','') != '' and
               contains($unitsList, concat('|', translate($afterX,'0123456789.,',''), '|'))
                     ">
               <xsl:value-of select="concat($clean, ' x ', $afterX)"/>
            </xsl:if>
         </xsl:when>
         <xsl:when test="$rest != ''">
            <xsl:call-template name="extract-measure">
               <xsl:with-param name="str" select="$rest"/>
            </xsl:call-template>
         </xsl:when>
         <xsl:otherwise/>
      </xsl:choose>
   </xsl:template>
