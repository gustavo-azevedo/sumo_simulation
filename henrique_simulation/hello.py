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

#funcoes para calcular a distancia

global matriz_carros

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


def separacao(vetor):
    i = 0
    j = 0
    vetor_puro=[]
    vetor_contaminado=[]
    for i in traci.vehicle.getIDList():
        if i not in vetor:
            vetor.append(i)
            traci.vehicle.setColor(i,(0,255,0,255))
    for i in vetor:
        if traci.vehicle.getColor(i) == (255,0,0,255): #se o carro eh vermelho e nao ja esta no vetor contaminado adiciona-se ele ao vetor contamindo
            if i not in vetor_contaminado:
                    vetor_contaminado.append(i)
        else:                                           #se o carro nao eh vermelho e ja nao esta no vetor dos puros adiciona-se ele ao vetor dos puros
            if i not in vetor_puro:
                vetor_puro.append(i)
    matriz_carros = 0
    matriz_carros = [vetor_puro,vetor_contaminado]
    return matriz_carros



def contaminacao(veh1,veh2,matriz_carros):
    if distancia(str(veh1),str(veh2)) < 5:
        traci.vehicle.setColor(str(veh2),(255,0,0,255))



# contains TraCI control loop
def run():
    step = 0
    vetor_puro = []
    vetor_contaminado = []
    matriz_contaminados = []
    matriz_contaminados_2 = []
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        print(step)
        step += 1  
        if step > 6 and step < 12:
            j = 0
            i = 0
            k = 0
            carros_totais = []
            carros_totais = (traci.vehicle.getIDList())
            for i in carros_totais:
                traci.vehicle.setColor(i,(0,255,0,255))
            print(carros_totais)
            traci.vehicle.setColor(carros_totais[1],(255,0,0,255))
            matriz_carros = separacao(carros_totais)
            print(matriz_carros)
        if step >= 12:
            for i in matriz_carros[1]:
                for j in matriz_carros[0]:
                    if j not in matriz_contaminados:
                        contaminacao(str(i),str(j),matriz_carros)
            print(matriz_carros)
            matriz_carros = separacao(carros_totais)


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
