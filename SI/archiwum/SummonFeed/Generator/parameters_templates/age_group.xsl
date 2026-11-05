
   <!-- dane potrzebne aby przekazywać informacje o grupie wiekowej - nazwa parametru lub id w kategorii menu -->
   <xsl:variable name='age_group_nazwa_w_panelu'></xsl:variable>
   <xsl:variable name='age_group_newborn'>|</xsl:variable>
   <xsl:variable name='age_group_infant'>|</xsl:variable>
   <xsl:variable name='age_group_toddler'>|</xsl:variable>
   <xsl:variable name='age_group_kids'>|</xsl:variable>
   <xsl:variable name='age_group_adult'>|</xsl:variable>
   <!-- Jeśli 'age_group_id_w_menu' nie będzie puste to skrypt zacznie sprawdzać id węzłów menu nawigacyjnego -->
   <xsl:variable name='age_group_id_w_menu'></xsl:variable>
   <xsl:variable name='age_group_newborn_id_menu'>|</xsl:variable>
   <xsl:variable name='age_group_infant_id_menu'>|</xsl:variable>
   <xsl:variable name='age_group_toddler_id_menu'>|</xsl:variable>
   <xsl:variable name='age_group_kids_id_menu'>|</xsl:variable>
   <xsl:variable name='age_group_adult_id_menu'>|</xsl:variable>

      <!-- 2026.05.07 MD -->
      <!-- wiek -->
      <xsl:if test="$age_group_id_w_menu = '*' 
                    or $age_group_id_w_menu != '' and iaiext:priority_menu/site/menu[1]/item[contains($age_group_id_w_menu, concat('|',translate(@id, $upperLetters, $lowerLetters),'|'))]/@textId 
                    or $age_group_nazwa_w_panelu != '' and parameters/parameter[@name = $age_group_nazwa_w_panelu]/value/@name != ''">
         <xsl:element name="g:age_group">
            <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
            <xsl:variable name='age_wer'>
               <xsl:text>|</xsl:text>
               <xsl:value-of select="parameters/parameter[@name = $age_group_nazwa_w_panelu]/value/@name" />
               <xsl:text>|</xsl:text>
            </xsl:variable>
            <xsl:choose>
               <xsl:when test="contains($age_group_newborn, $age_wer) or 
                               contains($age_group_newborn_id_menu, concat('|',iaiext:priority_menu/site/menu[1]/item/@id,'|'))">
                  <![CDATA[newborn]]>
               </xsl:when>
               <xsl:when test="contains($age_group_infant, $age_wer) or 
                               contains($age_group_infant_id_menu, concat('|',iaiext:priority_menu/site/menu[1]/item/@id,'|'))">
                  <![CDATA[infant]]>
               </xsl:when>
               <xsl:when test="contains($age_group_toddler, $age_wer) or 
                               contains($age_group_toddler_id_menu, concat('|',iaiext:priority_menu/site/menu[1]/item/@id,'|'))">
                  <![CDATA[toddler]]>
               </xsl:when>
               <xsl:when test="contains($age_group_kids, $age_wer) or 
                               contains($age_group_kids_id_menu, concat('|',iaiext:priority_menu/site/menu[1]/item/@id,'|'))">
                  <![CDATA[kids]]>
               </xsl:when>
               <xsl:when test="contains($age_group_adult, $age_wer) or 
                               contains($age_group_adult_id_menu, concat('|',iaiext:priority_menu/site/menu[1]/item/@id,'|'))">
                  <![CDATA[adult]]>
               </xsl:when>
               <xsl:when test="$age_group_id_w_menu = '*'">
                  <![CDATA[adult]]>
               </xsl:when>
            </xsl:choose>
            <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
         </xsl:element>
      </xsl:if>
