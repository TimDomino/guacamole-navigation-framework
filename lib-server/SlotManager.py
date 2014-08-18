#!/usr/bin/python

## @file
# Contains class SlotManager.

# import avango-guacamole libraries
import avango
import avango.gua
import avango.script
#import RadioMasterHID

# import framework libraries
from ConsoleIO   import *
from display_config import INTELLIGENT_SHUTTER_SWITCHING

# import python libraries
from copy import copy
import atexit

## @var total_number_of_shutter_glasses
total_number_of_shutter_glasses = 6

## Class to handle shutter configurations and timings. Associates the users per display to
# the available slots and sets the glasses correctly.
class SlotManager(avango.script.Script):

  ## Default constructor
  def __init__(self):
    self.super(SlotManager).__init__()
    self.always_evaluate(True)

    ## @var glasses_slot_status
    # List containing the number of slots for shutter glasses per display.
    # Form: [ [DISPLAY_NAME, [LIST OF SLOTS PER SHUTTER] ], ...  ]
    self.glasses_slot_status = []

  ## Custom constructor.
  # @param USER_LIST Reference to a list of all users in the setup.
  def my_constructor(self, USER_LIST):

    ## @var users
    # Reference to a list of all users to be handled in the setup.
    self.users = USER_LIST

    ## @var slots
    # Dictionary to map Display instances to a list of associated Slot instances.
    self.slots = dict()

    ## @var queued_commands
    # Format: [string list, frames] A list of commands in string form that are executed in x frames in the future.
    self.queued_commands = []

    # do not create RadioMasterHID when intelligent shutter switching is off
    if INTELLIGENT_SHUTTER_SWITCHING == False:
      return

    ''' Rest of function only executed when INTELLIGENT_SHUTTER_SWITCHING is switched on '''

    ## @var radio_master_hid
    # Instance of RadioMasterHID to handle shutter glass configurations.
    self.radio_master_hid = RadioMasterHID.RadioMaster()

    print_headline("Initializing RadioMasterHID")

    # Open HID shutter communication device
    _open_hid_output = self.radio_master_hid.openHID()

    if _open_hid_output.startswith("error"):
      print_error("openHID() - " + _open_hid_output, False)
    else:
      print_message("openHID() - " + _open_hid_output)

    # reset to default shutter configuration and register reset function on close
    self.reset_shutter_config("/opt/shutterConfig/DLP_1vip456_2tv3tv.xml")
    atexit.register(self.reset_shutter_config, INITIAL_CONFIGURATION = "/opt/shutterConfig/DLP_1vip456_2tv3tv.xml")

  ## Loads an XML shutter configuration and uploads it.
  def reset_shutter_config(self, INITIAL_CONFIGURATION):

    # load initial shutter configuration
    _load_config_output = self.radio_master_hid.load_config(INITIAL_CONFIGURATION)

    if _load_config_output != 0:
      print_error("load_config() - Failed to load shutter configuration " + INITIAL_CONFIGURATION, False)
    else:
      print_message("load_config() - Loaded shutter configuration " + INITIAL_CONFIGURATION)

    # send initial shutter configuration
    self.send_shutter_config(False)

    # set and send master configuration settings
    self.radio_master_hid.set_master_transmit(1)
    self.radio_master_hid.set_master_clock(1) # 0 = use internal sync signal; 1 = use external sync signal
    self.radio_master_hid.set_master_timing(16600,16500)
    self.radio_master_hid.send_master_config()

  ## Tells the RadioMasterHID to send the shutter configuration. Formats feedback nicely.
  # @param PRINT_CONFIG Boolean saying if the newly uploaded configuration is to be printed on the console.
  def send_shutter_config(self, PRINT_CONFIG):

    _send_output = self.radio_master_hid.send_shutter_config()

    if _send_output.startswith("error"):
      print_error("send_shutter_config() - " + _send_output, False)
    else:
      print_message("send_shutter_config() - " + _send_output)

    if PRINT_CONFIG:
      self.print_uploaded_shutter_config()

  ## Prints the currently uploaded shutter configuration including timings and values.
  def print_uploaded_shutter_config(self):

    print_headline("Currently uploaded shutter configuration")

    # print global settings
    print "Ext clock:", self.radio_master_hid.get_master_clock(), "Transmit:", self.radio_master_hid.get_master_transmit()
    print "Timings:", self.radio_master_hid.get_master_period(), self.radio_master_hid.get_master_offset(), "\n"

    # print all timings and values for each shutter
    ids = list(self.radio_master_hid.get_ids())
    for _id in ids:
      print_subheadline("Shutter " + str(_id) + " " + str(self.radio_master_hid.get_description(_id)) + " " + str(hex(self.radio_master_hid.get_init_value(_id)) + ":"))
      ec = self.radio_master_hid.get_event_count(_id)
      for e in range(ec):
        print self.radio_master_hid.get_timer_value(_id, e), hex(self.radio_master_hid.get_shutter_value(_id, e))
      print " "

    # add glasses slot status list to print
    print self.glasses_slot_status

  ## Checks if a given Display instance has a slot left to give away to another user.
  # @param DISPLAY The Display instance to be checked for a free slot.
  def display_has_free_slot(self, DISPLAY):

    # count users at DISPLAY
    _num_of_users = 0

    for _user in self.users:
      if _user.current_display == DISPLAY:
        _num_of_users += 1

    # compare to number of available slots
    if _num_of_users == len(DISPLAY.displaystrings):
      return False
    else:
      return True


  ## Tells the SlotManager that a new Slot instance is to be handled for a certain Display instance.
  # @param SLOT The Slot instance to register.
  # @param DISPLAY The Display instance to which the new slot belongs to.
  def register_slot(self, SLOT, DISPLAY):
    if DISPLAY in self.slots:
      _slot_list = self.slots[DISPLAY]
      _slot_list.append(SLOT)
      self.slots[DISPLAY] = _slot_list
    else:
      self.slots[DISPLAY] = [SLOT]
      self.glasses_slot_status.append([DISPLAY.name, [0 for i in range(total_number_of_shutter_glasses)]])


  ## Evaluated every frame.
  def evaluate(self):

    _entries_to_clear = []

    # handle queued commands
    for _entry in self.queued_commands:

      # reduce frames in which the commands are executed
      _entry[1] -= 1

      if _entry[1] == 0:
        _entries_to_clear.append(_entry)


    # clear commands when frame counter is zero
    for _i in range(len(_entries_to_clear)):

      _entry = _entries_to_clear[_i]

      for _command in _entry[0]:
        try:
          eval(_command)
        except:
          print_error("Could not execute command " + _entry[0], False)

      self.queued_commands.remove(_entry)

      # Only print newly uploaded shutter config when last entry was cleared
      if _i == len(_entries_to_clear) - 1:
        self.send_shutter_config(True)
      else:
        self.send_shutter_config(False)

  ## Registers a list of string commands to be executed in some frames in the future.
  # @param COMMAND_LIST A list of strings containing the commands.
  # @param FRAMES Number of frames in which the commands are to be executed.
  def queue_commands(self, COMMAND_LIST, FRAMES):
    self.queued_commands.append([COMMAND_LIST, FRAMES])


  ## Updates the shutter timings and scenegraph slot connections according to the
  # vip / active status, display and platform of users.
  def update_slot_configuration(self):

    # List to save for which glasses a configuration was set
    if INTELLIGENT_SHUTTER_SWITCHING:

      for _i in range(total_number_of_shutter_glasses):
        self.radio_master_hid.set_shutter_const(_i + 1, int("22", 16), 1)  # activate all shutter glasses

    # loop over all displays to be handled
    for _display in self.slots:

      # check if current display is a stereo one
      _stereo = True
      if _display.stereo == False:
        _stereo = False

      _default_user_list = []
      _vip_user_list = []
      _disabled_user_list = []
      _concatenated_user_list = []
      _num_users_on_display = 0

      # fill user lists for this display
      for _user in self.users:

        if _user.current_display != _display:
          continue

        _num_users_on_display += 1

        # inactive user
        if _user.is_active == False:
          _disabled_user_list.append([_user, 0])

        # active user
        elif _user.is_vip == False:
          _default_user_list.append([_user, 1])

        # active user and vip
        else:
          _vip_user_list.append([_user, 1])

      # get free slots still to be distributed
      _number_free_slots = len(self.slots[_display]) - len(_default_user_list) - len(_vip_user_list)

      # do not distribute free slots when intelligent shutter switching is off
      if INTELLIGENT_SHUTTER_SWITCHING == False:
        _concatenated_user_list = _default_user_list + _vip_user_list + _disabled_user_list

      # if vip users are present, distribute the free slots among them
      elif len(_vip_user_list) > 0:
        _i = 0

        while _number_free_slots > 0:
          # add slot to vip user _i
          _vip_user_list[_i][1] += 1
          _i += 1

          # start again when at end of list
          if _i == len(_vip_user_list):
            _i = 0

          _number_free_slots -= 1

        _concatenated_user_list = _default_user_list + _vip_user_list + _disabled_user_list

      # all users are disabled
      elif _num_users_on_display == len(_disabled_user_list):
        _concatenated_user_list = _disabled_user_list

      # all users are default users, distribute remaining slots among them
      else:
        _i = 0

        while _number_free_slots > 0:
          # add slot to default user _i
          _default_user_list[_i][1] += 1
          _i += 1

          # start again when at end of list
          if _i == len(_default_user_list):
            _i = 0

          _number_free_slots -= 1

        _concatenated_user_list = _default_user_list + _vip_user_list + _disabled_user_list

      # assign one slot to each user when intelligent switching is off
      _slot_instances = self.slots[_display]

      if INTELLIGENT_SHUTTER_SWITCHING == False:
        _i = 0

        for _state in _concatenated_user_list:
          _slot_instances[_i].assign_user(_state[0])
          _i += 1

        print_warning("Intelligent shutter switching disabled. Assigning one slot for each user," + \
                      " independent from active and vip status.")

        continue

      ''' Rest of functionality only executed when INTELLIGENT_SHUTTER_SWITCHING is switched on '''

      # update shutter values according to slots assigned
      print_headline("User - Slot Assignment on " + str(_display.name))

      # clear all slot connections
      for _slot in _slot_instances:
        _slot.clear_user()

      # get slot assignment list for current display
      _display_slot_assignment = []

      for _entry in self.glasses_slot_status:
        if _entry[0] == _display.name:
          _display_slot_assignment = _entry[1]

      # copy _display_slot_assignment to check for changes in the end
      _old_display_slot_assignment = list(_display_slot_assignment)

      _glasses_updated = [False for i in range(total_number_of_shutter_glasses)]

      # print and update user / glasses slot assignment
      for _state in _concatenated_user_list:
        print "User", _state[0].id, "(VIP:", str(_state[0].is_vip) + ") was assigned " + str(_state[1]) + " slots."

        if _state[0].glasses_id != None:
          _display_slot_assignment[_state[0].glasses_id - 1] = _state[1]

      _i = 0

      for _state in _concatenated_user_list:

        _user = _state[0]
        _number_of_slots = _state[1]

        # warn if a handled user has no glasses id specified
        if _user.glasses_id == None:
          print_warning("Warning: User " + str(_user.id) + " has no glasses id specified.")

        # check if the user has slots assigned to him
        if _number_of_slots > 0:
          if _stereo:

            # get correct opening and closing time according to shutter mode of display
            # PASSIVE_STEREO supports two opening and two closing times valid for both shutters of left and right eyes (4 per slot)
            # ACTIVE_STEREO supports opening and closing times for both shutters of left and right eyes seperately (8 per slot)

            _start_timings_left = _slot_instances[_i].shutter_timing[0]
            _start_timings_right = _slot_instances[_i].shutter_timing[1]
            _start_values_left = _slot_instances[_i].shutter_value[0]
            _start_values_right = _slot_instances[_i].shutter_value[1]
            _start_i = copy(_i)

            _i += (_number_of_slots - 1)

            _end_timings_left = _slot_instances[_i].shutter_timing[0]
            _end_timings_right = _slot_instances[_i].shutter_timing[1]
            _end_values_left = _slot_instances[_i].shutter_value[0]
            _end_values_right = _slot_instances[_i].shutter_value[1]
            _end_i = copy(_i)

            # PASSIVE_STEREO shutter mode
            if _display.get_shutter_mode() == "PASSIVE_STEREO":

              # Note: The terms _left_timings and _right_timings might be misleading here
              # In this case, they are opening and closing times. Unfortunately, this order is not
              # to be changed and in order to avoid redundant code pieces, the naming was chosen as is.

              _left_timings = (_start_timings_left[0], _start_timings_right[0])
              _left_values = (_start_values_left[0], _start_values_right[0])
              _right_timings = (_end_timings_left[1], _end_timings_right[1])
              _right_values = (_end_values_left[1], _end_values_right[1])

              # set event count properly
              if _user.glasses_id != None:
                self.radio_master_hid.set_event_count(_user.glasses_id, 4)

            # ACTIVE_STEREO shutter mode
            else:
              _left_timings = (_start_timings_left[0], _start_timings_left[1], _end_timings_left[2], _end_timings_left[3])
              _right_timings = (_start_timings_right[0], _start_timings_right[1], _end_timings_right[2], _end_timings_right[3])
              _left_values = (_start_values_left[0], _start_values_left[1], _end_values_left[2], _end_values_left[3])
              _right_values = (_start_values_right[0], _start_values_right[1], _end_values_right[2], _end_values_right[3])

              # set event count properly
              if _user.glasses_id != None:
                self.radio_master_hid.set_event_count(_user.glasses_id, 8)

            _j = 0

            # fail if glasses id is too large, else mark the glasses id as updated for this display
            if _user.glasses_id != None:
              if _user.glasses_id > total_number_of_shutter_glasses:
                print_error("Error at user " + str(_user.id) + ": Glasses ID (" + str(_user.glasses_id) + ") exceeds the maximum of available glasses (" + str(total_number_of_shutter_glasses) + ")." , True)
              else:
                _glasses_updated[_user.glasses_id - 1] = True

              # if user glasses are closing, do it immediately (slot image already present)
              if _display_slot_assignment[_user.glasses_id - 1] <= _old_display_slot_assignment[_user.glasses_id - 1]:

                # set ids with shutter timings and values properly
                while _j < len(_left_timings):
                  self.radio_master_hid.set_timer_value(_user.glasses_id, _j, _left_timings[_j])
                  self.radio_master_hid.set_shutter_value(_user.glasses_id, _j, int(str(_left_values[_j]), 16))
                  _j += 1

                while _j < 2 * len(_left_timings):
                  self.radio_master_hid.set_timer_value(_user.glasses_id, _j, _right_timings[_j - len(_left_timings)])
                  self.radio_master_hid.set_shutter_value(_user.glasses_id, _j, int(str(_right_values[_j - len(_left_timings)]), 16))
                  _j += 1

              # if the user glasses are opening, wait for some frames (new slot image not yet present)
              else:

                # set ids with shutter timings and values properly, queue the commands
                _command_list = []
                '''
                # set ids with shutter timings and values properly
                while _j < len(_left_timings):
                  self.radio_master_hid.set_timer_value(_user.glasses_id, _j, _left_timings[_j])
                  self.radio_master_hid.set_shutter_value(_user.glasses_id, _j, int(str(_left_values[_j]), 16))
                  _j += 1

                while _j < 2 * len(_left_timings):
                  self.radio_master_hid.set_timer_value(_user.glasses_id, _j, _right_timings[_j - len(_left_timings)])
                  self.radio_master_hid.set_shutter_value(_user.glasses_id, _j, int(str(_right_values[_j - len(_left_timings)]), 16))
                  _j += 1

                '''
                while _j < len(_left_timings):
                  _command_list.append("self.radio_master_hid.set_timer_value(" + str(_user.glasses_id) + "," + str(_j) + "," + str(_left_timings[_j]) + ")")
                  self.radio_master_hid.set_shutter_value(_user.glasses_id, _j, int(str(_left_values[_j]), 16))
                  _j += 1

                while _j < 2 * len(_left_timings):
                  _command_list.append("self.radio_master_hid.set_timer_value(" + str(_user.glasses_id) + "," + str(_j) + "," + str(_right_timings[_j - len(_left_timings)]) + ")")
                  self.radio_master_hid.set_shutter_value(_user.glasses_id, _j, int(str(_right_values[_j - len(_left_timings)]), 16))
                  _j += 1

                self.queue_commands(_command_list, 9)


            # assign user to slot instances (headtracking matrix update)
            for _k in range(_start_i, _end_i + 1):
              _slot_instances[_k].assign_user(_user)

            _i += 1

          # mono display
          else:
            _start_i = copy(_i)
            _i += (_number_of_slots - 1)
            _end_i = copy(_i)

            # assign user to slot instances
            for _k in range(_start_i, _end_i + 1):
              _slot_instances[_k].assign_user(_user)

              _i += 1

      # set number of assigned slots to 0 if the glasses were not handled
      for _i in range(total_number_of_shutter_glasses):
        if _glasses_updated[_i] == False:
          _display_slot_assignment[_i] = 0


    # open glasses for which no timings were assigned
    if INTELLIGENT_SHUTTER_SWITCHING:
      print_headline("Send updated shutter configuration")
      self.open_unused_shutter_glasses()
      self.send_shutter_config(False)

  ## Determines which shutter glasses have no slots assigned and opens them.
  def open_unused_shutter_glasses(self):
    # determine unused glasses
    _open_glasses = [True for i in range(total_number_of_shutter_glasses)]

    for _i in range(total_number_of_shutter_glasses):

      for _display in self.glasses_slot_status:

        if _display[1][_i] != 0:
          _open_glasses[_i] = False

    # open unused glasses
    for _i in range(total_number_of_shutter_glasses):
      if _open_glasses[_i]:
        print_warning("Opening shutter glasses " + str(_i + 1))
        self.radio_master_hid.set_shutter_const(_i + 1, int("88", 16), 1)
