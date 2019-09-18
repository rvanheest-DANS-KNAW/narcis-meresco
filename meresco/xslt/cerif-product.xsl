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
        <Product>
            <xsl:apply-templates select="input:knaw_long"/>
        </Product>
    </xsl:template>

    <xsl:template match="input:knaw_long">
        <xsl:apply-templates select="input:uploadid"/>
        <xsl:apply-templates select="input:metadata"/>
        <xsl:apply-templates select="input:accessRights"/>
    </xsl:template>

    <xsl:template match="input:metadata">
        <xsl:call-template name="product-type"/>

        <xsl:apply-templates select="input:language"/>
        <xsl:apply-templates select="input:titleInfo[not(@*)]"/>

        <xsl:apply-templates select="input:publication_identifier[@type='doi']"/>
        <xsl:apply-templates select="input:publication_identifier[@type='hdl']"/>
        <xsl:apply-templates select="input:publication_identifier[@type='purl']"/>
        <xsl:apply-templates select="input:publication_identifier[@type='nbn']"/>
        <xsl:apply-templates select="input:publication_identifier[@type='urn']"/>

        <xsl:if test="input:name[input:mcRoleTerm='cre']">
            <Creators>
                <xsl:apply-templates select="input:name[input:mcRoleTerm='cre']"/>
            </Creators>
        </xsl:if>

        <xsl:apply-templates select="input:rightsDescription"/>
        <xsl:apply-templates select="input:abstract[not(@*)]"/>

        <xsl:apply-templates select="input:subject/input:topic/input:topicValue"/>
    </xsl:template>

    <xsl:template match="input:uploadid">
        <xsl:attribute name="id">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>

    <xsl:template name="product-type">
        <Type xmlns="https://www.openaire.eu/cerif-profile/vocab/COAR_Product_Types">
            <xsl:choose>
                <xsl:when test="input:genre='software'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_5ce6'"/>
                    <xsl:comment xml:space="preserve"> software </xsl:comment>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_ddb1'"/>
                    <xsl:comment xml:space="preserve"> dataset </xsl:comment>
                </xsl:otherwise>
            </xsl:choose>
        </Type>
    </xsl:template>

    <xsl:template match="input:language">
        <xsl:if test=".">
            <Language>
                <xsl:value-of select="."/>
            </Language>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:titleInfo[not(@*)]">
        <xsl:if test="input:title">
            <Name xml:lang="en">
                <xsl:value-of select="input:title"/>
            </Name>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:publication_identifier">
        <xsl:variable name="elementName">
            <xsl:choose>
                <xsl:when test="@type='doi'">DOI</xsl:when>
                <xsl:when test="@type='hdl'">Handle</xsl:when>
                <xsl:when test="@type='purl'">URL</xsl:when>
                <xsl:when test="@type='nbn'">URN</xsl:when>
                <xsl:when test="@type='urn'">URN</xsl:when>
            </xsl:choose>
        </xsl:variable>

        <xsl:if test=".">
            <xsl:element name="{$elementName}">
                <xsl:value-of select="."/>
            </xsl:element>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:name">
        <xsl:variable name="elementName">
            <xsl:choose>
                <xsl:when test="input:mcRoleTerm='cre'">Creator</xsl:when>
            </xsl:choose>
        </xsl:variable>

        <xsl:element name="{$elementName}">
            <xsl:call-template name="displayName"/>
            <xsl:call-template name="person"/>
            <xsl:call-template name="organisation"/>
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

    <xsl:template match="input:rightsDescription">
        <xsl:if test=".">
            <License scheme="http://www.narcis.nl/cerif-profile/vocab/LicenseType"> <!-- TODO scheme needs to be filled in if available -->
                <xsl:value-of select="."/>
            </License>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:abstract[not(@*)]">
        <xsl:if test=".">
            <Description xml:lang="en">
                <xsl:value-of select="."/>
            </Description>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:subject/input:topic/input:topicValue">
        <xsl:if test=".">
            <Keyword>
                <xsl:value-of select="."/>
            </Keyword>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:accessRights">
        <Access xmlns="http://purl.org/coar/access_right">
            <xsl:choose>
                <xsl:when test=".='openAccess'">
                    <xsl:value-of select="'http://purl.org/coar/access_right/c_abf2'"/>
                    <xsl:comment xml:space="preserve"> open access </xsl:comment>
                </xsl:when>
                <xsl:when test=".='embargoedAccess'">
                    <xsl:value-of select="'http://purl.org/coar/access_right/c_f1cf'"/>
                    <xsl:comment xml:space="preserve"> embargoed access </xsl:comment>
                </xsl:when>
                <xsl:when test=".='restrictedAccess'">
                    <xsl:value-of select="'http://purl.org/coar/access_right/c_16ec'"/>
                    <xsl:comment xml:space="preserve"> restricted access </xsl:comment>
                </xsl:when>
                <xsl:when test=".='closedAccess'">
                    <xsl:value-of select="'http://purl.org/coar/access_right/c_14cb'"/>
                    <xsl:comment xml:space="preserve"> metadata only access </xsl:comment>
                </xsl:when>
            </xsl:choose>
        </Access>
    </xsl:template>
</xsl:stylesheet>
