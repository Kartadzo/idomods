<!-- Stan -->
      <xsl:variable name="condition_new"><![CDATA[new]]></xsl:variable>
      <xsl:variable name="condition_refurbished"><![CDATA[refurbished]]></xsl:variable>
      <xsl:variable name="condition_used"><![CDATA[used]]></xsl:variable>
      <xsl:element name="g:condition">
         <xsl:choose>
            <xsl:when test="parameters/parameter[@context_id = 'CONTEXT_STATE']">
               <xsl:for-each select="parameters/parameter[@context_id = 'CONTEXT_STATE'][1]">
                  <xsl:choose>
                     <xsl:when test="value[@context_id = 'CONTEXT_STATE_NEW'] or 
                                     value[@context_id = 'CONTEXT_STATE_NEW_OTHERS']">
                        <xsl:value-of select="$condition_new" />
                     </xsl:when>
                     <xsl:when test="value[@context_id = 'CONTEXT_STATE_USED'] or 
                                     value[@context_id = 'CONTEXT_STATE_FOR_PARTS_OR_BROKEN'] or 
                                     value[@context_id = 'CONTEXT_STATE_NEW_WITH_DEFECTS']">
                        <xsl:value-of select="$condition_used" />
                     </xsl:when>
                     <xsl:when test="value[@context_id = 'CONTEXT_STATE_REFURBISHED_BY_PRODUCER'] or
                                     value[@context_id = 'CONTEXT_STATE_REFURBISHED_BY_SELLER']">
                        <xsl:value-of select="$condition_refurbished" />
                     </xsl:when>
                     <xsl:otherwise>
                        <xsl:value-of select="$condition_new" />
                     </xsl:otherwise>
                  </xsl:choose>
               </xsl:for-each>
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="$condition_new" />
            </xsl:otherwise>
         </xsl:choose>
      </xsl:element>