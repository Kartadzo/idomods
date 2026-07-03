<!-- długość opisu -->
<xsl:variable name='dlugosc_opisu'>2400</xsl:variable>
<xsl:variable name='dlugosc_opisu_z_parametrow'>1200</xsl:variable>
<xsl:variable name='zignoruj_dlugi_opis_jesli_krotki_przekracza'>600</xsl:variable>

<!-- wymagany limit długości opisu po którego przekroczeniu nie zostanie dodany opis z parametrów  -->
<xsl:variable name='minimalna_dlugosc_opisu_dla_parametrow'>120</xsl:variable>

<!-- 2026.06.18 MD -->
<xsl:variable name="from_parameters_raw">
   <xsl:for-each select="parameters/parameter[@hide = 'n' and value/@name != '']">
      <xsl:text>&#xa;</xsl:text>
      <xsl:value-of select="@name" />
      <xsl:text>: </xsl:text>
      <xsl:for-each select="value">
         <xsl:value-of select="@name" />
         <xsl:text>; </xsl:text>
      </xsl:for-each>
   </xsl:for-each>
</xsl:variable>
<xsl:variable name="from_parameters">
   <xsl:choose>
      <xsl:when test="$from_parameters_raw != ''">
         <xsl:call-template name="tokenize">
            <xsl:with-param name="text" select="substring($from_parameters_raw, 1, $dlugosc_opisu_z_parametrow)" />
            <xsl:with-param name="delimiter" select="';'" />
         </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
         <xsl:text></xsl:text>
      </xsl:otherwise>
   </xsl:choose>
</xsl:variable>
<xsl:element name="g:description">
   <xsl:choose>
      <xsl:when test="description/short_desc = '' and description/long_desc = ''">
         <!-- nie jest git bo nie ma opisów  -->
         <xsl:if test="$from_parameters != ''">
            <xsl:value-of select="description/name" />
            <xsl:value-of select="$from_parameters" />
         </xsl:if>
      </xsl:when>
      <xsl:when test="description/short_desc = '' and string-length(normalize-space(description/long_desc)) > 0">
         <xsl:variable name = "opis_bez_twardych_spacji">
            <xsl:call-template name="string-replace-all">
               <xsl:with-param name="text" select="description/long_desc" tunnel="yes"/>
               <xsl:with-param name="replace" select="'&amp;nbsp;'" tunnel="yes"/>
               <xsl:with-param name="by" select="' '" tunnel="yes"/>
            </xsl:call-template>
         </xsl:variable>
         <xsl:variable name = "opis_bez_komentarzy">
            <xsl:call-template name="strip-tags">
               <xsl:with-param name="text" select="$opis_bez_twardych_spacji" />
               <xsl:with-param name="open" select="'&lt;!--'" />
               <xsl:with-param name="close" select="'--&gt;'" />
            </xsl:call-template>
         </xsl:variable>
         <xsl:variable name = "opis_bez_styli">
            <xsl:call-template name="strip-tags">
               <xsl:with-param name="text" select="$opis_bez_komentarzy" />
               <xsl:with-param name="open" select="'&lt;style'" />
               <xsl:with-param name="close" select="'&lt;/style&gt;'" />
            </xsl:call-template>
         </xsl:variable>
         <xsl:variable name = "opis_bez_zdjęć">
            <xsl:call-template name="strip-tags">
               <xsl:with-param name="text" select="$opis_bez_styli" />
               <xsl:with-param name="open" select="'&lt;img'" />
               <xsl:with-param name="close" select="'&quot;/&gt;'" />
            </xsl:call-template>
         </xsl:variable>
         <xsl:variable name = "opis_bez_tagow">
            <xsl:call-template name="strip-tags">
               <xsl:with-param name="text" select="$opis_bez_zdjęć" tunnel="yes"/>
            </xsl:call-template>
         </xsl:variable>
         <xsl:variable name="opis_do_kropki">
            <xsl:call-template name="tokenize">
               <xsl:with-param name="text" select="substring(normalize-space($opis_bez_tagow),1,$dlugosc_opisu)" />
            </xsl:call-template>
         </xsl:variable>
         <xsl:choose>
            <xsl:when test="$opis_do_kropki = ''">
               <!-- Nie ma przed kropka nic wiec podajemy co mamy bo mozliwe ze wgl nie
                    ma kropki lool-->
               <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
               <xsl:value-of select="normalize-space($opis_bez_tagow)" />
               <xsl:if test="string-length(normalize-space($opis_bez_tagow)) &lt; $minimalna_dlugosc_opisu_dla_parametrow and $from_parameters != ''">
                  <xsl:text>&#xa;</xsl:text>
                  <xsl:value-of select="description/name" />
                  <xsl:value-of select="$from_parameters" />
               </xsl:if>
               <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
            </xsl:when>
            <xsl:otherwise>
               <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
               <xsl:value-of select="normalize-space($opis_do_kropki)" />
               <xsl:if test="string-length(normalize-space($opis_do_kropki)) &lt; $minimalna_dlugosc_opisu_dla_parametrow and $from_parameters != ''">
                  <xsl:text>&#xa;</xsl:text>
                  <xsl:value-of select="description/name" />
                  <xsl:value-of select="$from_parameters" />
               </xsl:if>
               <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
         <!-- tutaj jeśli opis nie bedzie mial X znakow to zastapic go długim opisem mimo
              wszystko -->
         <!-- załóżmy -->
         <xsl:choose>
            <xsl:when test="string-length(description/short_desc) > $zignoruj_dlugi_opis_jesli_krotki_przekracza or description/long_desc = ''">
               <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
               <xsl:value-of select="description/short_desc" />
               <xsl:if test="string-length(description/short_desc) &lt; $minimalna_dlugosc_opisu_dla_parametrow and $from_parameters != ''">
                  <xsl:text>&#xa;</xsl:text>
                  <xsl:value-of select="description/name" />
                  <xsl:value-of select="$from_parameters" />
               </xsl:if>
               <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
            </xsl:when>
            <xsl:otherwise>
               <xsl:variable name = "opis_bez_twardych_spacji">
                  <xsl:call-template name="string-replace-all">
                     <xsl:with-param name="text" select="description/long_desc" tunnel="yes"/>
                     <xsl:with-param name="replace" select="'&amp;nbsp;'" tunnel="yes"/>
                     <xsl:with-param name="by" select="' '" tunnel="yes"/>
                  </xsl:call-template>
               </xsl:variable>
               <xsl:variable name = "opis_bez_komentarzy">
                  <xsl:call-template name="strip-tags">
                     <xsl:with-param name="text" select="$opis_bez_twardych_spacji" />
                     <xsl:with-param name="open" select="'&lt;!--'" />
                     <xsl:with-param name="close" select="'--&gt;'" />
                  </xsl:call-template>
               </xsl:variable>
               <xsl:variable name = "opis_bez_styli">
                  <xsl:call-template name="strip-tags">
                     <xsl:with-param name="text" select="$opis_bez_komentarzy" />
                     <xsl:with-param name="open" select="'&lt;style'" />
                     <xsl:with-param name="close" select="'&lt;/style&gt;'" />
                  </xsl:call-template>
               </xsl:variable>
               <xsl:variable name = "opis_bez_zdjęć">
                  <xsl:call-template name="strip-tags">
                     <xsl:with-param name="text" select="$opis_bez_styli" />
                     <xsl:with-param name="open" select="'&lt;img'" />
                     <xsl:with-param name="close" select="'&quot;/&gt;'" />
                  </xsl:call-template>
               </xsl:variable>
               <xsl:variable name = "opis_bez_tagow">
                  <xsl:call-template name="strip-tags">
                     <xsl:with-param name="text" select="$opis_bez_zdjęć" tunnel="yes"/>
                  </xsl:call-template>
               </xsl:variable>
               <xsl:variable name="opis_do_kropki">
                  <xsl:call-template name="tokenize">
                     <xsl:with-param name="text" select="substring(normalize-space($opis_bez_tagow),1,$dlugosc_opisu)" />
                  </xsl:call-template>
               </xsl:variable>
               <xsl:choose>
                  <xsl:when test="$opis_do_kropki = ''">
                     <!-- Nie ma przed kropka nic wiec podajemy co mamy bo mozliwe ze
                          wgl nie ma kropki lool-->
                     <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
                     <xsl:value-of select="normalize-space($opis_bez_tagow)" />
                     <xsl:if test="string-length(normalize-space($opis_bez_tagow)) &lt; $minimalna_dlugosc_opisu_dla_parametrow and $from_parameters != ''">
                        <xsl:text>&#xa;</xsl:text>
                        <xsl:value-of select="description/name" />
                        <xsl:value-of select="$from_parameters" />
                     </xsl:if>
                     <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
                  </xsl:when>
                  <xsl:otherwise>
                     <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
                     <xsl:value-of select="normalize-space($opis_do_kropki)" />
                     <xsl:if test="string-length(normalize-space($opis_do_kropki)) &lt; $minimalna_dlugosc_opisu_dla_parametrow and $from_parameters != ''">
                        <xsl:text>&#xa;</xsl:text>
                        <xsl:value-of select="description/name" />
                        <xsl:value-of select="$from_parameters" />
                     </xsl:if>
                     <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
                  </xsl:otherwise>
               </xsl:choose>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:otherwise>
   </xsl:choose>
</xsl:element>