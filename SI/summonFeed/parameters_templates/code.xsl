
<!-- 2025.01.13 - MD -->
<!-- Gtin / MPN -->
<xsl:choose>
   <xsl:when
      test="(../../@producer_code_standard = 'ISBN10' or ../../@producer_code_standard = 'ISBN13' or 
                         ../../@producer_code_standard = 'GTIN8' or ../../@producer_code_standard = 'GTIN13' or 
                         ../../@producer_code_standard = 'GTIN14' or ../../@producer_code_standard = 'GTIN12' or 
                         ../../@producer_code_standard = 'UPCE') and @code_producer!='' and
                         not(starts-with(@code_producer, '2') or starts-with(@code_producer, '02') or starts-with(@code_producer, '04'))">
      <xsl:element name="g:gtin">
         <xsl:value-of select="@code_producer" />
      </xsl:element>
   </xsl:when>
   <xsl:otherwise>
      <xsl:element name="g:mpn">
         <xsl:choose>
            <xsl:when test="@code_producer!=''">
               <xsl:value-of select="@code_producer" />
            </xsl:when>
            <xsl:when test="@iaiext:code_external!=''">
               <xsl:value-of select="@iaiext:code_external" />
            </xsl:when>
            <xsl:when test="../../@code_on_card!=''">
               <xsl:value-of select="../../@code_on_card" />
            </xsl:when>
            <xsl:when test="@code_on_card!=''">
               <xsl:value-of select="substring(@code_on_card,1,70)" />
            </xsl:when>
         </xsl:choose>
      </xsl:element>
   </xsl:otherwise>
</xsl:choose>
