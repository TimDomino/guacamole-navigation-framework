#!/usr/bin/python

## @file
# Contains classes Portal and PortalManager.

# import avango-guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

# import framework libraries
from ConsoleIO import *
import Tools
import hyperspace_config

# import python libraries
import time
import math

## Class to create, handle and destoy Portal instances.
class PortalManager(avango.script.Script):

  ## Default constructor.
  def __init__(self):
    self.super(PortalManager).__init__()

  ## Custom constructor.
  # @param SCENEGRAPH Reference to the scenegraph.
  # @param NAVIGATION_LIST List of all Navigation instances checked for portal updates.
  def my_constructor(self, SCENEGRAPH, NAVIGATION_LIST):

    ## @var SCENEGRAPH
    # Reference to the scenegraph.
    self.SCENEGRAPH = SCENEGRAPH

    ## @var NAVIGATION_LIST
    # List of all Navigation instances checked for portal updates.
    self.NAVIGATION_LIST = NAVIGATION_LIST

    ## @var last_teleportation_times
    # List containing the times when the last teleportation took place for a Navigation
    self.last_teleportation_times = [0.0 for i in range(len(self.NAVIGATION_LIST))]

    ## @var portal_group_node
    # Scenegraph grouping node for portals on server side.
    self.portal_group_node = avango.gua.nodes.TransformNode(Name = "portal_group")
    self.SCENEGRAPH["/net"].Children.value.append(self.portal_group_node)

    ## @var portals
    # List of current Portal instances.
    self.portals = []

    ## @var free_portals
    # List of Portal instances that are currently not coupled to a PortalCamera.
    self.free_portals = []

    ## @var transit_portals
    # List of Portal instances that allow transit.
    self.transit_portals = []

    ## @var counter
    # Integer which counts the number of portals already created. Used for portal IDs.
    self.counter = 0

    # add portal instances
    #'''

    if (4 in hyperspace_config.active_scenes):
      self.add_portal(avango.gua.make_trans_mat(0.0, 0.0, -100.0),
                      1.0,
                      avango.gua.make_trans_mat(-60.585, 6.62, -0.95),
                      0.6,
                      1.2,
                      "3D",
                      "PERSPECTIVE",
                      "False",
                      "data/materials/White.gmd")
      self.add_portal(avango.gua.make_trans_mat(10.0, 0.0, -100.0),
                      1.0,
                      avango.gua.make_trans_mat(-55.694, 6.62, -0.95),
                      0.6,
                      1.2,
                      "3D",
                      "PERSPECTIVE",
                      "False",
                      "data/materials/White.gmd")

    '''
    self.add_portal(avango.gua.make_trans_mat(0.0, 1.55, 0.0) * avango.gua.make_rot_mat(-90, 0, 1, 0),
                    1.0,
                    avango.gua.make_trans_mat(0.0, 2.0, -1.5) * avango.gua.make_rot_mat(45, 1, 0, 0),
                    1.0,
                    1.0,
                    "3D",
                    "PERSPECTIVE",
                    "False",
                    "data/materials/ShadelessBlue.gmd")
    '''

    '''
    self.add_portal(avango.gua.make_trans_mat(0.0, 1.55, 2.0),
                    0.2,
                    avango.gua.make_trans_mat(-1.2, 2.0, -2.5),
                    1.0,
                    1.0,
                    "3D",
                    "PERSPECTIVE",
                    "False",
                    "data/materials/ShadelessBlue.gmd")

                    1.0,
                    avango.gua.make_trans_mat(1.2, 2.0, -2.5),
                    1.0,
                    1.0,
                    "3D",
                    "PERSPECTIVE",
                    "False",
                    "data/materials/ShadelessBlue.gmd")
    '''

    '''
    self.add_bidirectional_portal(avango.gua.make_trans_mat(0.0, 1.55, 3.0),
                                  avango.gua.make_trans_mat(0.0, 1.55, -3.0),
                                  1.0,
                                  1.0,
                                  "3D",
                                  "PERSPECTIVE",
                                  "False")
    '''

    # tower portal
    '''
    self.add_bidirectional_portal( avango.gua.make_trans_mat(-23.0, 1.3, 21.0) * avango.gua.make_rot_mat(-90, 0, 1, 0),
                                   avango.gua.make_trans_mat(-12.0, 17.3, -7.0) * avango.gua.make_rot_mat(180, 0, 1, 0),
                                   4.0,
                                   2.6,
                                   "3D",
                                   "PERSPECTIVE",
                                   "False")
    '''
    self.always_evaluate(True)

  ## Evaluated every frame.
  def evaluate(self):

    # check every navigation instance for portal intersections
    for _nav in self.NAVIGATION_LIST:

      _nav_device_mat = _nav.platform.platform_transform_node.Transform.value * \
                        _nav.platform.platform_scale_transform_node.Transform.value * \
                          avango.gua.make_trans_mat(_nav.device.sf_station_mat.value.get_translate())


      _nav_device_pos = _nav_device_mat.get_translate()

      _nav_device_pos2 = _nav_device_mat * avango.gua.Vec3(0.0,0.0,1.0)
      _nav_device_pos2 = avango.gua.Vec3(_nav_device_pos2.x, _nav_device_pos2.y, _nav_device_pos2.z)


      for _portal in self.transit_portals:
        _mat = avango.gua.make_inverse_mat(_portal.portal_matrix_node.Transform.value)

        _nav_device_portal_space_mat = _mat * _nav_device_mat
        _nav_device_portal_space_pos = _mat * _nav_device_pos
        _nav_device_portal_space_pos2 = _mat * _nav_device_pos2
        _nav_device_portal_space_pos = avango.gua.Vec3(_nav_device_portal_space_pos.x, _nav_device_portal_space_pos.y, _nav_device_portal_space_pos.z)

        # do a teleportation if navigation enters portal
        if  _nav_device_portal_space_pos.x > -_portal.width/2     and \
            _nav_device_portal_space_pos.x <  _portal.width/2     and \
            _nav_device_portal_space_pos.y > -_portal.height/2    and \
            _nav_device_portal_space_pos.y <  _portal.height/2    and \
            _nav_device_portal_space_pos.z < 0.0                  and \
            _nav_device_portal_space_pos2.z >= 0.0                and \
            _portal.viewing_mode == "3D":

          _nav.inputmapping.set_abs_mat(_portal.platform_matrix * \
                                        avango.gua.make_scale_mat(_portal.platform_scale) * \
                                        avango.gua.make_trans_mat(_nav_device_portal_space_pos) * \
                                        avango.gua.make_rot_mat(_nav_device_portal_space_mat.get_rotate_scale_corrected()) * \
                                        avango.gua.make_trans_mat(_nav.device.sf_station_mat.value.get_translate() * -1.0) * \
                                        avango.gua.make_inverse_mat(avango.gua.make_scale_mat(_portal.platform_scale)))

          if _nav.movement_traces_activated:
            _nav.trace.clear(_nav.inputmapping.sf_abs_mat.value)
          _nav.inputmapping.scale_stop_time = None
          _nav.inputmapping.set_scale(_portal.platform_scale, False)


      '''
      _mat = _nav.platform.platform_scale_transform_node.WorldTransform.value * _nav.device.sf_station_mat.value
      _scale = _nav.inputmapping.sf_scale.value
      _last_teleport_time = self.last_teleportation_times[self.NAVIGATION_LIST.index(_nav)]

      for _portal in self.transit_portals:

        _mat_in_portal_space = avango.gua.make_inverse_mat(_portal.portal_matrix_node.Transform.value) * \
                               _mat

        _transit_check_mat = _mat_in_portal_space

        _vec_in_portal_space = _mat_in_portal_space.get_translate()

        # do a teleportation if navigation enters portal
        if (_vec_in_portal_space.x > -_portal.width/2              and \
            _vec_in_portal_space.x <  _portal.width/2              and \
            _vec_in_portal_space.y > -_portal.height/2             and \
            _vec_in_portal_space.y <  _portal.height/2             and \
            abs(_vec_in_portal_space.z) < max(0.1 * _scale, 0.1))  and \
            time.time() - _last_teleport_time > 1.0                and \
            _portal.viewing_mode == "3D":

          _nav.inputmapping.set_abs_mat(_portal.platform_matrix * \
                                        avango.gua.make_scale_mat(_portal.platform_scale) * \
                                        avango.gua.make_trans_mat(_vec_in_portal_space) * \
                                        avango.gua.make_rot_mat(_mat_in_portal_space.get_rotate_scale_corrected()) * \
                                        avango.gua.make_trans_mat(_nav.device.sf_station_mat.value.get_translate() * -1.0) * \
                                        avango.gua.make_inverse_mat(avango.gua.make_scale_mat(_portal.platform_scale)))

          _nav.inputmapping.scale_stop_time = None
          _nav.inputmapping.set_scale(_portal.platform_scale, False)
          self.last_teleportation_times[self.NAVIGATION_LIST.index(_nav)] = time.time()
      '''


  ## Adds a new Portal instance to the scene.
  # @param PLATFORM_MATRIX Transformation matrix of the portal platform.
  # @param PLATFORM_SCALE Scaling factor of the portal platform.
  # @param PORTAL_MATRIX Matrix where the portal display is located (entry).
  # @param WIDTH Width of the portal in meters.
  # @param HEIGHT Height of the portal in meters.
  # @param VIEWING_MODE Viewing mode of the portal, can be either "2D" or "3D".
  # @param CAMERA_MODE Projection mode of the portal camera, can be either "PERSPECTIVE" or "ORTHOGRAPHIC".
  # @param NEGATIVE_PARALLAX Indicating if negative parallax is allowed in the portal, can be either "True" or "False".
  # @param BORDER_MATERIAL The material string to be used for the portal's border.
  def add_portal(self, PLATFORM_MATRIX, PLATFORM_SCALE, PORTAL_MATRIX, WIDTH, HEIGHT, VIEWING_MODE, CAMERA_MODE, NEGATIVE_PARALLAX, BORDER_MATERIAL, TRANSIT = False):
    _portal = Portal(self, self.counter, PLATFORM_MATRIX, PLATFORM_SCALE, PORTAL_MATRIX, WIDTH, HEIGHT, VIEWING_MODE, CAMERA_MODE, NEGATIVE_PARALLAX, BORDER_MATERIAL)
    self.counter += 1
    self.portals.append(_portal)

    if TRANSIT:
      self.transit_portals.append(_portal)

    return _portal

  ## Add a new bidirectional portal to the scene.
  # @param FIRST_MATRIX First matrix defining the portal.
  # @param SECOND_MATRIX Second matrix defining the portal.
  # @param WIDTH Width of the portal in meters.
  # @param HEIGHT Height of the portal in meters.
  # @param VIEWING_MODE Viewing mode of the portal, can be either "2D" or "3D".
  # @param CAMERA_MODE Projection mode of the portal camera, can be either "PERSPECTIVE" or "ORTHOGRAPHIC".
  # @param NEGATIVE_PARALLAX Indicating if negative parallax is allowed in the portal, can be either "True" or "False".
  def add_bidirectional_portal(self, FIRST_MATRIX, SECOND_MATRIX, WIDTH, HEIGHT, VIEWING_MODE, CAMERA_MODE, NEGATIVE_PARALLAX):
    self.add_portal(FIRST_MATRIX, 1.0, SECOND_MATRIX, WIDTH, HEIGHT, VIEWING_MODE, CAMERA_MODE, NEGATIVE_PARALLAX, "data/materials/ShadelessBlue.gmd", True)

    # mirror matrices for opposite portal
    _mirrored_scene_matrix = SECOND_MATRIX * avango.gua.make_rot_mat(180, 0, 1, 0)
    _mirrored_portal_matrix = FIRST_MATRIX * avango.gua.make_rot_mat(180, 0, 1, 0)

    self.add_portal(_mirrored_scene_matrix, 1.0, _mirrored_portal_matrix, WIDTH, HEIGHT, VIEWING_MODE, CAMERA_MODE, NEGATIVE_PARALLAX, "data/materials/ShadelessOrange.gmd", True)

  ## Gets an active Portal instance by its ID. Returns None when no matching instance was found.
  # @param The Portal ID to be searched for.
  def get_portal_by_id(self, ID):
    _portal_instance = None

    for _portal in self.portals:
      if _portal.id == ID:
        _portal_instance = _portal

    return _portal_instance

  ## Removes a portal from the scene.
  # @param ID The portal ID to be removed.
  def remove_portal(self, ID):

    # find corresponding portal instance
    _portal_to_remove = self.get_portal_by_id(ID)

    if _portal_to_remove == None:
      print_error("Error: Portal ID could not be matched.", False)
      return

    # destroy portal on server side
    _portal_to_remove.deactivate()
    self.portals.remove(_portal_to_remove)
    del _portal_to_remove


## A Portal is the display of another location on a virtual display.
class Portal:

  ## Custom constructor.
  # @param PORTAL_MANAGER Reference to the PortalManager to be used.
  # @param ID The portal ID to be assigned to the new portal.
  # @param PLATFORM_MATRIX Transformation matrix of the portal exit's platform.
  # @param PLATFORM_SCALE Scaling factor of the portal exit's platform.
  # @param PORTAL_MATRIX Matrix where the portal display is located (entry).
  # @param WIDTH Width of the portal in meters.
  # @param HEIGHT Height of the portal in meters.
  # @param VIEWING_MODE Viewing mode of the portal, can be either "2D" or "3D".
  # @param CAMERA_MODE Projection mode of the portal camera, can be either "PERSPECTIVE" or "ORTHOGRAPHIC".
  # @param NEGATIVE_PARALLAX Indicating if negative parallax is allowed in the portal, can be either "True" or "False".
  # @param BORDER_MATERIAL The material string to be used for the portal's border.
  def __init__(self
             , PORTAL_MANAGER
             , ID
             , PLATFORM_MATRIX
             , PLATFORM_SCALE
             , PORTAL_MATRIX
             , WIDTH
             , HEIGHT
             , VIEWING_MODE
             , CAMERA_MODE
             , NEGATIVE_PARALLAX
             , BORDER_MATRIAL):

    ## @var PORTAL_MANAGER
    # Reference to the PortalManager to be used.
    self.PORTAL_MANAGER = PORTAL_MANAGER

    ## @var id
    # The portal ID assigned to the portal.
    self.id = ID

    ## @var scene_matrix
    # Matrix where the portal looks from (exit).
    self.scene_matrix = PLATFORM_MATRIX * \
                        avango.gua.make_scale_mat(PLATFORM_SCALE)

    ## @var portal_matrix
    # Matrix where the portal display is located (entry).
    self.portal_matrix = PORTAL_MATRIX

    ## @var width
    # Width of the portal in meters.
    self.width = WIDTH

    ## @var height
    # Height of the portal in meters.
    self.height = HEIGHT

    ## @var NET_TRANS_NODE
    # Reference to the nettrans node used for distribution.
    self.NET_TRANS_NODE = PORTAL_MANAGER.SCENEGRAPH["/net"]

    ## @var viewing_mode
    # Viewing mode of the portal, can be either "2D" or "3D".
    self.viewing_mode = VIEWING_MODE

    ## @var camera_mode
    # Projection mode of the portal camera, can be either "PERSPECTIVE" or "ORTHOGRAPHIC".
    self.camera_mode = CAMERA_MODE

    ## @var negative_parallax
    # Indicating if negative parallax is allowed in the portal, can be either "True" or "False".
    self.negative_parallax = NEGATIVE_PARALLAX

    ## @var border_material
    # The material string to be used for the portal's border.
    self.border_material = BORDER_MATRIAL

    ## @var visible
    # Boolean string variable indicating if the portal is currently visible.
    self.visible = "True"

    # metainformation for modification of scene_matrix #

    ## @var platform_transform
    # Transformation matrix of the portal platform.
    self.platform_matrix = PLATFORM_MATRIX

    ## @var platform_scale
    # Scaling factor of the portal platform.
    self.platform_scale = PLATFORM_SCALE

    self.append_portal_nodes()

  ## Switches viewing_mode to the other state.
  def switch_viewing_mode(self):
    if self.viewing_mode == "2D":
      self.viewing_mode = "3D"
    else:
      self.viewing_mode = "2D"

    self.portal_node.GroupNames.value = ["0-" + self.viewing_mode, "1-" + self.camera_mode, "2-" + self.negative_parallax, "3-" + self.border_material, "4-" + self.visible]

  ## Switches camera_mode to the other state.
  def switch_camera_mode(self):
    if self.camera_mode == "PERSPECTIVE":
      self.camera_mode = "ORTHOGRAPHIC"
    else:
      self.camera_mode = "PERSPECTIVE"

    self.portal_node.GroupNames.value = ["0-" + self.viewing_mode, "1-" + self.camera_mode, "2-" + self.negative_parallax, "3-" + self.border_material, "4-" + self.visible]

  ## Switches negative_parallax to the other state.
  def switch_negative_parallax(self):
    if self.negative_parallax == "True":
      self.negative_parallax = "False"
    else:
      self.negative_parallax = "True"

    self.portal_node.GroupNames.value = ["0-" + self.viewing_mode, "1-" + self.camera_mode, "2-" + self.negative_parallax, "3-" + self.border_material, "4-" + self.visible]

  ## Sets a new value for platform_matrix and updates scene_matrix.
  # @param PLATFORM_MATRIX The new platform transformation matrix to be set.
  def set_platform_matrix(self, PLATFORM_MATRIX):
    self.platform_matrix = PLATFORM_MATRIX
    self.scene_matrix_node.Transform.value = self.platform_matrix * \
                                             avango.gua.make_scale_mat(self.platform_scale)

  ## Sets a new value for platform_scale and updates scene_matrix.
  # @param SCALE The new platform scale factor to be set.
  def set_platform_scale(self, SCALE):
    self.platform_scale = SCALE
    self.scene_matrix_node.Transform.value = self.platform_matrix * \
                                             avango.gua.make_scale_mat(self.platform_scale)

  ## Connects the portal matrix node to a field or disconnects it if None is given.
  # @param SF_PORTAL_MATRIX The field to connect the portal matrix node with. None if disconnection is required.
  def connect_portal_matrix(self, SF_PORTAL_MATRIX):

    self.portal_matrix_node.Transform.disconnect()

    if SF_PORTAL_MATRIX != None:
      self.portal_matrix_node.Transform.connect_from(SF_PORTAL_MATRIX)

  ## Modifies the scene matrix by the input values given from a device.
  # @param DEVICE_INPUT_VALUES List of input values from a device.
  #
  def modify_scene_matrix(self, DEVICE_INPUT_VALUES = [0,0,0,0,0,0,0], OFFSET_MAT = avango.gua.make_identity_mat):

    _x = DEVICE_INPUT_VALUES[0]
    _y = DEVICE_INPUT_VALUES[1]
    _z = DEVICE_INPUT_VALUES[2]
    _rx = DEVICE_INPUT_VALUES[3]
    _ry = DEVICE_INPUT_VALUES[4]
    _rz = DEVICE_INPUT_VALUES[5]
    _w = DEVICE_INPUT_VALUES[6]

    if _w == -1:
      self.set_platform_scale(self.platform_scale * 0.985)
    elif _w == 1:
      self.set_platform_scale(self.platform_scale * 1.015)

    _trans_vec = avango.gua.Vec3(_x, _y, _z)
    _rot_vec = avango.gua.Vec3(_rx, _ry, _rz)

    if _trans_vec.length() != 0.0 or _rot_vec.length() != 0.0:

      # object metaphor
      _transformed_trans_vec = avango.gua.make_rot_mat(self.platform_matrix.get_rotate_scale_corrected()) * avango.gua.Vec3(_x*-1.0, _z, _y*-1.0)
      _transformed_trans_vec = OFFSET_MAT * _transformed_trans_vec
      _transformed_trans_vec = avango.gua.Vec3(_transformed_trans_vec.x, _transformed_trans_vec.y, _transformed_trans_vec.z)
      _transformed_trans_vec *= self.platform_scale

      _rot_vec = OFFSET_MAT * _rot_vec

      _new_platform_matrix = avango.gua.make_trans_mat(_transformed_trans_vec) * \
                             self.platform_matrix * \
                             avango.gua.make_rot_mat( _rot_vec.y, 0, 0, -1) * \
                             avango.gua.make_rot_mat( _rot_vec.x, -1, 0, 0) * \
                             avango.gua.make_rot_mat( _rot_vec.z, 0, 1, 0)

      '''
      # navigation metaphor
      _transformed_trans_vec = avango.gua.make_rot_mat(self.platform_matrix.get_rotate()) * avango.gua.Vec3(_x, _y, _z)
      _transformed_trans_vec = avango.gua.Vec3(_transformed_trans_vec.x, _transformed_trans_vec.y, _transformed_trans_vec.z)

      _new_platform_matrix = avango.gua.make_trans_mat(_transformed_trans_vec) * \
                             avango.gua.make_trans_mat(self.platform_matrix.get_translate()) * \
                             avango.gua.make_rot_mat( _rot_vec.z, 0, 0, 1) * \
                             avango.gua.make_rot_mat( _rot_vec.x, 1, 0, 0) * \
                             avango.gua.make_rot_mat( _rot_vec.y, 0, 1, 0) * \
                             avango.gua.make_rot_mat(self.platform_matrix.get_rotate_scale_corrected())
      '''

      _scene_transform = _new_platform_matrix * \
                         avango.gua.make_scale_mat(self.platform_scale)

      self.platform_matrix = _new_platform_matrix
      self.scene_matrix_node.Transform.value = _scene_transform


  ## Sets the border material to be used for the portal.
  # @param BORDER_MATERIAL The material string to be set.
  def set_border_material(self, BORDER_MATERIAL):
    self.border_material = BORDER_MATERIAL
    self.portal_node.GroupNames.value = ["0-" + self.viewing_mode, "1-" + self.camera_mode, "2-" + self.negative_parallax, "3-" + self.border_material, "4-" + self.visible]

  ## Sets the visiblity of this portal.
  # @param VISIBLE Boolean describing the visibility to be set.
  def set_visibility(self, VISIBLE):
    if VISIBLE:
      self.visible = "True"
    else:
      self.visible = "False"

    self.portal_node.GroupNames.value = ["0-" + self.viewing_mode, "1-" + self.camera_mode, "2-" + self.negative_parallax, "3-" + self.border_material, "4-" + self.visible]

  ## Sets width and height of the portal.
  # @param WIDTH The new portal width to be set.
  # @param HEIGHT The new portal height to be set.
  def set_size(self, WIDTH, HEIGHT):
    self.width = WIDTH
    self.height = HEIGHT
    self.portal_screen_node.Width.value = self.width
    self.portal_screen_node.Height.value = self.height

  ## Appends the necessary portal scenegraph nodes on server side.
  def append_portal_nodes(self):

    ## @var portal_node
    # Grouping node for this portal below the group node for all portals.
    self.portal_node = avango.gua.nodes.TransformNode(Name = "portal_" + str(self.id))
    self.portal_node.GroupNames.value = ["0-" + self.viewing_mode, "1-" + self.camera_mode, "2-" + self.negative_parallax, "3-" + self.border_material, "4-" + self.visible]
    self.PORTAL_MANAGER.portal_group_node.Children.value.append(self.portal_node)
    self.NET_TRANS_NODE.distribute_object(self.portal_node)

    ## @var portal_matrix_node
    # Scenegraph node representing the location where the portal display is located (entry).
    self.portal_matrix_node = avango.gua.nodes.TransformNode(Name = "portal_matrix")
    self.portal_matrix_node.Transform.value = self.portal_matrix
    self.portal_node.Children.value.append(self.portal_matrix_node)
    self.NET_TRANS_NODE.distribute_object(self.portal_matrix_node)

    ## @var scene_matrix_node
    # Scenegraph node representing the location where the portal looks from (exit).
    self.scene_matrix_node = avango.gua.nodes.TransformNode(Name = "scene_matrix")
    self.scene_matrix_node.Transform.value = self.scene_matrix
    self.portal_node.Children.value.append(self.scene_matrix_node)
    self.NET_TRANS_NODE.distribute_object(self.scene_matrix_node)

    ## @var portal_screen_node
    # Screen node representing the portal's screen in the scene.
    self.portal_screen_node = avango.gua.nodes.ScreenNode(Name = "portal_screen")
    self.portal_screen_node.Width.value = self.width
    self.portal_screen_node.Height.value = self.height
    self.scene_matrix_node.Children.value.append(self.portal_screen_node)
    self.NET_TRANS_NODE.distribute_object(self.portal_screen_node)


  ## Removes this portal from the portal group and destroys all the scenegraph nodes.
  def deactivate(self):
    self.PORTAL_MANAGER.portal_group_node.Children.value.remove(self.portal_node)

    del self.portal_screen_node
    del self.scene_matrix_node
    del self.portal_matrix_node
    del self.portal_node
