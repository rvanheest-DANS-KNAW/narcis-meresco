<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:input="http://www.knaw.nl/narcis/1.0/long/"
                xmlns="https://www.openaire.eu/cerif-profile/1.1/"
                exclude-result-prefixes="input xsi"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:schemaLocation="http://www.knaw.nl/narcis/1.0/long/ ../xsd/knaw_long-1-1.xsd
                                    https://www.openaire.eu/cerif-profile/1.1/ https://www.openaire.eu/schema/cris/1.1/openaire-cerif-profile.xsd"
                version="1.0">

    <!-- =================================================================================== -->
    <xsl:output encoding="UTF-8" indent="yes" method="xml" omit-xml-declaration="yes"/>
    <!-- =================================================================================== -->

    <!-- variable -->

    <xsl:template match="/">
        <Patent>
            <xsl:apply-templates select="input:knaw_long"/>
        </Patent>
    </xsl:template>

    <xsl:template match="input:knaw_long">
        <xsl:apply-templates select="input:uploadid"/>
        <Type xmlns="https://www.openaire.eu/cerif-profile/vocab/COAR_Patent_Types">http://purl.org/coar/resource_type/c_15cd</Type>
        <xsl:apply-templates select="input:metadata"/>
    </xsl:template>

    <xsl:template match="input:metadata">
        <xsl:apply-templates select="input:titleInfo[not(@*)]"/>

        <xsl:apply-templates select="input:dateIssued/input:parsed"/>
        <xsl:apply-templates select="input:dateAccepted/input:parsed"/>

        <xsl:apply-templates select="input:patent_number"/>

        <xsl:if test="input:name[input:mcRoleTerm='inv']">
            <Inventors>
                <xsl:apply-templates select="input:name[input:mcRoleTerm='inv']"/>
            </Inventors>
        </xsl:if>

        <xsl:if test="input:name[input:mcRoleTerm='pth']">
            <Holders>
                <xsl:apply-templates select="input:name[input:mcRoleTerm='pth']"/>
            </Holders>
        </xsl:if>

        <xsl:apply-templates select="input:abstract[not(@*)]"/>

        <xsl:apply-templates select="input:subject/input:topic/input:topicValue"/>
    </xsl:template>

    <xsl:template match="input:uploadid">
        <xsl:attribute name="id">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>

    <xsl:template match="input:titleInfo[not(@*)]">
        <xsl:if test="input:title">
            <Title xml:lang="en">
                <xsl:value-of select="input:title"/>
            </Title>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:dateIssued/input:parsed">
        <xsl:if test=".">
            <RegistrationDate>
                <xsl:value-of select="."/>
            </RegistrationDate>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:dateAccepted/input:parsed">
        <xsl:if test=".">
            <ApprovalDate>
                <xsl:value-of select="."/>
            </ApprovalDate>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:patent_number">
        <xsl:if test=".">
            <PatentNumber>
                <xsl:value-of select="."/>
            </PatentNumber>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:name">
        <xsl:variable name="elementName">
            <xsl:choose>
                <xsl:when test="input:mcRoleTerm='inv'">Inventor</xsl:when>
                <xsl:when test="input:mcRoleTerm='pth'">Holder</xsl:when>
            </xsl:choose>
        </xsl:variable>

        <xsl:element name="{$elementName}">
            <xsl:call-template name="displayName"/>
            <xsl:call-template name="person"/>
            <xsl:if test="input:mcRoleTerm='pth'"> <!-- only a patentholder may have an OrgUnit element -->
                <xsl:call-template name="organisation"/>
            </xsl:if>
        </xsl:element>
    </xsl:template>

    <xsl:template name="displayName">
        <DisplayName>
            <xsl:choose>
                <xsl:when test="./input:family or ./input:given">
                    <xsl:value-of select="concat(./input:family, ', ', ./input:given)"/>
                </xsl:when>
                <xsl:when test="./input:unstructured">
                    <xsl:value-of select="./input:unstructured"/>
                </xsl:when>
            </xsl:choose>
        </DisplayName>
    </xsl:template>

    <xsl:template name="person">
        <xsl:if test="input:type='personal'">
            <Person>
                <xsl:if test="input:nameIdentifier[@type='nod-prs']">
                    <xsl:attribute name="id">
                        <xsl:value-of select="concat('person:', input:nameIdentifier[@type='nod-prs'])"/>
                    </xsl:attribute>
                    <PersonName>
                        <FamilyNames>
                            <xsl:value-of select="./input:family"/>
                        </FamilyNames>
                        <FirstNames>
                            <xsl:value-of select="./input:given"/>
                        </FirstNames>
                    </PersonName>
                </xsl:if>
            </Person>
        </xsl:if>
    </xsl:template>

    <xsl:template name="organisation">
        <xsl:if test="input:type='corporate'">
            <OrgUnit>
                <xsl:if test="input:nameIdentifier[@type='nod-org']">
                    <xsl:attribute name="id">
                        <xsl:value-of select="concat('organisation:', input:nameIdentifier[@type='nod-org'])"/>
                    </xsl:attribute>
                    <Name xml:lang="en">
                        <xsl:value-of select="input:unstructured"/>
                    </Name>
                </xsl:if>
            </OrgUnit>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:abstract[not(@*)]">
        <xsl:if test=".">
            <Abstract>
                <xsl:value-of select="."/>
            </Abstract>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:subject/input:topic/input:topicValue">
        <xsl:if test=".">
            <Keyword>
                <xsl:value-of select="."/>
            </Keyword>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
