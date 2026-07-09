<xsl:variable name="product_currency">
         <xsl:choose>
            <xsl:when test="../../@currency!=''">
               <xsl:value-of select="../../@currency" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="@currency" />
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>
