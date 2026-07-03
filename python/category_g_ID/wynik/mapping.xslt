<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <xsl:variable name="cat_id" select="category_idosell/@id"/>
    <xsl:choose>
      <xsl:when test="$cat_id = '4404'">
        <xsl:value-of select='100' />
      </xsl:when>
      <xsl:when test="$cat_id = '4405'">
        <xsl:value-of select='104' />
      </xsl:when>
      <xsl:when test="$cat_id = '3633'">
        <xsl:value-of select='1129' />
      </xsl:when>
      <xsl:when test="$cat_id = '2576'">
        <xsl:value-of select='1130' />
      </xsl:when>
      <xsl:when test="$cat_id = '3653'">
        <xsl:value-of select='1143' />
      </xsl:when>
      <xsl:when test="$cat_id = '3606'">
        <xsl:value-of select='1147' />
      </xsl:when>
      <xsl:when test="$cat_id = '3664'">
        <xsl:value-of select='1148' />
      </xsl:when>
      <xsl:when test="$cat_id = '2016'">
        <xsl:value-of select='1239' />
      </xsl:when>
      <xsl:when test="$cat_id = '6704' or $cat_id = '6725'">
        <xsl:value-of select='1604' />
      </xsl:when>
      <xsl:when test="$cat_id = '4466'">
        <xsl:value-of select='169' />
      </xsl:when>
      <xsl:when test="$cat_id = '6029' or $cat_id = '6030'">
        <xsl:value-of select='173' />
      </xsl:when>
      <xsl:when test="$cat_id = '4464'">
        <xsl:value-of select='178' />
      </xsl:when>
      <xsl:when test="$cat_id = '4494' or $cat_id = '5985' or $cat_id = '6005'">
        <xsl:value-of select='187' />
      </xsl:when>
      <xsl:when test="$cat_id = '4575'">
        <xsl:value-of select='207' />
      </xsl:when>
      <xsl:when test="$cat_id = '4551'">
        <xsl:value-of select='212' />
      </xsl:when>
      <xsl:when test="$cat_id = '3612'">
        <xsl:value-of select='2966' />
      </xsl:when>
      <xsl:when test="$cat_id = '4512'">
        <xsl:value-of select='3032' />
      </xsl:when>
      <xsl:when test="$cat_id = '2417'">
        <xsl:value-of select='3189' />
      </xsl:when>
      <xsl:when test="$cat_id = '3646'">
        <xsl:value-of select='3282' />
      </xsl:when>
      <xsl:when test="$cat_id = '3637'">
        <xsl:value-of select='3289' />
      </xsl:when>
      <xsl:when test="$cat_id = '3601'">
        <xsl:value-of select='3376' />
      </xsl:when>
      <xsl:when test="$cat_id = '3669'">
        <xsl:value-of select='3413' />
      </xsl:when>
      <xsl:when test="$cat_id = '3659'">
        <xsl:value-of select='3579' />
      </xsl:when>
      <xsl:when test="$cat_id = '3661'">
        <xsl:value-of select='3649' />
      </xsl:when>
      <xsl:when test="$cat_id = '3668'">
        <xsl:value-of select='3894' />
      </xsl:when>
      <xsl:when test="$cat_id = '3600'">
        <xsl:value-of select='499687' />
      </xsl:when>
      <xsl:when test="$cat_id = '3137'">
        <xsl:value-of select='499792' />
      </xsl:when>
      <xsl:when test="$cat_id = '3151'">
        <xsl:value-of select='499796' />
      </xsl:when>
      <xsl:when test="$cat_id = '3580'">
        <xsl:value-of select='499811' />
      </xsl:when>
      <xsl:when test="$cat_id = '3597'">
        <xsl:value-of select='499813' />
      </xsl:when>
      <xsl:when test="$cat_id = '3505'">
        <xsl:value-of select='499845' />
      </xsl:when>
      <xsl:when test="$cat_id = '3649'">
        <xsl:value-of select='505317' />
      </xsl:when>
      <xsl:when test="$cat_id = '4389'">
        <xsl:value-of select='5181' />
      </xsl:when>
      <xsl:when test="$cat_id = '4588' or $cat_id = '6716'">
        <xsl:value-of select='5322' />
      </xsl:when>
      <xsl:when test="$cat_id = '6552'">
        <xsl:value-of select='5408' />
      </xsl:when>
      <xsl:when test="$cat_id = '4406'">
        <xsl:value-of select='549' />
      </xsl:when>
      <xsl:when test="$cat_id = '3581'">
        <xsl:value-of select='5579' />
      </xsl:when>
      <xsl:when test="$cat_id = '3582'">
        <xsl:value-of select='5580' />
      </xsl:when>
      <xsl:when test="$cat_id = '3584'">
        <xsl:value-of select='5582' />
      </xsl:when>
      <xsl:when test="$cat_id = '3586'">
        <xsl:value-of select='5583' />
      </xsl:when>
      <xsl:when test="$cat_id = '3585'">
        <xsl:value-of select='5584' />
      </xsl:when>
      <xsl:when test="$cat_id = '782'">
        <xsl:value-of select='576' />
      </xsl:when>
      <xsl:when test="$cat_id = '3655'">
        <xsl:value-of select='6288' />
      </xsl:when>
      <xsl:when test="$cat_id = '689'">
        <xsl:value-of select='631' />
      </xsl:when>
      <xsl:when test="$cat_id = '3626'">
        <xsl:value-of select='6312' />
      </xsl:when>
      <xsl:when test="$cat_id = '4508'">
        <xsl:value-of select='6551' />
      </xsl:when>
      <xsl:when test="$cat_id = '3660'">
        <xsl:value-of select='7451' />
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>No match</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>