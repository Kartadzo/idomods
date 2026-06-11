<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
    
    <xsl:template match="/">
        <rss xmlns:g="http://base.google.com/ns/1.0" version="2.0">
            <channel>
                <xsl:for-each select="/products/product">
                    <item>
                        <id>
                            <xsl:value-of select="product_id"/>
                        </id>
                        <name>
                            <xsl:value-of select="name"/>
                        </name>
                        <ean>
                            <xsl:value-of select="ean"/>
                        </ean>
                        <sku>
                            <xsl:value-of select="sku"/>
                        </sku>
                        
                        <image>
                            <!-- główny obraz -->
                            <xsl:value-of select="image"/>
                            <!-- dodatkowe obrazy: każdy poprzedzony znakiem nowej linii jeśli niepusty -->
                            <xsl:if test="string-length(normalize-space(image_extra_1)) &gt; 0">
                                <xsl:text>&#10;</xsl:text>
                                <xsl:value-of select="image_extra_1"/>
                            </xsl:if>
                            <xsl:if test="string-length(normalize-space(image_extra_2)) &gt; 0">
                                <xsl:text>&#10;</xsl:text>
                                <xsl:value-of select="image_extra_2"/>
                            </xsl:if>
                            <xsl:if test="string-length(normalize-space(image_extra_3)) &gt; 0">
                                <xsl:text>&#10;</xsl:text>
                                <xsl:value-of select="image_extra_3"/>
                            </xsl:if>
                            <xsl:if test="string-length(normalize-space(image_extra_4)) &gt; 0">
                                <xsl:text>&#10;</xsl:text>
                                <xsl:value-of select="image_extra_4"/>
                            </xsl:if>
                            <xsl:if test="string-length(normalize-space(image_extra_5)) &gt; 0">
                                <xsl:text>&#10;</xsl:text>
                                <xsl:value-of select="image_extra_5"/>
                            </xsl:if>
                            <xsl:if test="string-length(normalize-space(image_extra_6)) &gt; 0">
                                <xsl:text>&#10;</xsl:text>
                                <xsl:value-of select="image_extra_6"/>
                            </xsl:if>
                            <xsl:if test="string-length(normalize-space(image_extra_7)) &gt; 0">
                                <xsl:text>&#10;</xsl:text>
                                <xsl:value-of select="image_extra_7"/>
                            </xsl:if>
                            <xsl:if test="string-length(normalize-space(image_extra_8)) &gt; 0">
                                <xsl:text>&#10;</xsl:text>
                                <xsl:value-of select="image_extra_8"/>
                            </xsl:if>
                            <xsl:if test="string-length(normalize-space(image_extra_9)) &gt; 0">
                                <xsl:text>&#10;</xsl:text>
                                <xsl:value-of select="image_extra_9"/>
                            </xsl:if>
                            <xsl:if test="string-length(normalize-space(image_extra_10)) &gt; 0">
                                <xsl:text>&#10;</xsl:text>
                                <xsl:value-of select="image_extra_10"/>
                            </xsl:if>
                            <xsl:if test="string-length(normalize-space(image_extra_11)) &gt; 0">
                                <xsl:text>&#10;</xsl:text>
                                <xsl:value-of select="image_extra_11"/>
                            </xsl:if>
                            <xsl:if test="string-length(normalize-space(image_extra_12)) &gt; 0">
                                <xsl:text>&#10;</xsl:text>
                                <xsl:value-of select="image_extra_12"/>
                            </xsl:if>
                            <xsl:if test="string-length(normalize-space(image_extra_13)) &gt; 0">
                                <xsl:text>&#10;</xsl:text>
                                <xsl:value-of select="image_extra_13"/>
                            </xsl:if>
                            <xsl:if test="string-length(normalize-space(image_extra_14)) &gt; 0">
                                <xsl:text>&#10;</xsl:text>
                                <xsl:value-of select="image_extra_14"/>
                            </xsl:if>
                            <xsl:if test="string-length(normalize-space(image_extra_15)) &gt; 0">
                                <xsl:text>&#10;</xsl:text>
                                <xsl:value-of select="image_extra_15"/>
                            </xsl:if>
                        </image>
                        
                        <!-- Powiązania: wypisz je w jednym bloku powiazania, każdy w nowej linii jako "nazwa\id" -->
                        <powiazania>
                            <xsl:for-each select="POWIAZANIA/POWIAZANIE[powiazanie_zrodlo_nazwa = 'Dresowka Idoo']">
                                <xsl:if test="position() &gt; 1">
                                    <xsl:text>&#10;</xsl:text>
                                </xsl:if>
                                <nazwa>
                                <xsl:value-of select="normalize-space(powiazanie_zrodlo_nazwa)"/></nazwa>
                                <id>
                                <xsl:value-of select="normalize-space(powiazanie_produkt_id)"/></id>
                            </xsl:for-each>
                        </powiazania>
                        
                    </item>
                </xsl:for-each>
            </channel>
        </rss>
    </xsl:template>
    
</xsl:stylesheet>
