# -*- coding: utf-8 -*-
## begin license ##
#
#
## end license ##

from lxml.etree import _ElementTree
from lxml import etree
from meresco.components.xml_generic.validate import ValidateException


class MetadataFormat():
    
    NAMESPACEMAP = {
        'oai_dc'    : 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        'mods'      : 'http://www.loc.gov/mods/v3',
        'datacite'  : 'http://datacite.org/schema/kernel-3'
        'org'       : 'http://www.onderzoekinformatie.nl/nod/org',
        'proj'      : 'http://www.onderzoekinformatie.nl/nod/act',
        'prs'       : 'http://www.onderzoekinformatie.nl/nod/prs',
        'didl'      : 'urn:mpeg:mpeg21:2002:02-DIDL-NS',
        'dc'        : 'http://purl.org/dc/elements/1.1/',
        'rdf'       : 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'ore'       : 'http://www.openarchives.org/ore/terms/',
    }
    
    NAMESPACEMAPPER = {
        'oai_dc'       : NAMESPACEMAP.get('oai_dc'),
        'didl_dc'      : NAMESPACEMAP.get('oai_dc'),
        'didl_mods231' : NAMESPACEMAP.get('mods'),
        'didl_mods30'  : NAMESPACEMAP.get('mods'),
        'didl_mods36'  : NAMESPACEMAP.get('mods'),
        'datacite'     : NAMESPACEMAP.get('datacite'),
        'org'          : NAMESPACEMAP.get('org'),
        'proj'         : NAMESPACEMAP.get('proj'),
        'prs'          : NAMESPACEMAP.get('prs'),
    }

    def __init__(self, lxmlNode, uploadId):
        
        md_format = None
        if len(lxmlNode.xpath('//didl:DIDL[1]', namespaces=MetadataFormat.NAMESPACEMAP)) > 0: # Check for DIDL container, Max. 1 according to EduStandaard.
            
            if int(lxmlNode.xpath("count(//mods:mods)", namespaces=MetadataFormat.NAMESPACEMAP)) >= 1: # Check for MODS container.
                # Found MODS: Check op aanwezigheid rdf namespace, to differentiate between known versions:
                if lxmlNode.xpath("boolean(count(//rdf:*))", namespaces=MetadataFormat.NAMESPACEMAP):
                    md_format = 'didl_mods30'
                else:
                    md_format = 'didl_mods231'
            elif int(lxmlNode.xpath("count(//oai_dc:dc)", namespaces=MetadataFormat.NAMESPACEMAP)) == 1: # Check for OAI_DC container.
                md_format = 'didl_dc'
            
        elif int(lxmlNode.xpath("count(//mods:mods)", namespaces=MetadataFormat.NAMESPACEMAP)) >= 1: # Full MODS (MODS only)
            md_format ='didl_mods36'
        elif lxmlNode.xpath("boolean(count(//oai_dc:dc))", namespaces=MetadataFormat.NAMESPACEMAP): # No DIDL, nor MODS was found, check for plain DC:
            md_format = 'oai_dc'
        elif lxmlNode.xpath("boolean(count(//org:organisatie))", namespaces=MetadataFormat.NAMESPACEMAP): # No DIDL, nor MODS was found, check for plain DC:
            md_format = 'org' # NOD organization
        elif lxmlNode.xpath("boolean(count(//proj:activiteit))", namespaces=MetadataFormat.NAMESPACEMAP): # No DIDL, nor MODS was found, check for plain DC:
            md_format = 'proj' # NOD project
        elif lxmlNode.xpath("boolean(count(//prs:persoon))", namespaces=MetadataFormat.NAMESPACEMAP): # No DIDL, nor MODS was found, check for plain DC:
            md_format = 'prs' # NOD Person
        elif lxmlNode.xpath("boolean(count(//datacite:resource))", namespaces=SurfShareFormat.NAMESPACEMAP): # No DIDL, nor MODS or ORE was found, check for DATACITE:
            md_format = 'datacite'

        if md_format == None:
            raise ValidateException("No known EduStandaard format was found in the metadata for uploadid: %s! This record cannot be processed." % (uploadId))

        self._format = md_format
        self._namespace = NAMESPACEMAPPER.get(format, None)
         

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
        return self._format in ('org', 'proj', 'datacite')

    def isOrganisation(self):
        return self._format == 'org'

    def isProject(self):
        return self._format == 'proj'

    def isPerson(self):
        return self._format == 'prs'


