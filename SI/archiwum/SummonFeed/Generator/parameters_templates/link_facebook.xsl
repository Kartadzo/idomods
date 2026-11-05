
      <g:link>
         <xsl:choose>
            <xsl:when test="../../card/@url">
               <xsl:value-of select="substring-before(../../card/@url, '.feed')" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="substring-before(card/@url, '.feed')" />
            </xsl:otherwise>
         </xsl:choose>
         <xsl:text>.facebookads.html</xsl:text>
         <xsl:if test="count(../size) &gt; 1">
            <xsl:text>?selected_size=</xsl:text>
            <xsl:value-of select="@id" />
         </xsl:if>
      </g:link>
      <g:ios_url>
         <xsl:choose>
            <xsl:when test="../../card/@url">
               <xsl:value-of select="substring-before(../../card/@url, '.feed')" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="substring-before(card/@url, '.feed')" />
            </xsl:otherwise>
         </xsl:choose>
         <xsl:text>.facebookads.html</xsl:text>
         <xsl:if test="count(../size) &gt; 1">
            <xsl:text>?selected_size=</xsl:text>
            <xsl:value-of select="@id" />
         </xsl:if>
      </g:ios_url>
      <g:iphone_url>
         <xsl:choose>
            <xsl:when test="../../card/@url">
               <xsl:value-of select="substring-before(../../card/@url, '.feed')" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="substring-before(card/@url, '.feed')" />
            </xsl:otherwise>
         </xsl:choose>
         <xsl:text>.facebookads.html</xsl:text>
         <xsl:if test="count(../size) &gt; 1">
            <xsl:text>?selected_size=</xsl:text>
            <xsl:value-of select="@id" />
         </xsl:if>
      </g:iphone_url>
      <g:ipad_url>
         <xsl:choose>
            <xsl:when test="../../card/@url">
               <xsl:value-of select="substring-before(../../card/@url, '.feed')" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="substring-before(card/@url, '.feed')" />
            </xsl:otherwise>
         </xsl:choose>
         <xsl:text>.facebookads.html</xsl:text>
         <xsl:if test="count(../size) &gt; 1">
            <xsl:text>?selected_size=</xsl:text>
            <xsl:value-of select="@id" />
         </xsl:if>
      </g:ipad_url>
      <g:android_url>
         <xsl:choose>
            <xsl:when test="../../card/@url">
               <xsl:value-of select="substring-before(../../card/@url, '.feed')" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="substring-before(card/@url, '.feed')" />
            </xsl:otherwise>
         </xsl:choose>
         <xsl:text>.facebookads.html</xsl:text>
         <xsl:if test="count(../size) &gt; 1">
            <xsl:text>?selected_size=</xsl:text>
            <xsl:value-of select="@id" />
         </xsl:if>
      </g:android_url>
      <g:windows_phone_url>
         <xsl:choose>
            <xsl:when test="../../card/@url">
               <xsl:value-of select="substring-before(../../card/@url, '.feed')" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="substring-before(card/@url, '.feed')" />
            </xsl:otherwise>
         </xsl:choose>
         <xsl:text>.facebookads.html</xsl:text>
         <xsl:if test="count(../size) &gt; 1">
            <xsl:text>?selected_size=</xsl:text>
            <xsl:value-of select="@id" />
         </xsl:if>
      </g:windows_phone_url>
