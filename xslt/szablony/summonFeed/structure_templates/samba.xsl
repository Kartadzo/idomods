<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml"
    xmlns:php="http://php.net/xsl">
    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes" />
    
    <xsl:template match="/">
        <PRODUCTS>
            <xsl:for-each select="/offer/products/product">
                <PRODUCT>
                    <xsl:for-each select="sizes/size">
                        <xsl:choose>
                            <xsl:when test = "position() = 1">
                                <!-- Id produktu -->
                                <PRODUCT_ID>
                                    <xsl:value-of select="../../@id"/>
                                </PRODUCT_ID>
                                <xsl:call-template name="product"/>
                                 <xsl:call-template name="productSizeMatter"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <VARIANT>
                                    <!-- Id produktu -->
                                    <PRODUCT_ID>
                                        <xsl:value-of select="@code"/>
                                    </PRODUCT_ID>
                                    <xsl:call-template name="product"/>
                                    <xsl:call-template name="productSizeMatter"/>
                                </VARIANT>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:for-each>
                </PRODUCT>
            </xsl:for-each>
        </PRODUCTS>
    </xsl:template>

    <xsl:template name="product">
    </xsl:template>

    <xsl:template name="productSizeMatter">
    </xsl:template>
</xsl:stylesheet>
