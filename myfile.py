from pion.pion import Pion as P
from rzd import *
import time
from threading import Thread
from random import randint
import cv2
import cv2.aruco as aruco


ip = "127.0.0.1"
port = 8000
port_video = 18000
port2 = 8001
port_video2 = 18001

bot_port = 8002
bot_port2 = 8004

STEP = 0.5
H1 = 2.5
H2 = 1


def d1():
    drone = P(ip, port)
    drone.arm()
    drone.takeoff()
    bot = P(ip, bot_port)
    bot.arm()
    time.sleep(3)
    fly(drone, H1, True, bot)
    
def d2():
    drone2 = P(ip, port2)
    drone2.arm()
    drone2.takeoff()
    bot2 = P(ip, bot_port2)
    bot2.arm()
    time.sleep(3)
    fly(drone2, H2, False, bot2)


def bot1(coord):
    bot = P(ip, bot_port)
    bot.arm()
    bot.goto(coord[0], coord[1], 0, 0)


def main():
    camera = SocketCamera(ip, port_video)

    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    while True:
        frame = camera.get_cv_frame()
        if frame is not None:
            corners, ids, _ = detector.detectMarkers(frame)
            frame = aruco.drawDetectedMarkers(frame, corners, ids)
            cv2.imshow('Detected ArUco', frame)
        if cv2.waitKey(1) == 27:
            break
    cv2.destroyAllWindows()

coords = []

def bot_go(bot:P,x,y):
    bot.goto(x,y,0,0)

# main()
def fly(drone:P, h, dimension, bot:P):
    global STEP
    global coords
    time.sleep(3)
    current_x = drone.position[0]
    current_y = drone.position[1]
    new_coords = [current_x, current_y]
    coords.append(new_coords)
    # bot.goto(new_coords[0], new_coords[1],0,0)
    drone.goto(-current_x,current_y,h,0)

    Thread(target = bot_go,args = [bot,new_coords[0], new_coords[1]]).start()
    while True:
        drone.print_information()
        if int(drone.position[0]) == int(-current_x):
            print('reached')
            drone.point_reached = True
            time.sleep(3)
            current_x = drone.position[0]
            current_y = drone.position[1]
            if dimension:
                drone.goto(current_x, current_y+STEP, h, 0)
            else:
                drone.goto(current_x, current_y-STEP, h, 0)
                
            time.sleep(3)
            fly(drone, h, dimension,bot)


Thread(target = d1).start()
Thread(target = d2).start()
Thread(target = main).start()