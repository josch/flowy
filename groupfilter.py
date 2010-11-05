from record import RecordReader
from filter import Rule
import profiler

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
        for record in self.records: # These are the grouped records according to the groupers/modules 
#			print record
            matched = False
            for or_rules in self.rules:
#                matched = False
                for rule in or_rules: # This for-loop, just extracts the rule from the list
#                    print rule
                    if rule.match(record):
#                        print rule.operation
                        matched = True
                        break
                if not matched:
                    break
            if matched:
                record.rec_id = count
                count += 1
                # Adds a record to the TimeIndex class' time interval
                # as an index value, over those times that the record
                # covers with its start-/end-time intervals.
                self.index.add(record) 
                self.groups_table.append(record)
        print "Finished group-filtering for branch " + self.branch_name
        
        self.groups_table.flush()
        
        
        	
    def __iter__(self):
        for rec in self.record_reader:
            yield rec

class AcceptGroupFilter(GroupFilter):
    def __init__(self, records, branch_name, groups_table, index):
        GroupFilter.__init__(self, None, records, branch_name, groups_table,
                             index)
# NIK commented out on Feb 08    
# This function is not used anywhere 
# in the code
#    def go(self):
#        count = 0
#        for record in self.records:
#            record.rec_id = count
#            count += 1
#            self.index.add(record)
#            self.groups_table.append(record)
#        print "Finished filtering groups for branch " + self.branch_name
#        self.groups_table.flush()
