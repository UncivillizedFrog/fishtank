from bottle import route, run, template, redirect, request, post, static_file
import math
import sys
from apscheduler.scheduler import Scheduler
import pyfirmata
board = pyfirmata.ArduinoMega("/dev/ttyACM0")
import ConfigParser
import datetime
import sys
import time
from time import sleep
import logging;logging.basicConfig()
logging.basicConfig(level=logging.INFO,format='%(asctime)s : %(name)s : %(levelname)s : %(module)s.%(funcName)s(%(lineno)d) : %(thread)d %(threadName)s: %(message)s')

class LED:
    boardPin = board.get_pin("d:13:p")
    pwmPin1 = board.get_pin("d:2:p")
    pwmPin2 = board.get_pin("d:3:p")
    pwmPin3 = board.get_pin("d:4:p")
    pwmPin4 = board.get_pin("d:5:p")
    pwmPin5 = board.get_pin("d:6:p")
    pwmPin6 = board.get_pin("d:7:p")
    pwmPin7 = board.get_pin("d:8:p")
    pwmPin8 = board.get_pin("d:9:p")
    modding = 0
    config = ConfigParser.RawConfigParser()
    config.readfp(open('tanksettings.cfg'))
    net_Override = 0
    PWM_level = 255
    PWM_min = 30
    PWM_max = 255
    dim_Cyclesecs = 0
    dim_Ontimesecs = 900
    dim_Uptimehr = 4
    dim_Downtimehr = 5
    localTime=time.localtime()
    def __init__(self):
        self.dim_Cyclesecs=self.dim_Ontimesecs/(self.PWM_max-self.PWM_min)
        self.net_Override=0
        self.targetpin=LED.boardPin
        self.PWM_level = 255
        self.modCount = 0
        self.PWM_min = 30
        self.modding = 0
        self.sched = Scheduler()

        if LED.config.has_section('LightConfig'):
            pass
        else:
            LED.config.add_section('LightConfig')

        if LED.config.has_option('LightConfig', 'uptime') == 0:
            LED.config.set('LightConfig', 'configinit', 'true')
            LED.config.set('LightConfig', 'uptime', '7')
            LED.config.set('LightConfig', 'downtime', '23')
            LED.config.set('LightConfig', 'pwminit', '50')
            LED.config.set('LightConfig', 'cyclesecs', '900')

        if LED.config.getboolean('LightConfig', 'configinit'):
            self.dim_Uptimehr = LED.config.getint('LightConfig', 'uptime')
            self.dim_Downtimehr = LED.config.getint('LightConfig', 'downtime')
            self.PWM_min = LED.config.getint('LightConfig', 'pwminit')
            self.dim_Cyclesecs = LED.config.getint('LightConfig', 'cyclesecs')
            self.PWM_max = 255

        self.sched.add_interval_job(self.arduinoPinwriteoutAll, seconds = 1)
        self.sched.add_interval_job(self.timestatuscheck, seconds = 10)
        self.sched.add_cron_job(self.scheddimCycleUp,  hour=self.dim_Uptimehr)
        self.sched.add_cron_job(self.scheddimCycleDown,  hour=self.dim_Downtimehr)
        self.sched.start()
        self.sched.print_jobs()
    def arduinoPinwriteoutAll(self):
        self.arduinoPinwriteoutInd(self.pwmPin1,self.PWM_level)
        self.arduinoPinwriteoutInd(self.pwmPin2,self.PWM_level)
        self.arduinoPinwriteoutInd(self.pwmPin3,self.PWM_level)
        self.arduinoPinwriteoutInd(self.pwmPin4,self.PWM_level)
        self.arduinoPinwriteoutInd(self.pwmPin5,self.PWM_level)
        self.arduinoPinwriteoutInd(self.pwmPin6,self.PWM_level)
        self.arduinoPinwriteoutInd(self.pwmPin7,self.PWM_level)
        self.arduinoPinwriteoutInd(self.pwmPin8,self.PWM_level)
        print "writing %d" % (self.PWM_level)
    def arduinoPinwriteoutInd(self, outpin, PWM_Levelout):
        self.targetpin = outpin
        writeVAR = PWM_Levelout
        outpin.write(writeVAR / 255.0)

    def signalmod_PWM(self, modAmount):
        print "modding %d modAmount %d PWM_level %d pwm_min %d pwm_max %d:" % (self.modding, modAmount, self.PWM_level, self.PWM_min, self.PWM_max)
        if modAmount != 0:
            self.modding = 1
        else:
            self.modding = 0

        modTester = math.copysign(1, modAmount)
        if modTester == -1:
            if self.PWM_level <= self.PWM_min:
                self.PWM_level = self.PWM_min
                self.modding = 0
                print "quo"
            elif self.PWM_level > self.PWM_min:
                self.PWM_level += modAmount
                print "modded to %d" % (self.PWM_level)
        elif modTester == 1:
            if self.PWM_level >= self.PWM_max:
                self.PWM_level = self.PWM_max
                self.modding = 0
                print "quo"
            elif self.PWM_level < self.PWM_max:
                self.PWM_level += modAmount
                print "modded to %d" % (self.PWM_level)
    def timestatuscheck(self):
        self.localTime=time.localtime()
        if self.net_Override == 1:
            print "Overrides Engaged, pushing %d %02d:%02d" % (self.PWM_level, self.localTime.tm_hour, self.localTime.tm_min)
        elif self.modding == 0:
            if self.localTime.tm_hour < self.dim_Uptimehr:
               self. PWM_level = self.PWM_max
            elif self.localTime.tm_hour >= self.dim_Uptimehr and self.localTime.tm_hour < self.dim_Downtimehr and self.localTime.tm_min > 0:
               self. PWM_level = self.PWM_min
            elif self.localTime.tm_hour >= self.dim_Downtimehr and self.localTime.tm_min > 0:
                self.PWM_level = self.PWM_max
            print "Overrides Disengaged, pushing %d %02d:%02d" % (self.PWM_level, self.localTime.tm_hour, self.localTime.tm_min)
    def schedsignalmod_PWM(self):

        self.signalmod_PWM(self.modCount)

    def scheddimCycleUp(self):
        self.modCount = -1
        self.sched.add_interval_job(lambda: self.schedsignalmod_PWM(), seconds=self.dim_Cyclesecs, max_runs=(self.PWM_max-self.PWM_min) + 1)
        self.sched.print_jobs()

    def scheddimCycleDown(self):
        self.modCount = 1
        self.sched.add_interval_job(lambda: self.schedsignalmod_PWM(), seconds=self.dim_Cyclesecs, max_runs=(self.PWM_max-self.PWM_min) + 1)
        self.sched.print_jobs()
    def netdimCycleUp(self):
        self.modCount = -1
        self.sched.add_interval_job(lambda: self.schedsignalmod_PWM(), seconds=self.dim_Cyclesecs, max_runs=(self.PWM_max-self.PWM_min) + 1)
        self.sched.print_jobs()

    def netdimCycleDown(self):
        self.modCount = 1
        self.sched.add_interval_job(lambda: self.schedsignalmod_PWM(), seconds=self.dim_Cyclesecs, max_runs=(self.PWM_max-self.PWM_min) + 1)
        self.sched.print_jobs()


STATE=LED()





@route("/")
def default():
    return template("main_template", current_level=STATE.PWM_level, modding=STATE.modding, dim_time=STATE.dim_Ontimesecs)

@route ("/release_override")
def release_override():

    STATE.net_Override = 0
    if STATE.modding == 1:
        STATE.sched.unschedule_func(STATE.schedsignalmod_PWM)
        STATE.modding = 0
    redirect("/")

@route ("/engage_override")
def engage_override():

    STATE.net_Override = 1
    redirect("/")

@route("/turn_on")
def turn_on():
    if STATE.net_Override == 0:
        redirect("/")
        pass
    else:
        STATE.PWM_level = STATE.PWM_min
        redirect("/")

@route("/turn_off")
def turn_off():
   if STATE.net_Override == 0:
        redirect("/")
        pass
   else:
        STATE.PWM_level = STATE.PWM_max
        redirect("/")

@route("/dim_on")
def dim_on():
    if STATE.net_Override == 0:
        redirect("/")
        pass
    elif STATE.PWM_level == STATE.PWM_max:
        STATE.netdimCycleUp()
    redirect("/")

@route("/dim_off")
def dim_off():
    if STATE.net_Override == 0:
        redirect("/")
        pass
    elif STATE.PWM_level == STATE.PWM_min:
        STATE.netdimCycleDown()
    redirect("/")

@route ("/save_config")
def save_config():
    STATE.config.set('LightConfig', 'uptime', str(STATE.dim_Uptimehr))
    STATE.config.set('LightConfig', 'downtime', str(STATE.dim_Downtimehr))
    STATE.config.set('LightConfig', 'pwminit', str(STATE.PWM_min))
    STATE.config.set('LightConfig', 'cyclesecs', str(STATE.dim_Ontimesecs))
    with open('tanksettings.cfg', 'wb') as configfile:
        STATE.config.write(configfile)
    redirect ("/")

@post("/set_dim")
def set_dim():
    print request.forms.get("dim_time")
    STATE.dim_Ontimesecs = int(request.forms.get("dim_time"))
    STATE.dim_Cyclesecs = float(STATE.dim_Ontimesecs)/(STATE.PWM_max - STATE.PWM_min)
    redirect("/")

@post ("/set_brightness")
def set_brightness():
        STATE.PWM_min = int(request.forms.get("pwm_min"))
        redirect("/")

@post ("/set_uptime")
def set_uptime():
    STATE.sched.unschedule_func(STATE.scheddimCycleUp)
    STATE.dim_Uptimehr = int(request.forms.get("dimup_time"))
    STATE.sched.add_cron_job(STATE.scheddimCycleUp,  hour=STATE.dim_Uptimehr)
    redirect("/")

@post ("/set_downtime")
def set_downtime():
    STATE.sched.unschedule_func(STATE.scheddimCycleDown)
    STATE.dim_Downtimehr = int(request.forms.get("dimdown_time"))
    STATE.sched.add_cron_job(STATE.scheddimCycleDown, hour=STATE.dim_Downtimehr)
    redirect("/")

@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')

run(host="0.0.0.0", port=6767, debug=True)
