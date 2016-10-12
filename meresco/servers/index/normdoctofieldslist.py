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
from lxml.etree import parse, _ElementTree, tostring
from StringIO import StringIO
from meresco.xml import namespaces


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


fieldNamesXpathMap = {
    'subject'        : "//*[local-name()='topic' or local-name()='expertise_nl' or local-name()='expertise_en']/text()", # Expertise from personrecord or topics from knawLong:
    # 'leeropdracht'   : "//*[local-name()='leeropdracht_en' or local-name()='leeropdracht_nl']/text()", # Leeropdracht from personrecord
    # 'dais'           : "//long:dai/text()", # All dai's: also from relatedItems
    'abstract'       : "//long:metadata/long:abstract[not (@xml:lang)]/text()", # 'abstract' field from KNAWLONG.
    'abstract_en'    : "//long:metadata/long:abstract[@xml:lang='en']/text()", # 'abstract_en' field from KNAWLONG.
    'title'          : "//long:metadata/long:titleInfo[not (@xml:lang)]/long:*/text()", #'title'+'subtitle' field from KNAWLONG.
    'title_en'       : "//long:metadata/long:titleInfo[@xml:lang='en']/long:*/text()", #'title_en'+'subtitle field from KNAWLONG.
    'dd_year'        : "//long:metadata/long:dateIssued/long:parsed/text()", # Parsed (normalized) datefield from KNAWLONG.
    'coverage'       : "//long:metadata/long:coverage/text()", # 'coverage' field from KNAWLONG.
    'format'         : "//long:metadata/long:format/text()", # 'format' field from KNAWLONG.
    # 'dd_prices'      : "//prs:persoon/prs:prices/prs:price/text()",
    # 'dd_werkzaamheid': "//prs:persoon/prs:jobs/prs:job",
    # 'titulatuur'     : "//prs:persoon/prs:titulatuur/text()",
    # 'dd_cat'         : "//*[local-name()='category' and (@code)]", # Alle category elementen met attribuut 'code=', zonder namespace...(staan in zowel PRS als ORG...)
    # 'dd_thesis'      : "//ond:dissertatie[contains(.='true')]", # Alle promotie onderzoeken... xpath retourneerd een boolean...
    # 'dd_institute'   : "//org:organisatie/@code",
    # 'dd_os'          : "//org:organisatie/@code", # Onderzoekschool
    # 'dd_penv'        : "//ond:activiteit/ond:penvoerder/@instituut_code", # HarremaCode van penvoerend instituut.
    # 'dd_fin'         : "//ond:activiteit/ond:financier/@instituut_code", # HarremaCode van financierend instituut.
    'publication_identifier': "//long:publication_identifier/text()", # MODS:identifier from mods root as well as relatedItem (mostly: isbn, issn, doi etc.)
    }


class NormdocToFieldsList(Observable):

    def __init__(self, verbose=True, truncate_chars=300):
        Observable.__init__(self)
        self._verbose = verbose
        self._truncate_chars = truncate_chars

    def add(self, lxmlNode, **kwargs):
        # hier komt een compleet meresco:document binnen als LXMLnode:
        identifier = kwargs['identifier']

        # print "LXML:" , identifier, tostring(lxmlNode)
        # Get meta, header and metadata part(='long') from the normdoc:
        #  meta
        metapart = lxmlNode.xpath('/document:document/document:part[@name="meta"]/text()', namespaces=namespacesmap)
        e_metapart = etree.fromstring(metapart[0])
        # print "lxml metapart:", tostring(e_metapart)


        recordpart = lxmlNode.xpath('/document:document/document:part[@name="record"]/text()', namespaces=namespacesmap)
        e_recordpart = etree.fromstring(recordpart[0])
        # print "lxml recordpart:", tostring(e_recordpart)

        nodrecord = e_recordpart.xpath('//prs:persoon | //proj:activiteit | //org:organisatie', namespaces=namespacesmap)
        if len(nodrecord) > 0:
            print "lxml NOD-record:", tostring(e_recordpart)


        fieldslist = []

        # Add repository info from meta part to fieldslist:
        for child in e_metapart.getchildren():
            if child.tag == curieToTag('meta:repository'):
                for repokind in child.iterchildren():
                    # fieldname = tagToCurie(repokind.tag)
                    fieldslist.append((tagToCurie(repokind.tag), repokind.text))

        # Add OAI identifier:
        fieldslist.append(('oai_identifier', e_recordpart.xpath('/oai:record/oai:header/oai:identifier/text()', namespaces=namespacesmap)[0]))


        for field, xpath in fieldNamesXpathMap.iteritems():
            self._findAndAddFieldToList(fieldslist, e_recordpart, field, xpath)


        # Ready filling, now call add method:
        yield self.all.add(fieldslist=fieldslist, **kwargs)


    def _findAndAddFieldToList(self, fieldslist, lxmlNode, fieldName, xpath):
        # Adds fieldnames and values to the fieldslist list.
        results = lxmlNode.xpath(xpath, namespaces=namespacesmap)
        if not results:
            return

        # if fieldName == 'dais':
        #     # Unfortunately tokenizing DAIs goes wrong: 'nl/071791013' will be added to the index instead of '071791013', so searching on postfix ('071791013') is not possible.
        #     # Problem seems to be some 'intelligent' escaping (StandardTokenizer), since a dai like 'info:eu-repo/dai/nl/lettershereinsteadofnumbers' is tokenized correctly / allows for searching on postfix ('lettershereinsteadofnumbers')??
        #     # Escaping '/' with '\' doesn't do the job: one cannot search for a 'complete' DAI anymore, but postfix search OK...
        #     # So we add the postfix separately: addField:'info:eu-repo/dai/nl/15081968' and addField:'15081968', so we can find them either way.
        #     for dai in results:
        #         nameId = Dai(dai.replace('\n', ''))
        #         if nameId.is_valid():
        #             if self._verbose: print 'addField:', fieldName.upper(), "-->", nameId.get_id()
        #             self.do.addField(name=fieldName, value=nameId.get_id())
        #             for variant in nameId.getTypedVariants():
        #                 self.do.addField( name=UNQUALIFIED_TERMS, value=variant )
        #                 if self._verbose: print 'addField:', UNQUALIFIED_TERMS, "-->", variant
        # elif fieldName == 'dd_year':
        #     if self._verbose: print 'addField:', fieldName.upper(), results[0].strip().replace('\n', ''), "--->", self._getYearGroupForDrilldown( results[0].strip().replace('\n', '') )
        #     self.do.addField(name=fieldName, value=self._getYearGroupForDrilldown( results[0].strip().replace('\n', '') ))
        # elif fieldName == 'dd_prices':
        #     for price in results:
        #         if self._verbose: print 'addField:', fieldName.upper(), price.strip().replace('\n', ''), "--->", self._getPriceNameForDrilldown( price.strip().replace('\n', '') )
        #         self.do.addField(name=fieldName, value=self._getPriceNameForDrilldown( price.strip().replace('\n', '') ))
        # elif fieldName == 'dd_cat':
        #     for category in results:
        #         #if self._verbose: print 'addField:', fieldName.upper(), self._getCodeFromCategory( category )
        #         #self.do.addField(name=fieldName, self._getCodeFromCategory( category ))
        #         class6 = self._getCodeFromCategory( category )
        #         #Upload the catagory itself:
        #         if self._verbose: print 'addField:', fieldName.upper(), "-->", class6
        #         self.do.addField(name=fieldName, value=class6)
        #         #Upload the parent catagories:
        #         for index, char in enumerate(class6[::-1]):
        #             if char!='0' and index < 4:
        #                 if self._verbose: print 'addField:', fieldName.upper(), "-->", class6[:5-index].ljust(6, '0')
        #                 self.do.addField(name=fieldName, value=class6[:5-index].ljust(6, '0'))
        # elif fieldName == 'titulatuur': #'Prof.dr.ing.' persons should be found searching 'prof' only!?
        #     subtitles = results[0].split('.')
        #     if self._verbose: print 'addField:', fieldName.upper(), "-->", results[0]
        #     self.do.addField(name=fieldName, value=results[0])
        #     for title in subtitles:
        #         if self._verbose and not title=='': print 'addField:', "-->", fieldName.upper(), title
        #         if not title=='': self.do.addField(name=fieldName, value=title)
        # elif fieldName == 'dd_werkzaamheid':
        #     for werkzaamheid in results:
        #         inst, func = self._getWerkzaamheidForDrilldownFromJobs(werkzaamheid)
        #         if (inst and func):
        #             if self._verbose: print 'addField:', "dd_institute".upper(), "-->", inst
        #             if self._verbose: print 'addField:', "dd_position".upper(), "-->", func
        #             if self._verbose: print 'addField:', fieldName.upper(), "-->", inst+':'+func
        #             self.do.addField(name="dd_institute", value=inst)
        #             self.do.addField(name="dd_position", value=func)
        #             self.do.addField(name=fieldName, value=inst+':'+func)
        #         elif (func): # Only function was given: 'LCT' only!
        #             if self._verbose: print 'addField:', "dd_position".upper(), "-->", func
        #             self.do.addField(name="dd_position", value=func)
        # elif fieldName == 'dd_thesis': #results is a boolean (returned by Xpath)...
        #     if self._verbose: print 'addField:', fieldName.upper(), "-->", str(results).lower()
        #     self.do.addField(name=fieldName, value=str(results).lower())
        # elif fieldName == 'publication_identifier': #results are all <publication_identifier> tags from mods root, as well as mods/related_item.
        #     for pid in results:
        #         if self._verbose: print 'addField:', fieldName.upper(), "-->", pid
        #         self.do.addField(name=fieldName, value=pid)
        # elif fieldName == 'dd_institute': #Harrema code from an organisation. =Bovenliggend instituut: exactly 1
        #     dd_inst = self._getInstForDD(results[0])
        #     if (dd_inst):
        #         if self._verbose: print 'addField:', fieldName.upper(), "-->", dd_inst
        #         self.do.addField(name=fieldName, value=dd_inst)
        # elif fieldName == 'dd_penv': #Harrema code from an organisation. (Penvoerder): zero or more.
        #     for instituut_code in results:
        #         dd_inst = self._getInstForDD(instituut_code)
        #         if (dd_inst):
        #             if self._verbose: print 'addField:', fieldName.upper(), "-->", dd_inst
        #             self.do.addField(name=fieldName, value=dd_inst)
        # elif fieldName == 'dd_fin': #Harrema code from an organisation. (Financier): zero or more.
        #     for instituut_code in results:
        #         dd_inst = self._getInstForFin_DD(instituut_code)
        #         if (dd_inst):
        #             if self._verbose: print 'addField:', fieldName.upper(), "-->", dd_inst
        #             self.do.addField(name=fieldName, value=dd_inst)
        # elif fieldName == 'dd_os': #Onderzoekschool:
        #     dd_inst = self._getOSchoolForDD(results[0])
        #     if (dd_inst):
        #         if self._verbose: print 'addField:', fieldName.upper(), "-->", dd_inst
        #         self.do.addField(name=fieldName, value=dd_inst)
        elif fieldName in ('coverage', 'format'):
            for result in results:
                if self._verbose: print 'addField:', fieldName.upper(), "-->", result
                fieldslist.append((fieldName, result))               
        else:     # All other remaining results are joined with a space:
            fieldslist.append((fieldName, ' '.join(results).replace('\n', ''))) 
            if self._verbose: print 'addField:', fieldName.upper(), "-->", ' '.join(results).replace('\n', '')[:self._truncate_chars]


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
#         <harvestDate>2016-10-05T10:30:45Z</harvestDate>
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