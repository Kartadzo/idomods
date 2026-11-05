<xsl:element name="g:custom_label_0">
         <xsl:choose>
            <xsl:when test="price/@gross &lt;= 50">
               <xsl:text>0-50 </xsl:text>
               <xsl:value-of select="@currency" />
            </xsl:when>
            <xsl:when test="price/@gross &gt; 50 and price/@gross &lt;= 100">
               <xsl:text>50-100 </xsl:text>
               <xsl:value-of select="@currency" />
            </xsl:when>
            <xsl:when test="price/@gross &gt; 100 and price/@gross &lt;= 150">
               <xsl:text>100-150 </xsl:text>
               <xsl:value-of select="@currency" />
            </xsl:when>
            <xsl:when test="price/@gross &gt; 150 and price/@gross &lt;= 200">
               <xsl:text>150-200 </xsl:text>
               <xsl:value-of select="@currency" />
            </xsl:when>
            <xsl:when test="price/@gross &gt; 200 and price/@gross &lt;= 500">
               <xsl:text>200-500 </xsl:text>
               <xsl:value-of select="@currency" />
            </xsl:when>
            <xsl:when test="price/@gross &gt; 500">
               <xsl:text>500+ </xsl:text>
               <xsl:value-of select="@currency" />
            </xsl:when>
         </xsl:choose>
      </xsl:element>
