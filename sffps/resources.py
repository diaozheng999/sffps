
ENVIRONMENT = 0
ECONOMY = 1
INFRASTRUCTURE = 2
HAPPINESS = 3

RESOURCE_ABBRS = ['ENV', 'ECO', 'INF', 'HAP']

class Resources(object):
    comparator = {
        '>=' : lambda a,b: a >= b,
        '<=' : lambda a,b: a <= b,
        '==' : lambda a,b: a == b,
        '!=' : lambda a,b: a != b
    }
    def __init__(self, manager, resources, min_val, max_val):
        self.game_manager = manager
        self.resources = list(resources)
        self.min_val = min_val
        self.max_val = max_val

    def check(self, resource_checks):
        for (resource, op, value) in resource_checks:
            if not self.comparator[op](self.resources[resource], value):
                return False
        return True

    def update(self, resource_deltas):
        for (resource, delta) in resource_deltas:
            self.resources[resource] += delta
            if self.resources[resource] > self.max_val:
                self.resources[resource] = self.max_val
            if self.resources[resource] == self.min_val:
                self.game_manager.game_over()

    def set_value(self, resource_values):
        for (resource, value) in resource_values:
            self.resources[resource] = value
            if self.resources[resource] > self.max_val:
                self.resources[resource] = self.max_val
            if self.resources[resource] == self.min_val:
                self.game_manager.game_over()

    def repr_values(self, vals, positive=True):
        ret_str = ""
        for (resource, value) in vals:
            if ret_str:
                ret_str += ", "
            if positive and value >= 0:
                ret_str += '+'
            ret_str += '%d %s'%(value, RESOURCE_ABBRS[resource])
        return ret_str

    def repr_checks(self, checks):
        if len(checks) == 1:
            return "%s %s %d"%(RESOURCE_ABBRS[checks[0][0]], checks[0][1], checks[0][2])
        
        return "(%s)"%(' & '.join(
            ("%s %s %d"%(RESOURCE_ABBRS[a], b, c) for a,b,c in checks)
        ))