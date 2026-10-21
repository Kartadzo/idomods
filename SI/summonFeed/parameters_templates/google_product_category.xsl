<xsl:variable name="var_google_product_category">
         <xsl:call-template name="searchGoogleCategory">
            <xsl:with-param name="cat_id" select="category_idosell/@id" tunnel="yes" />
         </xsl:call-template>
      </xsl:variable>
      <xsl:choose>
         <xsl:when test="$var_google_product_category != '0'">
            <xsl:element name="g:google_product_category">
               <xsl:value-of select="$var_google_product_category" />
            </xsl:element>
         </xsl:when>
         <xsl:when test="category_idosell/@path != ''">
            <xsl:element name="g:google_product_category">
               <xsl:value-of select="category_idosell/@path"></xsl:value-of>
            </xsl:element>
         </xsl:when>
      </xsl:choose>