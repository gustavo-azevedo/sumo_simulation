import os, sys
import optparse
import subprocess
import random
import math


# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append("/home/gustavo/Downloads/sumo-0.32.0/tools")
    from sumolib import checkBinary
except ImportError:
    sys.exit("please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")       
import traci

#functions to calculate the distance between 2 cars

global car_matrix

def pythagoras(x,y):                     #simple pythagoras theorem
    pythagoras = math.sqrt(x*x + y*y)
    return pythagoras

def distance(veh1,veh2):      #euclidean distance of two cars
    distance = pythagoras(traci.vehicle.getPosition(str(veh1))[0] - traci.vehicle.getPosition(str(veh2))[0],traci.vehicle.getPosition(str(veh1))[1] - traci.vehicle.getPosition(str(veh2))[1])
    return distance

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
            vector.append(i)
            traci.vehicle.setColor(i,(0,255,0,255))
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



def contamination(veh1,veh2): #pass on the contaminated colors to the non-contaminated cars
    if distance(str(veh1),str(veh2)) < 30:   #if the car is within the contamination distance
        traci.vehicle.setColor(str(veh2),(255,0,0,255))  #the car is contaminated with the red color



# contains TraCI control loop
def run():
    step = 0
    non_contaminated_vector = []
    contaminated_vector = []
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1  
        if step > 6 and step < 12:  #it gives some time for the cars to enter the simulation
            j = 0
            i = 0
            k = 0
            all_cars = []
            all_cars = (traci.vehicle.getIDList()) 
            for i in all_cars:
                traci.vehicle.setColor(i,(0,255,0,255))
            traci.vehicle.setColor(all_cars[1],(255,0,0,255)) #the second car is the red one
            car_matrix = separation(all_cars)
        if step >= 12:      #starts the contamination
            car_matrix_actualized = traci.vehicle.getIDList()   #gets the cars who are in the simulation in the new step
            for i in car_matrix_actualized:
                if traci.vehicle.getRouteIndex(str(i)) == (len(traci.vehicle.getRoute(str(i))) - 1): #verification to see if the car is at the end of its route
                    new_destiny = random.choice(traci.edge.getIDList())
                    traci.vehicle.changeTarget(str(i),str(new_destiny))
            for i in car_matrix[1]:
                for j in car_matrix[0]:
                    if j not in car_matrix[1]:
                        contamination(str(i),str(j))
            car_matrix = separation(all_cars) 


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