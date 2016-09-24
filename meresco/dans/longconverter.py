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

namespacesmap = namespaces.copyUpdate({ #  See: https://github.com/seecr/meresco-xml/blob/master/meresco/xml/namespaces.py
    
    'dip'    : 'urn:mpeg:mpeg21:2005:01-DIP-NS',
    'dii'    : 'urn:mpeg:mpeg21:2002:01-DII-NS',
    'dai'    : 'info:eu-repo/dai',
    'gal'    : 'info:eu-repo/grantAgreement',
    'wmp'    : 'http://www.surfgroepen.nl/werkgroepmetadataplus',
    'prs'   : 'http://www.onderzoekinformatie.nl/nod/prs',
    'proj'   : 'http://www.onderzoekinformatie.nl/nod/act',
    'org'   : 'http://www.onderzoekinformatie.nl/nod/org',
    'long'  : 'http://www.knaw.nl/narcis/1.0/long/',
    'short' : 'http://www.knaw.nl/narcis/1.0/short/',
    'mods'  : 'http://www.loc.gov/mods/v3',
    'didl'  : 'urn:mpeg:mpeg21:2002:02-DIDL-NS',
    'norm'  : 'http://dans.knaw.nl/narcis/normalized',
})


HVSTR_NS = '{%s}' % namespacesmap['meta'] # '{http://meresco.org/namespace/harvester/meta}' 
DOCUMENT_NS = '{%s}' % namespacesmap['document'] # '{http://meresco.org/namespace/harvester/document}' 

MODS_VERSION = '3.6'

LONG_VERSION = '1.0'

MODS_NAMESPACE = namespacesmap['mods']
MODS = "{%s}" % MODS_NAMESPACE

NSMAP = {
    None : MODS_NAMESPACE,
    'xlink': 'http://www.w3.org/1999/xlink',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}

NORM_NS = '{%s}' % namespacesmap['norm'] 


class NormaliseOaiRecord(Converter):

    ACCESS_LEVELS = ['openAccess', 'restrictedAccess', 'closedAccess', 'embargoedAccess']

    def __init__(self, fromKwarg, toKwarg=None, name=None):
        Converter.__init__(self, name=name, fromKwarg=fromKwarg, toKwarg=toKwarg)
        self._truncate_chars = 300
        self._metadataformat = None
        self._openAccess = True
        

    def _convert(self, lxmlNode):
        self._openAccess = True #Reset AccesRights to openAcces

        record_part = lxmlNode.xpath("//document:document/document:part[@name='record']/text()", namespaces=namespacesmap)
        record_lxml = etree.fromstring(record_part[0]) # Geen xml.sax.saxutils.unescape() hier: Dat doet lxml reeds voor ons.
        self._metadataformat = MetadataFormat.getFormat(record_lxml) #TODO: pass it somehow from DNA, so we need to look this up only once per record...
        # TODO: uitzoeken waar dit nog meer plaats heeft???
        converted_record_lxml = self._convertRecordMetadataToLong(record_lxml)# Check en insert normalised mods into record part.
        record_txt = etree.tostring(converted_record_lxml, encoding="UTF-8") # convert from lxml to text...
        record_txt = record_txt.decode('utf-8') # Soms worden er chars opgestuurd die geen unicode zijn? Deze converteren we met geweld...
        lxmlNode.find('document:part[@name="record"]', namespaces=namespacesmap).text = record_txt # Set as text value...
        # etree.cleanup_namespaces(lxmlNode)
        return lxmlNode

    def _convertRecordMetadataToLong(self, lxmlNode):
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

        # De twee placeholders voor het originele- en genormaliseerde record:
        e_original_root = etree.Element(NORM_NS + "md_original")
        e_norm_root = etree.Element(NORM_NS + "normalized")

        if self._metadataformat is not None:
            # Create rootelement:
            # e_longroot = etree.SubElement(e_norm_root, namespacesmap.curieToTag('long:long'), nsmap={None:namespacesmap['long']})
            e_longroot = etree.Element(namespacesmap.curieToTag('long:long'), nsmap={None:namespacesmap['long']})
            e_longroot.set("version", LONG_VERSION)
            # Toplevel elements:
            self._getModificationDate(lxmlNode, e_longroot)
            self._getHumanStartPage(lxmlNode, e_longroot)
            self._getPersistentIdentifier(lxmlNode, e_longroot)
            self._getObjectFiles(lxmlNode, e_longroot)
            # All ObjectFiles have been looped through: accessright should now be known:
            self._getAccessRights(lxmlNode, e_longroot) #TODO: double check this.
            # Second level metadata elements:
            e_longmetadata = etree.Element("metadata")
            self._getTitleInfo(lxmlNode, e_longmetadata)
            e_longroot.append(e_longmetadata)
            print 'Long:', tostring(e_longroot)



            e_modsroot = etree.SubElement(e_norm_root, namespacesmap.curieToTag('mods:mods'), nsmap=NSMAP)
            e_modsroot.set("version", MODS_VERSION)
            e_modsroot.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-"+ MODS_VERSION.replace(".", "-") +".xsd")
            # e_modsroot.set("xmlns:xsi" , "http://www.w3.org/2001/XMLSchema-instance")

            if self._metadataformat in (MetadataFormat.MD_FORMAT[0], MetadataFormat.MD_FORMAT[1]):

                strTitle = lxmlNode.xpath("//dc:title/text()", namespaces=namespacesmap)
                e_titleInfo = etree.SubElement(e_modsroot, "titleInfo")
                e_title = etree.SubElement(e_titleInfo, "title").text = strTitle[0]
                strAbstract = lxmlNode.xpath("//dc:description/text()", namespaces=namespacesmap)
                if len(strAbstract) > 0:
                    e_abstract = etree.SubElement(e_modsroot, "abstract").text = strAbstract[0]

                strGenre = lxmlNode.xpath("//dc:type/text()", namespaces=namespacesmap)
                if len(strGenre) > 0:
                    e_genre = etree.SubElement(e_modsroot, "genre").text = strGenre[0]        

            elif self._metadataformat in (MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3]):
                
                strTitle = lxmlNode.xpath("//mods:titleInfo/mods:title/text()", namespaces=namespacesmap)
                if len(strTitle) > 0:
                    e_titleInfo = etree.SubElement(e_modsroot, "titleInfo")
                    e_title = etree.SubElement(e_titleInfo, "title").text = strTitle[0]

                strAbstract = lxmlNode.xpath("//mods:abstract/text()", namespaces=namespacesmap)
                if len(strAbstract) > 0:
                    e_abstract = etree.SubElement(e_modsroot, "abstract").text = strAbstract[0]

                strGenre = lxmlNode.xpath("//mods:genre/text()", namespaces=namespacesmap)
                if len(strGenre) > 0:
                    e_genre = etree.SubElement(e_modsroot, "genre").text = strGenre[0]

            elif self._metadataformat in (MetadataFormat.MD_FORMAT[5], MetadataFormat.MD_FORMAT[6], MetadataFormat.MD_FORMAT[7]): #NOD records
                NODLxml = self._convertNODRecord2long(lxmlNode)
                if NODLxml is not None:
                    e_norm_root.append(NODLxml.getroot())

        metadata_tags = lxmlNode.xpath("//oai:metadata/*", namespaces=namespacesmap)

        for child in metadata_tags:
            e_original_root.append(child) # voeg originele md toe aan placeholder origineel...
            metadata_tags.remove(child) # verwijder originele md van oai metadata tag...

        for child in lxmlNode.getchildren():
            # print child.tag, child.text

            if child.tag == namespacesmap.curieToTag('oai:metadata'):
                child.append(e_original_root)
                child.append(e_norm_root)
                e_original_root.text = child.text # Copy any (incorrect!) text node from metadata tag to the placeholder origineel.
                child.text = "" # Delete (incorrect!) text node from metadata tag.
        # print "MD_ORIGINAL:", etree.tostring(e_original_root)
        # print "CONVERTED:", etree.tostring(lxmlNode, encoding="UTF-8")

        return lxmlNode

        # MD_FORMAT[0] : NAMESPACEMAP.get('oai_dc'),
        # MD_FORMAT[1] : NAMESPACEMAP.get('oai_dc'),
        # MD_FORMAT[2] : NAMESPACEMAP.get('mods'),
        # MD_FORMAT[3] : NAMESPACEMAP.get('mods'),
        # MD_FORMAT[4] : NAMESPACEMAP.get('mods'),
        # MD_FORMAT[5] : NAMESPACEMAP.get('org'),
        # MD_FORMAT[6] : NAMESPACEMAP.get('proj'),
        # MD_FORMAT[7] : NAMESPACEMAP.get('prs'),

    def _convertNODRecord2long(self, lxmlNode):
        
        penvoerder, penvoerder_en, abstract, abstract_en, locatie, status, knaw_long = '', '', '', '', '', '', None

        # ORGANISATIE:
        if self._metadataformat == MetadataFormat.MD_FORMAT[5]:
            title = self._findAndBind(lxmlNode, '\n<titleInfo><title>%s</title></titleInfo>', '//org:naam_nl/text()')
            title_en = self._findAndBind(lxmlNode, '\n<titleInfo xml:lang="en"><title>%s</title></titleInfo>', '//org:naam_en/text()')
        
            taak = lxmlNode.xpath("//org:taak_nl/text()", namespaces=namespacesmap)
            if taak: abstract = '\n<abstract>%s</abstract>' % escapeXml(taak[0][:self._truncate_chars])
            taak = lxmlNode.xpath("//org:taak_en/text()", namespaces=namespacesmap)
            if taak: abstract_en = '\n<abstract xml:lang="en">%s</abstract>' % escapeXml(taak[0][:self._truncate_chars])
        
            # Locatie: In Dutch (NL) only!
            location = lxmlNode.xpath("//org:locatie/text()", namespaces=namespacesmap)
            if location: locatie = '\n<locatie>%s</locatie>' % escapeXml(location[0])
        
            knaw_long = '''<knaw_long xmlns="http://www.knaw.nl/narcis/1.0/long/"><metadata>%s%s<genre>organisation</genre>%s%s%s</metadata></knaw_long>''' % (
                title, title_en, locatie, abstract, abstract_en)
        # PROJECT:
        elif self._metadataformat == MetadataFormat.MD_FORMAT[6]:
            title = self._findAndBind(lxmlNode, '\n<titleInfo><title>%s</title></titleInfo>', '//proj:title_nl/text()')
            title_en = self._findAndBind(lxmlNode, '\n<titleInfo xml:lang="en"><title>%s</title></titleInfo>',
                                         '//proj:title_en/text()')
        
            # Samenvatting:
            taak = lxmlNode.xpath("//proj:summary_nl/text()", namespaces=namespacesmap)
            if taak: abstract = '\n<abstract>%s</abstract>' % escapeXml(taak[0][:self._truncate_chars])
            taak = lxmlNode.xpath("//proj:summary_en/text()", namespaces=namespacesmap)
            if taak: abstract_en = '\n<abstract xml:lang="en">%s</abstract>' % escapeXml(taak[0][:self._truncate_chars])
        
            # Penvoerder:
            taak = lxmlNode.xpath("//proj:penvoerder/proj:naam[@xml:lang='nl']/text()", namespaces=namespacesmap)
            if taak: penvoerder = '\n<penvoerder xml:lang="nl">%s</penvoerder>' % escapeXml(taak[0])
            taak = lxmlNode.xpath("//proj:penvoerder/proj:naam[@xml:lang='en']/text()", namespaces=namespacesmap)
            if taak: penvoerder_en = '\n<penvoerder xml:lang="en">%s</penvoerder>' % escapeXml(taak[0])
        
            # Status onderzoek (C/D):
            taak = lxmlNode.xpath("//proj:status/text()", namespaces=namespacesmap)
            if taak: status = '\n<status>%s</status>' % escapeXml(taak[0])
        
            knaw_long = '''<knaw_long xmlns="http://www.knaw.nl/narcis/1.0/long/"><metadata>%s%s<genre>research</genre>%s%s%s%s%s</metadata></knaw_long>''' % (
                title, title_en, penvoerder, penvoerder_en, abstract, abstract_en, status)
        # PERSOON:
        elif self._metadataformat == MetadataFormat.MD_FORMAT[7]:
            # TODO: Moeten de expertise keywords wel in de abstract verschijnen?
            fullName = lxmlNode.xpath("//prs:fullName/text()", namespaces=namespacesmap)
            if not fullName:
                fullName.append('n.a.')
            else:
                fullName[0] = escapeXml(fullName[0])
            title = ('\n<titleInfo><title>%s</title></titleInfo>' % fullName[0])
            title_en = ('\n<titleInfo xml:lang="en"><title>%s</title></titleInfo>' % fullName[0])
        
            taak = lxmlNode.xpath("//prs:expertise_nl/text()", namespaces=namespacesmap)
            if taak: abstract = '\n<abstract>%s</abstract>' % escapeXml(taak[0][:self._truncate_chars])
            taak = lxmlNode.xpath("//prs:expertise_en/text()", namespaces=namespacesmap)
            if taak: abstract_en = '\n<abstract xml:lang="en">%s</abstract>' % escapeXml(taak[0][:self._truncate_chars])
        
            # Copy ALL nameIdentifiers + OLD <dai> tag ########
            str_name = '\n<name><type>personal</type><name>' + fullName[0] + '</name>'
            # Kijk of er een 'oude' dai-only tag aanwezig is:
            dai = self._findAndBind(lxmlNode, '\n<dai>info:eu-repo/dai/nl/%s</dai>', '//prs:persoon/prs:dai/text()')
            if dai: str_name += dai
        
            nids = lxmlNode.xpath("//prs:persoon/prs:nameIdentifier", namespaces=namespacesmap)
        
            for nid in nids:  # serialize complete tag and remove default namespace...
                nid_type = nid.xpath('self::prs:nameIdentifier/@type', namespaces=namespacesmap)
                nid_val = nid.xpath('self::prs:nameIdentifier/text()', namespaces=namespacesmap)
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


    def _getModificationDate(self, lxmlNode, e_longRoot):
        datestamp = lxmlNode.xpath('//oai:header/oai:datestamp/text()', namespaces=namespacesmap)
        if len(datestamp) > 0:
            etree.SubElement(e_longRoot, "modificationDate").text = datestamp[0]

    def _getTitleInfo(self, lxmlNode, e_longmetadata, root='//mods:mods/'):
        # In contrast to all other translated tags(xml:lang="en"), this tag will ALWAYS have an xml:lang="en" and none xml:lang value.
        # Others (f.i. <abstract>) might lack the xml:lang="en" tag.
        if self._metadataformat in (MetadataFormat.MD_FORMAT[5], MetadataFormat.MD_FORMAT[6], MetadataFormat.MD_FORMAT[7]):
            title = self._findFirstXpath(lxmlNode, '//org:naam_nl/text()', '//proj:title_nl/text()', '//prs:fullName/text()')
            if len(title) > 0:
                etree.SubElement(etree.SubElement(e_longmetadata, "titleInfo"), "title").text = title[0]
                if self._metadataformat == MetadataFormat.MD_FORMAT[7]: # Person name also in english:
                    e_titleInfo = etree.SubElement(e_longmetadata, "titleInfo")
                    e_titleInfo.attrib[namespacesmap.curieToTag('xml:lang')] = "en"
                    etree.SubElement(e_titleInfo, "title").text = title[0]

            title_en = self._findFirstXpath(lxmlNode, '//org:naam_en/text()', '//proj:title_en/text()')
            if len(title_en) > 0:
                e_titleInfo = etree.SubElement(e_longmetadata, "titleInfo")
                e_titleInfo.attrib[namespacesmap.curieToTag('xml:lang')] = "en"
                etree.SubElement(e_titleInfo, "title").text = title_en[0]
        else:
            # In contrast to all other translated tags(xml:lang="en"), this tag will ALWAYS have an xml:lang="en" and none xml:lang value. Others (f.i. <abstract>) might lack the xml:lang="en" tag.
            # MD_FORMAT = ['oai_dc', 'didl_dc', 'didl_mods231', 'didl_mods30', 'didl_mods36', 'org', 'ond', 'prs']
            # SURFSHARE_FORMAT = ['oai_dc', 'didl_dc', 'didl_mmods', 'didl_mods231', 'didl_mods30', 'ore_rem']
            titleNL = ['',''] #wrapper for titleInfo string -> [('NL'||empty||!='EN')|| DC], ['EN' || [first titleInfo]].
            titleEN = None
            #Get title from any dc: (only ONE)
            if self._metadataformat in (MetadataFormat.MD_FORMAT[0], MetadataFormat.MD_FORMAT[1]): #if not fullmods:
                dc_titles = lxmlNode.xpath('//dc:title[1]/text()', namespaces=namespacesmap)  
                if dc_titles: # Found dc:title. Do NOT check if we're dealing with a subtitle (colon delimited according to SurfShare DC):
                    titleNL[0] = dc_titles[0]
            # Override found DC (sub)title with (m)mods's title value's:
            if self._metadataformat in (MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
                en = lxmlNode.xpath(root+"mods:titleInfo[@xml:lang='en']", namespaces=namespacesmap)
                nl = lxmlNode.xpath(root+"mods:titleInfo[@xml:lang='nl']", namespaces=namespacesmap)
                if len(nl) == 0: #If no Dutch, try to find tag without a language designation.
                    nl = lxmlNode.xpath(root+"mods:titleInfo[not(@xml:lang)]", namespaces=namespacesmap)
                    if len(nl) == 0: #If not empty language desigation, try to find tag with language designation other than 'en':
                        nl = lxmlNode.xpath(root+"mods:titleInfo[not(@xml:lang='en')]", namespaces=namespacesmap)
                        if len(nl) == 0: # Assign English lang.
                            nl = en
                if len(nl) > 0:
                    titleNL = self._titleFromTitleInfo(nl[0])
                if len(en) > 0:
                    titleEN = self._titleFromTitleInfo(en[0])
            if not titleEN or not titleEN[0] or titleEN[0] == '':
                titleEN = titleNL
            e_longmetadata.append(self._titleTag(titleNL))
            e_longmetadata.append(self._titleTag(titleEN, 'en'))


    def _titleFromTitleInfo(self, titleInfoNode):
        if titleInfoNode is not None:
            title = titleInfoNode.xpath('self::mods:titleInfo/mods:title/text()', namespaces=namespacesmap)
            subtitle = titleInfoNode.xpath('self::mods:titleInfo/mods:subTitle/text()', namespaces=namespacesmap)
        else:
            return
        if len(title) > 0:
            title = title[0].strip()
        if len(subtitle) > 0:
            subtitle = subtitle[0].strip()
        return [title, subtitle]


    def _titleTag(self, titles=['',''], xmllang=None):
        if not titles or not titles[0] or titles[0] == '':
            titles = ['None', None]
        e_titleinfo = etree.Element("titleInfo")
        if xmllang is not None:
            e_titleinfo.attrib[namespacesmap.curieToTag('xml:lang')] = xmllang
        e_title = etree.SubElement(e_titleinfo, "title").text = titles[0]
        subtitle = ''
        if titles[1]:
            e_subtitle = etree.SubElement(e_titleinfo, "subtitle").text = titles[1]
        return e_titleinfo


    def _getHumanStartPage(self, lxmlNode, e_longRoot):
        # DIDL or DC(1st dc:identifier)
        hsp = self._findFirstXpath(lxmlNode,
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@ref', #DIDL 3.0
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@ref', #fallback DIDL 2.3.1
        "//dc:identifier[contains(.,'://')]/text()", #fallback DC        
        "//mods:mods/mods:location/mods:url[contains(.,'://')]/text()", #fallback MODS
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref', #fallback DIDL 3.0
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref', #fallback DIDL 2.3.1
        "//dc:identifier[1]/text()") #Greedy fallback DC. If all else fails...
        if len(hsp) > 0:
            etree.SubElement(e_longRoot, "humanStartPage").text = hsp[0].strip()

    def _getPersistentIdentifier(self, lxmlNode, e_longRoot):
        pi = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Descriptor/didl:Statement/dii:Identifier/text()', namespaces=namespacesmap)
        if len(pi) > 0:
            etree.SubElement(e_longRoot, "persistentIdentifier").text = pi[0].strip()

    def _getObjectFiles(self, lxmlNode, e_longRoot):
        # MD_FORMAT = ['oai_dc', 'didl_dc', 'didl_mods231', 'didl_mods30', 'didl_mods36', 'org', 'ond', 'prs']
        # SURFSHARE_FORMAT = ['oai_dc', 'didl_dc', 'didl_mmods', 'didl_mods231', 'didl_mods30', 'ore_rem']
        e_objectFiles = None
        if self._metadataformat in (MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]): #FULLMODS only!
            if self._metadataformat in (MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]): # MODS >= 3.0
                objectfiles = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/objectFile"]', namespaces=namespacesmap)
            else: #Fallback to DIDL 2.3.1
                objectfiles = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/objectFile"]', namespaces=namespacesmap)
            if len(objectfiles) > 0: e_objectFiles = etree.SubElement(e_longRoot, "objectFiles")
            
            if self._metadataformat in (MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
                # >= DIDL3.0 only:
                # Get all accessRights for all objectFiles in one list:
                accesssRights = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/objectFile"]/didl:Descriptor/didl:Statement/dcterms:accessRights/text()', namespaces=namespacesmap)
                if (len(objectfiles) > 0 and len(accesssRights) == len(objectfiles) and str(accesssRights).lower().find('openaccess') == -1 ) or (len(objectfiles)==0):
                    self._openAccess = False
                    print "FOUND CLOSED ACCESS!"

            for objectfile in objectfiles:
                #create objectFile element:
                e_objectFile = etree.SubElement(e_objectFiles, "objectFile")
                #Look for resources to add:
                didl_resources = objectfile.xpath('self::didl:Item/didl:Component/didl:Resource', namespaces=namespacesmap)
                for resource in didl_resources:
                    e_resource = etree.SubElement(e_objectFile, "resource")
                    mimeType = resource.xpath('self::didl:Resource/@mimeType', namespaces=namespacesmap)
                    uri = resource.xpath('self::didl:Resource/@ref', namespaces=namespacesmap)
                    if mimeType:
                        e_resource.set("mimeType", mimeType[0])
                    if uri:
                        e_resource.set("ref", uri[0])
                        
                #Look for PI:3.0=mandatory; < 3.0=optional!
                pi = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dii:Identifier/text()', namespaces=namespacesmap)
                if pi:
                    e_persistentIdentifier = etree.SubElement(e_objectFile, "persistentIdentifier")
                    e_persistentIdentifier.text = pi[0].strip()

                #DIDL3.0 stuff:
                if self._metadataformat in (MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
                    #look for embargo:
                    embargo = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dcterms:available/text()', namespaces=namespacesmap)
                    if embargo:
                        e_embargo = etree.SubElement(e_objectFile, "embargo")
                        e_embargo.text = embargo[0].strip() 
                    #look for description:
                    descrip = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dc:description/text()', namespaces=namespacesmap)
                    if descrip:
                        e_descrip = etree.SubElement(e_objectFile, "description")
                        e_descrip.text = descrip[0].strip()
                    #look for published version(author/publisher):
                    publicationVersion = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/rdf:type/@rdf:resource[contains(.,"published") or contains(.,"author")]', namespaces=namespacesmap)
                    if publicationVersion: #both (author/publisher) may be available: we'll take the first one...
                        e_publicationVersion = etree.SubElement(e_objectFile, "publicationVersion")
                        e_publicationVersion.text = publicationVersion[0].strip()[publicationVersion[0].strip().rfind('/')+1:]
                    #Look for AccessRights:
                    oa = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dcterms:accessRights/text()', namespaces=namespacesmap)
                    if oa:
                        e_accessRights = etree.SubElement(e_objectFile, "accessRights")
                        if oa[0].lower().find('openaccess') >= 0:
                            e_accessRights.text = NormaliseOaiRecord.ACCESS_LEVELS[0]
                        else:
                            e_accessRights.text = NormaliseOaiRecord.ACCESS_LEVELS[2]

    def _getAccessRights(self, lxmlNode, e_longRoot):
        # Let op: Het aantal objectFiles dient bij aanroep reeds bekend te zijn in _getObjectFiles().
        # All formats different from DIDL3.0: No way to determine AccessRights (yet).
        # In this case, accessRights SHOULD be available from the metaPart (stack), if not, we will default to 'openAccess'
        accessRight = NormaliseOaiRecord.ACCESS_LEVELS[0] # default 'openAccess'

        # MD_FORMAT = ['oai_dc', 'didl_dc', 'didl_mods231', 'didl_mods30', 'didl_mods36', 'org', 'ond', 'prs']
        # SURFSHARE_FORMAT = ['oai_dc', 'didl_dc', 'didl_mmods', 'didl_mods231', 'didl_mods30', 'ore_rem']
        
        #Check for DC: See if any valid dc:rights element is available, if not AccessLevel is available from the requestscope (CA-mapper)
        if self._metadataformat in (MetadataFormat.MD_FORMAT[0]):
            # if hasattr(self.ctx, 'requestScope') and self.ctx.requestScope.get('accessRights') is not None:
            #     accessRight = self.ctx.requestScope.get('accessRights') #AR set in metaPart by mapper: Setting AR to stack value
            # else:
            accessLevels = lxmlNode.xpath('//dc:rights/text()', namespaces=namespacesmap)
            if len(accessLevels) > 0:
                for dc_accesslevel in accessLevels: # dc:rights may contain any kind of text, so we will look for the first valid occurence!
                    for ar in NormaliseOaiRecord.ACCESS_LEVELS:
                        if ar.lower() in dc_accesslevel.strip().lower():
                            accessRight = ar
                            break
        
        # if self._ssFormat not in (SurfShareFormat.SURFSHARE_FORMAT[4]): #No format found capable of setting accessRights from metadata...
        #     if hasattr(self.ctx, 'requestScope') and self.ctx.requestScope.get('accessRights') is not None:
        #         accessRight = self.ctx.requestScope.get('accessRights') #AR set in metaPart by mapper: Setting AR to stack value                
                
        if self._metadataformat in (MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]): #Gets accessRights from metadata:
            #Check accessRights from metaPart are available on the stack:
            # if hasattr(self.ctx, 'requestScope') and self.ctx.requestScope.get('accessRights') is not None: raise AccessRightsError('AccessRights should not be available from metaPart when using DIDL/MODS. (use of wrong wcp mapper?)')
            # else: accessRight = NormaliseOaiRecord.ACCESS_LEVELS[0] if self._openAccess == True else NormaliseOaiRecord.ACCESS_LEVELS[2] # Found AR in metadataPart...
            accessRight = NormaliseOaiRecord.ACCESS_LEVELS[0] if self._openAccess == True else NormaliseOaiRecord.ACCESS_LEVELS[2] # Found AR in metadataPart...
            
        etree.SubElement(e_longRoot, "accessRights").text = accessRight # default 'openAccess'


    def _findAndBind(self, node, template, *xpaths):
        items = []
        for p in xpaths:
            items += node.xpath(p, namespaces=namespacesmap)
        return '\n'.join(template % escapeXml(item) for item in items)


    def _findFirstXpath(self, node, *xpaths):
        # Will return the first non-empty list that matches an xpath.
        for x in xpaths:
            items = node.xpath(x, namespaces=namespacesmap)
            if len(items) > 0:
                return items
        return []

    # def _findAndBindFirst(self, node, template, *xpaths):
    #     # Will bind only the FIRST (xpath match/record) to the template. It will never return more than one templated element...
    #     items = []
    #     for p in xpaths:
    #         items = node.xpath(p, namespaces=namespacesmap)
    #         if len(items)>1:
    #             break
    #     for item in items:
    #         return template % escapeXml(item)
    #     return ''

    def smart_truncate(self, content, suffix=''):
        if len(content) <= self._truncate_chars:
            return content
        else:
            return ' '.join(content[:self._truncate_chars+1].split(' ')[0:-1]) + suffix

