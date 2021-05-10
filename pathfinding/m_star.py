import sys
sys.path.append("D:\Desktop\TIPE\KRO")

##############################: IMPORTS :############################
import math as m
import threading
import time
import database

##############################: GLOBAL VARIABLES :###################

matrice_test = [[0,0,0,0,0,0,0,0,0,0], 
                [0,0,1,0,0,0,0,0,0,0],
                [0,0,1,0,0,0,0,0,0,0],
                [0,0,1,0,0,0,0,0,0,0],
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

class inf :

    def __repr__(self) :
        return "infinity"

    def __eq__(self,other):
        if type(other) == type(self) :
            return True 
        return False 
    
    def __gt__(self,other) :
        if type(other) in [list,int,float] :
            return True
        if type(other) == inf :
            return False
        else :
            raise TypeError("Problème de typage")

    def __lt__(self,other):
        if type(other) in [list,int,float,inf] :
            return False
        raise TypeError("Problème de typage")

    def __le__(self,other):
        return self.__lt__(other) or self.__eq__(other)
    
    def __ge__(self,other):
        return self.__gt__(other) or self.__eq__(other)

class occupation_list :
    
    def __init__(self,liste:list[list[int]]) :
        self.occupation = liste
    
    def __repr__(self):
        return f"Occlist {self.occupation}"
    
    def occupation_add(self,segment) -> None :
        """ On choisi ici de retourner une erreur si le segment est mal structuré
        """

        if len(segment) != 2 :
            raise NameError(f"The segment {segment} is invalid (length != 2)")

        x,y = segment[0],segment[1]

        #Check the given segment
        if x > y :
            raise NameError(f"The segment [{x},{y}] was furnished instead of a valid segment at node {self}")
            return None
        if x==y :
            raise NameError(f"The singleton {x} was furnished instead of a valid segment at node {self}")
            return None

        #Check if the list is empty
        if self.occupation == [] :
            self.occupation.append(segment)
            return None

        #Loop through list
        for i in range(len(self.occupation)) :
            xi,yi = self.occupation[i][0],self.occupation[i][1]

            if i==0 and y <= xi :
                self.occupation.insert(0,segment)
                return None
            
            elif i==(len(self.occupation)-1) and yi <= x :
                self.occupation.append(segment)
                return None
            
            else :
                y1 = self.occupation[i-1][1]

                if y1 <= x < y <= yi :
                    self.occupation.insert(i,segment)
                    return None
        
        raise NameError("The intersection beetween the list and the segment is not empty")

    def occupation_remove_min(self,t) -> None :
        """Clean all the segment in the list that contain time lower than t"""
        temp_list = []
        for i in range(len(self.occupation)) :
            x,y = self.occupation[i][0],self.occupation[i][1]

            if y <= t :
                continue

            elif x <= t :
                temp_list.append([t,y])
            
            else :
                temp_list.append([x,y])
        
        self.occupation = temp_list

    def occupation_remove_max(self,t) -> None :
        """Clean all the segment in the list that contain time higher than t"""
        if type(t) == inf :
            return None
        
        temp_list = []
        for i in range(len(self.occupation)) :
            x,y = self.occupation[i][0],self.occupation[i][1]

            if x >= t :
                continue

            elif y >= t :
                temp_list.append([x,t])
            
            else :
                temp_list.append([x,y])
        
        self.occupation = temp_list

    def occupation_remove_min_and_actualise_to_0(self,t) -> None:
        temp_list = []
        for i in range(len(self.occupation)) :
            x,y = self.occupation[i][0],self.occupation[i][1]

            if y <= t :
                continue

            elif x <= t :
                temp_list.append([0,y-t])
            
            else :
                temp_list.append([x-t,y-t])
        
        self.occupation = temp_list

    def freetime_list(self,t) :
        """
        Fonction qui retourne la liste des temps libre sous la forme d'une liste de segment
        à partir de la date t. Les segments impraticables sont déjà enlevés
        La convention [0,inf] signifie que de 0 à l'infini c'est libre
        """
        list_after_t = [i for i in self.occupation if i[1] > t] #liste des créneaux après le temps t
        return_list = []
        n = len(list_after_t)
        if n == 0 :
            return [[t,inf()]]
        
        #Cas particulier n=1
        elif n == 1 :
            occ = list_after_t[0]
            if occ[0] < t or abs(t-occ[0]) <= database.max_move :
                return [[occ[1],inf()]]
            else :
                return [[t,occ[0]],[occ[1],inf()]]
        
        #Cas général
        #Sous-cas du premier segment
        occ = list_after_t[0]
        if not(occ[0] < t or abs(t-occ[0]) <= database.max_move) : #Si on a un espace entre t et le premier element
            return_list.append([t,occ[0]])

        #Cas des segments internes
        for i in range(1,n-1) :
            x = list_after_t[i][1]
            y = list_after_t[i+1][0]
            e = y-x
            assert e > 0
            if e > database.max_move :
                return_list.append([x,y])
        
        #Cas du dernier libre
        dernier = list_after_t[-1][1]
        return_list.append([dernier,inf()])

        return return_list

class Node(occupation_list) :

    def __init__(self,x: int,y: int):
        occupation_list.__init__(self,[])
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
        self.date_maxwait = inf()
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
    
    def get_wait_child_list(self,actual_time):
        """
        Prends en paramètre une heure d'arrivée, et retourne la liste des nouvelles cases
        virtuelles qui correspondent à cette même case, libre selon des créneaux spécifiques
        """
        #Cas terminal : Si le noeud n'est pas occupé, on renvoie alors child, puisque c'est le meilleur noeud sans temps d'attente
        if self.occupation == [] :
            return [self]
        
        #Fonction :
        return_liste = []
        liste_des_temps_libres = occupation_list(self.freetime_list(actual_time))

        #On va maintenant retirer les segments qui proposent une date d'attente d'au moins parent.date_maxwait
        if self.parent == None : #Arrive seulement si self est le noeud de depart
            t_max = inf()
        else :
            t_max = self.parent.date_maxwait

        liste_des_temps_libres.occupation_remove_max(t_max)
        #On a pas besoin de retirer les segments qui concernent des temps passés puisque freetime_list s'en charge

        #Il reste donc des segments de la forme [[x1,y1],[x2,y2],[x3,inf]] qui correspondent aux plages disponibles
        #On créer donc un noeud virtuel pour chaque, avec comme poids "p" (Soit p = xi-actual_time) le temps d'attente, et comme
        #date d'attente maximal la fin du segment yi : 
        
        #Data du noeud actuel :
        c1,c2   = self.coord

        for seg in liste_des_temps_libres.occupation :
            x,y = seg[0],seg[1]

            v_node = Node(c1,c2)
            v_node.voisins = self.voisins
            
            v_node.wait = x - actual_time
            v_node.date_maxwait = y

            return_liste.append(v_node)
        
        return return_liste
                        
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

    #Adding the date_maxwait to the first node
    #start_node.date_maxwait = inf()

    # Get the current node
    current_node  = start_node
    current_index = 0

    # Initialize both open and closed list
    open_list   = []
    closed_list = []


    open_list.append(start_node)

    # Adding a stop condition
    outer_iterations = 0
    max_iterations = (graph.m * graph.n)**2

    #! Loop until find the end
    while len(open_list) > 0 :
        outer_iterations += 1

        #If program has reach max search
        if outer_iterations > max_iterations:
            print("giving up on pathfinding too many iterations")
            return return_path(current_node)
        
        current_node = open_list[0] #pour trouver un min dans une liste
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
            # Straight Parents (on sépare cela de la fonction g pour l'instant car expérimental)
            plusvalue = get_straight_score_node(child,parent,start_node)

            # If child is occupied
            wait_child_list = child.get_wait_child_list(actual_time=parent.g)

            #On ne considère plus le noeud enfant de base
            for new_child in wait_child_list :
                # Create the f, g, and h values (for all created childs if delta > 0, else for the current child)
                new_child.g = (g(new_child,parent) + plusvalue) + new_child.wait
                new_child.h = h(new_child,end_node)
                new_child.f = new_child.g + new_child.h
                # Add the child parent (for all created childs if delta > 0, else for the current child)
                new_child.parent = parent
                # Add all or the child to the open list
                open_list.append(new_child)

##############################: PROGRAM :#############################

if __name__ == "__main__":
    
    graph = Graph((7,10))
    graph.fill_with_matrix(matrice_test)
    graph.fill_occupation_with_path([((0, 0), 0), ((0, 1), 0), ((0, 2), 0), ((0, 3), 0), ((0, 4), 0), ((0, 5), 0), ((0, 6), 0), ((0, 7), 0), ((0, 8), 0), ((0, 9), 0)])
    print(pathfinder((1,0),(0,9),graph))
