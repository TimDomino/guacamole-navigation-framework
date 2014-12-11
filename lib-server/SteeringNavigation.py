#!/usr/bin/python

## @file
# Contains class SteeringNavigation.

### import avango-guacamole libraries
import avango
import avango.gua
import avango.script

### import framework libraries
from Device           import *
#from GroundFollowing  import *
#from InputMapping     import *
from Intersection       import *
from Navigation       import *
import Utilities
from scene_config import scenegraphs

### import python libraries
import math
import time

## Representation of a steering navigation controlled by a 6-DOF device. Creates the device,
# an InputMapping instance and a GroundFollowing instance.
#
# Furthermore, this class reacts on the device's button inputs and toggles the 3-DOF (realistic) / 6-DOF (unrealistic) 
# navigation mode. When switching from unrealistic to realistic mode, an animation is triggered in which the matrix
# is rotated back in an upright position (removal of pitch and roll angle).
class SteeringNavigation(Navigation):

  ### additional fields ###

  ## input fields
  
  ## @var mf_rel_input_values
  # The relative input values of the device.
  mf_rel_input_values = avango.MFFloat()
  
  ## @var sf_reset_trigger
  # Boolean field to indicate if the navigation is to be reset.
  sf_reset_trigger = avango.SFBool()

  ## @var sf_nav_mode_toggle_trigger
  # Boolean field to indicate if the change of the dof mode is to be triggered.
  sf_nav_mode_toggle_trigger = avango.SFBool()

  ## internal fields

  sf_gf_start_mat = avango.gua.SFMatrix4()
  sf_gf_start_mat.value = avango.gua.make_identity_mat()

  ## @var mf_ground_pick_result
  # Intersections of the ground following ray with the objects in the scene.
  mf_ground_pick_result = avango.gua.MFPickResult()

  '''
  ## @var sf_request_trigger
  # Boolean field to indicate if the request mechanism is to be triggered.
  sf_request_trigger = avango.SFBool()
  '''

  ## Default constructor.
  def __init__(self):
    self.super(SteeringNavigation).__init__()

  ## Custom constructor.
  # @param STARTING_MATRIX Initial position matrix of the navigation to be created.
  # @param STARTING_SCALE Start scaling of the navigation.
  # @param INPUT_DEVICE_TYPE String indicating the type of input device to be created, e.g. "XBoxController" or "OldSpheron"
  # @param INPUT_DEVICE_NAME Name of the input device sensor as chosen in daemon.
  # @param NO_TRACKING_MAT Matrix which should be applied if no tracking is available.
  # @param GROUND_FOLLOWING_SETTINGS Setting list for the GroundFollowing instance: [activated, ray_start_height]
  # @param INVERT Boolean indicating if the input values should be inverted.
  # @param TRACE_VISIBILITY_LIST A list containing visibility rules according to the DisplayGroups' visibility tags. 
  # @param DEVICE_TRACKING_NAME Name of the device's tracking target name as chosen in daemon.
  # @param IS_REQUESTABLE Boolean saying if this Navigation is a requestable one. Requestable navigations can be switched to using a special button on the device.
  # @param REQUEST_BUTTON_NUM Button number of the device's sensor which should be used for the request mechanism.
  # @param REACTS_ON_PORTAL_TRANSIT Boolean saying if this navigation is allowed to be reset by portal transitions.
  def my_constructor(
      self
    , STARTING_MATRIX
    , STARTING_SCALE
    , INPUT_DEVICE_TYPE
    , INPUT_DEVICE_NAME
    , NO_TRACKING_MAT
    , GROUND_FOLLOWING_SETTINGS
    , INVERT
    , TRACE_VISIBILITY_LIST
    , DEVICE_TRACKING_NAME = None
    , IS_REQUESTABLE = False
    , REQUEST_BUTTON_NUM = None
    , REACTS_ON_PORTAL_TRANSIT = False
    ):

    self.list_constructor(TRACE_VISIBILITY_LIST)

    ### attributes ###

    ## @var reacts_on_portal_transit
    # Boolean saying if this navigation is allowed to be reset by portal transitions.
    self.reacts_on_portal_transit = REACTS_ON_PORTAL_TRANSIT

    ## @var nav_mode
    # value to indicate if the user is navigation mode: 0 = ground-based movement (incl GF); 1 = 6DoF navigation.
    self.nav_mode = 0 

    # factors for input amplifying
    ## @var input_trans_factor
    # Factor to modify the translation input.
    self.input_trans_factor = 1.0

    ## @var input_rot_factor
    # Factor to modify the rotation input.
    self.input_rot_factor = 1.0

    ## @var min_scale
    # The minimum scaling factor that can be applied.
    self.min_scale = 0.0001

    ## @var max_scale
    # The maximum scaling factor that can be applied.
    self.max_scale = 10000.0
    
    ## @var scale_stop_duration
    # Time how long a scaling process is stopped at a fixed step in seconds.
    self.scale_stop_duration = 1.0

    ## @var invert
    # Boolean indicating if the input values should be inverted.
    self.invert = INVERT
    
    self.transition_duration = 1.5 # in seconds


    ### variables ###

    ## @var input_device_type
    # String indicating the type of input device to be created, e.g. "XBoxController" or "OldSpheron"
    self.input_device_type = INPUT_DEVICE_TYPE

    ## @var input_device_name
    # Name of the input device sensor as chosen in daemon.
    self.input_device_name = INPUT_DEVICE_NAME

    ## @var start_matrix
    # Initial position matrix of the navigation.
    self.start_matrix = STARTING_MATRIX

    ## @var start_scale
    # Initial scaling factor of the navigation.
    self.start_scale = STARTING_SCALE

    ## @var blocked
    # Boolean variable indicating if the device input is blocked (e.g. when in coupling animation)
    self.blocked = False

    ## @var scale_stop_time
    # Time at which a scaling process stopped at a fixed step.
    self.scale_stop_time = None
    
    self.transition_start_quat = None
    
    self.transition_target_quat = None
    
    self.transition_start_time = None


    ### subclasses ###
        
    # create device
    ## @var device
    # Device instance handling relative inputs of physical device.
    if self.input_device_type == "OldSpheron":
      self.device = OldSpheronDevice()
      self.device.my_constructor(INPUT_DEVICE_NAME, DEVICE_TRACKING_NAME, NO_TRACKING_MAT)
    elif self.input_device_type == "NewSpheron":
      self.device = NewSpheronDevice()
      self.device.my_constructor(INPUT_DEVICE_NAME, DEVICE_TRACKING_NAME, NO_TRACKING_MAT)
    elif self.input_device_type == "XBoxController":
      self.device = XBoxDevice()
      self.device.my_constructor(INPUT_DEVICE_NAME, DEVICE_TRACKING_NAME, NO_TRACKING_MAT)
    elif self.input_device_type == "KeyboardMouse":
      self.device = KeyboardMouseDevice()
      self.device.my_constructor(NO_TRACKING_MAT)
    elif self.input_device_type == "Spacemouse":
      self.device = SpacemouseDevice()
      self.device.my_constructor(INPUT_DEVICE_NAME, DEVICE_TRACKING_NAME, NO_TRACKING_MAT)
    elif self.input_device_type == "Globefish":
      self.device = GlobefishDevice()
      self.device.my_constructor(INPUT_DEVICE_NAME, NO_TRACKING_MAT)
        

    self.input_trans_factor = self.device.translation_factor
    self.input_rot_factor = self.device.rotation_factor
    
    
    self.bc_init_movement_traces(str(self), 100, 50.0)
    
    self.init_groundfollowing(GROUND_FOLLOWING_SETTINGS) # evtl. init ground following
    
    if self.input_device_type == "Spacemouse":
      self.set_nav_mode(1) # set to 6DoF navigation

    else:
      self.set_nav_mode(0) # set to ground-based navigation
    

    '''
    ## @var is_requestable
    # Boolean saying if this Navigation is a requestable one. Requestable navigations
    # can be switched to using a special button on the device.
    self.is_requestable = IS_REQUESTABLE

    # connect request button
    if self.is_requestable:
      exec("self.sf_request_trigger.connect_from(self.device.device_sensor.Button" + str(REQUEST_BUTTON_NUM) + ")")
    '''
    

    ## @var nav_mode_transition_trigger
    # Triggers framewise evaluation of respective callback method
    self.nav_mode_transition_trigger = avango.script.nodes.Update(Callback = self.nav_mode_transition_callback, Active = False)

    ### field connections ###
    
    self.sf_reset_trigger.connect_from(self.device.sf_reset_trigger)
    self.sf_nav_mode_toggle_trigger.connect_from(self.device.sf_dof_trigger)
    self.mf_rel_input_values.connect_from(self.device.mf_dof)
    self.sf_reference_mat.connect_from(self.device.sf_station_mat)

    self.reset() # set to start parameters


  ### functions ###

  def init_groundfollowing(self, GROUND_FOLLOWING_SETTINGS):

    _groundfollowing_flag = GROUND_FOLLOWING_SETTINGS[0]

    if _groundfollowing_flag == True:

      ### further variables
    
      ## @var falling
      # A boolean indicating if the user is currently falling. Used for fall speed computations.
      self.falling = False

      ## @var initial_fall_velocity
      # The starting velocity when the user is falling in meters per frame. Is increased the longer the falling process goes on.
      self.initial_fall_velocity = 0.0

      ## @var height_modification_factor
      # Scaling factor used for the modification of up and down vectors.
      self.height_modification_factor = 0.15 # in meter per frame

      # fall velocity in meter per frame
      ## @var fall_velocity
      # Speed when the user is falling in meters per frame.
      self.fall_velocity = self.initial_fall_velocity

      ## @var ground_pick_direction_mat
      # Direction of the ground following ray.
      self.ground_pick_direction_mat = avango.gua.make_identity_mat()

      ## @var ray_start_height
      # Starting height of the ground following ray.
      self.ray_start_height = float(GROUND_FOLLOWING_SETTINGS[1])

      # pick length in meter
      ## @var ground_pick_length
      # Length of the ground following ray.
      self.ground_pick_length = float(GROUND_FOLLOWING_SETTINGS[2])

      ## @var groundfollowing_trigger
      # Triggers framewise evaluation of respective callback method
      self.groundfollowing_trigger = avango.script.nodes.Update(Callback = self.groundfollowing_callback, Active = False)
         
      self.set_pick_direction(avango.gua.Vec3(0.0, -1.0, 0.0))
      
      _scenegraph = scenegraphs[0]
      _pick_mask = "gf_pick_group"

      self.ground_intersection = Intersection()
      self.ground_intersection.my_constructor(_scenegraph, self.sf_gf_start_mat, self.ground_pick_length, _pick_mask)
      self.mf_ground_pick_result.connect_from(self.ground_intersection.mf_pick_result)
    
    

  ## Resets the navigation's matrix to the initial value.
  def reset(self):
   
    self.bc_set_nav_mat(self.start_matrix)
    self.bc_set_nav_scale(self.start_scale)

    self.bc_clear_movement_traces() # evtl. reset movement traces


  def set_nav_mode(self, MODE):
  
    self.nav_mode = MODE
    
    if self.nav_mode == 0: # switch to ground-based movement

      self.start_ground_alignment_transition()

      if self.groundfollowing_trigger != None:
        self.groundfollowing_trigger.Active.value = True
    
    elif self.nav_mode == 1: # switch to 6DoF navigation

      if self.groundfollowing_trigger != None:
        self.groundfollowing_trigger.Active.value = False


  def start_ground_alignment_transition(self):

    _nav_mat = self.bc_get_nav_mat()

    ## @var transition_start_quat
    # Quaternion representing the start rotation of the animation
    self.transition_start_quat = _nav_mat.get_rotate()

    # remove pitch and roll from current orientation
    _nav_mat = avango.gua.make_rot_mat(math.degrees(Utilities.get_yaw(_nav_mat)), 0, 1, 0)

    ## @var transition_target_quat
    # Quaternion representing the target rotation of the animation
    self.transition_target_quat = _nav_mat.get_rotate()
    
    # calc transition duration
    _quat = (avango.gua.make_inverse_mat(avango.gua.make_rot_mat(self.transition_target_quat)) * avango.gua.make_rot_mat(self.transition_start_quat)).get_rotate()
    _angle = _quat.get_angle()

    if _angle == 0.0: # no rotation difference --> no transition necessary
      return
      
    self.transition_duration = min(_angle * 0.03, 5.0)

    self.transition_start_time = time.time()
    
    # enable transition callback
    self.nav_mode_transition_trigger.Active.value = True
  

  ## Sets the pick_direction attribute.
  # @param PICK_DIRECTION New pick direction.
  def set_pick_direction(self, PICK_DIRECTION):

    PICK_DIRECTION.normalize()
    
    _ref = avango.gua.Vec3(0.0,0.0,-1.0)
    _angle = math.degrees(math.acos(_ref.dot(PICK_DIRECTION)))
    _axis = _ref.cross(PICK_DIRECTION)

    self.ground_pick_direction_mat = avango.gua.make_rot_mat(_angle, _axis)



  ## Applies a new scaling to this input mapping.
  # @param SCALE The new scaling factor to be applied.
  def map_scale_input(self, SCALE_INPUT):
  
    if SCALE_INPUT == 0.0:
      return
  
    _old_scale = self.bc_get_nav_scale()
    _new_scale = _old_scale * (1.0 + SCALE_INPUT * 0.015)
    _new_scale = max(min(_new_scale, self.max_scale), self.min_scale)


    if self.scale_stop_duration == 0.0:
      self.bc_set_nav_scale(_new_scale) # directly apply new scale
   
      return
     
    if self.scale_stop_time != None: # in stop time intervall
    
      if (time.time() - self.scale_stop_time) > self.scale_stop_duration:
        self.scale_stop_time = None
    
      return
      
    _old_scale = round(_old_scale,6)      
    _new_scale = round(_new_scale,6)
            
    # auto pause at specific scale levels
    if (_old_scale < 1000.0 and _new_scale > 1000.0) or (_new_scale < 1000.0 and _old_scale > 1000.0):
      #print("snap 1000:1")
      _new_scale = 1000.0
      self.scale_stop_time = time.time()
      
    elif (_old_scale < 100.0 and _new_scale > 100.0) or (_new_scale < 100.0 and _old_scale > 100.0):
      #print("snap 100:1")
      _new_scale = 100.0
      self.scale_stop_time = time.time()
            
    elif (_old_scale < 10.0 and _new_scale > 10.0) or (_new_scale < 10.0 and _old_scale > 10.0):
      #print("snap 10:1")
      _new_scale = 10.0
      self.scale_stop_time = time.time()
    
    elif (_old_scale < 1.0 and _new_scale > 1.0) or (_new_scale < 1.0 and _old_scale > 1.0):
      #print("snap 1:1")
      _new_scale = 1.0
      self.scale_stop_time = time.time()

    elif (_old_scale < 0.1 and _new_scale > 0.1) or (_new_scale < 0.1 and _old_scale > 0.1):
      #print("snap 1:10")
      _new_scale = 0.1
      self.scale_stop_time = time.time()

    elif (_old_scale < 0.01 and _new_scale > 0.01) or (_new_scale < 0.01 and _old_scale > 0.01):
      #print("snap 1:100")
      _new_scale = 0.01
      self.scale_stop_time = time.time()

    elif (_old_scale < 0.001 and _new_scale > 0.001) or (_new_scale < 0.001 and _old_scale > 0.001):
      #print("snap 1:1000")
      _new_scale = 0.001
      self.scale_stop_time = time.time()

    
    '''
    # scale relative to a reference point
    _scale_center_offset = self.sf_reference_mat.value.get_translate() 

    if _scale_center_offset.length() > 0: # scale/rotation center defined
      _pos1 = _scale_center_offset * _old_scale
      _pos2 = _scale_center_offset * _new_scale

      _vec = _pos1 - _pos2

      _new_mat = self.bc_get_nav_mat() * avango.gua.make_trans_mat(_vec)
    
      self.bc_set_nav_mat(_new_mat)
    '''

    self.bc_set_nav_scale(_new_scale) # apply new scale

 
  def map_movement_input(self, X, Y, Z, RX, RY, RZ):

    _trans_vec = avango.gua.Vec3(X, Y, Z)
    _trans_input = _trans_vec.length()

    _rot_vec = avango.gua.Vec3(RX, RY, RZ)
    _rot_input = _rot_vec.length()
    
    if _trans_input == 0.0 and _rot_input == 0.0:
      return

    _rot_center = self.get_reference_center()
    _nav_mat = self.bc_get_nav_mat()    
    
    if _trans_input != 0.0: # transfer function for translation      
      _ref_rot_mat = avango.gua.make_rot_mat(_nav_mat.get_rotate())
      _ref_rot_mat = _ref_rot_mat * avango.gua.make_rot_mat(self.sf_reference_mat.value.get_rotate())
      
      _trans_vec.normalize()
      _trans_vec *= math.pow(min(_trans_input, 1.0), 3) * self.input_trans_factor * self.bc_get_nav_scale()
      _trans_vec = self.transform_vector_with_matrix(_trans_vec, _ref_rot_mat) # transform into reference orientation (e.g. input device orientation)

    if _rot_input != 0.0: # transfer function for rotation
      _rot_vec.normalize()
      _rot_vec *= math.pow(min(_rot_input, 1.0), 3) * self.input_rot_factor


    # map input
    _nav_mat = avango.gua.make_trans_mat(_trans_vec) * \
               _nav_mat * \
               avango.gua.make_trans_mat(_rot_center) * \
               avango.gua.make_rot_mat(_rot_vec.y, 0, 1, 0) * \
               avango.gua.make_rot_mat(_rot_vec.x, 1, 0, 0) * \
               avango.gua.make_rot_mat(_rot_vec.z, 0, 0, 1) * \
               avango.gua.make_trans_mat(_rot_center * -1)

    self.bc_set_nav_mat(_nav_mat)


  ## Transforms a vector using a transformation matrix.
  # @param VECTOR The vector to be transformed.
  # @param MATRIX The matrix to be applied for transformation.
  def transform_vector_with_matrix(self, VECTOR, MATRIX):

    _vec = MATRIX * VECTOR
    return avango.gua.Vec3(_vec.x, _vec.y, _vec.z)

  
  def get_reference_center(self):
  
    _center = self.sf_reference_mat.value.get_translate() * self.bc_get_nav_scale()
    return _center

  
  ### callbacks ###

  ## Evaluated when device input values change.
  @field_has_changed(mf_rel_input_values)
  def mf_rel_input_values_changed(self):
    
    if self.blocked == True:
      return

    # get input values
    _s = self.mf_rel_input_values.value[6]
    
    _x = self.mf_rel_input_values.value[0]
    _y = self.mf_rel_input_values.value[1]
    _z = self.mf_rel_input_values.value[2]

    _rx = self.mf_rel_input_values.value[3]
    _ry = self.mf_rel_input_values.value[4]
    _rz = self.mf_rel_input_values.value[5]


    # invert movement if activated
    if self.invert == True:
      _x = -_x
      _y = -_y
      _z = -_z
      _rx = -_rx
      _ry = -_ry
      _rz = -_rz

    # ground-based movement --> ignore hight input and roll/pitch input
    if self.nav_mode == 0: 
      _y = 0.0
      _rx = 0.0
      _rz = 0.0
    
    # map inputs    
    self.map_scale_input(_s)
    self.map_movement_input(_x, _y, _z, _rx, _ry, _rz)

  
  ## Evaluated when value changes.
  @field_has_changed(sf_reset_trigger)
  def sf_reset_trigger_changed(self):
  
    if self.sf_reset_trigger.value == True: # button pressed
      #print("RESET")
      self.reset()       
          

  ## Evaluated when value changes.
  @field_has_changed(sf_nav_mode_toggle_trigger)
  def sf_nav_mode_toggle_trigger_changed(self):
  
    if self.sf_nav_mode_toggle_trigger.value == True: # button pressed
      
      if self.nav_mode_transition_trigger.Active.value == False: # not in a transition process
      
        if self.nav_mode == 0: # ground-based movement
          self.set_nav_mode(1) # set to 6DoF navigation mode
          
        elif self.nav_mode == 1: # 6DoF navigation
          self.set_nav_mode(0) # set to ground-based mode


  def nav_mode_transition_callback(self):

    _time = time.time() - self.transition_start_time
    if _time < self.transition_duration: # transition in process
    
      _factor = _time / self.transition_duration
    
      _quat = self.transition_start_quat.slerp_to(self.transition_target_quat, _factor)
    
      _nav_mat = self.bc_get_nav_mat()
      
      _nav_mat = avango.gua.make_trans_mat(_nav_mat.get_translate()) * \
                  avango.gua.make_rot_mat(_quat)
    
      self.bc_set_nav_mat(_nav_mat)
    
    else: # transition finished

      # snap to exact target parameters
      _nav_mat = self.bc_get_nav_mat()
      
      _nav_mat = avango.gua.make_trans_mat(_nav_mat.get_translate()) * \
                  avango.gua.make_rot_mat(self.transition_target_quat)

      self.bc_set_nav_mat(_nav_mat)

      self.nav_mode_transition_trigger.Active.value = False # disable transition callback
    

  def groundfollowing_callback(self):
  
    if self.nav_mode_transition_trigger.Active.value == False: # not in a transition process
      _nav_mat = self.bc_get_nav_mat()
      _nav_scale = self.bc_get_nav_scale()
    
      # prepare ground following matrix
      _gf_start_pos = self.sf_reference_mat.value.get_translate()
      _gf_start_pos.y = self.ray_start_height
      _gf_start_pos = self.sf_platform_mat.value * _gf_start_pos
      self.sf_gf_start_mat.value = avango.gua.make_trans_mat(_gf_start_pos.x, _gf_start_pos.y, _gf_start_pos.z) * self.ground_pick_direction_mat

      if len(self.mf_ground_pick_result.value) > 0: # an intersection with the ground was found
    
        # get first intersection target
        _pick_result = self.mf_ground_pick_result.value[0]             
        #print(_pick_result.Object.value, _pick_result.Object.value.Name.value)

        # compare distance to ground and ray_start_height
        _distance_to_ground = _pick_result.Distance.value * self.ground_pick_length
        _difference = _distance_to_ground - (self.ray_start_height * _nav_scale)
        _difference = round(_difference, 3)

        if _difference < 0: # climb up

          # end falling when necessary
          if self.falling == True:
            self.falling = False
            self.fall_velocity = self.initial_fall_velocity 

          # move player up
          _up_vec = avango.gua.Vec3(0.0, _difference * -1.0 * self.height_modification_factor, 0.0)
          _nav_mat = avango.gua.make_trans_mat(_up_vec) * _nav_mat

          self.bc_set_nav_mat(_nav_mat)

        elif _difference > 0:
          
          if _difference > (self.ray_start_height * _nav_scale): # falling

            # make player fall down faster every frame
            self.falling = True
            self.fall_velocity = min(self.fall_velocity + 0.003, 0.2)
            
            _fall_vec = avango.gua.Vec3(0.0, -self.fall_velocity, 0.0)
            _nav_mat = avango.gua.make_trans_mat(_fall_vec) * _nav_mat

            self.bc_set_nav_mat(_nav_mat)
            
          else: # climb down
            
            # end falling when necessary
            if self.falling:
              self.falling = False
              self.fall_velocity = self.initial_fall_velocity 

            # move platform downwards
            _down_vec = avango.gua.Vec3(0.0, _difference * -1.0 * self.height_modification_factor, 0.0)
            _nav_mat = avango.gua.make_trans_mat(_down_vec) * _nav_mat
            
            self.bc_set_nav_mat(_nav_mat)

          
