<xsl:template name="upperCaseCount"> 
      <xsl:param name="text"/> 
      <xsl:variable name="uppercaseOnly" select="translate($text, concat($lowerLetters,'0123456789., *%&amp;;\/-+()'), '')"/> 
      <xsl:value-of select="string-length($uppercaseOnly)"/> 
   </xsl:template>
