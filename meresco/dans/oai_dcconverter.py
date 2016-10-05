## begin license ##
#
#
## end license ##

import sys

from lxml import etree
from lxml.etree import parse, _ElementTree, tostring

from StringIO import StringIO
from xml.sax.saxutils import escape as escapeXml
from copy import deepcopy
from weightless.core import NoneOfTheObserversRespond, DeclineMessage
from meresco.core import Observable
from meresco.components import lxmltostring, Converter
from meresco.dans.metadataformats import MetadataFormat
from meresco.dans.nameidentifier import Orcid, Dai, Isni, Rid, NameIdentifierFactory
from meresco.xml import namespaces
from meresco.dans.longconverter import NormaliseOaiRecord, BINDING_DELIMITER


namespacesmap = namespaces.copyUpdate({ #  See: https://github.com/seecr/meresco-xml/blob/master/meresco/xml/namespaces.py
    
    'dip'    : 'urn:mpeg:mpeg21:2005:01-DIP-NS',
    'dii'    : 'urn:mpeg:mpeg21:2002:01-DII-NS',
    'dai'    : 'info:eu-repo/dai',
    'gal'    : 'info:eu-repo/grantAgreement',
    'wmp'    : 'http://www.surfgroepen.nl/werkgroepmetadataplus',
    'prs'    : 'http://www.onderzoekinformatie.nl/nod/prs',
    'proj'   : 'http://www.onderzoekinformatie.nl/nod/act',
    'org'    : 'http://www.onderzoekinformatie.nl/nod/org',
    'long'   : 'http://www.knaw.nl/narcis/1.0/long/',
    'short'  : 'http://www.knaw.nl/narcis/1.0/short/',
    'mods'   : 'http://www.loc.gov/mods/v3',
    'didl'   : 'urn:mpeg:mpeg21:2002:02-DIDL-NS',
    'norm'   : 'http://dans.knaw.nl/narcis/normalized',
})

# MarcrelatorRoleTerms which are considered "authors":
marcrelatorAuthorRoles = ['aut','dis','pta','rev','ctb','cre','prg','edt']

class DcConverter(Converter):

    def __init__(self, fromKwarg, toKwarg=None, name=None, truncate_chars=300):
        Converter.__init__(self, name=name, fromKwarg=fromKwarg, toKwarg=toKwarg)
        self._truncate_chars = truncate_chars
        self._nsOAI = {'dc': namespacesmap['dc'], None : namespacesmap['oai_dc']}


    def _convert(self, lxmlNode):

        e_root = deepcopy(lxmlNode).getroot() # We need a deepcopy; otherwise we'll modify the lxmlnode by reference.
        # assert knawlong format:
        if namespacesmap['long'] in e_root.nsmap.values(): # Check if long is available.

            long_metadata = "//long:metadata/long"

            dc_root = etree.Element(namespacesmap.curieToTag('oai_dc:dc'), nsmap=self._nsOAI)

            # Simple mappings
            self._addDCelement('//long:humanStartPage', 'identifier', dc_root, lxmlNode)
            self._addDCelement('//long:persistentIdentifier', 'identifier', dc_root, lxmlNode) # Waarom lijken alleen de 'top' PI's hierin mee te komen?
            
            self._addDCelement(long_metadata+':publisher', 'publisher', dc_root, lxmlNode)
            self._addDCelement(long_metadata+':abstract', 'description', dc_root, lxmlNode)
            self._addDCelement(long_metadata+':dateIssued/long:parsed', 'date', dc_root, lxmlNode)
            self._addDCelement(long_metadata+':genre', 'type', dc_root, lxmlNode,  'info:eu-repo/semantics/')
            self._addDCelement(long_metadata+':language', 'language', dc_root, lxmlNode)                  

            volume = lxmlNode.xpath(long_metadata+':relatedItem[@type="host"]/long:part/long:volume/text()', namespaces=namespacesmap)
            issue = lxmlNode.xpath(long_metadata+':relatedItem[@type="host"]/long:part/long:issue/text()', namespaces=namespacesmap)
            start_page = lxmlNode.xpath(long_metadata+':relatedItem[@type="host"]/long:part/long:start_page/text()', namespaces=namespacesmap)
            end_page = lxmlNode.xpath(long_metadata+':relatedItem[@type="host"]/long:part/long:end_page/text()', namespaces=namespacesmap)
            issn = lxmlNode.xpath(long_metadata+':relatedItem[@type="host"]/long:publication_identifier[@type="issn"]/text()', namespaces=namespacesmap)
            titleInfo = lxmlNode.xpath(long_metadata+':relatedItem[@type="host"]/long:titleInfo/long:title/text()', namespaces=namespacesmap)
            
            dc_source = ''          
            if volume and volume[0].strip():
                dc_source += 'VOLUME='+volume[0].strip()+';'
            if issue and issue[0].strip():
                dc_source += 'ISSUE='+issue[0].strip()+';'
            if start_page and start_page[0].strip():
                dc_source += 'STARTPAGE='+start_page[0].strip()+';'
            if end_page and end_page[0].strip():
                dc_source += 'ENDPAGE='+end_page[0].strip()+';'
            if issn and issn[0].strip():
                dc_source += 'ISSN='+issn[0].strip()+';'
            if titleInfo and titleInfo[0].strip():
                dc_source += 'TITLE='+titleInfo[0].strip()+';'

            # The next two dc:source lines are OpenAIRE v3.0:
            hostCitation = lxmlNode.xpath(long_metadata+':hostCitation'+'/text()', namespaces=namespacesmap)
            if hostCitation and hostCitation[0].strip(): # Remove all markup(!?) from the hostcitation.  
                citation = hostCitation[0].strip().replace("<i>", "").replace("</i>", "")
                # Strip the ISSN, if available:
                issn_pos = citation.rfind(". ISSN")
                if issn_pos > 0:
                    citation = citation[:issn_pos]
                etree.SubElement(dc_root, namespacesmap.curieToTag('dc:source'), nsmap=self._nsOAI).text = citation
            if issn and issn[0].strip(): # Add the ISSN on the next (dc:source) line if available:
                etree.SubElement(dc_root, namespacesmap.curieToTag('dc:source'), nsmap=self._nsOAI).text = 'urn:issn:'+issn[0].strip()
            # Add key / value pairs: ISSN=10944087;VOLUME=19;ISSUE=3;STARTPAGE=2093;ENDPAGE=2104;TITLE=Optics Express
            if dc_source != '':
                etree.SubElement(dc_root, namespacesmap.curieToTag('dc:source'), nsmap=self._nsOAI).text = dc_source[:-1]

            #long:rightsDescription => dc:rights. We will split
            rights = lxmlNode.xpath('//long:rightsDescription/text()', namespaces=namespacesmap)
            for right in rights:
                for splitted_right in right.split(BINDING_DELIMITER):
                    etree.SubElement(dc_root, namespacesmap.curieToTag('dc:rights'), nsmap=self._nsOAI).text = splitted_right

            #Object files
            files = lxmlNode.xpath('//long:objectFiles/long:objectFile', namespaces=namespacesmap)
            for file in files:
                uri = file.xpath('self::long:objectFile/long:resource/@ref', namespaces=namespacesmap)
                mime = file.xpath('self::long:objectFile/long:resource/@mimeType', namespaces=namespacesmap)
                if uri:
                    etree.SubElement(dc_root, namespacesmap.curieToTag('dc:relation'), nsmap=self._nsOAI).text = uri[0]
                if mime:
                    etree.SubElement(dc_root, namespacesmap.curieToTag('dc:format'), nsmap=self._nsOAI).text = mime[0]

            #Title TODO: subtitle
            title_ = ""
            titleInfos = lxmlNode.xpath(long_metadata+':titleInfo', namespaces=namespacesmap)
            for titleInfo in titleInfos:
                titles = titleInfo.xpath('self::long:titleInfo/long:title/text()', namespaces=namespacesmap)
                subtitles = titleInfo.xpath('self::long:titleInfo/long:subtitle/text()', namespaces=namespacesmap)
                if titles:
                    title = titles[0]
                    if subtitles:
                        title = title + ': ' + subtitles[0]
                    if title != title_:
                        etree.SubElement(dc_root, namespacesmap.curieToTag('dc:title'), nsmap=self._nsOAI).text = title
                        title_=title
            #Names
            names = lxmlNode.xpath(long_metadata+':name', namespaces=namespacesmap)
            for name in names:
                dc_role = 'contributor'
                family = given = fullname = ''
                roleTerm = name.xpath('self::long:name/long:mcRoleTerm/text()', namespaces=namespacesmap)
                if roleTerm and roleTerm[0].strip():
                    roleTerm = roleTerm[0].strip()
                    if roleTerm in marcrelatorAuthorRoles:
                        dc_role = 'creator'
                    family = name.xpath('self::long:name/long:family/text()', namespaces=namespacesmap)
                    given = name.xpath('self::long:name/long:given/text()', namespaces=namespacesmap)
                    fullname = name.xpath('self::long:name/long:unstructured/text()', namespaces=namespacesmap)
                    if fullname and fullname[0].strip():
                        fullname = fullname[0].strip()
                    else:
                        fullname = ''
                    if family and family[0].strip() and given and given[0].strip():
                        fullname = family[0].strip() + ', ' + given[0].strip()
                    if not fullname and family and family[0].strip():
                        fullname = family[0].strip()
                    if fullname:
                        etree.SubElement(dc_root, namespacesmap.curieToTag('dc:' + dc_role), nsmap=self._nsOAI).text = fullname

            #ISSN
            issns = lxmlNode.xpath('//long:relatedItem/long:publication_identifier[@type="issn"]/text()', namespaces=namespacesmap)
            for topic in issns:
                etree.SubElement(dc_root, namespacesmap.curieToTag('dc:isPartOf'), nsmap=self._nsOAI).text = 'urn:issn:'+topic.strip()

            #ISBN
            issns = lxmlNode.xpath('//long:relatedItem/long:publication_identifier[@type="isbn"]/text()', namespaces=namespacesmap)
            for topic in issns:
                etree.SubElement(dc_root, namespacesmap.curieToTag('dc:isPartOf'), nsmap=self._nsOAI).text = 'urn:isbn:'+topic.strip()

            # Alle MODS /Identifiers overnemen:
            identifierList = lxmlNode.xpath('//long:metadata/long:publication_identifier', namespaces=namespacesmap)
            for identifier in identifierList:
                idType = identifier.attrib.get('type')
                if idType.lower() in ['issn', 'isbn']: # Re-create isbn or issn to a valid urn:
                    idText = 'urn:' + idType.lower() + ":" + identifier.text
                else: 
                    idText = identifier.text
                etree.SubElement(dc_root, namespacesmap.curieToTag('dc:identifier'), nsmap=self._nsOAI).text = idText
                
            #Topics
            topics = lxmlNode.xpath(long_metadata+':subject/long:topic/text()', namespaces=namespacesmap)
            for topic in topics:
                etree.SubElement(dc_root, namespacesmap.curieToTag('dc:subject'), nsmap=self._nsOAI).text = topic

            #Coverages
            coverages = lxmlNode.xpath(long_metadata+':coverage/text()', namespaces=namespacesmap)
            for coverage in coverages:
                etree.SubElement(dc_root, namespacesmap.curieToTag('dc:coverage'), nsmap=self._nsOAI).text = coverage

            #Formats
            formats = lxmlNode.xpath(long_metadata+':format/text()', namespaces=namespacesmap)
            for format in formats:
                etree.SubElement(dc_root, namespacesmap.curieToTag('dc:format'), nsmap=self._nsOAI).text = format

            #1. FundingInfo & accessRights
            GAcodes = lxmlNode.xpath('//long:grantAgreements/long:grantAgreement/long:code/text()', namespaces=namespacesmap)
            if GAcodes: # EC_fundedresources stuff.
                for GAcode in GAcodes:
                    etree.SubElement(dc_root, namespacesmap.curieToTag('dc:relation'), nsmap=self._nsOAI).text = GAcode       
    
                #2. accessRights:
                    # Check for any embargoed files:
                    # true: dc:rights -> embargoedAccess
                    # false: dc:rights -> long:accessRights                
                embargoes = lxmlNode.xpath('//long:objectFile/long:embargo/text()', namespaces=namespacesmap)
                blnHasEmbargo = False
                for embargo in embargoes:
                    embargo_date = NormaliseOaiRecord('lxml')._normaliseDate(embargo) # TODO: refactor!
                    if embargo_date != '':
                        etree.SubElement(dc_root, namespacesmap.curieToTag('dc:date'), nsmap=self._nsOAI).text = 'info:eu-repo/date/embargoEnd/' + embargo_date
                        blnHasEmbargo = True
                if blnHasEmbargo:
                    etree.SubElement(dc_root, namespacesmap.curieToTag('dc:rights'), nsmap=self._nsOAI).text = 'info:eu-repo/semantics/embargoedAccess'
                else:
                    self._addDCelement('//long:accessRights', 'rights', dc_root, lxmlNode,  'info:eu-repo/semantics/')
            else: # Always copy accesslevel (OpenAIRE (M))
                self._addDCelement('//long:accessRights', 'rights', dc_root, lxmlNode,  'info:eu-repo/semantics/')
            
            return etree.ElementTree(dc_root)
        else:
            return None

    def _addDCelement(self, longPath, dcPath, dc_root, lxmlNode, dc_prefix = ''):
        longElem = lxmlNode.xpath(longPath+'/text()', namespaces=namespacesmap)
        if longElem and longElem[0].strip():
            etree.SubElement(dc_root, namespacesmap.curieToTag('dc:'+dcPath), nsmap=self._nsOAI).text = dc_prefix + longElem[0].strip()


    def _isISO8601(self, datestring):
        try:
            parseDate(datestring)
        except ValueError:
            return False
        return True

        def __str__(self):
            return 'KNAWLong2DC'
