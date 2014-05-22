#!/usr/bin/python

## @file
# Contains classes MultiDofDevice, SpacemouseDevice, KeyboardMouseDevice, XBoxDevice, OldSpheronDevice and NewSpheronDevice.

# import avango-guacamole libraries
import avango
import avango.gua
import avango.script
import avango.daemon

# import framework libraries
from TrackingReader import *
from ConsoleIO import *

## Base class for the representation of an input device supplying multiple degrees of freedom.
#
# This class should not be instantiated, but concrete device reading
# classed will inherit from this one.
class MultiDofDevice(avango.script.Script):

  # output fields
  ## @var mf_dof
  # The input values of the input device.
  mf_dof = avango.MFFloat()
  mf_dof.value = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] # init 7 channels: [trans_x, trans_y, trans_z, pitch, head, roll, scale]
  
  ## @var sf_reset_trigger
  # Boolean indicating if a reset of the platform is to be triggered.
  sf_reset_trigger = avango.SFBool()
  
  ## @var sf_coupling_trigger
  # Boolean indicating if a coupling with other platforms is to be triggered.
  sf_coupling_trigger = avango.SFBool()
  
  ## @var sf_dof_trigger
  # Boolean indicating if a change of dof mode is to be triggered.
  sf_dof_trigger = avango.SFBool()

  ## @var sf_station_mat
  # Tracking position and rotation.
  sf_station_mat = avango.gua.SFMatrix4()
  sf_station_mat.value = avango.gua.make_identity_mat()

  ## Default constructor.
  def __init__(self):
    self.super(MultiDofDevice).__init__()

    ## @var input_bindings
    # List of bindings between input values / button values and events. Code form.
    self.input_bindings = []
    
    # factors for amplifying
    ## @var translation_factor
    # Factor to modify the device's translation input.
    self.translation_factor = 1.0

    ## @var rotation_factor
    # Factor to modify the device's rotation input.
    self.rotation_factor = 1.0

    # init trigger callback
    ## @var frame_trigger
    # Triggers framewise evaluation of frame_callback method
    self.frame_trigger = avango.script.nodes.Update(Callback = self.frame_callback, Active = True)
    
    
  ## Initializes a tracking reader for the device's position and rotation
  # @param TRACKING_TARGET_NAME The tracking name as chosen in daemon, None if no tracking is available.
  # @param NO_TRACKING_MAT Tracking matrix to be used if no tracking is available.
  def init_station_tracking(self, TRACKING_TARGET_NAME, NO_TRACKING_MAT):
    
    ## @var tracking_reader
    # Tracking Reader to process the tracking input of the device.
    if TRACKING_TARGET_NAME != None:
      self.tracking_reader = TrackingTargetReader()
      self.tracking_reader.my_constructor(TRACKING_TARGET_NAME)
      self.sf_station_mat.connect_from(self.tracking_reader.sf_abs_mat)
    else:
      self.tracking_reader = TrackingDefaultReader()
      self.tracking_reader.set_no_tracking_matrix(NO_TRACKING_MAT)
      self.sf_station_mat.connect_from(self.tracking_reader.sf_abs_mat)


  ## Map an input value to a certain interval.
  # @param VALUE The value to be mapped.
  # @param OFFSET The offset to be applied to VALUE, MIN and MAX.
  # @param MIN The minimum value of the old interval.
  # @param MAX The maximum value of the old interval.
  # @param NEG_THRESHOLD The negative threshold to be used.
  # @param POS_THRESHOLD The positive threshold to be used.
  def filter_channel(self, VALUE, OFFSET, MIN, MAX, NEG_THRESHOLD, POS_THRESHOLD):

    VALUE = VALUE - OFFSET
    MIN = MIN - OFFSET
    MAX = MAX - OFFSET

    #print "+", VALUE, MAX, POS_THRESHOLD
    #print "-", VALUE, MIN, NEG_THRESHOLD

    if VALUE > 0:
      _pos = MAX * POS_THRESHOLD * 0.01

      if VALUE > _pos: # above positive threshold
        VALUE = min( (VALUE - _pos) / (MAX - _pos), 1.0) # normalize interval

      else: # beneath positive threshold
        VALUE = 0

    elif VALUE < 0:
      _neg = MIN * NEG_THRESHOLD * 0.01

      if VALUE < _neg:
        VALUE = max( (VALUE - _neg) / abs(MIN - _neg), -1.0)

      else: # above negative threshold
        VALUE = 0
    
    return VALUE

  ## Sets given values as input channel filtering parameters.
  # @param INPUT_CHANNEL_PARAMETERS List on which the following values will be set.
  # @param OFFSET The offset to be applied to VALUE, MIN and MAX.
  # @param MIN The minimum value of the old interval.
  # @param MAX The maximum value of the old interval.
  # @param NEG_THRESHOLD The negative threshold to be used.
  # @param POS_THRESHOLD The positive threshold to be used.
  def set_input_channel_parameters(self, INPUT_CHANNEL_PARAMETERS, OFFSET, MIN, MAX, NEG_THRESHOLD, POS_THRESHOLD):
  
    INPUT_CHANNEL_PARAMETERS[0] = OFFSET
    INPUT_CHANNEL_PARAMETERS[1] = MIN
    INPUT_CHANNEL_PARAMETERS[2] = MAX
    INPUT_CHANNEL_PARAMETERS[3] = NEG_THRESHOLD
    INPUT_CHANNEL_PARAMETERS[4] = POS_THRESHOLD

  ## Adds an input binding to the list of bindings for this device.
  # @param INSTRUCTION The binding in code form to be set.
  def add_input_binding(self, INSTRUCTION):
  
    self.input_bindings.append(INSTRUCTION)


  ## Callback: evaluated every frame
  def frame_callback(self):
  
    self.dofs = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
  
    for _input_binding in self.input_bindings:
      try:
        eval(_input_binding)
      except:
        print_error("Error parsing input binding " + str(_input_binding), False)
    
    self.mf_dof.value = self.dofs

  ## Filters and sets the x parameter.
  # @param VALUE The value to be set.
  def set_and_filter_dof(self, ID, VALUE, OFFSET, MIN, MAX, NEG_THRESHOLD, POS_THRESHOLD):

    self.dofs[ID] += self.filter_channel(VALUE, OFFSET, MIN, MAX, NEG_THRESHOLD, POS_THRESHOLD)


  def set_dof(self, ID, VALUE):

    self.dofs[ID] += VALUE


  ## Sets the reset trigger.
  # @param VALUE The value to be set.
  def set_reset_trigger(self, VALUE):

    if VALUE != self.sf_reset_trigger.value: # only propagate changes
      self.sf_reset_trigger.value = VALUE
    
  ## Sets the coupling trigger.
  # @param VALUE The value to be set. 
  def set_coupling_trigger(self, VALUE):

    if VALUE != self.sf_coupling_trigger.value: # only propagate changes
      self.sf_coupling_trigger.value = VALUE

  ## Sets the dof trigger.
  # @param VALUE The value to be set.
  def set_dof_trigger(self, VALUE): # only propagate changes

    if VALUE != self.sf_dof_trigger.value:
      self.sf_dof_trigger.value = VALUE


## Internal representation and reader for a spacemouse device.
class SpacemouseDevice(MultiDofDevice):

  ## Custom constructor.
  # @param DEVICE_STATION The name of the input device as chosen in daemon.
  # @param NO_TRACKING_MAT The matrix to be applied as a spacemouse is not tracked.
  def my_constructor(self, DEVICE_STATION, NO_TRACKING_MAT):
  
    # init sensor
    ## @var device_sensor
    # Device sensor for the device's inputs.
    self.device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
    self.device_sensor.Station.value = DEVICE_STATION

    self.init_station_tracking(None, NO_TRACKING_MAT)

    ## @var translation_factor
    # Factor to modify the device's translation input.
    self.translation_factor = 0.1

    ## @var rotation_factor
    # Factor to modify the device's rotation input.
    self.rotation_factor = 0.75
    
    self.add_input_binding("self.set_and_filter_dof(0, self.device_sensor.Value0.value, 0.0, -0.76, 0.82, 3, 3)")
    self.add_input_binding("self.set_and_filter_dof(1, self.device_sensor.Value1.value*-1.0, 0.0, -0.7, 0.6, 3, 3)")
    self.add_input_binding("self.set_and_filter_dof(2, self.device_sensor.Value2.value, 0.0, -0.95, 0.8, 3, 3)")
    self.add_input_binding("self.set_and_filter_dof(3, self.device_sensor.Value3.value, 0.0, -0.82, 0.8, 12, 12)")
    self.add_input_binding("self.set_and_filter_dof(4, self.device_sensor.Value4.value*-1.0, 0.0, -0.5, 0.6, 12, 12)")
    self.add_input_binding("self.set_and_filter_dof(5, self.device_sensor.Value5.value, 0.0, -0.86, 0.77, 12, 12)")
    self.add_input_binding("self.set_dof(6, self.device_sensor.Button0.value*1.0)")
    self.add_input_binding("self.set_dof(6, self.device_sensor.Button1.value*-1.0)")

  ## Creates a representation of the device in the virutal world.
  # @param PLATFORM_NODE The platform node to which the avatar should be appended to.
  # @param PLATFORM_ID The platform id used for setting the group name correctly.
  def create_device_avatar(self, PLATFORM_NODE, PLATFORM_ID):

    _loader = avango.gua.nodes.GeometryLoader()

    ## @var avatar_transform
    # Scenegraph transform node for the dekstop user's table.
    self.avatar_transform = avango.gua.nodes.TransformNode(Name = 'avatar_transform')
    self.avatar_transform.Transform.connect_from(self.tracking_reader.sf_avatar_body_mat)
    PLATFORM_NODE.Children.value.append(self.avatar_transform)

    ## @var device_avatar
    # Scenegraph node representing the geometry and transformation of the device avatar.
    self.device_avatar = _loader.create_geometry_from_file('device_avatar',
                                                           'data/objects/table/table.obj',
                                                           'data/materials/Stones.gmd',
                                                           avango.gua.LoaderFlags.LOAD_MATERIALS)
    self.device_avatar.Transform.value = avango.gua.make_trans_mat(-0.8, 0.2, 0.8) * avango.gua.make_scale_mat(0.2, 0.5, 0.5)
    self.avatar_transform.Children.value.append(self.device_avatar)
    self.device_avatar.GroupNames.value = ['avatar_group_' + str(PLATFORM_ID)]


## Internal representation and reader for a globefish device.
class GlobefishDevice(MultiDofDevice):

  ## Custom constructor.
  # @param DEVICE_STATION The name of the input device as chosen in daemon.
  # @param NO_TRACKING_MAT The matrix to be applied as a spacemouse is not tracked.
  def my_constructor(self, DEVICE_STATION, NO_TRACKING_MAT):
  
    # init sensor
    ## @var device_sensor
    # Device sensor for the device's inputs.
    self.device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
    self.device_sensor.Station.value = DEVICE_STATION

    self.init_station_tracking(None, NO_TRACKING_MAT)

    ## @var translation_factor
    # Factor to modify the device's translation input.
    self.translation_factor = 0.2#0.15

    ## @var rotation_factor
    # Factor to modify the device's rotation input.
    self.rotation_factor = 10.0
    
    self.add_input_binding("self.set_and_filter_dof(0, self.device_sensor.Value0.value, 0.0, -0.6, 0.85, 0, 0)")
    self.add_input_binding("self.set_and_filter_dof(1, self.device_sensor.Value1.value*-1.0, 0.0, -0.25, 0.25, 0, 0)")
    self.add_input_binding("self.set_and_filter_dof(2, self.device_sensor.Value2.value*-1.0, 0.0, -0.15, 0.15, 0, 0)")
    self.add_input_binding("self.set_and_filter_dof(3, self.device_sensor.Value3.value*-1.0, 0.0, -512.0, 512.0, 0, 0)")
    self.add_input_binding("self.set_and_filter_dof(4, self.device_sensor.Value4.value*-1.0, 0.0, -512.0, 512.0, 0, 0)")
    self.add_input_binding("self.set_and_filter_dof(5, self.device_sensor.Value5.value, 0.0, -512.0, 512.0, 0, 0)")


  ## Creates a representation of the device in the virutal world.
  # @param PLATFORM_NODE The platform node to which the avatar should be appended to.
  # @param PLATFORM_ID The platform id used for setting the group name correctly.
  def create_device_avatar(self, PLATFORM_NODE, PLATFORM_ID):

    _loader = avango.gua.nodes.GeometryLoader()

    ## @var avatar_transform
    # Scenegraph transform node for the dekstop user's table.
    self.avatar_transform = avango.gua.nodes.TransformNode(Name = 'avatar_transform')
    self.avatar_transform.Transform.connect_from(self.tracking_reader.sf_avatar_body_mat)
    PLATFORM_NODE.Children.value.append(self.avatar_transform)

    ## @var device_avatar
    # Scenegraph node representing the geometry and transformation of the device avatar.
    self.device_avatar = _loader.create_geometry_from_file('device_avatar',
                                                           'data/objects/table/table.obj',
                                                           'data/materials/Stones.gmd',
                                                           avango.gua.LoaderFlags.LOAD_MATERIALS)
    self.device_avatar.Transform.value = avango.gua.make_trans_mat(-0.8, 0.2, 0.8) * avango.gua.make_scale_mat(0.2, 0.5, 0.5)
    self.avatar_transform.Children.value.append(self.device_avatar)
    self.device_avatar.GroupNames.value = ['avatar_group_' + str(PLATFORM_ID)]


## Internal representation and reader for a keyboard and mouse setup.
class KeyboardMouseDevice(MultiDofDevice):

  ## Custom constructor.
  # @param NO_TRACKING_MAT The matrix to be applied as a spacemouse is not tracked.
  def my_constructor(self, NO_TRACKING_MAT):
  
    _device_service = avango.daemon.DeviceService()
  
    ## @var mouse_sensor
    # Input sensor referencing the mouse connected to the computer.
    self.mouse_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = _device_service)
    self.mouse_sensor.Station.value = "device-mouse"

    ## @var keyboard_sensor
    # Input sensor referencing the keyboard connected to the computer.
    self.keyboard_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = _device_service)
    self.keyboard_sensor.Station.value = "device-keyboard0"

    self.init_station_tracking(None, NO_TRACKING_MAT)

    ## @var translation_factor
    # Factor to modify the device's translation input.
    self.translation_factor = 0.08

    ## @var rotation_factor
    # Factor to modify the device's rotation input.
    self.rotation_factor = 8.0


    self.add_input_binding("self.set_dof(0, self.keyboard_sensor.Button1.value*-1.0)")           # A
    self.add_input_binding("self.set_dof(0, self.keyboard_sensor.Button3.value)")                # D
    self.add_input_binding("self.set_dof(1, self.keyboard_sensor.Button7.value)")                # UP
    self.add_input_binding("self.set_dof(1, self.keyboard_sensor.Button8.value*-1.0)")           #  DOWN
    self.add_input_binding("self.set_dof(2, self.keyboard_sensor.Button0.value*-1.0)")           # W
    self.add_input_binding("self.set_dof(2, self.keyboard_sensor.Button2.value)")                # S
    self.add_input_binding("self.set_reset_trigger(self.keyboard_sensor.Button4.value)")         # R
    self.add_input_binding("self.set_coupling_trigger(self.keyboard_sensor.Button5.value)")      # C
    self.add_input_binding("self.set_dof_trigger(self.keyboard_sensor.Button6.value)")           # G
    self.add_input_binding("self.set_and_filter_dof(3, self.mouse_sensor.Value1.value*-1.0, 0.0, -100.0, 100.0, 0, 0)") # mouse up
    self.add_input_binding("self.set_and_filter_dof(4, self.mouse_sensor.Value0.value*-1.0, 0.0, -100.0, 100.0, 0, 0)") # mouse right
    self.add_input_binding("self.set_dof(6, self.mouse_sensor.Button0.value*-1.0)")              # left button
    self.add_input_binding("self.set_dof(6, self.mouse_sensor.Button2.value*1.0)")               # right button

  ## Creates a representation of the device in the virutal world.
  # @param PLATFORM_NODE The platform node to which the avatar should be appended to.
  # @param PLATFORM_ID The platform id used for setting the group name correctly.
  def create_device_avatar(self, PLATFORM_NODE, PLATFORM_ID):

    _loader = avango.gua.nodes.GeometryLoader()

    ## @var avatar_transform
    # Scenegraph transform node for the dekstop user's table.
    self.avatar_transform = avango.gua.nodes.TransformNode(Name = 'avatar_transform')
    self.avatar_transform.Transform.connect_from(self.tracking_reader.sf_avatar_body_mat)
    PLATFORM_NODE.Children.value.append(self.avatar_transform)

    ## @var device_avatar
    # Scenegraph node representing the geometry and transformation of the device avatar.
    self.device_avatar = _loader.create_geometry_from_file('device_avatar',
                                                           'data/objects/table/table.obj',
                                                           'data/materials/Stones.gmd',
                                                           avango.gua.LoaderFlags.LOAD_MATERIALS)
    self.device_avatar.Transform.value = avango.gua.make_trans_mat(-0.8, 0.2, 0.8) * avango.gua.make_scale_mat(0.2, 0.5, 0.5)
    self.avatar_transform.Children.value.append(self.device_avatar)
    self.device_avatar.GroupNames.value = ['avatar_group_' + str(PLATFORM_ID)]


## Internal representation and reader for a XBox controller
class XBoxDevice(MultiDofDevice):

  ## Custom constructor.
  # @param DEVICE_STATION The name of the input device as chosen in daemon.
  # @param TRACKING_TARGET_NAME The tracking name as chosen in daemon, None if no tracking is available.
  # @param NO_TRACKING_MAT Tracking matrix to be used if no tracking is available.
  def my_constructor(self, DEVICE_STATION, TRACKING_TARGET_NAME, NO_TRACKING_MAT):

    self.init_station_tracking(TRACKING_TARGET_NAME, NO_TRACKING_MAT)
    
    ## @var device_sensor
    # Device sensor for the device's inputs.
    self.device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
    self.device_sensor.Station.value = DEVICE_STATION
    
    ## @var translation_factor
    # Factor to modify the device's translation input.
    self.translation_factor = 0.1

    ## @var rotation_factor
    # Factor to modify the device's rotation input.
    self.rotation_factor = 1.2

    self.add_input_binding("self.set_and_filter_dof(0, self.device_sensor.Value0.value, 0.0, -1.0, 1.0, 15, 15)")
    self.add_input_binding("self.set_and_filter_dof(2, self.device_sensor.Value1.value, 0.0, -1.0, 1.0, 15, 15)")    
    #self.add_input_binding("self.set_dof(1, self.device_sensor.Value4.value*-1.0)")
    #self.add_input_binding("self.set_dof(1, self.device_sensor.Value5.value)")
    self.add_input_binding("self.set_and_filter_dof(3, self.device_sensor.Value3.value, 0.0, -1.0, 1.0, 15, 15)")
    self.add_input_binding("self.set_and_filter_dof(4, self.device_sensor.Value2.value*-1.0, 0.0, -1.0, 1.0, 15, 15)")
    self.add_input_binding("self.set_reset_trigger(self.device_sensor.Button0.value)")       # X
    self.add_input_binding("self.set_coupling_trigger(self.device_sensor.Button1.value)")    # B
    self.add_input_binding("self.set_dof_trigger(self.device_sensor.Button2.value)")         # A
    self.add_input_binding("self.set_dof(6, self.device_sensor.Button6.value*-1.0)")         # TL
    self.add_input_binding("self.set_dof(6, self.device_sensor.Button7.value*1.0)")          # TR

  ## Creates a representation of the device in the virutal world.
  # @param PLATFORM_NODE The platform node to which the avatar should be appended to.
  # @param PLATFORM_ID The platform id used for setting the group name correctly.
  def create_device_avatar(self, PLATFORM_NODE, PLATFORM_ID):
    pass
    
## Internal representation and reader for the old spheron
class OldSpheronDevice(MultiDofDevice):

  ## Custom constructor.
  # @param DEVICE_STATION The name of the input device as chosen in daemon.
  # @param TRACKING_TARGET_NAME The tracking name as chosen in daemon, None if no tracking is available.
  # @param NO_TRACKING_MAT Tracking matrix to be used if no tracking is available.
  def my_constructor(self, DEVICE_STATION, TRACKING_TARGET_NAME, NO_TRACKING_MAT):

    self.init_station_tracking(TRACKING_TARGET_NAME, NO_TRACKING_MAT)
    
    ## @var device_sensor
    # Device sensor for the device's inputs.
    self.device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
    self.device_sensor.Station.value = DEVICE_STATION

    ## @var button_sensor
    # Device sensor for the device's button inputs.
    self.button_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
    self.button_sensor.Station.value = "device-old-spheron-buttons"
    
    ## @var translation_factor
    # Factor to modify the device's translation input.
    self.translation_factor = 0.5

    ## @var rotation_factor
    # Factor to modify the device's rotation input.
    self.rotation_factor = 0.0

    self.add_input_binding("self.set_and_filter_dof(0, self.device_sensor.Value0.value, -0.00787377543747, -0.0134, 0.003, 5, 5)")
    self.add_input_binding("self.set_and_filter_dof(1, self.device_sensor.Value1.value*-1.0, -0.00787377543747, -0.0115, -0.003, 20, 20)")
    self.add_input_binding("self.set_and_filter_dof(2, self.device_sensor.Value2.value, -0.00787377543747, -0.015, 0.0, 5, 5)")    
    self.add_input_binding("self.set_and_filter_dof(3, self.device_sensor.Value3.value, -0.00787377543747, -0.0095, -0.006, 0, 0)")
    self.add_input_binding("self.set_and_filter_dof(4, self.device_sensor.Value4.value*-1.0, 0.00787377543747, 0.00622577592731, 0.00912503432482, 0, 0)")
    self.add_input_binding("self.set_and_filter_dof(5, self.device_sensor.Value5.value, -0.00787377543747, -0.0095, -0.006, 0, 0)")
    self.add_input_binding("self.set_reset_trigger(self.button_sensor.Button1.value)")       # middle button      
    self.add_input_binding("self.set_dof(6, self.button_sensor.Button0.value*-1.0)")              # left button
    self.add_input_binding("self.set_dof(6, self.button_sensor.Button2.value*1.0)")               # right button

  ## Creates a representation of the device in the virutal world.
  # @param PLATFORM_NODE The platform node to which the avatar should be appended to.
  # @param PLATFORM_ID The platform id used for setting the group name correctly.
  def create_device_avatar(self, PLATFORM_NODE, PLATFORM_ID):

    _loader = avango.gua.nodes.GeometryLoader()

    ## @var avatar_transform
    # Scenegraph transform node for the dekstop user's table.
    self.avatar_transform = avango.gua.nodes.TransformNode(Name = 'avatar_transform')
    self.avatar_transform.Transform.connect_from(self.tracking_reader.sf_abs_mat)
    PLATFORM_NODE.Children.value.append(self.avatar_transform)

    ## @var device_avatar
    # Scenegraph node representing the geometry and transformation of the device avatar.
    self.device_avatar = _loader.create_geometry_from_file('device_avatar',
                                                           'data/objects/spheron.obj',
                                                           'data/materials/ShadelessWhite.gmd',
                                                           avango.gua.LoaderFlags.LOAD_MATERIALS)
    self.device_avatar.Transform.value = avango.gua.make_rot_mat(90, 0, 1, 0) * avango.gua.make_scale_mat(0.16, 0.16, 0.16)
    self.avatar_transform.Children.value.append(self.device_avatar)
    self.device_avatar.GroupNames.value = ['avatar_group_' + str(PLATFORM_ID)]


## Internal representation and reader for the new spheron
class NewSpheronDevice(MultiDofDevice):

  ## Custom constructor.
  # @param DEVICE_STATION The name of the input device as chosen in daemon.
  # @param TRACKING_TARGET_NAME The tracking name as chosen in daemon, None if no tracking is available.
  # @param NO_TRACKING_MAT Tracking matrix to be used if no tracking is available.
  def my_constructor(self, DEVICE_STATION, TRACKING_TARGET_NAME, NO_TRACKING_MAT):

    self.init_station_tracking(TRACKING_TARGET_NAME, NO_TRACKING_MAT)
    
    ## @var device_sensor
    # Device sensor for the device's inputs.
    self.device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
    self.device_sensor.Station.value = DEVICE_STATION
    
    ## @var translation_factor
    # Factor to modify the device's translation input.
    self.translation_factor = 0.25

    ## @var rotation_factor
    # Factor to modify the device's rotation input.
    self.rotation_factor = 25.0


    self.add_input_binding("self.set_and_filter_dof(0, self.device_sensor.Value0.value*-1.0, 0.0, -0.98, 1.0, 0, 0)")
    self.add_input_binding("self.set_and_filter_dof(1, self.device_sensor.Value1.value, 0.0, -0.44, 0.24, 0, 0)")
    self.add_input_binding("self.set_and_filter_dof(2, self.device_sensor.Value2.value, 0.0, -1.0, 0.94, 0, 0)")    
    self.add_input_binding("self.set_and_filter_dof(3, self.device_sensor.Value3.value*-1.0, 0.0, -2048, 2048, 0, 0)")
    self.add_input_binding("self.set_and_filter_dof(4, self.device_sensor.Value4.value*-1.0, 0.0, -2048, 2048, 0, 0)")
    self.add_input_binding("self.set_and_filter_dof(4, 100 * self.device_sensor.Value6.value, 0.0, -0.6, 0.37, 0, 0)")
    self.add_input_binding("self.set_and_filter_dof(5, self.device_sensor.Value5.value, 0.0, -2048, 2048, 0, 0)")
    
    self.add_input_binding("self.set_reset_trigger(self.device_sensor.Button1.value)")       # middle button      
    self.add_input_binding("self.set_dof(6, self.device_sensor.Button0.value*-1.0)")         # left button
    self.add_input_binding("self.set_dof(6, self.device_sensor.Button2.value*1.0)")          # right button


  ## Creates a representation of the device in the virutal world.
  # @param PLATFORM_NODE The platform node to which the avatar should be appended to.
  # @param PLATFORM_ID The platform id used for setting the group name correctly.
  def create_device_avatar(self, PLATFORM_NODE, PLATFORM_ID):

    _loader = avango.gua.nodes.GeometryLoader()

    ## @var avatar_transform
    # Scenegraph transform node for the dekstop user's table.
    self.avatar_transform = avango.gua.nodes.TransformNode(Name = 'avatar_transform')
    self.avatar_transform.Transform.connect_from(self.tracking_reader.sf_abs_mat)
    PLATFORM_NODE.Children.value.append(self.avatar_transform)

    ## @var device_avatar
    # Scenegraph node representing the geometry and transformation of the device avatar.
    self.device_avatar = _loader.create_geometry_from_file('device_avatar',
                                                           'data/objects/spheron.obj',
                                                           'data/materials/ShadelessWhite.gmd',
                                                           avango.gua.LoaderFlags.LOAD_MATERIALS)
    self.device_avatar.Transform.value = avango.gua.make_rot_mat(90, 0, 1, 0) * avango.gua.make_scale_mat(0.16, 0.16, 0.16)
    self.avatar_transform.Children.value.append(self.device_avatar)
    self.device_avatar.GroupNames.value = ['avatar_group_' + str(PLATFORM_ID)]
