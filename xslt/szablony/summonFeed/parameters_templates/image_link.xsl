<xsl:choose>
         <xsl:when test="images/icons/auction_icon/@url">
            <xsl:element name="g:image_link">
               <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
               <xsl:value-of select="images/icons/auction_icon/@url"></xsl:value-of>
               <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
            </xsl:element>
            <xsl:for-each select="images/large/image[position() &lt; 5]">
               <xsl:element name="g:additional_image_link">
                  <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
                  <xsl:value-of select="@url" />
                  <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
               </xsl:element>
            </xsl:for-each>
         </xsl:when>
         <xsl:otherwise>
            <xsl:variable name="vLowest">
               <xsl:for-each select="images/large/image/@iaiext:priority">
                  <xsl:sort data-type="number" />
                  <xsl:if test="position()=1">
                     <xsl:value-of select="." />
                  </xsl:if>
               </xsl:for-each>
            </xsl:variable>
            
            <xsl:for-each select="images/large/image[position() &lt; 5]">
               <xsl:choose>
                  <xsl:when test="@iaiext:priority = number($vLowest)">
                     <xsl:element name="g:image_link">
                        <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
                        <xsl:value-of select="@url" />
                        <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
                     </xsl:element>
                  </xsl:when>
                  <xsl:otherwise>
                     <xsl:element name="g:additional_image_link">
                        <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
                        <xsl:value-of select="@url" />
                        <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
                     </xsl:element>
                  </xsl:otherwise>
               </xsl:choose>
            </xsl:for-each>
         </xsl:otherwise>
      </xsl:choose>