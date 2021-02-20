##############################: IMPORTS :############################
import math as m
import threading
import time
import sys
import database

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

#############################: CLASS :###############################

class Clock(threading.Thread) :
    def __init__(self):
        threading.Thread.__init__(self)
        self.time = 0
        self.is_running = True

    def run(self) :
        print("Clock started")
        while is_running :
            time.sleep(0.100000)
            self.time += 1

class Noeud :

    def __init__(self,x: int,y: int):
        self.occupation = [] #liste temps
        self.voisins = []
        self.coord = (x,y)
        self.have_shelf = False

        #M-Star
        self.g = 0
        self.h = 0
        self.t = 0
        self.f = 0
        self.straight_parent = False

    def __eq__(self, other):
        return self.coord == other.coord

    def reset_node(self):
        self.g = self.h = self.f = 0
        self.parent = None
    
    def manhattan(self,other) :
        x1,y1 = self.coord
        x2,y2 = other.coord
        return(abs(x2-x1) + abs(y2-y1))
    
    def is_occupied(self,g) : #TODO fusionner is_occupied avec near_freetime 
        segment = (g - database.margin_error, g + database.margin_error)
        return intersection_is_empty(segment,self.occupation)
    
    def near_freetime(self,tot) :
        n = len(self.occupation)
        segment = (tot - database.margin_error, tot + database.margin_error + database.max_move)
        for (index,temps) in enumerate(self.occupation) :
            pass



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
    
##############################: GENERAL FUNCTIONS :####################

def intersection_is_empty(segment1:tuple,semgment2:tuple) :
    """
    return True if the intersection beetween the two given segments is empty
    """
    i1,i2 = segment1
    j1,j2 = semgment2
    return (i2 <= j1) or (j2 <= i1)

def intersection_is_empty_list(segment:tuple,liste:list) :
    """
    return True if the intersection beetween the given segment and the union of the other listed segment is empty
    """
    temp_bool = True
    for segment2 in liste :
        temp_bool = temp_bool and intersection_is_empty(segment,segment2)
        
##############################: PATHFINDING FUNCTIONS :################

def h(node: Noeud, end_node: Noeud):
    return node.manhattan(end_node)

def g(node: Noeud,parent: Noeud):
    return parent.g + 1

def return_path(current_node):
    path = []
    current = current_node
    while current is not None:
        path.append(current.position)
        current = current.parent
    return path[::-1]  # Return reversed path

def pathfinder (start: tuple,end: tuple,graph: M_Graph,shelf: bool =False) :

    # Create start and end node
    start_node   = graph.matrice[start[0]][start[1]]
    start_node.g = start_node.h = start_node.f = 0
    end_node   = graph.matrice[end[0]][end[1]]
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list    = []
    closed_list = []


    open_list.append(start_node)

    # Adding a stop condition
    outer_iterations = 0
    max_iterations = (graph.m * graph.n // 2)

    # Loop until find the end
    while len(open_list) > 0 :
        outer_iterations += 1

        #If program has reach max search
        if outer_iterations > max_iterations:
          return None
        
        # Get the current node
        current_node  = start_node
        current_index = 0
        for index, node in enumerate(open_list):
            if node.f < current_node.f:
                current_node  = node
                current_index = index

        open_list.pop(current_index)    #O(1) en recherche
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            return return_path(current_node)

        # Children
        children = []
        for node in current_node.voisins :
            
            #Get rid of any shelf conflict 
            if shelf and node.have_shelf :
                continue

            #Append
            children.append(node)

        # Loop through children
        for child in children:
            
            # Child is on the closed list
            if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                continue

            # Child is already in the open list
            if len([open_node for open_node in open_list if child.position == open_node.position and child.g > open_node.g]) > 0:
                continue

            # Consider the parent node
            parent = current_node

            # Straight Parents #TODO
            straight_score = 0 #temp

            # Child is occupied
            if child.is_occupied(straight_score + g) :
                pass #TODO


            # Create the f, g, and h values
            child.g = g(child,current_node)
            child.h = h(child,end_node)
            child.f = child.g + child.h + child.t

            # Add the child to the open list
            open_list.append(child)

##############################: PROGRAM :#############################

if __name__ == "__main__":
    
    graph = M_Graph((2,2))
    print([i.coord for i in graph.matrice[0][0].voisins])