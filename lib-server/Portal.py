#!/usr/bin/python

## @file
# Contains classes Portal.

# import avango-guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

# import framework libraries
from ApplicationManager import *
from Display import *
from ConsoleIO import *
from scene_config import scenegraphs
import Utilities

# import python libraries
import time
import math


## A Portal is the display of another location on a virtual display.
class Portal(Display):

  ## @var num_instances_created
  # Static intance counter to assign proper IDs to the portals.
  num_instances_created = 0

  ## Custom constructor.
  # @param PORTAL_MATRIX Matrix where the portal display is located (entry).
  # @param WIDTH Width of the portal in meters.
  # @param HEIGHT Height of the portal in meters.
  # @param VIEWING_MODE Viewing mode of the portal, can be either "2D" or "3D".
  # @param CAMERA_MODE Projection mode of the portal camera, can be either "PERSPECTIVE" or "ORTHOGRAPHIC".
  # @param NEGATIVE_PARALLAX Indicating if negative parallax is allowed in the portal, can be either "True" or "False".
  # @param BORDER_MATERIAL The material string to be used for the portal's border.
  # @param TRANSITABLE Boolean saying if teleportation for this portal is enabled.
  def __init__(self
             , PORTAL_MATRIX
             , WIDTH
             , HEIGHT):


    _stereo = True
    self.base_constructor("portal_" + str(Portal.num_instances_created), (1000, 1000), (WIDTH, HEIGHT), _stereo)

    ## @var id
    # The portal ID assigned to the portal.
    self.id = Portal.num_instances_created
    Portal.num_instances_created += 1

    ## @var portal_matrix
    # Matrix where the portal display is located (entry).
    self.portal_matrix = PORTAL_MATRIX

  ## Returns a boolean value saying if this display is virtual.
  def is_virtual(self):
    return True

  '''
  ## Switches viewing_mode to the other state.
  def switch_viewing_mode(self):
    if self.viewing_mode == "2D":
      self.viewing_mode = "3D"
    else:
      self.viewing_mode = "2D"

    for _user_repr in ApplicationManager.all_user_representations:
      if _user_repr.DISPLAY_GROUP.displays[0] == self:

        if self.viewing_mode == "2D":
          _user_repr.make_default_viewing_setup()
        else:
          _user_repr.make_complex_viewing_setup()

    self.settings_node.GroupNames.value = ["0-" + self.viewing_mode, "1-" + self.camera_mode, "2-" + self.negative_parallax, "3-" + self.border_material, "4-" + self.visible]

  ## Switches camera_mode to the other state.
  def switch_camera_mode(self):
    if self.camera_mode == "PERSPECTIVE":
      self.camera_mode = "ORTHOGRAPHIC"
    else:
      self.camera_mode = "PERSPECTIVE"

    self.settings_node.GroupNames.value = ["0-" + self.viewing_mode, "1-" + self.camera_mode, "2-" + self.negative_parallax, "3-" + self.border_material, "4-" + self.visible]

  ## Switches negative_parallax to the other state.
  def switch_negative_parallax(self):
    if self.negative_parallax == "True":
      self.negative_parallax = "False"
    else:
      self.negative_parallax = "True"

    self.settings_node.GroupNames.value = ["0-" + self.viewing_mode, "1-" + self.camera_mode, "2-" + self.negative_parallax, "3-" + self.border_material, "4-" + self.visible]


  ## Connects the portal matrix node to a field or disconnects it if None is given.
  # @param SF_PORTAL_MATRIX The field to connect the portal matrix node with. None if disconnection is required.
  def connect_portal_matrix(self, SF_PORTAL_MATRIX):

    self.portal_matrix_node.Transform.disconnect()
    
    if SF_PORTAL_MATRIX != None:
      self.portal_matrix_node.Transform.connect_from(SF_PORTAL_MATRIX)

  ## Sets the border material to be used for the portal.
  # @param BORDER_MATERIAL The material string to be set.
  def set_border_material(self, BORDER_MATERIAL):
    self.border_material = BORDER_MATERIAL
    self.settings_node.GroupNames.value = ["0-" + self.viewing_mode, "1-" + self.camera_mode, "2-" + self.negative_parallax, "3-" + self.border_material, "4-" + self.visible]

  ## Sets the visiblity of this portal.
  # @param VISIBLE Boolean describing the visibility to be set.
  def set_visibility(self, VISIBLE):
    if VISIBLE:
      self.visible = "True"
    else:
      self.visible = "False"

    self.settings_node.GroupNames.value = ["0-" + self.viewing_mode, "1-" + self.camera_mode, "2-" + self.negative_parallax, "3-" + self.border_material, "4-" + self.visible]

  ## Sets width and height of the portal.
  # @param WIDTH The new portal width to be set.
  # @param HEIGHT The new portal height to be set.
  def set_size(self, WIDTH, HEIGHT):
    self.size = (WIDTH, HEIGHT)
    self.portal_screen_node.Width.value = WIDTH
    self.portal_screen_node.Height.value = HEIGHT

  ## Deletes all nodes below a given node.
  # @param NODE The node to start deleting from.
  def delete_downwards_from(self, NODE):

    for _child in NODE.Children.value:
      self.delete_downwards_from(_child)
      del _child

  ## Removes this portal from the portal group and destroys all the scenegraph nodes.
  def deactivate(self):

    Portal.portal_group_node.Children.value.remove(self.portal_node)

    for _user_repr in ApplicationManager.all_user_representations:
      if _user_repr.DISPLAY_GROUP.displays[0] == self:
        ApplicationManager.all_user_representations.remove(_user_repr)
        del _user_repr

    self.delete_downwards_from(self.portal_node)
    del self.portal_node
  '''