# -*- coding: utf-8 -*-
## begin license ##
#
#
## end license ##

from lxml.etree import _ElementTree
from lxml import etree
from meresco.components.xml_generic.validate import ValidateException
from meresco.dans.namespacemapping import Namespaces


class MetadataFormat():
    """Determines EduStandaard metadata format from LxmlNode"""
    
    DIDLM23 = 'didl_mods231'
    DIDLM30 = 'didl_mods30'    
    DIDLM36 = 'didl_mods36'
    DIDLDC = 'didl_dc'
    OAIDC = 'oai_dc'
    DATACITE = 'datacite4'
    ORG = 'org'
    PROJ = 'proj'
    PRS = 'prs'
    
    def __init__(self, lxmlNode, uploadId):
        
        md_format = None
        if len(lxmlNode.xpath('//didl:DIDL[1]', namespaces=Namespaces.NAMESPACEMAP)) > 0: # Check for DIDL container, Max. 1 according to EduStandaard.
            
            if int(lxmlNode.xpath("count(//mods:mods)", namespaces=Namespaces.NAMESPACEMAP)) >= 1: # Check for MODS container.
                # Found MODS: Check op aanwezigheid rdf namespace, to differentiate between known versions:
                if lxmlNode.xpath("boolean(count(//rdf:*))", namespaces=Namespaces.NAMESPACEMAP):
                    md_format = DIDLM30
                else:
                    md_format = DIDLM23
            elif int(lxmlNode.xpath("count(//oai_dc:dc)", namespaces=Namespaces.NAMESPACEMAP)) == 1: # Check for OAI_DC container.
                md_format = DIDLDC
            
        elif int(lxmlNode.xpath("count(//mods:mods)", namespaces=Namespaces.NAMESPACEMAP)) >= 1: # Full MODS (MODS only)
            md_format =DIDLM36
        elif lxmlNode.xpath("boolean(count(//oai_dc:dc))", namespaces=Namespaces.NAMESPACEMAP): # No DIDL, nor MODS was found, check for plain DC:
            md_format = OAIDC
        elif lxmlNode.xpath("boolean(count(//org:organisatie))", namespaces=Namespaces.NAMESPACEMAP): # No DIDL, nor MODS was found, check for plain DC:
            md_format = ORG # NOD organization
        elif lxmlNode.xpath("boolean(count(//proj:activiteit))", namespaces=Namespaces.NAMESPACEMAP): # No DIDL, nor MODS was found, check for plain DC:
            md_format = PROJ # NOD project
        elif lxmlNode.xpath("boolean(count(//prs:persoon))", namespaces=Namespaces.NAMESPACEMAP): # No DIDL, nor MODS was found, check for plain DC:
            md_format = PRS # NOD Person
        elif lxmlNode.xpath("boolean(count(//datacite:resource))", namespaces=Namespaces.NAMESPACEMAP): # No DIDL, nor MODS or ORE was found, check for DATACITE:
            md_format = DATACITE
        
        if md_format == None:
            raise ValidateException("No known EduStandaard format was found in the metadata for uploadid: %s! This record cannot be processed." % (uploadId))

        self._format = md_format
        self._namespace = Namespaces.getNamespace(format)
         

    def getFormat(self):
        return self._format            
            
    def getNamespace(self):
        """Maps MD_FORMAT to metadatanamespace. May be used in OAI provenance."""
        return self._namespace

    def isDC(self):
        return self._format in (OAIDC, DIDLDC)
        
    def isOaiDC(self):
        return self._format == OAIDC
        
    def isDidlDC(self):
        return self._format == DIDLDC
        
    def isMods(self):
        return self._format in (DIDLM23, DIDLM30, DIDLM36)

    def isMods3(self):
        return self._format in (DIDLM30, DIDLM36)

    def isDatacite(self):
        return self._format == DATACITE

    def isNOD(self):
        return self._format in (ORG, PROJ, PRS)

    def isOrganisation(self):
        return self._format == ORG

    def isProject(self):
        return self._format == PROJ

    def isPerson(self):
        return self._format == PRS


