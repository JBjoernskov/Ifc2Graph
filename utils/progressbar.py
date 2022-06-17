import sys
import math

def progressbar(current,start,stop):

    total_time = stop-start
    relative_time = current-start

    n_ticks_total = 40
    n_ticks_current = math.ceil(relative_time/total_time*n_ticks_total)
    percent_done = math.ceil(relative_time/total_time*100)

    progress_str = '|'
    for i in range(n_ticks_total):
        if n_ticks_current > i:
            progress_str += '#'
        else:
            progress_str += '-'
    
    progress_str += '| ' + str(percent_done) + '% '


    sys.stdout.write('\r\x1b[K' + progress_str)
    sys.stdout.flush()
    
    if current==stop:
        print("")