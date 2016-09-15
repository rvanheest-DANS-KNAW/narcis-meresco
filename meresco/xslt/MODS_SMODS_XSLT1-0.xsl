<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
	xmlns:mods="http://www.loc.gov/mods/v3" exclude-result-prefixes="srw_dc" 
	xmlns:dc="http://purl.org/dc/elements/1.1/" 
	xmlns:srw_dc="info:srw/schema/1/dc-schema" 
	xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- 
	
	Version 1.1	2016-10-15 wilko.steinhoff@dans.knaw.nl
					Added truncation of the abstract element.
					Added copy of genre element.
					Updated introductory documentation
	
	Version 1.0		2016-10-14 wilko.steinhoff@dans.knaw.nl
	
	This stylesheet transforms any MODS 3 version records into versionless simpleMODS (SMODS) records. 
	
	The stylesheet will transform a single MODS record into simple MODS (SMODS), which is a 1:1 subset of the input MODS record.
			
	This stylesheet makes the following decisions in its interpretation of the MODS to simple DC mapping:
-->
		<xsl:output method="xml" indent="yes" omit-xml-declaration="yes"/>
				
		<xsl:template match="/mods:mods">
			<xsl:copy>
				<xsl:apply-templates select="mods:identifier"/>
				<xsl:apply-templates select="mods:genre"/>
				<xsl:apply-templates select="mods:titleInfo"/>
				<xsl:apply-templates select="mods:abstract"/>
				<xsl:apply-templates select="mods:name"/>
			</xsl:copy>
		</xsl:template>		
		
	<xsl:template match="mods:genre|mods:identifier|mods:titleInfo|mods:name">
		<xsl:copy-of select="."/>
	</xsl:template>
	
	<xsl:template match="mods:abstract">
		<xsl:copy>
			<xsl:if test="@xml:lang">
				<xsl:attribute name="xml:lang">
					<xsl:value-of select="@xml:lang" />
				</xsl:attribute>
			</xsl:if>
			<xsl:value-of select="substring(., 1, 25)" /> <!--300-->
		</xsl:copy>
	</xsl:template>
	
	</xsl:stylesheet>