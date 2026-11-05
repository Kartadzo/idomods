<xsl:template name="lowerCaseCount"> 
      <xsl:param name="text"/> 
      <xsl:variable name="lowercaseOnly" select="translate($text, concat($upperLetters,'0123456789., *%&amp;;\/-+()'), '')"/> 
      <xsl:value-of select="string-length($lowercaseOnly)"/> 
   </xsl:template>
