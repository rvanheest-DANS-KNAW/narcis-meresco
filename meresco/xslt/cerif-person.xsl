<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:input="http://www.onderzoekinformatie.nl/nod/prs"
                xmlns="https://www.openaire.eu/cerif-profile/1.1/"
                exclude-result-prefixes="input xsi"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:schemaLocation="http://www.onderzoekinformatie.nl/nod/prs ../xsd/nod-person-1-1.xsd"
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

        <xsl:apply-templates select="input:nameIdentifier"/>

        <xsl:apply-templates select="input:person_url"/>

        <xsl:apply-templates select="input:jobs/input:job/input:organisatie"/>
    </xsl:template>

    <xsl:template match="input:identifier">
        <xsl:attribute name="id">
            <xsl:value-of select="concat('oai:narcis.nl:Persons/', .)"/>
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

    <xsl:template match="input:nameIdentifier">
        <xsl:choose>
            <xsl:when test="@type='orcid'">
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
                <ORCID>
                    <xsl:text>https://orcid.org/</xsl:text>
                    <xsl:value-of select="normalize-space($orcid1)"/>
                    <xsl:text>-</xsl:text>
                    <xsl:value-of select="normalize-space($orcid2)"/>
                    <xsl:text>-</xsl:text>
                    <xsl:value-of select="normalize-space($orcid3)"/>
                    <xsl:text>-</xsl:text>
                    <xsl:value-of select="normalize-space($orcid4)"/>
                </ORCID>
            </xsl:when>
            <xsl:when test="@type='isni'">
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
                <ISNI>
                    <xsl:value-of select="normalize-space($isni1)"/>
                    <xsl:text> </xsl:text>
                    <xsl:value-of select="normalize-space($isni2)"/>
                    <xsl:text> </xsl:text>
                    <xsl:value-of select="normalize-space($isni3)"/>
                    <xsl:text> </xsl:text>
                    <xsl:value-of select="normalize-space($isni4)"/>
                </ISNI>
            </xsl:when>
            <xsl:when test="@type='rid'">
                <!--
                    TODO when adding the ResearcherID, this number must be properly formatted
                    we don't know yet what the format is gonna look like from the NOD OAI-PMH output
                  -->
                <ResearcherID>
                    <xsl:value-of select="."/>
                </ResearcherID>
            </xsl:when>
            <xsl:when test="@type='said'">
                <!--
                    TODO when adding the ScopusAuthorID, this number must be properly formatted
                    we don't know yet what the format is gonna look like from the NOD OAI-PMH output
                  -->
                <ScopusAuthorID>
                    <xsl:value-of select="."/>
                </ScopusAuthorID>
            </xsl:when>
        </xsl:choose>

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
