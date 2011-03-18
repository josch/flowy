#!/usr/bin/env python

from parser import Parser
from filter_validator import FilterValidator
from splitter_validator import SplitterValidator
from grouper_validator import GrouperValidator
from groupfilter_validator import GroupFilterValidator
from merger_validator import MergerValidator
from ungrouper_validator import UngrouperValidator
from threading import Thread
import argparse
import profiler
import time
import ply
import pickle
import sys
#profiler.profile_on()

start = time.clock()
print start

def run(args):

	#valstart_elapsed = (time.clock() - start)
    #print "Parsing and validation started:", valstart_elapsed

    p = Parser()

    p.parse(args.flwfile.read())
    if args.trace:
        p.input.name = args.trace.name
    
    #inps = get_inputs_list(p)
    #print get_input_fields_types(inps[0])
#    hdf_file = "../testFT2.h5"
#    r = pytables.FlowRecordsTable(hdf_file)
#    recordReader = record.RecordReader(r)
    f = FilterValidator(p)
#    fl = f.impl
    s = SplitterValidator(p, f)
    spl = s.impl
    

    gr = GrouperValidator(p, s)
#    grs = gr.impl

    gr_filt = GroupFilterValidator(p, gr)
    # Returns a number of group-filter instances
    # with accordance to the number of branches.
    gr_filters = gr_filt.impl

    
    mr = MergerValidator(p, gr_filt)
    mergers = mr.impl
    
    #valend_elapsed = (time.clock() - start)
    #print "Parsing and validation finished:", valend_elapsed
    
    splitter_thread = Thread(target=spl.go)
    
    gf_threads = [Thread(target=gf.go)for gf in gr_filters]

    splitter_elapsed = (time.clock() - start)
    print "Splitter time estarted:", splitter_elapsed
    splitter_thread.start()
    
    
    
    groupfil_start= (time.clock() - start)
    print "Group filter time started:", groupfil_start
    for gf_thread in gf_threads:
        gf_thread.start()
    	
    #Originally it was after gf_thread.start()
    splitter_thread.join()
    print "Splitter finished"
    
    splitter_elapsed = (time.clock() - start)
    print "Splitter time elapsed:", splitter_elapsed
    
    for gf_thread in gf_threads:
        gf_thread.join()

	groupfil_elapsed = (time.clock() - start)
    print "Group filter threads joined:", groupfil_elapsed

    merger_threads = [Thread(target=m.go()) for m in mergers]
    for merger_thread in merger_threads:
        merger_thread.start()

        
    for merger_thread in merger_threads:
        merger_thread.join()

    
    merger_elapsed = (time.clock() - start)
    print "Merger time elapsed:", merger_elapsed    
    

    ung = UngrouperValidator(p, mr)
    ungroupers = ung.impl

    ungrouper_threads = [Thread(target=u.go) for u in ungroupers]
    for ungrouper_thread in ungrouper_threads:
        ungrouper_thread.start()
    
    for ungrouper_thread in ungrouper_threads:
        ungrouper_thread.join()
        
        
#    profiler.profile_off()
#    import pickle
#    stats = profiler.get_profile_stats()
#    sorted_stats = sorted(stats.iteritems(), key=lambda a: a[1][1]/a[1][0])
#    for st in sorted_stats:
#        print st
#        print ' '
        
    print "FINISHED!"
    overall_elapsed = (time.clock() - start)
    print "Overall time elapsed:", overall_elapsed 
#    fname = mergers[0].merger_table.tuples_table.file_path
#    print fname



    import ft2hdf

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='some meaningful description here')
    parser.add_argument('-p', '--profile', action='store_true', help="turn profiling on")
    parser.add_argument('--version',       action='version', version='%(prog)s 2.0')
    parser.add_argument('--trace', type=argparse.FileType('r'), help="h5 input trace file")
    parser.add_argument('flwfile', type=argparse.FileType('r'), default=sys.stdin, help="*.flw file to evaluate")
    args = parser.parse_args()

    if args.profile:
        profiler.profile_on()

    try:
        run(args)
    except (ply.yacc.YaccError, SyntaxError) as e:
        import sys
        sys.stderr.write(str(e)+'\n')

    if args.profile:
        profiler.profile_off()
        stats = profiler.get_profile_stats()
        sorted_stats = sorted(stats.iteritems(), key=lambda a: a[1][0])
        with open('./profile_stats1', 'w') as f:
            pickle.dump(sorted_stats,f)
