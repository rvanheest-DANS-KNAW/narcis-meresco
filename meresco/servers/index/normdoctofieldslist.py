## begin license ##
#
# "Meresco Examples" is a project demonstrating some of the
# features of various components of the "Meresco Suite".
# Also see http://meresco.org.
#
# Copyright (C) 2016 Seecr (Seek You Too B.V.) http://seecr.nl
#
# This file is part of "Meresco Examples"
#
# "Meresco Examples" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Examples" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Examples"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from meresco.core import Observable
from meresco.xml.namespaces import tagToCurie, curieToTag

from lxml import etree
from lxml.etree import parse, _ElementTree, tostring, _Element
from StringIO import StringIO
from meresco.xml import namespaces

from meresco.dans.longconverter import NormaliseOaiRecord

from re import compile
from meresco.dans.nameidentifier import Orcid, Dai, Isni, Rid, NameIdentifierFactory


namespacesmap = namespaces.copyUpdate({ #  See: https://github.com/seecr/meresco-xml/blob/master/meresco/xml/namespaces.py
    
    'dip'    : 'urn:mpeg:mpeg21:2005:01-DIP-NS',
    'dii'    : 'urn:mpeg:mpeg21:2002:01-DII-NS',
    'dai'    : 'info:eu-repo/dai',
    'gal'    : 'info:eu-repo/grantAgreement',
    'wmp'    : 'http://www.surfgroepen.nl/werkgroepmetadataplus',
    'prs'    : 'http://www.onderzoekinformatie.nl/nod/prs',
    'prj'   : 'http://www.onderzoekinformatie.nl/nod/act',
    'org'    : 'http://www.onderzoekinformatie.nl/nod/org',
    'long'   : 'http://www.knaw.nl/narcis/1.0/long/',
    'short'  : 'http://www.knaw.nl/narcis/1.0/short/',
    'mods'   : 'http://www.loc.gov/mods/v3',
    'didl'   : 'urn:mpeg:mpeg21:2002:02-DIDL-NS',
    'norm'   : 'http://dans.knaw.nl/narcis/normalized',
})

WCPNODCOLLECTION = ['project', 'organisation', 'person']
WCPEDUCOLLECTION = ['publication', 'dataset' ]
WCPCOLLECTION =  WCPEDUCOLLECTION + WCPNODCOLLECTION
UNQUALIFIED_TERMS = ''  #'__all__'


# print "TAGTOCURIE:", tagToCurie(repokind.tag), repokind.tag
# namespaces.tagToCurie('{http://steiny.org/steiny}:steiny')
# TAGTOCURIE: meta:id {http://meresco.org/namespace/harvester/meta}id

# RegEx to find dd_price field value's (price's name, without year and prefix 'NWO'):
priceRegex = compile('NWO\\s{0,1}\\-\\s{0,1}(\\w*?)\\s[1-2]{1}[0-9]{3}.*?')

# MarcrelatorRoleTerms which are considered "authors":
marcrelatorAuthorRoles = ['aut','dis','pta','rev','ctb','cre','prg','edt']

# Known (NOD person) nameIdentifiers to look for:
personNameIdentifiers = ['dai-nl', 'orcid', 'isni', 'nod-prs']


def enum(**enums):
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)


Coll = enum(PUB='publication', DAT='dataset', ORG='organisation', PRJ='project', PRS='person')
# print "DATA:", Collection.DAT



def removeNamespace(tagName):
    return '}' in tagName and tagName.split('}')[1] or tagName


def getNamespace(tagName):
    return '}' in tagName and tagName.split('}')[0][1:] or ''

# Een simpele mapping van velden die 'slechts' hernoemt dienen te worden, voordat ze de index in verwdijnen.
# Voor (samengestelde) velden die nog een (inhoudelijke) bewerking nodig hebben moet Xpath gebruikt worden.
# TODO: alle index field names met ergens 'identifier' zijn hernoemt naar 'id'...
fieldnamesMapping = {
    'long.metadata.dateIssued.parsed'      : 'dateissued',
    'long.metadata.genre'                  : 'pubtype',
    'long.metadata.publisher'              : 'publisher',
    'long.metadata.language'               : 'language',
    'long.metadata.coverage'               : 'coverage',
    'long.metadata.format'                 : 'format',
    'long.metadata.relatedItem.placeTerm'       : UNQUALIFIED_TERMS, # __all__
    'long.metadata.relatedItem.titleInfo.title' : UNQUALIFIED_TERMS, # __all__
    'long.metadata.relatedItem.publisher'       : UNQUALIFIED_TERMS, # __all__
    'long.metadata.grantAgreements.grantAgreement.code' : 'fundingid',
    'long.accessRights'                    : 'access',
    'long.persistentIdentifier'            : 'persistentid',
    'long.humanStartPage'            : 'humanstartpage',
    'organisatie.acroniem'             : 'acroniem',
    'organisatie.taak_en'              : 'abstract_en',
    'organisatie.taak_nl'              : 'abstract',
    'organisatie.categories.category.term' : 'category_term',
    'activiteit.summary_nl'            : 'abstract',
    'activiteit.summary_en'            : 'abstract_en',
    'activiteit.title_en'              : 'title_en',
    'activiteit.title_nl'              : 'title',
    'activiteit.status'                : 'status',
    'persoon.titulatuur_achter'        : 'titulatuur_achter',
    'persoon.categories.category.term' : 'category_term',
    }

MetaFieldNamesToXpath = {
    'oai:id'        : '/meta:meta/meta:record/meta:id/text()',
    'dare:id'       : '/meta:meta/meta:record/meta:id/text()',
    'meta:repositoryid'     : '/meta:meta/meta:repository/meta:id/text()',
    'meta:repositorygroupid': '/meta:meta/meta:repository/meta:repositoryGroupId/text()',
    'meta:collection'       : '/meta:meta/meta:repository/meta:collection/text()',
    }


fieldNamesXpathMap = {
    'subject'        : "//*[local-name()='topic' or local-name()='expertise_nl' or local-name()='expertise_en']/text()", # Expertise from personrecord or topics from Long:
    'leeropdracht'   : "//*[local-name()='leeropdracht_en' or local-name()='leeropdracht_nl']/text()", # Leeropdracht from personrecord
    'nids'           : "//long:relatedItem//long:nameIdentifier/text()", # All nid's: also from relatedItems
    'abstract'       : "//long:metadata/long:abstract[not (@xml:lang)]/text()", # 'abstract' field from KNAWLONG.
    'abstract_en'    : "//long:metadata/long:abstract[@xml:lang='en']/text()", # 'abstract_en' field from KNAWLONG.
    'title'          : "//long:metadata/long:titleInfo[not (@xml:lang)]/long:*/text()", #'title'+'subtitle' field from KNAWLONG.
    'title_en'       : "//long:metadata/long:titleInfo[@xml:lang='en']/long:*/text()", #'title_en'+'subtitle field from KNAWLONG.
    'dd_year'        : "//long:metadata/long:dateIssued/long:parsed/text()", # Parsed (normalized) datefield from KNAWLONG.
    'coverage'       : "//long:metadata/long:coverage/text()", # 'coverage' field from KNAWLONG.
    'format'         : "//long:metadata/long:format/text()", # 'format' field from KNAWLONG.
    'dd_prices'      : "//prs:persoon/prs:prices/prs:price/text()",
    'dd_werkzaamheid': "//prs:persoon/prs:jobs/prs:job",
    'titulatuur'     : "//prs:persoon/prs:titulatuur/text()",
    'dd_cat'         : "//*[local-name()='category' and (@code)]", # Alle category elementen met attribuut 'code=', zonder namespace...(staan in zowel PRS als ORG...)
    'dd_thesis'      : "//prj:dissertatie[contains(.='true')]", # Alle promotie onderzoeken... xpath retourneerd een boolean...
    'dd_institute'   : "//org:organisatie/@code",
    'dd_os'          : "//org:organisatie/@code", # Onderzoekschool
    'dd_penv'        : "//prj:activiteit/prj:penvoerder/@instituut_code", # HarremaCode van penvoerend instituut.
    'dd_fin'         : "//prj:activiteit/prj:financier/@instituut_code", # HarremaCode van financierend instituut.
    'publicationid'  : "//long:publication_identifier/text()", # TODO: Bestaat dit veld in LONG??? MODS:identifier from mods root as well as relatedItem (mostly: isbn, issn, doi etc.)
    'pidref'         : "//long:long/long:persistentIdentifier/@ref", # Physical location to wich the pubId reffers to. (BRI)
    }




class NormdocToFieldsList(Observable):

    def __init__(self, verbose=False, truncate_chars=300):
        Observable.__init__(self)
        self._verbose = verbose
        self._truncate_chars = truncate_chars
        self._fieldslist = []

    def add(self, lxmlNode, **kwargs):
        
        self._fieldslist = [] # reset list
        # hier komt een compleet meresco:document binnen als LXMLnode:
        # uploadid = kwargs['identifier']
        # print '###', kwargs['identifier'], '###'

        # Get meta, header and metadata part(='long') from the normdoc:
        e_metapart = etree.fromstring(lxmlNode.xpath('/document:document/document:part[@name="meta"]/text()', namespaces=namespacesmap)[0])
        wcp_collection = e_metapart.xpath('/meta:meta/meta:repository/meta:collection/text()', namespaces=namespacesmap)[0]
         
        # print "lxml metapart:", tostring(e_metapart)

        e_recordpart = etree.fromstring(lxmlNode.xpath('/document:document/document:part[@name="record"]/text()', namespaces=namespacesmap)[0])
        # print "lxml recordpart:", tostring(e_recordpart)

        # Add known meta fields for all records: 
        for field, xpad in MetaFieldNamesToXpath.iteritems():
            self._fieldslist.append((field, e_metapart.xpath(xpad, namespaces=namespacesmap)[0]))
            if self._verbose: print 'addField:', field.upper(), "-->", e_metapart.xpath(xpad, namespaces=namespacesmap)[0]

        record = None
        if wcp_collection in WCPNODCOLLECTION:
            record = e_recordpart.xpath('//prs:persoon | //prj:activiteit | //org:organisatie', namespaces=namespacesmap)
        else:
            record = e_recordpart.xpath('//norm:normalized/long:long', namespaces=namespacesmap)
        self._fillFieldslist(record[0], '')

        self._addAuthorsAndNamesFields(record[0], wcp_collection)
        
        for field, xpad in fieldNamesXpathMap.iteritems():
            self._findAndAddToFieldslist(record[0], field, xpad)

        # Ready filling, now call add method:
        yield self.all.add(fieldslist=self._fieldslist, **kwargs)


    def _fillFieldslist(self, aNode, parentName): # NOD-nodes and Long nodes will pass here...
        if type(aNode) != _Element:
            print "type(aNode) != _Element"
            return
        if parentName:
            parentName += '.'
        localName = removeNamespace(aNode.tag)
        fieldname = parentName + localName
        value = aNode.text
        # send addField message
        if value and value.strip() and fieldnamesMapping.has_key(fieldname):
            # Map all accessRights other than 'openAccess' to 'closedAccess' into the index:
            if fieldname == 'long.accessRights' and value.strip().lower() not in (NormaliseOaiRecord.ACCESS_LEVELS[0].lower(), NormaliseOaiRecord.ACCESS_LEVELS[2].lower()):
                if self._verbose: print 'Changing', value, 'to', NormaliseOaiRecord.ACCESS_LEVELS[2]
                value = NormaliseOaiRecord.ACCESS_LEVELS[2]
            self._fieldslist.append((fieldnamesMapping.get(fieldname), value.strip().replace('\n', '')))
            if self._verbose: print 'addField:', fieldnamesMapping.get(fieldname).upper(), "-->", value.strip().replace('\n', '')[:self._truncate_chars]
            #Old dare-id for resolving old record pages:
            # if fieldname == 'header.identifier': self.do.addField(name='dare-identifier', value=value.strip().replace('\n', '').replace('.', '').replace(':', '').replace('/', '').replace('&', ''))
        elif value and value.strip() and fieldname=='persoon.fullName': # uit NOD_PRS
            self._fieldslist.append(('title', value.strip().replace('\n', '')))
            self._fieldslist.append(('title_en', value.strip().replace('\n', '')))
            self._fieldslist.append(('sort_title', value.strip().replace('\n', ''))) #PRS sorteren op achternaam
            self._fieldslist.append(('sort_title_en', value.strip().replace('\n', ''))) #PRS sorteren op achternaam
            if self._verbose:
                print 'addField:', 'title'.upper(), "-->", value.strip().replace('\n', '')[:self._truncate_chars]
                print 'addField:', 'title_en'.upper(), "-->", value.strip().replace('\n', '')[:self._truncate_chars]
                print 'addField:', 'sort_title'.upper(), "-->", value.strip().replace('\n', '')[:self._truncate_chars]
                print 'addField:', 'sort_title_en'.upper(), "-->", value.strip().replace('\n', '')[:self._truncate_chars]
        elif value and value.strip() and fieldname=='organisatie.naam_en': # uit NOD_ORG
            self._fieldslist.append(('title_en', value.strip().replace('\n', '')))
            self._fieldslist.append(('sort_title_en', value.strip().replace('\n', ''))) #ORG sorteren op naam
            if self._verbose:
                print 'addField:', 'title_en'.upper(), "-->", value.strip().replace('\n', '')[:self._truncate_chars]
                print 'addField:', 'sort_title_en'.upper(), "-->", value.strip().replace('\n', '')[:self._truncate_chars]
        elif value and value.strip() and fieldname=='organisatie.naam_nl': # uit NOD_ORG
            self._fieldslist.append(('title', value.strip().replace('\n', '')))
            self._fieldslist.append(('sort_title', value.strip().replace('\n', ''))) #ORG sorteren op naam
            if self._verbose:
                print 'addField:', 'title'.upper(), "-->", value.strip().replace('\n', '')[:self._truncate_chars]
                print 'addField:', 'sort_title'.upper(), "-->", value.strip().replace('\n', '')[:self._truncate_chars]
        for child in aNode.getchildren():  # Recursief verder...
            self._fillFieldslist(child, fieldname)


    def _findAndAddToFieldslist(self, lxmlNode, fieldName, xpath):
        # Adds fieldnames and values to the fieldslist list.
        results = lxmlNode.xpath(xpath, namespaces=namespacesmap)
        if not results:
            return
        # elif fieldName == 'nids':
        #     # Unfortunately tokenizing DAIs goes wrong: 'nl/071791013' will be added to the index instead of '071791013', so searching on postfix ('071791013') is not possible.
        #     # Problem seems to be some 'intelligent' escaping (StandardTokenizer), since a dai like 'info:eu-repo/dai/nl/lettershereinsteadofnumbers' is tokenized correctly / allows for searching on postfix ('lettershereinsteadofnumbers')??
        #     # Escaping '/' with '\' doesn't do the job: one cannot search for a 'complete' DAI anymore, but postfix search OK...
        #     # So we add the postfix separately: addField:'info:eu-repo/dai/nl/15081968' and addField:'15081968', so we can find them either way.
        #     for dai in results:
        #         nameId = Dai(dai.replace('\n', ''))
        #         if nameId.is_valid():
        #             if self._verbose: print 'addField:', fieldName.upper(), "-->", nameId.get_id()
        #             self._fieldslist.append((fieldName, nameId.get_id()))
        #             for variant in nameId.getTypedVariants():
        #                 self._fieldslist.append(( '', variant ))
        #                 if self._verbose: print 'addField:',  "__all__ -->", variant
        elif fieldName == 'dd_year':
            if self._verbose: print 'addField:', fieldName.upper(), results[0].strip().replace('\n', ''), "--->", self._getYearGroupForDrilldown( results[0].strip().replace('\n', '') )
            self._fieldslist.append((fieldName, self._getYearGroupForDrilldown( results[0].strip().replace('\n', '') )))
        elif fieldName == 'dd_prices':
            for price in results:
                if self._verbose: print 'addField:', fieldName.upper(), price.strip().replace('\n', ''), "--->", self._getPriceNameForDrilldown( price.strip().replace('\n', '') )
                self._fieldslist.append((fieldName, self._getPriceNameForDrilldown( price.strip().replace('\n', '') )))
        elif fieldName == 'dd_cat':
            for category in results:
                class6 = self._getCodeFromCategory( category )
                # Add the catagory itself:
                if self._verbose: print 'addField:', fieldName.upper(), "-->", class6
                self._fieldslist.append((fieldName, class6))
                # Add the parent catagories:
                for index, char in enumerate(class6[::-1]):
                    if char!='0' and index < 4:
                        if self._verbose: print 'addField:', fieldName.upper(), "-->", class6[:5-index].ljust(6, '0')
                        self._fieldslist.append((fieldName, class6[:5-index].ljust(6, '0')))
        elif fieldName == 'titulatuur': #'Prof.dr.ing.' persons should be found searching 'prof' only!?
            subtitles = results[0].split('.')
            if self._verbose: print 'addField:', fieldName.upper(), "-->", results[0]
            self._fieldslist.append((fieldName, results[0]))
            for title in subtitles:
                if self._verbose and not title=='': print 'addField:', "-->", fieldName.upper(), title
                if not title=='': self._fieldslist.append((fieldName, title))
        elif fieldName == 'dd_werkzaamheid':
            for werkzaamheid in results:
                inst, func = self._getWerkzaamheidForDrilldownFromJobs(werkzaamheid)
                if (inst and func):
                    if self._verbose: print 'addField:', "dd_institute".upper(), "-->", inst
                    if self._verbose: print 'addField:', "dd_position".upper(), "-->", func
                    if self._verbose: print 'addField:', fieldName.upper(), "-->", inst+':'+func
                    self._fieldslist.append(("dd_institute", inst))
                    self._fieldslist.append(("dd_position", func))
                    self._fieldslist.append((fieldName, inst+':'+func))
                elif (func): # Only function was given: 'LCT' only!
                    if self._verbose: print 'addField:', "dd_position".upper(), "-->", func
                    self._fieldslist.append(("dd_position", func))
        elif fieldName == 'dd_thesis': #results is a boolean (returned by Xpath)...
            if self._verbose: print 'addField:', fieldName.upper(), "-->", str(results).lower()
            self._fieldslist.append((fieldName, str(results).lower()))
            # Replaced to generic elif@bottom ;-)
            # elif fieldName == 'publication_identifier': #results are all <publication_identifier> tags from mods root, as well as mods/related_item.
            #     for pid in results:
            #         if self._verbose: print 'addField:', fieldName.upper(), "-->", pid
            #         self.do.addField(name=fieldName, value=pid)
        elif fieldName == 'dd_institute': #Harrema code from an organisation. =Bovenliggend instituut: exactly 1
            dd_inst = self._getInstForDD(results[0])
            if (dd_inst):
                if self._verbose: print 'addField:', fieldName.upper(), "-->", dd_inst
                self._fieldslist.append((fieldName, dd_inst))
        elif fieldName == 'dd_penv': #Harrema code from an organisation. (Penvoerder): zero or more.
            for instituut_code in results:
                dd_inst = self._getInstForDD(instituut_code)
                if (dd_inst):
                    if self._verbose: print 'addField:', fieldName.upper(), "-->", dd_inst
                    self._fieldslist.append((fieldName, dd_inst))
        elif fieldName == 'dd_fin': #Harrema code from an organisation. (Financier): zero or more.
            for instituut_code in results:
                dd_inst = self._getInstForFin_DD(instituut_code)
                if (dd_inst):
                    if self._verbose: print 'addField:', fieldName.upper(), "-->", dd_inst
                    self._fieldslist.append((fieldName, dd_inst))
        elif fieldName == 'dd_os': #Onderzoekschool:
            dd_inst = self._getOSchoolForDD(results[0])
            if (dd_inst):
                if self._verbose: print 'addField:', fieldName.upper(), "-->", dd_inst
                self._fieldslist.append((fieldName, dd_inst))
        elif fieldName in ('coverage', 'format', 'publication_identifier'):
            for result in results:
                if self._verbose: print 'addField:', fieldName.upper(), "-->", result
                self._fieldslist.append((fieldName, result))               
        else:  # All other remaining results are joined with a space:
            self._fieldslist.append((fieldName, ' '.join(results).replace('\n', ''))) 
            if self._verbose: print 'adddField:', fieldName.upper(), "-->", ' '.join(results).replace('\n', '')[:self._truncate_chars]

    # returns the year category, used for drilldown: <1900, <1910 etc.
    def _getYearGroupForDrilldown(self, date_string):
        if date_string and date_string.strip() and len(date_string.strip()) >= 4:
            YYYY = int(date_string.strip()[:4])
            if YYYY < 1900: # first category (all before 1900)
                return '1000'
            elif YYYY >= 1990: # per year category (starting from 1990)
                return str(YYYY)
            else:
                return str(YYYY)[:3]+'0' # per decennium category (between 1900 and the seventies)
        return

    # returns the prices/grants category, used for drilldown: veni, vidi, vici, etc.
    def _getPriceNameForDrilldown(self, price_string):
        if price_string and price_string.strip():
            m = priceRegex.match(price_string.strip())
            if m:
                return m.group(1).lower().strip()
        #for pricename in ['veni','vidi','vici','spinoza']:
        #    if price_string and price_string.strip() and price_string.lower().find(pricename) >= 0: return pricename
        return

    # returns the category code for drilldown use. 
    def _getCodeFromCategory(self, element):        
        if type(element) == _Element:
            func = element.xpath('attribute::code')
            if(func):
                return func[0][:6].upper()

    # returns the composed werkzaamheid, used for drilldown: ie. 'U.WUR:HGL', if it matches our businessrules, 'None' otherwise.
    def _getWerkzaamheidForDrilldownFromJobs(self, element):
        if type(element) == _Element:
            func = element.xpath('self::prs:job/prs:functie_nl/@acronym', namespaces=namespacesmap)
            if(func and func[0].upper() in ['BHL', 'GHL', 'HGL', 'OHL', 'PTH', 'UHD', 'UHL', 'ADL', 'HHL', 'LCT']): #, 'LCT'  #Continue, we are interested in this 'werkzaamheid'.
                if func[0].upper() == 'LCT': return None, func[0] # Lectoren will be added to dd_position only (NOT dd_institute)
                inst = element.xpath('self::prs:job/prs:organisatie/@code', namespaces=namespacesmap)
                if inst:
                    lijst = inst[0].split('.',3)
                    if(len(lijst)>=3 and lijst[0]=='U' and lijst[1].isupper()): return lijst[0]+'_'+lijst[1], func[0] # university. i.e: U_UVA (mind the underscore, not a dot!)
                    elif (lijst[0]=='A' or lijst[0]=='W' or lijst[0]=='T') : return lijst[0], func[0] # KNAW, NWO, TNO, Minus Hogescholen => or lijst[0]=='V' or lijst[0]=='N'
        return None, None


    def _getInstForDD(self, code):
        if code:
            lijst = code.split('.',3)
            if(len(lijst)>=3 and lijst[0]=='U' and lijst[1].isupper()): return lijst[0]+'_'+lijst[1] # university. i.e: U_UVA (mind the underscore, not a dot!)
            elif (lijst[0]=='A' or lijst[0]=='W' or lijst[0]=='T' ) : return lijst[0] # KNAW, NWO or TNO.


    def _getInstForFin_DD(self, code): # Retourneer de instituut_code zonder punten, maar met underscore.
        if code:
            return code.strip().replace('.', '_') # Mind the underscore, not a dot!

            
    def _getOSchoolForDD(self, code):
        if code:
            lijst = code.split('.',3)
            if(len(lijst)>=3 and lijst[0]=='U' and lijst[1].isupper() and lijst[2]=='OS'): return lijst[0]+'_'+lijst[1] # university. i.e: U_UVA (mind the underscore, not a dot!)



    def _addAuthorsAndNamesFields(self, lxmlNode, wcpcollection):

        authors = [] # i.e.: Messineo, Maria;Bennis, prof.dr. H.J.
        names = [] # i.e.: Maastricht Universiteit;Messineo, Maria;Bal, M.P.;Bennis, prof.dr. H.J.
        ds_creators = [] # Beta: List of dataset creators, which will be sent to the index for drilldown(!)

        if wcpcollection in WCPEDUCOLLECTION:
            # LONG ONLY:
            pubnames = lxmlNode.xpath('//long:metadata/long:name', namespaces=namespacesmap)
            for name in pubnames:
                # Get sub-elements: Either family and/or unstructed is available...
                roleterm = name.xpath('self::long:name/long:mcRoleTerm/text()', namespaces=namespacesmap)
                unstructured = name.xpath('self::long:name/long:unstructured/text()', namespaces=namespacesmap)
                family = name.xpath('self::long:name/long:family/text()', namespaces=namespacesmap)
                given = name.xpath('self::long:name/long:given/text()', namespaces=namespacesmap)
                nids = name.xpath('self::long:name/long:nameIdentifier', namespaces=namespacesmap)
                patroniem = name.xpath('self::long:name/long:termsOfAddress/text()', namespaces=namespacesmap)
                tiepe = name.xpath('self::long:name/long:type/text()', namespaces=namespacesmap)
                strdai='' # temp DAI container
                fg_naam = [] # fg = Family + Given name...
                
                if family: fg_naam.append(family[0])
                if given: fg_naam.append(given[0])
                if patroniem: fg_naam.append(patroniem[0])

                if unstructured: #use unstructured value as NAMES field
                    names.append(unstructured[0])
                else:
                    names.append(', '.join(fg_naam))

                # Compose qualified author string and index author/non-author dais:
                nidFieldname = 'nids_non_aut'
                if roleterm and tiepe:
                    if roleterm[0] in marcrelatorAuthorRoles and tiepe[0] == 'personal':
                        if (family or given): #authors need to be F+Given, NOT unstructured; this may contain 'noise' (other stuff, not related to the person name.
                            authors.append(', '.join(fg_naam))
                        else:
                            authors.append(unstructured[0])
                        nidFieldname = 'nids_aut'

                        #BETA functionality: Add dataset creators for dataset creators drilldown:  collection == 'dataset' and
                        if wcpcollection == 'dataset':
                            if roleterm[0].lower() == 'cre' and (family or given): #We're NOT interested in unstractured/displayForm labels here...
                                ds_creators.append(', '.join(fg_naam))
                if len(nids) > 0:
                    # print "Aantal name nameIdentifiers (pub):", len(nids)
                    for nid in nids:
                        nameId = NameIdentifierFactory.factory(nid.attrib['type'], nid.text)
                        if nameId.is_valid():
                            #  Add 'known' ID format to dais/nameID field:
                            self._fieldslist.append(( nidFieldname, nameId.get_id() ))
                            self._fieldslist.append(( 'nids', nameId.get_id() ))
                            if not self._verbose: print 'addField:', nidFieldname.upper(), "-->", nameId.get_id()
                            if not self._verbose: print 'addField: NIDS', "-->", nameId.get_id()
                            #  Add all ID formats to general field:
                            for variant in nameId.getTypedVariants():
                                self._fieldslist.append(( UNQUALIFIED_TERMS, variant ))
                                if not self._verbose: print 'addField:', UNQUALIFIED_TERMS, "-->", variant

        # NOD_PRS:
        elif wcpcollection == 'person':
            prs_name = lxmlNode.xpath('//prs:persoon/prs:fullName/text()', namespaces=namespacesmap)
            if prs_name:
                names.append(prs_name[0])
                #All orgs from <jobs>: Need to be unique?
                prs_orgs = lxmlNode.xpath('//prs:organisatie/text()', namespaces=namespacesmap)
                if prs_orgs:
                    orgs_set = set([])
                    for org in prs_orgs:
                        orgs_set.add(org)
                    for org in orgs_set:
                        names.append(org)
 
            nids = lxmlNode.xpath('//prs:persoon/prs:nameIdentifier', namespaces=namespacesmap)
            if len(nids) > 0:
                # print "Aantal nod Persoon nameIdentifiers:", len(nids)
                for nid in nids:
                    nameId = NameIdentifierFactory.factory(nid.attrib['type'], nid.text)
                    if nameId.is_valid():
                        #  Add 'known' ID format to dais/nameID field:
                        self._fieldslist.append(( 'nids', nameId.get_id() ))
                        if self._verbose: print 'addField: NIDS', "-->", nameId.get_id()
                        #  Add all ID formats to general field:
                        for variant in nameId.getTypedVariants():
                            self._fieldslist.append(( UNQUALIFIED_TERMS, variant ))
                            if self._verbose: print 'addField:', UNQUALIFIED_TERMS, "-->", variant


        elif wcpcollection == 'organisation':
            # NOD_ORG: (naam_en + naam_nl)
            org_names = lxmlNode.xpath('//org:organisatie/org:*[local-name()="naam_nl" or local-name()="naam_en"]/text()', namespaces=namespacesmap)
            for org_name in org_names:
                names.append(org_name)


        elif wcpcollection == 'project':
            # NOD_ACT: (fullnames + dais)
            act_persons = lxmlNode.xpath('//prj:activiteit/prj:person', namespaces=namespacesmap)
            for act_person in act_persons:
                act_name = act_person.xpath('self::prj:person/prj:fullName/text()', namespaces=namespacesmap)
                names.append(act_name[0])

            nids = lxmlNode.xpath('//prj:person/prj:nameIdentifier', namespaces=namespacesmap)
            if len(nids) > 0:
                # print "Aantal nod Project nameIdentifiers:", len(nids)
                for nid in nids:
                    nameId = NameIdentifierFactory.factory(nid.attrib['type'], nid.text)
                    if nameId.is_valid():
                        #  Add 'known' ID format to dais/nameID field:
                        self._fieldslist.append(( 'nids', nameId.get_id() ))
                        if self._verbose: print 'addField: NIDS', "-->", nameId.get_id()
                        #  Add all ID formats to general field:
                        for variant in nameId.getTypedVariants():
                            self._fieldslist.append(( UNQUALIFIED_TERMS, variant ))
                            if self._verbose: print 'addField:', UNQUALIFIED_TERMS, "-->", variant

        # Add fields to the fieldslist:
        for author in authors:
            if self._verbose: print 'addField:', 'authors'.upper(), "-->", author.replace('\n', '')[:MAX_CHAR]
            self._fieldslist.append(('authors', author.replace('\n', '')))
        for name in names:
            if self._verbose: print 'addField:', 'names'.upper(), "-->", name.replace('\n', '')[:MAX_CHAR]
            self._fieldslist.append(('names', name.replace('\n', '')))

# Incoming:
# <document xmlns="http://meresco.org/namespace/harvester/document">
#     <part name="record">
#         &lt;record xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"&gt;
#             &lt;header xmlns="http://www.openarchives.org/OAI/2.0/"&gt;
#                 &lt;identifier&gt;record:1&lt;/identifier&gt;&lt;datestamp&gt;2008-12-15T14:08:34Z&lt;/datestamp&gt;
#             &lt;/header&gt;
#             &lt;metadata xmlns="http://www.openarchives.org/OAI/2.0/"&gt;
#                 &lt;ns0:md_original xmlns:ns0="http://dans.knaw.nl/narcis/normalized"&gt;
#                     &lt;oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/      http://www.openarchives.org/OAI/2.0/oai_dc.xsd"&gt;
#                         &lt;dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/"&gt;http://meresco.com?record=1&lt;/dc:identifier&gt;
#                     &lt;/oai_dc:dc&gt;
#                 &lt;/ns0:md_original&gt;
#                 &lt;ns0:normalized xmlns:ns0="http://dans.knaw.nl/narcis/normalized"&gt;
#                     &lt;long xmlns="http://www.knaw.nl/narcis/1.0/long/" version="1.0"&gt;&lt;modificationDate&gt;2008-12-15T14:08:34Z&lt;/modificationDate&gt;&lt;humanStartPage&gt;http://meresco.com?record=1&lt;/humanStartPage&gt;&lt;accessRights&gt;restrictedAccess&lt;/accessRights&gt;&lt;metadata&gt;&lt;titleInfo&gt;&lt;title&gt;Example Program 1&lt;/title&gt;&lt;/titleInfo&gt;&lt;titleInfo xml:lang="en"&gt;&lt;title&gt;Example Program 1&lt;/title&gt;&lt;/titleInfo&gt;&lt;name&gt;&lt;type&gt;personal&lt;/type&gt;&lt;unstructured&gt;Seecr&lt;/unstructured&gt;&lt;mcRoleTerm&gt;aut&lt;/mcRoleTerm&gt;&lt;/name&gt;&lt;publisher&gt;Seecr&lt;/publisher&gt;&lt;subject&gt;&lt;topic&gt;Search&lt;/topic&gt;&lt;/subject&gt;&lt;abstract&gt;This is an example program about Search with Meresco&lt;/abstract&gt;&lt;dateIssued&gt;&lt;parsed&gt;2016&lt;/parsed&gt;&lt;unParsed&gt;2016&lt;/unParsed&gt;&lt;/dateIssued&gt;&lt;language&gt;en&lt;/language&gt;&lt;/metadata&gt;
#                     &lt;/long&gt;
#                 &lt;/ns0:normalized&gt;
#             &lt;/metadata&gt;
#         &lt;/record&gt;</part>
#     <part name="meta">
#         &lt;meta xmlns="http://meresco.org/namespace/harvester/meta"&gt;
#             &lt;upload&gt;
#             &lt;id&gt;meresco:record:1&lt;/id&gt;
#             &lt;/repository&gt;
#         &lt;/meta&gt;
#     </part>
# </document>


# lxml recordpart:
# <record xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
#     <header xmlns="http://www.openarchives.org/OAI/2.0/">
#         <identifier>record:1</identifier>
#         <datestamp>2008-12-15T14:08:34Z</datestamp>
#     </header>
#     <metadata xmlns="http://www.openarchives.org/OAI/2.0/">
#         <ns0:md_original xmlns:ns0="http://dans.knaw.nl/narcis/normalized">
#             <oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
#                 xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/      http://www.openarchives.org/OAI/2.0/oai_dc.xsd">
#                 <dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/"
#                     >http://meresco.com?record=1</dc:identifier>
#                 <dc:description xmlns:dc="http://purl.org/dc/elements/1.1/">This is an example
#                     program about Search with Meresco</dc:description>
#                 <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">Example Program 1</dc:title>
#                 <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">Seecr</dc:creator>
#                 <dc:publisher xmlns:dc="http://purl.org/dc/elements/1.1/">Seecr</dc:publisher>
#                 <dc:date xmlns:dc="http://purl.org/dc/elements/1.1/">tweeduizendzestien</dc:date>
#                 <dc:date xmlns:dc="http://purl.org/dc/elements/1.1/">2016</dc:date>
#                 <dc:type xmlns:dc="http://purl.org/dc/elements/1.1/">Example &amp; 1</dc:type>
#                 <dc:subject xmlns:dc="http://purl.org/dc/elements/1.1/">Search</dc:subject>
#                 <dc:language xmlns:dc="http://purl.org/dc/elements/1.1/">en</dc:language>
#                 <dc:rights xmlns:dc="http://purl.org/dc/elements/1.1/">restrictedAccess</dc:rights>
#             </oai_dc:dc>
#         </ns0:md_original>
#         <ns0:normalized xmlns:ns0="http://dans.knaw.nl/narcis/normalized">
#             <long xmlns="http://www.knaw.nl/narcis/1.0/long/" version="1.0">
#                 <modificationDate>2008-12-15T14:08:34Z</modificationDate>
#                 <humanStartPage>http://meresco.com?record=1</humanStartPage>
#                 <accessRights>restrictedAccess</accessRights>
#                 <metadata>
#                     <titleInfo>
#                         <title>Example Program 1</title>
#                     </titleInfo>
#                     <titleInfo xml:lang="en">
#                         <title>Example Program 1</title>
#                     </titleInfo>
#                     <name>
#                         <type>personal</type>
#                         <unstructured>Seecr</unstructured>
#                         <mcRoleTerm>aut</mcRoleTerm>
#                     </name>
#                     <publisher>Seecr</publisher>
#                     <subject>
#                         <topic>Search</topic>
#                     </subject>
#                     <abstract>This is an example program about Search with Meresco</abstract>
#                     <dateIssued>
#                         <parsed>2016</parsed>
#                         <unParsed>2016</unParsed>
#                     </dateIssued>
#                     <language>en</language>
#                 </metadata>
#             </long>
#         </ns0:normalized>
#     </metadata>
# </record>


# e_metapart:
# <meta xmlns="http://meresco.org/namespace/harvester/meta">
#     <upload>
#         <id>knaw:record:4</id>
#     </upload>
#     <record>
#         <id>record:4</id>
#         <harvestdate>2016-10-05T10:30:45Z</harvestdate>
#         <metadataNamespace>http://www.loc.gov/mods/v3</metadataNamespace>
#     </record>
#     <repository>
#         <id>knaw</id>
#         <set>oa_publications</set>
#         <baseurl>http://depot.knaw.nl/cgi/oai2</baseurl>
#         <repositoryGroupId>knaw</repositoryGroupId>
#         <metadataPrefix>nl_didl</metadataPrefix>
#         <collection>publication</collection>
#     </repository>
# </meta>