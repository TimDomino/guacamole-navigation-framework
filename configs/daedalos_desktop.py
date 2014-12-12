#!/usr/bin/python

## @file
# Contains workspace, display, navigation, display group and user configuration classes to be used by the framework.

# import guacamole libraries
import avango
import avango.gua

# import framework libraries
from DisplayGroup import *
from PhysicalDisplay import *
from VirtualDisplay import *
from Workspace import Workspace
from SteeringNavigation import SteeringNavigation
from StaticNavigation import StaticNavigation

## Create Workspaces first ##
desktop_workspace = Workspace('Desktop-Workspace', avango.gua.make_trans_mat(0.0, 0.043, 0.0))

workspaces = [desktop_workspace]

## Create Navigation instances ##
trace_visibility_list_desktop_nav = {  "desktop"  : False
                                     , "portal" : False
                                     }


spacemouse_navigation = SteeringNavigation()
spacemouse_navigation.my_constructor( STARTING_MATRIX = avango.gua.make_trans_mat(0, 1.5, 20)
                                    , STARTING_SCALE = 1.0
                                    , INPUT_DEVICE_TYPE = 'Spacemouse'
                                    , INPUT_DEVICE_NAME = 'device-spacemouse'
                                    , NO_TRACKING_MAT = avango.gua.make_trans_mat(0.0, 0.0, 0.0)
                                    , GROUND_FOLLOWING_SETTINGS = [False, 0.75, 100.0]
                                    , INVERT = False
                                    , TRACE_VISIBILITY_LIST = trace_visibility_list_desktop_nav
                                    , DEVICE_TRACKING_NAME = None
                                    , REACTS_ON_PORTAL_TRANSIT = False
                                    )

## Create Display instances. ##
dell_desktop = DellMonitor()

displays = [dell_desktop]

## Create display groups ##
desktop_workspace.create_display_group( DISPLAY_LIST = [dell_desktop]
                                      , NAVIGATION_LIST = [spacemouse_navigation]
                                      , VISIBILITY_TAG = "desktop"
                                      , OFFSET_TO_WORKSPACE = avango.gua.make_trans_mat(0, 0, 0) 
                                      )


## Create users ##
avatar_visibility_table = {
                            "desktop"  : {"portal" : False}
                          , "portal" : {"desktop" : True}
                          }

desktop_workspace.create_user( VIP = False
                             , AVATAR_VISIBILITY_TABLE = avatar_visibility_table
                             , HEADTRACKING_TARGET_NAME = None
                             , NO_TRACKING_MAT = avango.gua.make_trans_mat(0.0, 0.0, 0.6)
                             , EYE_DISTANCE = 0.065)


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
