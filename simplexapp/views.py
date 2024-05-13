from django.shortcuts import render
import heapq

def slack_variables(c,A):
    n = len(A)
    c += [0]*n
    
    M = [[0]*n for j in range(n)]
    
    for i in range(len(M)):
        M[i][i] = 1
        A[i] += M[i]


'''
   Renvoie une matrice d'identité rectangulaire avec les entrées diagonales spécifiées, commençant éventuellement au milieu.
'''
def identity(numRows, numCols, val=1, rowStart=0):
   return [[(val if i == j else 0) for j in range(numCols)]
               for i in range(rowStart, numRows)]


'''
   standardForm: [float], [[float]], [float], [[float]], [float], [[float]], [float] -> [float], [[float]], [float]
    Convertir un programme linéaire sous forme générale en forme standard pour le
    algorithme simplex. Les entrées sont supposées avoir les bonnes dimensions: coût
    est une liste de longueur n, GreaterThans est une matrice n par m, gtThreshold est un vecteur
    de longueur m, avec le même motif pour les entrées restantes. Non
    des erreurs de dimension sont détectées et nous supposons qu'il n'y a pas de variables sans restriction.
'''
def standardForm(cost, greaterThans=[], gtThreshold=[], lessThans=[], ltThreshold=[],
                equalities=[], eqThreshold=[], maximization=True):
   newVars = 0
   numRows = 0
   if gtThreshold != []:
      newVars += len(gtThreshold)
      numRows += len(gtThreshold)
   if ltThreshold != []:
      newVars += len(ltThreshold)
      numRows += len(ltThreshold)
   if eqThreshold != []:
      numRows += len(eqThreshold)

   if not maximization:
      cost = [-x for x in cost]

   if newVars == 0:
      return cost, equalities, eqThreshold

   newCost = list(cost) + [0] * newVars

   constraints = []
   threshold = []

   oldConstraints = [(greaterThans, gtThreshold, -1), (lessThans, ltThreshold, 1),
                     (equalities, eqThreshold, 0)]

   offset = 0
   for constraintList, oldThreshold, coefficient in oldConstraints:
      constraints += [c + r for c, r in zip(constraintList,
         identity(numRows, newVars, coefficient, offset))]

      threshold += oldThreshold
      offset += len(oldThreshold)

   return newCost, constraints, threshold


def dot(a,b):
   return sum(x*y for x,y in zip(a,b))

def column(A, j):
   return [row[j] for row in A]

def transpose(A):
   return [column(A, j) for j in range(len(A[0]))]

def isPivotCol(col):
   return (len([c for c in col if c == 0]) == len(col) - 1) and sum(col) == 1

def variableValueForPivotColumn(tableau, column):
   pivotRow = [i for (i, x) in enumerate(column) if x == 1][0]
   return tableau[pivotRow][-1]

# assume the last m columns of A are the slack variables; the initial basis is
# the set of slack variables
def initialTableau(c, A, b):
   tableau = [row[:] + [x] for row, x in zip(A, b)]
   tableau.append([ci for ci in c] + [0])
   return tableau


def primalSolution(tableau):
   # the pivot columns denote which variables are used
   columns = transpose(tableau)
   indices = [j for j, col in enumerate(columns[:-1]) if isPivotCol(col)]
   return [(colIndex, variableValueForPivotColumn(tableau, columns[colIndex]))
            for colIndex in indices]


def objectiveValue(tableau):
   return -(tableau[-1][-1])


def canImprove(tableau):
   lastRow = tableau[-1]
   return any(x > 0 for x in lastRow[:-1])


# this can be slightly faster
def moreThanOneMin(L):
   if len(L) <= 1:
      return False

   x,y = heapq.nsmallest(2, L, key=lambda x: x[1])
   return x == y


def findPivotIndex(tableau):
   # pick minimum positive index of the last row
   column_choices = [(i,x) for (i,x) in enumerate(tableau[-1][:-1]) if x > 0]
   column = min(column_choices, key=lambda a: a[1])[0]

   # check if unbounded
   if all(row[column] <= 0 for row in tableau):
      raise Exception('Linear program is unbounded.')

   # check for degeneracy: more than one minimizer of the quotient
   quotients = [(i, r[-1] / r[column])
      for i,r in enumerate(tableau[:-1]) if r[column] > 0]

   if moreThanOneMin(quotients):
      raise Exception('Linear program is degenerate.')

   # pick row index minimizing the quotient
   row = min(quotients, key=lambda x: x[1])[0]

   return row, column


def pivotAbout(tableau, pivot):
   i,j = pivot

   pivotDenom = tableau[i][j]
   tableau[i] = [x / pivotDenom for x in tableau[i]]

   for k,row in enumerate(tableau):
      if k != i:
         pivotRowMultiple = [y * tableau[k][j] for y in tableau[i]]
         tableau[k] = [x - y for x,y in zip(tableau[k], pivotRowMultiple)]


'''
   simplex: [float], [[float]], [float] -> [float], float
    Résolvez le programme linéaire de forme standard donné:
       max <c, x>
       s.t. Ax = b
            x> = 0
    fournissant la solution optimale x * et la valeur de la fonction objectif
'''
def solution_variable(nb_variable, liste_tuples):
    v = [(i,0) for i in range(nb_variable)]
    
    for i in range(nb_variable):
        for j in range(nb_variable):
            if liste_tuples[j][0] == v[i][0]:
                v[i] = liste_tuples[j]
                break
    return v

def simplex(c, A, b):
   nb_variable = len(c)
   slack_variables(c,A)
   tableau = initialTableau(c, A, b)
   #print("Initial tableau:")
   #for row in tableau:
      #print(row)
   #print()

   while canImprove(tableau):
      pivot = findPivotIndex(tableau)
      #print("Next pivot index is=%d,%d \n" % pivot)
      pivotAbout(tableau, pivot)
      #print("Tableau after pivot:")
      '''for row in tableau:
         print(row)
      print()'''
    
   primaSolution = primalSolution(tableau)
   print(primaSolution)

   return tableau, solution_variable(nb_variable, primaSolution), objectiveValue(tableau)
   #return tableau, primalSolution(tableau), objectiveValue(tableau) 


def index(request):
    return render(request, 'index.html', {})

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
        c = []
        for i in range(nb_variable):
            number = 'number' + str(i+1)
            c.append(int(request.POST.get(number)))

        # Contraintes
        A = []
        for i in range(nb_contraintes):
            tmp = []
            for j in range(nb_variable):
                number = 'contrainte' + str(i) + str(j)
                tmp.append(int(request.POST.get(number)))
            A.append(tmp)

        # Second Membre
        b = []
        
        k = 1
        for j in range(nb_variable+1, nb_variable + nb_contraintes + 1):
            number = 'second_membre' + str(k)
            b.append(int(request.POST.get(number)))
            k += 1
        
        t, s, z = simplex(c, A, b)
        print(s)
        print(z)
        dictio = {}
        for i in range(nb_variable):
            dictio[s[i][0] + 1] = s[i][1]

        context = {
            'dictio': dictio,
            'z': z,
        }
        
    return render(request, 'result.html', context)
