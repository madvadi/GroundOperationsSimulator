This is an example of running a ground station for a Low Earth Orbit (LEO) spacecraft. The simulation is modeled after BAE Azalea-style satellite systems and is designed to explore how to operate a typical multi-sensor spacecraft (incorporating optical, radar, or Software Defined Radio payloads). From an astrodynamic and operational standpoint, Azalea represents an ideal archetype for studying modern commercial and defense-oriented LEO constellations.

The specification for this simulation is to understand what happens during key phases of the satellite's journey, simulating the following operational stages:  

## 1. Launch and Early Orbit Phase (LEOP)
Spanning the first hours to weeks after separation, LEOP is the highest-risk phase of the mission. The simulation models the chronological sequence of early survival and stabilization steps:
* **Separation and De-tumbling:** Following separation from the launch vehicle dispenser, the spacecraft uses its Attitude Determination and Control System (ADCS) magnetorquers and reaction wheels to dampen residual tip-off rates.
* **First Acquisition of Signal (AOS):** The ground station locks onto the initial telemetry beacon during the first visibility pass to establish communication.
* **Appendage Deployment:** Automated timers or ground commands trigger burn-wire release mechanisms to deploy solar arrays, telemetry antennas, and any deployable sensor booms.
* **Power Subsystem (EPS) & Thermal Startup:** The Electrical Power Subsystem transitions from internal launch batteries to solar generation and battery charging. Initial thermal stabilization is monitored across the first eclipse cycles.
* **ADCS Safe-Point Transition:** The spacecraft transitions from rate-damping mode into a Sun-pointing or safe attitude mode to guarantee positive power margins.
* **Initial Health Assessment & Orbit Determination:** Telemetry channels are meticulously checked across all housekeeping subsystems (EPS, OBDH, ADCS, Thermal). Concurrently, initial tracking data and onboard GPS are used to determine launch dispersion and verify the orbit.
* **Trajectory Correction Manoeuvres (TCM):** Small thruster burns (if propulsion is equipped) are executed to correct injection errors relative to the target operational orbit.

## 2. Moving to Station (Orbit Raising & Phasing)
Once the platform is confirmed stable, the spacecraft performs a series of orbit-raising or drift maneuvers using its propulsion system to move from its initial launch insertion orbit into its precise operational slot within the constellation plane. 

## 3. Payload Commissioning (In-Orbit Testing - IOT)
With the spacecraft safely parked in its operational orbit, payload checkout begins:
* **Subsystem & Bus Validation:** High-level bus and payload electronics are powered on and tested under real space conditions.
* **Payload Calibration:** For an Azalea-class architecture, this involves calibrating Software Defined Radios (SDR), RF mapping sensors, or optical/SAR payloads against known ground targets.
* **Insurance Milestone:** Successful completion of payload commissioning typically marks the point where launch and early-orbit insurance policies transition or expire.

## 4. On-Station Operations (Routine Operations)
The long-term nominal phase of the mission:
* Regular tasking, data collection, and onboard processing (such as machine learning data analysis).
* Automated pass scheduling for downlinking gathered intelligence data to ground stations.
* Routine housekeeping monitoring, momentum dumps, and minor station-keeping burns.

## 5. Spacecraft Decommissioning (End of Life - EOL)
When the mission lifetime concludes (typically around 5 years for smallsat architectures):
* **Passivation:** Depleting residual fuel, discharging batteries, and shutting down transmitters to prevent orbital debris generation.
* **De-orbit / Re-entry:** Executing controlled de-orbit burns or relying on atmospheric drag to ensure compliance with space sustainability regulations regarding orbital lifetime.

## Cross-Cutting State: Non-Nominal Operations (Anomalies & Contingencies)
* Rather than a final phase, non-nominal handling is a dynamic operational mode that can trigger 
* Simulates anomaly detection, automatic safe-mode entry, fault isolation, contingency command uplinks, and recovery procedures managed by the ground control team.
