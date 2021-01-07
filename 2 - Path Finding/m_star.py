# pylint: disable=unused-variable

##############################: IMPORTS :#############################
import math as m
import threading
import time
import sys

##############################: GLOBAL VARIABLES :###################
caractères = [0, #Vide
              1, #Blocage
             "D",#Départ
             "A"]#Arrivée

matrice_test = [[0,0,0,0,0,0,0,0,0,0], 
                [0,0,0,0,0,1,0,"A",0,0],
                [0,0,0,0,0,1,0,0,0,0],
                [0,0,0,0,0,1,0,0,0,0],
                [0,0,0,0,0,1,0,0,0,0],
                [0,"D",0,0,1,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],]

#############################: CLASS :################################

class Horloge :

    def __init__(self) :
        self.set_time()
        print("Horloge initialisée à {}".format(self.time))

    def set_time(self) :
        self.time = time.time()
    
    def get_time(self,rounded=True) :
        """Récupère le temps écoulé depuis le dernier set_time"""
        if rounded :
            return round(time.time() - self.time, 3)
        else :
            return time.time() - self.time

class Matrice_temporelle(Horloge) :
    """Matrice contenant des couples de réels"""

    def __init__(self,taille=(0,0)):
        self.x,self.y = taille
        self.matrice = [[0.0]*self.x]*self.y
        self.set_time()
    
    def send_trajectory(self,liste):
        """Fonction qui reçoit une liste de couple (case,temps de mouvement estimé pour se déplacer à la case) et qui l'ajoute à la matrice"""
        temps = 0
        tmp_bool = True  ##Ici le booléen temporaire permet d'actualiser la matrice seulement une fois pour get_case()
        for (case,tm) in liste :
            i,j = case
            valcase = self.get_case(i,j,tmp_bool)
            self.set_case(i,j,valcase + temps + tm)
            temps += tm
            tmp_bool = False


    def actualiser(self):
        """Fonction qui retire le temps qui s'est écoulé à toute la matrice"""
        delta = self.get_time()
        for i in range(self.x) :
            for j in range(self.y) :
                case = self.matrice[i][j]
                self.set_case(i,j,round(case - delta,3))

    def get_case(self,a,b,boole=True) :
        if boole :
            self.actualiser()
        return self.matrice[a][b]

    def get_matrice(self) :
        self.actualiser()
        return self.matrice

    def set_case(self,a,b,x):
        #Pas besoin d'actualiser ici
        if x >= 0.0 :
            self.matrice[a][b] = x
        else :
            self.matrice[a][b] = 0.0 
        
class Noeud :

    def __init__(self,x: int,y: int):
        self.occupation = [] #liste temps
        self.voisins = []
        self.coord = (x,y)
        self.have_shelf = False

        #M-Star
        self.g = 0
        self.h = 0
        self.f = 0
        self.straight_parent = False

    def reset_node(self):
        self.g = self.h = self.f = 0
        self.parent = None
    
    def manhattan(self,other) :
        x1,y1 = self.coord
        x2,y2 = other.coord
        return(abs(x2-x1) + abs(y2-y1))

class M_Graph :

    def __init__(self,taille: tuple):
        self.n,self.m = taille

        self.matrice = []
        for i in range(self.n) :
            ligne = []
            for j in range(self.m) :
                ligne.append(Noeud(i,j))
            self.matrice.append(ligne)
        
        #Remplissage des voisins verticaux et horizontaux de chaque Noeud
        for i in range(self.n):
            for j in range(self.m):
                noeudactuel = self.matrice[i][j]
                voisins = []

                try :
                    if i >= 1 :
                        nord = self.matrice[i-1][j]
                        voisins.append(nord)
                except IndexError :
                    pass

                try :
                    sud = self.matrice[i+1][j]
                    voisins.append(sud)
                except IndexError :
                    pass

                try :
                    est = self.matrice[i][j+1]
                    voisins.append(est)
                except IndexError :
                    pass

                try :
                    if j>= 1 :
                        ouest = self.matrice[i][j-1]
                        voisins.append(ouest)
                except IndexError :
                    pass

                noeudactuel.voisins = voisins
    
##############################: FUNCTIONS :############################

def h(node: Noeud, end_node: Noeud):
    return node.manhattan(end_node)

def g(node: Noeud,parent: Noeud):
    return parent.g + 1


def pathfinder (start: tuple,end: tuple,graph: M_Graph,shelf: bool) :

    start_node   = graph.matrice[start]
    start_node.g = start_node.h = start_node.f = 0

    end_node   = graph.matrice[end]
    end_node.g = end_node.h = end_node.f = 0

    open_list    = []
    closed_list1 = []
    closed_list2 = []

    open_list.append(start_node)

    while len(open_list) > 0 :
        
        # Get the current node
        current_node  = start_node
        current_index = 0
        for index, node in enumerate(open_list):
            if node.f < current_node.f:
                current_node  = node
                current_index = index

        open_list.pop(current_index)
        closed_list1.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.coord)
                current = current.parent
            return path[::-1]

        # Children
        children = []
        for node in current_node.voisins :
            
            #Get rid of any shelf conflict 
            if not(shelf and node.have_shelf) :
                continue

            #Check if occupied in time range
            #TODO

            #Append
            children.append(node)

        # Loop through children
        for child in children:
            
            # Child is on the closed list
            for closed_child in closed_list1:
                if child == closed_child:
                    continue

                # Create the f, g, and h values
                child.g = g(child,current_node)
                child.h = h(child,end_node)
                child.f = child.g + child.h

                # Child is already in the open list
                for open_node in open_list:
                    if child == open_node and child.g > open_node.g:
                        continue

                # Add the child to the open list
                open_list.append(child)





##############################: PROGRAM :#############################

if __name__ == "__main__":
    
    graph = M_Graph((2,2))
    print([i.coord for i in graph.matrice[0][0].voisins])