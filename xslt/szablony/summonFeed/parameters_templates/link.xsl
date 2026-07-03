
   <xsl:variable name="Kraj_dostawy" select="'PL'" />

<!-- dla google -->
      <!-- 18.07.2025 MD -->
      <!-- link do produktu -->
      <xsl:element name="g:link">
         <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
         <xsl:choose>
            <xsl:when test="../../card/@url">
               <xsl:value-of select="substring-before(../../card/@url, '.feed')" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="substring-before(card/@url, '.feed')" />
            </xsl:otherwise>
         </xsl:choose>
         <xsl:text disable-output-escaping="yes">.googleshopping</xsl:text>
         <xsl:value-of select="translate($Kraj_dostawy, $upperLetters, $lowerLetters)" />
         <xsl:text disable-output-escaping="yes">.html</xsl:text>
         <xsl:if test="count(../size) &gt; 1">
            <xsl:text>?selected_size=</xsl:text>
            <xsl:value-of select="@id" />
         </xsl:if>
         <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
      </xsl:element>
      <xsl:element name="g:display_ads_link">
         <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
         <xsl:choose>
            <xsl:when test="../../card/@url">
               <xsl:value-of select="substring-before(../../card/@url, '.feed')" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="substring-before(card/@url, '.feed')" />
            </xsl:otherwise>
         </xsl:choose>
         <xsl:text disable-output-escaping="yes">.googleremarketing.html</xsl:text>
         <xsl:if test="count(../size) &gt; 1">
            <xsl:text>?selected_size=</xsl:text>
            <xsl:value-of select="@id" />
         </xsl:if>
         <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
      </xsl:element>
      <xsl:element name="g:mobile_link">
         <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
         <xsl:choose>
            <xsl:when test="../../card/@url">
               <xsl:value-of select="substring-before(../../card/@url, '.feed')" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="substring-before(card/@url, '.feed')" />
            </xsl:otherwise>
         </xsl:choose>
         <xsl:text disable-output-escaping="yes">.googleshopping</xsl:text>
         <xsl:value-of select="translate($Kraj_dostawy, $upperLetters, $lowerLetters)" />
         <xsl:text disable-output-escaping="yes">.html</xsl:text>
         <xsl:if test="count(../size) &gt; 1">
            <xsl:text>?selected_size=</xsl:text>
            <xsl:value-of select="@id" />
         </xsl:if>
         <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
      </xsl:element>
