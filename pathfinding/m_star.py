##############################: IMPORTS :############################
import math as m
import threading
import time
import sys
import database

##############################: GLOBAL VARIABLES :###################

matrice_test = [[0,0,0,0,0,1,0,0,0,0], 
                [0,0,0,0,0,1,0,1,0,0],
                [0,0,0,0,0,1,0,0,0,1],
                [0,1,1,1,1,1,0,1,0,0],
                [0,0,0,1,0,0,0,1,0,0],
                [1,0,1,1,1,0,1,1,0,0],
                [0,0,0,0,0,0,1,0,0,0],]

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
        self.accessible = True

        #M-Star
        self.g = 0
        self.h = 0
        self.f = 0
        self.straight_parent = False
        self.wait = 0
        self.parent = None

    def __repr__(self):
        x,y = self.coord
        return ("Noeud({},{})".format(x,y))

    def __eq__(self, other):
        return self.coord == other.coord

    def reset_node(self):
        self.g = self.h = self.f = 0
        self.parent = None
    
    def manhattan(self,other) :
        x1,y1 = self.coord
        x2,y2 = other.coord
        return(abs(x2-x1) + abs(y2-y1))
    
    def minimum_waiting_time(self,total_time):
        if self.occupation == [] :
            return 0
        delta = (database.margin_error + database.max_move)/2
        segment =(total_time-delta,total_time+delta)
        
        if total_time + delta <= self.occupation[0][0] :
            return 0
        
        n = len(self.occupation)
        for i in range(0,n-1) :
            act = self.occupation[i]
            nxt = self.occupation[i+1]

            if act[1] <= total_time :
                continue

            elif act[1] + 2*delta <= nxt[0] :
                return (act[1]-total_time)
        
        return (self.occupation[-1][1]-total_time)
            
class M_Graph :

    def __repr__(self):
        return ("Graph({},{})".format(self.n,self.m) )

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

    def fill_with_matrix(self,matrix) : #BUG ça marche étonnament pas ?
        if matrix == [] :
            raise NameError("An empty matrix was given")

        if self.n != len(matrix) or self.m != len(matrix[0]) :
            raise NameError("Dimensions are uncompatible \n Matrix : {},{} Graph : {},{}".format(len(matrix),len(matrix[0]),self.n,self.m))

        for i in range(self.n) :
            for j in range(self.m) :
                if matrix[i][j] == 1 :
                    self.matrice[i][j].accessible = False
                else :
                    self.matrice[i][j].accessible = True
    
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
    return node.manhattan(end_node)*database.horizontally_move_time

def g(node: Noeud,parent: Noeud):
    return parent.g + database.horizontally_move_time

def return_path(current_node):
    path = []
    current = current_node
    while current is not None:
        path.append((current.coord,current.wait))
        current = current.parent
    return path[::-1]  # Return reversed path

def get_straight_score(child:Noeud,parent:Noeud,starting_node:Noeud) :
    
    if parent == starting_node :
        return 0

    pparent = parent.parent

    x1   = child.coord[0] - parent.coord[0]
    y1   = child.coord[1] - parent.coord[1]
    x2   = pparent.coord[0] - parent.coord[0]
    y2   = pparent.coord[1] - parent.coord[1]

    if x1 != x2 and y1 != y2 :
        return database.rotation_move_time
    
    return 0

def pathfinder (start: tuple,end: tuple,graph: M_Graph,shelf: bool =False) :

    #! Peut-être actualiser toute les listes temps d'occupation des noeuds

    # Create start and end node
    start_node   = graph.matrice[start[0]][start[1]]
    start_node.g = start_node.h = start_node.f = 0
    end_node   = graph.matrice[end[0]][end[1]]
    end_node.g = end_node.h = end_node.f = 0

    # Get the current node
    current_node  = start_node
    current_index = 0

    # Initialize both open and closed list
    open_list   = []
    closed_list = []


    open_list.append(start_node)

    # Adding a stop condition
    outer_iterations = 0
    max_iterations = (graph.m * graph.n)

    #! Loop until find the end
    while len(open_list) > 0 :
        outer_iterations += 1

        #If program has reach max search
        if outer_iterations > max_iterations:
            print("giving up on pathfinding too many iterations")
            return return_path(current_node)
        
        current_node = open_list[0]  #BUG FIX : perpetual Node(0,0)
        
        # Get the current node
        for index, node in enumerate(open_list):
            if node.f < current_node.f:
                current_node  = node
                current_index = index

        open_list.remove(current_node)    #O(1) en recherche
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

            #Skip if this node is not obstruated
            if not(node.accessible) :
                continue

            #Append
            children.append(node)

        #! Loop through children
        for child in children:
            
            # Child is on the closed list
            if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                continue

            # Child is already in the open list
            if len([open_node for open_node in open_list if child == open_node and child.g > open_node.g]) > 0:
                continue

            # Consider the parent node
            parent = current_node

            #Valeur à ajouter à la fin au g du noeud
            plusvalue = 0

            # Straight Parents
            plusvalue = get_straight_score(child,parent,start_node)

            # Child is occupied
            delta = child.minimum_waiting_time(parent.g)
            if delta != 0 :
                x,y = child.coord
                occupied_node = Noeud(x,y)
                occupied_node.voisins = child.voisins
                occupied_node.wait += delta
                plusvalue += delta

                child = occupied_node #On ne considère plus le noeud enfant de base

            # Create the f, g, and h values
            child.g = g(child,parent) + plusvalue
            child.h = h(child,end_node)
            child.f = child.g + child.h

            # Add the child parent
            child.parent = parent

            # Add the child to the open list
            open_list.append(child)

##############################: PROGRAM :#############################

if __name__ == "__main__":
    
    graph = M_Graph((7,10))
    graph.fill_with_matrix(matrice_test)
    print(pathfinder((0,0),(6,9),graph))
