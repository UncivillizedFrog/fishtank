USE_FIRMATA = True
USE_NANPY = False

from bottle import route, run, template, redirect, request, post, static_file
import math
import sys
from apscheduler.scheduler import Scheduler
if USE_FIRMATA:
    import pyfirmata
    board = pyfirmata.ArduinoMega("/dev/ttyACM0")
elif USE_NANPY:
    from nanpy import Arduino
    from nanpy.arduinotree import ArduinoTree
import ConfigParser
import datetime
import sys
import time
from time import sleep
import logging;logging.basicConfig()
logging.basicConfig(level=logging.INFO,format='%(asctime)s : %(name)s : %(levelname)s : %(module)s.%(funcName)s(%(lineno)d) : %(thread)d %(threadName)s: %(message)s')

##PWM TIMER SHIT
#sets all pins to 120hz
def set_timer(timer, prescale):
    a= ArduinoTree()
    mask = 7
    register = a.register.get("TCCR" + str(timer) + "B")
    register.value = (register.value & ~mask) | prescale
 
def set_timers():
    prescale = 4
    set_timer(2, prescale)
    set_timer(3, prescale)
    set_timer(4, prescale)
    set_timer(5, prescale)

##
##Pin assignments!    
if USE_FIRMATA:
    boardPin = board.get_pin("d:13:p")
    pwmPin1 = board.get_pin("d:2:p")
    pwmPin2 = board.get_pin("d:3:p")
    pwmPin3 = board.get_pin("d:4:p")
    pwmPin4 = board.get_pin("d:5:p")
    pwmPin5 = board.get_pin("d:6:p")
    pwmPin6 = board.get_pin("d:7:p")
    pwmPin7 = board.get_pin("d:8:p")
    pwmPin8 = board.get_pin("d:9:p")
    
else:
    boardPin = 13
    pwmPin1 = 2
    pwmPin2 = 3
    pwmPin3 = 4
    pwmPin4 = 5
    pwmPin5 = 6
    pwmPin6 = 7
    pwmPin7 = 8
    pwmPin8 = 9

if USE_NANPY:
    Arduino.pinMode(boardPin, Arduino.OUTPUT)
    Arduino.pinMode(pwmPin1, Arduino.OUTPUT)
    Arduino.pinMode(pwmPin2, Arduino.OUTPUT)
    Arduino.pinMode(pwmPin3, Arduino.OUTPUT)
    Arduino.pinMode(pwmPin4, Arduino.OUTPUT)
    Arduino.pinMode(pwmPin5, Arduino.OUTPUT)
    Arduino.pinMode(pwmPin6, Arduino.OUTPUT)
    Arduino.pinMode(pwmPin7, Arduino.OUTPUT)
    Arduino.pinMode(pwmPin8, Arduino.OUTPUT)
    # my version of firmata sets the pwm in the firmware
    set_timers()

targetpin = boardPin
PWM_Levelout = 0
outpin = 0
writeVAR = 0
 
def arduinoPinwriteoutAll():
   arduinoPinwriteoutInd(pwmPin1,PWM_level)
   arduinoPinwriteoutInd(pwmPin2,PWM_level)
   arduinoPinwriteoutInd(pwmPin3,PWM_level)
   arduinoPinwriteoutInd(pwmPin4,PWM_level)
   arduinoPinwriteoutInd(pwmPin5,PWM_level)
   arduinoPinwriteoutInd(pwmPin6,PWM_level)
   arduinoPinwriteoutInd(pwmPin7,PWM_level)
   arduinoPinwriteoutInd(pwmPin8,PWM_level)
def arduinoPinwriteoutInd(outpin, PWM_Levelout):
    global targetpin
    targetpin = outpin
    global writeVAR
    writeVAR = PWM_Levelout
    if USE_FIRMATA:
        outpin.write(writeVAR / 255.0)
    elif USE_NANPY:
        Arduino.analogWrite(targetpin, writeVAR)

global PWM_min
PWM_max = 255
PWM_level = 255
 
dim_Ontimesecs = 900
dim_Cyclesecs = dim_Ontimesecs/(PWM_max-PWM_min)

checked = 0

config = ConfigParser.RawConfigParser()
config.readfp(open('tanksettings.cfg'))

def configinitcheck():
    if config.has_section('LightConfig'):
        global checked
        checked = 1
        return
    else:
        config.add_section('LightConfig')
    if config.has_option('LightConfig', 'uptime') == 0:
        config.set('LightConfig', 'configinit', 'true')
        config.set('LightConfig', 'uptime', '7')
        config.set('LightConfig', 'downtime', '23')
        config.set('LightConfig', 'pwminit', '50')
        config.set('LightConfig', 'cyclesecs', '900')

configinitcheck()

def configinitset():
    global dim_Uptimehr
    global dim_Downtimehr
    global PWM_min
    global dim_Cyclesecs
    if config.getboolean('LightConfig', 'configinit'):
        dim_Uptimehr = config.getint('LightConfig', 'uptime')
        dim_Downtimehr = config.getint('LightConfig', 'downtime')
        PWM_min = config.getint('LightConfig', 'pwminit')
        dim_Cyclesecs = config.getint('LightConfig', 'cyclesecs')
    else:
        return
configinitset()


 
def signalmod_PWM(modAmount):
    global PWM_level
    global modding
    if modAmount != 0:
        modding = 1
    else:
        modding = 0
    print "modding %d modAmount %d PWM_level %d pwm_min %d pwm_max %d:" % (modding, modAmount, PWM_level, PWM_min, PWM_max)
    global modTester
    modTester = math.copysign(1, modAmount)
    if modTester == -1:
        if PWM_level <= PWM_min:
            PWM_level = PWM_min
            modding = 0
        elif PWM_level > PWM_min:
            PWM_level += (modAmount)
    elif modTester == 1:
        if PWM_level >= PWM_max:
            PWM_level = PWM_max
            modding = 0
        elif PWM_level <= PWM_max:
            PWM_level += (modAmount)

sched = Scheduler()
 
sched.add_interval_job(arduinoPinwriteoutAll, seconds = 1)

global net_Override
net_Override = 0

def timestatuscheck():
    global localTime
    localTime = time.localtime()   
    global PWM_level
    if net_Override == 1:
        print "%d %02d:%02d" % (PWM_level, localTime.tm_hour, localTime.tm_min)
        return
    elif modding == 0:
        if (localTime.tm_hour < dim_Uptimehr):
            PWM_level = PWM_max
        elif (localTime.tm_hour >= dim_Uptimehr) and (localTime.tm_hour < dim_Downtimehr) and (localTime.tm_min > 0):
            PWM_level = PWM_min
        elif (localTime.tm_hour >= dim_Downtimehr) and (localTime.tm_min > 0):
            PWM_level = PWM_max
    print "%d %02d:%02d" % (PWM_level, localTime.tm_hour, localTime.tm_min)

def schedsignalmod_PWM():
    signalmod_PWM(modAmount)

def scheddimCycleUp():
    global modAmount
    modAmount = -1
    sched.add_interval_job(schedsignalmod_PWM, seconds=dim_Cyclesecs, max_runs=(PWM_max-PWM_min) + 1)
   
def scheddimCycleDown():
    global modAmount
    modAmount = 1
    sched.add_interval_job(schedsignalmod_PWM, seconds=dim_Cyclesecs, max_runs=(PWM_max-PWM_min) + 1)

def netdimCycleUp():
    global modAmount
    modAmount = -1
    sched.add_interval_job(schedsignalmod_PWM, seconds=dim_Cyclesecs, max_runs=(PWM_max-PWM_min) + 1)
   
def netdimCycleDown():
    global modAmount
    modAmount = 1
    sched.add_interval_job(schedsignalmod_PWM, seconds=dim_Cyclesecs, max_runs=(PWM_max-PWM_min) + 1)

sched.add_cron_job(scheddimCycleUp,  hour=dim_Uptimehr)
sched.add_interval_job(timestatuscheck, seconds = 10)
sched.add_cron_job(scheddimCycleDown,  hour=dim_Downtimehr)
sched.start()
sched.print_jobs()

@route("/")
def default():
    return template("main_template", current_level=PWM_level, modding=modding, dim_time=dim_Ontimesecs)

@route ("/release_override")
def release_override():
    global modding
    global net_Override
    net_Override = 0
    if modding == 1:
        sched.unschedule_func(schedsignalmod_PWM)
        modding = 0
    redirect("/")

@route ("/engage_override")
def engage_override():
    global net_Override
    net_Override = 1
    redirect("/")

@route("/turn_on")
def turn_on():
    if net_Override == 0:
        redirect("/")
        return
    global PWM_level
    PWM_level = PWM_min
    redirect("/")

@route("/turn_off")
def turn_off():
   if net_Override == 0:
        redirect("/")
        return
   global PWM_level
   PWM_level = PWM_max
   redirect("/")

@route("/dim_on")
def dim_on():
    if net_Override == 0:
        redirect("/") 
        return
    if PWM_level == PWM_max:
        netdimCycleUp()
    redirect("/")

@route("/dim_off")
def dim_off():
    if net_Override == 0:
        redirect("/") 
        return
    if PWM_level == PWM_min:
        netdimCycleDown()
    redirect("/")

@route ("/save_config")
def save_config():
    config.set('LightConfig', 'uptime', str(dim_Uptimehr))
    config.set('LightConfig', 'downtime', str(dim_Downtimehr))
    config.set('LightConfig', 'pwminit', str(PWM_min))
    config.set('LightConfig', 'cyclesecs', str(dim_Ontimesecs))
    with open('tanksettings.cfg', 'wb') as configfile:
        config.write(configfile)
    redirect ("/")
@post("/set_dim")
def set_dim():
    global dim_Ontimesecs, dim_Cyclesecs
    print request.forms.get("dim_time")
    dim_Ontimesecs = int(request.forms.get("dim_time"))
    dim_Cyclesecs = float(dim_Ontimesecs)/(PWM_max - PWM_min)
    redirect("/")

@post ("/set_brightness")
def set_brightness():
        global PWM_min
        PWM_min = int(request.forms.get("pwm_min"))
        redirect("/")

@post ("/set_uptime")
def set_uptime():
    global dim_Uptimehr
    sched.unschedule_func(scheddimCycleUp)
    dim_Uptimehr = int(request.forms.get("dimup_time"))
    sched.add_cron_job(scheddimCycleUp,  hour=dim_Uptimehr)
    redirect("/")

@post ("/set_downtime")
def set_downtime():
    global dim_Downtimehr
    sched.unschedule_func(scheddimCycleDown)
    dim_Downtimehr = int(request.forms.get("dimdown_time"))
    sched.add_cron_job(scheddimCycleDown, hour=dim_Downtimehr)
    redirect("/")

@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')

run(host="0.0.0.0", port=6767, debug=True)
