import os
from copy import copy

import cmd

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from Basilisk import __path__

bskPath = __path__[0]
fileName = os.path.basename(os.path.splitext(__file__)[0])

from Basilisk.simulation import spacecraft

from Basilisk.utilities import (
    SimulationBaseClass,
    macros,
    orbitalMotion,
    simIncludeGravBody,
    vizSupport,
)
from Basilisk.utilities import simHelpers

import socket
import json

import cmdAction

def run(i):
    simTaskName = "simTask"
    simProcessName = "simProcess"

    scSim = SimulationBaseClass.SimBaseClass()

    scSim.SetProgressBar(False)

    #  create the simulation process
    dynProcess = scSim.CreateNewProcess(simProcessName)

    # create the dynamics task and specify the integration update time
    simulationTimeStep = macros.sec2nano(10.0)
    dynProcess.addTask(scSim.CreateNewTask(simTaskName, simulationTimeStep))

    # setup Gravity Body (Pure Point-Mass with Mean Earth Radius)
    gravFactory = simIncludeGravBody.gravBodyFactory()
    planet = gravFactory.createEarth()
    planet.isCentralBody = True  # ensure this is the central gravitational body
    planet.radEquator = 6371000.0  # Mean Earth radius in meters

    mu = planet.mu

    # Mean Earth radius & Altitude
    Re = 6371000.0 # in meters
    Alt = 600000.0 # in meters

    #
    #   setup orbit and simulation time
    #
    oe = orbitalMotion.ClassicElements()
    rLEO = Re + Alt  # meters
    oe.a = rLEO
    oe.e = 0.0
    oe.i = i * macros.D2R
    oe.Omega = 0.0 * macros.D2R
    oe.omega = 0.0 * macros.D2R 
    oe.f = 0.0 * macros.D2R

    # set the simulation time (3 full orbits)
    n = np.sqrt(mu / oe.a / oe.a / oe.a)
    P = 2.0 * np.pi / n
    simulationTime = macros.sec2nano(3.0 * P)
    
    # Setup data logging before the simulation is initialized
    numDataPoints = 600
    samplingTime = simHelpers.samplingTime(
        simulationTime, simulationTimeStep, numDataPoints
    )

    scObject = spacecraft.Spacecraft()
    scObject.ModelTag = f"BAE-Azalea-Sat"

    scSim.AddModelToTask(simTaskName, scObject)
    gravFactory.addBodiesTo(scObject)

    oe_k = copy(oe)
    oe_k.f = oe.f + ( 90.0) * macros.D2R
    rN, vN = orbitalMotion.elem2rv(mu, oe_k)

    scObject.hub.r_CN_NInit = rN  # m
    scObject.hub.v_CN_NInit = vN  # m/s

    dataRec = scObject.scStateOutMsg.recorder(samplingTime)
    scSim.AddModelToTask(simTaskName, dataRec)

    viz = vizSupport.enableUnityVisualization(scSim, simTaskName, scObject)
    '''
    viz.comProtocol = "tcp"
    viz.comAddress = "127.0.0.1"
    viz.comPortNumber = "5556"
    '''

    # Initialize a non-blocking TCP socket server for user interaction
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("127.0.0.1", 8080))
    server_socket.listen(1)
    server_socket.setblocking(False)

    scSim.InitializeSimulation()
    sim_time = 0.0
    step_size = 1.0 

    handler = cmdAction.ActionHandler( scObject)

    print(f'Starting Simulation')

    while sim_time < simulationTime:
            sim_time += step_size
            scSim.ConfigureStopTime(macros.sec2nano(sim_time))
            scSim.ExecuteSimulation()
            '''
            state_msg = scObject.scStateOutMsg.read()
            # 2. Extract telemetry / status
            current_state = {
            "time": sim_time,
            #"position": dataRecs[0].r_BN_N,
            #"velocity": dataRecs[1].v_BN_N
            "position": state_msg.r_BN_N,
            "velocity": state_msg.v_BN_N
            }
            '''

            # 1. Non-blocking check for incoming user commands
            try:
                client_socket, addr = server_socket.accept()
                client_socket.setblocking(True)
                data = client_socket.recv(1024).decode()
                #if data:
                cmd = json.loads(data)
                # Example command: {"action": "set_target", "value": [1.0, 0.0, 0.0]} 
                response = handler[cmd.get("action")](sim_time, cmd) 
                client_socket.sendall(response.encode())#json.dumps({"status": "acknowledged"}).encode())
                client_socket.close()

                if cmd.get("action") == "exit":
                    sim_time = simulationTime
            except BlockingIOError:
                pass  # No incoming connection this step; continue simulation
    server_socket.close()

    print(f'Simulation ended\n')


if __name__ == "__main__":
    run(97.5)
