import math
class Timer:
    def __init__(self,checkpoint_name):
        self.start_time = time.time()
        self.checkpoint_name = checkpoint_name

    def print_elapsed_time(self):
        total_elapsed_secs = time.time()-self.start_time
        h = math.floor(total_elapsed_secs/3600)
        m = math.floor((total_elapsed_secs-h*3600)/60)
        s = math.floor((total_elapsed_secs-h*3600-m*60))
        str1 = "\"%s\" elapsed time: %dh %dm %ds" % (self.checkpoint_name,h,m,s)
        print(str1)