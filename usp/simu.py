import os, sys
import optparse
import subprocess
import random
import math
import numpy as np
import pandas as pd


# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append("/home/gustavo/Downloads/sumo-1.3.1/tools")
    from sumolib import checkBinary
except ImportError:
    sys.exit("please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")       
import traci

#functions to calculate the distance between 2 cars

global car_matrix


def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options


def separation(vector):     #its a function that separates the cars between vector of contaminated cars and non-contaminated
    i = 0
    j = 0
    non_contaminated_vector=[]
    contaminated_vector=[]
    for i in traci.vehicle.getIDList(): #if there are any cars who were not in the simulation, they're added into the non-contaminated vector and set their colors at green
        if i not in vector:
            non_contaminated_vector.append(i)
    for i in vector:
        if traci.vehicle.getColor(i) == (255,0,0,255): #if there are any red cars not yet in the contaminated vector they're added into it
            if i not in contaminated_vector:
                    contaminated_vector.append(i)
        else:                                           #if there are any cars who are not red and it's not already in the non-contaminated vector adds then into the non-contaminated vector
            if i not in non_contaminated_vector:
                non_contaminated_vector.append(i)
    car_matrix = 0
    car_matrix = [non_contaminated_vector,contaminated_vector]
    return car_matrix

def pos_x(x):
    pos_x = traci.vehicle.getPosition(x)[0]
    return pos_x

def pos_y(x):
    pos_y = traci.vehicle.getPosition(x)[1]
    return pos_y

def contamination(indexes,data_car,car_matrix): #pass on the contaminated colors to the non-contaminated cars
    for i in indexes:
        if (data_car['tc'][int(i)] == 2):
            traci.vehicle.setColor(str(i),(255,0,0,255))
        else:
            data_car['tc'][int(i)] = data_car['tc'][int(i)] + 1 



# contains TraCI control loop
def run():
    step = 0
    non_contaminated_vector = []
    contaminated_vector = []
    car_matrix_actualized =[]
    car_matrix_last=[]
    data_car = pd.DataFrame()
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1  
        if step > 6 and step < 12:  #it gives some time for the cars to enter the simulation
            car_matrix_actualized = traci.vehicle.getIDList()
            j = 0
            i = 0
            k = 0
            all_cars = []
            all_cars = (traci.vehicle.getIDList())
            for i in car_matrix_actualized:
                if i not in car_matrix_last:
                    x,y = traci.vehicle.getPosition(i)
                    dic_add = {"id":str(i),
                    "tc":0}
                    data_car = data_car.append(dic_add, ignore_index=True) 
            traci.vehicle.setColor(all_cars[1],(255,0,0,255)) #the second car is the red one
            car_matrix = separation(all_cars)
            car_matrix_last = car_matrix_actualized
        if step >= 12:      #starts the contamination
            car_matrix_actualized = traci.vehicle.getIDList()   #gets the cars who are in the simulation in the new step
            for i in car_matrix_actualized:
                if i not in car_matrix_last:
                    x,y = traci.vehicle.getPosition(i)
                    dic_add = {"id":str(i),
                    "tc":0}
                    data_car = data_car.append(dic_add, ignore_index=True) 
            for i in car_matrix[0][:]:   #removing cars who got out, even though there is no car who gets out muahahahaha
                if i not in car_matrix_actualized:
                    car_matrix[0].remove(i)
            for i in car_matrix[1][:]:   #removing cars who got out, even though there is no car who gets out muahahahaha
                if i not in car_matrix_actualized:
                    car_matrix[1].remove(i)
            for i in car_matrix_actualized: 
                if traci.vehicle.getRouteIndex(str(i)) == (len(traci.vehicle.getRoute(str(i))) - 1): #verification to see if the car is at the end of its route
                    new_destiny = random.choice(traci.edge.getIDList())
                    while (new_destiny[0] == ':'):
                        new_destiny = random.choice(traci.edge.getIDList())
                    traci.vehicle.changeTarget(str(i),str(new_destiny))
            car_matrix_0 = np.array(car_matrix[0])
            pos_ix = np.array(list(map(pos_x,car_matrix_0)))
            pos_iy = np.array(list(map(pos_y,car_matrix_0)))
            for i in car_matrix[1]:
                dist = np.sqrt((pos_ix - traci.vehicle.getPosition(i)[0])**2 + (pos_iy - traci.vehicle.getPosition(i)[1])**2)
                print(car_matrix_0)
                print(dist)
                print(dist<30)
                print(dist[dist < 30])
                indexes = car_matrix_0[dist < 30]
                car_matrix_actualized = traci.vehicle.getIDList()
                contamination(indexes,data_car,car_matrix) 
                
            all_cars = list(car_matrix_actualized)
            car_matrix = separation(all_cars) 
            car_matrix_last = car_matrix_actualized
            print("\n")

    traci.close()
    sys.stdout.flush()

# main entry point
if __name__ == "__main__":
    options = get_options()

    # check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "usp.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()