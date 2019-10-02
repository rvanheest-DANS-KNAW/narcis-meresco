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
        <Publication>
            <xsl:apply-templates select="input:knaw_long"/>
        </Publication>
    </xsl:template>

    <xsl:template match="input:knaw_long">
        <xsl:apply-templates select="input:uploadid"/>
        <xsl:apply-templates select="input:metadata"/>
        <xsl:apply-templates select="input:accessRights"/>
    </xsl:template>

    <xsl:template match="input:uploadid">
        <xsl:attribute name="id">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>

    <xsl:template match="input:metadata">
        <xsl:call-template name="publication-type"/>

        <xsl:apply-templates select="input:language"/>
        <xsl:apply-templates select="input:titleInfo[not(@*)]/input:title"/>
        <xsl:apply-templates select="input:titleInfo[not(@*)]/input:subtitle"/>

        <xsl:call-template name="publishedIn"/>
        <xsl:apply-templates select="input:dateIssued/input:parsed"/>
        <xsl:apply-templates select="input:relatedItem[@type='host']/input:part/input:volume"/>
        <xsl:apply-templates select="input:relatedItem[@type='host']/input:part/input:issue"/>
        <xsl:apply-templates select="input:relatedItem[@type='host']/input:part/input:start_page"/>
        <xsl:apply-templates select="input:relatedItem[@type='host']/input:part/input:end_page"/>

        <xsl:apply-templates select="input:publication_identifier[@type='doi']"/>
        <xsl:apply-templates select="input:publication_identifier[@type='handle']"/>
        <xsl:apply-templates select="input:publication_identifier[@type='pmid']"/>
        <xsl:apply-templates select="input:publication_identifier[@type='wos']"/>
        <xsl:apply-templates select="input:publication_identifier[@type='scopus']"/>
        <xsl:apply-templates select="input:relatedItem/input:publication_identifier[@type='issn']"/>
        <xsl:apply-templates select="input:publication_identifier[@type='isbn']"/>

        <xsl:apply-templates select="input:location_url"/>
        <xsl:apply-templates select="../input:persistentIdentifier"/>

        <xsl:if test="input:name[input:mcRoleTerm='aut']">
            <Authors>
                <xsl:apply-templates select="input:name[input:mcRoleTerm='aut']"/>
            </Authors>
        </xsl:if>

        <xsl:apply-templates select="input:subject/input:topic/input:topicValue"/>
        <xsl:apply-templates select="input:abstract"/>
        
        <Status scheme="http://vocabularies.coar-repositories.org/documentation/version_types/">http://purl.org/coar/version/c_be7fb7dd8ff6fe43<!-- Not Applicable (or Unknown) --></Status>
    </xsl:template>

    <xsl:template name="publication-type">
        <Type xmlns="https://www.openaire.eu/cerif-profile/vocab/COAR_Publication_Types">
            <xsl:choose>
                <xsl:when test="input:genre='annotation'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_1162'"/>
                    <xsl:comment xml:space="preserve"> annotation </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='article'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_6501'"/>
                    <xsl:comment xml:space="preserve"> journal article </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='bachelorthesis'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_7a1f'"/>
                    <xsl:comment xml:space="preserve"> bachelor thesis </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='book'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_2f33'"/>
                    <xsl:comment xml:space="preserve"> book </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='bookpart'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_3248'"/>
                    <xsl:comment xml:space="preserve"> book part </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='bookreview'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_ba08'"/>
                    <xsl:comment xml:space="preserve"> book review </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='conferencepaper'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_5794'"/>
                    <xsl:comment xml:space="preserve"> conference paper </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='contributiontoperiodical'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_3e5a'"/>
                    <xsl:comment xml:space="preserve"> contribution to journal </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='doctoralthesis'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_db06'"/>
                    <xsl:comment xml:space="preserve"> doctoral thesis </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='researchproposal'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_baaf'"/>
                    <xsl:comment xml:space="preserve"> research proposal </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='lecture'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_8544'"/>
                    <xsl:comment xml:space="preserve"> lecture </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='masterthesis'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_bdcc'"/>
                    <xsl:comment xml:space="preserve"> master thesis </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='preprint'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_816b'"/>
                    <xsl:comment xml:space="preserve"> preprint </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='report'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_93fc'"/>
                    <xsl:comment xml:space="preserve"> report </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='studentthesis'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_46ec'"/>
                    <xsl:comment xml:space="preserve"> thesis </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='technicaldocumentation'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_71bd'"/>
                    <xsl:comment xml:space="preserve"> technical documentation </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='workingpaper'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_8042'"/>
                    <xsl:comment xml:space="preserve"> working paper </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='conferenceobject'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_c94f'"/>
                    <xsl:comment xml:space="preserve"> conference object </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='other'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_18cf'"/>
                    <xsl:comment xml:space="preserve"> text </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='conferenceitem'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_c94f'"/>
                    <xsl:comment xml:space="preserve"> conference object </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='conferenceitemnotinproceedings'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_c94f'"/>
                    <xsl:comment xml:space="preserve"> conference object </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='conferenceposter'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_6670'"/>
                    <xsl:comment xml:space="preserve"> conference poster </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='conferenceproceedings'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_f744'"/>
                    <xsl:comment xml:space="preserve"> conference proceedings </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='reportpart'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_ba1f'"/>
                    <xsl:comment xml:space="preserve"> report part </xsl:comment>
                </xsl:when>
                <xsl:when test="input:genre='review'">
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_efa0'"/>
                    <xsl:comment xml:space="preserve"> review </xsl:comment>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="'http://purl.org/coar/resource_type/c_18cf'"/>
                    <xsl:comment xml:space="preserve"> text </xsl:comment>
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

    <xsl:template match="input:titleInfo[not(@*)]/input:title">
        <xsl:if test=".">
            <Title xml:lang="en">
                <xsl:value-of select="."/>
            </Title>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:titleInfo[not(@*)]/input:subtitle">
        <xsl:if test=".">
            <Subtitle xml:lang="en">
                <xsl:value-of select="."/>
            </Subtitle>
        </xsl:if>
    </xsl:template>

    <xsl:template name="publishedIn">
        <xsl:if test="input:relatedItem[@type='host']/input:titleInfo[not(@*)]/input:title">
            <PublishedIn>
                <Publication>
                    <Type xmlns="https://www.openaire.eu/cerif-profile/vocab/COAR_Publication_Types">
                        <xsl:choose>
                            <xsl:when test="input:genre='annotation'">
                                <xsl:value-of select="'http://purl.org/coar/resource_type/c_0640'"/>
                                <xsl:comment xml:space="preserve"> journal </xsl:comment>
                            </xsl:when>
                            <xsl:when test="input:genre='article'">
                                <xsl:value-of select="'http://purl.org/coar/resource_type/c_0640'"/>
                                <xsl:comment xml:space="preserve"> journal </xsl:comment>
                            </xsl:when>
                            <xsl:when test="input:genre='bookpart'">
                                <xsl:value-of select="'http://purl.org/coar/resource_type/c_2f33'"/>
                                <xsl:comment xml:space="preserve"> book </xsl:comment>
                            </xsl:when>
                            <xsl:when test="input:genre='bookreview'">
                                <xsl:value-of select="'http://purl.org/coar/resource_type/c_0640'"/>
                                <xsl:comment xml:space="preserve"> journal </xsl:comment>
                            </xsl:when>
                            <xsl:when test="input:genre='conferencepaper'">
                                <xsl:value-of select="'http://purl.org/coar/resource_type/c_f744'"/>
                                <xsl:comment xml:space="preserve"> conference proceedings </xsl:comment>
                            </xsl:when>

                            <xsl:when test="input:genre='contributiontoperiodical'">
                                <xsl:value-of select="'http://purl.org/coar/resource_type/c_0640'"/>
                                <xsl:comment xml:space="preserve"> journal </xsl:comment>
                            </xsl:when>
                            <xsl:when test="input:genre='preprint'">
                                <xsl:value-of select="'http://purl.org/coar/resource_type/c_0640'"/>
                                <xsl:comment xml:space="preserve"> journal </xsl:comment>
                            </xsl:when>
                            <xsl:when test="input:genre='workingpaper'">
                                <xsl:value-of select="'http://purl.org/coar/resource_type/c_0640'"/>
                                <xsl:comment xml:space="preserve"> journal </xsl:comment>
                            </xsl:when>
                            <xsl:when test="input:genre='reportpart'">
                                <xsl:value-of select="'http://purl.org/coar/resource_type/c_93fc'"/>
                                <xsl:comment xml:space="preserve"> report </xsl:comment>
                            </xsl:when>
                            <xsl:when test="input:genre='review'">
                                <xsl:value-of select="'http://purl.org/coar/resource_type/c_0640'"/>
                                <xsl:comment xml:space="preserve"> journal </xsl:comment>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="'http://purl.org/coar/resource_type/c_18cf'"/>
                                <xsl:comment xml:space="preserve"> text </xsl:comment>
                            </xsl:otherwise>
                        </xsl:choose>
                    </Type>
                    <Title xml:lang="en">
                        <xsl:value-of select="input:relatedItem[@type='host']/input:titleInfo[not(@*)]/input:title"/>
                    </Title>
                </Publication>
            </PublishedIn>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:dateIssued/input:parsed">
        <xsl:if test=".">
            <PublicationDate>
                <xsl:value-of select="."/>
            </PublicationDate>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:relatedItem[@type='host']/input:part/input:volume">
        <xsl:if test=".">
            <Volume>
                <xsl:value-of select="."/>
            </Volume>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:relatedItem[@type='host']/input:part/input:issue">
        <xsl:if test=".">
            <Issue>
                <xsl:value-of select="."/>
            </Issue>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:relatedItem[@type='host']/input:part/input:start_page">
        <xsl:if test=".">
            <StartPage>
                <xsl:value-of select="."/>
            </StartPage>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:relatedItem[@type='host']/input:part/input:end_page">
        <xsl:if test=".">
            <EndPage>
                <xsl:value-of select="."/>
            </EndPage>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:publication_identifier[@type='doi']">
        <xsl:if test=".">
            <DOI>
                <xsl:value-of select="."/>
            </DOI>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:publication_identifier[@type='handle']">
        <xsl:if test=".">
            <Handle>
                <xsl:value-of select="."/>
            </Handle>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:publication_identifier[@type='pmid']">
        <xsl:if test=".">
            <PMCID>
                <xsl:value-of select="."/>
            </PMCID>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:publication_identifier[@type='wos']">
        <xsl:if test=".">
            <ISI-Number>
                <xsl:value-of select="."/>
            </ISI-Number>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:publication_identifier[@type='scopus']">
        <xsl:if test=".">
            <SCP-Number>
                <xsl:value-of select="."/>
            </SCP-Number>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:relatedItem/input:publication_identifier[@type='issn']">
        <xsl:if test=".">
            <ISSN>
                <xsl:value-of select="."/>
            </ISSN>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:publication_identifier[@type='isbn']">
        <xsl:if test=".">
            <ISBN>
                <xsl:value-of select="."/>
            </ISBN>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:location_url">
        <xsl:if test=".">
            <URL>
                <xsl:value-of select="."/>
            </URL>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:name">
        <xsl:variable name="elementName">
            <xsl:choose>
                <xsl:when test="input:mcRoleTerm='aut'">Author</xsl:when>
            </xsl:choose>
        </xsl:variable>

        <xsl:element name="{$elementName}">
            <xsl:call-template name="displayName"/>
            <xsl:call-template name="person"/>
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

    <xsl:template match="input:subject/input:topic/input:topicValue">
        <xsl:if test=".">
            <Keyword xml:lang="en">
                <xsl:value-of select="."/>
            </Keyword>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:abstract">
        <xsl:if test=".">
            <Abstract>
                <xsl:attribute name="xml:lang">
                    <xsl:value-of select="'en'"/>
                </xsl:attribute>
                <xsl:value-of select="."/>
            </Abstract>
        </xsl:if>
    </xsl:template>

    <xsl:template match="input:persistentIdentifier">
        <xsl:if test=".">
            <URN>
                <xsl:value-of select="."/>
            </URN>
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
