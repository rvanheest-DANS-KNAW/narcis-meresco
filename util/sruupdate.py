#!/usr/bin/env python
## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#
#    This file is part of Meresco Core.
#
#    Meresco Core is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Meresco Core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Meresco Core; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

import httplib
import sys

# SRU_UPDATE_REQUEST = """<?xml version="1.0" encoding="UTF-8"?>
# <updateRequest xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:ucp="http://www.loc.gov/KVS_IHAVENOIDEA/">
#     <srw:version>1.0</srw:version>
#     <ucp:action>info:srw/action/1/%(action)s</ucp:action>
#     <ucp:recordIdentifier>%(recordIdentifier)s</ucp:recordIdentifier>
# </updateRequest>"""


# SRU_UPDATE_REQUEST = """<ucp:updateRequest xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:ucp="info:lc/xmlns/update-v1">
#     <srw:version>1.0</srw:version>
#     <ucp:action>info:srw/action/1/%(action)s</ucp:action>
#     <ucp:recordIdentifier>%(recordIdentifier)s</ucp:recordIdentifier>
# </ucp:updateRequest>"""



SRU_UPDATE_REQUEST = """<ucp:updateRequest xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:ucp="info:lc/xmlns/update-v1">
    <srw:version>1.0</srw:version>
    <ucp:action>info:srw/action/1/replace</ucp:action>
    <ucp:recordIdentifier>mpi:oai:www.mpi.nl:1839_2C806818-9B67-45DF-973A-44D30124E5E5</ucp:recordIdentifier>
    <srw:record>
        <srw:recordPacking>xml</srw:recordPacking>
        <srw:recordSchema>metadata</srw:recordSchema>
        <srw:recordData><document xmlns="http://meresco.org/namespace/harvester/document"><part name="record">&lt;record xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"&gt;
            &lt;header xmlns="http://www.openarchives.org/OAI/2.0/"&gt;&lt;identifier&gt;oai:www.mpi.nl:1839_2C806818-9B67-45DF-973A-44D30124E5E5&lt;/identifier&gt;&lt;datestamp&gt;2008-12-15T14:08:34Z&lt;/datestamp&gt;&lt;/header&gt;
            &lt;metadata xmlns="http://www.openarchives.org/OAI/2.0/"&gt;
            &lt;oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/      http://www.openarchives.org/OAI/2.0/oai_dc.xsd"&gt;
            &lt;dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/"&gt;http://meresco.com?record=1&lt;/dc:identifier&gt;
            &lt;dc:description xmlns:dc="http://purl.org/dc/elements/1.1/"&gt;This is an example program about Search with Meresco&lt;/dc:description&gt;
            &lt;dc:title xmlns:dc="http://purl.org/dc/elements/1.1/"&gt;Example Program 1&lt;/dc:title&gt;
            &lt;dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/"&gt;Seecr&lt;/dc:creator&gt;
            &lt;dc:publisher xmlns:dc="http://purl.org/dc/elements/1.1/"&gt;Seecr&lt;/dc:publisher&gt;
            &lt;dc:date xmlns:dc="http://purl.org/dc/elements/1.1/"&gt;tweeduizendzestien&lt;/dc:date&gt;
            &lt;dc:date xmlns:dc="http://purl.org/dc/elements/1.1/"&gt;2016-5-5&lt;/dc:date&gt;
            &lt;dc:type xmlns:dc="http://purl.org/dc/elements/1.1/"&gt;Example &amp;amp; 1&lt;/dc:type&gt;
            &lt;dc:subject xmlns:dc="http://purl.org/dc/elements/1.1/"&gt;Search&lt;/dc:subject&gt;
            &lt;dc:language xmlns:dc="http://purl.org/dc/elements/1.1/"&gt;en&lt;/dc:language&gt;
            &lt;dc:rights xmlns:dc="http://purl.org/dc/elements/1.1/"&gt;restrictedAccess&lt;/dc:rights&gt;
            &lt;/oai_dc:dc&gt;&lt;/metadata&gt;
            &lt;/record&gt;</part>
            <part name="meta">&lt;meta xmlns=&quot;http://meresco.org/namespace/harvester/meta&quot;&gt;
                &lt;upload&gt;
                &lt;id&gt;mpi:oai:www.mpi.nl:1839_2C806818-9B67-45DF-973A-44D30124E5E5&lt;/id&gt;
                &lt;/upload&gt;
                &lt;record&gt;
                &lt;id&gt;oai:www.mpi.nl:1839_2C806818-9B67-45DF-973A-44D30124E5E5&lt;/id&gt;
                &lt;harvestdate&gt;2018-04-04T13:46:09Z&lt;/harvestdate&gt;               
                &lt;/record&gt;
                &lt;repository&gt;
                &lt;id&gt;mpi&lt;/id&gt;
                &lt;baseurl&gt;http://corpus1.mpi.nl/ds/oaiprovider/oai3&lt;/baseurl&gt;
                &lt;repositoryGroupId&gt;mpi&lt;/repositoryGroupId&gt;
                &lt;metadataPrefix&gt;oai_dc&lt;/metadataPrefix&gt;
                &lt;collection&gt;dataset&lt;/collection&gt;
                &lt;/repository&gt;
                &lt;/meta&gt;</part>
        </document>
        </srw:recordData>
    </srw:record>
</ucp:updateRequest>"""




def send(data, baseurl, port, path):
    connection = httplib.HTTPConnection(baseurl, port)
    connection.putrequest("POST", path)
    connection.putheader("Host", baseurl)
    connection.putheader("Content-Type", "text/xml; charset=\"utf-8\"")
    connection.putheader("Content-Length", str(len(data)))
    connection.endheaders()
    connection.send(data)
    
    response = connection.getresponse()
    print "STATUS:", response.status
    print "HEADERS:", response.getheaders()
    print "MESSAGE:", response.read()

if __name__ == "__main__":
    nrs = input("range of records (python code: ['uploadId#1', 'eur:oai:ep.eur.nl:1765/22562'])> ")
    for i in nrs:
        send(SRU_UPDATE_REQUEST, 'localhost', 8000, '/update')
