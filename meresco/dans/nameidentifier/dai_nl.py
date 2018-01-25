from re import compile, IGNORECASE

from nameidentifier import NameIdentifier


# from __init__ import pattern_dai
# The DAI (or PPN) contains 9 to 10 characters. The first 8 to 9 characters are numbers. The last (9th or 10th) character is a control character.
# https://wiki.surfnet.nl/display/standards/DAI
# Echter heeft meneer Blokmans een 8 cijferige DAI en niet alleen in VSOI: http://www.narcis.nl/person/RecordID/PRS1234955

class Dai(NameIdentifier):
    ID_PATTERN = compile(r'^(info:eu-repo/dai/nl/)?(\d{6,9}[0-9X])$', IGNORECASE)

    def __init__(self, baseDigits):
        NameIdentifier.__init__(self, "dai-nl", baseDigits, ['info:eu-repo/dai/nl/'])

    def validate_and_initialize(self):

        m = self.get_idpattern().match(self.init_value)

        if m:
            self.unformatted = m.group(2).upper()

            self.formatted.append(self.unformatted)

            str_id = None
            if len(self.formatted) > 0:
                str_id = '%s%s' % (self.prefixes[0], self.formatted[0])  # info:eu-repo/dai/nl/071935553X
                self.valid = True
            self.id = str_id

            self.typedVariants.update(self.formatted)
            for prefix in self.prefixes:
                for suffix in self.formatted:
                    self.typedVariants.add(prefix + suffix)

    def __str__(self):
        return self.get_init_value()
