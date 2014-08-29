


## hyperspace scenes
# a list of scenes or a single scene that is loaded;
# the first scene is activated by default
#
scenes = {
    0: "SceneVRHyperspace0(self, SCENEGRAPH, NET_TRANS_NODE)" # default plane
  , 1: "SceneVRHyperspace1(self, SCENEGRAPH, NET_TRANS_NODE)" # entering the plane
  , 2: "SceneVRHyperspace2(self, SCENEGRAPH, NET_TRANS_NODE)" # virtual air steward (flight instructions & bar)
  , 3: "SceneVRHyperspace3(self, SCENEGRAPH, NET_TRANS_NODE)" # transparent plane
  , 4: "SceneVRHyperspace4(self, SCENEGRAPH, NET_TRANS_NODE)" # sky window
  , 5: "SceneVRHyperspace5(self, SCENEGRAPH, NET_TRANS_NODE)" # office meeting
  , 6: "SceneVRHyperspace6(self, SCENEGRAPH, NET_TRANS_NODE)" # office meeting & barchart
  , 7: "SceneVRHyperspace7(self, SCENEGRAPH, NET_TRANS_NODE)" # avatar call
}

active_scenes = [3, 4]

stereo = False

animation_nodes = {
  3: [ "/net/SceneVRHyperspace3/terrain_group" ],
  4: [ "/net/SceneVRHyperspace4/terrain_group" ]
}


# this flag is set automatically, nothing to do here
prepipes = (3 in active_scenes) or (4 in active_scenes)
