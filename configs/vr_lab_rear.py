#!/usr/bin/python

## @file
# Contains workspace, display, navigation, display group and user configuration classes to be used by the framework.

# import guacamole libraries
import avango
import avango.gua

# import framework libraries
from DisplayGroup import *
from DisplaySetups import *
from VirtualDisplay import *
from Workspace import Workspace
from SteeringNavigation import SteeringNavigation
from StaticNavigation import StaticNavigation

## Create Workspaces first ##
vr_lab_rear = Workspace('VR-Lab-Rear', avango.gua.make_trans_mat(0.0, 0.043, 0.0))

workspaces = [vr_lab_rear]

## Create Navigation instances ##
trace_visibility_list_dlp_wall_nav = {  "dlp_wall"  : False
                                      , "portal" : False
                                     }


spheron_navigation = SteeringNavigation()
spheron_navigation.my_constructor( STARTING_MATRIX = avango.gua.make_trans_mat(0, 0, 15) * \
                                                     avango.gua.make_rot_mat(0, 0, 1, 0)
                                 , STARTING_SCALE = 1.0
                                 , INPUT_DEVICE_TYPE = 'NewSpheron'
                                 , INPUT_DEVICE_NAME = 'device-new-spheron'
                                 , NO_TRACKING_MAT = avango.gua.make_trans_mat(0.0, 1.75, 1.6)
                                 , GROUND_FOLLOWING_SETTINGS = [True, 0.75, 100.0]
                                 , INVERT = False
                                 , TRACE_VISIBILITY_LIST = trace_visibility_list_dlp_wall_nav
                                 , DEVICE_TRACKING_NAME = 'tracking-new-spheron'
                                 , REACTS_ON_PORTAL_TRANSIT = True)

'''
xbox_navigation = SteeringNavigation()
xbox_navigation.my_constructor(       STARTING_MATRIX = avango.gua.make_trans_mat(0, 0, 0)
                                    , STARTING_SCALE = 1.0
                                    , INPUT_DEVICE_TYPE = 'XBoxController'
                                    , INPUT_DEVICE_NAME = 'device-xbox-1'
                                    , NO_TRACKING_MAT = avango.gua.make_trans_mat(0.0, 1.2, 0.6)
                                    , GROUND_FOLLOWING_SETTINGS = [True, 0.75, 100.0]
                                    , INVERT = False
                                    , TRACE_VISIBILITY_LIST = trace_visibility_list_dlp_wall_nav
                                    , DEVICE_TRACKING_NAME = 'tracking-xbox-1'
                                    , IS_REQUESTABLE = True
                                    , REQUEST_BUTTON_NUM = 3
                                    , REACTS_ON_PORTAL_TRANSIT = True)

spacemouse_navigation = SteeringNavigation()
spacemouse_navigation.my_constructor( STARTING_MATRIX = avango.gua.make_trans_mat(0, 0, 0)
                                    , STARTING_SCALE = 1.0
                                    , INPUT_DEVICE_TYPE = 'Spacemouse'
                                    , INPUT_DEVICE_NAME = 'device-spacemouse'
                                    , NO_TRACKING_MAT = avango.gua.make_trans_mat(0.0, 0.0, 0.0)
                                    , GROUND_FOLLOWING_SETTINGS = [False, 0.75, 100.0]
                                    , INVERT = False
                                    , TRACE_VISIBILITY_LIST = trace_visibility_list_dlp_wall_nav
                                    , DEVICE_TRACKING_NAME = 'tracking-new-spheron'
                                    , REACTS_ON_PORTAL_TRANSIT = False)
'''

## Create Display instances. ##
large_powerwall = LargePowerwall()

displays = [large_powerwall]

## Create display groups ##
vr_lab_rear.create_display_group( DISPLAY_LIST = [large_powerwall]
                                , NAVIGATION_LIST = [spheron_navigation]#, xbox_navigation]
                                , VISIBILITY_TAG = "dlp_wall"
                                , OFFSET_TO_WORKSPACE = avango.gua.make_trans_mat(0, 0, 1.6) )


## Create users ##
avatar_visibility_table = {
                            "dlp_wall"  : {"portal" : False}
                          , "portal" : {"dlp_wall" : True}
                          }

vr_lab_rear.create_user( VIP = False
                       , AVATAR_VISIBILITY_TABLE = avatar_visibility_table
                       , HEADTRACKING_TARGET_NAME = 'tracking-dlp-glasses-6'
                       , EYE_DISTANCE = 0.065)

vr_lab_rear.create_user( VIP = False
                       , AVATAR_VISIBILITY_TABLE = avatar_visibility_table
                       , HEADTRACKING_TARGET_NAME = 'tracking-dlp-glasses-4'
                       , EYE_DISTANCE = 0.065)

vr_lab_rear.create_user( VIP = False
                       , AVATAR_VISIBILITY_TABLE = avatar_visibility_table
                       , HEADTRACKING_TARGET_NAME = 'tracking-dlp-glasses-3'
                       , EYE_DISTANCE = 0.065)

## Create tools ##

# visibility table
# format: A : { B : bool}
# interpretation: does display with tag A see representation of tool in displays with tag B?
tool_visibility_table = {
                          "dlp_wall"  : {"portal" : False} 
                        , "portal" : {"dlp_wall" : True, "portal" : True}
                       }

vr_lab_rear.create_ray_pointer( POINTER_TRACKING_STATION = 'tracking-dlp-pointer1' 
                              , POINTER_DEVICE_STATION = 'device-pointer1'
                              , VISIBILITY_TABLE = tool_visibility_table)

#vr_lab_rear.create_portal_cam(  CAMERA_TRACKING_STATION = 'tracking-portal-camera-32'
#                             ,  CAMERA_DEVICE_STATION = 'device-portal-camera-32'
#                             ,  VISIBILITY_TABLE = tool_visibility_table)

## Create portal navigations. ##
'''
tower_portal_1_nav = StaticNavigation()
tower_portal_1_nav.my_constructor(STATIC_ABS_MAT = avango.gua.make_trans_mat(-12.0, 17.3, -7.0)
                                , STATIC_SCALE = 1.0)

tower_portal_2_nav = StaticNavigation()
tower_portal_2_nav.my_constructor(STATIC_ABS_MAT = avango.gua.make_trans_mat(-23.0, 1.3, 21.0) * avango.gua.make_rot_mat(-90, 0, 1, 0)
                                , STATIC_SCALE = 1.0)

## Create portal displays. ##
tower_portal_1 = VirtualDisplay(ENTRY_MATRIX = avango.gua.make_trans_mat(-23.0, 1.3, 21.0) * avango.gua.make_rot_mat(90, 0, 1, 0)
                              , WIDTH = 4.0
                              , HEIGHT = 2.6)

side_portal = VirtualDisplay(ENTRY_MATRIX = avango.gua.make_trans_mat(-21.0, 1.3, 19.0)
                           , WIDTH = 4.0
                           , HEIGHT = 2.6)

tower_portal_2 = VirtualDisplay(ENTRY_MATRIX = avango.gua.make_trans_mat(-12.0, 17.3, -7.0) * avango.gua.make_rot_mat(180, 0, 1, 0)
                              , WIDTH = 4.0
                              , HEIGHT = 2.6)

## Create virtual display groups ##
tower_portal_1_dg = VirtualDisplayGroup(DISPLAY_LIST = [tower_portal_1, side_portal]
                                      , NAVIGATION_LIST = [tower_portal_1_nav]
                                      , VISIBILITY_TAG = "portal"
                                      , VIEWING_MODE = "3D"
                                      , CAMERA_MODE = "PERSPECTIVE"
                                      , NEGATIVE_PARALLAX = "False"
                                      , BORDER_MATERIAL = "data/materials/White.gmd"
                                      , TRANSITABLE = True
                                      )

tower_portal_2_dg = VirtualDisplayGroup(DISPLAY_LIST = [tower_portal_2]
                                      , NAVIGATION_LIST = [tower_portal_2_nav]
                                      , VISIBILITY_TAG = "portal"
                                      , VIEWING_MODE = "3D"
                                      , CAMERA_MODE = "PERSPECTIVE"
                                      , NEGATIVE_PARALLAX = "False"
                                      , BORDER_MATERIAL = "data/materials/White.gmd"
                                      , TRANSITABLE = True
                                      )

virtual_display_groups = [tower_portal_1_dg, tower_portal_2_dg]
'''
virtual_display_groups = []