import os
from copy import copy

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

    scObjects = []
    dataRecs = []

    # Create 4 spacecraft equally spaced by 90 degrees (0, 90, 180, 270 deg)
    for k in range(3):
        scObject = spacecraft.Spacecraft()
        scObject.ModelTag = f"bsk-Sat-{k}"

        scSim.AddModelToTask(simTaskName, scObject)
        gravFactory.addBodiesTo(scObject)

        oe_k = copy(oe)
        oe_k.f = oe.f + (k * 90.0) * macros.D2R
        rN, vN = orbitalMotion.elem2rv(mu, oe_k)

        scObject.hub.r_CN_NInit = rN  # m
        scObject.hub.v_CN_NInit = vN  # m/s

        dataRec = scObject.scStateOutMsg.recorder(samplingTime)
        scSim.AddModelToTask(simTaskName, dataRec)

        scObjects.append(scObject)
        dataRecs.append(dataRec)

    '''
    if vizSupport.vizFound:
        viz = vizSupport.enableUnityVisualization(scSim, simTaskName, scObjects)#
    '''

    viz = vizSupport.enableUnityVisualization(scSim, simTaskName, scObjects)

    # Initialize a non-blocking TCP socket server for user interaction
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("127.0.0.1", 8080))
    server_socket.listen(1)
    server_socket.setblocking(False)

    scSim.InitializeSimulation()
    sim_time = 0.0
    step_size = 1.0  # 1-second chunks
    count = 0.0
    show_tel = simulationTime/100

    try:
        while sim_time < simulationTime:
            sim_time += step_size
            scSim.ConfigureStopTime(macros.sec2nano(sim_time))
            scSim.ExecuteSimulation()
            #state_msg = scObjects[0].scStateOutMsg.read()
            # 2. Extract telemetry / status
            current_state = {
            "time": sim_time,
            "position": dataRecs[0].r_BN_N,
            "velocity": dataRecs[1].v_BN_N
            }

            '''
            count += show_tel/1000
            if count >= show_tel:
                print(f"Time: {sim_time}s | Pos: {current_state['position']}")
                count = 0.0

            '''

            # 1. Non-blocking check for incoming user commands
            try:
                client_socket, addr = server_socket.accept()
                client_socket.setblocking(True)
                data = client_socket.recv(1024).decode()
                if data:
                    cmd = json.loads(data)
                    # Example command: {"action": "set_target", "value": [1.0, 0.0, 0.0]}
                    if cmd.get("action") == "set_target":
                        # Dynamically update a module variable in Python
                        #myGuidanceModule.sigma_R = cmd.get("value")
                        print(f"Command applied at t={sim_time}s")
                        print(f"Time: {sim_time}s | Pos: {current_state['position']}")
                    elif cmd.get("action") == "exit":
                        sim_time = simulationTime
                client_socket.close()
            except BlockingIOError:
                pass  # No incoming connection this step; continue simulation

    # (Optional) You can push this status to an active telemetry socket or log it
    finally:
        server_socket.close()

    '''
    scSim.ConfigureStopTime(simulationTime)
    scSim.ExecuteSimulation()
    '''

    posDataList = [rec.r_BN_N for rec in dataRecs]
    velDataList = [rec.v_BN_N for rec in dataRecs]

    np.set_printoptions(precision=16)

    figureList, finalDiff = plotOrbits(
        dataRecs[0].times(),
        posDataList,
        oe,
        mu,
        P,
        i,
        Re
    )

    plt.show()
    plt.close("all")
    

    return finalDiff, figureList


def plotOrbits(
    timeAxis,
    posDataList,
    oe,
    mu,
    P,
    i,
    Re
):
    plt.close("all")
    omega_E = 2.0 * np.pi / 86164.1 # Earth sidereal rotation rate [rad/s]
    sc_colors = ["#aa0000", "#00aa00", "#0000aa", "#aa00aa"]
    tgt_colors = ["#ff6666", "#66ff66", "#6666ff", "#ff66ff"]
    time_orbits = timeAxis * macros.NANO2SEC / P

    figureList = {}

    # Define quarter-orbit ticks across the time domain
    max_orbits = time_orbits[-1]
    quarter_ticks = np.arange(0, max_orbits + 0.01, 0.25)

    # Compute distance data structures for plotting and pandas table
    dist_sc_km_list = []
    dist_tgt_km_list = []

    # 1. Spacecraft distance from initial position at t = 0
    for k, posData in enumerate(posDataList):
        r0_sc = posData[0]
        dist_sc_km = [np.linalg.norm(pos - r0_sc) / 1000.0 for pos in posData]
        dist_sc_km_list.append(dist_sc_km)

    # 2. Ground Targets distance from initial position at t = 0
    for k, posData in enumerate(posDataList):
        r0_sc = posData[0]
        r0_sc_mag = np.linalg.norm(r0_sc)
        r0_target = Re * r0_sc / r0_sc_mag

        dist_tgt_km = []
        for idx in range(len(timeAxis)):
            t = timeAxis[idx] * macros.NANO2SEC
            theta = omega_E * t
            cos_t = np.cos(theta)
            sin_t = np.sin(theta)

            x_t = r0_target[0] * cos_t - r0_target[1] * sin_t
            y_t = r0_target[0] * sin_t + r0_target[1] * cos_t
            z_t = r0_target[2]
            r_target_t = np.array([x_t, y_t, z_t])

            dist_km = np.linalg.norm(r_target_t - r0_target) / 1000.0
            dist_tgt_km.append(dist_km)
        dist_tgt_km_list.append(dist_tgt_km)

    # --- Generate Pandas Table for First 8 Quarter Orbits ---
    target_quarter_orbits = np.arange(0.0, 2.01, 0.25)
    table_data = []

    for q_orb in target_quarter_orbits:
        idx = np.argmin(np.abs(time_orbits - q_orb))
        row = {"Time (t/T)": f"{q_orb:.2f}"}
        for k in range(4):
            row[f"SC {k} Dist (km)"] = f"{dist_sc_km_list[k][idx]:.2f}"
            row[f"Tgt {k} Dist (km)"] = f"{dist_tgt_km_list[k][idx]:.2f}"
        table_data.append(row)

    df = pd.DataFrame(table_data)
    print("\n" + "="*80)
    print(" PANDAS TABLE: INITIAL POSITION DISTANCES (FIRST 8 QUARTER ORBITS)")
    print("="*80)
    print(df.to_string(index=False))
    print("="*80 + "\n")

    # --- Figure 1: Distance from Initial Starting Point in km ---
    plt.figure(1, figsize=(11, 6), dpi=100)
    ax1 = plt.gca()
    ax1.ticklabel_format(useOffset=False, style="plain")

    for k in range(4):
        plt.plot(time_orbits, dist_sc_km_list[k], color=sc_colors[k], linewidth=2.0, label=f"Spacecraft {k} from initial point")
        plt.plot(time_orbits, dist_tgt_km_list[k], color=tgt_colors[k], linestyle="--", linewidth=1.5, label=f"Ground Target {k} from initial point")

    plt.xticks(quarter_ticks)
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0.5)
    plt.xlabel("Time (t / T) [Orbits]")
    plt.ylabel("Distance from Initial Position [km]")
    plt.title(f"Position Relative to Fixed Initial Point (i = {i} deg)")
    plt.grid(True)
    plt.tight_layout()
    figureList[fileName + " Distance From Initial Point i=" + str(i) + " Degrees"] = plt.figure(1)

    # --- Figure 2: Spacecraft Altitude in km ---
    plt.figure(2, figsize=(11, 6), dpi=100)
    ax2 = plt.gca()
    ax2.ticklabel_format(useOffset=False, style="plain")

    for k, posData in enumerate(posDataList):
        alt_km = [(np.linalg.norm(pos) - Re) / 1000.0 for pos in posData]
        plt.plot(time_orbits, alt_km, color=sc_colors[k], linewidth=2.0, label=f"Spacecraft {k} Altitude")

    plt.xticks(quarter_ticks)
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0.5)
    plt.xlabel("Time (t / T) [Orbits]")
    plt.ylabel("Altitude Above Mean Radius [km]")
    plt.title(f"Spacecraft Altitude Throughout Simulation (i = {i} deg)")
    plt.grid(True)
    plt.tight_layout()
    figureList[fileName + " Altitude km i=" + str(i) + " Degrees"] = plt.figure(2)

    finalDiff = 0.0
    return figureList, finalDiff


if __name__ == "__main__":
    run(97.5)
