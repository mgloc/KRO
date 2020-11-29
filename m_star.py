#IMPORTS :
import math as m
import threading
import time

#VARIABLES :
caractères = [0, #Vide
              1, #Blocage
             "D",#Départ
             "A"]#Arrivée

matrice_test = [[0,0,0,0,0,0,0,0,0,0], #mettre des valeurs réelle estimation distance durée + horloge
                [0,0,0,0,0,1,0,"A",0,0],
                [0,0,0,0,0,1,0,0,0,0],
                [0,0,0,0,0,1,0,0,0,0],
                [0,0,0,0,0,1,0,0,0,0],
                [0,"D",0,0,1,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],]


#FONCTIONS :

def manhattan(A,B):
    xA,yA = A
    xB,yB = B
    return abs(xB-xA) + abs(yB-yA)

#OBJETS :

class Horloge :

    def __init__(self) :
        self.set_time()
        print("Horloge initialisée à {}".format(self.time))

    def set_time(self) :
        self.time = time.time()
    
    def get_time(self,rounded=True) :
        #Récupère le temps écoulé depuis le dernier set_time
        if rounded :
            return round(time.time() - self.time, 3)
        else :
            return time.time() - self.time

class Matrice_temporelle(Horloge) :

    def __init__(self,taille=(0,0)):
        self.x,self.y = taille
        self.matrice = [[0.0]*self.x]*self.y
        self.set_time()
    
    def send_trajectory(self,liste):
        #fonction qui reçoit une liste de mouvement et qui l'ajoute à la liste
        pass

    def actualiser(self):
        #Fonction qui retire le temps qui s'est écoulé à toute la matrice
        delta = self.get_time()
        for i in range(self.x) :
            for j in range(self.y) :
                case = self.matrice[i][j]
                self.set_case(i,j,round(case - delta,3))

    def get_case(self,a,b) :
        self.actualiser()
        return self.matrice[a][b]

    def get_matrice(self) :
        self.actualiser()
        return self.matrice

    def set_case(self,a,b,x):
        if x >= 0.0 :
            self.matrice[a][b] = x
        else :
            self.matrice[a][b] = 0.0 
        
    


#PROGRAMME :

main_clock = Horloge()

matrice = Matrice_temporelle((1,1))
matrice.set_case(0,0,10)
time.sleep(2)
print(matrice.get_matrice())
matrice.get_time()