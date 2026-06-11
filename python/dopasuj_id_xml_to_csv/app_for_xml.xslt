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
						<xsl:element name="name">
							<xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
							<xsl:value-of select="translate(description/name[xml:lang='pol']/.,'.',',')"/>
							<xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
						</xsl:element>
					</product>
				</xsl:for-each>
			</channel>
		</rss>
	</xsl:template>
</xsl:stylesheet>