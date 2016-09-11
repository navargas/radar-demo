#!/usr/bin/env python

import traceback
import signal
import curses
import time
import math
import sys

try:
    import curses
except ImportError as e:
    print "Cannot import curses. Try running 'pip install curses'"
    sys.exit(1)

# Catch sigint
def cancel(signum,frame):
    curses.endwin()
    sys.exit(0)
signal.signal(signal.SIGINT, cancel)

class Board:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.pad = curses.newpad(self.height, self.width)
    def draw(self, angle):
        angle+=90
        self.pad.erase()
        # Start at center
        curY = self.height/2
        curX = self.width/2
        while curX < self.width-1 and curY < self.height-1 and curX > 0 and curY > 0:
            self.pad.addch(int(curY), int(curX), ord('.'), curses.color_pair(1))
            # Increase by cos/sin of angle until border is reached
            curY += math.cos(math.radians(angle))
            curX += math.sin(math.radians(angle))
        self.pad.addch(self.height/2, self.width/2, ord('@'), curses.color_pair(1))
    def refresh(self):
        self.pad.refresh(0,0, 0,0, self.height-1, self.width-1)

# Entrypoint
def main():
    # Initialize curses
    stdscr = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    # Pickup default colors
    for i in range(0, curses.COLORS):
        curses.init_pair(i, i, -1);
    # Use full terminal screen size
    y, x = stdscr.getmaxyx()
    b = Board(y, x)
    angle = 0
    # Hide cursor
    curses.curs_set(0)
    curses.doupdate()
    # Raw radar speed
    speed_factor = 5
    while 1:
        # Tick sleep duration
        time.sleep(1.0/60.0)
        proper_angle = angle % 360
        b.draw(proper_angle)
        # Hemisphere does not matter at this point
        # We just need to know how far from vertical the angle is
        if proper_angle > 180:
            proper_angle -= 180
        # The radar would appear to move very quickly while near horizontal
        # and very slowly while near vertical without this adjustment.
        # Likely the result of the font aspect ratio.
        distance_from_horizontal = (90 - abs(proper_angle - 90))/90.0
        scale = speed_factor * max(distance_from_horizontal, .15)
        angle -= scale
        # Redraw pad onto window
        b.refresh()

# Reset curses on error
try:
    main()
    curses.endwin()
except Exception as e:
    curses.endwin()
    print ''.join(traceback.format_tb(sys.exc_info()[2]))
    print e
