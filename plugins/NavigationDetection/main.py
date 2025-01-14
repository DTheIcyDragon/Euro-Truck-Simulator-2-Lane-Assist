"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
PluginInfo = PluginInformation(
    name="NavigationDetection",
    description="Uses the navigation line in the minimap.",
    version="3.1",
    author="Glas42",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic",
    dynamicOrder="lane detection",
    exclusive="LaneDetection",
    requires=["DefaultSteering", "bettercamScreenCapture", "TruckSimAPI", "SDKController"]
)

from src.mainUI import switchSelectedPlugin
from src.translator import Translate
from src.mainUI import resizeWindow
import src.variables as variables
import src.settings as settings
import src.controls as controls
import src.helpers as helpers
from src.logger import print
import src.sounds as sounds
from tkinter import ttk
import tkinter as tk

import plugins.DefaultSteering.main as DefaultSteering
import numpy as np
import subprocess
import ctypes
import time
import cv2
import os


controls.RegisterKeybind("Lane change to the left",
                         notBoundInfo="Bind this if you dont want to use the indicators\nto change lanes with the NavigationDetection.",
                         description="Bind this if you dont want to use the indicators\nto change lanes with the NavigationDetection.")

controls.RegisterKeybind("Lane change to the right",
                         notBoundInfo="Bind this if you dont want to use the indicators\nto change lanes with the NavigationDetection.",
                         description="Bind this if you dont want to use the indicators\nto change lanes with the NavigationDetection.")


############################################################################################################################    
# Settings
############################################################################################################################
def LoadSettings():
    global map_topleft
    global map_bottomright
    global arrow_topleft
    global arrow_bottomright

    global arrow_percentage

    global navigationsymbol_x
    global navigationsymbol_y

    global offset

    global trafficlightdetection_is_enabled
    global lefthand_traffic

    global fuel_update_timer
    global fuel_total
    global fuel_current
    global fuel_percentage

    global check_map_timer
    global do_zoom
    global do_blocked
    global mod_enabled
    global allow_playsound
    global allow_playsound_timer

    global controls_last_left
    global controls_last_right

    global left_x_lane
    global right_x_lane
    global left_x_turn
    global right_x_turn
    global left_x_turndrive
    global right_x_turndrive
    global approve_upper_y_left
    global approve_lower_y_left
    global approve_upper_y_right
    global approve_lower_y_right
    
    global detection_offset_lane_y

    global turnincoming_detected
    global turnincoming_direction
    global turnincoming_last_detected

    global indicator_last_left
    global indicator_last_right
    global indicator_left_wait_for_response
    global indicator_right_wait_for_response
    global indicator_left_response_timer
    global indicator_right_response_timer
    global indicator_enable_left
    global indicator_enable_right
    global indicator_changed_by_code

    global lanechanging_do_lane_changing
    global lanechanging_speed
    global lanechanging_width
    global lanechanging_autolanezero
    global lanechanging_current_lane
    global lanechanging_final_offset

    map_topleft = settings.GetSettings("NavigationDetection", "map_topleft", "unset")
    map_bottomright = settings.GetSettings("NavigationDetection", "map_bottomright", "unset")
    arrow_topleft = settings.GetSettings("NavigationDetection", "arrow_topleft", "unset")
    arrow_bottomright = settings.GetSettings("NavigationDetection", "arrow_bottomright", "unset")
    arrow_percentage = settings.GetSettings("NavigationDetection", "arrow_percentage", "unset")

    if map_topleft == "unset":
        map_topleft = None
    if map_bottomright == "unset":
        map_bottomright = None
    if arrow_topleft == "unset":
        arrow_topleft = None
    if arrow_bottomright == "unset":
        arrow_bottomright = None
    if arrow_percentage == "unset":
        arrow_percentage = None
    
    if arrow_topleft != None and arrow_bottomright != None and map_topleft != None and map_bottomright != None:
        navigationsymbol_x = round((arrow_topleft[0] + arrow_bottomright[0]) / 2 - map_topleft[0])
        navigationsymbol_y = round((arrow_topleft[1] + arrow_bottomright[1]) / 2 - map_topleft[1])
    else:
        navigationsymbol_x = 0
        navigationsymbol_y = 0

    offset = settings.GetSettings("NavigationDetection", "offset", 0)

    if "TrafficLightDetection" in settings.GetSettings("Plugins", "Enabled", []):
        trafficlightdetection_is_enabled = True
    else:
        trafficlightdetection_is_enabled = False

    lefthand_traffic = settings.GetSettings("NavigationDetection", "lefthand_traffic", False)

    fuel_update_timer = 0
    fuel_total = 0
    fuel_current = 0
    fuel_percentage = 100

    check_map_timer = 0
    do_zoom = False
    do_blocked = False
    mod_enabled = False
    allow_playsound = False
    allow_playsound_timer = time.time()

    controls_last_left = False
    controls_last_right = False

    left_x_lane = 0
    right_x_lane = 0
    left_x_turn = 0
    right_x_turn = 0
    left_x_turndrive = 0
    right_x_turndrive = 0
    approve_upper_y_left = 0
    approve_lower_y_left = 0
    approve_upper_y_right = 0
    approve_lower_y_right = 0

    detection_offset_lane_y = 0

    turnincoming_detected = False
    turnincoming_direction = None
    turnincoming_last_detected = 0

    indicator_last_left = False
    indicator_last_right = False
    indicator_left_wait_for_response = False
    indicator_right_wait_for_response = False
    indicator_left_response_timer = 0
    indicator_right_response_timer = 0
    indicator_enable_left = False
    indicator_enable_right = False
    indicator_changed_by_code = True

    lanechanging_do_lane_changing = settings.GetSettings("NavigationDetection", "lanechanging_do_lane_changing", True)
    lanechanging_speed = settings.GetSettings("NavigationDetection", "lanechanging_speed", 1)
    lanechanging_width = settings.GetSettings("NavigationDetection", "lanechanging_width", 10)
    lanechanging_autolanezero = settings.GetSettings("NavigationDetection", "lanechanging_autolanezero", True)
    lanechanging_current_lane = 0
    lanechanging_final_offset = 0
LoadSettings()


def plugin(data):
############################################################################################################################
# Code
############################################################################################################################
    global map_topleft
    global map_bottomright
    global arrow_topleft
    global arrow_bottomright

    global arrow_percentage

    global navigationsymbol_x
    global navigationsymbol_y

    global offset

    global trafficlightdetection_is_enabled
    global lefthand_traffic

    global fuel_update_timer
    global fuel_total
    global fuel_current
    global fuel_percentage

    global check_map_timer
    global do_zoom
    global do_blocked
    global mod_enabled
    global allow_playsound
    global allow_playsound_timer

    global controls_last_left
    global controls_last_right

    global left_x_lane
    global right_x_lane
    global left_x_turn
    global right_x_turn
    global left_x_turndrive
    global right_x_turndrive
    global approve_upper_y_left
    global approve_lower_y_left
    global approve_upper_y_right
    global approve_lower_y_right
    
    global detection_offset_lane_y

    global turnincoming_detected
    global turnincoming_direction
    global turnincoming_last_detected

    global indicator_last_left
    global indicator_last_right
    global indicator_left_wait_for_response
    global indicator_right_wait_for_response
    global indicator_left_response_timer
    global indicator_right_response_timer
    global indicator_enable_left
    global indicator_enable_right
    global indicator_changed_by_code

    global lanechanging_do_lane_changing
    global lanechanging_speed
    global lanechanging_width
    global lanechanging_autolanezero
    global lanechanging_current_lane
    global lanechanging_final_offset
    
    current_time = time.time()
    
    try:
        frame = data["frame"]
        width = frame.shape[1]
        height = frame.shape[0]
    except:
        return data

    if frame is None: return data
    
    if isinstance(frame, np.ndarray) and frame.ndim == 3 and frame.size > 0:
        valid_frame = True
    else:
        valid_frame = False
        return data
    
    try:
        gamepaused = data["api"]["pause"]
        if gamepaused == True:
            speed = 0
        else:
            speed = round(data["api"]["truckFloat"]["speed"]*3.6, 2)
    except:
        gamepaused = False
        speed = 0

    if current_time > fuel_update_timer + 5:
        fuel_update_timer = current_time
        try:
            fuel_total = data["api"]["configFloat"]["fuelCapacity"]
            fuel_current = data["api"]["truckFloat"]["fuel"]
            if fuel_total != 0:
                fuel_percentage = (fuel_current/fuel_total)*100
            else:
                fuel_percentage = 100
        except:
            fuel_total = 0
            fuel_current = 0
            fuel_percentage = 100

    try:
        indicator_left = data["api"]["truckBool"]["blinkerLeftActive"]
        indicator_right = data["api"]["truckBool"]["blinkerRightActive"]
    except:
        indicator_left = False
        indicator_right = False

    if trafficlightdetection_is_enabled == True:
        try:
            trafficlight = data["TrafficLightDetection"]["simple"]
        except:
            trafficlight = None
            if "TrafficLightDetection" not in settings.GetSettings("Plugins", "Enabled", []):
                trafficlightdetection_is_enabled = False
                trafficlight = "Off"
    else:
        trafficlight = "Off"

    f5_key_state = ctypes.windll.user32.GetAsyncKeyState(0x74)
    f5_pressed = f5_key_state & 0x8000 != 0
    
    if f5_pressed == True or do_blocked == True or do_zoom == True:
        check_map_timer = current_time
    
    if current_time - 1 < check_map_timer or check_map_timer == 0:
        check_map = True
    else:
        check_map = False

    if check_map == True:
        if map_topleft != None and map_bottomright != None and arrow_topleft != None and arrow_bottomright != None and map_topleft[0] < map_bottomright[0] and map_topleft[1] < map_bottomright[1] and arrow_topleft[0] < arrow_bottomright[0] and arrow_topleft[1] < arrow_bottomright[1]:
            lower_blue = np.array([121, 68, 0])
            upper_blue = np.array([250, 184, 109])
            mask_blue = cv2.inRange(frame[arrow_topleft[1] - map_topleft[1]:arrow_bottomright[1] - map_bottomright[1], arrow_topleft[0] - map_topleft[0]:arrow_bottomright[0] - map_bottomright[0]], lower_blue, upper_blue)
            arrow_height, arrow_width = mask_blue.shape[:2]
            pixel_ratio = round(cv2.countNonZero(mask_blue) / (arrow_width * arrow_height), 3)
        else:
            pixel_ratio = 0

        if arrow_percentage != None:
            if pixel_ratio > arrow_percentage * 0.85 and pixel_ratio < arrow_percentage * 1.15:
                do_zoom = False
            else:
                do_zoom = True
            if pixel_ratio < 0.01:
                do_blocked = True
            else:
                do_blocked = False
        else:
            do_zoom = False
            do_blocked = False
        if check_map_timer == 0:
            check_map_timer = current_time
        
        lower_green = np.array([0, 200, 0])
        upper_green = np.array([230, 255, 150])
        mask_green = cv2.inRange(frame, lower_green, upper_green)
        if cv2.countNonZero(mask_green) > 0:
            mod_enabled = False
        else:
            mod_enabled = True
    
    if mod_enabled == False:
        lower_red = np.array([0, 0, 160])
        upper_red = np.array([110, 110, 255])
        lower_green = np.array([0, 200, 0])
        upper_green = np.array([230, 255, 150])
        white_limit = 1

        mask_red = cv2.inRange(frame, lower_red, upper_red)
        mask_green = cv2.inRange(frame, lower_green, upper_green)

        frame_with_mask = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
    else:
        lower_red = np.array([0, 0, 160])
        upper_red = np.array([110, 110, 255])
        white_limit = 1

        mask_red = cv2.inRange(frame, lower_red, upper_red)

        frame_with_mask = cv2.bitwise_and(frame, frame, mask=mask_red)

    cv2.rectangle(frame_with_mask, (0,0), (round(width/6),round(height/3)),(0,0,0),-1)
    cv2.rectangle(frame_with_mask, (width,0), (round(width-width/6),round(height/3)),(0,0,0),-1)

    frame_gray = cv2.cvtColor(frame_with_mask, cv2.COLOR_BGR2GRAY)
    frame_gray_unblurred = frame_gray.copy()

    frame_gray = cv2.GaussianBlur(frame_gray,(3,3),0)

    frame = cv2.cvtColor(frame_gray_unblurred, cv2.COLOR_BGR2RGB)
    
    y_coordinate_of_lane = round(navigationsymbol_y / 1.3)
    y_coordinate_of_turn = round(navigationsymbol_y / 4) 
    automatic_x_offset = round(width/2-navigationsymbol_y)

    def GetArrayOfLaneEdges(y_coordinate_of_detection, tilt, x_offset, y_offset):
        detectingLane = False
        laneEdges = []

        for x in range(0, int(width)):
            
            y = round(y_coordinate_of_detection + y_offset + (navigationsymbol_x - x + x_offset) * tilt)
            if y < 0:
                y = 0
            if y > height - 1:
                y = height - 1

            pixel = frame_gray[y, x]
            if (white_limit <= pixel):
                
                if not detectingLane:
                    detectingLane = True
                    laneEdges.append(x - x_offset)
            else:
                if detectingLane:
                    detectingLane = False
                    laneEdges.append(x - x_offset)

        if len(laneEdges) < 2:
            laneEdges.append(width)

        return laneEdges
    
    
    if turnincoming_direction != None:
        if turnincoming_direction == "Left":
            tilt = 0.25
        else:
            tilt = -0.25
    else:
        tilt = 0
    x_offset = lanechanging_final_offset - offset
    y_offset = detection_offset_lane_y
    lanes = GetArrayOfLaneEdges(y_coordinate_of_lane, tilt, x_offset, y_offset)
    try:
        closest_x_pair = min([(left_x, right_x) for left_x, right_x in zip(lanes[::2], lanes[1::2])], key=lambda pair: abs((pair[0] + pair[1]) / 2 - navigationsymbol_x))
        left_x_lane, right_x_lane = closest_x_pair
    except:
        if lefthand_traffic == False:
            left_x_lane = lanes[len(lanes)-2]
            right_x_lane = lanes[len(lanes)-1]
        else:
            try:
                left_x_lane = lanes[len(lanes)-4]
                right_x_lane = lanes[len(lanes)-3]
            except:
                left_x_lane = lanes[len(lanes)-2]
                right_x_lane = lanes[len(lanes)-1]
    
    left_y_lane = round(y_coordinate_of_lane + detection_offset_lane_y + (navigationsymbol_x - left_x_lane - x_offset) * tilt)
    right_y_lane = round(y_coordinate_of_lane + detection_offset_lane_y + (navigationsymbol_x - right_x_lane - x_offset) * tilt)

    tilt = 0
    x_offset = lanechanging_final_offset - offset
    y_offset = 0
    lanes = GetArrayOfLaneEdges(y_coordinate_of_turn, tilt, x_offset, y_offset)
    try:
        closest_x_pair = min([(left_x, right_x) for left_x, right_x in zip(lanes[::2], lanes[1::2])], key=lambda pair: abs((pair[0] + pair[1]) / 2 - navigationsymbol_x))
        left_x_turn, right_x_turn = closest_x_pair
    except:
        if lefthand_traffic == False:
            left_x_turn = lanes[len(lanes)-2]
            right_x_turn = lanes[len(lanes)-1]
        else:
            try:
                left_x_turn = lanes[len(lanes)-4]
                right_x_turn = lanes[len(lanes)-3]
            except:
                left_x_turn = lanes[len(lanes)-2]
                right_x_turn = lanes[len(lanes)-1]

    if left_x_lane + lanechanging_final_offset == width:
        left_x_lane = 0
        left_y_lane = 0
        right_x_lane = 0
        right_y_lane = 0
    if left_x_turn + lanechanging_final_offset == width:
        left_x_turn = 0
        right_x_turn = 0

    width_lane = right_x_lane - left_x_lane
    width_turn = right_x_turn - left_x_turn

    center_x_lane = (left_x_lane + right_x_lane) / 2
    center_x_turn = (left_x_turn + right_x_turn) / 2

    approve_x_left = round(navigationsymbol_x - width/4)
    if approve_x_left >= width:
        approve_x_left = width - 1
    if approve_x_left < 0:
        approve_x_left = 0
    approve_upper_y_left = 0
    approve_lower_y_left = 0
    for y in range(height-1, -1, -1):
        pixel = frame_gray[y, approve_x_left]
        if (white_limit <= pixel):
            if approve_upper_y_left == 0:
                approve_upper_y_left = y
                approve_lower_y_left = y
            else:
                approve_lower_y_left = y
        else:
            if approve_upper_y_left != 0:
                break

    approve_x_right = round(navigationsymbol_x + width/4)
    if approve_x_right >= width:
        approve_x_right = width - 1
    if approve_x_right < 0:
        approve_x_right = 0
    approve_upper_y_right = 0
    approve_lower_y_right = 0
    for y in range(height-1, -1, -1):
        pixel = frame_gray[y, approve_x_right]
        if (white_limit <= pixel):
            if approve_upper_y_right == 0:
                approve_upper_y_right = y
                approve_lower_y_right = y
            else:
                approve_lower_y_right = y
        else:
            if approve_upper_y_right != 0:
                break
    
    if approve_lower_y_left != 0 and approve_lower_y_right != 0:
        current_color = (0, 0, 255)
    else:
        current_color = (0, 255, 0)
    if approve_lower_y_left != 0:
        cv2.line(frame, (approve_x_left, approve_upper_y_left), (approve_x_left, approve_lower_y_left), current_color, 2)
    if approve_lower_y_right != 0:
        cv2.line(frame, (approve_x_right, approve_upper_y_right), (approve_x_right, approve_lower_y_right), current_color, 2)

    if approve_upper_y_left != 0 and approve_upper_y_right != 0:
        if approve_lower_y_left + round((approve_lower_y_left - approve_upper_y_left) / 2) <= y_coordinate_of_lane <= approve_upper_y_left - round((approve_lower_y_left - approve_upper_y_left) / 2) or approve_lower_y_right + round((approve_lower_y_right - approve_upper_y_right) / 2) <= y_coordinate_of_lane <= approve_upper_y_right - round((approve_lower_y_right - approve_upper_y_right) / 2):
            if approve_lower_y_left < approve_lower_y_right:
                distance = round((approve_lower_y_left + approve_lower_y_right) / 2 + (approve_lower_y_left - approve_upper_y_left) / 2) - y_coordinate_of_lane
            else:
                distance = round((approve_lower_y_left + approve_lower_y_right) / 2 + (approve_lower_y_right - approve_upper_y_right) / 2) - y_coordinate_of_lane
            if distance < 0:
                detection_offset_lane_y = distance
            else:
                detection_offset_lane_y = 0
        else:
            detection_offset_lane_y = 0
    else:
        detection_offset_lane_y = 0

    if width_turn == 0:
        if approve_upper_y_left != 0:
            turnincoming_detected = True
            turnincoming_direction = "Left"
        if approve_upper_y_right != 0:
            turnincoming_detected = True
            turnincoming_direction = "Right"
    else:
        turnincoming_detected = False
        turnincoming_direction = None

    if approve_upper_y_left != 0 and approve_upper_y_right != 0:
        turnincoming_detected = False
        turnincoming_direction = None

    if approve_upper_y_left == 0 and approve_upper_y_right == 0:
        turnincoming_detected = False
        turnincoming_direction = None

    if turnincoming_detected == True:
        turnincoming_last_detected = current_time
        if lanechanging_autolanezero == True:
            lanechanging_current_lane = 0
    
    if DefaultSteering.enabled == True:
        enabled = True
    else:
        enabled = False
    try:
        data["sdk"]
    except:
        data["sdk"] = {}
    indicator_changed_by_code = False
    if indicator_left != indicator_last_left:
        indicator_left_wait_for_response = False
    if indicator_right != indicator_last_right:
        indicator_right_wait_for_response = False
    if current_time - 1 > indicator_left_response_timer:
        indicator_left_wait_for_response = False
    if current_time - 1 > indicator_right_response_timer:
        indicator_right_wait_for_response = False
    if turnincoming_direction == "Left" and indicator_left == False and indicator_left_wait_for_response == False and enabled == True:
        data["sdk"]["LeftBlinker"] = True
        indicator_left_wait_for_response = True
        indicator_left_response_timer = current_time
    if turnincoming_direction == "Right" and indicator_right == False and indicator_right_wait_for_response == False and enabled == True:
        data["sdk"]["RightBlinker"] = True
        indicator_right_wait_for_response = True
        indicator_right_response_timer = current_time
    if turnincoming_direction == None and indicator_left == True and indicator_left_wait_for_response == False and current_time - 2 > turnincoming_last_detected and indicator_changed_by_code == True and enabled == True:
        data["sdk"]["LeftBlinker"] = True
        indicator_left_wait_for_response = True
        indicator_left_response_timer = current_time
    if turnincoming_direction == None and indicator_right == True and indicator_right_wait_for_response == False and current_time - 2 > turnincoming_last_detected and indicator_changed_by_code == True and enabled == True:
        data["sdk"]["RightBlinker"] = True
        indicator_right_wait_for_response = True
        indicator_right_response_timer = current_time
    if turnincoming_detected == True:
        indicator_changed_by_code = True
    else:
        indicator_changed_by_code = False
    
    try:
        if controls.GetKeybindFromName("Lane change to the left")['buttonIndex'] != -1:
            controls_left_set = True
            controls_left = controls.GetKeybindValue("Lane change to the left")
        else:
            controls_left_set = False
            controls_left = False
    except:
        controls_left_set = False
        controls_left = False
    try:
        if controls.GetKeybindFromName("Lane change to the right")['buttonIndex'] != -1:
            controls_right_set = True
            controls_right = controls.GetKeybindValue("Lane change to the right")
        else:
            controls_right_set = False
            controls_right = False
    except:
        controls_right_set = False
        controls_right = False

    if enabled == True:
        if controls_left_set == False:
            if indicator_left != indicator_last_left and indicator_left == True and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and current_time - 1 > turnincoming_last_detected:
                lanechanging_current_lane += 1
        else:
            if controls_left == True and controls_last_left == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and current_time - 1 > turnincoming_last_detected:
                if indicator_left == True:
                    lanechanging_current_lane += 1
                elif indicator_left == False and indicator_right_wait_for_response == False:
                    lanechanging_current_lane += 1
                    indicator_enable_left = True
        if controls_right_set == False:
            if indicator_right != indicator_last_right and indicator_right == True and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and current_time - 1 > turnincoming_last_detected:
                lanechanging_current_lane -= 1
        else:
            if controls_right == True and controls_last_right == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and current_time - 1 > turnincoming_last_detected:
                if indicator_right == True:
                    lanechanging_current_lane -= 1
                elif indicator_right == False and indicator_left_wait_for_response == False:
                    lanechanging_current_lane -= 1
                    indicator_enable_right = True

    if indicator_enable_left == True and indicator_left == False and indicator_left_wait_for_response == False and enabled == True:
        data["sdk"]["LeftBlinker"] = True
        indicator_changed_by_code = True
        indicator_left_wait_for_response = True
        indicator_left_response_timer = current_time
    elif indicator_left == True and indicator_left_wait_for_response == False:
        indicator_enable_left = False
    if indicator_enable_right == True and indicator_right == False and indicator_right_wait_for_response == False and enabled == True:
        data["sdk"]["RightBlinker"] = True
        indicator_changed_by_code = True
        indicator_right_wait_for_response = True
        indicator_right_response_timer = current_time
    elif indicator_right == True and indicator_right_wait_for_response == False:
        indicator_enable_right = False

    lanechanging_target_offset = lanechanging_width * lanechanging_current_lane
    lanechanging_current_correction = lanechanging_target_offset - lanechanging_final_offset
    if abs(lanechanging_current_correction) > lanechanging_speed/10:
        if lanechanging_current_correction > 0:
            lanechanging_current_correction = lanechanging_speed/10
        else:
            lanechanging_current_correction = -lanechanging_speed/10
    lanechanging_final_offset += lanechanging_current_correction
    lanechanging_progress = lanechanging_final_offset/lanechanging_width
    
    if lanechanging_progress == lanechanging_current_lane and indicator_left == True and indicator_left_wait_for_response == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and enabled == True and controls_left_set == False:
        data["sdk"]["LeftBlinker"] = True
        indicator_left_wait_for_response = True
        indicator_left_response_timer = current_time
    elif lanechanging_progress == lanechanging_current_lane and indicator_left == True and indicator_left_wait_for_response == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and enabled == True and controls_left_set == True:
        data["sdk"]["LeftBlinker"] = True
        indicator_left_wait_for_response = True
        indicator_left_response_timer = current_time

    if lanechanging_progress == lanechanging_current_lane and indicator_right == True and indicator_right_wait_for_response == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and enabled == True and controls_right_set == False:
        data["sdk"]["RightBlinker"] = True
        indicator_right_wait_for_response = True
        indicator_right_response_timer = current_time
    elif lanechanging_progress == lanechanging_current_lane and indicator_right == True and indicator_right_wait_for_response == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and enabled == True and controls_right_set == True:
        data["sdk"]["RightBlinker"] = True
        indicator_right_wait_for_response = True
        indicator_right_response_timer = current_time

    if width_lane != 0:
        if turnincoming_detected == False:
            correction = navigationsymbol_x - center_x_lane
        else:
            if turnincoming_direction == "Left":
                correction = navigationsymbol_x - center_x_lane - width_lane/40
            else:
                correction = navigationsymbol_x - center_x_lane + width_lane/40
    else:
        correction = 0
        if turnincoming_direction == "Left" and enabled == True:
            data["sdk"]["LeftBlinker"] = False
        if turnincoming_direction == "Right" and enabled == True:
            data["sdk"]["RightBlinker"] = False
        turnincoming_detected = False
        tunincoming_direction = None

    allow_trafficlight_symbol = True
    allow_no_lane_detected = True
    allow_do_blocked = True
    allow_do_zoom = True
    show_turn_line = True
    
    map_detected = True
    
    if map_topleft == None or map_bottomright == None or arrow_topleft == None or arrow_bottomright == None or arrow_percentage == None or map_topleft[0] > map_bottomright[0] or map_topleft[1] > map_bottomright[1] or arrow_topleft[0] > arrow_bottomright[0] or arrow_topleft[1] > arrow_bottomright[1]:
        if allow_playsound == True:
            sounds.PlaysoundFromLocalPath("assets/sounds/info.mp3")
            allow_playsound = False
            allow_playsound_timer = current_time
        frame = cv2.GaussianBlur(frame, (9, 9), 0)
        frame = cv2.addWeighted(frame, 0.5, frame, 0, 0)

        xofinfo = round(width/2)
        yofinfo = round(height/3.5)
        sizeofinfo = round(height/5)
        infothickness = round(height/50)
        if infothickness < 1:
            infothickness = 1
        cv2.circle(frame, (xofinfo,yofinfo), sizeofinfo, (0,127,255), infothickness, cv2.LINE_AA)
        cv2.line(frame, (xofinfo,round(yofinfo+sizeofinfo/2)), (xofinfo,round(yofinfo-sizeofinfo/10)), (0,127,255), infothickness*2, cv2.LINE_AA)
        cv2.circle(frame, (xofinfo,round(yofinfo-sizeofinfo/2)), round(infothickness*1.3), (0,127,255), -1, cv2.LINE_AA)

        sizeoftext = round(height/200)
        textthickness = round(height/100)
        text_size, _ = cv2.getTextSize("Do the", cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, textthickness)
        text_width, text_height = text_size
        cv2.putText(frame, "Do the", (round(width/2-text_width/2), round(yofinfo+sizeofinfo*1.3+text_height)), cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, (0,127,255), textthickness, cv2.LINE_AA)
        text_size, _ = cv2.getTextSize("Setup", cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, textthickness)
        text_width, text_height = text_size
        cv2.putText(frame, "Setup", (round(width/2-text_width/2), round(yofinfo+sizeofinfo*1.3+text_height*2.4)), cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, (0,127,255), textthickness, cv2.LINE_AA)

        correction = 0
        map_detected = False
        allow_trafficlight_symbol = False
        allow_no_lane_detected = False
        allow_do_blocked = False
        allow_do_zoom = False
        show_turn_line = False

    if do_blocked == True and allow_do_blocked == True:
        if allow_playsound == True:
            sounds.PlaysoundFromLocalPath("assets/sounds/info.mp3")
            allow_playsound = False
            allow_playsound_timer = current_time
        frame = cv2.GaussianBlur(frame, (9, 9), 0)
        frame = cv2.addWeighted(frame, 0.5, frame, 0, 0)

        xofinfo = round(width/2)
        yofinfo = round(height/3.5)
        sizeofinfo = round(height/5)
        infothickness = round(height/50)
        if infothickness < 1:
            infothickness = 1
        cv2.circle(frame, (xofinfo,yofinfo), sizeofinfo, (0,127,255), infothickness, cv2.LINE_AA)
        cv2.line(frame, (xofinfo,round(yofinfo+sizeofinfo/2)), (xofinfo,round(yofinfo-sizeofinfo/10)), (0,127,255), infothickness*2, cv2.LINE_AA)
        cv2.circle(frame, (xofinfo,round(yofinfo-sizeofinfo/2)), round(infothickness*1.3), (0,127,255), -1, cv2.LINE_AA)

        sizeoftext = round(height/200)
        textthickness = round(height/100)
        text_size, _ = cv2.getTextSize("Minimap vision", cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, textthickness)
        text_width, text_height = text_size
        cv2.putText(frame, "Minimap vision", (round(width/2-text_width/2), round(yofinfo+sizeofinfo*1.3+text_height)), cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, (0,127,255), textthickness, cv2.LINE_AA)
        text_size, _ = cv2.getTextSize("blocked", cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, textthickness)
        text_width, text_height = text_size
        cv2.putText(frame, "blocked", (round(width/2-text_width/2), round(yofinfo+sizeofinfo*1.3+text_height*2.4)), cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, (0,127,255), textthickness, cv2.LINE_AA)

        correction = 0
        map_detected = False
        allow_trafficlight_symbol = False
        allow_no_lane_detected = False
        allow_do_blocked = False
        allow_do_zoom = False
        show_turn_line = False

    elif do_zoom == True and allow_do_zoom == True:
        if allow_playsound == True:
            sounds.PlaysoundFromLocalPath("assets/sounds/info.mp3")
            allow_playsound = False
            allow_playsound_timer = current_time
        frame = cv2.GaussianBlur(frame, (9, 9), 0)
        frame = cv2.addWeighted(frame, 0.5, frame, 0, 0)

        xofinfo = round(width/2)
        yofinfo = round(height/3.5)
        sizeofinfo = round(height/5)
        infothickness = round(height/50)
        if infothickness < 1:
            infothickness = 1
        cv2.circle(frame, (xofinfo,yofinfo), sizeofinfo, (0,127,255), infothickness, cv2.LINE_AA)
        cv2.line(frame, (xofinfo,round(yofinfo+sizeofinfo/2)), (xofinfo,round(yofinfo-sizeofinfo/10)), (0,127,255), infothickness*2, cv2.LINE_AA)
        cv2.circle(frame, (xofinfo,round(yofinfo-sizeofinfo/2)), round(infothickness*1.3), (0,127,255), -1, cv2.LINE_AA)

        sizeoftext = round(height/200)
        textthickness = round(height/100)
        text_size, _ = cv2.getTextSize("Zoom Minimap in", cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, textthickness)
        text_width, text_height = text_size
        cv2.putText(frame, "Zoom Minimap in", (round(width/2-text_width/2), round(yofinfo+sizeofinfo*1.3+text_height*1.7)), cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, (0,127,255), textthickness, cv2.LINE_AA)
        
        correction = 0
        map_detected = False
        allow_trafficlight_symbol = False
        allow_no_lane_detected = False
        allow_do_blocked = False
        allow_do_zoom = False
        show_turn_line = False

    if width_lane == 0 and allow_no_lane_detected == True:
        if allow_playsound == True:
            sounds.PlaysoundFromLocalPath("assets/sounds/info.mp3")
            allow_playsound = False
            allow_playsound_timer = current_time
        frame = cv2.GaussianBlur(frame, (9, 9), 0)
        frame = cv2.addWeighted(frame, 0.5, frame, 0, 0)

        xofinfo = round(width/2)
        yofinfo = round(height/3.5)
        sizeofinfo = round(height/5)
        infothickness = round(height/50)
        if infothickness < 1:
            infothickness = 1
        cv2.circle(frame, (xofinfo,yofinfo), sizeofinfo, (0,127,255), infothickness, cv2.LINE_AA)
        cv2.line(frame, (xofinfo,round(yofinfo+sizeofinfo/2)), (xofinfo,round(yofinfo-sizeofinfo/10)), (0,127,255), infothickness*2, cv2.LINE_AA)
        cv2.circle(frame, (xofinfo,round(yofinfo-sizeofinfo/2)), round(infothickness*1.3), (0,127,255), -1, cv2.LINE_AA)

        sizeoftext = round(height/200)
        textthickness = round(height/100)
        text_size, _ = cv2.getTextSize("No Lane", cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, textthickness)
        text_width, text_height = text_size
        cv2.putText(frame, "No Lane", (round(width/2-text_width/2), round(yofinfo+sizeofinfo*1.3+text_height)), cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, (0,127,255), textthickness, cv2.LINE_AA)
        text_size, _ = cv2.getTextSize("Detected", cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, textthickness)
        text_width, text_height = text_size
        cv2.putText(frame, "Detected", (round(width/2-text_width/2), round(yofinfo+sizeofinfo*1.3+text_height*2.4)), cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, (0,127,255), textthickness, cv2.LINE_AA)

        correction = 0
        map_detected = False
        allow_trafficlight_symbol = False
        allow_no_lane_detected = False
        allow_do_blocked = False
        allow_do_zoom = False
        show_turn_line = False

    showing_traffic_light_symbol = False
    if trafficlightdetection_is_enabled == True and allow_trafficlight_symbol == True:
        if trafficlight == "Red":
            traffic_light_symbol = round(width/2), round(height/5), round(width/75)
            cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 0, 0), -1)
            cv2.circle(frame, (traffic_light_symbol[0], traffic_light_symbol[1] - traffic_light_symbol[2] * 2), traffic_light_symbol[2], (0, 0, 255), -1, cv2.LINE_AA)
            cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2]), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2]), (150, 150, 150), round(traffic_light_symbol[2]/10))
            cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2] * 3), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2] * 3), (150, 150, 150), round(traffic_light_symbol[2]/10))
            cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 0, 255), traffic_light_symbol[2])
            showing_traffic_light_symbol = True
        if trafficlight == "Yellow":
            traffic_light_symbol = round(width/2), round(height/5), round(width/75)
            cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 0, 0), -1)
            cv2.circle(frame, (traffic_light_symbol[0], traffic_light_symbol[1]), traffic_light_symbol[2], (0, 255, 255), -1, cv2.LINE_AA)
            cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2]), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2]), (150, 150, 150), round(traffic_light_symbol[2]/10))
            cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2] * 3), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2] * 3), (150, 150, 150), round(traffic_light_symbol[2]/10))
            cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 255, 255), traffic_light_symbol[2])
            showing_traffic_light_symbol = True
        if trafficlight == "Green":
            traffic_light_symbol = round(width/2), round(height/5), round(width/75)
            cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 0, 0), -1)
            cv2.circle(frame, (traffic_light_symbol[0], traffic_light_symbol[1] + traffic_light_symbol[2] * 2), traffic_light_symbol[2], (0, 255, 0), -1, cv2.LINE_AA)
            cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2]), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2]), (150, 150, 150), round(traffic_light_symbol[2]/10))
            cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2] * 3), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2] * 3), (150, 150, 150), round(traffic_light_symbol[2]/10))
            cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 255, 0), traffic_light_symbol[2])
            showing_traffic_light_symbol = True
    
    if allow_trafficlight_symbol == True:
        if width_lane != 0:
            cv2.line(frame, (round(left_x_lane + lanechanging_final_offset - offset), left_y_lane), (round(right_x_lane + lanechanging_final_offset - offset), right_y_lane),  (255, 255, 255), 2)
        if width_turn != 0 and showing_traffic_light_symbol == False and show_turn_line == True:
            cv2.line(frame, (round(left_x_turn + lanechanging_final_offset - offset), y_coordinate_of_turn), (round(right_x_turn + lanechanging_final_offset - offset), y_coordinate_of_turn), (255, 255, 255), 2)
    
    if lanechanging_do_lane_changing == True or fuel_percentage < 15:
        current_text = "Enabled"
        width_target_current_text = width/4
        fontscale_current_text = 1
        textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
        width_current_text, height_current_text = textsize_current_text
        max_count_current_text = 3
        while width_current_text != width_target_current_text:
            fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
            textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
            width_current_text, height_current_text = textsize_current_text
            max_count_current_text -= 1
            if max_count_current_text <= 0:
                break
        width_enabled_text, height_enabled_text = width_current_text, height_current_text

    if lanechanging_do_lane_changing == True:
        current_text = f"Lane: {lanechanging_current_lane}"
        width_target_current_text = width/4
        fontscale_current_text = 1
        textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
        width_current_text, height_current_text = textsize_current_text
        max_count_current_text = 3
        while width_current_text != width_target_current_text:
            fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
            textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
            width_current_text, height_current_text = textsize_current_text
            max_count_current_text -= 1
            if max_count_current_text <= 0:
                break
        width_lane_text, height_lane_text = width_current_text, height_current_text
        thickness_current_text = round(fontscale_current_text*2)
        if thickness_current_text <= 0:
            thickness_current_text = 1
        if turnincoming_detected == True:
            current_color = (150, 150, 150)
        else:
            current_color = (200, 200, 200)
        cv2.putText(frame, f"Lane: {lanechanging_current_lane}", (round(0.01*width), round(0.07*height+height_current_text+height_enabled_text)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, current_color, thickness_current_text)
    
    if fuel_percentage < 15:
        current_text = "Refuel!"
        width_target_current_text = width/4
        fontscale_current_text = 1
        textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
        width_current_text, height_current_text = textsize_current_text
        max_count_current_text = 3
        while width_current_text != width_target_current_text:
            fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
            textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
            width_current_text, height_current_text = textsize_current_text
            max_count_current_text -= 1
            if max_count_current_text <= 0:
                break
        thickness_current_text = round(fontscale_current_text*2)
        if thickness_current_text <= 0:
            thickness_current_text = 1
        if lanechanging_do_lane_changing == True:
            cv2.putText(frame, current_text, (round(0.01*width), round(0.10*height+height_current_text+height_enabled_text+height_lane_text)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 0, 255), thickness_current_text)
        else:
            cv2.putText(frame, current_text, (round(0.01*width), round(0.07*height+height_current_text+height_enabled_text)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 0, 255), thickness_current_text)
        
    if current_time - 1 > allow_playsound_timer and allow_trafficlight_symbol == True and allow_no_lane_detected == True and allow_do_zoom == True and show_turn_line == True:
        allow_playsound = True

    indicator_last_left = indicator_left
    indicator_last_right = indicator_right
    controls_last_left = controls_left
    controls_last_right = controls_right

    if speed > 63:
        correction *= 63/speed

    if turnincoming_detected == False and width_turn != 0 and width_turn < width_lane:
        curve = (center_x_lane - center_x_turn)/30
    else:
        curve = correction/10
    if gamepaused == True:
        curve = 0

    if width_lane == 0:
        lane_detected = False
        check_map_timer = current_time
    else:
        lane_detected = True

    if speed > -0.5:
        data["LaneDetection"] = {}
        data["LaneDetection"]["difference"] = -correction/30
    else:
        data["LaneDetection"] = {}
        data["LaneDetection"]["difference"] = correction/30
    data["NavigationDetection"] = {}
    data["NavigationDetection"]["lanedetected"] = lane_detected
    data["NavigationDetection"]["mapdetected"] = map_detected
    data["NavigationDetection"]["turnincoming"] = turnincoming_detected
    data["NavigationDetection"]["curve"] = curve
    data["NavigationDetection"]["lane"] = lanechanging_current_lane
    data["NavigationDetection"]["laneoffsetpercent"] = lanechanging_progress
    
    data["frame"] = frame

    return data
        

# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    pass

def onDisable():
    pass

# Plugins can also have UIs, this works the same as the panel example
class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
            resizeWindow(950,600)        
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self
        
        def tabFocused(self): # Called when the tab is focused
            resizeWindow(950,600)

        def UpdateSettings(self):

            self.UI_offset.set(self.UI_offsetSlider.get())
            self.UI_lanechanging_speed.set(self.UI_lanechanging_speedSlider.get())
            self.UI_lanechanging_width.set(self.UI_lanechanging_widthSlider.get())

            settings.CreateSettings("NavigationDetection", "offset", self.UI_offsetSlider.get())
            settings.CreateSettings("NavigationDetection", "lanechanging_speed", self.UI_lanechanging_speedSlider.get())
            settings.CreateSettings("NavigationDetection", "lanechanging_width", self.UI_lanechanging_widthSlider.get())
            
            LoadSettings()
        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=950, height=600, border=0, highlightthickness=0)
            self.root.grid_propagate(1) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            notebook = ttk.Notebook(self.root)
            notebook.pack(anchor="center", fill="both", expand=True)
            
            generalFrame = ttk.Frame(notebook)
            generalFrame.pack()
            setupFrame = ttk.Frame(notebook)
            setupFrame.pack()
            advancedFrame = ttk.Frame(notebook)
            advancedFrame.pack()

            notebook.add(generalFrame, text=Translate("General"))
            notebook.add(setupFrame, text=Translate("Setup"))
            notebook.add(advancedFrame, text=Translate("Advanced"))
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
            
            ############################################################################################################################
            # UI
            ############################################################################################################################

            self.UI_offsetSlider = tk.Scale(generalFrame, from_=-20, to=20, resolution=0.1, orient=tk.HORIZONTAL, length=500, command=lambda x: self.UpdateSettings())
            self.UI_offsetSlider.set(settings.GetSettings("NavigationDetection", "offset"))
            self.UI_offsetSlider.grid(row=2, column=0, padx=10, pady=0, columnspan=2)
            self.UI_offset = helpers.MakeComboEntry(generalFrame, "Lane Offset", "NavigationDetection", "offset", 2, 0, labelwidth=10, width=8, isFloat=True, sticky="ne")

            helpers.MakeEmptyLine(generalFrame, 3, 0)

            helpers.MakeCheckButton(generalFrame, "Left-hand traffic\n----------------------\nEnable this if you are driving in a country with left-hand traffic.", "NavigationDetection", "lefthand_traffic", 4, 0, width=80, callback=lambda: LoadSettings())
            
            helpers.MakeEmptyLine(generalFrame, 5, 0)
            
            helpers.MakeCheckButton(generalFrame, "Lane Changing\n---------------------\nIf enabled, you can change the lane you are driving on using the games indicators\nor the buttons you set in the Controls menu.", "NavigationDetection", "lanechanging_do_lane_changing", 6, 0, width=80, callback=lambda: LoadSettings())
            
            self.UI_lanechanging_speedSlider = tk.Scale(generalFrame, from_=0.1, to=3, resolution=0.1, orient=tk.HORIZONTAL, length=500, command=lambda x: self.UpdateSettings())
            self.UI_lanechanging_speedSlider.set(settings.GetSettings("NavigationDetection", "lanechanging_speed"))
            self.UI_lanechanging_speedSlider.grid(row=7, column=0, padx=10, pady=0, columnspan=2)
            self.UI_lanechanging_speed = helpers.MakeComboEntry(generalFrame, "Lane Changing Speed", "NavigationDetection", "lanechanging_speed", 7, 0, labelwidth=18, width=8, isFloat=True, sticky="ne")

            helpers.MakeLabel(generalFrame, "╚> This slider sets the speed of the lane changing.", 8, 0, sticky="nw")
            
            self.UI_lanechanging_widthSlider = tk.Scale(generalFrame, from_=1, to=30, resolution=0.1, orient=tk.HORIZONTAL, length=500, command=lambda x: self.UpdateSettings())
            self.UI_lanechanging_widthSlider.set(settings.GetSettings("NavigationDetection", "lanechanging_width"))
            self.UI_lanechanging_widthSlider.grid(row=9, column=0, padx=10, pady=0, columnspan=2)
            self.UI_lanechanging_width = helpers.MakeComboEntry(generalFrame, "Lane Width", "NavigationDetection", "lanechanging_width", 9, 0, labelwidth=18, width=8, isFloat=True, sticky="ne")
            
            helpers.MakeLabel(generalFrame, "╚> This slider sets how much the truck needs to go left or right to change the lane.", 10, 0, sticky="nw")

            helpers.MakeEmptyLine(generalFrame, 11, 0)

            helpers.MakeButton(generalFrame, "Give feedback, report a bug or suggest a new feature", lambda: switchSelectedPlugin("plugins.Feedback.main"), 12, 0, width=80, sticky="nw")

            helpers.MakeButton(generalFrame, "Open Wiki", lambda: helpers.OpenInBrowser("https://wiki.tumppi066.fi/plugins/navigationdetection"), 12, 1, width=23, sticky="nw")

            
            helpers.MakeLabel(setupFrame, "Choose a setup method:", 1, 0, font=("Robot", 12, "bold"), sticky="nw")
            
            helpers.MakeButton(setupFrame, "Automatic Setup", self.automatic_setup, 2, 0, sticky="nw")

            helpers.MakeLabel(setupFrame, "The automatic setup will search for the minimap on your screen using AI (YOLOv5), it needs to download some\nfiles the first time you run it. Make sure that the minimap is always visible and not blocked by other applications.", 3, 0, sticky="nw")

            helpers.MakeEmptyLine(setupFrame, 4, 0)

            helpers.MakeButton(setupFrame, "Manual Setup", self.manual_setup, 5, 0, sticky="nw")

            helpers.MakeLabel(setupFrame, "The manual setup will take a screenshot of your screen and then ask you to select the minimap and arrow positions.\nYou can take a look at the example image when you don't know what to do. The example image will open in another window.", 6, 0, sticky="nw")


            helpers.MakeCheckButton(advancedFrame, "Automatically change to lane 0 if a turn got detected and lane changing is enabled.\nNote: If disabled, you will be unable to change lanes when detecting a turn.", "NavigationDetection", "lanechanging_autolanezero", 2, 0, width=97, callback=lambda: LoadSettings())
            
        def save(self):
            LoadSettings()
        
        def manual_setup(self):
            subprocess.Popen([f"{os.path.dirname(os.path.dirname(variables.PATH))}/venv/Scripts/python.exe", os.path.join(variables.PATH, "plugins/NavigationDetection", "manual_setup.py")], shell=True)

        def automatic_setup(self):
            subprocess.Popen([f"{os.path.dirname(os.path.dirname(variables.PATH))}/venv/Scripts/python.exe", os.path.join(variables.PATH, "plugins/NavigationDetection", "automatic_setup.py")], shell=True)

        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    except Exception as ex:
        print(ex.args)

# this comment is used to reload the app after finishing the setup - 0