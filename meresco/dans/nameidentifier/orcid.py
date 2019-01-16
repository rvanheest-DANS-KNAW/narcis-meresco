from re import compile, IGNORECASE

from nameidentifier import NameIdentifier


class Orcid(NameIdentifier):
    ID_PATTERN = compile(r'^(https?://orcid.org/)?(\d{4}).?(\d{4}).?(\d{4}).?(\d{3}[0-9X])$', IGNORECASE)

    def __init__(self, baseDigits):
        NameIdentifier.__init__(self, "orcid", baseDigits, ['http://orcid.org/'])

    def validate_and_initialize(self):

        m = self.get_idpattern().match(self.init_value)

        if m:
            self.unformatted = ('%s%s%s%s' % (m.group(2), m.group(3), m.group(4), m.group(5))).upper()

            self.formatted.append(self.unformatted)
            self.formatted.append(('%s-%s-%s-%s' % (m.group(2), m.group(3), m.group(4), m.group(5))).upper())
            self.formatted.append(('%s %s %s %s' % (m.group(2), m.group(3), m.group(4), m.group(5))).upper())

            # str_id = 'INVALID ' + self.get_name() + ': ' + self.init_value
            str_id = None
            if len(self.formatted) > 0:
                str_id = '%s%s' % (self.prefixes[0], self.formatted[1])  # http://orcid.org/0000-0002-5228-1970
                self.valid = True
            self.id = str_id

            self.typedVariants.update(self.formatted)
            for prefix in self.prefixes:
                for suffix in self.formatted:
                    self.typedVariants.add(prefix + suffix)

    def __str__(self):
        return self.get_init_value()
