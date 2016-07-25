# -*- coding: utf-8 -*-
## begin license ##
#
#
## end license ##

from lxml.etree import _ElementTree
from lxml import etree


class MetadataFormat():
    
    """Determines EduStandaard metadata format from LxmlNode"""
    
    # Current EduStandaard formats in use, chronologically:
    MD_FORMAT = ['oai_dc', 'didl_mods231', 'didl_mods30', 'mods36']
    
    NAMESPACEMAP = {
        'dc'            : 'http://purl.org/dc/elements/1.1/',
        'oai_dc'        : 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        'mods'          : 'http://www.loc.gov/mods/v3',
        'didl'          : 'urn:mpeg:mpeg21:2002:02-DIDL-NS',
        'rdf'           : 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'ore'           : 'http://www.openarchives.org/ore/terms/',
    }
    
    NAMESPACEMAPPER = {
        MD_FORMAT[0] : NAMESPACEMAP.get('oai_dc'),
        MD_FORMAT[1] : NAMESPACEMAP.get('mods'),
        MD_FORMAT[2] : NAMESPACEMAP.get('mods'),
        MD_FORMAT[3] : NAMESPACEMAP.get('mods'),
    }


    @staticmethod
    def getFormat(lxmlNode): # Returns a known metadata format, None otherwise. 
        """Returns MD_FORMAT, or None if not found"""
        
        md_format = None
        # print "FORMATBEFORE:", etree.tostring(lxmlNode, encoding="UTF-8")
        # Quit if no lxmlnode is provided:
        # if type(lxmlNode) != _ElementTree:
        #     return md_format
        
        # print "FORMAT:", etree.tostring(lxmlNode, encoding="UTF-8")

        if lxmlNode.xpath('//didl:DIDL[1]', namespaces=MetadataFormat.NAMESPACEMAP): # Check for DIDL container, Max. 1 according to EduStandaard.
            
            if int(lxmlNode.xpath("count(//mods:mods)", namespaces=MetadataFormat.NAMESPACEMAP)) == 1: # Check for MODS container.
                # Found MODS: Check op aanwezigheid rdf namespace, to differentiate between known versions:
                if lxmlNode.xpath("boolean(count(//rdf:*))", namespaces=MetadataFormat.NAMESPACEMAP):
                    md_format = MetadataFormat.MD_FORMAT[2] # DIDL_MODS30
                else:
                    md_format = MetadataFormat.MD_FORMAT[1] # DIDL_MODS231
            
        elif int(lxmlNode.xpath("count(//mods:mods)", namespaces=MetadataFormat.NAMESPACEMAP)) == 1: # Full MODS (MODS only)
            md_format = MetadataFormat.MD_FORMAT[3] # MODS 3.?
        elif lxmlNode.xpath("boolean(count(//oai_dc:dc))", namespaces=MetadataFormat.NAMESPACEMAP): # No DIDL, nor MODS was found, check for plain DC:
            md_format = MetadataFormat.MD_FORMAT[0] # OAI_DC
        # elif lxmlNode.xpath("boolean(count(//rdf:RDF/rdf:Description/ore:describes))", namespaces=MetadataFormat.NAMESPACEMAP):#No DIDL, no DC, check for ORE:
        #     md_format = MetadataFormat.MD_FORMAT[5]

        print "Found EduStandaard format:", md_format
        return md_format


    @staticmethod
    def getMetadataNamespace(md_format):
        """Maps MD_FORMAT to metadatanamespace. May be used in OAI provenance."""
        return MetadataFormat.NAMESPACEMAPPER.get(md_format, None)