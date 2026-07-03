<xsl:variable name="sell_by">
         <xsl:choose>
            <xsl:when test="../../iaiext:sell_by/iaiext:retail and ../../iaiext:sell_by/iaiext:retail/@quantity > 0">
               <xsl:value-of select="../../iaiext:sell_by/iaiext:retail/@quantity" />
            </xsl:when>
            <xsl:when test="iaiext:sell_by/iaiext:retail and iaiext:sell_by/iaiext:retail/@quantity > 0">
               <xsl:value-of select="iaiext:sell_by/iaiext:retail/@quantity" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:text>1</xsl:text>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>
      <xsl:variable name="size_id">
         <xsl:choose>
            <xsl:when test="@name!=''">
               <xsl:value-of select="@id" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:text>-</xsl:text>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>
      <xsl:variable name="product_currency">
         <xsl:choose>
            <xsl:when test="../../@currency!=''">
               <xsl:value-of select="../../@currency" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="@currency" />
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>
      <xsl:variable name="cena_serwis">
         <xsl:choose>
            <xsl:when test="../../iaiext:pricecomparator_price/iaiext:site">
               <xsl:value-of select="../../iaiext:pricecomparator_price/iaiext:site/@gross" />
            </xsl:when>
            <xsl:when test="iaiext:pricecomparator_price/iaiext:site">
               <xsl:value-of select="iaiext:pricecomparator_price/iaiext:site/@gross" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:text>0</xsl:text>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>
      <xsl:variable name="cena_przekreslona">
         <xsl:choose>
            <xsl:when test="sizes/size/strikethrough_retail_price">
               <xsl:value-of select="sizes/size/strikethrough_retail_price/@gross" />
            </xsl:when>
            <xsl:when test="strikethrough_retail_price">
               <xsl:value-of select="strikethrough_retail_price/@gross" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:text>0</xsl:text>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>
      <xsl:variable name="cena_przedpromocyjna">
         <xsl:choose>
            <xsl:when test="../../promotion/price/normal_retail_price/iaiext:site/iaiext:price_per_size[@id = $size_id]/@panel_name != '' and
                            ../../promotion/price/normal_retail_price/iaiext:site/iaiext:price_per_size[@id = $size_id]/@gross > price/@gross">
               <xsl:value-of select="../../promotion/price/normal_retail_price/iaiext:site/iaiext:price_per_size[@id = $size_id]/@gross" />
            </xsl:when>
            <xsl:when test="../../promotion/price/normal_retail_price and ../../promotion/price/normal_retail_price/@gross > price/@gross">
               <xsl:value-of select="../../promotion/price/normal_retail_price/@gross" />
            </xsl:when>
            <xsl:when test="promotion/price/normal_retail_price/iaiext:site/iaiext:price_per_size[@id = $size_id]/@panel_name != '' and
                            promotion/price/normal_retail_price/iaiext:site/iaiext:price_per_size[@id = $size_id]/@gross > price/@gross">
               <xsl:value-of select="promotion/price/normal_retail_price/iaiext:site/iaiext:price_per_size[@id = $size_id]/@gross" />
            </xsl:when>
            <xsl:when test="promotion/price/normal_retail_price and promotion/price/normal_retail_price/@gross > price/@gross">
               <xsl:value-of select="promotion/price/normal_retail_price/@gross" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:text>0</xsl:text>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>
      <xsl:variable name="mainPrice">
         <xsl:choose>
            <xsl:when test="$cena_serwis > 0">
               <xsl:choose>
                  <xsl:when test="$cena_przedpromocyjna > $cena_serwis or $cena_przekreslona > $cena_serwis">
                     <xsl:choose>
                        <xsl:when test="$cena_przedpromocyjna > 0 and $cena_przedpromocyjna > $cena_przekreslona">
                           <xsl:value-of select="$cena_przedpromocyjna" />
                        </xsl:when>
                        <xsl:otherwise>
                           <xsl:value-of select="$cena_przekreslona" />
                        </xsl:otherwise>
                     </xsl:choose>
                  </xsl:when>
                  <xsl:otherwise>
                     <xsl:value-of select="$cena_serwis" />
                  </xsl:otherwise>
               </xsl:choose>
            </xsl:when>
            <xsl:otherwise>
               <xsl:choose>
                  <xsl:when test="$cena_przedpromocyjna > price/@gross or $cena_przekreslona > price/@gross">
                     <xsl:choose>
                        <xsl:when test="$cena_przedpromocyjna > 0 and $cena_przedpromocyjna > $cena_przekreslona">
                           <xsl:value-of select="$cena_przedpromocyjna" />
                        </xsl:when>
                        <xsl:otherwise>
                           <xsl:value-of select="$cena_przekreslona" />
                        </xsl:otherwise>
                     </xsl:choose>
                  </xsl:when>
                  <xsl:otherwise>
                     <xsl:value-of select="price/@gross" />
                  </xsl:otherwise>
               </xsl:choose>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>
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