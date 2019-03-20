__author__ = 'wilkos'
from crossref import Crossref
from dai_nl import Dai
from grid import Grid
from isni import Isni
from nod_prs import NodPrs
from orcid import Orcid
from rid import Rid
from viaf import Viaf
from ror import Ror
from unknown import Unknown


class NameIdentifierFactory(object):
    # Create based on class name:
    @staticmethod
    def factory(type, baseval):
        baseval = baseval.strip().replace('\n', '')
        # return eval(type + "("+baseval+")")
        if type.strip().lower() == "dai" or type.lower() == "dai-nl" or 'dai' in type.lower(): return Dai(baseval)
        if type.strip().lower() == "orcid": return Orcid(baseval)
        if type.strip().lower() == "isni": return Isni(baseval)
        if type.strip().lower() == "rid": return Rid(baseval)
        if type.strip().lower() == "viaf": return Viaf(baseval)
        if type.strip().lower() == "prs" or type.lower() == "nod-prs": return NodPrs(baseval)
        if "crossref" in type.lower(): return Crossref(baseval)
        if type.strip().lower() == "grid" or "grid" in type.lower(): return Grid(baseval)
        if type.strip().lower() == "ror": return Ror(baseval)
        return Unknown(type.strip().replace('\n', ''), baseval)
        # assert 0, "Bad nid creation: " + type
