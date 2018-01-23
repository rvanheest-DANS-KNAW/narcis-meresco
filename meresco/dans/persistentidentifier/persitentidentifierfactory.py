__author__ = 'wilkos'

from arxiv import ArXiv
from doi import Doi
from handle import Handle
from href import Href
from isbn import Isbn
from issn import Issn
from unknown import Unknown
from urnnbn import UrnNbn


class PidFactory(object):
    # Create based on class name:
    @staticmethod
    def factory(type, baseval):
        baseval = baseval.strip().replace('\n', '')
        if type.strip().lower() == "doi":
            return Doi(baseval)
        if type.strip().lower() == "urn" or type.strip().lower() == "urn:nbn" or type.strip().lower() == "urnnbn":
            return UrnNbn(baseval)
        if type.strip().lower() == "arxiv":
            return ArXiv(baseval)
        if type.strip().lower() == "href" or type.strip().lower() == "url":
            return Href(baseval)
        if type.strip().lower() == "issn":
            return Issn(baseval)
        if type.strip().lower() == "isbn":
            return Isbn(baseval)
        if type.strip().lower() == "uri":
            if ("issn" in baseval.lower()):
                return Issn(baseval)
            elif ("isbn" in baseval.lower()):
                return Isbn(baseval)
            elif (":doi" in baseval.lower()):
                return Doi(baseval)
            else:
                return Href(baseval)
        if type.strip().lower() == "handle" or type.strip().lower() == "hdl":
            return Handle(baseval)
        return Unknown(type.strip().replace('\n', ''), baseval)

# <mods:identifier type="uri">info:doi/10.90022333/234</mods:identifier>
# <mods:identifier type="uri">URN:ISSN:1876-4142</mods:identifier>
# <mods:identifier type="uri">urn:isbn:978-94-6290-466-8</mods:identifier>


# DataCite kernel4:
# If RelatedIdentifier is used,
# relatedIdentifierType is
# mandatory.
# Controlled List Values:

# ARK
# arXiv
# bibcode
# DOI
# EAN13
# EISSN
# Handle
# IGSN
# ISBN
# ISSN
# ISTC
# LISSN
# LSID
# PMID
# PURL
# UPC
# URL
# URN
