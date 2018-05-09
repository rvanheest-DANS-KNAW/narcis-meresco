import os, shutil, glob
import xml.etree.ElementTree
import urllib
import datetime
import httplib
import sys
import time


# 2018-04-04:
# MPI repo vertoonde 31.000 spookrecords, die niet met een simpele 'SRU delete' te verwijderen waren; zowel niet uit de index als uit de api-sorage.
# Wel werden de records op de gateway-storage verwijderd.
# Gelijktijdig had MPI de base-url (en identifiers) aangepast, hierdoor was het onmogelijk om de 'oude' records te reharvesten en daarna te deleten.
# Situatie: Na een clear en/of refresh nog 31.000 spook-records, die niet gereharvest en gecleared konden worden, tevens was sturen van een SRU-delete niet functioneel (? waarom niet is nog onduidelijk).
# 
# Vandaar dit script:
# 1: Haalt de uploadids van de spookrecords uit storage.
# 2: Stuurt een (dummy) update voor het record naar de gateway.
# 3: Stuurt een delete voor het record naar de gateway.
# Dit werkt wel.

# http://anarcis01.dans.knaw.nl:9080/sru?operation=searchRetrieve&version=1.1&maximumRecords=1&recordSchema=knaw_short&query=(untokenized.meta_repositoryid%20exact%20rce-kb)




SRU_DELETE_REQUEST = """<ucp:updateRequest xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:ucp="info:lc/xmlns/update-v1">
    <srw:version>1.0</srw:version>
    <ucp:action>info:srw/action/1/delete</ucp:action>
    <ucp:recordIdentifier>%(upload_id)s</ucp:recordIdentifier>
</ucp:updateRequest>"""



SRU_UPDATE_REQUEST = """<ucp:updateRequest xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:ucp="info:lc/xmlns/update-v1">
    <srw:version>1.0</srw:version>
    <ucp:action>info:srw/action/1/replace</ucp:action>
    <ucp:recordIdentifier>%(upload_id)s</ucp:recordIdentifier>
    <srw:record>
        <srw:recordPacking>xml</srw:recordPacking>
        <srw:recordSchema>metadata</srw:recordSchema>
        <srw:recordData><document xmlns="http://meresco.org/namespace/harvester/document"><part name="record">&lt;record xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"&gt;
            &lt;header xmlns="http://www.openarchives.org/OAI/2.0/"&gt;&lt;identifier&gt;%(oai_id)s&lt;/identifier&gt;&lt;datestamp&gt;2018-12-15T14:08:34Z&lt;/datestamp&gt;&lt;/header&gt;
            &lt;metadata xmlns="http://www.openarchives.org/OAI/2.0/"&gt;
            &lt;oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/  http://www.openarchives.org/OAI/2.0/oai_dc.xsd"&gt;
            &lt;dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/"&gt;GhostId&lt;/dc:identifier&gt;
            &lt;dc:description xmlns:dc="http://purl.org/dc/elements/1.1/"&gt;This is a bogus/ghost record.&lt;/dc:description&gt;
            &lt;dc:title xmlns:dc="http://purl.org/dc/elements/1.1/"&gt;To be deleted&lt;/dc:title&gt;
            &lt;/oai_dc:dc&gt;&lt;/metadata&gt;
            &lt;/record&gt;</part>
            <part name="meta">&lt;meta xmlns=&quot;http://meresco.org/namespace/harvester/meta&quot;&gt;
                &lt;upload&gt;
                &lt;id&gt;%(upload_id)s&lt;/id&gt;
                &lt;/upload&gt;
                &lt;record&gt;
                &lt;id&gt;%(oai_id)s&lt;/id&gt;
                &lt;harvestdate&gt;2018-12-04T13:46:09Z&lt;/harvestdate&gt;               
                &lt;/record&gt;
                &lt;repository&gt;
                &lt;id&gt;%(repoid)s&lt;/id&gt;
                &lt;baseurl&gt;http://corpus1.mpi.nl/ds/oaiprovider/oai3&lt;/baseurl&gt;
                &lt;repositoryGroupId&gt;%(repogid)s&lt;/repositoryGroupId&gt;
                &lt;metadataPrefix&gt;oai_dc&lt;/metadataPrefix&gt;
                &lt;collection&gt;dataset&lt;/collection&gt;
                &lt;/repository&gt;
                &lt;/meta&gt;</part>
        </document>
        </srw:recordData>
    </srw:record>
</ucp:updateRequest>"""



REPOID = 'rce-kb'
REPOGROUPID = 'rce'
STORAGE_DIR = '/data/meresco/api/store/'+REPOID



def send(data, baseurl, port, path):
    connection = httplib.HTTPConnection(baseurl, port)
    connection.putrequest("POST", path)
    connection.putheader("Host", baseurl)
    connection.putheader("Content-Type", "text/xml; charset=\"utf-8\"")
    connection.putheader("Content-Length", str(len(data)))
    connection.endheaders()
    connection.send(data)
    
    response = connection.getresponse()
    if response.status != 200:
        print "STATUS:", response.status
    # print "HEADERS:", response.getheaders()
    # print "MESSAGE:", response.read()

# Global record counter:
cnt = 0

# Loop over meresco storage:
for subdir, dirs, files in os.walk(STORAGE_DIR):

    if "knaw_short" in files:  # Found existing (non-deleted) record dir.

        # File-list is alfabetisch gesort: header, knaw_short, meta. Wij willen meta first, dus we reversen de file map.
        #for bestand in reversed(files):
        for bestand in reversed(files):
            if bestand == 'meta':
                meta = xml.etree.ElementTree.parse(os.path.join(subdir, bestand)).getroot()
                oai_id = meta.find(
                    '{http://meresco.org/namespace/harvester/meta}record/{http://meresco.org/namespace/harvester/meta}id')
                upload_id = meta.find(
                    '{http://meresco.org/namespace/harvester/meta}upload/{http://meresco.org/namespace/harvester/meta}id')
                harvestdate = meta.find(
                    '{http://meresco.org/namespace/harvester/meta}record/{http://meresco.org/namespace/harvester/meta}harvestdate')
                collection = meta.find(
                    '{http://meresco.org/namespace/harvester/meta}repository/{http://meresco.org/namespace/harvester/meta}collection')
                if oai_id is None or upload_id is None:
                    break  # skip this dir and rest of the files in it...
                else:
                    cnt += 1
                    print cnt, upload_id.text, oai_id.text, harvestdate.text, collection.text
                    send(SRU_UPDATE_REQUEST % { "repoid": REPOID, "repogid": REPOGROUPID, "upload_id": upload_id.text, "oai_id": oai_id.text}, 'localhost', 8000, '/update')
                    time.sleep(.030)
                    send(SRU_DELETE_REQUEST % { "upload_id": upload_id.text}, 'localhost', 8000, '/update')
                
                
print "finished!", cnt



# OR:

# uploadids = ['rug:oai:pure.rug.nl:publications/960b00bd-83b6-49ee-8e93-ee2eabacfb42','rug:oai:pure.rug.nl:publications/047d7a40-2293-4f64-b88e-50e9bb92de2a','rug:oai:pure.rug.nl:publications/eb49b4be-7ac4-4434-a1a0-dd5d528e8dc6','rug:oai:pure.rug.nl:publications/5fceb4c9-1c27-42a3-a077-8972ed6370d0','rug:oai:pure.rug.nl:publications/0d76af52-a1e4-484c-9f3c-77115e0ba5d3','rug:oai:pure.rug.nl:publications/8277ff88-b336-4849-af0f-f4da8400d1e8','rug:oai:pure.rug.nl:publications/d51b6494-58de-4ad2-b23f-aa14d1928e97','rug:oai:pure.rug.nl:publications/1b36ab03-4931-4226-8960-1a154c3680f5','rug:oai:pure.rug.nl:publications/6cf4c248-e5d3-4d24-ba4f-541dd7f8b089','rug:oai:pure.rug.nl:publications/d713c77d-1847-44f1-8992-2830e3fe0683','rug:oai:pure.rug.nl:publications/fb6d5838-a978-4d14-af7f-5d8d8ce71088','rug:oai:pure.rug.nl:publications/7e57430a-8ebe-4e32-89bf-cc9d63e41ceb']
# 
# for uploadid in uploadids:
# 
#     send(SRU_UPDATE_REQUEST % { "repoid": "rug", "repogid": "rug", "upload_id": uploadid, "oai_id": uploadid[4:]}, 'localhost', 8000, '/update')
#     time.sleep(.030)
#     send(SRU_DELETE_REQUEST % { "upload_id": uploadid}, 'localhost', 8000, '/update')
# 
# print "ready"
