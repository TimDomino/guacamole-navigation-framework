#!/usr/bin/python

## @file
# Contains class View.

# import avango-guacamole libraries
import avango
import avango.gua
import avango.script
import avango.oculus
from avango.script import field_has_changed

# import framework libraries
from ClientTrackingReader import *
from ClientPortal import *
from ConsoleIO import *
import hyperspace_config

# import python libraries
import time


## Internal representation of a standard view on client side.
#
# Creates viewing setup and initializes a tracking sensor in order to avoid latency
# due to distribution in the network. Refers to a StandardUser on server side.
class View(avango.script.Script):

  ## @var sf_pipeline_string
  # String field containing the concatenated pipeline values.
  sf_pipeline_string = avango.SFString()

  ## Default constructor.
  def __init__(self):
    self.super(View).__init__()

    ## @var portal_pre_views
    # A list of all PortalPreView instances for this view.
    self.portal_pre_views = []

  ## Custom constructor.
  # @param SCENEGRAPH Reference to the scenegraph to be displayed.
  # @param VIEWER Reference to the viewer to which the created pipeline will be appended to.
  # @param PLATFORM_ID The platform id on which this user is standing on.
  # @param SLOT_ID The identification number of the slot to display.
  # @param DISPLAY_INSTANCE An instance of Display to represent the values.
  # @param SCREEN_NUM The number of the screen node on the platform.
  # @param STEREO Boolean indicating if the view to be constructed is stereo or mono.
  def my_constructor(self, SCENEGRAPH, VIEWER, PLATFORM_ID, SLOT_ID, DISPLAY_INSTANCE, SCREEN_NUM, STEREO):

    ## @var SCENEGRAPH
    # Reference to the scenegraph.
    self.SCENEGRAPH = SCENEGRAPH

    ## @var platform_id
    # The platform id for which this client process is responsible for.
    self.platform_id = PLATFORM_ID

    ## @var slot_id
    # User ID of this user within his or her user group.
    self.slot_id = SLOT_ID

    ## @var screen_num
    # The number of the screen node on the platform.
    self.screen_num = SCREEN_NUM

    ## @var is_stereo
    # Boolean indicating if the view to be constructed is stereo or mono.
    self.is_stereo = STEREO

    ## @var ONLY_TRANSLATION_UPDATE
    # In case this boolean is true, only the translation values will be locally updated from the tracking system.
    self.ONLY_TRANSLATION_UPDATE = False

    # retrieve the needed values from display
    ## @var display_values
    # Values that are retrieved from the display. Vary for each view on this display.
    self.display_values = DISPLAY_INSTANCE.register_view(SLOT_ID)

    self.timer = avango.nodes.TimeSensor()

    ##
    #
    self.display_render_mask = DISPLAY_INSTANCE.render_mask

    # check if no more users allowed at this screen
    if not self.display_values:
      # TODO better handling of this case?
      print 'Error: no more users allowed at display "' + DISPLAY_INSTANCE.name + '"!'
      return

    ## @var window_size
    # Size of the window in which this View will be rendered.
    self.window_size = avango.gua.Vec2ui(DISPLAY_INSTANCE.resolution[0], DISPLAY_INSTANCE.resolution[1])

    # create camera
    ## @var camera
    # The camera from which this View will be rendered.
    self.camera = avango.gua.nodes.Camera()
    self.camera.SceneGraph.value = SCENEGRAPH.Name.value
    self.camera.Mode.value = DISPLAY_INSTANCE.cameramode

    # set render mask for camera
    #_render_mask = "!do_not_display_group && !video_abstraction && !avatar_group_" + str(self.platform_id) + " && !couple_group_" + str(self.platform_id)
    _render_mask = "!pre_scene1 && !pre_scene2 && !do_not_display_group && !video_abstraction && !avatar_group_" + str(self.platform_id) + " && !couple_group_" + str(self.platform_id)

    for _i in range(0, 10):
      if _i != self.platform_id:
        _render_mask = _render_mask + " && !platform_group_" + str(_i)

    for _screen in range(0, 10):
      for _slot in range(0, 10):
        if _screen != self.screen_num or _slot != self.slot_id:
          _render_mask = _render_mask + " && !s" + str(_screen) + "_slot" + str(_slot)

    _render_mask = _render_mask + " && " + self.display_render_mask

    self.camera.RenderMask.value = _render_mask

    # create pipeline
    ## @var pipeline
    # The pipeline used to render this View.
    self.pipeline = avango.gua.nodes.Pipeline()
    self.pipeline.Enabled.value = True

    if DISPLAY_INSTANCE.stereomode == "HMD":

      '''
        HMD View
      '''

      self.camera.LeftScreen.value = "/net/platform_" + str(self.platform_id) + "/scale/s" + str(self.screen_num) + "_slot" + str(self.slot_id) + "/screenL"
      self.camera.RightScreen.value = "/net/platform_" + str(self.platform_id) + "/scale/s" + str(self.screen_num) + "_slot" + str(self.slot_id) + "/screenR"
      self.camera.LeftEye.value = "/net/platform_" + str(self.platform_id) + "/scale/s" + str(self.screen_num) + "_slot" + str(self.slot_id) + "/eyeL"
      self.camera.RightEye.value = "/net/platform_" + str(self.platform_id) + "/scale/s" + str(self.screen_num) + "_slot" + str(self.slot_id) + "/eyeR"

      # create window
      ## @var window
      # The window in which this View will be rendered to.
      self.window = avango.oculus.nodes.OculusWindow()
      self.window.Display.value = self.display_values[0] # GPU-ID
      self.window.Title.value = "Display: " + str(DISPLAY_INSTANCE.name) + "; Slot: " + str(self.slot_id)
      self.window.LeftResolution.value = avango.gua.Vec2ui(self.window_size.x / 2, self.window_size.y)
      self.window.RightResolution.value = avango.gua.Vec2ui(self.window_size.x / 2, self.window_size.y)

      self.pipeline.EnableStereo.value = True
      self.pipeline.LeftResolution.value = self.window.LeftResolution.value
      self.pipeline.RightResolution.value = self.window.RightResolution.value


    else:

      '''
        Standard View
      '''

      self.camera.LeftScreen.value = "/net/platform_" + str(self.platform_id) + "/scale/screen_" + str(self.screen_num)
      self.camera.RightScreen.value = "/net/platform_" + str(self.platform_id) + "/scale/screen_" + str(self.screen_num)
      self.camera.LeftEye.value = "/net/platform_" + str(self.platform_id) + "/scale/s" + str(self.screen_num) + "_slot" + str(self.slot_id) + "/eyeL"
      self.camera.RightEye.value = "/net/platform_" + str(self.platform_id) + "/scale/s" + str(self.screen_num) + "_slot" + str(self.slot_id) + "/eyeR"

      # create window
      ## @var window
      # The window in which this View will be rendered to.
      self.window = avango.gua.nodes.Window()
      self.window.Display.value = self.display_values[0] # GPU-ID
      self.window.Title.value = "Display: " + str(DISPLAY_INSTANCE.name) + "; Slot: " + str(self.slot_id)
      self.window.LeftResolution.value = self.window_size
      self.window.RightResolution.value = self.window_size
      #self.window.EnableVsync.value = False

      if DISPLAY_INSTANCE.stereomode == "SIDE_BY_SIDE":
        self.window.Size.value = avango.gua.Vec2ui(self.window_size.x * 2, self.window_size.y)
        self.window.LeftPosition.value = avango.gua.Vec2ui(0, 0)
        self.window.RightPosition.value = avango.gua.Vec2ui(self.window_size.x, 0)
        self.window.StereoMode.value = avango.gua.StereoMode.SIDE_BY_SIDE

      elif DISPLAY_INSTANCE.stereomode == "ANAGLYPH_RED_CYAN" or DISPLAY_INSTANCE.stereomode == "CHECKERBOARD":
        self.window.Size.value = self.window_size
        self.window.LeftPosition.value = avango.gua.Vec2ui(0, 0)
        self.window.RightPosition.value = avango.gua.Vec2ui(0, 0)

        if DISPLAY_INSTANCE.stereomode == "ANAGLYPH_RED_CYAN":
          self.window.StereoMode.value = avango.gua.StereoMode.ANAGLYPH_RED_CYAN

        elif DISPLAY_INSTANCE.stereomode == "CHECKERBOARD":
          self.window.StereoMode.value = avango.gua.StereoMode.CHECKERBOARD

      self.pipeline.LeftResolution.value = self.window.LeftResolution.value
      self.pipeline.RightResolution.value = self.window.RightResolution.value

      if self.is_stereo:
        self.pipeline.EnableStereo.value = True
      else:
        self.pipeline.EnableStereo.value = False


    self.pipeline.Window.value = self.window
    self.pipeline.Camera.value = self.camera
    self.pipeline.EnableFPSDisplay.value = True
    self.pipeline.EnablePreviewDisplay.value = False
    self.pipeline.EnableBackfaceCulling.value = False
    self.pipeline.EnableFrustumCulling.value = True
    self.pipeline.EnableFXAA.value = True
    self.pipeline.AmbientColor.value = avango.gua.Color(0.25, 0.25, 0.25)

    if hyperspace_config.prepipes:

      print "pipeline.enabled = ", self.pipeline.Enabled.value
      print "pipeline.stereo  = ", self.pipeline.EnableStereo.value

      self.camera.RenderMask.value += "&& !pre_scene1 && !pre_scene2"

      avango.gua.create_texture("/opt/guacamole/resources/skymaps/bright_sky.jpg")

      # pre render setup
      self.pre_camera2 = avango.gua.nodes.Camera()
      self.pre_camera2.SceneGraph.value = SCENEGRAPH.Name.value
      self.pre_camera2.LeftScreen.value = self.camera.LeftScreen.value
      self.pre_camera2.RightScreen.value = self.camera.RightScreen.value
      self.pre_camera2.LeftEye.value = self.camera.LeftEye.value
      self.pre_camera2.RightEye.value = self.camera.RightEye.value
      self.pre_camera2.RenderMask.value = "!main_scene && !pre_scene1 && !do_not_display_group && !avatar_group_" + str(self.platform_id) + " && !couple_group_" + str(self.platform_id)

      self.pre_pipeline2 = avango.gua.nodes.Pipeline()
      self.pre_pipeline2.Camera.value = self.pre_camera2
      self.pre_pipeline2.Enabled.value = self.pipeline.Enabled.value
      self.pre_pipeline2.EnableStereo.value = self.pipeline.EnableStereo.value
      self.pre_pipeline2.LeftResolution.value = self.pipeline.LeftResolution.value
      self.pre_pipeline2.RightResolution.value = self.pipeline.RightResolution.value
      self.pre_pipeline2.OutputTextureName.value = "pre_scene2_texture"
      self.pre_pipeline2.EnableFrustumCulling.value = True
      self.pre_pipeline2.EnableBackfaceCulling.value = True
      self.pre_pipeline2.EnableSsao.value = False
      self.pre_pipeline2.FogStart.value = 850.0
      self.pre_pipeline2.FogEnd.value = 1000.0
      self.pre_pipeline2.EnableFog.value = True
      self.pre_pipeline2.FogColor.value = avango.gua.Color(1.0, 1.0, 1.0)
      self.pre_pipeline2.AmbientColor.value = avango.gua.Color(0.2, 0.4, 0.5)
      self.pre_pipeline2.BackgroundTexture.value = "/opt/guacamole/resources/skymaps/bright_sky.jpg"
      self.pre_pipeline2.BackgroundMode.value = avango.gua.BackgroundMode.SKYMAP_TEXTURE

      self.pre_camera1 = avango.gua.nodes.Camera()
      self.pre_camera1.SceneGraph.value = SCENEGRAPH.Name.value
      self.pre_camera1.LeftScreen.value = self.camera.LeftScreen.value
      self.pre_camera1.RightScreen.value = self.camera.RightScreen.value
      self.pre_camera1.LeftEye.value = self.camera.LeftEye.value
      self.pre_camera1.RightEye.value = self.camera.RightEye.value
      self.pre_camera1.RenderMask.value = "!main_scene && !pre_scene2 && !do_not_display_group && !avatar_group_" + str(self.platform_id) + " && !couple_group_" + str(self.platform_id)


      self.pre_pipeline1 = avango.gua.nodes.Pipeline()
      self.pre_pipeline1.Camera.value = self.pre_camera1
      self.pre_pipeline1.Enabled.value = self.pipeline.Enabled.value
      self.pre_pipeline1.EnableStereo.value = self.pipeline.EnableStereo.value
      self.pre_pipeline1.LeftResolution.value = self.pipeline.LeftResolution.value
      self.pre_pipeline1.RightResolution.value = self.pipeline.RightResolution.value
      self.pre_pipeline1.OutputTextureName.value = "pre_scene1_texture"
      self.pre_pipeline1.PreRenderPipelines.value = [self.pre_pipeline2]
      self.pre_pipeline1.EnableFrustumCulling.value = True
      self.pre_pipeline1.EnableBackfaceCulling.value = True
      self.pre_pipeline1.EnableSsao.value = False
      self.pre_pipeline1.BackgroundTexture.value = "pre_scene2_texture"
      self.pre_pipeline1.BackgroundMode.value = avango.gua.BackgroundMode.QUAD_TEXTURE

      #'''
      self.pipeline.PreRenderPipelines.value = [self.pre_pipeline1]
      self.pipeline.EnableFrustumCulling.value = True
      self.pipeline.EnableBackfaceCulling.value = False
      self.pipeline.EnableSsao.value = False
      self.pipeline.BackgroundMode.value = avango.gua.BackgroundMode.QUAD_TEXTURE
      self.pipeline.BackgroundTexture.value = "pre_scene1_texture"
      self.pipeline.EnableSsao.value = False
      self.pipeline.FogStart.value = 850.0
      self.pipeline.FogEnd.value = 1000.0
      self.pipeline.EnableFog.value = False
      #'''

    else:

      self.pipeline.BackgroundMode.value = avango.gua.BackgroundMode.SKYMAP_TEXTURE
      self.pipeline.BackgroundTexture.value = "/opt/guacamole/resources/skymaps/bright_sky.jpg"


    '''
      General user settings
    '''

    # add tracking reader to avoid latency
    self.init_local_tracking_override(None, avango.gua.make_identity_mat(), avango.gua.make_identity_mat())

    # set display string and warpmatrices as given by the display
    if len(self.display_values) > 1:
      self.set_warpmatrices(self.window, self.display_values[1])

    # append pipeline to the viewer
    VIEWER.Pipelines.value.append(self.pipeline)

    self.always_evaluate(True)

  ## Adds a tracking reader to the view instance.
  # @param TRACKING_TARGET_NAME The target name of the tracked object as chosen in daemon.
  # @param TRANSMITTER_OFFSET The transmitter offset to be applied.
  # @param NO_TRACKING_MAT The matrix to be applied if no valid tracking target was specified.
  def init_local_tracking_override(self, TRACKING_TARGET_NAME, TRANSMITTER_OFFSET, NO_TRACKING_MAT):

    ## @var TRACKING_TARGET_NAME
    # The target name of the tracked object as chosen in daemon.
    self.TRACKING_TARGET_NAME = TRACKING_TARGET_NAME

    ## @var TRANSMITTER_OFFSET
    # The transmitter offset to be applied.
    self.TRANSMITTER_OFFSET = TRANSMITTER_OFFSET

    ## @var NO_TRACKING_MAT
    # Matrix to be applied if no headtracking is available.
    self.NO_TRACKING_MAT = NO_TRACKING_MAT

    ## @var headtracking_reader
    # Instance of a child class of ClientTrackingReader to supply translation input.
    if self.TRACKING_TARGET_NAME != None:
      self.headtracking_reader = ClientTrackingTargetReader()
      self.headtracking_reader.my_constructor(TRACKING_TARGET_NAME)
      self.headtracking_reader.set_transmitter_offset(TRANSMITTER_OFFSET)
      self.headtracking_reader.set_receiver_offset(avango.gua.make_identity_mat())
      print_message("Client tracking update - Slot " + str(self.slot_id) + ": Connected to tracking reader with target " + str(self.TRACKING_TARGET_NAME))

  ## Sets the warp matrices if there is a correct amount of them.
  # @param WINDOW The window instance to apply the warp matrices to.
  # @param WARPMATRICES A list of warp matrices to be applied if there are enough of them.
  def set_warpmatrices(self, WINDOW, WARPMATRICES):

    if len(WARPMATRICES) == 6:
      WINDOW.WarpMatrixRedRight.value    = WARPMATRICES[0]
      WINDOW.WarpMatrixGreenRight.value  = WARPMATRICES[1]
      WINDOW.WarpMatrixBlueRight.value   = WARPMATRICES[2]

      WINDOW.WarpMatrixRedLeft.value     = WARPMATRICES[3]
      WINDOW.WarpMatrixGreenLeft.value   = WARPMATRICES[4]
      WINDOW.WarpMatrixBlueLeft.value    = WARPMATRICES[5]

  ##
  def create_portal_preview(self, LOCAL_PORTAL_NODE):
    _pre_view = PortalPreView()
    _pre_view.my_constructor(LOCAL_PORTAL_NODE, self)
    self.portal_pre_views.append(_pre_view)

  ##
  def remove_portal_preview(self, LOCAL_PORTAL_NODE):

    _pre_views_to_remove = []

    for _pre_view in self.portal_pre_views:
      if _pre_view.compare_portal_node(LOCAL_PORTAL_NODE) == True:
        _pre_views_to_remove.append(_pre_view)

    for _pre_view in _pre_views_to_remove:
      print "Remove a pre view"
      _pre_view.deactivate()
      self.portal_pre_views.remove(_pre_view)
      del _pre_view
      print "New list of pre views", self.portal_pre_views

  ## Called whenever sf_pipeline_string changes.
  @field_has_changed(sf_pipeline_string)
  def sf_pipeline_string_changed(self):

    _splitted_string = self.sf_pipeline_string.value.split("#")

    print "set to", _splitted_string
    '''
    # Note: Calling avango.gua.create_texture during runtime causes the application
    # to crash. All textures have to be preloaded, for example in ClientPipelineValues.py
    # avango.gua.create_texture(_splitted_string[0])

    if self.display_render_mask == "!main_scene":
      self.pipeline.BackgroundMode.value = avango.gua.BackgroundMode.COLOR
      self.pipeline.BackgroundColor.value = avango.gua.Color(0.2, 0.45, 0.6)
    else:
      self.pipeline.BackgroundMode.value = avango.gua.BackgroundMode.SKYMAP_TEXTURE
      self.pipeline.BackgroundTexture.value = _splitted_string[0]
      self.pipeline.FogTexture.value = _splitted_string[0]

    if _splitted_string[1] == "True":
      self.pipeline.EnableBloom.value = True
    else:
      self.pipeline.EnableBloom.value = False

    self.pipeline.BloomIntensity.value = float(_splitted_string[2])
    self.pipeline.BloomThreshold.value = float(_splitted_string[3])
    self.pipeline.BloomRadius.value = float(_splitted_string[4])

    if _splitted_string[5] == "True":
      self.pipeline.EnableSsao.value = True
    else:
      self.pipeline.EnableSsao.value = False

    self.pipeline.SsaoRadius.value = float(_splitted_string[6])
    self.pipeline.SsaoIntensity.value = float(_splitted_string[7])

    if _splitted_string[8] == "True":
      self.pipeline.EnableBackfaceCulling.value = True
    else:
      self.pipeline.EnableBackfaceCulling.value = False

    if _splitted_string[9] == "True":
      self.pipeline.EnableFrustumCulling.value = True
    else:
      self.pipeline.EnableFrustumCulling.value = False

    if _splitted_string[10] == "True":
      self.pipeline.EnableFXAA.value = True
    else:
      self.pipeline.EnableFXAA.value = False

    _ambient_color_values = _splitted_string[11].split(",")
    _ambient_color = avango.gua.Color(float(_ambient_color_values[0]), float(_ambient_color_values[1]), float(_ambient_color_values[2]))
    self.pipeline.AmbientColor.value = _ambient_color

    if _splitted_string[12] == "True":
      self.pipeline.EnableFog.value = True
    else:
      self.pipeline.EnableFog.value = False

    self.pipeline.FogStart.value = float(_splitted_string[13])
    self.pipeline.FogEnd.value = float(_splitted_string[14])
    self.pipeline.NearClip.value = float(_splitted_string[15])
    self.pipeline.FarClip.value = float(_splitted_string[16])
    '''
    #avango.gua.reload_materials()

  ## Evaluated every frame.
  def evaluate(self):

    try:
      _pipeline_info_node = self.SCENEGRAPH["/net/pipeline_values"].Children.value[0]
    except:
      return

    # connect sf_pipeline_string with Name field of info node once
    if _pipeline_info_node != None and self.sf_pipeline_string.value == "":
      self.sf_pipeline_string.connect_from(_pipeline_info_node.Name)


    if hyperspace_config.toggle_transparency:

      if time.time() < hyperspace_config.toggle_transparency_end_time:
        _val_inc = (hyperspace_config.toggle_transparency_end_val - hyperspace_config.toggle_transparency_start_val)
        _time_factor = max(min((hyperspace_config.toggle_transparency_end_time - time.time()) / hyperspace_config.toggle_transparency_duration, 1.0), 0.0)

        avango.gua.set_material_uniform("data/materials/bwb/Glass2.gmd", "transparency", hyperspace_config.toggle_transparency_start_val + _val_inc * _time_factor)
      else:
        hyperspace_config.toggle_transparency = False


    # local tracking update code, does not noticeably increase performance
    '''
    _node_to_update = self.SCENEGRAPH["/net/platform_" + str(self.platform_id) + "/scale/s" + str(self.screen_num) + "_slot" + str(self.slot_id)]

    # return when scenegraph is not yet present
    if _node_to_update == None:
      return

    # get this slot's information node containing the tracking target and transmitter offset
    _information_node = _node_to_update.Children.value[0]

    # get this slot's no tracking node containing the no tracking matrix
    _no_tracking_node = _information_node.Children.value[0]

    _tracking_target_name = _information_node.Name.value

    if _tracking_target_name == "None":
      _tracking_target_name = None

    # create new tracking reader when tracking target properties change
    if _tracking_target_name != self.TRACKING_TARGET_NAME or \
       self.TRANSMITTER_OFFSET != _information_node.Transform.value or \
       self.NO_TRACKING_MAT != _no_tracking_node.Transform.value:

      self.init_local_tracking_override(_tracking_target_name, _information_node.Transform.value, _no_tracking_node.Transform.value)

    # when no value is to be updated, stop evaluation
    if self.TRACKING_TARGET_NAME == None:
      return

    # update slot node
    # TODO: Consider ONLY_TRANSLATION_UPDATE
    if _node_to_update != None:
      _node_to_update.Transform.value = self.headtracking_reader.sf_tracking_mat.value
   '''
