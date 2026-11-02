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

from typing import Any, Dict

def ActionHandler( scObject):

    # --- Action Functions --- 
    def _handle_set_target(sim_time: float, data: dict):
        # 1. Check the type of the value of the "value" key at the start
        val = data.get("value")
        val_type = type(val).__name__
        
        # Depending on your guidance module, 'sigma_R' might expect a float, int, or list/vector.
        # Adjust allowed types here as needed:
        if not isinstance(val, (str)):
            raise TypeError(f"Expected 'value' to be a number or list for 'set_target', got {val_type}.")

        set_target = np.array(json.loads(val))

        state_msg = scObject.scStateOutMsg.read()
            # 2. Extract telemetry / status
        current_state = {
            "time": sim_time,
            #"position": dataRecs[0].r_BN_N,
            #"velocity": dataRecs[1].v_BN_N
            "position": state_msg.r_BN_N,
            "velocity": state_msg.v_BN_N
            }

        # 3. Print simulation logs
        print(f"Command applied at t={sim_time}s")
        print(f"Time: {sim_time}s | Pos: {current_state.get('position', 'Unknown')}")
        print(f'Set Target: {set_target}')


        return json.dumps({"status": "Execute the function set_target"})

    def _handle_exit(sim_time : float, data: dict) :

        return json.dumps({"status": "Execute the function exit"}) 

    # Private dictionary storing action name strings mapped to their respective functions
    _action_registry: Dict[str, callable] = {
            "set_target": _handle_set_target,
            "exit" : _handle_exit
            }

    def execute_action( json_input: Any) -> Any:
        """
        Parses the JSON input, checks the action, and dispatches it to the appropriate function.
        Accepts either a JSON string or a pre-parsed dictionary.
        """
        if isinstance(json_input, str):
            try:
                data = json.loads(json_input)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {e}")
        elif isinstance(json_input, dict):
            data = json_input
        else:
            raise TypeError("Input must be a JSON string or a dictionary.")

        action_name = data.get("action")
        if not action_name:
            raise KeyError("The JSON object must contain an 'action' key.")

        if action_name not in _action_registry:
            raise ValueError(f"Action '{action_name}' is not recognized.")

        # Dispatch to the corresponding function in the private dictionary
        return _action_registry[action_name](data)



    return _action_registry

    
