<xsl:element name="g:price">
         <xsl:value-of select="$mainPrice" />
         <xsl:text><![CDATA[ ]]></xsl:text>
         <xsl:value-of select="$product_currency" />
      </xsl:element>
      <!-- produkcja -->
      <!-- pierwszeństwo dla ceny serwis; jesli bedzie promocja lub przekreślona cena to od razu promocyjna cene większa od
           normalnej-->
      <xsl:choose>
         <xsl:when test="$cena_serwis > 0 and $mainPrice > $cena_serwis">
            <xsl:element name="g:sale_price">
               <xsl:value-of select="$cena_serwis" />
               <xsl:text><![CDATA[ ]]></xsl:text>
               <xsl:value-of select="$product_currency" />
            </xsl:element>
         </xsl:when>
         <xsl:when test="$mainPrice > price/@gross and 0 = $cena_serwis">
            <xsl:element name="g:sale_price">
               <xsl:value-of select="price/@gross" />
               <xsl:text><![CDATA[ ]]></xsl:text>
               <xsl:value-of select="$product_currency" />
            </xsl:element>
         </xsl:when>
      </xsl:choose>
