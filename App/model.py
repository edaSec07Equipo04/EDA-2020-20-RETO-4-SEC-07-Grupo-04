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
import config
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.ADT import list as lt
from DISClib.DataStructures import listiterator as it
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Utils import error as error
from DISClib.DataStructures import edge as e
from DISClib.ADT import orderedmap as om
from DISClib.ADT import stack
from DISClib.DataStructures import mapentry as me
from math import radians, cos, sin, asin, sqrt
import datetime 
import time
assert config

"""
En este archivo definimos los TADs que vamos a usar y las operaciones
de creacion y consulta sobre las estructuras de datos.
"""

# -----------------------------------------------------
#                       API
# -----------------------------------------------------

# Funciones para agregar informacion al grafo
def newAnalyzer():
    try:
        citibike = {
                    'graph': None,
                    'stations': None,
                    'exitStations':None,
                    'arriveStations':None,
                    'totalStations':None,   
                    'paths':None          
                    }

        citibike['graph']=gr.newGraph(datastructure='ADJ_LIST',
                                        directed=True,
                                        size=1000,
                                        comparefunction=compareStations)
        citibike['exitStations']=m.newMap(1019,
                                        maptype='PROBING',
                                        loadfactor=0.5,
                                        comparefunction=compareStations)
        citibike['arriveStations']=m.newMap(1019,
                                        maptype='PROBING',
                                        loadfactor=0.5,
                                        comparefunction=compareStations)
        citibike['totalStations']=m.newMap(1019,
                                        maptype='PROBING',
                                        loadfactor=0.5,
                                        comparefunction=compareStations)                                  
        citibike['stations']=lt.newList('ARRAY_LIST', compareStations)
        return citibike

    except Exception as exp:
        error.reraise(exp,'model:newAnalyzer')

def addTrip(citibike, trip):
    """
    """
    lst=citibike['stations']
    origin = trip['start station id']
    destination = trip['end station id']
    duration = int(trip['tripduration'])
    addStation(citibike,origin)
    addStation(citibike,destination)
    addExitStation(citibike,origin)
    addArriveStation(citibike,destination)
    addTotalStation(citibike,origin)
    addTotalStation(citibike,destination)
    addConnection(citibike,origin,destination,duration)
    lt.addLast(lst,trip)


def addStation(citibike,stationId):
    """
    Adiciona una estación como un vértice del grafo
    """
    if not gr.containsVertex(citibike['graph'],stationId):
        gr.insertVertex(citibike['graph'],stationId)
    return citibike

def addConnection(citibike,origin,destination,duration):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(citibike['graph'],origin,destination)
    if edge is None:
        gr.addEdge(citibike['graph'],origin,destination,duration)
    else:
        e.updateAverageWeight(edge,duration)
    return citibike

def newExitStation(station):
    """
    Crea una nueva estructura para modelar los viajes de una estación
    """
    exitStation = {'name': '', 'trips':0}
    exitStation['name'] = station
    return exitStation

def addExitStation(citibike,station):
    """
    Crea una nueva estructura para modelar los viajes de una estación
    """
    exitStations = citibike['exitStations']
    existStation = m.contains(exitStations,station)
    if existStation:
        entry = m.get(exitStations,station)
        data = me.getValue(entry)
    else:
        data = newExitStation(station)
        m.put(exitStations,station,data)
    data['trips'] +=1

def newArriveStation(station):
    """
    Crea una nueva estructura para modelar los viajes de una estación
    """
    arriveStation = {'name': '', 'trips':0}
    arriveStation['name'] = station
    return arriveStation

def addArriveStation(citibike,station):
    """
    Crea una nueva estructura para modelar los viajes de una estación
    """
    arriveStations = citibike['arriveStations']
    existStation = m.contains(arriveStations,station)
    if existStation:
        entry = m.get(arriveStations,station)
        data = me.getValue(entry)
    else:
        data = newArriveStation(station)
        m.put(arriveStations,station,data)
    data['trips'] +=1

def newTotalStation(station):
    """
    Crea una nueva estructura para modelar los viajes de una estación
    """
    totalStation = {'name': '', 'trips':0}
    totalStation['name'] = station
    return totalStation

def addTotalStation(citibike,station):
    """
    Crea una nueva estructura para modelar los viajes de una estación
    """
    totalStations = citibike['totalStations']
    existStation = m.contains(totalStations,station)
    if existStation:
        entry = m.get(totalStations,station)
        data = me.getValue(entry)
    else:
        data = newTotalStation(station)
        m.put(totalStations,station,data)
    data['trips'] +=1
# ==============================
# Funciones de consulta
# ==============================

def totalStops(citibike):
    """
    Retorna el total de estaciones (vertices) del grafo
    """
    return gr.numVertices(citibike['graph'])


def totalConnections(citibike):
    """
    Retorna el total arcos del grafo
    """
    return gr.numEdges(citibike['graph'])


########## REQUERIMIENTO 3 - Germán Rojas #############
def topStations(citibike):
    """
    Da la información de:
    - Top 3 estaciones de llegada
    - Top 3 estaciones de salida
    - Top 3 estaciones menos utilizadas
    """
    lstExit = lt.newList("ARRAY_LIST")
    lstArrive = lt.newList("ARRAY_LIST")
    lstTotal = lt.newList("ARRAY_LIST")
    count = 0
    while count < 3:
        obtainValues(citibike,lstExit,'e')
        obtainValues(citibike,lstArrive,'a')
        obtainValues(citibike,lstTotal,'t')
        count += 1
    pos = 1
    while pos < 4:
        changeInfo(citibike,lstExit,pos)
        changeInfo(citibike,lstArrive,pos)
        changeInfo(citibike,lstTotal,pos)
        pos+=1
    eM1 = lt.getElement(lstExit,1)
    eM2 = lt.getElement(lstExit,2)
    eM3 = lt.getElement(lstExit,3)
    aM1 = lt.getElement(lstArrive,1)
    aM2 = lt.getElement(lstArrive,2)
    aM3 = lt.getElement(lstArrive,3)
    tM1 = lt.getElement(lstTotal,1)
    tM2 = lt.getElement(lstTotal,2)
    tM3 = lt.getElement(lstTotal,3)

    return eM1,eM2,eM3,aM1,aM2,aM3,tM1,tM2,tM3
        

####################################################################


########## Requerimiento 5 - Grupal ##########
def routeRecomendations(citibike,ageRange):
    """
    Informa la estación desde la cual las personas en el rango ingresado inician más viajes. 
    La estación donde terminan más viajes personas en rango y el camino mas corto en tiempo entre dicho par de estaciones.
    """     
    lstExit = lt.newList("ARRAY_LIST",compareValues)
    lstArrive = lt.newList("ARRAY_LIST",compareValues)
    findStationsInRange(citibike,ageRange,lstExit,lstArrive)
    if lt.size(lstExit) == 0 or lt.size(lstArrive) == 0:
        return -1
    data = {'degree':None, #Lugar donde se guardan los datos obtenidos
            'indegree':None}
    data['degree']=om.newMap(omaptype='RBT',comparefunction=compareValues)
    data['indegree'] = om.newMap(omaptype='RBT',comparefunction=compareValues)
    itExit = it.newIterator(lstExit)
    itArrive = it.newIterator(lstArrive)
    while it.hasNext(itExit):
        station = it.next(itExit)
        vertexDegree = gr.outdegree(citibike['graph'],station)
        updateDegreeIndex(data['degree'],vertexDegree,station)
    while it.hasNext(itArrive):
        station = it.next(itArrive)
        vertexIndegree = gr.indegree(citibike['graph'],station)
        updateIndegreeIndex(data['indegree'],vertexIndegree,station)
    
    lstExitMax = lt.newList("ARRAY_LIST")
    obtainValues(data,lstExitMax,'d')

    lstArriveMax = lt.newList("ARRAY_LIST")
    obtainValues(data,lstArriveMax,'i')
    
    initStation = lt.getElement(lstExitMax,1)
    finalStation = lt.getElement(lstArriveMax,1)

    minimumCostPaths(citibike,initStation)
    path = minimumCostPath(citibike,finalStation)

    lstPath = lt.newList("ARRAY_LIST",compareValues)
    if path is not None:
        while (not stack.isEmpty(path)):
            stop = stack.pop(path)
            if lt.isPresent(lstPath,stop['vertexA']) == 0:
                lt.addLast(lstPath,stop['vertexA'])
            else:
                pass
            if lt.isPresent(lstPath,stop['vertexB']) == 0:
                lt.addLast(lstPath,stop['vertexB'])
            else:
                pass
    else:
        pass
    
    pos = 1
    while pos < (lt.size(lstPath)+1):
        changeInfo(citibike,lstPath,pos)
        pos += 1
    lstReturn = lt.newList("ARRAY_LIST")
    lt.addLast(lstReturn,initStation)
    lt.addLast(lstReturn,finalStation)
    lt.addLast(lstReturn,lstPath)
    return lstReturn
##################################################

########## Requerimiento 6 - Grupal ##########
def interestingRoutes(citibike,lat1,lon1,lat2,lon2):
    iterator = it.newIterator(citibike['stations'])
    startDistance = 1000000
    startStationId = ''
    endDistance = 1000000
    endStationId = ''
    while it.hasNext(iterator):
        station = it.next(iterator)
        startStationLatitude = float(station['start station latitude'])
        startStationLongitude = float(station['start station longitude'])
        endStationLatitude = float(station['end station latitude'])
        endStationLongitude = float(station['end station longitude'])
        startDistanceResult = distance(lat1,startStationLatitude,lon1,startStationLongitude)
        if startDistanceResult < startDistance:
            startDistance = startDistanceResult
            startStationId = station['start station id']
        endDistanceResult = distance(lat2,endStationLatitude,lon2,endStationLongitude)
        if endDistanceResult < endDistance:
            endDistance = endDistanceResult
            endStationId = station['end station id']
    minimumCostPaths(citibike,startStationId)
    path = minimumCostPath(citibike,endStationId)
    lstPath = lt.newList("ARRAY_LIST",compareValues)
    time = 0
    if path is not None:
        while (not stack.isEmpty(path)):
            stop = stack.pop(path)
            time += stop['weight']
            if lt.isPresent(lstPath,stop['vertexA']) == 0:
                lt.addLast(lstPath,stop['vertexA'])
            else:
                pass
            if lt.isPresent(lstPath,stop['vertexB']) == 0:
                lt.addLast(lstPath,stop['vertexB'])
            else:
                pass
    else:
        pass
    pos = 1
    while pos < (lt.size(lstPath)+1):
        changeInfo(citibike,lstPath,pos)
        pos += 1
    startStation = lt.getElement(lstPath,1)
    endStation = lt.getElement(lstPath,lt.size(lstPath))
    return startStation,endStation,time,lstPath



##################################################
######## Requerimiento 8 - Bono ###########
def bikeMaintenance(citibike,bikeId,date):
    """
    Dado un identificador de bicicleta y una fecha específica, retorna el recorrido realizado. 
    Esto es, todas las estaciones por las que ha pasado, indicando el tiempo total de uso y el tiempo total estacionada.
    """ 
    lstResults=lt.newList("ARRAY_LIST") #Estaciones con sus datos completos (bikeid, stoptime, starttime, etc.)
    lstStations = lt.newList("ARRAY_LIST",compareValues) #Nombres de las estaciones por las cuales circuló
    stationsInDate(citibike,bikeId,date,lstResults,lstStations)
    usageTimeResult = usageTime(lstResults)
    timeStopped = 86400-usageTimeResult
    return lstStations,usageTimeResult,timeStopped
##############################################################    


def numSCC(graph):
    """
    Informa cuántos componentes fuertemente conectados se encontraron
    """
    sc = scc.KosarajuSCC(graph)
    return scc.connectedComponents(sc)

def sameCC(graph,station1,station2):
    """
    Informa si dos estaciones están en el mismo componente conectado.
    """
    sc = scc.KosarajuSCC(graph)
    return scc.stronglyConnected(sc,station1,station2)

def stationsSize(graph):
    return lt.size(graph['stations'])

# ==============================
# Funciones Helper
# ==============================
def obtainValues(citibike,lst,method):
    """
    Agrega los ID de las estaciones a su lista correspondiente
    """
    if method == 'e':
        exitValues = m.valueSet(citibike['exitStations'])
        stationId = ''
        value = 0
        iterator = it.newIterator(exitValues)
        while it.hasNext(iterator):
            info = it.next(iterator)
            if info['trips'] > value:
                value = info['trips']
                stationId = info['name']
        m.remove(citibike['exitStations'],stationId)
        lt.addLast(lst,stationId)
    elif method == 'a':
        arriveValues = m.valueSet(citibike['arriveStations'])
        stationId = ''
        value = 0
        iterator = it.newIterator(arriveValues)
        while it.hasNext(iterator):
            info = it.next(iterator)
            if info['trips'] > value:
                value = info['trips']
                stationId = info['name']
        m.remove(citibike['arriveStations'],stationId)
        lt.addLast(lst,stationId)
    elif method == 't':
        totalValues = m.valueSet(citibike['totalStations'])
        stationId = ''
        value = 1000000
        iterator = it.newIterator(totalValues)
        while it.hasNext(iterator):
            info = it.next(iterator)
            if info['trips'] < value:
                value = info['trips']
                stationId = info['name']
        m.remove(citibike['totalStations'],stationId)
        lt.addLast(lst,stationId)
def distance(lat1,lat2,lon1,lon2):
    """
    Calcula la distancia entre dos puntos
    """
    lon1 = radians(lon1) 
    lon2 = radians(lon2) 
    lat1 = radians(lat1) 
    lat2 = radians(lat2)
    dlon = lon2 - lon1  
    dlat = lat2 - lat1 
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return(c * r) 

def usageTime(lstResults):
    """
    Calcula el tiempo de uso de una bicicleta
    """
    iterator=it.newIterator(lstResults)
    result = 0
    while it.hasNext(iterator):
        info=it.next(iterator)
        if lt.size(lstResults) == 1:
            result = int(info['tripduration'])
            return result
        else:           
            r = int(info['tripduration'])
            result += r
    return result

def stationsInDate(citibike,bikeId,date,lst,lst2):
    """
    Identifica las estaciones por las cuales la bicibleta circuló en la fecha indicada.
    """           
    iterator = it.newIterator(citibike['stations'])
    while it.hasNext(iterator):
        info = it.next(iterator)
        ocurredInitDate = info['starttime']
        ocurredInitDate = ocurredInitDate[:19]
        tripInitDate = datetime.datetime.strptime(ocurredInitDate, '%Y-%m-%d %H:%M:%S')
        if tripInitDate.date() == date and info['bikeid'] == bikeId:
            lt.addLast(lst,info)
            if lt.isPresent(lst2,info['start station name']) == 0:
                lt.addLast(lst2,info['start station name'])
            if lt.isPresent(lst2,info['end station name']) == 0:
                lt.addLast(lst2,info['end station name'])


def convertSecondsToDate(seconds):
    """
    Transforma segundos a días, horas, minutos y segundos.
    """
    days = seconds//(24*60*60)
    seconds = seconds % (24*60*60)
    hours = seconds // (60*60)
    seconds = seconds %(60*60)
    minutes = seconds // 60 
    seconds = seconds % 60
    print('Días: {} - Horas: {} - Minutos: {} - Segundos: {}'.format(int(days),int(hours),int(minutes),int(seconds)))

def printListContent(lst):
    """
    Imprime el contenido de una lista
    """
    iterator = it.newIterator(lst)
    while it.hasNext(iterator):
        print("- " + it.next(iterator))

def minimumCostPaths(citibike,station):
    """
    Calcula los caminos de costo mínimo desde la estación
    a todos los demas vertices del grafo
    """
    citibike['paths'] = djk.Dijkstra(citibike['graph'],station)
    return citibike

def minimumCostPath(citibike,station):
    """
    Retorna el camino de costo mínimo entre la estacion de inicio
    y la estacion destino
    Se debe ejecutar primero la funcion minimumCostPaths
    """
    path = djk.pathTo(citibike['paths'],station)
    return path

def changeInfo(citibike,lst,pos):
    """
    Intercambia el ID de la estación por su nombre correspondiente
    """
    lstCitibike = citibike['stations']
    iterator = it.newIterator(lstCitibike)
    stationId = lt.getElement(lst,pos)
    while it.hasNext(iterator):
            info = it.next(iterator)
            startStation = info['start station id']
            endStation = info['end station id']
            if stationId == startStation:
                stationId = info['start station name']
                lt.changeInfo(lst,pos,stationId)
                break
            elif stationId == endStation:           
                stationId = info['end station name']
                lt.changeInfo(lst,pos,stationId)
                break    


            
        
def findStationsInRange(citibike,ageRange,lst1,lst2):
    """
    Añade a las listas pasadas por parámetro las estaciones que se encuentren dentro del rango ingresado
    """
    
    iterator = it.newIterator(citibike['stations'])  #Lugar donde se encuentra la información de todas las estaicones
    while it.hasNext(iterator):
        info = it.next(iterator)
        ocurredDate = info['starttime']
        year=int(ocurredDate[:4])
        birthYear = int(info['birth year'])
        if ageRange[0] == "0":
            initRange = int(ageRange[0])
            finalRange = int(ageRange[2]+ageRange[3])
        elif ageRange == "60+" or ageRange=="60 +":
            initRange = 60
            finalRange = 120
        else: 
            initRange = int(ageRange[0]+ageRange[1])
            finalRange = int(ageRange[3]+ageRange[4])
        if year - birthYear >= initRange and year - birthYear <= finalRange:
            start = info['start station id']
            end = info['end station id']
            p1 = lt.isPresent(lst1,start)
            p2 = lt.isPresent(lst2,end)
            if p1 == 0:
                lt.addLast(lst1,start)  #Se añade a la lista de salidas
            else:
                pass
            if p2 == 0:
                lt.addLast(lst2,end) #Se añade a la lista de llegadas
            else:
                pass
# ==============================
# Funciones de Comparacion
# ==============================

def compareStations(station, keyvaluestation):
    """
    Compara dos estaciones
    """
    stationId = keyvaluestation['key']
    if (station == stationId):
        return 0
    elif (station > stationId):
        return 1
    else:
        return -1

def compareValues(v1,v2):
    if v1 == v2:
        return 0
    elif v1 > v2:
        return 1
    else:
        return -1

def compareValuesD(v1,v):
    v2 = v['key']
    if v1 == v2:
        return 0
    elif v1 > v2:
        return 1
    else:
        return -1

