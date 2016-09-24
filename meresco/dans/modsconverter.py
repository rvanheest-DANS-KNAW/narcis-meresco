## begin license ##
#
#
## end license ##

import sys

from lxml import etree
from lxml.etree import parse, _ElementTree, tostring

from StringIO import StringIO
from xml.sax.saxutils import escape as escapeXml

from weightless.core import NoneOfTheObserversRespond, DeclineMessage
from meresco.core import Observable
from meresco.components import lxmltostring, Converter
from meresco.dans.metadataformats import MetadataFormat
from meresco.xml import namespaces

import time

HVSTR_NS = '{http://meresco.org/namespace/harvester/meta}'
DOCUMENT_NS = '{http://meresco.org/namespace/harvester/document}'


namespaceMap = namespaces.copyUpdate({
    'prs'   : 'http://www.onderzoekinformatie.nl/nod/prs',
    'ond'   : 'http://www.onderzoekinformatie.nl/nod/act',
    'org'   : 'http://www.onderzoekinformatie.nl/nod/org',
    'long'  : 'http://www.knaw.nl/narcis/1.0/long/',
    'short' : 'http://www.knaw.nl/narcis/1.0/short/',
    'mods'  : 'http://www.loc.gov/mods/v3',
    'didl'  : 'urn:mpeg:mpeg21:2002:02-DIDL-NS',
    'norm'  : 'http://dans.knaw.nl/narcis/normalized',
})


MODS_VERSION = '3.6'

MODS_NAMESPACE = "http://www.loc.gov/mods/v3"
MODS = "{%s}" % MODS_NAMESPACE
NSMAP = {
None : MODS_NAMESPACE,
'xlink': 'http://www.w3.org/1999/xlink',
'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}
NORM_NAMESPACE = "http://dans.knaw.nl/narcis/normalized"
NORM_NS = "{%s}" % NORM_NAMESPACE


class ModsConverter(Converter):
    def __init__(self, fromKwarg, toKwarg=None, name=None):
        Converter.__init__(self, name=name, fromKwarg=fromKwarg, toKwarg=toKwarg)
        self._truncate_chars = 300

    def _convert(self, lxmlNode):
        record_part = lxmlNode.xpath("//document:document/document:part[@name='record']/text()", namespaces=namespaceMap)
        record_lxml = etree.fromstring(record_part[0]) # Geen xml.sax.saxutils.unescape() hier? Dat doet lxml reeds voor ons.
        md_format = MetadataFormat.getFormat(record_lxml) #TODO: pass it somehow from DNA, so we need to look this up only once per record...
        # print "FOUND MetaDataFormat:", md_format
        converted_record_lxml = self._convertRecordMetadataToMods(record_lxml, md_format)# Check en insert normalised mods into record part.
        record_txt = etree.tostring(converted_record_lxml, encoding="UTF-8") # convert from lxml to text...
        record_txt = record_txt.decode('utf-8')
        # print "record_txt", record_txt
        lxmlNode.find('document:part[@name="record"]', namespaces=namespaceMap).text = record_txt # Set as text value...
        # etree.cleanup_namespaces(lxmlNode)
        return lxmlNode

    def _convertRecordMetadataToMods(self, lxmlNode, metadataFormat):
        # print "Converting this lxmlNode to MODS:", etree.tostring(lxmlNode)

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
#             <dc:subject xmlns:dc="http://purl.org/dc/elements/1.1/">Search &amp; Destroy</dc:subject>
#             <dc:language xmlns:dc="http://purl.org/dc/elements/1.1/">en</dc:language>
#             <dc:rights xmlns:dc="http://purl.org/dc/elements/1.1/">Open Source</dc:rights>
#         </oai_dc:dc>
#     </metadata>
# </record>


        e_original_root = etree.Element(NORM_NS + "md_original")
        e_norm_root = etree.Element(NORM_NS + "normalized")
        

        if metadataFormat is not None:

            e_modsroot = etree.SubElement(e_norm_root, MODS + "mods", nsmap=NSMAP)
            e_modsroot.set("version", MODS_VERSION)
            e_modsroot.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-"+ MODS_VERSION.replace(".", "-") +".xsd")
            # e_modsroot.set("xmlns:xsi" , "http://www.w3.org/2001/XMLSchema-instance")

            if metadataFormat == MetadataFormat.MD_FORMAT[0] or metadataFormat == MetadataFormat.MD_FORMAT[1]:
                print "CONVERTING MD", metadataFormat

                strTitle = lxmlNode.xpath("//dc:title/text()", namespaces=namespaceMap)
                e_titleInfo = etree.SubElement(e_modsroot, "titleInfo")
                e_title = etree.SubElement(e_titleInfo, "title").text = strTitle[0]
                strAbstract = lxmlNode.xpath("//dc:description/text()", namespaces=namespaceMap)
                if len(strAbstract) > 0:
                    e_abstract = etree.SubElement(e_modsroot, "abstract").text = strAbstract[0]

                strGenre = lxmlNode.xpath("//dc:type/text()", namespaces=namespaceMap)
                if len(strGenre) > 0:
                    e_genre = etree.SubElement(e_modsroot, "genre").text = strGenre[0]        

            elif metadataFormat == MetadataFormat.MD_FORMAT[2] or metadataFormat == MetadataFormat.MD_FORMAT[3]:
                print "CONVERTING MD", metadataFormat
                strTitle = lxmlNode.xpath("//mods:titleInfo/mods:title/text()", namespaces=namespaceMap)
                if len(strTitle) > 0:
                    e_titleInfo = etree.SubElement(e_modsroot, "titleInfo")
                    e_title = etree.SubElement(e_titleInfo, "title").text = strTitle[0]

                strAbstract = lxmlNode.xpath("//mods:abstract/text()", namespaces=namespaceMap)
                if len(strAbstract) > 0:
                    e_abstract = etree.SubElement(e_modsroot, "abstract").text = strAbstract[0]

                strGenre = lxmlNode.xpath("//mods:genre/text()", namespaces=namespaceMap)
                if len(strGenre) > 0:
                    e_genre = etree.SubElement(e_modsroot, "genre").text = strGenre[0]
        else: #NOD records
            NODLxml = self._convertNODRecord2smods(lxmlNode)
            if NODLxml is not None:
                print 'NODE:' , tostring(NODLxml)
                e_norm_root.append(NODLxml.getroot())

        metadata_tags = lxmlNode.xpath("//oai:metadata/*", namespaces=namespaceMap)

        for child in metadata_tags:
            e_original_root.append(child) # voeg originele md toe aan marker element...
            metadata_tags.remove(child) # verwijder originele md van oai metadata tag....

        for child in lxmlNode.getchildren():
            # print child.tag, child.text
            if child.tag == '{http://www.openarchives.org/OAI/2.0/}metadata':
                child.append(e_original_root)
                child.append(e_norm_root)
                e_original_root.text = child.text # copy erronous text from metadata tag
                child.text = "" # delete erronous text from metadata tag
        # print "MD_ORIGINAL:", etree.tostring(e_original_root)
        # print "CONVERTED:", etree.tostring(lxmlNode, encoding="UTF-8")

        return lxmlNode


    def _convertNODRecord2smods(self, lxmlNode):
        

        penvoerder, penvoerder_en, abstract, abstract_en, locatie, status, knaw_long = '', '', '', '', '', '', None
        # ORGANISATIE:
        if lxmlNode.xpath("boolean(count(//org:organisatie))", namespaces=namespaceMap):
            title = self._findAndBind(lxmlNode, '\n<titleInfo><title>%s</title></titleInfo>', '//org:naam_nl/text()')
            title_en = self._findAndBind(lxmlNode, '\n<titleInfo xml:lang="en"><title>%s</title></titleInfo>', '//org:naam_en/text()')
        
            taak = lxmlNode.xpath("//org:taak_nl/text()", namespaces=namespaceMap)
            if taak: abstract = '\n<abstract>%s</abstract>' % escapeXml(taak[0][:self._truncate_chars])
            taak = lxmlNode.xpath("//org:taak_en/text()", namespaces=namespaceMap)
            if taak: abstract_en = '\n<abstract xml:lang="en">%s</abstract>' % escapeXml(taak[0][:self._truncate_chars])
        
            # Locatie: In Dutch (NL) only!
            location = lxmlNode.xpath("//org:locatie/text()", namespaces=namespaceMap)
            if location: locatie = '\n<locatie>%s</locatie>' % escapeXml(location[0])
        
            knaw_long = '''<knaw_long xmlns="http://www.knaw.nl/narcis/1.0/long/"><metadata>%s%s<genre>organisation</genre>%s%s%s</metadata></knaw_long>''' % (
                title, title_en, locatie, abstract, abstract_en)
        # ACTIVITEIT:
        elif lxmlNode.xpath("boolean(count(//ond:activiteit))", namespaces=namespaceMap):
            title = self._findAndBind(lxmlNode, '\n<titleInfo><title>%s</title></titleInfo>', '//ond:title_nl/text()')
            title_en = self._findAndBind(lxmlNode, '\n<titleInfo xml:lang="en"><title>%s</title></titleInfo>',
                                         '//ond:title_en/text()')
        
            # Samenvatting:
            taak = lxmlNode.xpath("//ond:summary_nl/text()", namespaces=namespaceMap)
            if taak: abstract = '\n<abstract>%s</abstract>' % escapeXml(taak[0][:self._truncate_chars])
            taak = lxmlNode.xpath("//ond:summary_en/text()", namespaces=namespaceMap)
            if taak: abstract_en = '\n<abstract xml:lang="en">%s</abstract>' % escapeXml(taak[0][:self._truncate_chars])
        
            # Penvoerder:
            taak = lxmlNode.xpath("//ond:penvoerder/ond:naam[@xml:lang='nl']/text()", namespaces=namespaceMap)
            if taak: penvoerder = '\n<penvoerder xml:lang="nl">%s</penvoerder>' % escapeXml(taak[0])
            taak = lxmlNode.xpath("//ond:penvoerder/ond:naam[@xml:lang='en']/text()", namespaces=namespaceMap)
            if taak: penvoerder_en = '\n<penvoerder xml:lang="en">%s</penvoerder>' % escapeXml(taak[0])
        
            # Status onderzoek (C/D):
            taak = lxmlNode.xpath("//ond:status/text()", namespaces=namespaceMap)
            if taak: status = '\n<status>%s</status>' % escapeXml(taak[0])
        
            knaw_long = '''<knaw_long xmlns="http://www.knaw.nl/narcis/1.0/long/"><metadata>%s%s<genre>research</genre>%s%s%s%s%s</metadata></knaw_long>''' % (
                title, title_en, penvoerder, penvoerder_en, abstract, abstract_en, status)
        # PERSOON:
        elif lxmlNode.xpath("boolean(count(//prs:persoon))", namespaces=namespaceMap):
            # TODO: Moeten de expertise keywords wel in de abstract verschijnen?
            fullName = lxmlNode.xpath("//prs:fullName/text()", namespaces=namespaceMap)
            if not fullName:
                fullName.append('n.a.')
            else:
                fullName[0] = escapeXml(fullName[0])
            title = ('\n<titleInfo><title>%s</title></titleInfo>' % fullName[0])
            title_en = ('\n<titleInfo xml:lang="en"><title>%s</title></titleInfo>' % fullName[0])
        
            taak = lxmlNode.xpath("//prs:expertise_nl/text()", namespaces=namespaceMap)
            if taak: abstract = '\n<abstract>%s</abstract>' % escapeXml(taak[0][:self._truncate_chars])
            taak = lxmlNode.xpath("//prs:expertise_en/text()", namespaces=namespaceMap)
            if taak: abstract_en = '\n<abstract xml:lang="en">%s</abstract>' % escapeXml(taak[0][:self._truncate_chars])
        
            # Copy ALL nameIdentifiers + OLD <dai> tag ########
            str_name = '\n<name><type>personal</type><name>' + fullName[0] + '</name>'
            # Kijk of er een 'oude' dai-only tag aanwezig is:
            dai = self._findAndBind(lxmlNode, '\n<dai>info:eu-repo/dai/nl/%s</dai>', '//prs:persoon/prs:dai/text()')
            if dai: str_name += dai
        
            nids = lxmlNode.xpath("//prs:persoon/prs:nameIdentifier", namespaces=namespaceMap)
        
            for nid in nids:  # serialize complete tag and remove default namespace...
                nid_type = nid.xpath('self::prs:nameIdentifier/@type', namespaces=namespaceMap)
                nid_val = nid.xpath('self::prs:nameIdentifier/text()', namespaces=namespaceMap)
                if len(nid_type) > 0 and len(nid_val) > 0:
                    str_name += '''<nameIdentifier type="%s">%s</nameIdentifier>''' % (nid_type[0], nid_val[0])
            str_name += '</name>'
            # Einde nameIdentifier ########
        
            knaw_long = '''<knaw_long xmlns="http://www.knaw.nl/narcis/1.0/long/"><metadata>%s%s%s<genre>person</genre>%s%s</metadata></knaw_long>''' % (
                title, title_en, str_name, abstract, abstract_en)
        
        # We'll return a Lxml node here:
        parser = etree.XMLParser(remove_blank_text=True)
        if knaw_long is not None:
            try:
                return parse(StringIO(knaw_long), parser)
            except:
                print 'Error while parsing', knaw_long
                raise
        return knaw_long

    def _findAndBind(self, node, template, *xpaths):
        items = []
        for p in xpaths:
            items += node.xpath(p, namespaces=namespaceMap)
        return '\n'.join(template % escapeXml(item) for item in items)

    
    def smart_truncate(self, content, suffix=''):
        if len(content) <= self._truncate_chars:
            return content
        else:
            return ' '.join(content[:self._truncate_chars+1].split(' ')[0:-1]) + suffix

