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
                        <item>
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
                            <xsl:variable name="phoneRaw"
                                select="iaiext:responsible_entity/producer/phone"/>
                            
                            <xsl:variable name="phoneClean">
                                <xsl:call-template name="normalize-phone">
                                    <xsl:with-param name="raw" select="$phoneRaw"/>
                                </xsl:call-template>
                            </xsl:variable>
                            
                                <Telefonkontaktowy>
                                    <xsl:value-of select="$phoneClean"/>
                                </Telefonkontaktowy>

                            <Typ>
                                <xsl:text>Producent</xsl:text>
                            </Typ> 
                        </item>
                    </xsl:if>
                    <xsl:if test="iaiext:responsible_entity/persons/person/code != ''">
                        <item>
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
                            <xsl:variable name="phoneRaw"
                                select="iaiext:responsible_entity/producer/phone"/>
                            
                            <xsl:variable name="phoneClean">
                                <xsl:call-template name="normalize-phone">
                                    <xsl:with-param name="raw" select="$phoneRaw"/>
                                </xsl:call-template>
                            </xsl:variable>
                            
                                <Telefonkontaktowy>
                                    <xsl:value-of select="$phoneClean"/>
                                </Telefonkontaktowy>

 
                            <Typ>
                                <xsl:text>Podmiot</xsl:text>
                            </Typ> 
                        </item>
                    </xsl:if>
                </xsl:for-each>
            </channel>
        </rss>
    </xsl:template>
    <xsl:template name="normalize-phone">
        <xsl:param name="raw"/>
        
        <!-- Sprowadź do małych liter -->
        <xsl:variable name="rawLower"
            select="translate(normalize-space($raw),
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZĄĆĘŁŃÓŚŻŹ',
                    'abcdefghijklmnopqrstuvwxyząćęłńóśżź')"/>
        
        <!-- Pomijamy ewidentne braki -->
        <xsl:choose>
            <xsl:when test="contains($rawLower, 'nie dotyczy')
                or contains($rawLower, 'brak')
                or contains($rawLower, 'nd')">
                <xsl:value-of select="''"/>
            </xsl:when>
            
            <xsl:otherwise>
                
                <!-- Usuwamy nawiasy, plusy, spacje, myślniki, slash -->
                <xsl:variable name="clean"
                    select="translate($raw,
                            ' ()-+/.',
                            '')"/>
                
                <!-- Usuwamy prefiksy kierunkowe:
                     48, 0048, 39, 0039, 91, 0091 itd.
                     (XSLT 1.0 → tylko substring) -->
                <xsl:variable name="noPrefix">
                    <xsl:choose>
                        
                        <!-- prefiks 48 -->
                        <xsl:when test="starts-with($clean, '48')">
                            <xsl:value-of select="substring($clean, 3)"/>
                        </xsl:when>
                        
                        <!-- prefiks 0048 -->
                        <xsl:when test="starts-with($clean, '0048')">
                            <xsl:value-of select="substring($clean, 5)"/>
                        </xsl:when>
                        
                        <!-- prefiks 39 -->
                        <xsl:when test="starts-with($clean, '39')">
                            <xsl:value-of select="substring($clean, 3)"/>
                        </xsl:when>
                        
                        <!-- prefiks 0039 -->
                        <xsl:when test="starts-with($clean, '0039')">
                            <xsl:value-of select="substring($clean, 5)"/>
                        </xsl:when>
                        
                        <!-- prefiks 91 -->
                        <xsl:when test="starts-with($clean, '91')">
                            <xsl:value-of select="substring($clean, 3)"/>
                        </xsl:when>
                        
                        <!-- prefiks 0091 -->
                        <xsl:when test="starts-with($clean, '0091')">
                            <xsl:value-of select="substring($clean, 5)"/>
                        </xsl:when>
                        
                        <!-- domyślnie: bez zmian -->
                        <xsl:otherwise>
                            <xsl:value-of select="$clean"/>
                        </xsl:otherwise>
                        
                    </xsl:choose>
                </xsl:variable>
                
                <!-- Zwracamy numer bez prefiksu -->
                <xsl:value-of select="normalize-space($noPrefix)"/>
                
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


</xsl:stylesheet>