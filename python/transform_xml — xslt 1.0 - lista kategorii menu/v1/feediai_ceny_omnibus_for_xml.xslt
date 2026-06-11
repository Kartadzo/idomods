<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml"
	xmlns:php="http://php.net/xsl">
	<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes" />
	<!-- PL|DE|CZ|SK|RO|UA||||||||||||||||||||||||||||||| -->
	<xsl:variable name="upperLetters" 
		select="'AĄBCĆDEĘFGHIJKLŁMNŃOÓPQRSŚTUVWXYZŹŻÄÖÜẞÁČĎÉĚÍŇÓŘŠŤÚŮÝŽÁÄČĎŽÉÍĹĽŇÓÔŔŠŤÚÝŽĂÂÎȘȚАБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ'" />
	<xsl:variable name="lowerLetters" 
		select="'aąbcćdeęfghijklłmnńoópqrsśtuvwxyzźżäöüßáčďéěíňóřšťúůýžáäčďžéíĺľňóôŕšťúýžăâîșțабвгґдеєжзиіїйклмнопрстуфхцчшщьюя'" />
	
	
	<xsl:template match="/">
		<rss xmlns:g="http://base.google.com/ns/1.0" version="2.0">
			<!-- <updated><xsl:value-of select="/offer/@generated"/></updated> -->
			<channel>
				<xsl:for-each select="/offer/products/product[
						price/@gross &gt; 0 and 
						description/name/. != '']">
					<!-- Id towaru -->
					<xsl:choose>
						<xsl:when test="count(sizes/size) &lt; 1">
						</xsl:when>
						<xsl:otherwise>
							<xsl:for-each select="sizes/size">
								<xsl:choose>
									<xsl:when test = "position() = 1">
										<xsl:for-each select="../..">
											<xsl:call-template name="product"/>
										</xsl:for-each>
									</xsl:when>
									<xsl:otherwise>
										<!-- Id rozmiaru produktu -->
										<xsl:for-each select="../..">
											<xsl:call-template name="product"/>
										</xsl:for-each>
									</xsl:otherwise>
								</xsl:choose>
							</xsl:for-each>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:for-each>
			</channel>
		</rss>
	</xsl:template>
	
	<xsl:template name="product" xmlns:g="http://base.google.com/ns/1.0" version="2.0">
		<xsl:for-each select="iaiext:navigation/iaiext:site/iaiext:menu[1]/iaiext:item">
			<xsl:element name="item">
				<xsl:text disable-output-escaping="yes">&lt;p&gt;</xsl:text>
				<xsl:call-template name="string-replace-all">
					<xsl:with-param name="text" select="@textid" />
					<xsl:with-param name="replace" select="'\'" />
					<xsl:with-param name="by" select="'&lt;/p&gt;&lt;p&gt;'" />
				</xsl:call-template>
				<xsl:text disable-output-escaping="yes">&lt;/p&gt;</xsl:text>
			</xsl:element>
		</xsl:for-each>
	</xsl:template>
	
	<xsl:template name="string-replace-all">
		<xsl:param name="text" />
		<xsl:param name="replace" />
		<xsl:param name="by" />
		<xsl:param name="depth" select="0" />
		<xsl:choose>
			<xsl:when test="contains($text, $replace) and $depth &lt; 1000">
				<xsl:value-of select="substring-before($text,$replace)"  />
				<xsl:value-of select="$by" disable-output-escaping="yes"/>
				<xsl:call-template name="string-replace-all">
					<xsl:with-param name="text" select="substring-after($text,$replace)" />
					<xsl:with-param name="replace" select="$replace" />
					<xsl:with-param name="by" select="$by" />
					<xsl:with-param name="depth" select="$depth + 1" />
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$text" />
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
</xsl:stylesheet>