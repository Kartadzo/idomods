<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:iof="http://www.iai-shop.com/developers/iof.phtml"
                xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml"
                xmlns:php="http://php.net/xsl">
    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes" />
    
    <!-- długoś aktualizacji 
         - zaczynamy od pierwszego, w razie powolnego aktualizowania produktów -> zmniejszyć -->
    <xsl:variable name='pierwszy_produkt'>0</xsl:variable>
    <xsl:variable name='ostatni_produkt'>126000</xsl:variable>
    <!-- PL|DE|CZ|SK|RO|UA||||||||||||||||||||||||||||||| -->
    <xsl:variable name="upperLetters"
        select="'AĄBCĆDEĘFGHIJKLŁMNŃOÓPQRSŚTUVWXYZŹŻÄÖÜẞÁČĎÉĚÍŇÓŘŠŤÚŮÝŽÁÄČĎŽÉÍĹĽŇÓÔŔŠŤÚÝŽĂÂÎȘȚАБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ'" />
    <xsl:variable name="lowerLetters"
        select="'aąbcćdeęfghijklłmnńoópqrsśtuvwxyzźżäöüßáčďéěíňóřšťúůýžáäčďžéíĺľňóôŕšťúýžăâîșțабвгґдеєжзиіїйклмнопрстуфхцчшщьюя'" />
    
    <xsl:template match="/">
        <rss xmlns:g="http://base.google.com/ns/1.0" version="2.0">
            <channel>
                <xsl:for-each
                    select="/products/product[
                            position() &gt;= $pierwszy_produkt and 
                            position() &lt;= $ostatni_produkt
                        ]">
                    <item>
                        <id>
                            <xsl:value-of select="number(id/.)+126000" />
                        </id>
                        <paramid>
                            <xsl:value-of select="id/." />
                        </paramid>
                        <kodZewnetrzny>
                            <xsl:text>KA-</xsl:text>
                            <xsl:value-of select="sku/." />
                        </kodZewnetrzny>
                        <kodProducentaEAN>
                            <xsl:value-of select="ean/." />
                        </kodProducentaEAN>
                        <xsl:copy-of select="name" />
                        <xsl:copy-of select="desc" />
                        <weight>
                            <xsl:value-of
                                select="(number(translate(weight/.,',','.'))*1000)*number(translate(quantityPerBox/.,',','.'))" />
                        </weight>
                        <KA-Typ>
                            <xsl:value-of select="brand/." />
                        </KA-Typ>
                        <xsl:copy-of select="photos" />
                        <sku>
                            <xsl:value-of select="sku/." />
                        </sku>
                        <vat>
                            <xsl:value-of select="vat/." />
                        </vat>
                        <retailPriceGross>
                            <xsl:value-of
                                select="number(translate(retailPriceGross/., ',', '.'))*number(translate(quantityPerBox/.,',','.'))" />
                        </retailPriceGross>
                        <visible>
                            <xsl:text>no</xsl:text>
                        </visible>
                        <xsl:copy-of select="qty" />
                        <paramWysokosc>
                            <xsl:variable name="tmpValue">
                                <xsl:choose>
                                    <xsl:when
                                        test="contains(translate(translate(desc/., ' ', ''), $upperLetters, $lowerLetters), 'wysokość-')">
                                        <xsl:value-of
                                            select="substring-after(translate(translate(desc/., ' ', ''), $upperLetters, $lowerLetters), 'wysokość-')" />
                                    </xsl:when>
                                    <xsl:otherwise></xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>
                            <xsl:variable name="tmpDesc">
                                <xsl:choose>
                                    <xsl:when test="$tmpValue != ''">
                                        <xsl:value-of
                                            select="substring-before($tmpValue, 'mm')" />
                                    </xsl:when>
                                    <xsl:otherwise></xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>
                            <xsl:variable name="originalText" select="$tmpDesc" />
                            <xsl:variable name="replace" select="'&amp;nbsp;'" />
                            <xsl:variable name="by" select="''" />
                            <xsl:variable name="finalValue">
                                <!-- Pierwsze zastąpienie -->
                                <xsl:variable name="step1">
                                    <xsl:choose>
                                        <xsl:when test="contains($originalText, $replace)">
                                            <xsl:value-of
                                                select="concat(substring-before($originalText, $replace), $by, substring-after($originalText, $replace))" />
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:value-of select="$originalText" />
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </xsl:variable>
                                
                                <!-- Drugie zastąpienie, wykonane na wyniku pierwszego -->
                                <xsl:variable name="step2">
                                    <xsl:choose>
                                        <xsl:when test="contains($step1, $replace)">
                                            <xsl:value-of
                                                select="concat(substring-before($step1, $replace), $by, substring-after($step1, $replace))" />
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:value-of select="$step1" />
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </xsl:variable>
                                
                                <!-- Trzecie zastąpienie -->
                                <xsl:variable name="step3">
                                    <xsl:choose>
                                        <xsl:when test="contains($step2, $replace)">
                                            <xsl:value-of
                                                select="concat(substring-before($step2, $replace), $by, substring-after($step2, $replace))" />
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:value-of select="$step2" />
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </xsl:variable>
                                <xsl:value-of select="$step3" />
                            </xsl:variable>
                            <xsl:choose>
                                <xsl:when
                                    test="$finalValue != '' and translate($finalValue,'0123456789','') = ''">
                                    <xsl:value-of
                                        select="format-number($finalValue div 10, '#.##')" />
                                </xsl:when>
                                <xsl:when
                                    test="$finalValue != '' and translate($finalValue,'0123456789','') != ''">
                                    <xsl:value-of
                                        select="$finalValue" />
                                    <xsl:text> mm</xsl:text>
                                </xsl:when>
                                <xsl:otherwise></xsl:otherwise>
                            </xsl:choose>
                        </paramWysokosc>
                        <paramSzerokosc>
                            <xsl:variable name="tmpValue">
                                <xsl:choose>
                                    <xsl:when
                                        test="contains(translate(translate(desc/., ' ', ''), $upperLetters, $lowerLetters), 'grubość-')">
                                        <xsl:value-of
                                            select="substring-after(translate(translate(desc/., ' ', ''), $upperLetters, $lowerLetters), 'grubość-')" />
                                    </xsl:when>
                                    <xsl:otherwise></xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>
                            <xsl:variable name="tmpDesc">
                                <xsl:choose>
                                    <xsl:when test="$tmpValue != ''">
                                        <xsl:value-of
                                            select="substring-before($tmpValue, 'mm')" />
                                    </xsl:when>
                                    <xsl:otherwise></xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>
                            <xsl:variable name="originalText" select="$tmpDesc" />
                            <xsl:variable name="replace" select="'&amp;nbsp;'" />
                            <xsl:variable name="by" select="''" />
                            <xsl:variable name="finalValue">
                                <!-- Pierwsze zastąpienie -->
                                <xsl:variable name="step1">
                                    <xsl:choose>
                                        <xsl:when test="contains($originalText, $replace)">
                                            <xsl:value-of
                                                select="concat(substring-before($originalText, $replace), $by, substring-after($originalText, $replace))" />
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:value-of select="$originalText" />
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </xsl:variable>
                                
                                <!-- Drugie zastąpienie, wykonane na wyniku pierwszego -->
                                <xsl:variable name="step2">
                                    <xsl:choose>
                                        <xsl:when test="contains($step1, $replace)">
                                            <xsl:value-of
                                                select="concat(substring-before($step1, $replace), $by, substring-after($step1, $replace))" />
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:value-of select="$step1" />
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </xsl:variable>
                                
                                <!-- Trzecie zastąpienie -->
                                <xsl:variable name="step3">
                                    <xsl:choose>
                                        <xsl:when test="contains($step2, $replace)">
                                            <xsl:value-of
                                                select="concat(substring-before($step2, $replace), $by, substring-after($step2, $replace))" />
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:value-of select="$step2" />
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </xsl:variable>
                                <xsl:value-of select="$step3" />
                            </xsl:variable>
                            <xsl:choose>
                                <xsl:when
                                    test="$finalValue != '' and translate($finalValue,'0123456789','') = ''">
                                    <xsl:value-of
                                        select="format-number($finalValue div 10, '#.##')" />
                                </xsl:when>
                                <xsl:when
                                    test="$finalValue != '' and translate($finalValue,'0123456789','') != ''">
                                    <xsl:value-of
                                        select="$finalValue" />
                                    <xsl:text> mm</xsl:text>
                                </xsl:when>
                                <xsl:otherwise></xsl:otherwise>
                            </xsl:choose>
                        </paramSzerokosc>
                        <paramDlugosc>
                            <xsl:variable name="tmpValue">
                                <xsl:choose>
                                    <xsl:when
                                        test="contains(translate(translate(desc/., ' ', ''), $upperLetters, $lowerLetters), 'długość-')">
                                        <xsl:value-of
                                            select="substring-after(translate(translate(desc/., ' ', ''), $upperLetters, $lowerLetters), 'długość-')" />
                                    </xsl:when>
                                    <xsl:otherwise></xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>
                            <xsl:variable name="tmpDesc">
                                <xsl:choose>
                                    <xsl:when test="$tmpValue != ''">
                                        <xsl:value-of
                                            select="substring-before($tmpValue, 'mm')" />
                                    </xsl:when>
                                    <xsl:otherwise></xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>
                            <xsl:variable name="originalText" select="$tmpDesc" />
                            <xsl:variable name="replace" select="'&amp;nbsp;'" />
                            <xsl:variable name="by" select="''" />
                            <xsl:variable name="finalValue">
                                <!-- Pierwsze zastąpienie -->
                                <xsl:variable name="step1">
                                    <xsl:choose>
                                        <xsl:when test="contains($originalText, $replace)">
                                            <xsl:value-of
                                                select="concat(substring-before($originalText, $replace), $by, substring-after($originalText, $replace))" />
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:value-of select="$originalText" />
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </xsl:variable>
                                
                                <!-- Drugie zastąpienie, wykonane na wyniku pierwszego -->
                                <xsl:variable name="step2">
                                    <xsl:choose>
                                        <xsl:when test="contains($step1, $replace)">
                                            <xsl:value-of
                                                select="concat(substring-before($step1, $replace), $by, substring-after($step1, $replace))" />
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:value-of select="$step1" />
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </xsl:variable>
                                
                                <!-- Trzecie zastąpienie -->
                                <xsl:variable name="step3">
                                    <xsl:choose>
                                        <xsl:when test="contains($step2, $replace)">
                                            <xsl:value-of
                                                select="concat(substring-before($step2, $replace), $by, substring-after($step2, $replace))" />
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:value-of select="$step2" />
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </xsl:variable>
                                <xsl:value-of select="$step3" />
                            </xsl:variable>
                            <xsl:choose>
                                <xsl:when
                                    test="$finalValue != '' and translate($finalValue,'0123456789','') = ''">
                                    <xsl:value-of
                                        select="format-number($finalValue div 10, '#.##')" />
                                </xsl:when>
                                <xsl:when
                                    test="$finalValue != '' and translate($finalValue,'0123456789','') != ''">
                                    <xsl:value-of
                                        select="$finalValue" />
                                    <xsl:text> mm</xsl:text>
                                </xsl:when>
                                <xsl:otherwise></xsl:otherwise>
                            </xsl:choose>
                        </paramDlugosc>
                    </item>
                </xsl:for-each>
            </channel>
        </rss>
    </xsl:template>
</xsl:stylesheet>