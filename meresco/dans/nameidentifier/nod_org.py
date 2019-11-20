from re import compile, IGNORECASE

from nameidentifier import NameIdentifier


# from __init__ import pattern_dai
# The ORG NOD idenitfier format: ORG1234567

class NodOrg(NameIdentifier):
    ID_PATTERN = compile(r'^(ORG)([0-9]{7})$', IGNORECASE)

    def __init__(self, baseDigits):
        NameIdentifier.__init__(self, "nod-org", baseDigits, vsoiprefix="NOD")

    def validate_and_initialize(self):

        m = self.get_idpattern().match(self.init_value)

        if m:
            self.unformatted = m.group(0).upper()
            self.formatted.append(self.unformatted)

            str_id = None
            if len(self.formatted) > 0:
                str_id = '%s' % (self.formatted[0])  # ORG1234567
                self.valid = True
            self.id = str_id

            self.typedVariants.update(self.formatted)

    def __str__(self):
        return self.get_init_value()
