import re

from persistentidentifier import PersistentIdentifier


class Isbn(PersistentIdentifier):
    # https://en.wikipedia.org/wiki/International_Standard_Book_Number
    # A 13-digit ISBN can be separated into its parts (prefix element, registration group, registrant, publication and check digit), and when this is done it is customary to separate the parts with hyphens or spaces.
    # Separating the parts (registration group, registrant, publication and check digit) of a 10-digit ISBN is also done with either hyphens or spaces.

    # <identifier type="uri">URN:ISBN:8510-3940-25412</identifier>
    # <mods:identifier type="uri">urn:isbn:978-94-6290-466-8</mods:identifier>

    # subjects = ["9789064461019", "0-8044-2957-X", "ISBN-13: 978-0-596-52068-7", "978 1 78536 720 2", "90-902734-1-6", "ISBN-13 978 0 596 52068 7", "ISBN-10 85-359-0277-5", "urn:isbn:978-94-6290-466-8", "isbn:978-94-6290-466-8"]

    # ID_PATTERN = re.compile("^(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]$", re.IGNORECASE)
    ID_PATTERN = re.compile("^[\dxX]{10,13}$")

    def __init__(self, basestring):
        PersistentIdentifier.__init__(self, "isbn", basestring, [])

    def _validate_and_initialize(self):

        isbn = re.split(':', self.init_value).pop().strip()
        if "isbn" in isbn.lower():
            isbn = isbn.split(" ", 1).pop()

        isbn_org_id = isbn
        filteredisbn = filter(lambda x: (x != ' ' and x != "-"), isbn)

        m = self.get_idpattern().match(filteredisbn)
        if m:
            self.unformatted = isbn_org_id
            self.id = "isbn:" + filteredisbn.upper()
            self.formatted.append(filteredisbn)
            # self.resolvableurl = '%s/%s' % (self.resolver, self.unformatted)
            self.typedVariants.add(self.id)
            self.typedVariants.add(self.unformatted)
            self.typedVariants.add(filteredisbn)
            self.typedVariants.add(self.init_value)
            self.valid = True

    def __str__(self):
        return self.get_init_value()
