"""
 * Copyright 2020, Departamento de sistemas y Computación
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * Contribución de:
 *
 * Dario Correal
 *
 """


import sys
import config
from App import controller
from DISClib.ADT import stack
from DISClib.ADT import list as lt
import timeit
assert config

"""
La vista se encarga de la interacción con el usuario.
Presenta el menu de opciones  y  por cada seleccion
hace la solicitud al controlador para ejecutar la
operación seleccionada.
"""

# ___________________________________________________
#  Variables
# ___________________________________________________
servicefile = ''
initialStation = None
recursionLimit = 20000

# ___________________________________________________
#  Menu principal
# ___________________________________________________

def printMenu():
    print("\n")
    print("************************************************")
    print("BIENVENIDO")
    print("1- Inicializar analizador.")
    print("2- Cargar información de bicicletas.")
    print("3- Conocer cantidad de cluster de viajes.")
    print("4- Conocer rutas turísticas circulares.")
    print("5- Conocer las estaciones críticas.")
    print("6- Conocer ruta turística por resistencia.")
    print("7- Recomendador de rutas por rango de edad.")
    print("8- Rutas de interés turístico.")
    print("9- Indicación de estaciones para publicidad.")
    print("10- Conocer las bicicletas para mantenimiento")
    print("0- SALIR")
    print("************************************************")



def optionTwo():
    print("\nCargando información de uso de bicicletas...")
    controller.loadTrips(cont)
    numedges = controller.totalConnections(cont)
    numvertex = controller.totalStops(cont)
    size= controller.SizeStations(cont)
    print('Numero de vertices: ' + str(numvertex))
    print('Numero de arcos: ' + str(numedges))
    print('Viajes cargados: '+ str(size))
    print('El limite de recursion actual: ' + str(sys.getrecursionlimit()))
    sys.setrecursionlimit(recursionLimit)
    print('El limite de recursion se ajusta a: ' + str(recursionLimit))


def optionThree():
    s1=input("Ingrese la estación inicial: ")
    s2=input("Ingrese la estación final: ")
    msg = ''
    print('La cantidad de clusters de viajes es: ' +
          str(controller.connectedComponents(cont['graph'])))
    result = controller.sameCC(cont['graph'],s1,s2)
    if result:
        msg = ' se encuentran en el mismo cluster.'
    else:
        msg = ' no se encuentran en el mismo cluster'

    print("Las estaciones "+s1+ " y " + s2 + msg)
    return -1


'''def optionFour():
    controller.minimumCostPaths(cont, initialStation)
    return -1
'''

def optionFive():
    result = controller.topStations(cont)
    eM1,eM2,eM3=result[0],result[1],result[2]
    aM1,aM2,aM3=result[3],result[4],result[5]
    tM1,tM2,tM3=result[6],result[7],result[8]
    print("======== Top 3 de salida ========")
    print("1. "+"\t"+str(eM1))
    print("2. "+"\t"+str(eM2))
    print("3. "+"\t"+str(eM3))
    print("=================================")
    print("======== Top 3 de llegada ========")
    print("1. "+"\t"+str(aM1))
    print("2. "+"\t"+str(aM2))
    print("3. "+"\t"+str(aM3))
    print("=================================")
    print("======== Tres estaciones menos utilizadas ========")
    print("1. "+"\t"+str(tM1))
    print("2. "+"\t"+str(tM2))
    print("3. "+"\t"+str(tM3))
    print("=================================")


'''def optionSix():
    path = controller.minimumCostPath(cont, destStation)
    if path is not None:
        pathlen = stack.size(path)
        print('El camino es de longitud: ' + str(pathlen))
        while (not stack.isEmpty(path)):
            stop = stack.pop(path)
            print(stop)
    else:
        print('No hay camino')
    return -1
'''

def optionSeven():
    ageRange = input("Ingrese el rango de edad (0-10, 11-20, 21-30, 31-40, 41-50, 51-60, 60+): ")
    ret = controller.routeRecomendations(cont,ageRange)
    if ret == -1:
        print("No hay rutas para ese rango de edad.")
    else:
        iStation = lt.getElement(ret,1)
        fStation = lt.getElement(ret,2)
        result = lt.getElement(ret,3)
        if lt.size(result) == 0:
            print("==================================")
            print("Estación inicial: " + iStation)
            print("\nEstación final: " + fStation)
            print("No camino entre "+iStation +" y "+fStation)
            print("==================================")
            
        else:
            initStation = lt.getElement(result,1)
            finalStation = lt.getElement(result,lt.size(result))
            print("==================================")
            print("Estación inicial: " + initStation)
            print("\nEstaciones intermedias: ")
            if lt.size(result) == 2:
                print("- No hay estaciones intermedias")
            else:
                for i in range(2,lt.size(result)):
                    print("\n- " + lt.getElement(result,i))
            
            print("\nEstación final: " + finalStation)
            print("==================================")
            
    return -1



'''def optionEight():
    maxvert, maxdeg = controller.servedRoutes(cont)
    print('Estación: ' + maxvert + '  Total rutas servidas: '
          + str(maxdeg))

    return -1
'''

'''def optionNine():
    maxvert, maxdeg = controller.servedRoutes(cont)
    print('Estación: ' + maxvert + '  Total rutas servidas: '
          + str(maxdeg))

    return -1
'''

def optionTen():
    """ id = input("Ingrese el ID a consultar: ")
    date = input('Ingrese la fecha a consultar: ') """
    controller.bikeMaintenance(cont,'31956','2018-01-21')
    
    return -1


"""
Menu principal
"""

while True:
    printMenu()
    opcion = input('Seleccione una opción para continuar: ')

    if int(len(opcion)==1) and int(opcion[0])==1:
        print("\nInicializando...")

        cont = controller.init()

    elif int(opcion[0])==2:

        #OJO CON TIEMPO DE EJECUCION#
        tiempoEjecución = timeit.timeit(optionTwo, number=1)
        print("El tiempo de ejecución de la función fue: " + str(tiempoEjecución)+ ' segundos')

    elif int(opcion[0])==3:

        #OJO CON TIEMPO DE EJECUCION#
        tiempoEjecución = timeit.timeit(optionThree, number=1)
        print("El tiempo de ejecución de la función fue: " + str(tiempoEjecución))
    
    elif int(opcion[0])==4:

        #OJO CON TIEMPO DE EJECUCION#
        tiempoEjecución = timeit.timeit(optionFour, number=1)
        print("El tiempo de ejecución de la función fue: " + str(tiempoEjecución))

    elif int(opcion[0])==5:

        #OJO CON TIEMPO DE EJECUCION#
        tiempoEjecución = timeit.timeit(optionFive, number=1)
        print("El tiempo de ejecución de la función fue: " + str(tiempoEjecución))

    elif int(opcion[0])==6:

        #OJO CON TIEMPO DE EJECUCION#
        tiempoEjecución = timeit.timeit(optionSix, number=1)
        print("El tiempo de ejecución de la función fue: " + str(tiempoEjecución))

    elif int(opcion[0])==7:

        #OJO CON TIEMPO DE EJECUCION#
        tiempoEjecución = timeit.timeit(optionSeven, number=1)
        print("El tiempo de ejecución de la función fue: " + str(tiempoEjecución))

    elif int(opcion[0])==8:

        #OJO CON TIEMPO DE EJECUCION#
        tiempoEjecución = timeit.timeit(optionEight, number=1)
        print("El tiempo de ejecución de la función fue: " + str(tiempoEjecución))

    elif int(opcion[0])==9:

        #OJO CON TIEMPO DE EJECUCION#
        tiempoEjecución = timeit.timeit(optionNine, number=1)
        print("El tiempo de ejecución de la función fue: " + str(tiempoEjecución))

    elif int(opcion[0])==1 and int(opcion[1])==0:

        #OJO CON TIEMPO DE EJECUCION#
        tiempoEjecución = timeit.timeit(optionTen, number=1)
        print("El tiempo de ejecución de la función fue: " + str(tiempoEjecución))

    else: 
        sys.exit(0)
sys.exit(0)
        