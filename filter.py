from copy import deepcopy
from copy import copy
from statement import Field
from record import RecordReader
import time
import profiler

class NoMatch(Exception):
    pass

class Filter(object):
    def __init__(self,rules, records, br_mask, nbranches):
        self.rules = rules
        self.records = records
        self.br_mask = br_mask
        
#        print "The filter has just been initiated"
    
    # Iteration of the filter happens at the splitter function go()
    # In this teration function, each of the records is being matched
    # against all of the conditions in each of the filters, and based
    # on what condition it matches, it is assigned an appropriate 
    # branch mask. I.e., if Branch A has a srcport=443, then the record
    # that matches this requirement gets a mask of [True, False], else
    # if Branch B's filter is matched, then a mask of [False, True] is
    # assigned.
    def __iter__(self):
        print "Started filtering"
#        start = time.clock()
#        print "Fitlering time started at:", start
        for record in self.records:
            self.br_mask.reset()
            try:
                for rule in self.rules:
                    rule_result =  rule.match(record)
                    self.br_mask.mask(rule.branch_mask, rule_result)
            except NoMatch:
                continue
            
            branches = self.br_mask.final_result()
            if True in branches:
                yield record, branches
        

#        print "Finished filtering"
#        time_elapsed = (time.clock() - start)
#        print "Filtering required:", time_elapsed

#class Field(object):
#    def __init__(self, name):
#        self.name = name
#    def __repr__(self):
#        return "Field('%s')"%self.name

# Implementation of a self-defined deepcopy function that operates
# for the simple data types.

def deep_copy(org):		
	out = dict().fromkeys(org)
	for k,v in org.iteritems():
	    try:
	        out[k] = v.copy()   # dicts, sets
	    except AttributeError:
	        try:
	            out[k] = v[:]   # lists, tuples, strings, unicode
	        except TypeError:
	            out[k] = v      # ints

	return out



class BranchMask(object):
    def __init__(self, branch_masks, pseudo_branches, n_real_branches):
        self.masks = branch_masks
#        self.orig_mask = deepcopy(branch_masks)
        self.orig_mask = deep_copy(branch_masks)
#        self.pseudo_branches = deepcopy(pseudo_branches)
        self.pseudo_branches = deep_copy(pseudo_branches)
        self.n_real_branches = n_real_branches

		
    def reset(self):
#        self.masks = deepcopy(self.orig_mask)
        self.masks = deep_copy(self.orig_mask)
        #self.masks = copy(self.orig_mask)
#        self.masks = self.orig_mask

    
    def mask(self, sub_branches, result):
        for br, sub_br, NOT in sub_branches:
            res = not result if NOT else result
            if sub_br == 0:
                self.masks[br][sub_br] = self.masks[br][sub_br] and res
            else:
                self.masks[br][sub_br] = self.masks[br][sub_br] or res

        
    def final_result(self):
        final_mask = {}

        for br, mask in self.masks.iteritems():
            final_mask[br] = True if False not in mask else False
        result = []
        for id in xrange(self.n_real_branches):
            try:
                result.append(final_mask[id])

            except KeyError:
                gr_res = True
                for or_group in self.pseudo_branches[id]:
                    res = False
                    for ref in or_group:
                        if ref[1]:
                            res = res or not final_mask[ref[0]]
                        else:
                            res = res or final_mask[ref[0]]
                            
                    gr_res = gr_res and res
                
                result.append(gr_res)
                
        return result


class Rule(object):
    def __init__(self, branch_mask, operation, args):
        self.operation = operation
        self.args = args
        self.branch_mask = branch_mask

	# This match operation is used at both the filtering and group-filering
	# stages, since group-filter also relies on this Rule class.
    def match(self, record):
        args = []
        for arg in self.args:
            if type(arg) is Field: 	# Used both at filterin and group-filtering stages
                args.append(getattr(record, arg.name))
            elif type(arg) is Rule:	# Used only at the group-fitlering stage 
                args.append(arg.match(record))
            else:					# Used at both stages. The actual argument numbers, i.e., port 80
                args.append(arg)

        return self.operation(*args)

class PreSplitRule(Rule):
    def match(self,record):
        result = Rule.match(self,record)
        if not result:
            raise NoMatch()

class GroupFilter(object):
    def __init__(self, rules, records, branch_name, groups_table, index):
        self.rules = rules
        self.records = records
        self.branch_name = branch_name
        self.index = index
        self.groups_table = groups_table
        self.record_reader = RecordReader(self.groups_table)
    
    def go(self):
    	
        count = 0
        for record in self.records:
            for or_rules in self.rules:
                matched = False
                for rule in or_rules:
                    if rule.match(record):
                        matched = True
                        break
                if not matched:
                    break
            if matched:
                record.rec_id = count
                count += 1
                self.index.add(record)
                self.groups_table.append(record)
        print "Finished filtering groups for branch " + self.branch_name
        self.groups_table.flush()
        
    def __iter__(self):
        for rec in self.record_reader:
            yield rec

class AcceptGroupFilter(GroupFilter):
    def __init__(self, records, branch_name, groups_table, index):
        GroupFilter.__init__(self, None, records, branch_name, groups_table,
                             index)
    def go(self):
        count = 0
        for record in self.records:
            record.rec_id = count
            count += 1
            self.index.add(record)
            self.groups_table.append(record)
        print "Finished filtering groups for branch " + self.branch_name
        self.groups_table.flush()
