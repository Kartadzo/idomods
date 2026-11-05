<!-- dla facebook -->
      <!-- Grupuj rozmiary i warianty -->
      <xsl:choose>
         <xsl:when test="group/@id">
            <g:item_group_id>
               <xsl:text disable-output-escaping="yes">&lt;![CDATA[group-</xsl:text>
               <xsl:value-of select="group/@id"/>
               <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
            </g:item_group_id>
         </xsl:when>
         <xsl:when test="not(group/@id) and count(sizes/size) &gt; 1">
            <g:item_group_id>
               <xsl:text disable-output-escaping="yes">&lt;![CDATA[group-</xsl:text>
               <xsl:value-of select="@id"/>
               <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
            </g:item_group_id>
         </xsl:when>
      </xsl:choose>