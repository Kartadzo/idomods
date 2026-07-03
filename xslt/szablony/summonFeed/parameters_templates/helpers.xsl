<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
   <!-- Helper templates extracted from Facebook.xml for use by fragment generators -->
   
   <!-- 2026.05.07  MD -->
   <xsl:template name="strip-tags">
      <xsl:param name="text" />
      <xsl:param name="open" select="'&lt;'" />
      <xsl:param name="close" select="'&gt;'" />
      <xsl:param name="depth" select="0" />
      <xsl:choose>
         <xsl:when test="contains($text, $open) and not(contains(substring-after($text, $open), $close))">
            <xsl:value-of select="normalize-space($text)" />
         </xsl:when>
         <xsl:when test="contains($text, $open) and $depth &lt; 1000">
            <xsl:value-of select="substring-before($text, $open)" />
            <xsl:text><![CDATA[ ]]></xsl:text>
            <xsl:call-template name="strip-tags">
               <xsl:with-param name="text" select="substring-after($text, $close)" />
               <xsl:with-param name="open" select="$open" />
               <xsl:with-param name="close" select="$close" />
               <xsl:with-param name="depth" select="$depth + 1" />
            </xsl:call-template>
         </xsl:when>
         <xsl:otherwise>
            <xsl:value-of select="normalize-space($text)" />
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
   
   <xsl:template name="tokenize">
      <xsl:param name="text" />
      <xsl:param name="delimiter" select="'.'" />
      <xsl:param name="depth" select="0" />
      <xsl:choose>
         <xsl:when test="contains($text, $delimiter) and $depth &lt; 1000">
            <xsl:value-of select="substring-before($text, $delimiter)" />
            <xsl:value-of select="$delimiter" />
            <xsl:call-template name="tokenize">
               <xsl:with-param name="text" select="substring-after($text, $delimiter)" />
               <xsl:with-param name="delimiter" select="$delimiter" />
               <xsl:with-param name="depth" select="$depth + 1" />
            </xsl:call-template>
         </xsl:when>
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
   
   <xsl:template name="string-replace-all">
      <xsl:param name="text" />
      <xsl:param name="replace" />
      <xsl:param name="by" />
      <xsl:param name="depth" select="0" />
      <xsl:choose>
         <xsl:when test="contains($text, $replace) and $depth &lt; 1000">
            <xsl:value-of select="substring-before($text,$replace)" />
            <xsl:value-of select="$by" />
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
   
   <!-- 08.10.2025 MD -->
   <xsl:template name="throwLastNode">
      <xsl:param name="text" />
      <xsl:param name="delimiter" select="'\'" />
      <xsl:choose>
         <xsl:when test="not(contains($text, $delimiter))">
            <xsl:value-of select="$text" />
         </xsl:when>
         <xsl:otherwise>
            <xsl:call-template name="throwLastNode">
               <xsl:with-param name="text" select="substring-after($text, $delimiter)" tunnel="yes" />
               <xsl:with-param name="delimiter" select="$delimiter" tunnel="yes" />
            </xsl:call-template>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
   
   <!-- 2026.02.12 MD -->
   <xsl:template name="throwNode">
      <xsl:param name="pos" select="1"/>
      <xsl:param name="index" />
      <xsl:param name="prev" select="''"/>
      <xsl:param name="border" select="'\'"/>
      
      <xsl:variable name="items" select="iaiext:priority_menu/site[1]/menu[1]/item[contains(@textId,$border)]"/>
      <xsl:variable name="total" select="count($items)"/>
      
      <xsl:choose>
         <xsl:when test="$pos &gt; $total">
            <xsl:if test="string-length($prev) > 2">
               <xsl:value-of select="$prev"/>
            </xsl:if>
         </xsl:when>
         <xsl:otherwise>
            <xsl:variable name="node">
               <xsl:call-template name="extract-node">
                  <xsl:with-param name="text"  select="$items[$pos]/@textId"/>
                  <xsl:with-param name="index" select="$index"/>
               </xsl:call-template>
            </xsl:variable>
            
            <xsl:variable name="nodeNorm" select="normalize-space($node)"/>
            
            <xsl:variable name="result">
               <xsl:value-of select="$prev"/>
               <xsl:if test="string-length($nodeNorm) > 0 
                  and not(contains(concat(';', $prev, ';'),concat('; ', $nodeNorm, ';')) 
                     or contains(concat(';', $prev, ';'),concat(';', $nodeNorm, ';')))">
                  <xsl:value-of select="$nodeNorm"/>
                  <xsl:text>; </xsl:text>
               </xsl:if>
            </xsl:variable>
            <xsl:call-template name="throwNode">
               <xsl:with-param name="pos"      select="$pos +1"/>
               <xsl:with-param name="index"    select="$index"/>
               <xsl:with-param name="prev"     select="$result"/>	
               <xsl:with-param name="border"   select="$border"/>
            </xsl:call-template>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
   
   <!-- 08.09.2025 MD -->
   <xsl:template name="extract-node">
      <xsl:param name="text"/>
      <xsl:param name="index"/>
      <xsl:param name="counter" select="1"/>
      
      <xsl:choose>
         <xsl:when test="not(contains($text,'\'))">
            <xsl:if test="$counter = $index">
               <xsl:value-of select="$text"/>
            </xsl:if>
         </xsl:when>
         <xsl:otherwise>
            <xsl:variable name="head">
               <xsl:choose> 
                  <xsl:when test="contains($text,' \ ')"> 
                     <xsl:value-of select="substring-before($text,' \ ')"/>
                  </xsl:when> 
                  <xsl:otherwise>
                     <xsl:value-of select="substring-before($text,'\')"/>
                  </xsl:otherwise> 
               </xsl:choose>
            </xsl:variable>
            <xsl:variable name="tail">
               <xsl:choose> 
                  <xsl:when test="contains($text,' \ ')"> 
                     <xsl:value-of select="substring-after($text,' \ ')"/>
                  </xsl:when> 
                  <xsl:otherwise>
                     <xsl:value-of select="substring-after($text,'\')"/>
                  </xsl:otherwise> 
               </xsl:choose>
            </xsl:variable>
            
            <xsl:if test="$counter = $index">
               <xsl:value-of select="$head"/>
            </xsl:if>
            
            <xsl:call-template name="extract-node">
               <xsl:with-param name="text"     select="$tail"/>
               <xsl:with-param name="index"    select="$index"/>
               <xsl:with-param name="counter"  select="$counter + 1"/>
            </xsl:call-template>
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
   
   <!-- 2026.06.03 MD -->
   <xsl:template name="extract-measure">
      <xsl:param name="str"/>
      
      <xsl:variable name="token" select="substring-before(concat($str,' '),' ')"/>
      <xsl:variable name="rest"  select="substring-after($str,' ')"/>
      
      <xsl:variable name="clean" select="translate($token,'*%&amp;;\/-+()','')"/>
      
      <xsl:choose>
         <!-- 1) format: 500ml, 1,5l, 1.5l -->
         <xsl:when test="
            translate($clean,'0123456789.,','') != '' and
            contains($unitsList, concat('|', translate($clean,'0123456789.,',''), '|')) and
            string-length(translate($clean,'0123456789.,','')) &gt; 0 and
            string-length(translate($clean,'0123456789.,','')) &lt; 4 and
            string-length(translate($clean,'0123456789','')) &lt; string-length($clean)
                     ">
            <xsl:value-of select="$clean"/>
         </xsl:when>
         <!-- 2) format: 500 ml, 1,5 l, 1.5 l, 15 kg -->
         <xsl:when test="
            translate($clean,'0123456789.,','') = '' and
            string-length($clean) &gt; 0 and
            string-length(translate($clean,'0123456789','')) &lt; string-length($clean) and
            contains($unitsList, concat('|', substring-before(concat($rest,' '),' '), '|')) and
            not(contains($unitsList, concat('|', $clean, '|')))
                     ">
            <xsl:value-of select="concat($clean, ' ', substring-before(concat($rest,' '),' '))"/>
         </xsl:when>
         <!-- 3) format: 4x500ml, 4x1,5l, 4x1.5l -->
         <xsl:when test="
            contains($clean,'x') and
            translate(substring-before($clean,'x'),'0123456789.,','') = '' and
            translate(substring-after($clean,'x'),'0123456789.,','') != '' and
            contains($unitsList, concat('|', translate(substring-after($clean,'x'),'0123456789.,',''), '|'))
                     ">
            <xsl:value-of select="$clean"/>
         </xsl:when>
         <!-- 4) format: 4 x 500ml, 4 x 1,5l, 4 x 1.5l -->
         <xsl:when test="
            translate($clean,'0123456789.,','') = '' and
            substring($rest,2,1) = 'x'
                     ">
            <xsl:variable name="afterX" select="substring($rest,3)"/>
            <xsl:if test="
               translate($afterX,'0123456789.,','') != '' and
               contains($unitsList, concat('|', translate($afterX,'0123456789.,',''), '|'))
                     ">
               <xsl:value-of select="concat($clean, ' x ', $afterX)"/>
            </xsl:if>
         </xsl:when>
         <xsl:when test="$rest != ''">
            <xsl:call-template name="extract-measure">
               <xsl:with-param name="str" select="$rest"/>
            </xsl:call-template>
         </xsl:when>
         <xsl:otherwise/>
      </xsl:choose>
   </xsl:template>
   
   <xsl:template name="normalize-measure">
      <xsl:param name="value"/>
      
      <xsl:variable name="clean" select="normalize-space(translate($value,'*%&amp;;\/-+() ',''))"/>
      
      <xsl:choose>
         <!-- 1) format NxMunit (np. 4x120g, 3x1,5l, 4x500 ml) -->
         <xsl:when test="contains($clean,'x')">
            <xsl:variable name="left"  select="substring-before($clean,'x')"/>
            <xsl:variable name="right" select="substring-after($clean,'x')"/>
            
            <xsl:value-of select="concat(number(translate($left,',','.')) * number(translate($right,'abcdefghijklmnopqrstuvwxyz,','.' ))
                  , ' '
                  , substring-before(concat(translate($right,'0123456789.,',''),' '),' '))"/>
         </xsl:when>
         <!-- 2) format liczba + jednostka (np. 500ml, 1,5l, 15kg) -->
         <xsl:when test="
            translate($clean,'0123456789.,','') != '' and
            string-length(translate($clean,'0123456789','')) &lt; string-length($clean)
                     ">
            <xsl:value-of select="concat(translate(substring-before($clean,translate($clean,'0123456789.,','')),',','.'), ' ', translate($clean,'0123456789.,',''))"/>
         </xsl:when>
         <!-- 3) format liczba + spacja + jednostka (np. 500 ml, 1,5 l, 15 kg) -->
         <xsl:when test="
            contains($clean,' ') and
            translate(substring-before($clean,' '),'0123456789.,','') = ''
                     ">
            <xsl:value-of select="concat(translate(substring-before($clean,' '),',','.'), ' ', substring-before(concat(substring-after($clean,' '),' '),' '))"/>
         </xsl:when>
         <xsl:otherwise/>
      </xsl:choose>
   </xsl:template>
   
   <!-- 2026.06.18 MD -->
   <xsl:template name="normalize-polish-pairs">
      <xsl:param name="text"/>
      
      <xsl:variable name="hasPair">
         <xsl:call-template name="has-polish-pair">
            <xsl:with-param name="tmp" select="$text"/>
         </xsl:call-template>
      </xsl:variable>
      
      <xsl:choose>
         <xsl:when test="$hasPair = 'true'">
            <xsl:value-of select="translate($text, 'ĄĆĘŁŃÓŚŹŻ', 'ACELNOSZZ')"/>
         </xsl:when>
         <xsl:otherwise>
            <xsl:value-of select="$text"/>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
   
   <xsl:template name="has-polish-pair">
      <xsl:param name="tmp"/>
      
      <xsl:variable name="pl" select="'ĄĆĘŁŃÓŚŹŻ'"/>
      
      <xsl:choose>
         <xsl:when test="string-length($tmp) &lt; 2">
            <xsl:text>false</xsl:text>
         </xsl:when>
         <xsl:when test="
            contains($pl, substring($tmp,1,1))
            and contains($pl, substring($tmp,2,1))
                     ">
            <xsl:text>true</xsl:text>
         </xsl:when>
         <xsl:otherwise>
            <xsl:call-template name="has-polish-pair">
               <xsl:with-param name="tmp" select="substring($tmp,2)"/>
            </xsl:call-template>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
   
   <xsl:template name="searchGoogleCategory">
      <xsl:param name="cat_id" />
      <xsl:choose>
         <xsl:when test="$cat_id = '6675'">
            <xsl:value-of select="'1604'" />
         </xsl:when>
         <xsl:when test="$cat_id = '4571'">
            <xsl:value-of select="'2271'" />
         </xsl:when>
         <xsl:when test="$cat_id = '5977'">
            <xsl:value-of select="'187'" />
         </xsl:when>
         <xsl:otherwise>
            <xsl:text>0</xsl:text>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
</xsl:stylesheet>
