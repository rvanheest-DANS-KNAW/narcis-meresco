class NameIdentifier(object):
    ID_PATTERN = None

    def __init__(self, name, init_value, prefixes=[], vsoiprefix=None):
        self.name = name  # Name of the nameIdentifier (lowercase). isni, orcid, dai-nl, rid, etc. 1::1
        self.prefixes = prefixes  # List of 'known' base string prefixes. 0::n
        # instance vars:
        self.init_value = init_value  # Initial value used to construct the NameIdentifier. 1::1
        self.unformatted = None  # Unformatted 'base' string: 07193555X, 0000000123456789, 000000021694233x, etc. 1::1
        self.id = None  # 'Fully qualified name' or 'preferred' variant.
        self.formatted = []  # List of 'known' base string variations (formatted): 0000 0001 3333 4444, 0000-0001-3333-4444, 0000#0001#3333#4444 etc. 0::n
        self.typedVariants = set()  # List of all possible 'valid' persistentidentifier string configurations. 1::n
        self.valid = False  # Given ID matches the regex or not.
        self.vsoiprefix = name.upper() if vsoiprefix is None else vsoiprefix  # Sets the prefix used in NARCIS DB. Defaults to the name of this identifier.
        self.validate_and_initialize()  # Match the constructor to the NID RegEx and generate the typedVariants

    def get_name(self):
        return self.name

    def get_init_value(self):
        return self.init_value

    def get_basedigits(self):
        return self.unformatted

    def get_id(self):
        return self.id

    def is_valid(self):
        return self.valid

    def get_idx_id(self):
        return '%s:%s' % (self.get_name().lower(), self.unformatted) if self.valid else None

    def validate_and_initialize(self):
        raise NotImplementedError("Subclasses should implement this.")

    def getTypedVariants(self):
        return self.typedVariants

    def get_vsoi_format(self):
        return '%s%s' % (self.vsoiprefix, self.get_basedigits()) if self.valid else None

    def __str__(self):
        return '%s (%s)' % (self.name, self.init_value)

    @classmethod
    def get_idpattern(cls):
        return cls.ID_PATTERN
