from re import compile, IGNORECASE

from nameidentifier import NameIdentifier


# https://www.wikidata.org/wiki/Property:P3153
class Crossref(NameIdentifier):
    ID_PATTERN = compile(r'^(?:.*?/10.13039/)?[1-9](\d+)$', IGNORECASE)

    def __init__(self, baseDigits):
        NameIdentifier.__init__(self, "crossref", baseDigits, ['https://data.crossref.org/fundingdata/funder/10.13039/',
                                                               'http://dx.doi.org/10.13039/'])

    def validate_and_initialize(self):
        m = self.get_idpattern().match(self.init_value)

        if m:
            self.unformatted = ('%s' % (m.group(1)))
            self.formatted.append(self.unformatted)
            self.valid = True
            self.id = self.unformatted
            self.typedVariants.update(self.formatted)
            for prefix in self.prefixes:
                for suffix in self.formatted:
                    self.typedVariants.add(prefix + suffix)

    def __str__(self):
        return self.get_init_value()
