#!/usr/bin/python

## @file
# Contains classes for special PhysicalDisplay subclasses.

# import avango-guacamole libraries
import avango
import avango.gua

# import framework libraries
from PhysicalDisplay import *

## Display configuration for the large powerwall in the VR lab.
class LargePowerwall(PhysicalDisplay):
  
  ## Default constructor.
  def __init__(self, render_mask = ""):
    PhysicalDisplay.__init__( self
                    , hostname = "kerberos"
                    , name = "large_powerwall"
                    , resolution = (1920, 1200)
                    #, displaystrings = [":0.0", ":0.1", ":0.2", ":0.3"]
                    , displaystrings = [":0.0", ":0.1", ":0.2"]
                    , size = (4.16, 2.61)
                    , transformation = avango.gua.make_trans_mat(0, 1.57, 0)
                    #, shutter_timings = [ [(0,2400), (100,2500)],
                    #                      [(3000,4600),(3100,4700)],
                    #                      [(5700,8175), (5800,8275)],
                    #                      [(8200,10700), (8300,10800)],
                    #                      [(11400,12900), (11500,13000)],
                    #                      [(14000,15800), (14100,15900)]
                    #                    ]
                    , shutter_timings = [ [(0,8175), (100,8275)],
                                          [(8200,10700), (8300,10800)],
                                          [(11400,12900), (11500,13000)],
                                          [(14000,15800), (14100,15900)]
                                        ]
                    #, shutter_values = [  [(22,44), (88,11)],
                    #                      [(22,44), (88,11)],
                    #                      [(22,44), (88,11)],
                    #                      [(22,44), (88,11)],
                    #                      [(22,44), (88,11)],
                    #                      [(22,44), (88,11)]
                    #                   ]
                    , shutter_values = [  [(22,44), (88,11)],
                                          [(22,44), (88,11)],
                                          [(22,44), (88,11)],
                                          [(22,44), (88,11)]
                                       ]
                    , max_viewing_distance = 5.0
                    , stereo = True
                    , stereomode = "SIDE_BY_SIDE"
                    , render_mask = render_mask
                    )

  ## Registers a new view at this display and returns the display string
  # and the warp matrices assigned to the new view.
  def register_view(self):
    view_num = self.num_views
    if view_num < len(self.displaystrings):
      warpmatrices = [
          "/opt/dlp-warpmatrices/dlp_6_warp_P4.warp"
        , "/opt/dlp-warpmatrices/dlp_6_warp_P5.warp"
        , "/opt/dlp-warpmatrices/dlp_6_warp_P6.warp"
        , "/opt/dlp-warpmatrices/dlp_6_warp_P4.warp"
        , "/opt/dlp-warpmatrices/dlp_6_warp_P5.warp"
        , "/opt/dlp-warpmatrices/dlp_6_warp_P6.warp"
        #  "/opt/dlp-warpmatrices/dlp_6_warp_P4.warp"
        #, "/opt/dlp-warpmatrices/dlp_6_warp_P5.warp"
        #, "/opt/dlp-warpmatrices/dlp_6_warp_P6.warp"        
        #, "/opt/dlp-warpmatrices/dlp_6_warp_P1.warp"
        #, "/opt/dlp-warpmatrices/dlp_6_warp_P2.warp"
        #, "/opt/dlp-warpmatrices/dlp_6_warp_P3.warp"
      ]
      self.num_views += 1
      return (self.displaystrings[view_num], warpmatrices)
    else:
      return None

## Display configuration for the small powerwall in the VR lab.
class SmallPowerwall(PhysicalDisplay):

  ## Default constructor.
  def __init__(self, render_mask = ""):
    PhysicalDisplay.__init__( self
                    , hostname = "pandora"
                    , name = "small_powerwall"
                    , resolution = (1920, 1200)
                    , displaystrings = [":0.0", ":0.1"]
                    , size = (3.0, 1.98)
                    , transformation = avango.gua.make_trans_mat(0, 1.42, 0)
                    , stereo = True
                    , stereomode = "SIDE_BY_SIDE"
                    , shutter_timings = [  [(100, 200, 2900, 3000), (8400, 8500, 11400, 11500)],
                                           [(2600, 2700, 5700, 5800), (11000, 11100, 14600, 14700)],
                                           [(6000, 6100, 8200, 8300), (14300, 14400, 15900, 16000)]
                                        ]
                    , shutter_values =  [  [(20, 80, 40, 10), (2, 8, 4, 1)],
                                           [(20, 80, 40, 10), (2, 8, 4, 1)],
                                           [(20, 80, 40, 10), (2, 8, 4, 1)]
                                        ]                    
                    , render_mask = render_mask
                    )

  ## Registers a new view at this display and returns the display string
  # and the warp matrices assigned to the new view.
  def register_view(self):
    view_num = self.num_views
    if view_num < 2:
      warpmatrices = [
          "/opt/lcd-warpmatrices/lcd_4_warp_P{0}.warp".format(2 * view_num + 2)
        , "/opt/lcd-warpmatrices/lcd_4_warp_P{0}.warp".format(2 * view_num + 2)
        , "/opt/lcd-warpmatrices/lcd_4_warp_P{0}.warp".format(2 * view_num + 2)

        , "/opt/lcd-warpmatrices/lcd_4_warp_P{0}.warp".format(2 * view_num + 1)
        , "/opt/lcd-warpmatrices/lcd_4_warp_P{0}.warp".format(2 * view_num + 1)
        , "/opt/lcd-warpmatrices/lcd_4_warp_P{0}.warp".format(2 * view_num + 1)
      ]
      self.num_views += 1
      return (self.displaystrings[view_num], warpmatrices)
    else:
      return None




## Display configuration for the 3D multiuser touch table in the VR lab.
class TouchTable3D(PhysicalDisplay):

  ## Custom constructor.
  # @param hostname The hostname to which this display is connected to.
  # @param name A name to be associated to that display. Will be used in XML configuration file.
  # @param resolution The display's resolution to be used.
  # @param displaystrings A list of strings on which the windows for each user will pop up.
  # @param size Physical size of the display medium in meters.
  # @param transformation A matrix specifying the display's transformation with respect to the platform coordinate system.
  def __init__(self, render_mask = ""):
    PhysicalDisplay.__init__( self
                    , hostname = "medusa"
                    , name = "touch_table_3D"
                    , resolution = (1400, 1050)
                    , displaystrings = [":0.0", ":0.1", ":0.2"] 
                    , shutter_timings = [  [(100, 200, 2900, 3000), (8400, 8500, 11400, 11500)],
                                           [(2600, 2700, 5700, 5800), (11000, 11100, 14600, 14700)],
                                           [(6000, 6100, 8200, 8300), (14300, 14400, 15900, 16000)]                                          
                                        ]

                    , shutter_values =  [  [(20, 80, 40, 10), (2, 8, 4, 1)],
                                           [(20, 80, 40, 10), (2, 8, 4, 1)],
                                           [(20, 80, 40, 10), (2, 8, 4, 1)]
                                        ]
                    , size = (1.17, 0.84)
                    , transformation = avango.gua.make_rot_mat(90.0, -1, 0, 0)
                    , max_viewing_distance = 1.0
                    , stereo = True
                    , stereomode = "SIDE_BY_SIDE"
                    , render_mask = render_mask                   
                    )

  ## Registers a new view at this display and returns the display string 
  # and the warp matrices assigned to the new view.
  def register_view(self):
    view_num = self.num_views
    if view_num < 3:
      warpmatrices = [
          "/opt/3D43-warpmatrices/3D43_warp_P4.warp"
        , "/opt/3D43-warpmatrices/3D43_warp_P5.warp"
        , "/opt/3D43-warpmatrices/3D43_warp_P6.warp"
        , "/opt/3D43-warpmatrices/3D43_warp_P1.warp"
        , "/opt/3D43-warpmatrices/3D43_warp_P2.warp"
        , "/opt/3D43-warpmatrices/3D43_warp_P3.warp"
      ]
      self.num_views += 1
      return (self.displaystrings[view_num], warpmatrices)
    else:
      return None


## Display configuration for the Samsung Stereo TV in the VR lab. 
class SamsungStereoTV(PhysicalDisplay):

  ## Default constructor.
  def __init__(self, render_mask = ""):
    PhysicalDisplay.__init__( self
                    , hostname = "apollo"
                    , name = "samsung_tv"
                    , resolution = (1920, 1080)
                    , displaystrings = [":0.0"]
                    , size = (1.235, 0.695)
                    , transformation = avango.gua.make_trans_mat(0.0,1.6,0.0) * avango.gua.make_rot_mat(-40.0,1,0,0)
                    , stereo = True
                    , stereomode = "CHECKERBOARD"
                    , render_mask = render_mask
                    )

## Display configuration for the Mitsubishi Stereo TV in the VR lab. 
class MitsubishiStereoTV(PhysicalDisplay):

  ## Default constructor.
  def __init__(self, render_mask = ""):
    PhysicalDisplay.__init__( self
                    , hostname = "demeter"
                    , name = "mitsubishi_tv"
                    , resolution = (1920, 1080)
                    , displaystrings = [":0.0"]
                    , size = (1.44, 0.81)
                    , transformation = avango.gua.make_trans_mat(0.0,1.3,0.0)
                    , stereo = True
                    , stereomode = "CHECKERBOARD"
                    , render_mask = render_mask
                    )

## Display configuration for the Dell monitors in the VR lab. 
class DellMonitor(PhysicalDisplay):

  ## Default constructor.
  def __init__(self, render_mask = ""):
    PhysicalDisplay.__init__( self
                    , hostname = "daedalos"
                    , name = "daedalos_desktop"
                    , resolution = (2560, 1440)
                    , displaystrings = [":0.0"]
                    , size = (0.595, 0.335)
                    , transformation = avango.gua.make_trans_mat(0.0, 0.0, 0.0)
                    , stereo = False
                    , render_mask = render_mask
                    )