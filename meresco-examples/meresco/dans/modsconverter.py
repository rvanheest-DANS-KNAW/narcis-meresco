## begin license ##
#
#
## end license ##

import sys
from lxml.etree import _ElementTree as ElementTreeType
from lxml import etree

from lxml.etree import parse, _ElementTree, tostring


from weightless.core import NoneOfTheObserversRespond, DeclineMessage
from meresco.core import Observable
from meresco.components import lxmltostring, Converter
from xml.sax.saxutils import unescape
from meresco.dans.metadataformats import MetadataFormat

import time

HVSTR_NS = '{http://meresco.org/namespace/harvester/meta}'
DOCUMENT_NS = '{http://meresco.org/namespace/harvester/document}'
namespaceMap = {
'document'  :  "http://meresco.org/namespace/harvester/document",
'oai': "http://www.openarchives.org/OAI/2.0/",
'oai_dc' :"http://www.openarchives.org/OAI/2.0/oai_dc/",
'dc'            : 'http://purl.org/dc/elements/1.1/',
}

MODS_VERSION = '3.6'

class ModsConverter(Converter):
    def __init__(self, fromKwarg, toKwarg=None, name=None):
        Converter.__init__(self, name=name, fromKwarg=fromKwarg, toKwarg=toKwarg)

    def _convert(self, lxmlNode):
        record_part = lxmlNode.xpath("//document:document/document:part[@name='record']/text()", namespaces=namespaceMap)
        record_lxml = etree.fromstring(unescape(record_part[0]))
        md_format = MetadataFormat.getFormat(record_lxml) #TODO: pass it somehow from DNA, so we need to look this up only once per record...

        converted_record_lxml = self._convertRecordMetadataToMods(record_lxml, md_format)# Check en insert harvestDate...
        meta_txt = etree.tostring(converted_record_lxml, encoding="UTF-8") # convert from lxml to text...
        lxmlNode.find('document:part[@name="record"]', namespaces=namespaceMap).text = meta_txt #Set as text value of the correct tag.
        return lxmlNode

    def _convertRecordMetadataToMods(self, lxmlNode, metadataFormat):
        print "CONVERTING TO MODS"

        MODS_NAMESPACE = "http://www.loc.gov/mods/v3"
        MODS = "{%s}" % MODS_NAMESPACE
        NSMAP = {
        None : MODS_NAMESPACE,
        'xlink': 'http://www.w3.org/1999/xlink',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        } 

        e_modsroot = etree.Element(MODS + "mods", nsmap=NSMAP)
        e_modsroot.set("version", MODS_VERSION)
        e_modsroot.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-"+ MODS_VERSION.replace(".", "-") +".xsd")
        # e_modsroot.set("xmlns:xsi" , "http://www.w3.org/2001/XMLSchema-instance")

        if metadataFormat == MetadataFormat.MD_FORMAT[0]:
            print "CONVERTING MD", MetadataFormat.MD_FORMAT[0]
        
# Try xslt (1.0 only)?

# import lxml.etree as ET

# dom = ET.parse(xml_filename)
# xslt = ET.parse(xsl_filename)
# transform = ET.XSLT(xslt)
# newdom = transform(dom)
# print(ET.tostring(newdom, pretty_print=True))

            strTitle = lxmlNode.xpath("//dc:title/text()", namespaces=namespaceMap)
            e_titleInfo = etree.SubElement(e_modsroot, "titleInfo")
            e_title = etree.SubElement(e_titleInfo, "title")
            e_title.text = strTitle[0]
            # print "MODS:", etree.tostring(e_modsroot), etree.tostring(lxmlNode)
            # oai_part = lxmlNode.find('/oai:record/oai:metadata', namespaces=namespaceMap)
            for child in lxmlNode.getchildren():
                print child.tag, child.text
                if child.tag == '{http://www.openarchives.org/OAI/2.0/}metadata':
                	for metadatakind in child.iterchildren():
                	    # print metadatakind.tag
                	    child.remove(metadatakind)
                	child.append(e_modsroot)
                	    # lxmlNode.replace(metadatakind, e_modsroot)
            print "CONVERTED:", etree.tostring(lxmlNode, encoding="UTF-8")
            # lxmlNode.replace(oai_part, e_modsroot)
        elif metadataFormat == MetadataFormat.MD_FORMAT[1]:
            print "CONVERTING MD", MetadataFormat.MD_FORMAT[1]
        elif metadataFormat == MetadataFormat.MD_FORMAT[2]:
            print "CONVERTING MD", MetadataFormat.MD_FORMAT[2]

        return lxmlNode













