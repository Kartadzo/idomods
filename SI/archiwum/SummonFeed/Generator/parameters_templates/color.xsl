<!-- Default XSLT loaded by color.json -->
<!-- Copy of the current color fragment code -->
   <!-- dane potrzebne aby przekazywać informacje o kolorze -->
   <xsl:variable name='kolor_nazwa_w_panelu'>|kolor|</xsl:variable>

      <!-- kolor -->
      <!-- 2026-01-29 - MD -->
      <xsl:choose>
         <xsl:when test="parameters/parameter/@context_id = 'CONTEXT_COLOR'">
            <xsl:element name="g:color">
               <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
               <xsl:for-each select="parameters/parameter[@context_id = 'CONTEXT_COLOR']/value[position() &lt; 5]">
                  <xsl:choose>
                     <xsl:when test="position() = 1">
                        <xsl:value-of select="@name" />
                     </xsl:when>
                     <xsl:otherwise>
                        <xsl:text>/</xsl:text>
                        <xsl:value-of select="@name" />
                     </xsl:otherwise>
                  </xsl:choose>
               </xsl:for-each>
               <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
            </xsl:element>
         </xsl:when>
         <xsl:when test="$kolor_nazwa_w_panelu != '' and parameters/parameter[@hide = 'n' and 
                         contains($kolor_nazwa_w_panelu, concat('|',translate(@name, $upperLetters, $lowerLetters),'|'))]">
            <xsl:variable name='kolor_get' select="parameters/parameter[@hide = 'n' and 
                                                   contains($kolor_nazwa_w_panelu, concat('|',translate(@name, $upperLetters, $lowerLetters),'|'))
                                                   ]/@name" />
            <xsl:variable name="value">
               <xsl:for-each select="parameters/parameter[@name= $kolor_get]/value">
                  <xsl:value-of select="@name" />
                  <xsl:text>/</xsl:text>
               </xsl:for-each>
            </xsl:variable>
            <xsl:variable name="value_tokenized">
               <xsl:call-template name="tokenize">
                  <xsl:with-param name="text" select="substring(normalize-space($value),1,100)" />
                  <xsl:with-param name="delimiter" select="'/'" />
               </xsl:call-template>
            </xsl:variable>
            <xsl:element name="g:color">
               <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
               <xsl:value-of select="substring($value_tokenized, 1, string-length($value_tokenized) - 1)" />
               <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
            </xsl:element>
         </xsl:when>
      </xsl:choose>
