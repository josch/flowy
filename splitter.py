from Queue import Queue
from Queue import Empty
import profiler

class Splitter(object):
    def __init__(self, name_to_br, filter):
        self.branches = name_to_br.values() # Returns the actual implementaion of Branches A and B, their values
        self.name_to_branch = name_to_br
        self.filter = filter
        print "Splitter initiated"
    
    def go(self):
        count = 0
        
        
    	# Exactly rec and branch are returned, since that is specified 
    	# by the 'generator' function, denoted by 'yield' inside the 
    	# __iter__ function. Every time an __iter__ is called, one tuple 
    	# of (rec, branch) is returned
        for rec, branch in self.filter:
            self.split(branch, rec)
            count = count + 1
        
        
        	
        print count
        self.ready()
           
        	    
        
    def split(self, branch_mask, record):
#        print zip(self.branches, branch_mask)
        for branch, active in zip(self.branches, branch_mask):
#            print active, branch
            if active:
                branch.put(record)
#                if branch.name == 'A': print record
#                if branch.name == 'B': print record
#    	print branch
    	
    def ready(self):
        print "Filters ready"
        for br in self.branches:
            br.ready = True
            


class Branch(Queue):
    def __init__(self, name):
        Queue.__init__(self, 0)
        self.name = name
        self.ready = False
        
    def __iter__(self):
        while(True):
            if self.empty() and self.ready:
                raise StopIteration
            try:
                record = self.get(timeout=3)
                yield record
                self.task_done()
            except Empty:
                if self.ready:
                    raise StopIteration
