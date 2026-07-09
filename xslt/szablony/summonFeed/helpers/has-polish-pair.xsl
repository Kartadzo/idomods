<xsl:template name="has-polish-pair">
      <xsl:param name="tmp"/>
      
      <xsl:variable name="pl" select="'ĄĆĘŁŃÓŚŹŻ'"/>
      
      <xsl:choose>
         <xsl:when test="string-length($tmp) &lt; 2">
            <xsl:text>false</xsl:text>
         </xsl:when>
         <xsl:when test="
            contains($pl, substring($tmp,1,1))
            and contains($pl, substring($tmp,2,1))
                     ">
            <xsl:text>true</xsl:text>
         </xsl:when>
         <xsl:otherwise>
            <xsl:call-template name="has-polish-pair">
               <xsl:with-param name="tmp" select="substring($tmp,2)"/>
            </xsl:call-template>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
