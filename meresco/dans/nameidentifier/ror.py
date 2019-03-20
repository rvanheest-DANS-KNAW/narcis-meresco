from re import compile

from nameidentifier import NameIdentifier


# https://ror.org/043c0p156
class Ror(NameIdentifier):
    ID_PATTERN = compile(r'^(?:(?:https?://)?(?:ror\.org/|ror:))?([a-zA-Z0-9]{9})$')


    def __init__(self, baseDigits):
        NameIdentifier.__init__(self, "ror", baseDigits, ['https://ror.org/'])

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
