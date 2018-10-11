<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:input="http://www.onderzoekinformatie.nl/nod/act"
                xmlns="https://www.openaire.eu/cerif-profile/1.1/"
                exclude-result-prefixes="input xsi"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:schemaLocation="http://www.onderzoekinformatie.nl/nod/act ../xsd/nod-research-1-1.xsd"
                version="1.0">

    <!-- =================================================================================== -->
    <xsl:output encoding="UTF-8" indent="yes" method="xml" omit-xml-declaration="yes"/>
    <!-- =================================================================================== -->

    <!-- variable -->

    <xsl:template match="/">
        <Project>
            <xsl:apply-templates select="input:activiteit"/>
        </Project>
    </xsl:template>

    <xsl:template match="input:activiteit">
        <xsl:apply-templates select="input:identifier"/>

        <xsl:apply-templates select="input:type_nl"/>
        <xsl:apply-templates select="input:type_en"/>

        <xsl:apply-templates select="input:title_nl"/>
        <xsl:apply-templates select="input:title_en"/>

        <xsl:apply-templates select="input:url"/>
        <xsl:apply-templates select="input:extern-identifier"/>

        <xsl:apply-templates select="input:startdate"/>
        <xsl:apply-templates select="input:enddate"/>

        <Consortium>
            <xsl:apply-templates select="input:penvoerder"/>

            <xsl:apply-templates select="input:samenwerking"/>

            <xsl:apply-templates select="input:opdrachtgever"/>
        </Consortium>

        <Team>
            <xsl:apply-templates select="input:person"/>
        </Team>

        <xsl:apply-templates select="input:financier"/>

        <xsl:apply-templates select="input:categories/input:category"/>

        <xsl:apply-templates select="input:summary_nl"/>
        <xsl:apply-templates select="input:summary_en"/>

        <xsl:apply-templates select="input:status"/>
    </xsl:template>

    <xsl:template match="input:identifier">
        <xsl:attribute name="id">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>

    <xsl:template match="input:type_nl">
        <xsl:if test=".">
            <Type scheme="https://www.narcis.nl/vocab/project-types" xml:lang="nl">
                <xsl:value-of select="."/>
            </Type>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:type_en">
        <xsl:if test=".">
            <Type scheme="https://www.narcis.nl/vocab/project-types" xml:lang="en">
                <xsl:value-of select="."/>
            </Type>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:title_nl">
        <xsl:if test=".">
            <Title xml:lang="nl">
                <xsl:value-of select="."/>
            </Title>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:title_en">
        <xsl:if test=".">
            <Title xml:lang="en">
                <xsl:value-of select="."/>
            </Title>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:url">
        <xsl:if test=".">
            <Identifier type="nod-ond">
                <xsl:value-of select="."/>
            </Identifier>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:extern-identifier">
        <xsl:choose>
            <xsl:when test="@type='NWO-Dossier'">
                <xsl:if test=".">
                    <Identifier type="NWO-Dossier">
                        <xsl:value-of select="."/>
                    </Identifier>
                </xsl:if>
            </xsl:when>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="input:startdate">
        <xsl:if test=".">
            <StartDate>
                <xsl:value-of select="."/>
            </StartDate>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:enddate">
        <xsl:if test=".">
            <EndDate>
                <xsl:value-of select="."/>
            </EndDate>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:penvoerder">
        <xsl:if test=".">
            <OrgUnit>
                <xsl:attribute name="id">
                    <xsl:value-of select="@code"/>
                </xsl:attribute>
            </OrgUnit>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:samenwerking">
        <xsl:if test=".">
            <OrgUnit>
                <xsl:attribute name="id">
                    <xsl:value-of select="@code"/>
                </xsl:attribute>
            </OrgUnit>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:opdrachtgever">
        <xsl:if test=".">
            <OrgUnit>
                <xsl:attribute name="id">
                    <xsl:value-of select="@code"/>
                </xsl:attribute>
            </OrgUnit>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:financier">
        <xsl:if test=".">
            <Funded>
                <By>
                    <OrgUnit>
                        <xsl:attribute name="id">
                            <xsl:value-of select="@code"/>
                        </xsl:attribute>
                    </OrgUnit>
                </By>
            </Funded>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:person">
        <Member>
            <Person>
                <xsl:attribute name="id">
                    <xsl:value-of select="input:nameIdentifier[@type='nod-prs']"/>
                </xsl:attribute>
            </Person>
            <Affiliation>
                <OrgUnit>
                    <xsl:attribute name="id">
                        <xsl:value-of select="input:werkzaamheid"/>
                    </xsl:attribute>
                </OrgUnit>
            </Affiliation>
        </Member>
    </xsl:template>

    <xsl:template match="input:categories/input:category">
        <Subject scheme="https://www.narcis.nl/vocab/narcis-classificatie">
            <xsl:value-of select="@code"/>
        </Subject>
    </xsl:template>

    <xsl:template match="input:summary_nl">
        <xsl:if test=".">
            <Abstract xml:lang="nl">
                <xsl:value-of select="."/>
            </Abstract>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:summary_en">
        <xsl:if test=".">
            <Abstract xml:lang="en">
                <xsl:value-of select="."/>
            </Abstract>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:status">
        <xsl:if test=".">
            <Status scheme="nod-status">
                <xsl:choose>
                    <xsl:when test=". = 'C'">
                        <xsl:text>current</xsl:text>
                    </xsl:when>
                    <xsl:when test=". = 'D'">
                        <xsl:text>completed</xsl:text>
                    </xsl:when>
                </xsl:choose>
            </Status>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
