from django.shortcuts import render

import numpy as np

# Fonction pour ajouter des variables d'ecart
def ajout_variables_ecart(nb_contraintes, objectif, contraintes):
    matrice_identite = np.eye(nb_contraintes)
    
    matrice_null =  np.zeros((1, nb_contraintes))  # Assurez-vous que matrice_null est également 2D   
    objectif = np.hstack((objectif, matrice_null))
    contraintes = np.hstack((contraintes, matrice_identite))
    return (objectif, contraintes)
    
'''def nom_variables(objectif_etendus):
    indice_variables = []
    for i in range(len(objectif_etendus[0])):
        indice_variables.append(i)
    return indice_variables'''

# Retourner la solution realisable
def solution_realisable(second_membre):
    indices_tries = np.argsort(second_membre[:, 0])
    matrice_triee = second_membre[indices_tries]
    #print(matrice_triee)
    legende = []
    solution = []
    #print(second_membre)
    for i in range(1,len(matrice_triee)):
        legende.append("x"+str(int(matrice_triee[i][0])))
        solution.append(matrice_triee[i][1])
        
    #print(matrice_triee)
    return [legende, solution, ['Z',matrice_triee[0][1]]]

# Retourner l'indice de la variable entrante
def indice_variable_entrante(objectif):
     
    # Utilisez un masque pour sélectionner uniquement les valeurs négatives
    #valeurs_negatives = objectif[objectif < 0]
   
    # Récupérez l'indice de la valeur négative la plus petite
         
    return np.argmin(objectif)

# Retourner l'indice de la variable sortante    
def indice_variable_sortante(contraintes_etendus, second_membre, indice):
    l = []
    j = 0
    
    for i in range(len(second_membre)-1):
        
        if second_membre[i][1] != 0:
            
            if contraintes_etendus[j][indice] != 0:
                l.append([second_membre[i][0],second_membre[i][1]/contraintes_etendus[j][indice]])
            j += 1
    
    k = l[0]
    
    for i in range(len(l)):
        if l[i][1] < k[1]:
            k = l[i]
                
    return k[0]
 
# Diviser la ligne de pivot par le pivot
def dif_ligne_piv(contraintes_etendus, second_membre, indice_entrante, indice_sortante):
    
    
    #print((indice_sortante - 3))
    
    pivot = contraintes_etendus[indice_sortante - 3][indice_entrante]
    for j in range(len(contraintes_etendus[indice_sortante - 3])):
        contraintes_etendus[indice_sortante - 3][j] = contraintes_etendus[indice_sortante - 3][j]/pivot
    
    #print("1",second_membre)

    #print(second_membre[indice_sortante - 1][1]/pivot)
    
    second_membre[indice_sortante - 1][1] =  second_membre[indice_sortante - 1][1]/pivot 
    
    #print(second_membre[indice_sortante - 1][1])
    
    #print("2",second_membre)
        
# La variable entrante prend la place de la variable sortante    
def echanger_entrante_sortante(second_membre, indice_entrante, indice_sortante):
    i = np.where(second_membre[:, 0] == indice_entrante)[0][0]
    j = np.where(second_membre[:, 0] == indice_sortante)[0][0]
    
    
    second_membre[j][0] , second_membre[i][0] = second_membre[i][0],  second_membre[j][0]
    
# Pivotage 
def pivotage(second_membre, objectif_etendus, contraintes_etendus, indice_entrante, indice_sortante):
    ligne_pivot = contraintes_etendus[indice_sortante - 3]
    pivot = objectif_etendus[0][indice_entrante]
      
    for i in range(len(objectif_etendus[0])):
        objectif_etendus[0][i] = objectif_etendus[0][i] - pivot * ligne_pivot[i]
        
    
    #print(" Z ",second_membre[-1][1])
    #print("Pivot : ", pivot)
    #print(second_membre)
    #print("Valeur sortante : ",second_membre[indice_sortante - 1])
    
    #print(indice_sortante - 1)
        
    second_membre[-1][1] = second_membre[-1][1] - pivot * second_membre[indice_sortante - 1][1]
    
    
    
    for i in range(2,len(second_membre)-1):
        if i != indice_sortante - 1:
            pivot = contraintes_etendus[i-2][indice_entrante]
            #print("pivot : ",pivot)
    
            second_membre[i][1] = second_membre[i][1] - pivot * second_membre[indice_sortante-1][1]
            
    #print(second_membre)
            
            
    
    for i in range(len(contraintes_etendus)):
        if i != indice_sortante - 3:
            pivot = contraintes_etendus[i][indice_entrante]
            for j in range(len(contraintes_etendus[i])):
                contraintes_etendus[i][j] = contraintes_etendus[i][j] - pivot * ligne_pivot[j]
    
       
    
def solution_simplexe(nb_variable, nb_contraintes, objectif, contraintes, second_membre):
    # Ajouter des variables d'ecart
    objectif_etendus = ajout_variables_ecart(nb_contraintes, objectif, contraintes)[0]
    contraintes_etendus = ajout_variables_ecart(nb_contraintes, objectif, contraintes)[1]
    
    
    while 1:
        
        # Indice de la variable entrante
        indice_entrante = int(indice_variable_entrante(objectif_etendus))
        #print(indice_entrante)
        #print(objectif_etendus[0][indice_entrante])
        
        if objectif_etendus[0][indice_entrante] >= 0:
            solution = solution_realisable(second_membre)
            #print(contraintes_etendus)
            #print(objectif_etendus)
            return solution
            
            

        indice_sortante = int(indice_variable_sortante(contraintes_etendus, second_membre, indice_entrante))
        
        dif_ligne_piv(contraintes_etendus, second_membre, indice_entrante, indice_sortante)
        
        echanger_entrante_sortante(second_membre, indice_entrante, indice_sortante)
           
        pivotage(second_membre, objectif_etendus, contraintes_etendus, indice_entrante, indice_sortante)

def index(request):
    # Exemple d'utilisationnb_variable = 2
    nb_variable = 2
    nb_contraintes = 3
    objectif = np.array([[1,-4, -7]])
    contraintes = np.array([[0, 4, 0],
                            [0, 0, 5],
                            [0, 4, 7]])
    second_membre = np.array([[1,0], [2,0], [3,13], [4,6], [5,5], [0,0]], dtype=float)

    solution = solution_simplexe(nb_variable, nb_contraintes, objectif, contraintes, second_membre)
    return render(request, 'index.html', {'solution': solution})

def saisie(request):
    if request.method == 'POST':
        nb_variable = int(request.POST.get('number1'))
        nb_contraintes = int(request.POST.get('number2'))

        indices_objectifs = []
        for i in range(nb_variable):
            indices_objectifs.append(i+1)

        indices_contraintes = []
        for i in range(nb_contraintes):
            l = []
            for j in range(nb_variable):
                l.append(str(i)+str(j))
            indices_contraintes.append(l)

        second_membre = []
        for i in range(nb_contraintes):
            second_membre.append(i+1)


        context = {
            'indices_objectifs': indices_objectifs,
            'indices_contraintes': indices_contraintes,
            'nb_variable': nb_variable,
            'nb_contraintes': nb_contraintes,
            'second_membre': second_membre

        }
        #print(nb_variable)
        #print(nb_contraintes)

    return render(request, 'saisie.html', context)

def result(request, nb_variable, nb_contraintes):
    if request.method == 'POST':
        #nb_variable = request.POST.get('number1')
        #nb_contraintes = 

        # Objectifs
        l = [1]
        for i in range(nb_variable):
            number = 'number' + str(i+1)
            l.append(-int(request.POST.get(number)))

        objectif = np.array([l])

        print("Objectif : ",objectif)

        # Contraintes
        l = []
        for i in range(nb_contraintes):
            tmp = [0]
            for j in range(nb_variable):
                number = 'contrainte' + str(i) + str(j)
                tmp.append(int(request.POST.get(number)))
            l.append(tmp)

        contraintes = np.array(l)

        #print("Les contraintes : ")
        print(contraintes)

        # Second Membre
        l = []
        for i in range(nb_variable):
            l.append([i+1, 0])

        k = 1
        for j in range(nb_variable+1, nb_variable + nb_contraintes + 1):
            number = 'second_membre' + str(k)
            l.append([j,int(request.POST.get(number))])
            k += 1
        l.append([0,0])

        second_membre = np.array(l, dtype=float)

        print(second_membre)

        solution = solution_simplexe(nb_variable, nb_contraintes, objectif, contraintes, second_membre)
        z = solution[2][1]
        print(solution)
        print(z)
        dictio = {}
        for i in range(nb_variable):
            dictio[solution[0][i]] = solution[1][i]

        print(dictio)

        context = {
            'dictio': dictio,
            'z': z,
        }
        

    return render(request, 'result.html', context)
