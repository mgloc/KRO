#===IMPORTATIONS=============================================================================== :
from tkinter import Tk,Grid,Canvas,Label,Button
import random
import time
import sys

#VARAIBLES :
tailledehangar = [10,15] #lignes, colonnes
compteur = 0
listedesrobots = []
listedesarmoires = []
listedesrequêtes = [] #pour le moment, une requete = position d'une armoire
switch_couloir = {1:0,2:3,4:3,5:6,7:6,8:9,10:9,11:12,13:12}

#FONCTIONS CUSTOMISÉES :

#? Défini les armoires propre au hangar n°1 ainsi que les différentes zones
def set_hangar1() :
    
    #Armoires
    for colonne in [1,2,4,5,7,8,10,11,13] :
        for ligne in range(1,7) :
            globals()['armoire'+str(colonne)+str(ligne)] = armoire(colonne,ligne)

    #Affichage
    main_w.scan_draw_loop()

def requete_test():
    listedesrequêtes.append([7,7])

#===FONCTIONS UTILITAIRES=============================================================================== :
#? Recherche l'existence d'un doublon dans une liste
def existe_double(liste) :
    liste.sort()
    for i in range(len(liste)-1):
        if liste[i] == liste[i+1] :
            return(True)
    return(False)

def check_zone(zone,irobot): #simplifiable en return ( condition du if )
    if (zone[0][0] <= irobot.posx <= zone[0][1]) and (zone[1][0] <= irobot.posy <= zone[1][1]) :
        return True
    return False

def check_égalité_point(point1,point2):
    return (point1 == point2)
    
def check_présence_robot(point):
    'Renvoie un booléen selon la présence d\'un robot aux coordonnées entrées'
    for krobot in listedesrobots :
        if (krobot.posx == point[0]) and (krobot.posy == point[1]) :
            return True
    return False

def id_robot_point(point):
    "Regarde si il y a un robot sur une case et le renvoie, si il n'y a pas de robot sur la case, renvoie FALSE"
    for irobot in listedesrobots :
        if check_égalité_point([irobot.posx,irobot.posy],point) :
            return irobot
    return False

def ajout_id_liste(mouvement,n,irobot) :
    for _ in range(n) :
        irobot.listedesinstructions.append(mouvement)

def signe(x):
    if x >= 0 :
        return 1
    return -1

def création_chemin_récupération_armoire(robot_init,coordonneés_armoire):
    #On check si il n'y a pas un robot qui puisse bloquer le départ de notre robot
    case1 = données.case_croisement_1
    case2 = données.case_croisement_2
    if check_présence_robot(case2):
        robot_init.listedesinstructions.extend(['pass','pass'])
    elif check_présence_robot(case1):
        robot_init.listedesinstructions.append('pass')
    #Génération du chemin
    robot_init.listedesinstructions.extend(['a','t_d','a'])
    couloir_armoire = switch_couloir[coordonneés_armoire[0]]

    if couloir_armoire != 0 :
        robot_init.listedesinstructions.append('t_d')
        robot_init.listedesinstructions.extend(['a']*couloir_armoire)
        robot_init.listedesinstructions.append('t_g')
    
    robot_init.listedesinstructions.extend(['a']*(données.couloir_ciculation_bas-coordonneés_armoire[1]))
    pickup_armoire(couloir_armoire,robot_init,coordonneés_armoire)
    robot_init.listedesinstructions.extend(['a']*coordonneés_armoire[1])
    robot_init.listedesinstructions.append(['t_d'])
    robot_init.listedesinstructions.extend(['a']*(tailledehangar[0]-couloir_armoire-1))
    robot_init.listedesinstructions.append(['t_d'])
    robot_init.listedesinstructions.extend(['a']*(données.zone_livraison[1][0]-1))
    
def pickup_armoire(couloir_armoire,robot_init,coordonneés_armoire) :
    if couloir_armoire < coordonneés_armoire[1] :
        robot_init.listedesinstructions.extend(['t_d','a','t_dt','l_on','a','t_d'])
    else :
        robot_init.listedesinstructions.extend(['t_g','a','t_dt','l_on','a','t_g'])

#===OBJETS=============================================================================== :

class données :
    #Variables
    zone_init = [[1,11],[8,8]]
    point_init = [1,8]
    zone_angle_sens = 90
    zone_livraison = [ [10,9],[14,9] ]
    point_livraison = [14,9]
    case_croisement_1 =  [0,8]
    case_croisement_2 =  [0,9]
    couloir_ciculation_bas = 7

class robot : 
    "Initialise un robot de rangement d'armoire; Le robot peut juste avancer, tourner et modifier l'état de son levier"
    def __init__(self,x=0,y=0,angle=0) :

        self.posx = x       #on défini le repère positif de gauche vers droite et de haut vers bas (matrice)
        self.posy = y
        self.angle = angle  #robot.angle défini l'angle du robot, Nord = 0, Sud = 180, Ouest = 90, Est = 270
        self.levier = 0     #robot.levier = 1 (resp. 0) ===> Le robot a son levier tendu (resp. contracté)
        self.armoire_portee = None

        self.listedesinstructions = []
        self.compteurdesinstructions = 0

        self.switch_mov = {'a' : self.avancer, 
                         't_d' : self.tourner_droite,
                         't_g' : self.tourner_gauche,
                        't_dt' : self.tourner_demitour,
                        'pass' : self.ne_rien_faire,
                        'l_on' : self.levier_on,
                        'l_off':self.levier_off}

        listedesrobots.append(self)

    #Fonctions de levier
    def levier_on(self) :
        self.levier = 1
        # Enregistrement de l'armoire cible dans une base
        self.armoire_portee = self.verrouiller_armoire(listedesarmoires)
        # On met maintenant l'armoire dans un endroit "néant" => En réalité elle se situe sur le robot
        if self.armoire_portee != None :
            self.armoire_portee.posx = -10
            self.armoire_portee.posy = -10

    def levier_off(self) :
        self.levier = 0
        self.deverouiller_armoire()
        
    #Fonctions de déplacements

    def ne_rien_faire(self):
        pass

    def avancer(self) :
        if   self.angle   == 0 :
             self.posy    += -1
        elif self.angle   == 180 :
             self.posy    += 1
        elif self.angle   == 90 :
             self.posx    += -1
        elif self.angle   == 270 :
             self.posx    += 1
        else: 
            print("Le robot est dans un angle non valide")
    
    def tourner_custom(self,choix_angle) :
        if self.angle == choix_angle :
            pass
        elif (self.angle-180)%360 == choix_angle :
            self.tourner_demitour()
        elif (self.angle-90)%360 == choix_angle :
            self.tourner_droite()
        else :
            self.tourner_gauche()

    def tourner_gauche(self) :
        self.angle += 90
        self.angle = self.angle % 360
    
    def tourner_droite(self) :
        self.angle += -90
        self.angle = self.angle % 360
    
    def tourner_demitour(self) :
        self.angle += 180
        self.angle = self.angle % 360

    #Fonctions de scan (en cas réel elles sont impossibles à créer mais remplacées par des capteurs physique (ex : laser pour presence_armoire))
    def verrouiller_armoire(self,listedesarmoires):
        for iarmoire in listedesarmoires :
            if (iarmoire.posx == self.posx) and (iarmoire.posy == self.posy) :
                return(iarmoire)
        return(None)
    
    def deverouiller_armoire(self) :
        if self.armoire_portee != None :
            self.armoire_portee.posx = self.posx
            self.armoire_portee.posy = self.posy
            self.armoire_portee = None    

class armoire :
    "Initialise une armoire"
    def __init__(self,x=0,y=0): 
        self.posx       = x
        self.posy       = y
        listedesarmoires.append(self)
    
    def set_position(self,x,y): 
        self.posx = x
        self.posy = y

class controlleur_fixe(robot,armoire) :
    "Séquence de contrôles tests"
    def __init__(self):
        robot1 = robot(8,8,0)
        robot1.posx = robot1.posx
        
class windows :
    "Interface de visualisation matriciel"
    def __init__(self):
        self.fenetre = Tk()
        self.fenetre.resizable(width=False, height=False)
        self.tableau = [[0]*tailledehangar[1] for i in range(tailledehangar[0])]
        self.compteur = 0

        #Les 3 couleurs à utiliser
        self.couleurs ={
          0: 'white'   #Vide (blanc)
        , 1: '#ff2f1d' #Robot (rouge)
        , 2: '#d06c10' #Armoire (orange)
        , 3: '#ffb380' #Robot qui porte une armoire (beige)
        }

        #Dimensions du canevas
        self.can_width  = 50*tailledehangar[1]
        self.can_height = 50*tailledehangar[0]
 
        #Taille d'une case
        self.size = 50
 
        #Canevas
        self.can = Canvas(self.fenetre, width=self.can_width, height=self.can_height)
        self.can.grid()

        #Compteur
        self.compteur_lbl = Label(self.fenetre, text=str(compteur), font=("", 16))
        self.compteur_lbl.grid(padx=8, pady=8)

        #Bouton
        self.bouton_lancer_fonction = Button(self.fenetre, text="Lancer la fonction test", command=controlleur_fixe)
        self.bouton_lancer_fonction.grid(row=2,column=0)
        
        self.bouton_lancer_fonction = Button(self.fenetre, text="Lancer la fonction controlleur", command=controlleur)
        self.bouton_lancer_fonction.grid(row=1,column=0)

        self.bouton_lancer_requete_test = Button(self.fenetre, text="Lancer la requête test", command=requete_test)
        self.bouton_lancer_requete_test.grid(row=0,column=1)

        self.bouton_set_hangar = Button(self.fenetre, text="Placer set n°1", command=set_hangar1)
        self.bouton_set_hangar.grid(row=3,column=0)
        
        #Création grille départ
        for ligne in range(tailledehangar[0])  : 
            for colonne in range(tailledehangar[1]): 
                self.can.create_rectangle(colonne*self.size,      #x0
                                          ligne*self.size,        #y0
                                          (colonne+1)*self.size,  #x1
                                          (ligne+1)*self.size,    #y1
                                          fill = self.couleurs[self.tableau[ligne][colonne]]) #option

    #*Méthodes utilitaires
    def placer_objet(self,posx=0,posy=0,couleur_objet=0) :
        if (0 <= posx <= tailledehangar[1]) and (0 <= posy <= tailledehangar[0]) :
            self.tableau[posy][posx] = couleur_objet
    
    def nettoyer_case(self,posx=0,posy=0) :
        if (0 <= posx <= tailledehangar[1]) and (0 <= posy <= tailledehangar[0]) :
            self.tableau[posy][posx] = 0
    
    def nettoyer_toutes_cases(self) :
        self.tableau = [[0]*tailledehangar[1] for i in range(tailledehangar[0])]
        #Draw :
        for ligne in range(tailledehangar[0]) :
            for colonne in range(tailledehangar[1]) :
                self.can.create_rectangle(colonne*self.size,      #x0
                                          ligne*self.size,        #y0
                                          (colonne+1)*self.size,  #x1
                                          (ligne+1)*self.size,    #y1
                                          fill = self.couleurs[self.tableau[ligne][colonne]]) #option

    def scan_draw_loop(self) :
        "Scan les positions des objets et les affichent dans le canvas"
        #Effacer la grille en mémoire :
        self.nettoyer_toutes_cases()
        #Reperer les robots et les placer en mémoire
        for irobot in listedesrobots :
            if irobot.armoire_portee == None :
                self.placer_objet(irobot.posx,irobot.posy,1)
            else :
                self.placer_objet(irobot.posx,irobot.posy,3)
        for iarmoire in listedesarmoires :
            self.placer_objet(iarmoire.posx,iarmoire.posy,2)
        #Dessiner la grille :
        for ligne in range(tailledehangar[0]) :
            for colonne in range(tailledehangar[1]) :
                if self.tableau[ligne][colonne] != 0 :
                    self.can.create_rectangle(colonne*self.size,  #x0
                                          ligne*self.size,        #y0
                                          (colonne+1)*self.size,  #x1
                                          (ligne+1)*self.size,    #y1
                                          fill = self.couleurs[self.tableau[ligne][colonne]]) #option
        self.fenetre.update() #met à jour l'interface
        self.compteur += 1
        time.sleep(1)         #laisse à l'utilisateur le temps de voir le robot

    def incremente_loop(self):
        "Incrémente le compteur à chaque seconde"
        global compteur
        compteur += 1
        self.compteur_lbl['text'] = str(compteur)
        self.fenetre.after(1000, self.incremente_loop)

class controlleur(données) :
    "Le controlleur est l'unitée principal du programme, c'est lui qui s'occupe de transferer les lignes d'ordres aux robots"
    
    def __init__(self) :
        while True : #a modifier avec while "Fenetre est ouverte"
            #? CHECK INACTIVITEE/DEPLACEMENT AUTO EN ATTENTE :
            for irobot in listedesrobots :
                if check_zone(self.zone_init, irobot) and not(check_présence_robot([irobot.posx - 1, irobot.posy])) and not(check_égalité_point([irobot.posx,irobot.posy],self.point_init)):
                    irobot.tourner_custom(self.zone_angle_sens)
                    irobot.avancer()
            
            #? CHECK REQUETES
            if listedesrequêtes != [] :
                if check_présence_robot(self.point_init) : #on regarde si il y a un robot sur la case initialisation
                    robot_init = id_robot_point(self.point_init)                 #on récupère l'id du robot
                    coordonnées_armoire = listedesrequêtes[0]
                    del listedesrequêtes[0]
                    création_chemin_récupération_armoire(robot_init,coordonnées_armoire)


            # ENVOI DE L'EXECUTION AU ROBOT (tâche normalement SQL):
            
            #? EXECUTION DES ROBOTS :


            #? CHECK COLLISION (armoires):
            listedespositions_temp = []
            for iarmoire in listedesarmoires :
                if (iarmoire.posx,iarmoire.posy) != (-10,-10) :
                    listedespositions_temp.append((iarmoire.posx,iarmoire.posy))
            for irobot in listedesrobots :
                if irobot.armoire_portee != None :
                    listedespositions_temp.append((irobot.posx,irobot.posy))

            if existe_double(listedespositions_temp) :
                print("Collision entre armoires")
                sys.exit(0)
            
            #? CHECK COLLISION (robots):
            listedespositions_temp = []
            for irobot in listedesrobots :
                listedespositions_temp.append((irobot.posx,irobot.posy))

            if existe_double(listedespositions_temp) :
                print("Collision entre robots")
                sys.exit(0)

            #? AFFICHAGE
            main_w.scan_draw_loop()

#===INITITALISATION D'AFFICHAGE=============================================================================== :
main_w = windows()
main_w.incremente_loop()

#BOUCLE AFFICHAGE :
main_w.fenetre.mainloop()


##TODO Idée : 
  # Grande boucle while :

    #? Event créé avec un bouton et stacké dans une liste


    # Truc principaux du robot : Aller chercher un objet sur une armoire puis ramener l'armoire ( en checkant si personne ne veux justement cette armoire)
    # Aller chercher une armoire et la remplir avec un objet
    # Mettre une limite d'objet sur une armoire