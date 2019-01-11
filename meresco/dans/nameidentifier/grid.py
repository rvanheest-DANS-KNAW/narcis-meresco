from re import compile, IGNORECASE

from nameidentifier import NameIdentifier


# https://www.wikidata.org/wiki/Property:P2427
class Grid(NameIdentifier):
    ID_PATTERN = compile(r'.*?(grid\.\d{4,6}\.[a-f0-9]{1,2})$', IGNORECASE)

    def __init__(self, baseDigits):
        NameIdentifier.__init__(self, "grid", baseDigits, ['https://www.grid.ac/institutes/'])

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
