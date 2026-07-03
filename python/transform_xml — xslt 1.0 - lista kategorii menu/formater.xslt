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
	
	<!-- słowa formatowane do pisanych z tylko jednej dużej litery w tytule -->
	<xsl:variable name="corrected" select="'\GRATIS\'" />	
	
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
		<xsl:variable name="language" select="'eng'" />
				<!-- 2026.04.30 MD -->
				<xsl:variable name="nazwaTowaru">
					<xsl:choose>
						<xsl:when test="iaiext:pricecomparator_name 
							and iaiext:pricecomparator_name[@xml:lang = $language]/. != ''">
							<xsl:call-template name="wordFormat">
								<xsl:with-param name="text" select="substring(iaiext:pricecomparator_name[@xml:lang = $language]/., 1, 146)" tunnel="yes" />
							</xsl:call-template>
							<xsl:if test="string-length(iaiext:pricecomparator_name[@xml:lang = $language]/.) >= 146">
								<xsl:text disable-output-escaping="yes">...</xsl:text>
							</xsl:if>
						</xsl:when>
						<xsl:otherwise>
							<xsl:call-template name="wordFormat">
								<xsl:with-param name="text" select="substring(description/name[@xml:lang = $language]/., 1, 146)" tunnel="yes" />
							</xsl:call-template>
							<xsl:if test="string-length(description/name/.) >= 146 and description/name/. != ''">
								<xsl:text disable-output-escaping="yes">...</xsl:text>
							</xsl:if>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:variable>
				<xsl:variable name="upperCaseCount">
					<xsl:call-template name="upperCaseCount">
						<xsl:with-param name="text" select="$nazwaTowaru" />
					</xsl:call-template>
				</xsl:variable>
				<xsl:variable name="lowerCaseCount">
					<xsl:call-template name="lowerCaseCount">
						<xsl:with-param name="text" select="$nazwaTowaru" />
					</xsl:call-template>
				</xsl:variable>
		<xsl:for-each select="iaiext:navigation/iaiext:site/iaiext:menu[1]/iaiext:item">
			<xsl:element name="item">
				
				<xsl:text disable-output-escaping="yes">&lt;p&gt;</xsl:text>
				<xsl:value-of select="../../../../sizes/size/@code" />
				<xsl:text disable-output-escaping="yes">&lt;/p&gt;</xsl:text>
				
				<xsl:text disable-output-escaping="yes">&lt;p&gt;</xsl:text>
				<xsl:choose>
					<xsl:when test="($lowerCaseCount div $upperCaseCount) &lt; 0.3">
						<!-- wszystkie litery oprócz pierwszej i producenta zamienia na małe litery -->
						<xsl:variable name="lower-text">
							<xsl:value-of select="concat(substring($nazwaTowaru, 1, 1), translate(substring(normalize-space($nazwaTowaru), 2), $upperLetters, $lowerLetters))" />
						</xsl:variable>
						<xsl:choose>
							<xsl:when test="contains($lower-text, translate(producer/@name, $upperLetters, $lowerLetters))">
								<xsl:value-of select="substring-before($lower-text, translate(producer/@name, $upperLetters, $lowerLetters))" />
								<xsl:value-of select="producer/@name" />
								<xsl:value-of select="substring-after($lower-text, translate(producer/@name, $upperLetters, $lowerLetters))" />
							</xsl:when>
							<xsl:otherwise>
								<xsl:value-of select="$lower-text" />
							</xsl:otherwise>
						</xsl:choose>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="$nazwaTowaru" />
					</xsl:otherwise>
				</xsl:choose>
				<xsl:text disable-output-escaping="yes">&lt;/p&gt;</xsl:text>
				
				<xsl:text disable-output-escaping="yes">&lt;p&gt;</xsl:text>
				<xsl:call-template name="string-replace-all">
					<xsl:with-param name="text" select="@textid" />
					<xsl:with-param name="replace" select="'\'" />
					<xsl:with-param name="by" select="' &lt;/p&gt;&lt;p&gt;'" />
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
	
	<xsl:template name="wordFormat">
		<xsl:param name="text" />
		<xsl:param name="delimiter" select="' '" />
		<xsl:choose>
			<xsl:when test="contains($text, $delimiter) and not(contains(substring-before($text, $delimiter),'/'))">
				<xsl:variable name="word">
					<xsl:text><![CDATA[\]]></xsl:text>
					<xsl:value-of select="substring-before($text, $delimiter)" />
					<xsl:text><![CDATA[\]]></xsl:text>
				</xsl:variable>
				<xsl:choose>
					<xsl:when test="contains($corrected, $word)">
						<xsl:value-of select="substring(translate($word, '\', ''),1,1)" />
						<xsl:value-of select="translate(substring(translate($word, '\', ''),2), $upperLetters, $lowerLetters)" />
						<xsl:value-of select="$delimiter" />
						<xsl:call-template name="wordFormat">
							<xsl:with-param name="text" select="substring-after($text, $delimiter)" />
						</xsl:call-template>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="translate($word, '\', '')" />
						<xsl:value-of select="$delimiter" />
						<xsl:call-template name="wordFormat">
							<xsl:with-param name="text" select="substring-after($text, $delimiter)" />
						</xsl:call-template>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:when>
			<xsl:when test="contains($text, '/')">
				<xsl:variable name="word">
					<xsl:text><![CDATA[\]]></xsl:text>
					<xsl:value-of select="substring-before($text, '/')" />
					<xsl:text><![CDATA[\]]></xsl:text>
				</xsl:variable>
				<xsl:choose>
					<xsl:when test="contains($corrected, $word)">
						<xsl:value-of select="substring(translate($word, '\', ''),1,1)" />
						<xsl:value-of select="translate(substring(translate($word, '\', ''),2), $upperLetters, $lowerLetters)" />
						<xsl:text><![CDATA[/]]></xsl:text>
						<xsl:call-template name="wordFormat">
							<xsl:with-param name="text" select="substring-after($text, '/')" />
						</xsl:call-template>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="translate($word, '\', '')" />
						<xsl:text><![CDATA[/]]></xsl:text>
						<xsl:call-template name="wordFormat">
							<xsl:with-param name="text" select="substring-after($text, '/')" />
						</xsl:call-template>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:when>
			<xsl:otherwise>
				<xsl:variable name="word">
					<xsl:text><![CDATA[\]]></xsl:text>
					<xsl:value-of select="$text" />
					<xsl:text><![CDATA[\]]></xsl:text>
				</xsl:variable>
				<xsl:choose>
					<xsl:when test="contains($corrected, $word)">
						<xsl:value-of select="substring(translate($word, '\', ''),1,1)" />
						<xsl:value-of select="translate(substring(translate($word, '\', ''),2), $upperLetters, $lowerLetters)" />
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="translate($word, '\', '')" />
					</xsl:otherwise>
				</xsl:choose>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
	<!-- 03.07.2025 MD -->
	<xsl:template name="upperCaseCount"> 
		<xsl:param name="text"/> 
		<xsl:variable name="uppercaseOnly" select="translate($text, concat($lowerLetters,'0123456789., *%&amp;;\/-+()'), '')"/> 
		<xsl:value-of select="string-length($uppercaseOnly)"/> 
	</xsl:template> 
	<xsl:template name="lowerCaseCount"> 
		<xsl:param name="text"/> 
		<xsl:variable name="lowercaseOnly" select="translate($text, concat($upperLetters,'0123456789., *%&amp;;\/-+()'), '')"/> 
		<xsl:value-of select="string-length($lowercaseOnly)"/> 
	</xsl:template> 
</xsl:stylesheet>