import serial
import time
import math
import openpyxl
import threading 
import matplotlib.pyplot as plt
#----------------------------------------------------------------------------------------------------------

#%%----------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------
def lynxlift(h,p,r,y):        #Turn height pitch and roll into three different angles for the three servos
    if p < -25:     #Try to account for movement outside of domain restrictions.. It's not perfect
        p = -25
    if p > 25:
        p = 25
    if r < -25:
        r = -25
    if r > 25:
        r = 25
    global p0
    global p1
    global p2
    global p3
    d2r = math.pi/180.0
    r2d = 180.0/math.pi
    sp = math.sin(p*d2r)
    cp = math.cos(p*d2r)
    sr = math.sin(r*d2r)
    cr = math.cos(r*d2r)

    hm80sp = (h - 80.0*sp)
    cpm80 = (80.0*cp - 80.0)
    sumsquared = hm80sp**2 + cpm80**2
    try:
        t0 = r2d * (-math.acos((1/144)*(sumsquared - 441)/math.sqrt(sumsquared)) + math.asin(hm80sp/math.sqrt(sumsquared)))
    except:
        t0 = -1
    froot3 = 40*math.sqrt(3)
    frcrfr = (froot3*cr - froot3)
    cpsrsp = froot3*cp*sr + h + 40*sp
    frspsr = (40*cp - froot3*sp*sr - 40)
    sumsquared = frcrfr**2 + frspsr**2 + cpsrsp**2
    try:
        t1 = r2d * (-math.acos((1/144)*(sumsquared - 441)/math.sqrt(sumsquared)) + math.asin(cpsrsp/math.sqrt(sumsquared)))
    except:
        t1 = -1


    cpsrsp = (-froot3*cp*sr + h + 40*sp)
    frspsr = (-40*cp - froot3*sp*sr + 40)
    sumsquared = frcrfr**2 + frspsr**2 + cpsrsp**2
    try:
        t2 = r2d * (-math.acos((1/144)*(sumsquared - 441)/math.sqrt(sumsquared)) + math.asin(cpsrsp/math.sqrt(sumsquared)))
    except:
        t2 = -1


    p0 = int(t0 * 10)
    p1 = int(t1 * 10)
    p2 = int(t2 * 10)
    p3 = -int(y * 10)
#----------------------------------------------------------------------------------------------------------
def sendAngles():   #This function is threaded to always run in the background
    while 1:
        print('{:06d}\t'.format(int(time.time()*1000)%100000),end='')
        to_send = '{},{},{},{}\n'.format(p0,p1,p2,p3)
        print(to_send.strip())
        if p0 > 0 and p1 > 0 and p2 > 0:
            DOF.write(to_send.encode()) #Write to the arduino
        time.sleep(.050)
#----------------------------------------------------------------------------------------------------------
#Main

def lynxmpu(h):
    MPU9250 = serial.Serial()   #MPU 9250 Serial Port
    MPU9250.baudrate = 115200
    MPU9250.port = 'COM3'
    MPU9250.open()
    while(1): #Change to let the table run for longer. 
        vals = MPU9250.readline().decode().strip().split(',')   #Read the serial input, decode it from bytes to a string, strip the \n, and parse it based on where the , is.
        pitch = float(vals[0])
        roll = float(vals[1])
        yaw = float(vals[2])
        to_send = "{},{},{}\n".format(pitch,roll,yaw)
     #   measurements.write(to_send)
        lynxlift(h,pitch,roll,yaw)    #Change the 100 if trying to do a different height
        #end while
#----------------------------------------------------------------------------------------------------------

def lynxbounce():
    for i in range (0,4):
        for x in range (0,900):
            to_send = '{},{},{}\n'.format(-900+x,-900+x,-900+x)
            DOF.write(to_send.encode())
            time.sleep(.01)
        for j in range (-90,0):
            to_send = '{},{},{}\n'.format(0-x,0-x,0-x)
            DOF.write(to_send.encode())
            time.sleep(.01)
#----------------------------------------------------------------------------------------------------------
def rotate(h):
    p = 0
    r = 0
    for x in range (0,25):
        p = p + 2 * x + 1
        lynxlift(h,p/2,r/2,0)
        time.sleep(.3)
        lynxlift(h,p,r,0)
        time.sleep(.3)
        r = r + 2 * x + 1
        lynxlift(h,p/2,r/2,0)
        time.sleep(.3)
        lynxlift(h,p,r,0)
        time.sleep(.3)
        p = p - (2 * x + 2)
        lynxlift(h,p/2,r/2,0)
        time.sleep(.3)
        lynxlift(h,p,r,0)
        time.sleep(.3)
        r = r - (2 * x + 2)
        lynxlift(h,p/100,r/100,0)
        time.sleep(.3)
        lynxlift(h,p,r,0)
        time.sleep(.3)
#----------------------------------------------------------------------------------------------------------
def polarSpiralGen(b = 1, dt = 1, max = 30):
    t = 0
    while b*t < max:
        yield b*t,t
        t+=dt
    rt = t
    while b*rt >= 0:
        yield b*rt,t
        t+=dt
        rt-=dt

def spiralgen(b=1,ds=1,max=30):
    t = 0
    s = 0
    while b*t < max:
        yield b*t,t
        s+=ds
        t = 2*math.pi * math.sqrt(2*s/b)
    pt = t
    while s >= 0:
        returnt = 2*math.pi * math.sqrt(2*s/b)
        dt = pt-returnt
        pt = returnt
        t += dt
        yield b*returnt,t
        s-=ds
        

def polar2Cart(r,t):
    return r*math.cos(t),r*math.sin(t)

def generator(dt,reverse):
    b = 0.01
    t = 0
    x = y = 0
    r = 0

    while r < 30:
        r = b * t
        x = r * math.cos(t*math.pi/180)
        y = r * math.sin(t*math.pi/180)
        if not reverse:
            yield x,y
        t += dt
    t -= dt
    
    last_t = t

    while r > 0.5:
        r = b * last_t
        x = r * math.cos(t*math.pi/180)
        y = r * math.sin(t*math.pi/180)
        if reverse: 
            yield x,y
        t += dt
        last_t -= dt
 
def cartesianSpiral(b = 1, dt = 1, max = 30):
    return (polar2Cart(r,t) for r,t in spiralgen(b,dt,max))        

def circularrotate(h,dt): #This function completes the spiral at a constant speed, but it is slightly choppy
    y = threading.Thread(target = feedback)
    coords = list(cartesianSpiral(.5,.1,30))
    plt.plot(*zip(*coords))
    plt.show()
    y.start()
    for pitch,roll in coords:
         lynxlift(h,pitch,roll,0)
         time.sleep(0.050)

def circularrotate2(h,dt): #This function smoothly goes through the spiral, but not at a constant speed.
    y = threading.Thread(target = feedback)
    ls = list(generator(dt, False))
    ls2 = list(generator(dt, True))
    lynxlift(100,0,0,0)
    plt.plot([l[0] for l in ls], [l[1] for l in ls], color = 'blue')
    plt.plot([l[0] for l in ls2], [l[1] for l in ls2],color = 'orange')
    y.start()
    plt.show()
    for pitch,roll in ls + ls2:
        lynxlift(h,pitch,roll,0)
        time.sleep(0.050)
#----------------------------------------------------------------------------------------------------------
def pitchtest(h): 
    y = threading.Thread(target = feedback)
    y.start()
    while(1):   
        for x in range (-20,20,1):
            lynxlift(100,x,0,0)
            time.sleep(0.025)
            if DOF.in_waiting:
                print(DOF.readline().decode().strip())
        for i in range (20,-20,-1):
            lynxlift(100,i,0,0)
            time.sleep(0.025)
            if DOF.in_waiting:
                print(DOF.readline().decode().strip())
#----------------------------------------------------------------------------------------------------------
def pitchtest2():
    print('{:06d}\t'.format(int(time.time()*1000)%100000),end='')
    to_send = '{},{},{},{}\n'.format(300,300,300,0)
    time.sleep(.050)
    y = threading.Thread(target = feedback)
    y.start()
    while True:
        for i in range (100,700,5):
            time.sleep(0.025)
            to_send = '{},{},{},{}\n'.format(i,300,300,0)
            DOF.write(to_send.encode())
        for i in range (700,100,-5):
            time.sleep(0.025)
            to_send = '{},{},{},{}\n'.format(i,300,300,0)
            DOF.write(to_send.encode())


#----------------------------------------------------------------------------------------------------------
def feedback():
    MPU9250 = serial.Serial()   #MPU 9250 Serial Port
    MPU9250.baudrate = 115200
    MPU9250.port = 'COM3'
    MPU9250.open()
    while True:
    #    time.sleep(0.25)
        vals = MPU9250.readline().decode().strip().split(',')   #Read the serial input, decode it from bytes to a string, strip the \n, and parse it based on where the , is.
        pitch = float(vals[1])
        roll = float(vals[0])
        yaw = float(vals[2])
        to_send = "{},{},\n".format(pitch,roll)
        measurements.write(to_send)





p0 = 0
p1 = 0
p2 = 0
p3 = 0
measurements = open("measurements.csv","w")
DOF = serial.Serial()       #4-DOF Table Serial Port
DOF.baudrate = 115200
DOF.port = 'COM4'
DOF.open()
#pitchtest2()
x = threading.Thread(target = sendAngles)
x.start()
#lynxmpu(100)
#rotate(100)
#pitchtest(100)
#circularrotate(100,6)
circularrotate2(100,6)

# Use exit() or Ctrl-Z plus Return to exit
# >>> [x**2 for x in range(0,12)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121]
# >>> [x**2 for x in range(0,12) if x % 2 == 0]
# [0, 4, 16, 36, 64, 100]
# >>> (x**2 for x in range(0,12) if x % 2 == 0)
# <generator object <genexpr> at 0x000001E035D21A98>
# >>> a = (x**2 for x in range(0,12) if x % 2 == 0)
# >>> a
# <generator object <genexpr> at 0x000001E035E1E8B8>
# >>> [x for x in a]
# [0, 4, 16, 36, 64, 100]
# >>> [x for x in a]
# []
# >>> sum(x**2 for x in range(0,12) if x % 2 == 0)
# 220
# >>> 
