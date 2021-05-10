class inf :

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

class Node(occupation_list) :

    def __init__(self,x: int,y: int):
        occupation_list.__init__(self)

oc1 = occupation_list([])
oc2 = occupation_list([])

oc1.occupation.append("sexe")
print(oc2.occupation)
