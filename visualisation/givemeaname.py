import sys
sys.path.append("D:\Desktop\TIPE\KRO")

##############################: IMPORTS :############################
import math as m
import threading
import time
import database
from tkinter import Tk,Grid,Canvas,Label,Button
from pathfinding import m_star

##############################: GLOBAL VARIABLES :###################


#############################: CLASS :###############################

class windows :
    "Interface de visualisation matriciel"
    def __init__(self,dimensions:tuple=(7,10),name:str="Fenêtre"):
        self.fenetre = Tk()
        self.fenetre['bg']="lavender"
        self.fenetre.resizable(width=False, height=False)
        self.fenetre.title(name)


        #Couleurs
        self.couleurs ={
          0: 'white'   #Vide (blanc)
        , 1: '#ff2f1d' #Robot (rouge)
        , 2: '#d06c10' #Armoire (orange)
        , 3: '#ffb380' #Robot qui porte une armoire (beige)
        }

        #Dimensions du canevas
        self.can_width  = 1280
        self.can_height = 800
        #Canevas
        self.can = Canvas(self.fenetre, width=self.can_width, height=self.can_height)
        self.can.pack()
    
    def place_robot(self,coord:tuple=(0,0)):
        self.can.create_rectangle((10, 20), (100, 200),fill="orange")
        self.fenetre.after(1000,self.place_robot)




if __name__ == "__main__" :
    pass