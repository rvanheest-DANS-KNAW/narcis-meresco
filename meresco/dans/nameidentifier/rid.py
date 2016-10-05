from nameidentifier import NameIdentifier
from re import compile, IGNORECASE


class Rid(NameIdentifier):

    ID_PATTERN = compile(r'^([A-z])-?(\d{4})-?(\d{4})$', IGNORECASE)

    def __init__(self, baseDigits):
        NameIdentifier.__init__(self, "rid", baseDigits)

    def validate_and_initialize(self):

        m = self.get_idpattern().match(self.init_value)

        if m:
            self.unformatted = ('%s%s%s' % (m.group(1), m.group(2), m.group(3))).upper()
            self.formatted.append(('%s-%s-%s' % (m.group(1), m.group(2), m.group(3))).upper())
            self.formatted.append(self.unformatted)

            # str_id = 'INVALID ' + self.get_name() + ': ' +  self.init_value
            str_id = None
            if len(self.formatted) > 0:
                str_id = '%s' % (self.formatted[0]) # J-2649-2013, A-8329-2010, E-9043-2011
                self.valid = True
            self.id = str_id

            self.typedVariants.extend(self.formatted)

    def __str__(self):
        return self.get_init_value()
