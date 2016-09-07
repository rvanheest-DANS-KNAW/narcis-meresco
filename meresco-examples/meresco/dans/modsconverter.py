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

        converted_record_lxml = self._convertRecordMetadataToMods(record_lxml, md_format)# Check en insert normalised mods into record part.
        record_txt = etree.tostring(converted_record_lxml, encoding="UTF-8") # convert from lxml to text...
        lxmlNode.find('document:part[@name="record"]', namespaces=namespaceMap).text = record_txt # Set as text value...
        return lxmlNode

    def _convertRecordMetadataToMods(self, lxmlNode, metadataFormat):
        print "Converting node MODS:", etree.tostring(lxmlNode)

# <record xmlns="http://www.openarchives.org/OAI/2.0/"
#     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
#     <header xmlns="http://www.openarchives.org/OAI/2.0/">
#         <identifier>record:1</identifier>
#         <datestamp>2008-12-15T14:08:34Z</datestamp>
#     </header>
#     <metadata xmlns="http://www.openarchives.org/OAI/2.0/">
#         <oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
#             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#             xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/      http://www.openarchives.org/OAI/2.0/oai_dc.xsd">
#             <dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/"
#                 >http://meresco.com?record=1</dc:identifier>
#             <dc:description xmlns:dc="http://purl.org/dc/elements/1.1/">This is an example program
#                 about Search with Meresco</dc:description>
#             <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">Example Program 1</dc:title>
#             <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">Seecr</dc:creator>
#             <dc:publisher xmlns:dc="http://purl.org/dc/elements/1.1/">Seecr</dc:publisher>
#             <dc:date xmlns:dc="http://purl.org/dc/elements/1.1/">2016</dc:date>
#             <dc:type xmlns:dc="http://purl.org/dc/elements/1.1/">Example</dc:type>
#             <dc:subject xmlns:dc="http://purl.org/dc/elements/1.1/">Search</dc:subject>
#             <dc:language xmlns:dc="http://purl.org/dc/elements/1.1/">en</dc:language>
#             <dc:rights xmlns:dc="http://purl.org/dc/elements/1.1/">Open Source</dc:rights>
#         </oai_dc:dc>
#     </metadata>
# </record>


        MODS_NAMESPACE = "http://www.loc.gov/mods/v3"
        MODS = "{%s}" % MODS_NAMESPACE
        NSMAP = {
        None : MODS_NAMESPACE,
        'xlink': 'http://www.w3.org/1999/xlink',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        }
        NORM_NAMESPACE = "http://dans.knaw.nl/narcis/normalized"
        NORM_NS = "{%s}" % NORM_NAMESPACE


        e_original_root = etree.Element(NORM_NS + "md_original")
        e_norm_root = etree.Element(NORM_NS + "normalized")
        
        e_modsroot = etree.SubElement(e_norm_root, MODS + "mods", nsmap=NSMAP)
        # e_modsroot = etree.Element(MODS + "mods", nsmap=NSMAP)
        e_modsroot.set("version", MODS_VERSION)
        e_modsroot.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-"+ MODS_VERSION.replace(".", "-") +".xsd")
        # e_modsroot.set("xmlns:xsi" , "http://www.w3.org/2001/XMLSchema-instance")

        if metadataFormat == MetadataFormat.MD_FORMAT[0]: # OAI-DC
            print "CONVERTING MD", MetadataFormat.MD_FORMAT[0]

            strTitle = lxmlNode.xpath("//dc:title/text()", namespaces=namespaceMap)
            e_titleInfo = etree.SubElement(e_modsroot, "titleInfo")
            e_title = etree.SubElement(e_titleInfo, "title").text = strTitle[0]
# End conversion

            metadata_tags = lxmlNode.xpath("//oai:metadata/*", namespaces=namespaceMap)
            for child in metadata_tags:
                e_original_root.append(child) # voeg originele md toe aan marker element...
                metadata_tags.remove(child) # verwijder originele md van oai metadata tag....

            print "MD_ORIGINAL:", etree.tostring(e_original_root)

            for child in lxmlNode.getchildren():
                # print child.tag, child.text
                if child.tag == '{http://www.openarchives.org/OAI/2.0/}metadata':
                    child.append(e_original_root)
                    child.append(e_norm_root)
            print "CONVERTED:", etree.tostring(lxmlNode, encoding="UTF-8")

        elif metadataFormat == MetadataFormat.MD_FORMAT[1]:
            print "CONVERTING MD", MetadataFormat.MD_FORMAT[1]
        elif metadataFormat == MetadataFormat.MD_FORMAT[2]:
            print "CONVERTING MD", MetadataFormat.MD_FORMAT[2]

        return lxmlNode

# Try xslt (1.0 only)?

# import lxml.etree as ET

# dom = ET.parse(xml_filename)
# xslt = ET.parse(xsl_filename)
# transform = ET.XSLT(xslt)
# newdom = transform(dom)
# print(ET.tostring(newdom, pretty_print=True))
