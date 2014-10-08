#!/usr/bin/python

## @file
# Client application for the distributed Navigation and Viewing Framework.

# import avango-guacamole libraries
import avango
import avango.script
import avango.gua
import avango.oculus

# import framework libraries
import ClientMaterialUpdaters
from View import *
from ClientPortal import * 
from display_config import displays

# import python libraries
import sys

# Command line parameters:
# client.py SERVER_IP PLATFORM_ID DISPLAY_NAME SCREEN_NUM
# @param SERVER_IP The IP address on which the server process is running.
# @param PLATFORM_ID The platform id for which this client is responsible for.
# @param DISPLAY_NAME The name associated to the display for which this client is responsible for.
# @param SCREEN_NUM The number of the screen on the platform.

## Main method for the client application.
def start():

  # disable logger warningss
  logger = avango.gua.nodes.Logger(EnableWarning = False)

  # get the server ip
  server_ip = str(sys.argv[1])

  # get the platform id
  platform_id = int(sys.argv[2])

  # get the display name
  display_name = str(sys.argv[3])

  # get the screen number on platform
  screen_num = int(sys.argv[4])

  # get own hostname
  hostname = open('/etc/hostname', 'r').readline()
  hostname = hostname.strip(" \n")

  print "This client is running on", hostname, "and listens to server", server_ip
  print "It is responsible for platform", platform_id, "and display", display_name

  # create distribution node
  nettrans = avango.gua.nodes.NetTransform(
                Name = "net",
                # specify role, ip, and port
                Groupname = "AVCLIENT|{0}|7432".format(server_ip)
                )

  # create a dummy scenegraph to be extended by distribution
  graph = avango.gua.nodes.SceneGraph(Name = "scenegraph")

  # create node for local portal updates
  local_portal_node = avango.gua.nodes.TransformNode(Name = "local_portal_group")

  graph.Root.value.Children.value = [nettrans, local_portal_node]

  # create material updaters as this cannot be distributed
  avango.gua.load_shading_models_from("data/materials")
  avango.gua.load_materials_from("data/materials")
  
  timer = avango.nodes.TimeSensor()
  
  water_updater = ClientMaterialUpdaters.TimedMaterialUniformUpdate()
  water_updater.MaterialName.value = "data/materials/Water.gmd"
  water_updater.UniformName.value = "time"
  water_updater.TimeIn.connect_from(timer.Time)

  # get the display instance
  for _display in displays:
    if _display.name == display_name:
      handled_display_instance = _display


  # create a viewer
  viewer = avango.gua.nodes.Viewer()

  # Create a view for each displaystring (= slot)
  _string_num = 0
  views = []

  for _displaystring in handled_display_instance.displaystrings:
    _view = View()
    _view.my_constructor(graph, 
                         viewer,
                         platform_id, 
                         _string_num,
                         handled_display_instance, 
                         screen_num, 
                         handled_display_instance.stereo)
    views.append(_view)
    _string_num += 1

  viewer.SceneGraphs.value = [graph]

  # create client portal manager
  portal_manager = ClientPortalManager()
  portal_manager.my_constructor(graph, views)

  # start rendering process
  viewer.run()

if __name__ == '__main__':
  start()
