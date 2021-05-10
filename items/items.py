import sys
sys.path.append("D:\Desktop\TIPE\KRO")

##############################: IMPORTS :############################
import math as m
import threading
import time
import database
from pathfinding import m_star

##############################: GLOBAL VARIABLES :###################


#############################: CLASS :###############################

class robot(threading.Thread) :

    def __init__(self,ids,coord,angle=0) :
        self.id = ids
        self.coord = coord
        self.angle = angle
        
        #Thread variables
        self.is_active = True
        self.request_follow_path = []
        self.request_ping = False

        #Init thread
        self.activate()
    #Path---------------------------------
    def send_path(self,chemin):
        self.request_follow_path = chemin

    def follow_path(self,chemin): #TODO Follow_path func
        n = len(chemin)
        for i in range(n):
            task = chemin[i]

            #Attente :
            time.sleep(task[0])
    #Ping---------------------------------
    def send_ping(self):
        self.request_ping = True
    
    def ping(self):
        print("ping received, printing pong in 2 sec")
        time.sleep(2)
        self.request_ping = False
        print("Pong !")
    #State-switch-------------------------
    def desactivate(self):
        """Desactivate the robot"""
        self.is_active = False
    
    def activate(self):
        """Activate the robot, or reset it, will need .start() to be activate"""
        if self.is_active :
            self.desactivate()

        threading.Thread.__init__(self)
        self.is_active = True
        self.start()
    #-------------------------------------
    def run(self) :

        while self.is_active :

            #Check event follow path
            if self.request_follow_path != [] :
                self.follow_path(self.request_follow_path)

            #Check event ping
            if self.request_ping :
                self.ping()
            
            #Sleep to loop
            time.sleep(0.5)
            


if __name__ == "__main__" :
    my_robot = robot(1,(0,0))