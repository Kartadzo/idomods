<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml"
                xmlns:php="http://php.net/xsl">
   <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes" />
   
   <xsl:template match="/">
      <rss xmlns:g="http://base.google.com/ns/1.0" version="2.0">
         <channel>
            <xsl:for-each select="/offer/products/product[
                                 price/@gross &gt; 0 
                                 and description/name/. != ''
                                 and @type != 'packaging'
                                 ]">
               <!-- Id towaru -->
               <xsl:choose>
                  <xsl:when test="count(sizes/size) &lt; 1">
                     <item>
                        <g:id>
                           <xsl:value-of select="@id"/>
                        </g:id>
                        <xsl:call-template name="product"/>
                        <xsl:call-template name="productSizeMatter"/>
                     </item>
                  </xsl:when>
                  <xsl:otherwise>
                     <xsl:for-each select="sizes/size">
                        <xsl:choose>
                           <xsl:when test = "position() = 1">
                              <item>
                                 <g:id>
                                    <xsl:value-of select="../../@id"/>
                                 </g:id>
                                 <xsl:for-each select="../..">
                                    <xsl:call-template name="product"/>
                                 </xsl:for-each>
                                 <xsl:call-template name="productSizeMatter"/>
                              </item>
                           </xsl:when>
                        </xsl:choose>
                     </xsl:for-each>
                  </xsl:otherwise>
               </xsl:choose>
            </xsl:for-each>
         </channel>
      </rss>
   </xsl:template>
   
   <xsl:template name="product"
                 xmlns:g="http://base.google.com/ns/1.0" version="2.0">
   </xsl:template>
   
   <xsl:template name="productSizeMatter"
                 xmlns:g="http://base.google.com/ns/1.0" version="2.0">
   </xsl:template>
</xsl:stylesheet>
