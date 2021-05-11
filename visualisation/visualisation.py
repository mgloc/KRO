import sys
from typing import Text
sys.path.append("D:\Desktop\TIPE\KRO")

##############################: IMPORTS :############################
import math as m
import threading
import time
import database
from tkinter import StringVar, Tk,Canvas,Label
from pathfinding import m_star
from items import items
import random
from decorators_test import *

##############################: GLOBAL VARIABLES :###################
cos ={0:1,90:0,180:-1,270:0,360:1}
sin ={0:0,90:1,180:0,270:-1,360:0}

robot_list = []
shelf_list = []

clock = 0

#############################: WINDOW :###############################

class windows :
    "Interface de visualisation matriciel"
    def __init__(self,dimensions:tuple=database.size,name:str="Fenêtre"):
        self.root = Tk()
        self.root['bg']="lavender"
        self.root.resizable(width=False, height=False)
    
        #Affectations
        self.root.title(name)
        self.dimensions = dimensions

        #Widgets
        self.createWidgets()

    def createWidgets(self):
        #Dimensions du canevas
        self.can_width   = 1280
        self.can_height  = 800
        self.taille_case = min(self.can_width,self.can_height)/max(self.dimensions[0],self.dimensions[1])
        #Canevas
        self.can = Canvas(self.root, width=self.can_width, height=self.can_height)
        self.can.pack()
        #Label compteur
        self.clock = StringVar(value=0)
        self.lbl_compteur = Label(self.root,textvariable=self.clock)
        self.lbl_compteur.pack()
    
    def convert_coord_to_pixels(self,coord):
        return (coord[1]*self.taille_case,coord[0]*self.taille_case)

    #Robots----------------------------------------------------------------
    def place_robot(self,coord:tuple=(0,0),angle=0,is_carrying=False)->None:
        corner_tl_coord = self.convert_coord_to_pixels(coord)                   #tl = top left
        corner_br_coord = self.convert_coord_to_pixels((coord[0]+1,coord[1]+1)) #br = bottom right
        middle          = ((corner_tl_coord[0]+corner_br_coord[0])/2,(corner_tl_coord[1]+corner_br_coord[1])/2)
        middle_plus_angle= self.convert_coord_to_pixels((-sin[angle],cos[angle]))
        middle_top      = (middle[0]+0.5*middle_plus_angle[0],middle[1]+0.5*middle_plus_angle[1])

        #Body
        if is_carrying :
            self.can.create_rectangle(corner_tl_coord, corner_br_coord,fill="green")
        else :
            self.can.create_rectangle(corner_tl_coord, corner_br_coord,fill="orange")

        #Angle
        self.can.create_line(middle,middle_top,fill="red")
    
    def place_all_robot(self,robot_list:list[items.robot])->None:
        for robot in robot_list :
            is_carrying = (robot.carried_shelf != None)
            self.place_robot(robot.coord,robot.angle,is_carrying)
    
    #Shelf-----------------------------------------------------------------
    def place_shelf(self,coord:tuple=(0,0),is_carried=False)->None:
        if is_carried :
            return None
        corner_tl_coord = self.convert_coord_to_pixels(coord)                   #tl = top left
        corner_br_coord = self.convert_coord_to_pixels((coord[0]+1,coord[1]+1)) #br = bottom right
        
        #Body
        self.can.create_rectangle(corner_tl_coord, corner_br_coord,fill="blue")

    def place_all_shelf(self,shelf_list:list[items.shelf])->None:
        for shelf in shelf_list :
            is_carried = shelf.is_picked_up
            self.place_shelf(shelf.coord,is_carried)

    #Actualisations--------------------------------------------------
    def actualise_canvas(self):
        self.can.delete("all")
        self.place_all_robot(robot_list)
        self.place_all_shelf(shelf_list)
        self.root.after(database.period_10_fps,self.actualise_canvas)
    
    def actualise_clock(self) :
        global clock
        clock += database.period_10_fps
        self.clock.set(clock)
        self.root.after(database.period_10_fps,self.actualise_clock)

#Thread tk----------------------------
def runtk():
    my_w = windows()
    my_w.root.after(100,my_w.actualise_canvas)
    my_w.root.after(100,my_w.actualise_clock)
    my_w.root.mainloop()

#############################: CONTROLLER :###############################

class controller :

    def __init__(self):
        #Initialisation :
        self.graph = m_star.Graph(database.size)

        #Canvas initialisation :
        self.visualisation_thread = threading.Thread(target=runtk)
        self.visualisation_thread.start()

    #Sendpath---------------------------------------------
    def send_robot_to_coord(self,robot,coord) :
        assert robot in robot_list
        if robot.is_available_path() :
            chemin = m_star.pathfinder(robot.coord,coord,self.graph,clock)
            robot.send_path(chemin)
    
    def send_robot_three_points(self,robot,coord1,coord2):
        assert robot in robot_list
        if robot.is_available_path() :
            chemin1,end_clock = m_star.pathfinder(robot.coord,coord1,self.graph,clock,return_end_clock=True)
            chemin2 = m_star.pathfinder(coord1,coord2,self.graph,end_clock,custom_clock=True)
            robot.send_path(chemin1 + chemin2)
    

    def send_robot_pick_up(self,robot,shelf,coord):
        assert robot in robot_list
        assert shelf in shelf_list
        print(f"launched at {clock}")
        if robot.is_available_path() and robot.is_available_pick_up() :
            chemin_armoire,end_clock = m_star.pathfinder(robot.coord,shelf.coord,self.graph,clock+100,return_end_clock=True,robot_coord_list=[r.coord for r in robot_list if r.is_available_path(log_error=False)])
            end_clock += database.pick_move_time
            chemin_coord = m_star.pathfinder(shelf.coord,coord,self.graph,end_clock,custom_clock=True,shelf=True,shelf_coord_list=[s.coord for s in shelf_list],robot_coord_list=[r.coord for r in robot_list if r.is_available_path(log_error=False)]) 
            robot.send_path(chemin_armoire + [shelf] + chemin_coord)

    #Creation---------------------------------------------
    def new_robot(self,coord=(0,0),angle=0):
        robot_list.append(items.robot(len(robot_list),coord,angle))

    def new_shelf(self,coord=(0,0),capacity=5):
        shelf_list.append(items.shelf(len(robot_list),coord,capacity))

###########################: TEST FUNCTIONS :#######################################

def spawn_10():
    global robot_list
    global shelf_list
    my_ctrl = controller()
    for i in range(20):
        my_ctrl.new_robot((i,0))
        my_ctrl.new_shelf((i,10))
    
    pod_list = [(i,19) for i in range(20)]
    pod_list[18],pod_list[19]=pod_list[19],pod_list[18]

    for i in range(20):
        time.sleep(0.1)
        my_ctrl.send_robot_pick_up(robot_list[i],shelf_list[i],pod_list[i])

####################################################################################
if __name__ == "__main__" :

    # my_ctrl = controller()
    # my_ctrl.new_robot()
    # my_ctrl.new_shelf(coord=(5,5))
    # time.sleep(1)
    # my_ctrl.send_robot_pick_up(robot_list[0],shelf_list[0],(10,10))
    #TODO Idée pour vérifier la source d'erreur avec progression linéaire sur le décalage du segment en fonction du nombre de path lancées

    spawn_10()


