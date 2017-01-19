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
    
    def __init__(self, lxmlNode, uploadId):
        
        md_format = None
        if len(lxmlNode.xpath('//didl:DIDL[1]', namespaces=Namespaces.NAMESPACEMAP)) > 0: # Check for DIDL container, Max. 1 according to EduStandaard.
            
            if int(lxmlNode.xpath("count(//mods:mods)", namespaces=Namespaces.NAMESPACEMAP)) >= 1: # Check for MODS container.
                # Found MODS: Check op aanwezigheid rdf namespace, to differentiate between known versions:
                if lxmlNode.xpath("boolean(count(//rdf:*))", namespaces=Namespaces.NAMESPACEMAP):
                    md_format = 'didl_mods30'
                else:
                    md_format = 'didl_mods231'
            elif int(lxmlNode.xpath("count(//oai_dc:dc)", namespaces=Namespaces.NAMESPACEMAP)) == 1: # Check for OAI_DC container.
                md_format = 'didl_dc'
            
        elif int(lxmlNode.xpath("count(//mods:mods)", namespaces=Namespaces.NAMESPACEMAP)) >= 1: # Full MODS (MODS only)
            md_format ='didl_mods36'
        elif lxmlNode.xpath("boolean(count(//oai_dc:dc))", namespaces=Namespaces.NAMESPACEMAP): # No DIDL, nor MODS was found, check for plain DC:
            md_format = 'oai_dc'
        elif lxmlNode.xpath("boolean(count(//org:organisatie))", namespaces=Namespaces.NAMESPACEMAP): # No DIDL, nor MODS was found, check for plain DC:
            md_format = 'org' # NOD organization
        elif lxmlNode.xpath("boolean(count(//proj:activiteit))", namespaces=Namespaces.NAMESPACEMAP): # No DIDL, nor MODS was found, check for plain DC:
            md_format = 'proj' # NOD project
        elif lxmlNode.xpath("boolean(count(//prs:persoon))", namespaces=Namespaces.NAMESPACEMAP): # No DIDL, nor MODS was found, check for plain DC:
            md_format = 'prs' # NOD Person
        elif lxmlNode.xpath("boolean(count(//datacite:resource))", namespaces=Namespaces.NAMESPACEMAP): # No DIDL, nor MODS or ORE was found, check for DATACITE:
            md_format = 'datacite'
        
        if md_format == None:
            raise ValidateException("No known EduStandaard format was found in the metadata for uploadid: %s! This record cannot be processed." % (uploadId))

        self._format = md_format
        self._namespace = Namespaces.getNamespace(format)
         

    def getFormat(self):
        return self._format            
            
    def getNamespace(self):
        return self._namespace

    def isDC(self):
        return self._format in ('oai_dc', 'didl_dc')
        
    def isOaiDC(self):
        return self._format =='oai_dc'
        
    def isDidlDC(self):
        return self._format =='didl_dc'
        
    def isMods(self):
        return self._format in ('didl_mods231', 'didl_mods30', 'didl_mods36')

    def isMods3(self):
        return self._format in ('didl_mods30', 'didl_mods36')

    def isDatacite(self):
        return self._format == 'datacite'

    def isNOD(self):
        return self._format in ('org', 'proj', 'prs')

    def isOrganisation(self):
        return self._format == 'org'

    def isProject(self):
        return self._format == 'proj'

    def isPerson(self):
        return self._format == 'prs'


