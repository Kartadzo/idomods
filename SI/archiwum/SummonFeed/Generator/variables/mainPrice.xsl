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
