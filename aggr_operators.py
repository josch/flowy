import options

if options.import_grouper_ops:
    external_import = __import__(options.import_grouper_ops)

class last(object):
    __slots__ = ['field', 'gr_field', 'last']
    def __init__(self, field, gr_field):
        self.field = field
        self.gr_field = gr_field
        self.last = None
        
    def __call__(self, record = None):
        if record == None:
            return self.last
        else:
            self.last = getattr(record, self.field)
            return self.last


class sum(object):
    __slots__ = ['field', 'gr_field', 'sum']
    def __init__(self, field, gr_field):
        self.field = field
        self.gr_field = gr_field
        self.sum = 0
        
    def __call__(self, record = None):
        if record == None:
            return self.sum
        else:
            self.sum += getattr(record, self.field)
            return self.sum

class avg(object):
    __slots__ = ['field', 'gr_field', 'sum','n','avg']
    def __init__(self, field, gr_field):
        self.field = field
        self.gr_field = gr_field
        self.sum = 0
        self.n = 0
        self.avg = None
        
    def __call__(self, record = None):
        if record == None:
            if str(self.field_type).find('Int') != -1:
                return int(round(self.avg))
            else:
                return self.avg
        else:
            self.sum += getattr(record, self.field)
            self.n += 1
            self.avg = self.sum / self.n
            return self.avg
        
class max(object):
    __slots__ = ['field', 'gr_field', 'max']
    def __init__(self, field, gr_field):
        self.field = field
        self.gr_field = gr_field
        self.max = float("-inf")

    def __call__(self, record = None):
        if record == None:
            return self.max
        else:
            new_val = getattr(record, self.field)
            if self.max < new_val:
                self.max = new_val
            return self.max
        
class min(object):
    __slots__ = ['field', 'gr_field', 'min']
    def __init__(self, field, gr_field):
        self.field = field
        self.gr_field = gr_field
        self.min = float("inf")

    def __call__(self, record = None):
        if record == None:
            return self.min
        else:
            new_val = getattr(record, self.field)
            if self.min > new_val:
                self.min = new_val
            return self.min

class count(object):
    __slots__ = ['field', 'gr_field', 'count']
    def __init__(self, field, gr_field):
        self.field = field
        self.gr_field = gr_field
        self.count = 0

    def __call__(self, record = None):
        if record == None:
            return self.count
        else:
            self.count += 1
            return self.count
        
class union(object):
    __slots__ = ['field', 'gr_field', 'union']
    def __init__(self, field, gr_field):
        self.field = field
        self.gr_field = gr_field
        self.union = []

    def __call__(self, record = None):
        if record == None:
            return sorted(set(self.union))
        else:
            self.union.append(getattr(record, self.field))
            return self.union
        
class bitAND(object):
    __slots__ = ['field', 'gr_field', 'bitAND']
    def __init__(self, field, gr_field):
        self.field = field
        self.gr_field = gr_field
        self.bitAND = pow(2,field_type.size) - 1 # all 1s for the given size

    def __call__(self, record = None):
        if record == None:
            return self.bitAND
        else:
            self.bitAND &= getattr(record, self.field)
            return self.bitAND
        
class bitOR(object):
    __slots__ = ['field', 'gr_field', 'bitOR']
    def __init__(self, field, gr_field):
        self.field = field
        self.gr_field = gr_field
        self.bitOR = 0

    def __call__(self, record = None):
        if record == None:
            return self.bitOR
        else:
            self.bitOR |= getattr(record, self.field)
            return self.bitOR
