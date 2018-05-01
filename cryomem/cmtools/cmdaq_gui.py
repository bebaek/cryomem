"""
GUI launcher for magnetotransport DAQ for magnetic JJ research
Implement only simple functions

BB, 2016
"""

import tkinter as tk
from tkinter import filedialog
import os, platform, sys, queue, time, threading, shlex, functools
import subprocess as subp
import signal
import configparser

#def call_daq(cmd, **kwargs):
#    """Call DAQ function"""
#    print(kwargs)
#    getattr(daq_dipstick, cmd)(**kwargs)

#def iter_except(function, exception):
    #try:
        #while True:
            #yield function()
    #except exception:
        #return

class StdoutRedirector(object):
    def __init__(self, text_area):
        self.text_area = text_area
        self.autoscroll = True

    def write(self, s):
        self.text_area.insert(tk.END, s)
        if self.autoscroll == True:
            self.text_area.see(tk.END)

    def flush(self):
        #self.text_area.update_idletasks()
        pass

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.platform = platform.system()   # Windows or Linux
        self.load_config()                  # GUI configs
        self.fname_config = 'cfg_daq_dipstick.txt'
        self.msg_update_period = 10         # in millisecond
        self.pack()
        self.create_widgets()
        self.apply_config()

    def create_widgets(self):
        pad = {'padx': 1, 'pady': 2}

        # frame 1 ###########################################
        frame1 = tk.Frame(self)
        frame1.pack(fill='x', pady=2)

        # button: change directory
        b = tk.Button(frame1, width=20, text='Work directory', command=self.chdir)
        b.pack(side='left')

        # label: working directory
        self.var_cwd = tk.StringVar()
        l_cwd = tk.Label(frame1, textvariable=self.var_cwd, relief=tk.RIDGE,
                anchor='w', justify='left')
        self.show_cwd()
        self.var_cwd.set(os.getcwd())
        l_cwd.pack(side='left', expand=True, fill='both')

        # frame 2 ###########################################
        frame2 = tk.Frame(self)
        frame2.pack(fill='x', pady=2)
        
        # reset button
        self.b_reset = tk.Button(frame2, text='Reset All Aout', 
                command=self.reset)
        self.b_reset.pack(side='left')

        b = tk.Button(frame2, text='Console', command=self.open_console)
        b.pack(side='left')
        b = tk.Button(frame2, text='File Browser', command=self.open_fbrowser)
        b.pack(side='left')
        b = tk.Button(frame2, text="QUIT", fg="red", command=self.quit)
        b.pack(side='right')

        # frame 3 ###########################################
        frame3 = tk.Frame(self)
        frame3.pack(fill='x', pady=2)
        
        # frame 3: create widgets #################
        l_cmd = tk.Label(frame3, text='Command', anchor='center', width=10)

        # Command entry
        self.e_cmd = tk.Entry(frame3)#, width=80)
        self.e_cmd.bind('<Return>', self.get_cmd)

        # Output area
        # frame for labels and buttons
        frame3_out = tk.Frame(frame3, width=10)
        tk.Label(frame3_out, text='Output', anchor='center').pack()

        self.scroll = 'Man Scroll'
        self.b_scroll = tk.Button(frame3_out, text=self.scroll, 
                command=self.toggle_scroll, width=10)
        self.b_scroll.pack(fill='x')

        b_clear = tk.Button(frame3_out, text='Clear', 
                command=self.clear).pack(fill='x')

        self.b_stop = tk.Button(frame3_out, text='Stop', fg='red', 
                command=self.stop)
        self.b_stop.pack(fill='x')

        self.tb_out = tk.Text(frame3, height=35, width=80)     # text box
        sb_out = tk.Scrollbar(frame3)          # scrollbar
        sb_out.config(command=self.tb_out.yview)
        self.tb_out.config(yscrollcommand=sb_out.set)

        # redirect all stdout, stderr to output text box
        sys.stdout = StdoutRedirector(self.tb_out)
        sys.stderr = StdoutRedirector(self.tb_out)

        # Config area 
        # frame for labels and buttons
        frame3_cfg = tk.Frame(frame3)
        l_config = tk.Label(frame3_cfg, text='Config', anchor='center', 
                width=10).pack()
        b_loadconfig = tk.Button(frame3_cfg, text='Load', 
                command=self.load_newdaqconfig).pack(fill='x')
        b_saveconfig = tk.Button(frame3_cfg, text='Save', 
                command=self.save_daqconfig).pack(fill='x')
        b_clearconfig = tk.Button(frame3_cfg, text='Clear', 
                command=self.clear_daqconfig).pack(fill='x')

        # textbox
        self.tb_cfg = tk.Text(frame3, width=50)
        sb_cfg = tk.Scrollbar(frame3)          # scrollbar
        sb_cfg.config(command=self.tb_cfg.yview)
        self.tb_cfg.config(yscrollcommand=sb_cfg.set)
        #self.tb_cfg.pack(side='left', **pad)
        #sb_out.pack(side='left', fill='y', **pad)
 
        # Batch area
        # labels
        l_batch = tk.Label(frame3, text='Batch', anchor='center', width=10)
        self.var_batch = tk.StringVar()
        l_fbatch = tk.Label(frame3, textvariable=self.var_batch, 
                relief=tk.RIDGE, anchor='w', justify='left')
        self.batch = ''         # batch filename
        self.var_batch.set(self.batch)

        # frame for labels and buttons
        frame3_batch = tk.Frame(frame3, width=10)
        b_loadbatch = tk.Button(frame3_batch, text='Load',
                command=self.load_batch).pack(fill='x')
        b_savebatch = tk.Button(frame3_batch, text='Save', 
                command=self.save_batch).pack(fill='x')
        b_saveasbatch = tk.Button(frame3_batch, text='Save As', 
                command=self.saveas_batch).pack(fill='x')
        b_clearbatch = tk.Button(frame3_batch, text='Clear', 
                command=self.clear_batch).pack(fill='x')
        self.b_run_batch = tk.Button(frame3_batch, text='Run', fg='red', 
                command=self.run_batch)
        self.b_run_batch.pack(fill='x')

        # textbox
        self.tb_batch = tk.Text(frame3, height=15)     # text box
        sb_batch = tk.Scrollbar(frame3)          # scrollbar
        sb_batch.config(command=self.tb_batch.yview)
        self.tb_batch.config(yscrollcommand=sb_batch.set)
        
        # frame 3 grid ##################
        # Command
        l_cmd.grid(row=0, column=0)
        self.e_cmd.grid(row=0, column=1, columnspan=6, sticky='ew')

        # Output area
        frame3_out.grid(row=1, column=0, sticky='nsew')
        self.tb_out.grid(row=1, column=1, sticky='ns')
        sb_out.grid(row=1, column=2, sticky='ns')

        # Config area 
        frame3_cfg.grid(row=1, column=3, sticky='nsew')
        self.tb_cfg.grid(row=1, column=4, sticky='ns')
        sb_cfg.grid(row=1, column=5, sticky='ns')

        # Batch area 
        l_batch.grid(row=2, column=0)
        l_fbatch.grid(row=2, column=1, sticky='ew')
        frame3_batch.grid(row=3, column=0, sticky='nsew')
        self.tb_batch.grid(row=3, column=1)
        sb_batch.grid(row=3, column=2, sticky='ns')
        
        # grid padding
        for row in range(3):
            frame3.rowconfigure(row, pad=4)
        for row in range(5):
            frame3.columnconfigure(row, pad=4)

        # initially idle state
        self.set_cmdrunning(False)
        
    def load_config(self):
        """Load custom GUI configs"""
        self.config = configparser.ConfigParser()
        self.fconfig = os.path.dirname(os.path.abspath(__file__)) + \
                '/data/cmdaq_gui.cfg'
        if os.path.exists(self.fconfig):
            try:
                self.config.read(self.fconfig)
            except:
                print('Corrupted config file: {}'.format(self.fconfig))
                print('This file will be overwritten when QUIT is clicked.\n')

    def save_config(self):
        """Save custom GUI configs"""
        self.config['Main'] = {}     # just overwrite 
        self.config['Main']['work directory'] = self.cwd
        
        wsize, wx, wy = self.master.geometry().split('+')
        self.config['Main']['window x'] = wx
        self.config['Main']['window y'] = wy

        with open(self.fconfig, 'w') as f:
            self.config.write(f)

    def quit(self):
        if self.get_cmdrunning():
            self.stop()
        self.save_config()  # save environments to gui config file
        self.master.destroy()

    def toggle_scroll(self):
        """Toggle Output textbox scroll between auto and manual"""
        if self.scroll == 'Man Scroll':
            self.scroll = 'Auto Scroll'
            sys.stdout.autoscroll = False
        else:
            self.scroll = 'Man Scroll'
            sys.stdout.autoscroll = True 

        self.b_scroll.config(text=self.scroll)

    def stop(self):
        #self.proc.terminate()      # gentler kill?
        #self.proc.kill()      
        #self.proc.stdout.close()   # not sure if this is needed
        # this was tricky
        if self.platform == 'Windows':
            subp.Popen('TASKKILL /F /PID {pid} /T'.format(pid=self.proc.pid))
            time.sleep(0.1)
            print('Subprocess killed.\n')
            self.set_cmdrunning(True)
            #self.set_daqcontrol('normal')
            #self.set_stop('disable')
        elif self.platform == 'Linux':
            #self.proc.terminate()   # doesn't work
            #self.proc.kill()
            #os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM) #doesn't work
            os.killpg(self.proc.pid, signal.SIGTERM) # works
            self.proc.wait()
            time.sleep(0.1)
            print('Subprocess killed.\n')
            self.set_cmdrunning(False)
            #self.set_daqcontrol('normal')
            #self.set_stop('disable')
        else:
            print('Unsupported: {}'.format(self.platform))

    def load_batch(self):
        fname = filedialog.askopenfilename(title='Open batch file')
        if fname != '':
            try:
                with open(fname,'r') as f:
                    self.clear_batch()
                    self.tb_batch.insert('end',f.read())
                    self.batch = fname
                    self.var_batch.set(self.batch)
                print('Batch loaded:', self.batch)
                print('Edit and save.\n')
            except:
                print('No batch loaded:\n')

    def save_batch(self):
        if self.batch != '':
            with open(self.batch, 'w') as f:
                f.write(self.tb_batch.get('1.0','end-1c'))
            print('Saved batch:', self.batch, '\n')
            #self.b_save_batch.config(state='disable')   # button state
            #self.b_run_batch.config(state='normal')
        else:
            self.saveas_batch()
    
    def saveas_batch(self):
        fname = filedialog.asksaveasfilename(title='Save batch file as', 
                initialfile=self.batch)
        if fname != '':
            with open(fname,'w') as f:
                f.write(self.tb_batch.get('1.0','end-1c'))
            self.batch = fname
            self.var_batch.set(fname)
            print('Batch saved:', fname, '\n')
        else:
            print('No batch saved:\n')

    def run_batch(self):
        self.subp_run_cmd(shlex.quote(self.batch))
    
    def clear_batch(self):
        self.tb_batch.delete('1.0', 'end')

    def load_newdaqconfig(self):
        try:
            with filedialog.askopenfile(initialfile=self.fname_config,
                title='Open config file') as f:
                self.clear_daqconfig()
                self.tb_cfg.insert('end',f.read())
            print('DAQ config loaded. Edit and save.\n')
        except:
            print('No DAQ config loaded:\n')

    def show_daqconfig(self):
        try:
            with open(self.fname_config, 'r') as f:
                self.clear_daqconfig()
                self.tb_cfg.insert('end',f.read())
            print('DAQ config loaded:', self.fname_config)
            print('Edit and save.\n')
        except:
            print('No DAQ config file exists:', self.fname_config, '\n')

    def save_daqconfig(self):
        with open(self.fname_config, 'w') as f:
            f.write(self.tb_cfg.get('1.0','end-1c'))
        print('Saved DAQ config:', self.fname_config, '\n')

    def clear_daqconfig(self):
        self.tb_cfg.delete('1.0', 'end')

    def apply_config(self):
        """Apply saved GUI config"""
        # window location
        try:
            wx = self.config['Main']['window x']
            wy = self.config['Main']['window y']
            self.master.geometry('+{}+{}'.format(wx,wy))
        except:
            print('No previous window location found.\n')

        # work directory
        try:
            os.chdir(self.config['Main']['work directory'])
            self.cwd = os.getcwd()
            self.show_cwd()
        except:
            print('No previous work directory found.\n')
            self.chdir()

        self.show_daqconfig()

    def get_cmd(self, event):
        cmd = event.widget.get()
        self.subp_run_cmd(cmd)

    def subp_run_cmd(self, cmd):
        """Run user command as shell subprocess"""
        # debug
        if cmd[0] == '!': exec(cmd[1:]); return

        # run given shell command
        print('> '+cmd)

        # this is tricky too
        q = queue.Queue()
        if self.platform == 'Windows':
            cmd2 = 'ping 127.0.0.1 -n 1 > nul & ' + cmd
            self.proc = subp.Popen(cmd2, stdout=subp.PIPE, stderr=subp.PIPE,
                    shell=True)
        elif self.platform == 'Linux':
            #cmd2 = 'exec \"sleep 0.1; ' + cmd + '\"'   # doesn't work
            #cmd2 = 'exec ' + cmd                       # not sure
            cmd2 = 'sleep 0.1; ' + cmd
            self.proc = subp.Popen(cmd2, stdout=subp.PIPE, stderr=subp.PIPE,
                    shell=True, preexec_fn=os.setsid)   # works
            #self.proc = subp.Popen(cmd, stdout=subp.PIPE, stderr=subp.PIPE,
                    #shell=True, preexec_fn=os.setpgrp) # doesn't work
            #self.proc = subp.Popen(cmd2, stdout=subp.PIPE, stderr=subp.PIPE,
                    #shell=True)
        else:
            print('Not supported platform: \"{}\"\n'.format(self.platform))
            return
        self.set_cmdrunning(True)
        #self.set_daqcontrol('disable')
        #self.set_stop('normal')
        t = threading.Thread(target=self.update_q, args=[q]).start()
        self.update_msgbox(q)
        #self.master.after(1, self.process_pipe)   # schedule pipe check

    def update_q(self, q):
        """update queue with subprocess stdio/stderr
        
        See https://gist.github.com/zed/42324397516310c86288
        """
        def readch():
            return functools.partial(self.proc.stdout.read,8)
            
        for msg in iter(self.proc.stdout.readline, b''):
            #for msg in iter(readch(), b''):
            q.put(msg)
        for msg in iter(self.proc.stderr.readline, b''):
            q.put(msg)
        time.sleep(self.msg_update_period*0.0011)
        #print('Subprocess finished. Exit status: {}\n'.format(self.proc.poll()))

        # not allowed from a different thread?
        #self.set_daqcontrol('normal')
        #self.set_stop('disable')
        
    def update_msgbox(self, q):
        """Update message box widget with q"""
        #for line in queue.deque(itertools.islice(iter_except(q.get_nowait, 
        #    queue.Empty), 10000), maxlen=1):
        #    if line == None:
        #        return
        #    else:
        #        #self.tb_out.insert('end', line)
        #        print(line.decode())
        try:
            #self.tb_out.insert('end', q.get_nowait().decode())
            #self.tb_out.see('end')
            print(q.get_nowait().decode(), end='')
        except:
            pass

        # schedule next run if needed
        pstat = self.proc.poll()
        if pstat == None or not q.empty():
            self.master.after(self.msg_update_period, self.update_msgbox, q)    
        else:
            print('Finished updating Output textbox. Proc status: ',pstat,'\n')
            self.set_cmdrunning(False)
            #self.set_daqcontrol('normal')
            #self.set_stop('disable')
            
    def pollproc(self):
        print('Subprocess status: ',self.proc.poll())

    #def process_pipe(self):
    #    if self.p.poll() is None:   # process is running
    #        #self.tb_out.insert(p.stdout.read(1).decode())
    #        print(self.p.stdout.read(1).decode(), end='', flush=True)
    #        print(self.p.stderr.read(1).decode(), end='', flush=True)
    #        self.master.after(1, self.process_pipe)   # schedule pipe check
    #    else:                       # process is not running
    #        print(self.p.stdout.read().decode(), end='', flush=True)
    #        print(self.p.stderr.read().decode(), end='', flush=True)
    #        print('Subprocess finished. Exit code:', self.p.poll(), '\n')
    #        self.set_daqstate('normal')

    def get_cmdrunning(self):
        return self.cmdrunning

    def set_cmdrunning(self, cmdrunning):
        """Enable/disable widgets depending on cmd run status"""
        self.cmdrunning = cmdrunning    # toggle state variable
        
        # enable or disable run-related buttons
        if cmdrunning:
            disable_on_run = 'disable'
            enable_on_run = 'normal'
        else:
            disable_on_run = 'normal'
            enable_on_run = 'disable'
        self.b_reset.config(state=disable_on_run)
        self.e_cmd.config(state=disable_on_run)
        self.b_run_batch.config(state=disable_on_run)
        self.b_stop.config(state=enable_on_run)

    #def set_daqcontrol(self, newstate):
    #    """set widgets for starting DAQ with 'disable' or 'normal'"""
    #    self.b_reset.config(state=newstate)
    #    self.e_cmd.config(state=newstate)
    #    self.b_run_batch.config(state=newstate)
#
#    def set_stop(self, newstate):
#        """set stop button state with 'disable' or 'normal'"""
#        self.b_stop.config(state=newstate)

    def reset(self):
        #self.subp_run_cmd('python -u -m cmdaqiv reset')
        self.subp_run_cmd('cmdaq reset')

    def show_cwd(self):
        self.cwd = os.getcwd()
        self.var_cwd.set(self.cwd)

    def chdir(self):
        newdir = filedialog.askdirectory(title='Select Working Directory')
        if newdir != '':    # from cancel button
            os.chdir(newdir)
            self.show_cwd()
            self.show_daqconfig()

    def open_console(self):
        if self.platform == 'Windows':
            subp.call('start cmd /K cmdata', cwd=os.getcwd(), shell=True)
            #subp.call('start cmd', cwd=os.getcwd(), shell=True)
            #os.system('cmd.exe')
        elif self.platform == 'Linux':
            os.system('gnome-terminal')
        else:
            print('Require linux or windows.\n')

    def open_fbrowser(self):
        if self.platform == 'Windows':
            subp.call('explorer {}'.format(self.cwd), shell=True)
            #os.system('cmd.exe')
        elif self.platform == 'Linux':
            subp.call('nautilus --browser {}'.format(shlex.quote(self.cwd)), 
                    shell=True)
        else:
            print('Require linux or windows.\n')

    def clear(self):
        self.tb_out.delete('1.0', tk.END)

   #def spawn_daq(self, cmd):
    #    """Call DAQ command in a new thread"""
    #    self.queue = queue.Queue()
    #    print('daq step 0')
    #    self.ThreadedTask(self.queue, cmd).start()   # here, spawn a new thread
    #    print('daq step 1')
    #    self.master.after(1000, self.process_queue)

    #def process_queue(self):
    #    try:
    #        msg = self.queue.get(0)
    #        
    #        # enable buttons and entry
    #        if self.b_reset['state'] is not 'disabled':
    #            newstate ='normal'
    #            self.b_reset.config(state=newstate)
    #            self.e_cmd.config(state=newstate)
    #            print(self.b_reset['state'])
    #    except queue.Empty:
    #        # disable buttons and entry
    #        if self.b_reset['state'] is not 'disabled':
    #            newstate ='disabled'
    #            self.b_reset.config(state=newstate)
    ##            self.e_cmd.config(state=newstate)
    #            print(self.b_reset['state'])
    #        self.master.after(1000, self.process_queue)

    #def get_cmd(self, event):
    #    cmd = event.widget.get()
    #    print(cmd)
    #    #os.system(cmd)
    #    #subprocess.run(["dir"])
    #    argv = ['dummy'] + cmd.split()
    #    print(argv)
    #    #cmdaqiv.app(args)
    #    self.spawn_daq(argv)

def main():
    root = tk.Tk()
    root.title('Cryomem DAQ')
    root.resizable(width=False, height=False)
    #root.iconbitmap(shlex.quote(os.path.dirname(os.path.abspath(__file__)) + '/data/py.ico'))      # method 1
    #img = tk.Image('photo', file='data/cm.gif')    # method 2
    #root.tk.call('wm', 'iconphoto', root._w, img)
    #root.iconbitmap('cm.gif')
    app = Application(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()
