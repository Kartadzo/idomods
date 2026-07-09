
<!-- 2026.04.30 MD -->
<xsl:variable name="nazwaTowaru">
   <xsl:choose>
      <xsl:when test="iaiext:pricecomparator_name 
         and iaiext:pricecomparator_name != ''
         and ../@language = iaiext:pricecomparator_name/@xml:lang">
         <xsl:call-template name="wordFormat">
            <xsl:with-param name="text" select="substring(iaiext:pricecomparator_name[@xml:lang = ../../@language]/., 1, 146)" tunnel="yes" />
         </xsl:call-template>
         <xsl:if test="string-length(iaiext:pricecomparator_name[@xml:lang = ../../@language]/.) >= 146">
            <xsl:text disable-output-escaping="yes">...</xsl:text>
         </xsl:if>
      </xsl:when>
      <xsl:otherwise>
         <xsl:call-template name="wordFormat">
            <xsl:with-param name="text" select="substring(description/name/., 1, 146)" tunnel="yes" />
         </xsl:call-template>
         <xsl:if test="string-length(description/name/.) >= 146 and description/name/. != ''">
            <xsl:text disable-output-escaping="yes">...</xsl:text>
         </xsl:if>
      </xsl:otherwise>
   </xsl:choose>
</xsl:variable>
<xsl:variable name="upperCaseCount">
   <xsl:call-template name="upperCaseCount">
      <xsl:with-param name="text" select="$nazwaTowaru" />
   </xsl:call-template>
</xsl:variable>
<xsl:variable name="lowerCaseCount">
   <xsl:call-template name="lowerCaseCount">
      <xsl:with-param name="text" select="$nazwaTowaru" />
   </xsl:call-template>
</xsl:variable>

<xsl:variable name="wybierzZrodloNazwy">
   <xsl:choose>
      <xsl:when test="($lowerCaseCount div $upperCaseCount) &lt; 0.3">
         <!-- wszystkie litery oprócz pierwszej i producenta zamienia na małe litery -->
         <xsl:variable name="lower-text">
            <xsl:value-of select="concat(substring($nazwaTowaru, 1, 1), translate(substring(normalize-space($nazwaTowaru), 2), $upperLetters, $lowerLetters))" />
         </xsl:variable>
         <xsl:choose>
            <xsl:when test="contains($lower-text, translate(producer/@name, $upperLetters, $lowerLetters))">
               <xsl:value-of select="substring-before($lower-text, translate(producer/@name, $upperLetters, $lowerLetters))" />
               <xsl:value-of select="producer/@name" />
               <xsl:value-of select="substring-after($lower-text, translate(producer/@name, $upperLetters, $lowerLetters))" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="$lower-text" />
            </xsl:otherwise>
         </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
         <xsl:value-of select="$nazwaTowaru" />
      </xsl:otherwise>
   </xsl:choose>
</xsl:variable>

<xsl:element name="g:title">
   <xsl:call-template name="normalize-polish-pairs">
      <xsl:with-param name="text" select="$wybierzZrodloNazwy"/>
   </xsl:call-template>
</xsl:element>