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
import datetime 
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
                    'paths':None          
                    }

        citibike['graph']=gr.newGraph(datastructure='ADJ_LIST',
                                        directed=True,
                                        size=1000,
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
    vertex = gr.vertices(citibike['graph']) #Número de vértices (estaciones) en Citibike
    iterator = it.newIterator(vertex)
    data = {'degree':None,     #Lugar donde se guardarán los datos obtenidos (Salidas, llegadas, totales)
            'indegree':None,
            'total': None} 
    data['degree']=om.newMap(omaptype='RBT',comparefunction=compareValues)
    data['indegree']=om.newMap(omaptype='RBT',comparefunction=compareValues)
    data['total']=om.newMap(omaptype='RBT',comparefunction=compareValues)   
    while it.hasNext(iterator):  #Se agrega la información a data
        station = it.next(iterator)
        vertexDegree=gr.outdegree(citibike['graph'],station) #Número de salidas
        updateDegreeIndex(data['degree'],vertexDegree,station)
        vertexIndegree=gr.indegree(citibike['graph'],station) #Número de llegadas
        updateIndegreeIndex(data['indegree'],vertexIndegree,station)
        totalVertex = vertexDegree+vertexIndegree #Total de salidas y llegadas
        updateTotalIndex(data['total'],totalVertex,station)

    lstExitMax = lt.newList("ARRAY_LIST") #Lugar donde se guardarán las estaciones de salida
    obtainValues(data,lstExitMax,'d')
    
    lstArriveMax = lt.newList("ARRAY_LIST") #Lugar donde se guardarán las estaciones de llegada
    obtainValues(data,lstArriveMax,'i')
    
    lstTotal = lt.newList("ARRAY_LIST") #Lugar donde se guardarán las estaciones menos usadas
    obtainValues(data,lstTotal,'t')
    
    pos = 1

    while pos < 4:   #Acá se actualizan los nombres de las estaciones
        changeInfo(citibike,lstExitMax,pos)
        changeInfo(citibike,lstArriveMax,pos)
        changeInfo(citibike,lstTotal,pos)
        pos +=1
    
    eM1,eM2,eM3 = lt.getElement(lstExitMax,1),lt.getElement(lstExitMax,2),lt.getElement(lstExitMax,3)
    aM1,aM2,aM3 = lt.getElement(lstArriveMax,1),lt.getElement(lstArriveMax,2),lt.getElement(lstArriveMax,3)
    tM1,tM2,tM3 = lt.getElement(lstTotal,1),lt.getElement(lstTotal,2),lt.getElement(lstTotal,3)

    return eM1,eM2,eM3,aM1,aM2,aM3,tM1,tM2,tM3
    


####################################################################


########## Requerimiento 5 - Grupal ##########
def routeRecomendations(citibike,ageRange):     
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

    return lstPath
##################################################


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

def obtainValues(data,lst,method):
    """
    Agrega los ID de las estaciones a su lista correspondiente
    """
    while lt.size(lst) < 3:
        if method == 'd':   #Estaciones de salida
            a = om.maxKey(data['degree'])
            r = om.get(data['degree'],om.maxKey(data['degree']))
            if r['key'] is not None:
                degreeMap=me.getValue(r)['degreeIndex']
                result = m.get(degreeMap,a)
                iterations = knowQuantity(result)
                if iterations == 0:
                    n = lt.getElement(me.getValue(result)['lstStations'],1)
                    om.deleteMax(data['degree'])
                    lt.addLast(lst,n)
                elif iterations == 1:
                    n = lt.getElement(me.getValue(result)['lstStations'],1)
                    k = lt.getElement(me.getValue(result)['lstStations'],2)
                    om.deleteMax(data['degree'])
                    lt.addLast(lst,n)
                    lt.addLast(lst,k)
                elif iterations == -1:
                    n = lt.getElement(me.getValue(result)['lstStations'],1)
                    k = lt.getElement(me.getValue(result)['lstStations'],2)
                    l = lt.getElement(me.getValue(result)['lstStations'],3)
                    lt.addLast(lst,n)
                    lt.addLast(lst,k)
                    lt.addLast(lst,l)
        elif method == 't': #Estaciones menos usadas
            a = om.minKey(data['total'])
            r = om.get(data['total'],om.minKey(data['total']))
            if r['key'] is not None:
                totalMap=me.getValue(r)['totalIndex']
                result = m.get(totalMap,a)
                iterations = knowQuantity(result)
                if iterations == 0:
                    n = lt.getElement(me.getValue(result)['lstStations'],1)
                    om.deleteMin(data['total'])
                    lt.addLast(lst,n)
                elif iterations == 1:
                    n = lt.getElement(me.getValue(result)['lstStations'],1)
                    k = lt.getElement(me.getValue(result)['lstStations'],2)
                    om.deleteMin(data['total'])
                    lt.addLast(lst,n)
                    lt.addLast(lst,k)
                elif iterations == -1:
                    n = lt.getElement(me.getValue(result)['lstStations'],1)
                    k = lt.getElement(me.getValue(result)['lstStations'],2)
                    l = lt.getElement(me.getValue(result)['lstStations'],3)
                    lt.addLast(lst,n)
                    lt.addLast(lst,k)
                    lt.addLast(lst,l)
        elif method == 'i': #Estaciones de llegada
            a = om.maxKey(data['indegree'])
            r = om.get(data['indegree'],om.maxKey(data['indegree']))
            if r['key'] is not None:
                inDegreeMap=me.getValue(r)['inDegreeIndex']
                result = m.get(inDegreeMap,a)
                iterations = knowQuantity(result)
                if iterations == 0:
                    n = lt.getElement(me.getValue(result)['lstStations'],1)
                    om.deleteMax(data['indegree'])
                    lt.addLast(lst,n)
                elif iterations == 1:
                    n = lt.getElement(me.getValue(result)['lstStations'],1)
                    k = lt.getElement(me.getValue(result)['lstStations'],2)
                    om.deleteMax(data['indegree'])
                    lt.addLast(lst,n)
                    lt.addLast(lst,k)
                elif iterations == -1:
                    n = lt.getElement(me.getValue(result)['lstStations'],1)
                    k = lt.getElement(me.getValue(result)['lstStations'],2)
                    l = lt.getElement(me.getValue(result)['lstStations'],3)
                    lt.addLast(lst,n)
                    lt.addLast(lst,k)
                    lt.addLast(lst,l)        
        

def knowQuantity(info):
    """
    Indica la operación que debe realizar la función obtainValues
    """
    result = lt.size(me.getValue(info)['lstStations'])
    if result == 1:
        return 0
    elif result == 2:
        return 1
    elif result >=3:
        return -1

def updateDegreeIndex(map,degree,station):
    entry = om.get(map,degree)
    if entry is None:
        degreeEntry = newDataEntry(station)
        om.put(map,degree,degreeEntry)
    else:
        degreeEntry=me.getValue(entry)
    addDegreeIndex(degreeEntry,degree,station)

def updateIndegreeIndex(map,inDegree,station):
    entry = om.get(map,inDegree)
    if entry is None:
        inDegreeEntry = newDataEntry2(station)
        om.put(map,inDegree,inDegreeEntry)
    else:
        inDegreeEntry=me.getValue(entry)
    addIndegreeIndex(inDegreeEntry,inDegree,station)

def updateTotalIndex(map,total,station):
    entry = om.get(map,total)
    if entry is None:
        totalEntry = newDataEntry3(station)
        om.put(map,total,totalEntry)
    else:
        totalEntry=me.getValue(entry)
    addTotalIndex(totalEntry,total,station)

def addDegreeIndex(degreeEntry,degree,station):
    lst = degreeEntry['lstDegree']
    lt.addLast(lst,station)
    degreeIndex = degreeEntry['degreeIndex']
    degreeValue = m.get(degreeIndex,degree)
    if degreeValue is None:
        entry = newDegreeEntry(degree,station)
        lt.addLast(entry['lstStations'],station)
        m.put(degreeIndex,degree,entry)
    else:
        entry = me.getValue(degreeValue)
        lt.addLast(entry['lstStations'],station)
    return degreeEntry

def addIndegreeIndex(inDegreeEntry,inDegree,station):
    lst = inDegreeEntry['lstIndegree']
    lt.addLast(lst,station)
    inDegreeIndex = inDegreeEntry['inDegreeIndex']
    inDegreeValue = m.get(inDegreeIndex,inDegree)
    if inDegreeValue is None:
        entry = newIndegreeEntry(inDegree,station)
        lt.addLast(entry['lstStations'],station)
        m.put(inDegreeIndex,inDegree,entry)
    else:
        entry = me.getValue(inDegreeValue)
        lt.addLast(entry['lstStations'],station)
    return inDegreeEntry

def addTotalIndex(totalEntry,total,station):
    lst = totalEntry['lstTotal']
    lt.addLast(lst,station)
    totalIndex = totalEntry['totalIndex']
    totalValue = m.get(totalIndex,total)
    if totalValue is None:
        entry = newTotalEntry(total,station)
        lt.addLast(entry['lstStations'],station)
        m.put(totalIndex,total,entry)
    else:
        entry = me.getValue(totalValue)
        lt.addLast(entry['lstStations'],station)
    return totalEntry

def newDataEntry(value):
    entry = {'degreeIndex':None,'lstDegree':None}
    entry['degreeIndex']=m.newMap(numelements=3,
                                    maptype='PROBING',
                                    comparefunction=compareValuesD)
    entry['lstDegree']=lt.newList('ARRAY_LIST',compareStations)
    return entry

def newDataEntry2(value):
    entry = {'inDegreeIndex':None,'lstIndegree':None}
    entry['inDegreeIndex']=m.newMap(numelements=3,
                                    maptype='PROBING',
                                    comparefunction=compareValuesD)
    entry['lstIndegree']=lt.newList('ARRAY_LIST',compareStations)
    return entry

def newDataEntry3(value):
    entry = {'totalIndex':None,'lstTotal':None}
    entry['totalIndex']=m.newMap(numelements=3,
                                    maptype='PROBING',
                                    comparefunction=compareValuesD)
    entry['lstTotal']=lt.newList('ARRAY_LIST',compareStations)
    return entry

def newDegreeEntry(degree, station):
    degreeEntry = {'degree':None, 'lstStations':None,}
    degreeEntry['degree']=degree
    degreeEntry['lstStations']=lt.newList('ARRAY_LIST',compareStations)    
    return degreeEntry

def newIndegreeEntry(indegree, station):
    inDegreeEntry = {'indegree':None, 'lstStations':None,}
    inDegreeEntry['indegree']=indegree
    inDegreeEntry['lstStations']=lt.newList('ARRAY_LIST',compareStations)    
    return inDegreeEntry

def newTotalEntry(total, station):
    totalEntry = {'total':None, 'lstStations':None,}
    totalEntry['indegree']=total
    totalEntry['lstStations']=lt.newList('ARRAY_LIST',compareStations)    
    return totalEntry

def findStationsInRange(citibike,ageRange,lst1,lst2):
    """
    Añade a las listas pasadas por parámetro las estaciones que se encuentren dentro del rango ingresado
    """
    
    iterator = it.newIterator(citibike['stations'])  #Lugar donde se encuentra la información de todas las estaicones
    if ageRange[0] == "0":
        initRange = int(ageRange[0])
        finalRange = int(ageRange[2]+ageRange[3])
    elif ageRange == "60+" or ageRange=="60 +":
        initRange = 60
        finalRange = year - 1870
    else: 
        initRange = int(ageRange[0]+ageRange[1])
        finalRange = int(ageRange[3]+ageRange[4])
    while it.hasNext(iterator):
        info = it.next(iterator)
        ocurredDate = info['starttime']
        year=int(ocurredDate[:4])
        birthYear = int(info['birth year'])
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
