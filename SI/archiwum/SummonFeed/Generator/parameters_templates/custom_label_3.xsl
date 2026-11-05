<g:custom_label_3>
         <xsl:variable name="label3">
            <xsl:call-template name="throwNode">
               <xsl:with-param name="index" select="2"/>
               <xsl:with-param name="border" select="'\\'"/>
            </xsl:call-template>
         </xsl:variable>
         <xsl:call-template name="tokenize">
            <xsl:with-param name="text" select="substring(normalize-space($label3),1,100)" />
            <xsl:with-param name="delimiter" select="';'" />
         </xsl:call-template>
      </g:custom_label_3>
