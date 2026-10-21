<!-- g product type -->
      <xsl:for-each select="iaiext:navigation/iaiext:site[1]/iaiext:menu[1]">
         <xsl:for-each select="iaiext:item[position() &lt; 6 and not(contains(@textid, ../../../../producer/@name))]">
            <xsl:element name="g:product_type">
               <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
               <xsl:call-template name="string-replace-all">
                  <xsl:with-param name="text" select="@textid" tunnel="yes" />
                  <xsl:with-param name="replace" select="'\\'" tunnel="yes" />
                  <xsl:with-param name="by" select="' &gt; '" tunnel="yes" />
               </xsl:call-template>
               <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
            </xsl:element>
         </xsl:for-each>
      </xsl:for-each>
