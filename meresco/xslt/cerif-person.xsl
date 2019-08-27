<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:input="http://www.onderzoekinformatie.nl/nod/prs"
                xmlns="https://www.openaire.eu/cerif-profile/1.1/"
                exclude-result-prefixes="input xsi"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:schemaLocation="http://www.onderzoekinformatie.nl/nod/prs ../xsd/nod-person-1-1.xsd
                                    https://www.openaire.eu/cerif-profile/1.1/ https://www.openaire.eu/schema/cris/1.1/openaire-cerif-profile.xsd"
                version="1.0">

    <!-- =================================================================================== -->
    <xsl:output encoding="UTF-8" indent="yes" method="xml" omit-xml-declaration="yes"/>
    <!-- =================================================================================== -->

    <!-- variable -->

    <xsl:template match="/">
        <Person>
            <xsl:apply-templates select="input:persoon"/>
        </Person>
    </xsl:template>

    <xsl:template match="input:persoon">
        <xsl:apply-templates select="input:identifier"/>

        <PersonName>
            <xsl:apply-templates select="input:surname"/>
            <xsl:apply-templates select="input:initials"/>
        </PersonName>

<!--        <xsl:call-template name="nameIdentifier">-->
<!--            <xsl:with-param name="type">orcid</xsl:with-param>-->
<!--            <xsl:with-param name="label">ORCID</xsl:with-param>-->
<!--        </xsl:call-template>-->
<!--        <xsl:call-template name="nameIdentifier">-->
<!--            <xsl:with-param name="type">rid</xsl:with-param>-->
<!--            <xsl:with-param name="label">RID</xsl:with-param>-->
<!--        </xsl:call-template>-->
<!--        <xsl:call-template name="nameIdentifier">-->
<!--            <xsl:with-param name="type">said</xsl:with-param>-->
<!--            <xsl:with-param name="label">SAID</xsl:with-param>-->
<!--        </xsl:call-template>-->
<!--        <xsl:call-template name="nameIdentifier">-->
<!--            <xsl:with-param name="type">isni</xsl:with-param>-->
<!--            <xsl:with-param name="label">ISNI</xsl:with-param>-->
<!--        </xsl:call-template>-->
        <xsl:call-template name="nameIdentifier">
            <xsl:with-param name="type">dai-nl</xsl:with-param>
            <xsl:with-param name="label">DAI</xsl:with-param>
        </xsl:call-template>

        <xsl:apply-templates select="input:person_url"/>

        <xsl:apply-templates select="input:jobs/input:job/input:organisatie"/>
    </xsl:template>

    <xsl:template match="input:identifier">
        <xsl:attribute name="id">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>

    <xsl:template match="input:surname">
        <xsl:if test=".">
            <FamilyNames>
                <xsl:value-of select="."/>
            </FamilyNames>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:initials">
        <xsl:if test=".">
            <FirstNames>
                <xsl:value-of select="."/>
            </FirstNames>
        </xsl:if>
    </xsl:template>

    <xsl:template name="nameIdentifier">
        <xsl:param name="type"/>
        <xsl:param name="label"/>

        <xsl:variable name="elemCount" select="count(input:nameIdentifier[@type=$type])"/>

        <xsl:apply-templates select="input:nameIdentifier[@type=$type]">
            <xsl:with-param name="label">
                <xsl:choose>
                    <xsl:when test="$elemCount = 1">
                        <xsl:value-of select="$label"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="concat('Alternative', $label)"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:with-param>
        </xsl:apply-templates>
    </xsl:template>

    <xsl:template match="input:nameIdentifier[@type='orcid']">
        <xsl:param name="label"/>

        <xsl:variable name="orcid1">
            <xsl:value-of select="substring(., 1, 4)"/>
        </xsl:variable>
        <xsl:variable name="orcid2">
            <xsl:value-of select="substring(., 5, 4)"/>
        </xsl:variable>
        <xsl:variable name="orcid3">
            <xsl:value-of select="substring(., 9, 4)"/>
        </xsl:variable>
        <xsl:variable name="orcid4">
            <xsl:value-of select="substring(., 13, 4)"/>
        </xsl:variable>

        <xsl:element name="{$label}">
            <xsl:text>https://orcid.org/</xsl:text>
            <xsl:value-of select="normalize-space($orcid1)"/>
            <xsl:text>-</xsl:text>
            <xsl:value-of select="normalize-space($orcid2)"/>
            <xsl:text>-</xsl:text>
            <xsl:value-of select="normalize-space($orcid3)"/>
            <xsl:text>-</xsl:text>
            <xsl:value-of select="normalize-space($orcid4)"/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="input:nameIdentifier[@type='isni']">
        <xsl:param name="label"/>

        <xsl:variable name="isni1">
            <xsl:value-of select="substring(., 1, 4)"/>
        </xsl:variable>
        <xsl:variable name="isni2">
            <xsl:value-of select="substring(., 5, 4)"/>
        </xsl:variable>
        <xsl:variable name="isni3">
            <xsl:value-of select="substring(., 9, 4)"/>
        </xsl:variable>
        <xsl:variable name="isni4">
            <xsl:value-of select="substring(., 13, 4)"/>
        </xsl:variable>

        <xsl:element name="{$label}">
            <xsl:value-of select="normalize-space($isni1)"/>
            <xsl:text> </xsl:text>
            <xsl:value-of select="normalize-space($isni2)"/>
            <xsl:text> </xsl:text>
            <xsl:value-of select="normalize-space($isni3)"/>
            <xsl:text> </xsl:text>
            <xsl:value-of select="normalize-space($isni4)"/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="input:nameIdentifier[@type='dai-nl']">
        <xsl:param name="label"/>

        <xsl:element name="{$label}">
            <xsl:text>info:eu-repo/dai/nl/</xsl:text>
            <xsl:value-of select="."/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="input:nameIdentifier[@type='rid']">
        <xsl:param name="label"/>

        <!--
            TODO when adding the ResearcherID, this number must be properly formatted
            we don't know yet what the format is gonna look like from the NOD OAI-PMH output
          -->
        <xsl:element name="{$label}">
            <xsl:value-of select="."/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="input:nameIdentifier[@type='said']">
        <xsl:param name="label"/>

        <!--
            TODO when adding the ScopusAuthorID, this number must be properly formatted
            we don't know yet what the format is gonna look like from the NOD OAI-PMH output
          -->
        <xsl:element name="{$label}">
            <xsl:value-of select="."/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="input:person_url">
        <xsl:if test=".">
            <ElectronicAddress>
                <xsl:value-of select="concat('url:', .)"/>
            </ElectronicAddress>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:jobs/input:job/input:organisatie">
        <Affiliation>
            <OrgUnit>
                <xsl:attribute name="id">
                    <xsl:value-of select="@id"/>
                </xsl:attribute>
            </OrgUnit>
        </Affiliation>
    </xsl:template>
</xsl:stylesheet>
