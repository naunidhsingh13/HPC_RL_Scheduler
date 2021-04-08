import IOModule.Log_print as Log_print

__metaclass__ = type


class Cqsim_sim:

    def __init__(self, module, debug=None):
        self.myInfo = "Cqsim Sim"
        self.module = module
        self.debug = debug
        
        self.debug.line(4, " ")
        self.debug.line(4, "#")
        self.debug.debug("# "+self.myInfo, 1)
        self.debug.line(4, "#")
        
        self.event_seq = []
        self.current_event = None
        #obsolete
        self.job_num = len(self.module['job'].job_info())
        self.currentTime = 0
        #obsolete
        self.read_job_buf_size = 100
        self.read_job_pointer = 0  # next position in job list
        self.previous_read_job_time = -1  # lastest read job submit time

        self.reserved_job = False

        self.debug.line(4)
        for module_name in self.module:
            temp_name = self.module[module_name].myInfo
            self.debug.debug(temp_name+" ................... Load",4)
            self.debug.line(4)
        
    def reset_sim(self, module=None, debug=None):

        if module:
            self.module = module
        if debug:
            self.debug = debug

        self.event_seq = []

        self.current_event = None
        #obsolete
        self.job_num = len(self.module['job'].job_info())
        self.currentTime = 0
        #obsolete
        self.read_job_buf_size = 100
        self.read_job_pointer = 0
        self.previous_read_job_time = -1
        
    def cqsim_sim(self):

        self.import_submit_events()
        done = self.scan_event()
        # self.print_result()
        # self.debug.debug("------ Simulating Done!", 2)
        # self.debug.debug(lvl=1)
        return done

    def import_submit_events(self):
        # fread jobs to job list and buffer to event_list dynamically
        if self.read_job_pointer < 0:
            return -1
        temp_return = self.module['job'].dyn_import_job_file()
        i = self.read_job_pointer
        # while (i < len(self.module['job'].job_info())):
        while i < self.module['job'].job_info_len():
            self.insert_event(1, self.module['job'].job_info(i)['submit'], 2, [1, i])
            self.previous_read_job_time = self.module['job'].job_info(i)['submit']
            self.debug.debug("  "+"Insert job["+"2"+"] "+str(self.module['job'].job_info(i)['submit']), 4)
            i += 1
        # print("Insert Jobs!")
        if temp_return is None or temp_return < 0 :
            self.read_job_pointer = -1
            return -1
        else:
            self.read_job_pointer = i
            return 0

    def insert_event(self, this_type, time, priority, para=None):

        temp_index = -1
        new_event = {"type": this_type, "time": time, "prio": priority, "para": para}
        if this_type == 1:
            # This is not a monitor event
            i = 0
            while i < len(self.event_seq):
                if self.event_seq[i]['time'] == time:
                    if self.event_seq[i]['prio'] > priority:
                        temp_index = i
                        break
                elif self.event_seq[i]['time'] > time:
                    temp_index = i
                    break 
                i += 1
        # elif (type == 2):
        #     temp_index = self.get_index_monitor()
            
        if temp_index >= len(self.event_seq) or temp_index == -1:
            self.event_seq.append(new_event)
        else:
            self.event_seq.insert(temp_index, new_event)
    
    def scan_event(self):
        # self.debug.debug("# "+self.myInfo+" -- scan_event",5)
        self.debug.line(2, " ")
        self.debug.line(2, "=")
        self.debug.line(2, "=")
        self.current_event = None

        # while len(self.event_seq) > 0 or self.read_job_pointer >= 0:
        # While changed to if because taking a single step
        # Changed back to while -> Now Scan Event returns done (T/F)
        while len(self.event_seq) > 0 or self.read_job_pointer >= 0:

            if len(self.event_seq) > 0:
                temp_current_event = self.event_seq[0]
                temp_currentTime = temp_current_event['time']
            else:
                temp_current_event = None
                temp_currentTime = -1

            # put this as a looped check. So that always event goes on to the next Decision requiring step.
            if (len(self.event_seq) == 0 or temp_currentTime >= self.previous_read_job_time) \
                    and self.read_job_pointer >= 0:
                self.import_submit_events()
                continue

            else:

                self.current_event = temp_current_event
                self.currentTime = temp_currentTime

                if self.current_event['type'] == 1:

                    self.debug.line(2," ")
                    self.debug.line(2,">>>")
                    self.debug.line(2,"--")
                    # print ("  Time: "+str(self.currentTime))
                    self.debug.debug("  Time: "+str(self.currentTime),2)
                    self.debug.debug("   "+str(self.current_event),2)
                    self.debug.line(2,"--")
                    self.debug.debug("  Wait: "+str(self.module['job'].wait_list()),2)
                    self.debug.debug("  Run : "+str(self.module['job'].run_list()),2)
                    self.debug.line(2,"--")
                    self.debug.debug("  Tot:" + str(self.module['node'].get_tot()) + " Idle:" +
                                     str(self.module['node'].get_idle())+" Avail:" +
                                     str(self.module['node'].get_avail())+" ", 2)
                    self.debug.line(2,"--")

                    self.event_job(self.current_event['para'])
                    return False  # Returning done as false. Hence next Step (Decision) is required.
                    # Upon returning do call - del self.event_seq[0]
                    # And also call :-
                    # self.event_job(self.current_event['para'])

                else:
                    # Delete other types of events.
                    self.sys_collect()
                    del self.event_seq[0]

        self.debug.line(2, "=")
        self.debug.line(2, "=")
        self.debug.line(2, " ")
        return True  # Returning Done as true.
    
    def event_job(self, para_in = None):
        # self.debug.debug("# "+self.myInfo+" -- event_job",5)
        """
        self.debug.line(2,"xxxxx")
        i = 0
        while (i<len(self.event_seq)):
            self.debug.debug(self.event_seq[i],2) 
            i += 1
            
        self.debug.line(2,"xxxxx")
        self.debug.line(2," ")
        self.debug.line(2," ")
        """
        if self.current_event['para'][0] == 1:
            self.submit(self.current_event['para'][1])
        elif self.current_event['para'][0] == 2:
            self.finish(self.current_event['para'][1])
    
    def submit(self, job_index):
        # self.debug.debug("# "+self.myInfo+" -- submit",5)
        self.debug.debug("[Submit]  "+str(job_index),3)
        self.module['job'].job_submit(job_index)
        return
    
    def finish(self, job_index):
        # self.debug.debug("# "+self.myInfo+" -- finish",5)
        self.debug.debug("[Finish]  "+str(job_index),3)
        self.module['node'].node_release(job_index,self.currentTime)
        self.module['job'].job_finish(job_index)
        self.module['output'].print_result(self.module['job'], job_index)
        self.module['job'].remove_job_from_dict(job_index)
        return
    
    def start(self, job_index):
        # self.debug.debug("# "+self.myInfo+" -- start",5)
        self.debug.debug("[Start]  "+str(job_index),3)
        self.module['node'].node_allocate(self.module['job'].job_info(job_index)['reqProc'], job_index,
                                          self.currentTime, self.currentTime +
                                          self.module['job'].job_info(job_index)['reqTime'])
        self.module['job'].job_start(job_index, self.currentTime)
        self.insert_event(1, self.currentTime+self.module['job'].job_info(job_index)['run'], 1, [2, job_index])
        return
    
    def score_calculate(self):

        temp_wait_list = self.module['job'].wait_list()
        wait_num = len(temp_wait_list)
        temp_wait = []
        i = 0
        while i < wait_num:
            temp_job = self.module['job'].job_info(temp_wait_list[i])
            temp_wait.append(temp_job)
            i += 1
        score_list = self.module['alg'].get_score(temp_wait, self.currentTime)
        self.module['job'].refresh_score(score_list)
        return
    
    def start_scan(self, temp_wait):
        start_max = self.module['win'].start_num()
        wait_num = len(temp_wait)
        win_count = start_max

        i = 0
        # while i < wait_num:
        if win_count >= start_max:
            win_count = 0
            temp_wait = self.start_window(temp_wait)

        temp_job = self.module['job'].job_info(temp_wait[0])

        if self.reserved_job:

            if self.module['node'].is_available(temp_job[0]):
                self.start(temp_wait[0])
                self.reserved_job = False
                return False
            else:
                temp_wait = self.module['job'].wait_list()
                self.backfill(temp_wait)
                return True
        else:

            if self.module['node'].is_available(temp_job['reqProc']):
                self.start(temp_wait[i])
                return False
            else:
                self.reserved_job = True
                return True

    def start_window(self, temp_wait_B):
        """
        :param temp_wait_B:
        :return: ???
        """

        win_size = self.module['win'].window_size()
        
        if len(temp_wait_B)>win_size:
            temp_wait_A = temp_wait_B[0:win_size]
            temp_wait_B = temp_wait_B[win_size:]
        else:
            temp_wait_A = temp_wait_B
            temp_wait_B = []

        temp_wait_info = []
        max_num = len(temp_wait_A)
        i = 0
        while i < max_num:
            temp_job = self.module['job'].job_info(temp_wait_A[i])
            temp_wait_info.append({"index": temp_wait_A[i], "proc": temp_job['reqProc'],
                                   "node": temp_job['reqProc'], "run": temp_job['run'], "score": temp_job['score']})
            i += 1 
            
        temp_wait_A = self.module['win'].start_window(temp_wait_info, {"time": self.currentTime})
        temp_wait_B[0:0] = temp_wait_A  # Prepends A to B -> B = A + B
        return temp_wait_B
    
    def backfill(self, temp_wait):
        temp_wait_info = []
        max_num = len(temp_wait)
        i = 0
        while i < max_num:
            temp_job = self.module['job'].job_info(temp_wait[i])
            temp_wait_info.append({"index": temp_wait[i], "proc": temp_job['reqProc'],
                                   "node": temp_job['reqProc'], "run": temp_job['run'], "score": temp_job['score']})
            i += 1
        backfill_list = self.module['backfill'].backfill(temp_wait_info, {'time': self.currentTime})
        # self.debug.debug("HHHHHHHHHHHHH "+str(backfill_list)+" -- backfill",2)
        if not backfill_list:
            return 0
        
        for job in backfill_list:
            self.start(job)
        return 1
    
    def sys_collect(self):
        # self.debug.debug("# "+self.myInfo+" -- sys_collect",5)

        temp_inter = 0
        if len(self.event_seq) > 1:
            temp_inter = self.event_seq[1]['time'] - self.currentTime
        temp_size = 0
        
        event_code = None
        if self.event_seq[0]['type'] == 1:
            if self.event_seq[0]['para'][0] == 1:
                event_code = 'S'
            elif self.event_seq[0]['para'][0] == 2:
                event_code = 'E'
        elif self.event_seq[0]['type'] == 2:
            event_code = 'Q'
        temp_info = self.module['info'].info_collect(time=self.currentTime, event=event_code,
                                                     uti=(self.module['node'].get_tot() -
                                                          self.module['node'].get_idle())*1.0/self.module['node'].get_tot(),
                                                     waitNum=len(self.module['job'].wait_list()),
                                                     waitSize=self.module['job'].wait_size(), inter=temp_inter)
        self.print_sys_info(temp_info)
        return
    
    def print_sys_info(self, sys_info):
        self.module['output'].print_sys_info(sys_info)
    
    def print_adapt(self, adapt_info):
        self.module['output'].print_adapt(adapt_info)
    
    def print_result(self):
        self.module['output'].print_sys_info()
        self.debug.debug(lvl=1)
        self.module['output'].print_result(self.module['job'])

