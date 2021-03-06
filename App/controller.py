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

import config as cf
from App import model
import datetime
import csv
import os 

"""
El controlador se encarga de mediar entre la vista y el modelo.
Existen algunas operaciones en las que se necesita invocar
el modelo varias veces o integrar varias de las respuestas
del modelo en una sola respuesta.  Esta responsabilidad
recae sobre el controlador.
"""

# ___________________________________________________
#  Inicializacion del catalogo
# ___________________________________________________

def init():

    analyzer = model.newAnalyzer()
    return analyzer

# ___________________________________________________
#  Funciones para la carga de datos y almacenamiento
#  de datos en los modelos
# ___________________________________________________

def loadTrips(citibike):
    for filename in os.listdir(cf.data_dir):
        if filename.endswith('.csv'):
            print('Cargando archivo: ' + filename)
            loadFile(citibike, filename)
    return citibike

def loadFile(citibike, tripfile):
    """
    """
    tripfile = cf.data_dir + tripfile
    input_file = csv.DictReader(open(tripfile, encoding="utf-8"),
                                delimiter=",")
    for trip in input_file:
        model.addTrip(citibike, trip)
        
    return citibike






# ___________________________________________________
#  Funciones para consultas
# ___________________________________________________

def totalConnections(citibike):
    return model.totalConnections(citibike)

def totalStops(citibike):
    return model.totalStops(citibike)

def connectedComponents(citibike):
    return model.numSCC(citibike)

def sameCC(citibike,station1,station2):
    return model.sameCC(citibike,station1,station2)

def SizeStations(graph):
    return model.stationsSize(graph)

def topStations(citibike):
    """
    Da la información de:
    - Top 3 estaciones de llegada
    - Top 3 estaciones de salida
    - Top 3 estaciones menos utilizadas
    """
    return model.topStations(citibike)

# Req 02
def req2(citibike,initial_time, final_time, initial_vertex):
    return model.req2(citibike,initial_time, final_time, initial_vertex)


##Req 04##
def resitencia(citibike,idstation,time_max ):
    return model.stationsbyres(citibike,idstation,time_max )



def routeRecomendations(citibike,ageRange):
    """
    Informa la estación desde la cual las personas en el rango ingresado inician más viajes.
    La estación donde terminan más viajes personas en rango y el camino mas corto en tiempo entre dicho par de estaciones.
    """
    return model.routeRecomendations(citibike,ageRange)

def bikeMaintenance(citibike,bikeId,date):
    """
    Dado un identificador de bicicleta y una fecha específica, retorna el recorrido realizado.
    Esto es, todas las estaciones por las que ha pasado, indicando el tiempo total de uso y el tiempo total estacionada.
    """
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    return model.bikeMaintenance(citibike,bikeId,date.date())

def interestingRoutes(citibike,lat1,lon1,lat2,lon2):
    return model.interestingRoutes(citibike,lat1,lon1,lat2,lon2)

def convertSecondsToDate(seconds):
    """
    Transforma segundos a días, horas, minutos y segundos.
    """
    return model.convertSecondsToDate(seconds)

def printListContent(lst):
    """
    Imprime el contenido de una lista
    """
    return model.printListContent(lst)
