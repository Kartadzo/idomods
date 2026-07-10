<!-- SZABLON parametru. Pliki '_*' są pomijane przez generator.
     Skopiuj jako nazwa_parametru.xsl (ta sama nazwa bazowa co .json).

     ZASADA: ten plik zawiera WYŁĄCZNIE emisję elementu wyjściowego.
       • zmienne obliczeniowe na poziomie szablonu  → variables/nazwa.xsl + wpis w variables/_registry.json,
         a nazwy wypisz w "createVars" (wtedy generator wstrzyknie je w preambule, raz i w dobrej kolejności);
       • zmienne branch-local (wewnątrz <xsl:when>/<xsl:if>, zależne od zmiennych tej gałęzi)
         ZOSTAJĄ tutaj — nie da się ich wynieść;
       • configVary NIE deklaruj tutaj, jeśli parametr jest 'zmigrowany' (createVars w rejestrze) —
         generator wygeneruje ich deklaracje w preambule;
       • zmiennych globalnych ($upperLetters, $Kraj_dostawy, …) NIE deklaruj — są auto-wstrzykiwane
         po <xsl:output>, gdy tylko pojawi się referencja $nazwa;
       • helpery wołaj przez <xsl:call-template name="..."/> i wypisz w "helpers" w .json.

     Kontekst węzła bieżącego zależy od pola "context" w .json:
       product → bieżący <product>,  size → bieżący <size>,  feed → poziom arkusza.
-->
<xsl:element name="g:nazwa_elementu">
   <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
   <xsl:value-of select="sciezka/do/pola" />
   <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
</xsl:element>