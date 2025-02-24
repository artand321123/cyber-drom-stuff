from pion.pion import Pion as P
from drone_cv import *
import time
from threading import Thread
import cv2
import cv2.aruco as aruco

# НАСТРОЙКИ
IP = "127.0.0.1"

DRONE1_PORT = 8000
DRONE1_VIDEO_PORT = 18000
DRONE1_HEIGHT = 2.5

DRONE2_PORT = 8001
DRONE2_VIDEO_PORT = 18001
DRONE2_HEIGHT = 1.5

BOT1_PORT = 8002
BOT2_PORT = 8003

DRONE_STEP = 1


class Car(P):
    """
    Класс машины
    """
    def __init__(self, ip: str, port: int):
        super().__init__(ip, port)
        self.ip = ip
        self.port = port
        self.targets = []
        self.base = (self.position[0], self.position[1], 0, 0)

        controller_thread = Thread(target=self.car_controller_thread)
        controller_thread.start()
    
    def car_controller_thread(self):
        """
        Собирать добавленные в список грузы и доставлять их на базу
        """
        while True:
            if len(self.targets) > 0:
                self.goto(*self.targets[0])
                time.sleep(10)
                self.goto(*self.base)
                time.sleep(5)
                self.targets.pop(0)

class FlyerDrone(P):
    """
    Класс дрона-разведчика
    """
    def __init__(
            self, ip: str,
            port: int,
            camera_port: int,
            height: float,
            car: Car,
            side: bool,
            base: tuple
        ):
        """
        Конструктор

        ip: IP-адрес

        port: Порт дрона

        camera_port: Порт камеры

        height: Высота полёта

        car: Машина, которой отправлять координаты грузов

        side: Сторона поля, на которой летит дрон
        """
        super().__init__(ip, port)
        self.camera_port = camera_port
        self.height = height
        self.car = car
        self.side = side
        self.base = base
        print(self.base)
        self.aruco_detector_thread = Thread(target=self.aruco_detector)
        self.aruco_detector_thread.start()

    def takeoff(self):
        """
        Запуск двигателей и взлёт
        """
        print("TAKING OFF")
        self.arm()
        time.sleep(3)
        super().takeoff()
        time.sleep(3)
        print("TAKEN OFF")
    
    def return_to_base(self):
        """
        Возврат на базу и посадка
        """
        print("RETURNING TO BASE")
        self.goto(*self.base, self.height, 0)
        time.sleep(10)
        self.land()
        time.sleep(3)
        self.disarm()
        print("LANDED")

    def search_targets(self, targets: list[tuple]):
        """
        Поиск грузов
        """
        print("SEARCHING FOR TARGETS")
        for target in targets:
            print(f"TARGET {targets.index(target)}/{len(targets)}:", target)
            self.goto(*target, self.height, 0)
            time.sleep(10)
        print("TARGETS SEARCHED")

    def aruco_detector(self):
        """
        Обнаружение маркеров ArUco с камеры
        и добавление их координат в список грузов для машины
        """
        camera = SocketCamera(self.ip, self.camera_port)
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
        detected_ids = []
        print("ARUCO DETECTOR STARTED")

        while True:
            frame = camera.get_cv_frame()
            if frame is not None:
                corners, ids, _ = detector.detectMarkers(frame)
                if ids is not None and ids[0][0] not in detected_ids:
                    frame = aruco.drawDetectedMarkers(frame, corners, ids)
                    detected_ids.append(ids[0][0])
                    print('CODE SPOTTED:', corners, '-', ids[0][0])
                    cv2.imshow(f'CODE SPOTTED: {ids[0][0]}', frame)
                else:
                    cv2.imshow('aruco detector', frame)
            if cv2.waitKey(1) == 27:
                break
        cv2.destroyAllWindows()

if __name__ == "__main__":
    drone = FlyerDrone(IP, DRONE1_PORT, DRONE1_VIDEO_PORT, DRONE1_HEIGHT, Car(IP, 8001), True, (-3.92, -2.14))
    drone.takeoff()
    time.sleep(5)
    drone.search_targets([
        (-4, 4),
        (4, 3),
        (-4, 2),
        (4, 1),
        (-4, 0),
        (4, -1),
        (-4, -2),
        (4, -3),
        (-4, -4)
    ])
    drone.return_to_base()