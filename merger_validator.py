from validator_common import *
from copy import deepcopy
from merger import MergerStorage
from merger import Merger as MergerImpl
from merger import MergerBranch as MergerBranchImpl
from merger import MergerLastBranch as MergerLastBranchImpl
from merger import MergerRejectBranch as MergerRejectBranchImpl
from merger import MergerRule as MergerRuleImpl
import itertools
import allen_ops
import options

class MergerValidator(object):
    def __init__(self, parser, gr_filter_validator):
        self.parser = parser
        self.gr_filter_validator = gr_filter_validator
        self.mergers = deepcopy(parser.mergers)
        # The last field returns a list of the present fields for each branch
        # ('rec_id', 'Last', 'First', 'records', 'srcip', 'dstip', 'bytes', 'n', 'flags', 'srcports')
		# ('rec_id', 'Last', 'First', 'records', 'srcip', 'dstip', 'bytes', 'n', 'flags', 'dstports')
        self.branches_fields = gr_filter_validator.branches_fields
        # A simple dictionary mapptin of branch name to a GroupFilter
        # {'A': <groupfilter.GroupFilter object at 0x9c3d66c>, 'B': <groupfilter.GroupFilter object at 0x9c43ccc>} 
        self.br_name_to_gr_filter = gr_filter_validator.br_name_to_gr_filter
       	# Checks that all the defined merger modules are actually exported
		# Returns a dictionay of a merger name and module implementation
        self.megers_export_modules = self.find_mergers_export_modules()
        # Returns the size of the field type of the 'records' field, 4 bytes
        self.id_size = self.get_id_size()
        self.impl = self.get_mergers_impl()

	# Returns the size of the field type of the 'records' field, 4 bytess
    def get_id_size(self):
        rec_reader = self.gr_filter_validator.impl[0].records
        field_types = dict(zip(rec_reader.group_record_fields,
                               rec_reader.group_record_types))
        id_size = field_types['records'].itemsize
        return id_size

	# Check for duplicate merger names
    def check_duplicate_merger_names(self):
        duplicates = {}
        for merger in self.mergers:
            old_val = duplicates.setdefault(merger.name, 0)
            duplicates[merger.name] = old_val + 1
            
        duplicate_names = [k for k,v in duplicates.iteritems() if v > 1]
        if len(duplicate_names) > 0:
            msg = "Merger(s) %s"%duplicate_names
            msg += " is/are all defined more than once."
            raise SyntaxError(msg)
        
    # Check for duplicate module names
    def check_duplicate_module_names(self, merger):
        duplicates = {}
        for module in merger.modules:
            old_val = duplicates.setdefault(module.name, 0)
            duplicates[module.name] = old_val + 1
            
        duplicate_names = [k for k,v in duplicates.iteritems() if v > 1]
        if len(duplicate_names) > 0:
            msg = "Module(s) %s"%duplicate_names
            msg += " is/are all defined more than once in merger"
            msg += " %s."%merger.name
            raise SyntaxError(msg)
	
	
	# Checks that all the defined merger modules are actually exported
	# Returns a dictionay of a merger name and module implementation
    def find_mergers_export_modules(self):
        merger_to_export_module = {}
        for merger in self.mergers:
            exp = None
            for module in merger.modules:
                if merger.export == module.name:
                    exp = module
                    break
            
            if exp:
                merger_to_export_module[merger.name] = exp
#                print merger_to_export_module
            else:
                msg = "Merger %s"%merger.name
                msg += " export module %s is not defined."%merger.export
        
        return merger_to_export_module

#--------------------------------------ALLEN CHECKS-------------------------------------#
#All the operations on rules are around a sample set like: {'M': Module('m1', 38, [[Rule('EQ', 40, [Field('A.srcip'), Field('B.dstip')], False)], [Rule('EQ', 41, [Field('A.srcports'), Field('B.dstports')], False)], [Rule('LT', 42, [Field('A.bytes'), Field('B.bytes')], False)], [AllenRule('oi', 43, [Field('B'), Field('A')], False), AllenRule('d', 43, [Field('B'), Field('A')], False)]], ['B', 'A'])}

	#Returns only the Allen rules
    def iterate_module_allen_op_groups(self, merger):
        for module in merger.modules:
            for rules in module.rules:
                if type(rules[0]) is not AllenRule:
                    continue
                else:
                    for op in rules:
                        yield op

	# Orders allen operations and the branches that they influence in a reverse order, if not already so
    def order_allen_ops_args(self, merger):
        order = self.get_merger_branches_order(merger)#Orders merger branches, exported module's branches being first
        arg_combinaions = tuple(itertools.combinations(order, 2))#combinations('ABCD', 2) --> AB AC AD BC BD CD
        for allen_op in self.iterate_module_allen_op_groups(merger):#Returns only the Allen rules
            first, second = allen_op.args[:2] # Returns Field('B') Field('A')
            op = allen_op.op # operations like oi, d
            if (first.name, second.name) not in arg_combinaions:
                allen_op.args = [second, first] + allen_op.args[2:]# reverse names
                allen_op.op = allen_ops.inv_op_str(op)# and operations
                
	# A number of different checks of the AllenRule
    def check_allen_ops(self, merger):
        allen_arg_pairs = []
        arg_pairs_to_line = {}
        for module in merger.modules:
            for rules in module.rules:
                if type(rules[0]) is not AllenRule:
                    continue

                first_arg = rules[0].args[0].name # Get the branch names influenced by the AllenRule
                second_arg = rules[0].args[1].name
                line = rules[0].line
                order = (first_arg, second_arg)
                allen_arg_pairs.append(order)# [('B', 'A')]
                
                self.check_allen_satisfiability(arg_pairs_to_line, order, line)
                self.check_allen_consistency(first_arg, second_arg, rules)
                self.check_allen_deltas(rules)

        self.check_allen_reachability(allen_arg_pairs, merger)

	# The following 3 methods run different tests on the allen arguments and rules
    def check_allen_satisfiability(self, arg_pairs_to_line, order, line):
        if arg_pairs_to_line.has_key(order):
            msg = "Unsatisfiable Allen op group. "
            msg += "All allen ops concerning a pair of branches should"
            msg += " be connected with and OR into a single group "
            msg += "within a single module.\n"
            msg += "Argument pair %s on line %s"%(order, line)
            msg += " is also used on line %s."%arg_pairs_to_line[order]
            raise SyntaxError(msg)
        else:
            arg_pairs_to_line[order] = line
    def check_allen_consistency(self, first_arg, second_arg, rules):
        for al_op in rules:
            first = al_op.args[0].name
            second = al_op.args[1].name
            
            if (first != first_arg or second != second_arg):
                msg = "Inconsistent group of Allen statements "
                msg += "on line %s"%rules[0].line
                msg += ": %s, %s.\n"%(first, second)
                msg += "All branches in this group should have "
                msg += "%s and %s"%(first_arg, second_arg)
                msg += " as left and righthand side arguments "
                msg += "respectively."
                raise SyntaxError(msg)
    def check_allen_deltas(self, rules):
        for al_op in rules:
            if al_op.op == 'LT' or al_op.op == 'GT':
                if len(al_op.args) < 3:
                    msg = "Allen op < or > on line %s "%al_op.line
                    msg += " should have delta explicitly stated."
                    raise SyntaxError(msg)
    # A check for reachability of subsequent branches from the first one
    def check_allen_reachability(self, allen_arg_pairs, merger):
        br_order = self.get_merger_branches_order(merger)
        # check reachability through allen index from initial branch
        # of export module:
        reachable = br_order[0:1] # list of first branch of exp module
        unreachable = br_order[1:]
        change = True
        while(change):
            change = False
            for arg1, arg2 in allen_arg_pairs:
                if arg1 in reachable and arg2 in unreachable:
                    unreachable.remove(arg2)
                    reachable.append(arg2)
                    change = True
        if len(unreachable) > 0:
            msg = "Branch(es): %s"%unreachable
            msg += " in merger %s"%merger.name
            msg += " is/are unreachable through an allen op or chain of"
            msg += " allen ops from the first branch of the exported module"
            raise SyntaxError(msg)
#--------------------------------------END ALLEN CHECKS---------------------------------#

	# Orders the merger modules s.t. the exported module comes first
    def order_modules(self):
        for merger in self.mergers:
            exp_module = self.megers_export_modules[merger.name]
            new_modules_order = [exp_module]
            new_modules_order += [m for m in merger.modules if m != exp_module]
            merger.modules = new_modules_order
            
    # Checks that the modules are interconnected among each other with at least one branch
    def check_for_disjoint_modules(self):
        for merger in self.mergers:
            exp_module = self.megers_export_modules[merger.name]
            exp_branches = set(exp_module.branches)
            for module in merger.modules:
                branches = set(module.branches)
                # NOTE & is set intersection
                if len(exp_branches & branches) < 1:
                    msg = "Merger module %s.%s"%(merger.name,module.name)
                    msg += " in has no overlaping branches with the"
                    msg += " export module."
                    raise SyntaxError(msg)
                    
    
    # Check the validity of the AllenRule, by seeing if the branch names are all defined    
    def check_branch_id_ref(self, rule, module_branches):
        for arg in rule.args:
            if type(arg) is Field:
                id_ref = arg.name
                if id_ref not in self.br_name_to_gr_filter.keys():
                    msg = 'Branch %s referenced on line'%id_ref
                    msg += ' %s is not defined.'%rule.line
                    raise SyntaxError(msg)
                if id_ref not in module_branches:
                    msg = 'Branch %s referenced on line'%id_ref
                    msg += " %s "%rule.line
                    msg += "is not in module's branches statement."
                    raise SyntaxError(msg)

	# Check the validity of the Rule, GrouperRule and statements like A.bytes
    def check_qid_field_ref(self, rule, module_branches):
        for arg in rule.args:
            if type(arg) is Field:
                qid_field = arg.name
                branch, _, field = qid_field.partition('.') #Separates statements like A.bytes
                try:
                    if field not in self.branches_fields[branch]:
                        msg = 'Wrong field %s on line %s. '%(qid_field,
                                                            rule.line)
                        msg += 'Branch %s does not have field %s.'%(branch,
                                                                    field)
                        raise SyntaxError(msg)
                except KeyError:
                    msg = 'Branch %s referenced on line'%branch
                    msg += ' %s is not defined'%rule.line
                    raise SyntaxError(msg)
                if branch not in module_branches:
                    msg = 'Branch %s referenced on line'%branch
                    msg += " %s "%rule.line
                    msg += "is not in module's branches statement."
                    raise SyntaxError(msg)
    
	# Orders merger branches with the exported module's branches being first
    def get_merger_branches_order(self, merger):
        br_order = []
        # first add export module
        for module in merger.modules:
            if module.name == merger.export:
                for br in module.branches:
                    if br not in br_order:
                        br_order.append(br)

        # add all the others:
        for module in merger.modules:
            for br in module.branches:
                if br not in br_order:
                    br_order.append(br)
        
        return br_order

	#
    def order_merger_rules(self, merger):
        """
        Produces mapping between incrementally larger available branches tuples
        (A,B,C,etc) ordered as they will appear in the implementation.
        """
        br_order = self.get_merger_branches_order(merger)
        needed_brs_to_rule = {}
        for module in merger.modules:
            replace_with_vals(module)
            replace_bound_rules(module)
            for rules in module.rules:
                rule_branches = self.get_rule_needed_branches(rules[0])
                
                ordered_branches = tuple(br for br in br_order
                                         if br in rule_branches)
                
                if len(rules) > 1:
                    rule = Rule('or_op', 0, rules)
                else:
                    rule = rules[0]
                needed_brs_to_rule.setdefault(ordered_branches,
                                              []).append(rule)

        avail_to_rules = {}
        tup = ()
        # create sets - needed for the set intersection operation
        needed_sets =  map(set, needed_brs_to_rule.keys())
        # incrementaly add branches to the tuple of available branches
        #  and check which rules have their branch needs satisfied
        for br in br_order:
            tup += (br,)
            # find how many of the needed branches are in this tuple
            # of branches. It makes elementwise intesection of the sets
            # of the needed branches and the tuple of available branches
            intersect = map(set(tup).intersection , needed_sets )
            for el, intersection, key in zip(needed_sets , intersect,
                                             needed_brs_to_rule.keys()):
                if len(intersection) == len(el):
                    # Lenght is the same, which means all needed branches
                    # are present. Remove these elements, take the rules from
                    # the needed_brs_to_rule and delete the key their to
                    # keep the zip() in sync
                    needed_sets.remove(el)
                    avail_to_rules[tup] = needed_brs_to_rule[key]
                    del needed_brs_to_rule[key]
        return avail_to_rules

	#    
    def get_rule_needed_branches(self, rule):
        args_list = set()
        for sub_rule in iterate_subrules(rule):
            for arg in sub_rule.args:
                if type(arg) is Field:
                    args_list.add(arg.name)
        
        for arg in rule.args:
            if type(arg) is Field:
                    args_list.add(arg.name)
        
        if type(rule) is AllenRule:
            return list(args_list)
        
        else:
            return [qid.partition('.')[0] for qid in args_list]
    

	# Validates the correctness of the merger stage
    def validate(self):
        self.check_duplicate_merger_names()
        for merger in self.mergers:
            self.check_duplicate_module_names(merger)
            for module in merger.modules:
            	# Checks the whole rule list to see that all 
            	# the rules fall into [Rule, GrouperRule, AllenRule]
            	# Returns the actual rules
                for rule in iterate_rules(module):
                	# Checks that all the rule entries are correctly specified
                    if type(rule) is AllenRule:
                        self.check_branch_id_ref(rule, module.branches)
                    else:
                        self.check_qid_field_ref(rule, module.branches)
            # Orders allen operations and the branches that they influence in a reverse order
            self.order_allen_ops_args(merger)
            # Performs several checks on the branches and the operations (consistency, reachability, etc.)
            self.check_allen_ops(merger)
        
        # Orders the merger modules s.t. the exported module comes first    
        self.order_modules() 
        # Checks that the modules are interconnected among each other with at least one branch
        self.check_for_disjoint_modules()

	
	# Get the allen indexing operations for each branch.
    def get_branches_allen_index_ops(self, merger):
        """
        Get the allen indexing operations for each branch.
        """
        br_to_allen_ind_ops = {}
        for module in merger.modules:
            for rules in module.rules:
                if type(rules[0]) != AllenRule:
                    continue
                br = rules[0].args[0].name
                br_to_allen_ind_ops.setdefault(br, []).append(rules)
        return br_to_allen_ind_ops
	
	#
    def get_rule_impl(self, rule, br_to_record):
        if type(rule) == AllenRule:
            op = find_op(rule, module='allen_ops')
            args = [ (arg.name, None)
                    if type(arg) == Field else arg 
                    for arg in rule.args]
        else:
            args = []
            op = find_op(rule)
            for arg in rule.args:
                if type(arg) == Rule:
                    arg_impl = self.get_rule_impl(arg, br_to_record)
                elif type(arg) == Field:
                    branch, _, field = arg.name.partition('.')
                    arg_impl = (branch, field)
                else:
                    arg_impl = arg

                args.append(arg_impl)
        return MergerRuleImpl(op, args, br_to_record)
    
    # Create indexing rules implementation for AllenRules
    def get_index_rule_impl(self, rules):
        res = []
        for or_rules in rules:
            or_rules_impl = []
            for rule in or_rules:
                op = find_op(rule, 'allen_index')
                args = [arg.name if type(arg) == Field else arg 
                        for arg in rule.args]
                # replace with values
                args = [arg.value if type(arg) == Arg else arg
                        for arg in args]
                #[<allen_index.oi object at 0x9f5adcc>, <allen_index.d object at 0x9f5ae0c>]
                or_rules_impl.append(op(*args))
            res.append(or_rules_impl)
        return res

	# Creates a file MergedM.h5 for further storage of the merged files
    def get_merger_table_impl(self, merger):
        fields = self.megers_export_modules[merger.name].branches
        types = [UIntCol(self.id_size) for _ in fields]
        field_types = dict(zip(fields,types))
        recordClass = record.get_record_class(fields, types)
        # TODO fix file names 
        fname = options.temp_path + options.merger_file_prefix
        fname += merger.name + ".h5"
        if options.delete_temp_files: if_exists_delete(fname)
        pytables.create_table_file(fname, field_types)
        mergerTable = FlowRecordsTable(fname)
        
        return MergerStorage(merger.name, mergerTable, recordClass)

	# Actual implementation of the merger stage
    def get_merger_impl(self, merger):
        # Create merger storage
        merger_table = self.get_merger_table_impl(merger)

        # Create indexing rules implementation
        br_to_index_rule_impl = {}

# {'B': [[AllenRule('oi', 43, [Field('B'), Field('A')], False), AllenRule('d', 43, [Field('B'), Field('A')], False)]]}
        for br, rules in self.get_branches_allen_index_ops(merger).iteritems():
            br_to_index_rule_impl[br] = self.get_index_rule_impl(rules)# List of allen index rules implemented
        
        for br in self.get_merger_branches_order(merger):#orders branches with the exported branch being first
            if br not in br_to_index_rule_impl.keys():
                br_to_index_rule_impl[br] = []
        
        # some "globals" shared among branches or needed for their creation
        needed_brs = self.order_merger_rules(merger) # Re-orders the rules as they will appear in the implementation
        tup = () # tuple of available branches
        name = merger.name
        br_order = self.get_merger_branches_order(merger) # Returns reversely-ordered branch names of the merger
        export_branches = self.megers_export_modules[merger.name].branches # Returns branch names contained in the export module
        br_to_record = {}
        name_to_branch = {}
        merger_impl = None
        for br_name in br_order: # For each branch in the ordered branch set
            tup += (br_name,)
            next_branches_names = [br for br in br_order if br not in tup]
            records = self.br_name_to_gr_filter[br_name] # Group-filters associated with each branch
            index_rules = br_to_index_rule_impl[br_name] # Allen index rule associated with each branch
            index = records.index # Time index object
            if len(tup)<2: # If tuple contains only one branch, then execute the initial Merger class
                # first branch
                rules = []
                impl = MergerImpl(name, br_name, records, name_to_branch,
                                  next_branches_names, export_branches,
                                  br_to_record, index, index_rules, rules,
                                  merger_table)
                merger_impl = impl
            else:
                unimpl_rules = needed_brs[tup]
                rules = [self.get_rule_impl(rule, br_to_record) 
                         for rule in unimpl_rules]
                if br_name not in export_branches:
                    # Reject branch
                    impl = MergerRejectBranchImpl(br_name, records, 
                                        name_to_branch, next_branches_names,
                                        export_branches, br_to_record, index,
                                        index_rules, rules, merger_table)
                
                elif not next_branches_names:
                    # Last non-rejecting branch
                    impl = MergerLastBranchImpl(br_name, records, 
                                        name_to_branch, next_branches_names,
                                        export_branches, br_to_record, index,
                                        index_rules, rules, merger_table)

                else:
                    # For normal middle branches execute the MergerBranch class
                    impl = MergerBranchImpl(br_name, records, name_to_branch,
                                        next_branches_names, export_branches,
                                        br_to_record, index, index_rules,
                                        rules, merger_table)
            
            name_to_branch[br_name] = impl
        
        return merger_impl

    def get_mergers_impl(self):
        self.validate()
        mergers_impl = [self.get_merger_impl(merger)
                        for merger in self.mergers]
        
        return mergers_impl
