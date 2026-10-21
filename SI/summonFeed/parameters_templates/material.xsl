<!-- dane potrzebne aby przekazywać informacje o materiale -->
   <xsl:variable name='material_nazwa_w_panelu'>|materiał|</xsl:variable>

      
      <!-- materiał -->
      <!-- 2026-01-29 - MD -->
      <xsl:if test="$material_nazwa_w_panelu != '' and parameters/parameter[@hide = 'n' and 
                    contains($material_nazwa_w_panelu, concat('|',translate(@name, $upperLetters, $lowerLetters),'|'))]">
         <xsl:variable name='material_get' select="parameters/parameter[@hide = 'n' and 
                                                   contains($material_nazwa_w_panelu, concat('|',translate(@name, $upperLetters, $lowerLetters),'|'))
                                                   ]/@name" />
         <xsl:variable name="value">
            <xsl:for-each select="parameters/parameter[@name= $material_get]/value">
               <xsl:value-of select="@name" />
               <xsl:text>/</xsl:text>
            </xsl:for-each>
         </xsl:variable>
         <xsl:variable name="value_tokenized">
            <xsl:call-template name="tokenize">
               <xsl:with-param name="text" select="substring(normalize-space($value),1,200)" />
               <xsl:with-param name="delimiter" select="'/'" />
            </xsl:call-template>
         </xsl:variable>
         <xsl:element name="g:material">
            <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
            <xsl:value-of select="substring($value_tokenized, 1, string-length($value_tokenized) - 1)" />
            <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
         </xsl:element>
      </xsl:if>