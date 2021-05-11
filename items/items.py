import sys
sys.path.append("D:\Desktop\TIPE\KRO")

##############################: IMPORTS :############################
import math as m
import threading
import time
import database
##############################: GLOBAL VARIABLES :###################


#############################: CLASS :###############################
     
class shelf :

    def __init__(self,ids:int,coord:tuple,capacity:int=5):
        self.id = ids
        self.coord = coord
        #Soulevage
        self.is_picked_up = False
        #Contenu
        self.capacity = capacity
        self.contenu = [[] for _ in range(self.capacity)]

    def __repr__(self) -> str:
        return f"shelf id:{self.id},coord:{self.coord}"
    
    #Pick-up Pick-down-------------------------------------------------
    def pick_up(self):
        self.is_picked_up = True
    
    def put_down(self,coord):
        self.is_picked_up = False
        self.coord = coord

    #Items-------------------------------------------------------------
    def item_add(self,item,slot):
        assert 1<=slot<=self.capacity
        self.contenu[slot].append(item)
        
    def item_remove(self,item):
        for i in range(self.capacity) :
            if item in self.contenu[i] :
                self.contenu[i].remove(item)
                return None
        print(f"No such item {item} was found in shelf {self.id}")
        return None

class robot(threading.Thread) :

    def __init__(self,ids,coord,angle=0) :
        self.id = ids
        self.coord = coord
        self.angle = angle

        #Shelf relationship
        self.carried_shelf = None

        #Thread variables
        self.is_active = True
        #-Path
        self.request_follow_path = []
        #-Ping
        self.request_ping = False

        #Init thread
        self.activate()
    
    def __repr__(self) -> str:
        return f"robot id:{self.id},coord:{self.coord},active:{self.is_active}"
    
    #Turn--------------------------------
    #Utilisation du sens trigonométrique et de 0° pour l'est
    def turn_left(self) :
        time.sleep((database.rotation_move_half_time)*1e-3)
        self.angle += 90
        self.angle = self.angle % 360
        time.sleep((database.rotation_move_half_time)*1e-3)
    
    def turn_right(self) :
        time.sleep((database.rotation_move_half_time)*1e-3)
        self.angle += -90
        self.angle = self.angle % 360
        time.sleep((database.rotation_move_half_time)*1e-3)
    
    def turn_over(self) :
        self.turn_left()
        self.turn_left()

    def turn(self,choosen_angle) :
        if self.angle == choosen_angle :
            pass
        elif (self.angle-180)%360 == choosen_angle :
            self.turn_over()
        elif (self.angle-90)%360 == choosen_angle :
            self.turn_right()
        else :
            self.turn_left()
    
    def turn_toward_coord(self,coord):
        if self.coord == coord :
            return None

        x,y = self.coord
        x1,y1 = coord
        if x1 == x-1 :
            self.turn(90) #90° = North
        elif x1 == x+1 :
            self.turn(270) #-90° = South
        elif y1 == y-1 :
            self.turn(180) #180° = West
        elif y1 == y+1 :
            self.turn(0) #0° = East
        else :
            raise NameError(f"Invalid turn given : {self.coord},{coord}")
    
    #Move---------------------------------
    def move_toward_coord(self,coord):
        if self.coord == coord :
            return None
        
        x,y   = self.coord
        x1,y1 = coord

        pas = 1/database.movement_step
        for i in range(1,int(database.movement_step)) : #Méthode du barycentre pour effectuer une transition de 15 pas
            lmb = i*pas
            self.coord = ((1-lmb)*x + lmb*x1,(1-lmb)*y + lmb*y1)
            time.sleep(database.period_10_fps*1e-3)
        
        self.coord = coord

    #Pick-up Pick-down a shelf-----------
    def pick_up(self,choosen_shelf:shelf):
        #Cas impossibles
        if self.coord != choosen_shelf.coord :
            print(f"Impossible pick-up asked on coord:{self.coord},for {self} and {choosen_shelf} : Unmatched coords")
            return None
        if self.carried_shelf != None :
            print(f"Impossible pick-up asked on coord:{self.coord},for {self} and {choosen_shelf} : Robot already carrying {self.carried_shelf}")
            return None
        
        #Pick-up
        self.carried_shelf = choosen_shelf
        self.carried_shelf.pick_up()
    
    def put_down(self):
        #Cas impossibles
        if self.carried_shelf == None:
            print(f"Impossible put-down asked : {self} was carrying nothing")
            return None
        
        #Put-down
        self.carried_shelf.put_down(self.coord)
        self.carried_shelf = None

    def is_available_pick_up(self):
        if self.carried_shelf == None :
            return True
        else :
            print(f"Robot{self.id} is busy right now")
            return False

    #Path---------------------------------
    def send_path(self,chemin):
        self.request_follow_path = chemin

    def is_available_path(self):
        if self.request_follow_path == [] :
            return True
        else :
            print(f"Robot{self.id} is busy right now")
            return False

    def follow_path(self,chemin):
        n = len(chemin)
        for i in range(n):
            task = chemin[i]
            if type(task) == tuple :
                wait = task[1]
                coord = task[0]

                #Attente :
                time.sleep(wait*1e-3)

                #Rotation :
                self.turn_toward_coord(coord)

                #Avancement :
                self.move_toward_coord(coord)
            
            elif type(task) == shelf :
                self.pick_up(choosen_shelf=task)
        
        self.request_follow_path = []

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
 
class pod :
    
    def __init__(self,coord):

        self.coord = coord
        self.slots = []

if __name__ == "__main__" :
    my_robot = robot(1,(0,0))