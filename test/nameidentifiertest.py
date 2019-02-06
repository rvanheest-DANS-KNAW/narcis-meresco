import unittest
from meresco.dans.nameidentifier import NameIdentifierFactory

VALID = "valid"
INVALID = "invalid"

identifier_types = \
{
 "isni":
     {VALID: ["https://isni.org/isni/1234 1234 1234 1234", "http://isni.org/isni/1234 1234 1234 1234", "isni.org/isni/1234 1234 1234 1234",
              "1234 1234 1234 1234", "1234123412341234", "1234-1234-1234-123x", "1234-1234-1234-123X"],
      INVALID: ["http://isni.org/1234 1234 1234 1234", "isni/1234 1234 1234 1234", "a234 1234 1234 1234", "1234 1234 1234 12345", "1234  1234  1234  1234", ""]
     },

 "orcid":
     {VALID: ["https://orcid.org/1234 1234 1234 1234", "http://orcid.org/1234 1234 1234 1234",
              "1234 1234 1234 1234", "1234123412341234", "1234-1234-1234-123x", "1234-1234-1234-123X"],
      INVALID: ["orcid.org/1234 1234 1234 1234", "a234 1234 1234 1234", "1234 1234 1234 12345", "1234  1234  1234  1234", ""]
      },

 "dai":
    {VALID:   ["info:eu-repo/dai/nl/1234567", "1234567", "1234567890", "0123456X", "0123456x"],
     INVALID: ["info:eu-repo/dai/1234567", "0123456A", "x123456", ""]
    },

 "crossref":
    {VALID:  ["https://data.crossref.org/fundingdata/funder/10.13039/12345", "http://dx.doi.org/10.13039/12345",
              "9876543210", "12"],
    INVALID: ["10.13039/12345", "http://dx.doi.org/10.13039/012345", "012345", "a12345", ""]
    },

 "grid":
     {VALID: ["https://www.grid.ac/institutes/grid.1234.0a", "grid.123456.af", "whateverhere_grid.123456.af"],
      INVALID: ["rid.123456.af", "grid.123.1", "grid.1234567.1", "grid.12345.123", "grid.12345.g", "grid.1234", ""]
     },

 "prs":
     {VALID: ["PRS1234567", "prs1234567"],
      INVALID: ["PR1234567", "1234567", "PRS123456", "PRS12345678", "PRS 1234567", "PRS123456x", ""]
     },

 "rid":
     {VALID: ["https://www.researcherid.com/rid/A-1234-1234", "http://www.researcherid.com/rid/A-1234-1234",
              "A-1234-1234", "x12341234"],
      INVALID: ["1-1234-1234", "A.1234.1234", "A-123-1234", "A-1234-12345", ""]
     },

 "viaf":
     {VALID: ["https://viaf.org/viaf/10", "http://viaf.org/viaf/10", "viaf.org/viaf/10", "viaf.org/viaf/10123",
              "viaf.org/viaf/101234567", "viaf.org/viaf/1012345678901234567", "viaf.org/viaf/1012345678901234567890"],
      INVALID: ["https://viaf.org/10", "viaf.org/viaf/01", "viaf.org/viaf/1a", "viaf.org/viaf/1", "viaf.org/viaf/1012345678",
                "viaf.org/viaf/10123456789012345678901", ""]
     },

 "ror":
     {VALID: ["https://ror.org/043c0p156", "http://ror.org/043c0p156", "ror.org/043c0p156", "ror:043c0p156", "043c0p156"],
      INVALID: ["https://ror.org/043c0p-56", "http://ror.org/_043c0p15", "rot.org/043c0p156", "ror043c0p156", "043c0p15", ""]
     },

 }


class NameIdentifierTest(unittest.TestCase):

    def test_identifier(self):

        for id_type in identifier_types:

            print "\nRunning {} validator test".format(id_type.upper()),

            for id in identifier_types[id_type][VALID]:
                identifier = NameIdentifierFactory.factory(id_type, id)
                self.assertTrue(identifier.is_valid())
                print "+",
                # print "valid {} {}".format(id_type, id)

            for id in identifier_types[id_type][INVALID]:
                identifier = NameIdentifierFactory.factory(id_type, id)
                self.assertFalse(identifier.is_valid())
                print "-",
                # print "invalid {} {}".format(id_type, id)
        print ""


if __name__ == '__main__':
    unittest.main()
