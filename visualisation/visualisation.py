import sys
sys.path.append("D:\Desktop\TIPE\KRO")

##############################: IMPORTS :############################
import math as m
import threading
import time
import database
from tkinter import Tk,Canvas
from pathfinding import m_star
from items import items

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
    
    def convert_coord_to_pixels(self,coord):
        return (coord[1]*self.taille_case,coord[0]*self.taille_case)

    #Robots----------------------------------------------------------------
    def place_robot(self,coord:tuple=(0,0),angle=0)->None:
        corner_tl_coord = self.convert_coord_to_pixels(coord)                   #tl = top left
        corner_br_coord = self.convert_coord_to_pixels((coord[0]+1,coord[1]+1)) #br = bottom right
        middle          = ((corner_tl_coord[0]+corner_br_coord[0])/2,(corner_tl_coord[1]+corner_br_coord[1])/2)
        middle_plus_angle= self.convert_coord_to_pixels((-sin[angle],cos[angle]))
        middle_top      = (middle[0]+0.5*middle_plus_angle[0],middle[1]+0.5*middle_plus_angle[1])

        #Body
        self.can.create_rectangle(corner_tl_coord, corner_br_coord,fill="orange")

        #Angle
        self.can.create_line(middle,middle_top,fill="red")
    
    def place_all_robot(self,robot_list:list[items.robot])->None:
        for robot in robot_list :
            self.place_robot(robot.coord,robot.angle)

    #Actualisations--------------------------------------------------
    def actualise_canvas(self):
        self.can.delete("all")
        self.place_all_robot(robot_list)
        self.root.after(database.period_10_fps,self.actualise_canvas)
    
    def actualise_clock(self) :
        global clock
        clock += database.period_10_fps
        self.root.after(database.period_10_fps,self.actualise_clock)


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


    def send_robot_to_coord(self,robot,coord) :
        assert robot in robot_list
        if robot.is_available_path() :
            robot.send_path(chemin)
            chemin = m_star.pathfinder(robot.coord,coord,self.graph,clock)
    
    def new_robot(self,coord=(0,0),angle=0):
        robot_list.append(items.robot(len(robot_list),coord,angle))


####################################################################################

if __name__ == "__main__" :

    my_ctrl = controller()
    my_ctrl.new_robot()
    my_ctrl.send_robot_to_coord(robot_list[0],(2,9))
    time.sleep(2)
    my_ctrl.new_robot()
    my_ctrl.send_robot_to_coord(robot_list[0],(1,9))

