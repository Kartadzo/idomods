<!-- dane potrzebne aby przekazywać informacje o płci - nazwa parametru lub id w kategorii menu -->
   <!-- Przykłady można edytować -->
   <xsl:variable name='gender_nazwa_w_panelu'></xsl:variable>
   <xsl:variable name='gender_male'>|</xsl:variable>
   <xsl:variable name='gender_female'>|</xsl:variable>
   <xsl:variable name='gender_unisex'>|</xsl:variable>
   <!-- Jeśli 'gender_id_w_panelu' nie będzie puste to skrypt zacznie sprawdzać id węzłów menu nawigacyjnego -->
   <xsl:variable name='gender_id_w_panelu'></xsl:variable>
   <xsl:variable name='gender_male_id_menu'>|</xsl:variable>
   <xsl:variable name='gender_female_id_menu'>|</xsl:variable>
   <xsl:variable name='gender_unisex_id_menu'>|</xsl:variable>

      
      <!-- 2026.05.07 MD -->
      <!-- płeć -->
      <xsl:if test="substring($gender_id_w_panelu, 1, 1) = '*'
                    or $gender_id_w_panelu != ''  and iaiext:priority_menu/site/menu[1]/item[contains($gender_id_w_panelu, concat('|',translate(@id, $upperLetters, $lowerLetters),'|'))]/@textId 
                    or $gender_nazwa_w_panelu != '' and parameters/parameter[@name = $gender_nazwa_w_panelu]/value/@name != ''">
         <xsl:element name="g:gender">
            <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
            <xsl:variable name='gender_wer'>
               <xsl:text>|</xsl:text>
               <xsl:value-of select="parameters/parameter[@name = $gender_nazwa_w_panelu]/value/@name" />
               <xsl:text>|</xsl:text>
            </xsl:variable>
            <xsl:choose>
               <xsl:when test="contains($gender_male, $gender_wer)">
                  <![CDATA[male]]>
               </xsl:when>
               <xsl:when test="contains($gender_female, $gender_wer)">
                  <![CDATA[female]]>
               </xsl:when>
               <xsl:when test="contains($gender_unisex, $gender_wer)">
                  <![CDATA[unisex]]>
               </xsl:when>
               <xsl:when test="contains($gender_male_id_menu, concat('|',iaiext:priority_menu/site/menu[1]/item/@id,'|'))">
                  <![CDATA[male]]>
               </xsl:when>
               <xsl:when test="contains($gender_female_id_menu, concat('|',iaiext:priority_menu/site/menu[1]/item/@id,'|'))">
                  <![CDATA[female]]>
               </xsl:when>
               <xsl:when test="contains($gender_unisex_id_menu, concat('|',iaiext:priority_menu/site/menu[1]/item/@id,'|'))">
                  <![CDATA[unisex]]>
               </xsl:when>
               <xsl:when test="substring($gender_id_w_panelu, 1, 1) = '*'">
                  <xsl:value-of select="substring-after($gender_id_w_panelu,'*')" />
               </xsl:when>
            </xsl:choose>
            <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
         </xsl:element>
      </xsl:if>