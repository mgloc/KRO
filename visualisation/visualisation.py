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
chemin_test = [((1, 0), 0), ((0, 0), 10), ((0, 1), 0), ((0, 2), 0), ((0, 3), 0), ((0, 4), 0), ((0, 5), 0), ((0, 6), 0), ((0, 7), 0), ((0, 8), 0), ((0, 9), 0)]

global robot_list
robot_list = []

#############################: CLASS :###############################

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
        return (coord[0]*self.taille_case,coord[1]*self.taille_case)


    def place_robot(self,coord:tuple=(0,0))->None:
        coord = self.convert_coord_to_pixels(coord)
        self.can.create_rectangle(coord, (coord[0]+self.taille_case,coord[1]+self.taille_case),fill="orange")
    
    def place_all_robot(self,robot_list:list[items.robot])->None:
        for robot in robot_list :
            self.place_robot(robot.coord)
    
    def actualise_canvas(self):
        self.can.delete("all")
        self.place_all_robot(robot_list)
        self.root.after(database.period_10_fps,self.actualise_canvas)

def runtk():
    my_w = windows()
    my_w.root.after(100,my_w.actualise_canvas)
    my_w.root.mainloop()


if __name__ == "__main__" :
    thd = threading.Thread(target=runtk)
    thd.start()

    robot_list.append(items.robot(0,(0,0)))
    robot_list[0].send_path(chemin = chemin_test)

