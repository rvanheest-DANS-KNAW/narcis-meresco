from re import compile, IGNORECASE

from nameidentifier import NameIdentifier


class Isni(NameIdentifier):
    ID_PATTERN = compile(r'^(https?://isni.org/isni/|isni.org/isni/)?(\d{4}).?(\d{4}).?(\d{4}).?(\d{3}[0-9X])$',
                         IGNORECASE)

    def __init__(self, basevalue):
        NameIdentifier.__init__(self, 'isni', basevalue,
                                ['http://isni.org/isni/', 'isni.org/isni/',
                                 'ISNI '])  # , 'http://isni-url.oclc.nl/isni/'

    def validate_and_initialize(self):

        m = self.get_idpattern().match(self.init_value)

        if m:
            self.unformatted = ('%s%s%s%s' % (m.group(2), m.group(3), m.group(4), m.group(5))).upper()

            self.formatted.append(self.unformatted)
            self.formatted.append(('%s %s %s %s' % (m.group(2), m.group(3), m.group(4), m.group(5))).upper())

            str_id = None
            if len(self.formatted) > 0:
                str_id = '%s%s' % (self.prefixes[0], self.formatted[0])  # http://isni.org/isni/000000013333448X
                self.valid = True
            self.id = str_id

            self.typedVariants.update(self.formatted)
            for prefix in self.prefixes:
                for suffix in self.formatted:
                    self.typedVariants.add(prefix + suffix)

    def __str__(self):
        return self.get_init_value()
