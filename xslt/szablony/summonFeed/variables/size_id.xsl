<xsl:variable name="size_id">
         <xsl:choose>
            <xsl:when test="@name!=''">
               <xsl:value-of select="@id" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:text>-</xsl:text>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>
