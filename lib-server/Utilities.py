#!/usr/bin/python

## @file
# Contains helper methods for various tasks.

# import avango-guacamole libraries
import avango
import avango.gua
import avango.script

# import framework libraries
from SceneManager import SceneManager

# import python libraries
import math

## Converts a rotation matrix to the Euler angles yaw, pitch and roll.
# @param MATRIX The rotation matrix to be converted.
def get_euler_angles(MATRIX):

  quat = MATRIX.get_rotate()
  qx = quat.x
  qy = quat.y
  qz = quat.z
  qw = quat.w

  sqx = qx * qx
  sqy = qy * qy
  sqz = qz * qz
  sqw = qw * qw
  
  unit = sqx + sqy + sqz + sqw # if normalised is one, otherwise is correction factor
  test = (qx * qy) + (qz * qw)

  if test > 1:
    yaw = 0.0
    roll = 0.0
    pitch = 0.0

  if test > (0.49999 * unit): # singularity at north pole
    yaw = 2.0 * math.atan2(qx,qw)
    roll = math.pi/2.0
    pitch = 0.0
  elif test < (-0.49999 * unit): # singularity at south pole
    yaw = -2.0 * math.atan2(qx,qw)
    roll = math.pi/-2.0
    pitch = 0.0
  else:
    yaw = math.atan2(2.0 * qy * qw - 2.0 * qx * qz, 1.0 - 2.0 * sqy - 2.0 * sqz)
    roll = math.asin(2.0 * test)
    pitch = math.atan2(2.0 * qx * qw - 2.0 * qy * qz, 1.0 - 2.0 * sqx - 2.0 * sqz)

  if yaw < 0.0:
    yaw += 2.0 * math.pi

  if pitch < 0:
    pitch += 2 * math.pi
  
  if roll < 0:
    roll += 2 * math.pi

  return yaw, pitch, roll


## Extracts the yaw (head) rotation from a rotation matrix.
# @param MATRIX The rotation matrix to extract the angle from.
def get_yaw(MATRIX):

  try:
    _yaw, _, _ = get_euler_angles(MATRIX)
    return _yaw
  except:
    return 0


## Returns the rotation matrix of the rotation between two input vectors.
# @param VEC1 First vector.
# @param VEC2 Second vector.
def get_rotation_between_vectors(VEC1, VEC2):

  VEC1.normalize()
  VEC2.normalize()    

  _angle = math.degrees(math.acos(VEC1.dot(VEC2)))
  _axis = VEC1.cross(VEC2)

  return avango.gua.make_rot_mat(_angle, _axis)

## Returns the Euclidean distance between two points.
# @param POINT1 Starting point.
# @param POINT2 End point.
def euclidean_distance(POINT1, POINT2):
  _diff_x = POINT2.x - POINT1.x
  _diff_y = POINT2.y - POINT1.y
  _diff_z = POINT2.z - POINT1.z

  return math.sqrt(math.pow(_diff_x, 2) + math.pow(_diff_y, 2) + math.pow(_diff_z, 2))

## Computes the distance between a Point and a 3D-line.
# @param POINT_TO_CHECK The point to compute the distance for.
# @param LINE_POINT_1 One point lying on the line.
# @param LINE_VEC Direction vector of the line.
def compute_point_to_line_distance(POINT_TO_CHECK, LINE_POINT_1, LINE_VEC):

  _point_line_vec = avango.gua.Vec3(LINE_POINT_1.x - POINT_TO_CHECK.x, LINE_POINT_1.y - POINT_TO_CHECK.y, LINE_POINT_1.z - POINT_TO_CHECK.z)

  _dist = (_point_line_vec.cross(LINE_VEC)).length() / LINE_VEC.length()

  return _dist

def compute_plane(POINT1, POINT2, POINT3):

  _v1 = POINT1 - POINT3
  _v2 = POINT2 - POINT3
  _v1.normalize()
  _v2.normalize()
  
  _n = _v1.cross(_v2)
  _n.normalize()
  
  _d = - _n.dot(POINT1)
  return (_n, _d)

def compute_point_plane_distance(N, D, POINT):

  # compute point plane distance: <0.0 --> in front of plane: >0.0 behind plane
  return N.x * POINT.x + N.y * POINT.y + N.z * POINT.z + D


## Checks if a point is inside the viewing frustum of a user.
# @param POINT The point to be checked.
# @param USER_REPRESENTATION The UserRepresentation instance to which SCREEN is belonging to.
# @param SCREEN The screen to create the viewing frustum for. 
def is_inside_frustum(POINT, USER_REPRESENTATION, SCREEN):

  _user_head_world_pos = USER_REPRESENTATION.head.WorldTransform.value.get_translate()
  _screen_world_mat = SCREEN.WorldTransform.value

  # if user representation is in virtual display, start intersecting from the virtual display plane
  if USER_REPRESENTATION.is_in_virtual_display():
    _head_in_screen_pos = avango.gua.make_inverse_mat(_screen_world_mat) * _user_head_world_pos
    _near_clip = abs(_head_in_screen_pos.z)
  else:
    _near_clip = SceneManager.current_near_clip

  _far_clip = SceneManager.current_far_clip


  # head space (but with nav orientation)
  _head_mat = SCREEN.WorldTransform.value
  _head_mat.set_translate(_user_head_world_pos)
      
  _point = avango.gua.make_inverse_mat(_head_mat) * POINT # point in head space
  _depth = abs(_point.z)
  if (_depth < _near_clip) or (_depth > _far_clip): # point in front of near plane or behind far plane --> outside frustum
    return False

      
  # compute screen corner points
  _screen_width = SCREEN.Width.value
  _screen_height = SCREEN.Height.value
  
  _tl_world_pos = _screen_world_mat * avango.gua.Vec3(-_screen_width * 0.5, _screen_height * 0.5, 0.0)
  _tr_world_pos = _screen_world_mat * avango.gua.Vec3(_screen_width * 0.5, _screen_height * 0.5, 0.0)
  _bl_world_pos = _screen_world_mat * avango.gua.Vec3(-_screen_width * 0.5, -_screen_height * 0.5, 0.0)
  _br_world_pos = _screen_world_mat * avango.gua.Vec3(_screen_width * 0.5, -_screen_height * 0.5, 0.0)

  _tl_world_pos = avango.gua.Vec3(_tl_world_pos.x, _tl_world_pos.y, _tl_world_pos.z)
  _tr_world_pos = avango.gua.Vec3(_tr_world_pos.x, _tr_world_pos.y, _tr_world_pos.z)    
  _bl_world_pos = avango.gua.Vec3(_bl_world_pos.x, _bl_world_pos.y, _bl_world_pos.z)
  _br_world_pos = avango.gua.Vec3(_br_world_pos.x, _br_world_pos.y, _br_world_pos.z)
  
  ## compute lateral planes ##
  _left_plane = compute_plane(_bl_world_pos, _tl_world_pos, _user_head_world_pos)
  _distance = compute_point_plane_distance(_left_plane[0], _left_plane[1], POINT)
  if _distance < 0.0: # point in front of left plane --> outside frustum
    return False

  _right_plane = compute_plane(_tr_world_pos, _br_world_pos, _user_head_world_pos)
  _distance = compute_point_plane_distance(_right_plane[0], _right_plane[1], POINT)
  if _distance < 0.0: # point in front of right plane --> outside frustum
    return False

  _top_plane = compute_plane(_tl_world_pos, _tr_world_pos, _user_head_world_pos)
  _distance = compute_point_plane_distance(_top_plane[0], _top_plane[1], POINT)
  if _distance < 0.0: # point in front of top plane --> outside frustum
    return False

  _bottom_plane = compute_plane(_br_world_pos, _bl_world_pos, _user_head_world_pos)
  _distance = compute_point_plane_distance(_bottom_plane[0], _bottom_plane[1], POINT)
  if _distance < 0.0: # point in front of bottom plane plane --> outside frustum
    return False

  return True    
    

