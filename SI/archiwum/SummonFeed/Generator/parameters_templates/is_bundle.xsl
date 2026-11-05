<xsl:choose>
         <xsl:when test="sum(bundled/product/@quantity) > 1">
            <xsl:element name="g:is_bundle">
               <xsl:text>yes</xsl:text>
            </xsl:element>
         </xsl:when>
         <!-- <xsl:otherwise>
              <xsl:text>no</xsl:text>
              </xsl:otherwise> -->
        </xsl:choose>