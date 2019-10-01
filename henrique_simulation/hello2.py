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

def pitagoras(x,y):
    pitagoras = math.sqrt(x*x + y*y)
    return pitagoras

def distancia(veh1,veh2):
	distancia = pitagoras(traci.vehicle.getPosition(str(veh1))[0] - traci.vehicle.getPosition(str(veh2))[0],traci.vehicle.getPosition(str(veh1))[1] - traci.vehicle.getPosition(str(veh2))[1])
	return distancia

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

# contains TraCI control loop
def run():
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1  
        if step > 2:
            if distancia("veh1","veh0") < 5:
                traci.vehicle.setColor("veh1",(255,0,0,255))
            if distancia("veh0","veh2") < 5 :
                traci.vehicle.setColor("veh2",(255,0,0,255))
            if traci.vehicle.getColor("veh2") == (255,0,0,255):
                if distancia("veh1","veh2") < 5 :
                    traci.vehicle.setColor("veh1",(255,0,0,255))
            print(traci.vehicle.getColor("veh0"))
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
    traci.start([sumoBinary, "-c", "hello.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()
