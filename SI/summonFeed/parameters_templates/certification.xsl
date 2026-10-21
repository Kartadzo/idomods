
<!-- dane potrzebne aby przekazywać informacje -->
<xsl:variable name='certyfikaty_nazwa_w_panelu'>|Certyfikat|</xsl:variable>

   <!-- 2026-06-24 - MD -->      
   <xsl:choose>
      <xsl:when test="parameters/parameter/@context_id = 'CONTEXT_CERTIFICATION'">
         <xsl:for-each select="parameters/parameter[@context_id = 'CONTEXT_CERTIFICATION']">
            <xsl:for-each select="value">
               <xsl:choose>
                  <xsl:when test="string-length(@name) - string-length(translate(@name, ':', '')) = 2">
                     <xsl:element name="g:certification">
                        <xsl:element name="g:certification_authority">
                           <xsl:value-of select="substring-before(@name, ':')" />
                        </xsl:element>
                        <xsl:element name="g:certification_name">
                           <xsl:value-of select="substring-before(substring-after(@name, ':'), ':')" />
                        </xsl:element>
                        <xsl:element name="g:certification_code">
                           <xsl:value-of select="substring-after(substring-after(@name, ':'), ':')" />
                        </xsl:element>
                     </xsl:element>
                  </xsl:when>
               </xsl:choose>
            </xsl:for-each>
         </xsl:for-each>
      </xsl:when>
      <xsl:when test="parameters/parameter[contains(translate($certyfikaty_nazwa_w_panelu, $upperLetters, $lowerLetters), concat('|', translate(@name, $upperLetters, $lowerLetters), '|'))]">
         <xsl:for-each select="parameters/parameter[contains(translate($certyfikaty_nazwa_w_panelu, $upperLetters, $lowerLetters), concat('|', translate(@name, $upperLetters, $lowerLetters), '|'))]">
            <xsl:for-each select="value">
               <xsl:choose>
                  <xsl:when test="string-length(@name) - string-length(translate(@name, ':', '')) = 2">
                     <xsl:element name="g:certification">
                        <xsl:element name="g:certification_authority">
                           <xsl:value-of select="substring-before(@name, ':')" />
                        </xsl:element>
                        <xsl:element name="g:certification_name">
                           <xsl:value-of select="substring-before(substring-after(@name, ':'), ':')" />
                        </xsl:element>
                        <xsl:element name="g:certification_code">
                           <xsl:value-of select="substring-after(substring-after(@name, ':'), ':')" />
                        </xsl:element>
                     </xsl:element>
                  </xsl:when>
               </xsl:choose>
            </xsl:for-each>
         </xsl:for-each>
      </xsl:when>
   </xsl:choose>
