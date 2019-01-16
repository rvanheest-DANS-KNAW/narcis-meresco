from re import compile, IGNORECASE

from nameidentifier import NameIdentifier

# https://www.wikidata.org/wiki/Property:P214
class Viaf(NameIdentifier):
    ID_PATTERN = compile(r'^(https?://viaf.org/viaf/|viaf.org/viaf/)?([1-9]\d(\d{0,7}|\d{17,20}))$', IGNORECASE)

    def __init__(self, baseDigits):
        NameIdentifier.__init__(self, "viaf", baseDigits, ['https://viaf.org/viaf/'])

    def validate_and_initialize(self):
        m = self.get_idpattern().match(self.init_value)

        if m:
            self.unformatted = ('%s' % (m.group(2)))
            self.formatted.append(self.unformatted)
            self.valid = True
            self.id = self.unformatted
            self.typedVariants.update(self.formatted)
            for prefix in self.prefixes:
                for suffix in self.formatted:
                    self.typedVariants.add(prefix + suffix)

    def __str__(self):
        return self.get_init_value()
