<xsl:template name="string-normalize-all">
      <xsl:param name="text"/>
      
      <xsl:variable name="step1">
         <xsl:call-template name="string-replace-all">
            <xsl:with-param name="text" select="$text"/>
            <xsl:with-param name="replace" select="'&amp;nbsp;'"/>
            <xsl:with-param name="by" select="' '"/>
         </xsl:call-template>
      </xsl:variable>
      
      <xsl:variable name="step2">
         <xsl:call-template name="string-replace-all">
            <xsl:with-param name="text" select="$step1"/>
            <xsl:with-param name="replace" select="'&amp;eacute;'"/>
            <xsl:with-param name="by" select="'é'"/>
         </xsl:call-template>
      </xsl:variable>
      
      <xsl:variable name="step3">
         <xsl:call-template name="string-replace-all">
            <xsl:with-param name="text" select="$step2"/>
            <xsl:with-param name="replace" select="'&amp;oacute;'"/>
            <xsl:with-param name="by" select="'ó'"/>
         </xsl:call-template>
      </xsl:variable>
      
      <xsl:variable name="step4">
         <xsl:call-template name="string-replace-all">
            <xsl:with-param name="text" select="$step3"/>
            <xsl:with-param name="replace" select="'&amp;aacute;'"/>
            <xsl:with-param name="by" select="'á'"/>
         </xsl:call-template>
      </xsl:variable>
      
      <xsl:variable name="step5">
         <xsl:call-template name="string-replace-all">
            <xsl:with-param name="text" select="$step4"/>
            <xsl:with-param name="replace" select="'&amp;iacute;'"/>
            <xsl:with-param name="by" select="'í'"/>
         </xsl:call-template>
      </xsl:variable>
      
      <xsl:variable name="step6">
         <xsl:call-template name="string-replace-all">
            <xsl:with-param name="text" select="$step5"/>
            <xsl:with-param name="replace" select="'&amp;uacute;'"/>
            <xsl:with-param name="by" select="'ú'"/>
         </xsl:call-template>
      </xsl:variable>
      
      <xsl:variable name="step7">
         <xsl:call-template name="string-replace-all">
            <xsl:with-param name="text" select="$step6"/>
            <xsl:with-param name="replace" select="'&amp;ntilde;'"/>
            <xsl:with-param name="by" select="'ñ'"/>
         </xsl:call-template>
      </xsl:variable>
      
      <xsl:variable name="step8">
         <xsl:call-template name="string-replace-all">
            <xsl:with-param name="text" select="$step7"/>
            <xsl:with-param name="replace" select="'&amp;amp;'"/>
            <xsl:with-param name="by" select="'&amp;'"/>
         </xsl:call-template>
      </xsl:variable>
      
      <xsl:variable name="step9">
         <xsl:call-template name="string-replace-all">
            <xsl:with-param name="text" select="$step8"/>
            <xsl:with-param name="replace" select="'&amp;quot;'"/>
            <xsl:with-param name="by" select="'&quot;'"/>
         </xsl:call-template>
      </xsl:variable>
      
      <xsl:value-of select="$step9"/>
   </xsl:template>
