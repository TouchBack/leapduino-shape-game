#!/usr/bin/python

################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################

import Leap, sys, math, time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

import serial
import time

import random

sout = None
shape_name = None

def swrite(msg):
    global sout
    if sout:
        sout.write(msg)
    # print(msg)

class SampleListener(Leap.Listener):
    def on_init(self, controller):
        global shape_name
        self.next_update = time.time()
        self.update_interval = 1.0/30.0
        self.last_r = 0
        self.last_g = 0
        self.last_b = 0
        self.last_m = 0

        self.shape = shape_name

        self.sphere_radius = 250
        self.sphere_center = Leap.Vector(0,250+self.sphere_radius/2,0)

        self.cube_center = self.sphere_center
        self.cube_side = self.sphere_radius*2

        # print "Initialized"

    def on_connect(self, controller):
        # print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        # print "Exited"
        pass

    def send_feedback(self):
        out_str = "{r:%d,g:%d,b:%d,m1:%d,m2:%d}" % (self.last_r,
            self.last_g,self.last_b,self.last_m,self.last_m)
        swrite(out_str)

    def in_sphere(self, controller, center, radius):
        frame = controller.frame()

        if frame.hands.is_empty:
            return False

        # else
        # get just first finger for now

        finger = frame.fingers.frontmost # could do fingers[0] for first

        return center.distance_to(finger.tip_position) < radius

    def in_cube(self, controller, center, side):
        frame = controller.frame()

        if frame.hands.is_empty:
            return False

        finger = frame.fingers.frontmost
        half = side/2.0

        left = center.x - half
        right = center.x + half
        front = center.z + half # positive z is towards user
        back = center.z - half
        top = center.y + half
        bottom = center.y - half

        x = finger.tip_position.x
        y = finger.tip_position.y
        z = finger.tip_position.z
        in_x = left < x < right
        in_y = bottom < y < top
        in_z = back < z < front # see above

        return in_x and in_y and in_z

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        # print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
        #       frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

        if not frame.hands.is_empty:

            in_shape = False

            if self.shape == "sphere":
                in_shape = self.in_sphere(controller,self.sphere_center,self.sphere_radius)
            elif self.shape == "cube":
                in_shape = self.in_cube(controller,self.cube_center,self.cube_side)

            if in_shape:
                self.last_r = 0
                self.last_g = 100
                self.last_b = 0
                self.last_m = 100
            else:
                self.last_r = 100
                self.last_g = 100
                self.last_b = 0
                self.last_m = 0


        else:
            self.last_r = 0
            self.last_g = 0
            self.last_b = 0
            self.last_m = 0

        if(time.time() >= self.next_update):
            self.next_update += self.update_interval
            self.send_feedback()

        if not (frame.hands.is_empty and frame.gestures().is_empty):
            # print ""
            pass

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

def main():

    title = '''
            _                                   _                   ___ 
  ___ _   _| |__   ___    ___  _ __   ___ _ __ | |__   ___ _ __ ___/ _ \\
 / __| | | | '_ \ / _ \  / _ \| '__| / __| '_ \| '_ \ / _ \ '__/ _ \// /
| (__| |_| | |_) |  __/ | (_) | |    \__ \ |_) | | | |  __/ | |  __/ \/ 
 \___|\__,_|_.__/ \___|  \___/|_|    |___/ .__/|_| |_|\___|_|  \___| () 
                                         |_|                            
    '''

    msg_win = '''
 __   __  _____  _     _      _  _  _ _____ __   _   /
   \_/   |     | |     |      |  |  |   |   | \  |  / 
    |    |_____| |_____|      |__|__| __|__ |  \_| .  
                                                      
    '''

    msg_lose = '''
 __   __  _____  _     _              _____  _______ _______      
   \_/   |     | |     |      |      |     | |______ |______      
    |    |_____| |_____|      |_____ |_____| ______| |______ . . .
                                                                  
    '''

    art_cube = '''
                      _.-+.
                 _.-""     '.
             +:""            '.
             J \               '.
              L \             _.-+
              |  '.       _.-"   |
              J    \  _.-"       L
               L    +"          J
               +    |           |
                \   |          .+
                 \  |       .-'
                  \ |    .-'
                   \| .-'
                    +'   
    '''

    art_sphere = '''
             ::..:::::!!**               
         .............::!!**oo           
     ...................::!!**ooee       
   .......................::!!ooeeee     
   .......................::!!**ooee     
 .........................::!!**ooeeee   
 .........................::!!**ooeeee   
:.........................::!!**ooeeeeee 
........................::!!**ooooeeeeee 
:.......................::!!**ooeeeeeeee 
:.....................::!!****ooeeeeeeee 
!::................:::!!****ooeeeeeeeeee 
*!!::..........::::!!!****ooooeeeeeeeeee 
 **!!::::::::::!!!!*****ooooeeeeeeeeee   
 oo**!!!!!!!!!!*******ooooeeeeeeeeeeee   
   oooo********oooooooeeeeeeeeeeeeee     
   eeeeooooooooooeeeeeeeeeeeeeeeeeee     
     eeeeeeeeeeeeeeeeeeeeeeeeeeeee       
         eeeeeeeeeeeeeeeeeeeee           
             eeeeeeeeeeeee
    '''

    print(title)

    global sout
    global shape_name
    port_name = raw_input("Enter Arduino port name: ")
    try:
        sout = serial.Serial(port_name, 9600, timeout=0)
        print("Initializing...")
        time.sleep(3)
    except:
        print("Failed to initialize serial port; running in debug mode")
        sout = None

    valid_shapes = ["sphere","cube"]
    art = [ art_sphere, art_cube ]
    shape_name = random.choice( valid_shapes )

    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    # print "Press Enter to quit..."
    # sys.stdin.readline()

    guess = raw_input("What shape is this? CUBE... or SPHERE?\nEnter your guess: ").strip().lower()

    print( art[ valid_shapes.index( shape_name ) ] )
    if guess == shape_name:
        print( msg_win )
        print( "You got it! It's a %s!" % shape_name )
    else:
        print( msg_lose )
        print( "Sorry, nope! It's a %s, not a %s!" % (shape_name, guess) )

    # Remove the sample listener when done
    controller.remove_listener(listener)

    swrite("{r:0,g:0,b:0,m:0}")


if __name__ == "__main__":
    main()
