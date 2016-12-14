## begin license ##
#
#
## end license ##

import sys
from lxml.etree import _ElementTree as ElementTreeType
from lxml import etree

from weightless.core import NoneOfTheObserversRespond, DeclineMessage
from meresco.core import Observable
from meresco.components import lxmltostring
from meresco.dans.uiaconverter import UiaConverter
from meresco.dans.metadataformats import MetadataFormat

import time

HVSTR_NS = '{http://meresco.org/namespace/harvester/meta}'
DOCUMENT_NS = '{http://meresco.org/namespace/harvester/document}'
surfshareNamespaceMap = {'document'  :  "http://meresco.org/namespace/harvester/document" }

class AddHarvestDateAndMetadataNamespace(UiaConverter):
    def __init__(self, dateformat, fromKwarg, toKwarg=None, name=None):
        UiaConverter.__init__(self, name=name, fromKwarg=fromKwarg, toKwarg=toKwarg)
        self._dateformat = dateformat

    def _convert(self, lxmlNode):
        record_part = lxmlNode.xpath("//document:document/document:part[@name='record']/text()", namespaces=surfshareNamespaceMap)
        record_lxml = etree.fromstring(record_part[0]) # Geen xml.sax.saxutils.unescape() hier? Dat doet lxml reeds voor ons.
        md_format = MetadataFormat.getFormat(record_lxml, self._uploadid) #TODO: pass it somehow from DNA, so we need to look this up only once per record...
        
        metapart = lxmlNode.xpath("//document:document/document:part[@name='meta']/text()", namespaces=surfshareNamespaceMap)
        if len(metapart) > 0: # metapart gevonden...
            meta_lxml = etree.fromstring(metapart[0])# Convert naar lxml... Ook hier GEEN xml.sax.saxutils.unescape()
            self._insertHarvestDateAndMetadataNamespace(meta_lxml, md_format)# Check en insert harvestDate...
            meta_txt = etree.tostring(meta_lxml, encoding="UTF-8") # convert from lxml to text...
            lxmlNode.find('document:part[@name="meta"]', namespaces=surfshareNamespaceMap).text = meta_txt #Set as text value of the correct tag.

        return lxmlNode


    def _insertHarvestDateAndMetadataNamespace(self, lxmlNode, metadataFormat):
        _bln_has_harvestdate, _bln_has_metadataNamespace = False, False        
        #Check if tag is already available, we dont want it twice, or overwritten when re-indexing f.e:
        for child in lxmlNode.iterchildren():
            if child.tag == HVSTR_NS + 'record':
                for recordkind in child.iterchildren():
                    if recordkind.tag == HVSTR_NS + 'harvestDate':
                        _bln_has_harvestdate = True
                        # print 'HarvestDate tag already available from meta part:' , recordkind.text , '. Skipping adding harvestDate...'
                    if recordkind.tag == HVSTR_NS + 'metadataNamespace':
                        _bln_has_metadataNamespace = True
                        # print 'MetadataNamespace tag already available from meta part:' , recordkind.text , '. Skipping adding metadataNamespace...'                        
                if not _bln_has_harvestdate:
                    e_harvestdate = etree.SubElement(child, HVSTR_NS + 'harvestDate')
                    e_harvestdate.text = time.strftime(self._dateformat, time.gmtime())
                    # print 'Added harvestDate tag to meta part:', e_harvestdate.text
                if not _bln_has_metadataNamespace:
                    e_metadataNamespace = etree.SubElement(child, HVSTR_NS + 'metadataNamespace')
                    e_metadataNamespace.text = MetadataFormat.getMetadataNamespace(metadataFormat)
                    # print 'Added metadataNamespace tag to meta part:', e_metadataNamespace.text
                break
        return lxmlNode        