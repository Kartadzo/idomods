<xsl:variable name="unit_of_measure" select="'kg'" />
<xsl:variable name="rounding_format" select="'#.##'" />

<xsl:if test="@weight and @weight != 0">
         <xsl:variable name="value_in_unit">
            <xsl:choose>
               <xsl:when test="$unit_of_measure = 'kg'">
                  <xsl:value-of select="@weight div 1000" />
               </xsl:when>
               <xsl:when test="$unit_of_measure = 'g'">
                  <xsl:value-of select="@weight" />
               </xsl:when>
               <xsl:otherwise>
                  <xsl:value-of select="@weight" />
               </xsl:otherwise>
            </xsl:choose>
         </xsl:variable>
         <xsl:element name="g:shipping_weight">
            <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
            <xsl:value-of select="format-number(number($value_in_unit), $rounding_format)" />
            <xsl:text> </xsl:text>
            <xsl:value-of select="$unit_of_measure" />
            <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
         </xsl:element>
      </xsl:if>
