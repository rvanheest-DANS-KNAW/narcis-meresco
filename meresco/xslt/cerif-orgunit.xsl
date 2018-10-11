<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:input="http://www.onderzoekinformatie.nl/nod/org"
                xmlns="https://www.openaire.eu/cerif-profile/1.1/"
                exclude-result-prefixes="input xsi"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:schemaLocation="http://www.onderzoekinformatie.nl/nod/org ../xsd/nod-organisation-1-1.xsd"
                version="1.0">

    <!-- =================================================================================== -->
    <xsl:output encoding="UTF-8" indent="yes" method="xml" omit-xml-declaration="yes"/>
    <!-- =================================================================================== -->

    <!-- variable -->

    <xsl:template match="/">
        <OrgUnit>
            <xsl:apply-templates select="input:organisatie"/>
        </OrgUnit>
    </xsl:template>

    <xsl:template match="input:organisatie">
        <xsl:apply-templates select="input:identifier"/>

        <xsl:apply-templates select="input:acroniem"/>

        <xsl:apply-templates select="input:naam_nl"/>

        <xsl:apply-templates select="input:naam_en"/>

        <xsl:apply-templates select="input:org_telefoon"/>

        <xsl:apply-templates select="input:org_fax"/>

        <xsl:apply-templates select="input:org_email"/>

        <xsl:apply-templates select="input:org_url"/>

        <xsl:apply-templates select="input:org_parent"/>
    </xsl:template>

    <xsl:template match="input:identifier">
        <xsl:attribute name="id">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>

    <xsl:template match="input:acroniem">
        <xsl:if test=".">
            <Acronym>
                <xsl:value-of select="."/>
            </Acronym>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:naam_nl">
        <xsl:if test=".">
            <Naam xml:lang="nl">
                <xsl:value-of select="."/>
            </Naam>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:naam_en">
        <xsl:if test=".">
            <Naam xml:lang="en">
                <xsl:value-of select="."/>
            </Naam>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:org_telefoon">
        <xsl:if test=".">
            <ElectronicAddress>
                <xsl:value-of select="concat('tel:', .)"/>
            </ElectronicAddress>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:org_fax">
        <xsl:if test=".">
            <ElectronicAddress>
                <xsl:value-of select="concat('fax:', .)"/>
            </ElectronicAddress>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:org_email">
        <xsl:if test=".">
            <ElectronicAddress>
                <xsl:value-of select="concat('mailto:', .)"/>
            </ElectronicAddress>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:org_url">
        <xsl:if test=".">
            <ElectronicAddress>
                <xsl:value-of select="concat('url:', .)"/>
            </ElectronicAddress>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:org_parent">
        <xsl:if test=".">
            <PartOf>
                <OrgUnit>
                    <xsl:attribute name="id">
                        <xsl:value-of select="."/>
                    </xsl:attribute>
                </OrgUnit>
            </PartOf>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
