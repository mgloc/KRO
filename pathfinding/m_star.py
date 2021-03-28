##############################: IMPORTS :############################
import math as m
import threading
import time
import sys
import database

#TODO GLOBAL : Créer un objet occupation et les fonctions usuelles qui vont avec

##############################: GLOBAL VARIABLES :###################

matrice_test = [[0,0,0,0,0,0,0,0,0,0], 
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
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
            time.sleep(0.1)
            self.time += 1

class occupation_list :
    
    def __init__(self) :
        self.occupation = []
        self.taille = 0
    
    def occupation_add(self,segment) :

        x,y = segment[0],segment[1]

        #Check the order of the given segment
        if x > y :
            segment = [y,x]
            y,x = x,y
        
        if x==y :
            raise NameError(f"The singleton {x} was furnished instead of a valid segment")
            return None

        #Check if the list is empty
        if self.occupation == [] :
            self.occupation.append(segment)
            self.taille = 1
            return None

        #Loop through list
        for i in range(self.taille) :
            xi,yi = self.occupation[i][0],self.occupation[i][1]

            if i==0 and y <= xi :
                self.occupation.insert(0,segment)
                self.taille += 1
                return None
            
            elif i==(self.taille-1) and yi <= x :
                self.occupation.append(segment)
                self.taille += 1
                return None
            
            else :
                y1 = self.occupation[i-1][1]

                if y1 <= x < y <= yi :
                    self.occupation.insert(i,segment)
                    self.taille += 1
                    return None
        
        raise NameError("The intersection beetween the list and the segment is not empty")

    def occupation_remove_min(self,t) :
        temp_list = []
        for i in range(self.taille) :
            x,y = self.occupation[i][0],self.occupation[i][1]

            if y <= t :
                continue

            elif x <= t :
                temp_list.append([t,y])
            
            else :
                temp_list.append([x,y])
        
        self.occupation = temp_list

    def occupation_remove_min_and_actualise(self,t):
        temp_list = []
        for i in range(self.taille) :
            x,y = self.occupation[i][0],self.occupation[i][1]

            if y <= t :
                continue

            elif x <= t :
                temp_list.append([0,y-t])
            
            else :
                temp_list.append([x-t,y-t])
        
        self.occupation = temp_list

class Node(occupation_list) :

    def __init__(self,x: int,y: int):
        occupation_list.__init__(self)
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
        return ("Node({},{})".format(x,y))

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
            
class Graph :

    def __repr__(self):
        return ("Graph({},{})".format(self.n,self.m) )

    def __init__(self,taille: tuple):
        self.n,self.m = taille
        self.matrice = []

        self.fill_node_auto()
        self.fill_voisins_auto()

    def fill_node_auto(self) :
        if self.matrice != [] :
            raise NameError("Cette fonction est uniquement executable à l'initialisation d'un graph vide")

        else :    
            for i in range(self.n) :
                ligne = []
                for j in range(self.m) :
                    ligne.append(Node(i,j))
                self.matrice.append(ligne)

    def fill_voisins_auto(self):
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

    def compatibility_check(self,matrix) :
        if matrix == [] :
            raise NameError("An empty matrix was given")
            return False

        if self.n != len(matrix) or self.m != len(matrix[0]) :
            raise NameError("Dimensions are uncompatible \n Matrix : {},{} Graph : {},{}".format(len(matrix),len(matrix[0]),self.n,self.m))
            return False
        return True
      
    def fill_with_matrix(self,matrix) :
        if self.compatibility_check(matrix) :

            for i in range(self.n) :
                for j in range(self.m) :
                    if matrix[i][j] == 1 :
                        self.matrice[i][j].accessible = False
                    else :
                        self.matrice[i][j].accessible = True
    
    def fill_occupation_with_matrix(self,matrix) :
        if self.compatibility_check(matrix) :

            for i in range(self.n) :
                for j in range(self.m) :
                    liste_occupation = matrix[i][j]
                    if liste_occupation != [] :
                        current_node = self.matrice[i][j]
                        current_node.occupation = liste_occupation

    def fill_occupation_with_path(self,ppath) : #TODO Get clock
        #get current clock
        sum_time = 0 #<--putclockhere
        n        = len(ppath)

        #Explore path
        for index,elem in enumerate(ppath) :
            initial_time = sum_time
            coord = elem[0]

            #Check if there is a neccessity to wait before accessing the next node
            if index < n-1 :
                sum_time += ppath[index+1][1] #get waiting time before accessing the next node
            
            #Check if there is a turn to access the following node
            if 1 <= index < n-1 :
                sum_time += get_straight_score_coord(ppath[index+1][0],coord,ppath[index-1][0])
            
            #Adding the linear movement
            sum_time += database.horizontally_move_time
            
            #Adding the segment to the matrice
            i,j = coord
            self.matrice[i][j].occupation_add([initial_time,sum_time])
        
##############################: PATHFINDING FUNCTIONS :################

def h(node: Node, end_node: Node):
    return node.manhattan(end_node)*database.horizontally_move_time

def g(node: Node,parent: Node):
    return parent.g + database.horizontally_move_time

def return_path(current_node):
    path = []
    current = current_node
    while current is not None:
        path.append((current.coord,current.wait))
        current = current.parent
    return path[::-1]  # Return reversed path

def get_straight_score_coord(coord1:tuple,coord2:tuple,coord3:tuple) :
    x1 = coord1[0] - coord2[0]
    y1 = coord1[1] - coord2[1]
    x2 = coord3[0] - coord2[0]
    y2 = coord3[1] - coord2[1]

    if x1 != x2 and y1 != y2 :
        return database.rotation_move_time
    
    return 0

def get_straight_score_node(child:Node,parent:Node,starting_node:Node) :
    
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

def pathfinder (start: tuple,end: tuple,graph: Graph,shelf: bool =False) :

    #TODO #1 Simples vérifications de dimensions

    #TODO #2 Actualiser toute les listes temps d'occupation des noeuds

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
            final_path = return_path(current_node)
            graph.fill_occupation_with_path(final_path)
            return final_path

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
            plusvalue = get_straight_score_node(child,parent,start_node)

            # Child is occupied
            delta = child.minimum_waiting_time(parent.g)
            if delta != 0 :
                x,y = child.coord
                occupied_node = Node(x,y)
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
    
    graph = Graph((7,10))
    graph.fill_with_matrix(matrice_test)
    graph.fill_occupation_with_path([((0, 0), 0), ((0, 1), 0), ((0, 2), 0), ((0, 3), 0), ((0, 4), 0), ((0, 5), 0), ((0, 6), 0), ((0, 7), 0), ((0, 8), 0), ((0, 9), 0)])
    print(pathfinder((1,0),(0,9),graph))
