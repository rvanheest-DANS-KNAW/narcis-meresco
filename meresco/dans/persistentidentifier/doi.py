from re import compile, IGNORECASE
from urlparse import urlparse

from persistentidentifier import PersistentIdentifier


class Doi(PersistentIdentifier):
    DOIURI_PATTERN = compile("^(https?://(dx\\.)?)?doi\\.org/(urn:)?(doi:)?", IGNORECASE)
    ID_PATTERN = compile("^(?:urn:)?(?:doi:)?(10(?:\\.[0-9]+)+)/(.+)$", IGNORECASE)

    def __init__(self, baseDigits):
        PersistentIdentifier.__init__(self, "doi", baseDigits,
                                      ["https://dx.doi.org/", "http://dx.doi.org/", "http://doi.org/",
                                       "https://doi.org/", "doi:"], "https://dx.doi.org/")

    def _validate_and_initialize(self):

        # First, get the DOI-part of the given string; strip the 'resolver' part:
        doi_part = self.init_value
        uri_match = Doi.DOIURI_PATTERN.match(self.init_value)
        if uri_match:
            doi_part = self.init_value.replace(uri_match.group(0), "")

        # Continue to check for valid DOI:
        m = self.get_idpattern().match(doi_part)

        if m:
            self.unformatted = ('%s/%s' % (m.group(1), m.group(2))).lower()

            # Get rid of any query params and fragments...
            o = urlparse('http://www.example.com/%s' % self.unformatted)
            self.formatted.append(o.path[1:])

            str_id = None
            if len(self.formatted) > 0:
                str_id = '%s%s' % (self.prefixes[4], self.formatted[0])  # doi:10.1000/000000013333448X
                self.resolvableurl = self.resolver + self.formatted[0]
                self.valid = True
            self.id = str_id

            self.typedVariants.add(self.init_value)
            self.typedVariants.update(self.formatted)
            for prefix in self.prefixes:
                for suffix in self.formatted:
                    self.typedVariants.add(prefix + suffix)

    def __str__(self):
        return self.get_init_value()
