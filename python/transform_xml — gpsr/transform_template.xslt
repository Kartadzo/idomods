<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml"
                xmlns:php="http://php.net/xsl">
    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes" />
    
    <xsl:template match="/">
        <rss xmlns:g="http://base.google.com/ns/1.0" version="2.0">
            <!-- <updated><xsl:value-of select="/offer/@generated"/></updated> -->
            <channel>
                <xsl:for-each select="/offer/products/product">
                    <xsl:if test="iaiext:responsible_entity/producer/code != ''">
                        <p>
                            <Nazwawlasna>
                                <xsl:value-of select="iaiext:responsible_entity/producer/@id"/>
                            </Nazwawlasna>
                            <Nazwa>
                                <xsl:value-of select="iaiext:responsible_entity/producer/name"/>
                            </Nazwa>
                            <Kraj>
                                <xsl:value-of select="iaiext:responsible_entity/producer/country"/>
                            </Kraj>
                            <Ulicainumer>
                                <xsl:value-of select="iaiext:responsible_entity/producer/street"/>
                                <xsl:text> </xsl:text>
                                <xsl:value-of select="iaiext:responsible_entity/producer/number"/>
                            </Ulicainumer>   
                            <Miasto>
                                <xsl:value-of select="iaiext:responsible_entity/producer/city"/>
                            </Miasto>  
                            <Kodpocztowy>
                                <xsl:value-of select="iaiext:responsible_entity/producer/zipcode"/>
                            </Kodpocztowy>
                            <Email>
                                <xsl:value-of select="iaiext:responsible_entity/producer/mail"/>
                            </Email>
                            <Telefonkontaktowy>
                                <xsl:value-of select="iaiext:responsible_entity/producer/phone"/>
                            </Telefonkontaktowy>   
                            <Typ>
                                <xsl:text>Producent</xsl:text>
                            </Typ> 
                        </p>
                    </xsl:if>
                    <xsl:if test="iaiext:responsible_entity/persons/person/code != ''">
                        <p>
                            <Nazwawlasna>
                                <xsl:value-of select="iaiext:responsible_entity/producer/@id"/>
                            </Nazwawlasna>
                            <Nazwa>
                                <xsl:value-of select="iaiext:responsible_entity/producer/name"/>
                            </Nazwa>
                            <Kraj>
                                <xsl:value-of select="iaiext:responsible_entity/producer/country"/>
                            </Kraj>
                            <Ulicainumer>
                                <xsl:value-of select="iaiext:responsible_entity/producer/street"/>
                                <xsl:text> </xsl:text>
                                <xsl:value-of select="iaiext:responsible_entity/producer/number"/>
                            </Ulicainumer>   
                            <Miasto>
                                <xsl:value-of select="iaiext:responsible_entity/producer/city"/>
                            </Miasto>  
                            <Kodpocztowy>
                                <xsl:value-of select="iaiext:responsible_entity/producer/zipcode"/>
                            </Kodpocztowy>
                            <Email>
                                <xsl:value-of select="iaiext:responsible_entity/producer/mail"/>
                            </Email>
                            <Telefonkontaktowy>
                                <xsl:value-of select="iaiext:responsible_entity/producer/phone"/>
                            </Telefonkontaktowy>   
                            <Typ>
                                <xsl:text>Podmiot</xsl:text>
                            </Typ> 
                        </p>
                    </xsl:if>
                </xsl:for-each>
            </channel>
        </rss>
    </xsl:template>
</xsl:stylesheet>