
<xsl:template name="wordFormat">
   <xsl:param name="text" />
   <xsl:param name="delimiter" select="' '" />
   <!-- lista słów do skorygowania, otoczona separatorem '\'; przekazywana z parametru
        (configVar 'corrected'), więc MUSI być podawana dalej przy każdej rekurencji -->
   <xsl:param name="corrected" select="'\GRATIS\'" />
   
   <xsl:choose>
      <xsl:when test="contains($text, $delimiter) and not(contains(substring-before($text, $delimiter),'/'))">
         <xsl:variable name="word">
            <xsl:text><![CDATA[\]]></xsl:text>
            <xsl:value-of select="substring-before($text, $delimiter)" />
            <xsl:text><![CDATA[\]]></xsl:text>
         </xsl:variable>
         <xsl:choose>
            <xsl:when test="contains($corrected, $word)">
               <xsl:value-of select="substring(translate($word, '\', ''),1,1)" />
               <xsl:value-of select="translate(substring(translate($word, '\', ''),2), $upperLetters, $lowerLetters)" />
               <xsl:value-of select="$delimiter" />
               <xsl:call-template name="wordFormat">
                  <xsl:with-param name="text" select="substring-after($text, $delimiter)" />
                  <xsl:with-param name="corrected" select="$corrected" />
               </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="translate($word, '\', '')" />
               <xsl:value-of select="$delimiter" />
               <xsl:call-template name="wordFormat">
                  <xsl:with-param name="text" select="substring-after($text, $delimiter)" />
                  <xsl:with-param name="corrected" select="$corrected" />
               </xsl:call-template>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:when>
      <xsl:when test="contains($text, '/')">
         <xsl:variable name="word">
            <xsl:text><![CDATA[\]]></xsl:text>
            <xsl:value-of select="substring-before($text, '/')" />
            <xsl:text><![CDATA[\]]></xsl:text>
         </xsl:variable>
         <xsl:choose>
            <xsl:when test="contains($corrected, $word)">
               <xsl:value-of select="substring(translate($word, '\', ''),1,1)" />
               <xsl:value-of select="translate(substring(translate($word, '\', ''),2), $upperLetters, $lowerLetters)" />
               <xsl:text><![CDATA[/]]></xsl:text>
               <xsl:call-template name="wordFormat">
                  <xsl:with-param name="text" select="substring-after($text, '/')" />
                  <xsl:with-param name="corrected" select="$corrected" />
               </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="translate($word, '\', '')" />
               <xsl:text><![CDATA[/]]></xsl:text>
               <xsl:call-template name="wordFormat">
                  <xsl:with-param name="text" select="substring-after($text, '/')" />
                  <xsl:with-param name="corrected" select="$corrected" />
               </xsl:call-template>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
         <xsl:variable name="word">
            <xsl:text><![CDATA[\]]></xsl:text>
            <xsl:value-of select="$text" />
            <xsl:text><![CDATA[\]]></xsl:text>
         </xsl:variable>
         <xsl:choose>
            <xsl:when test="contains($corrected, $word)">
               <xsl:value-of select="substring(translate($word, '\', ''),1,1)" />
               <xsl:value-of select="translate(substring(translate($word, '\', ''),2), $upperLetters, $lowerLetters)" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="translate($word, '\', '')" />
            </xsl:otherwise>
         </xsl:choose>
      </xsl:otherwise>
   </xsl:choose>
</xsl:template>