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

class MetaToFieldsList(Observable):

    def add(self, lxmlNode, **kwargs):
        fieldslist = []
        for child in lxmlNode.getroot().getchildren():
            if child.tag == curieToTag('meta:repository'):
                for repokind in child.iterchildren():
                    fieldname = tagToCurie(repokind.tag)
                    fieldslist.append((fieldname, repokind.text))

        yield self.all.add(fieldslist=fieldslist, **kwargs)



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