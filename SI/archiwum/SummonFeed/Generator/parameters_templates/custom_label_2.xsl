<g:custom_label_2>
         <xsl:variable name="label2">
            <xsl:call-template name="throwNode">
               <xsl:with-param name="index" select="1"/>
               <xsl:with-param name="border" select="'\\'"/>
            </xsl:call-template>
         </xsl:variable>
         <xsl:call-template name="tokenize">
            <xsl:with-param name="text" select="substring(normalize-space($label2),1,100)" />
            <xsl:with-param name="delimiter" select="';'" />
         </xsl:call-template>
      </g:custom_label_2>
