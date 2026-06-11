<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:iof="http://www.iai-shop.com/developers/iof.phtml"
	xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml"
	xmlns:php="http://php.net/xsl">
	<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes" />
	
	<xsl:template match="/">
		<rss xmlns:g="http://base.google.com/ns/1.0" version="2.0">
			<channel>
				<xsl:for-each select="/offer/products/product">
					<product id="{@id}">
						<xsl:element name="alert_omnibus_jest_mniejszy">
							<xsl:value-of select="sizes/size/price/@gross > iaiext:omnibus_price_retail/iaiext:site/@gross"/>
						</xsl:element>
						<xsl:element name="omnibus_minus_price_roznica_10gr">
							<xsl:value-of select="(iaiext:omnibus_price_retail/iaiext:site/@gross - sizes/size/price/@gross) > 0.1"/>
						</xsl:element>
						<xsl:element name="price">
							<xsl:value-of select="sizes/size/price/@gross"/>
						</xsl:element>
						<xsl:element name="omnibus_price_retail">
							<xsl:value-of select="iaiext:omnibus_price_retail/iaiext:site/@gross"/>
						</xsl:element>
						<xsl:element name="strikethrough_retail_price">
							<xsl:value-of select="sizes/size/strikethrough_retail_price/@gross"/>
						</xsl:element>
						<xsl:element name="promotion">
							<xsl:value-of select="promotion/price/normal_retail_price/iaiext:site/iaiext:price_per_size/@gross"/>
						</xsl:element>
					</product>
				</xsl:for-each>
			</channel>
		</rss>
	</xsl:template>
</xsl:stylesheet>