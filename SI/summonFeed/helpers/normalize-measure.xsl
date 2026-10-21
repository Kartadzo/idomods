<xsl:template name="normalize-measure">
      <xsl:param name="value"/>
      
      <xsl:variable name="clean" select="normalize-space(translate($value,'*%&amp;;\/-+() ',''))"/>
      
      <xsl:choose>
         <!-- 1) format NxMunit (np. 4x120g, 3x1,5l, 4x500 ml) -->
         <xsl:when test="contains($clean,'x')">
            <xsl:variable name="left"  select="substring-before($clean,'x')"/>
            <xsl:variable name="right" select="substring-after($clean,'x')"/>
            
            <xsl:value-of select="concat(number(translate($left,',','.')) * number(translate($right,'abcdefghijklmnopqrstuvwxyz,','.' ))
                  , ' '
                  , substring-before(concat(translate($right,'0123456789.,',''),' '),' '))"/>
         </xsl:when>
         <!-- 2) format liczba + jednostka (np. 500ml, 1,5l, 15kg) -->
         <xsl:when test="
            translate($clean,'0123456789.,','') != '' and
            string-length(translate($clean,'0123456789','')) &lt; string-length($clean)
                     ">
            <xsl:value-of select="concat(translate(substring-before($clean,translate($clean,'0123456789.,','')),',','.'), ' ', translate($clean,'0123456789.,',''))"/>
         </xsl:when>
         <!-- 3) format liczba + spacja + jednostka (np. 500 ml, 1,5 l, 15 kg) -->
         <xsl:when test="
            contains($clean,' ') and
            translate(substring-before($clean,' '),'0123456789.,','') = ''
                     ">
            <xsl:value-of select="concat(translate(substring-before($clean,' '),',','.'), ' ', substring-before(concat(substring-after($clean,' '),' '),' '))"/>
         </xsl:when>
         <xsl:otherwise/>
      </xsl:choose>
   </xsl:template>
