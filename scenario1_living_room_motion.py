#!/usr/bin/python

import sys
import time
import datetime
from smartthings import *


if __name__=="__main__":
    parser = OptionParser()
    parser.add_option(
        "", "--debug",
        default = False,
        action = "store_true",
        dest = "debug",
        help = "",
    )
    parser.add_option(
        "", "--verbose",
        default = False,
        action = "store_true",
        dest = "verbose",
        help = "",
    )
    parser.add_option(
        "", "--dusk",
        default = 18.0,
        dest = "dusk_time",
        help = "24h decimal number (between 0-23.9999)"
    )
    parser.add_option(
        "", "--dawn",
        default = 6.0,
        dest = "dawn_time",
        help = "24h decimal number (between 0-23.9999)"
    )
    parser.add_option(
        "", "--delay",
        default = 1,
        dest = "delay_secs",
        help = "Main loop sleep duration (sec)"
    )

    (options, args) = parser.parse_args()

    #if not options.device_type:
    #    print >> sys.stderr, "%s: --type <%s>" % ( sys.argv[0], "|".join(dtypes))
    #    parser.print_help(sys.stderr)
    #    sys.exit(1)
        
    st = SmartThings(verbose=options.verbose)
    st.load_settings()
    st.request_endpoints()


    # Main loop
    first = True
    while True:
      if not first:
        print '. sleeping'
        time.sleep(options.delay_secs)
      first = False
      
      # Poll light
      print '. polling light'
      ds = st.request_named_device('switch', 'Living Room Lights')
      if len(ds) <= 0:
        print '! Could not find "Living Room Lights" (switch)'
        continue
      dev_light = ds[0]
      
      if dev_light['value']['switch']:
        # Poll bedroom door contact sensor
        print '. polling bedroom door sensor'
        ds = st.request_named_device('contact', 'Bedroom Door')
        if len(ds) <= 0:
          print '!Could not find "Bedroom Door" (contact)'
          continue
        dev_door = ds[0]
        
        # If door is closed, turn off lights
        if dev_door['value']['contact']:
          print '. turning light off'
          st.device_request(dev_light, {'switch': 0})
          print '. sleeping for some time before resuming main loop'
          time.sleep(20.0) # TODO: add to options
      
      else: # dev_light['value']['switch'] is False
        # Check if it's the right time to turn on lights
        now = datetime.datetime.now()
        curr_hours = now.hour + now.minute/60. + now.second/3600.
        if not (curr_hours >= options.dusk_time or curr_hours <= options.dawn_time):
          print '. there\'s still light outside'
          continue
        
        # Poll living room motion sensor
        print '. polling living room motion sensor'
        ds = st.request_named_device('motion', 'Living Room Motion')
        if len(ds) <= 0:
          print '!Could not find "Living Room Motion" (motion)'
          continue
        dev_motion = ds[0]
        
        # If motion, turn on lights
        if dev_motion['value']['motion']:
          print '. turning light on'
          st.device_request(dev_light, {'switch': 1})
