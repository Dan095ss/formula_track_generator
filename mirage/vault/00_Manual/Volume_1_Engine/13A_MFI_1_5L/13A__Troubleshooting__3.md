---
type: manual_section
vehicle: '[[Car_Mitsubishi_Mirage_1999]]'
title: MFI 1.5L (впрыск) — Troubleshooting
title_en: MFI 1.5L — Troubleshooting
chapter_code: 13A
chapter: MFI 1.5L (впрыск)
section: Troubleshooting
section_index: page-72
volume: Volume 1
source_pdf: 13A MFI 1.5L.pdf
page_range: 72-82
page_count: 11
topics:
- fuel_injection
- diagnostics
aliases:
- 13A Troubleshooting
- 13A-Troubleshooting
- MFI 1.5L Troubleshooting
related_parts: []
related_issues: []
last_verified: '2026-05-08'
tags:
- manual
- fuel_injection
---

# MFI 1.5L (впрыск) — Troubleshooting

> **Глава:** `13A` MFI 1.5L  
> **Источник:** `13A MFI 1.5L.pdf` (стр. 72-82)  
> **Авто:** [[Car_Mitsubishi_Mirage_1999]]

---

TECHNICAL DESCRIPTION

0 The ECM turns on the evaporative emission ventilation solenoid which shuts off the evaporative emission canister outlet port. Then the evaporative emission purge solenoid is driven. As a result, the fuel system will be set into a negative pressure.

When the fuel system reaches negative pressure, the evaporative emission purge solenoid is turned “off,” and the fuel system are sealed. As the fuel pressure inside the fuel tank changes, the ECM judges if there is a leak in the fuel system.

DTC SET CONDITIONS Check Area

At least sixteen minutes have passed since the starting sequence was completed.

Engine coolant temperature higher than 60” C (1 40 O F) .

Engine speed is 1,600 r/min or more.

Power steering pressure switch: “OFF.” Barometric pressure is higher than 76 kPa (11 psi).

Volumetric efficiency is at between 20 and 80 percent.

The engine coolant temperature is 30°C (86’F) or less when the engine is started.

Intake air temperature is higher than 5°C (41 O F ) .

The pressure rise when the evaporative emission purge solenoid and evaporative emission ventilation solenoid are closed is less than 451 Pa (0.065 psi).

OVERVIEW OF TROUBLESHOOTING

0 To determine the cause of DTC P0442, a performance test is needed. The performance test uses a mechanical vacuum gauge and scan tool ME3991502 set on the fuel tank differential pressure sensor (TANK PRS SNSR 73). The mechanical gauge reading is used to verify scan tool MB991502 reading. A comparison of the mechanical gauge to scan tool MB991502 determines the problem in the system.

Prior to doing the performance test, several simple inspections are needed to exclude some possibilities of the symptom.

0

The pressure fluctuation width is less than 647 Pa (0.094 psi).

At least twenty seconds have passed since pressure fluctuation detection commenced.

Fuel tank differential pressure sensor output voltage is 1 - 4 volts.

Intake air temperature is 30°C (86°F) or less when the engine started.

Vehicle speed is 30 km/h (18.7 mph) or more.

Monitoring time: 75 - 125 seconds

0

0

0

0

0 0

Judgment Criteria

Internal pressure of the fuel tank has changed more than 843 Pa (0.122 psi) in 20 seconds after the tank and vapor line were closed.

TROUBLESHOOTING HINTS The most likely causes for this code to be set are:

0

Loose fuel cap.

0 Fuel cap relief pressure is incorrect.

0 Evaporative emission canister seal is faulty.

0 Evaporative emission canister is clogged.

0 Fuel vent valve failed.

0 Purge line or vapor line is clogged.

0 Fuel tank, purge line or vapor line seal failed.

0 Evaporative emission purge solenoid failed.

0 Evaporative emission ventilation solenoid failed.

0 Fuel tank differential pressure sensor failed.

0 Engine coolant temperature sensor failed.

0 Intake air temperature sensor failed.

0 Power steering pressure switch failed.

0 Use of incorrect fuel.

MFI <I

DIAGNOSIS Required Special Tool:

MB991502: Scan Tool (MUT-IT)

Caution To prevent damage to scan tool MB991502, turn the ignition switch off before connecting or disconnecting scan tool MB991502.

In this procedure, scan tool MB991502 should be used in the metric mode (showing the value in kPa). If not, set scan tool MB991502 by selecting the “System Setup” at the main menu.

STEP 1. Check for other DTCs.

If any other DTCs are set, please check those DTCs first then follow the steps below.

STEP 2. Evaporative Emission System Leak Monitor Test using scan tool MB991502.

NOTE: This monitor is carried out at an engine speed of 1,600 r/min or more, transmission is in “N” or “R” position.

The engine speed has to be automatically adjusted.

(1) Erase the DTCs using scan tool MB991502. Ensure that the fuel cap is securely tightened.

(2) Select “System Test” and press “YES” key.

(3) Select “Evap Leak Mon” and press “YES” key.

(4) If “Evap Leak Mon” is selected before starting the engine, “Engine must be running.” is displayed. In this case, start the engine and then select “Evap Leak Mon” again.

(5) If “Keep the TPS in idle position. during the test.” is displayed, the ECM adjusts engine speed automatically.

A manual adjustment for engine speed is not needed.

(6) Keep the, idling position during the monitor.

NOTE: if the engine speed does not reach 2,000 r/min during the monitor test, adjustment of the Speed Aqusting Screw may be needed. Refer to P13A-143 for the adjustment procedure.

(7) Item “In Progress” is displayed during the monitor. Keep the engine speed and load within the defined range. Scan tool Mi3991502 shows these items on the screen.

Item “In Progress” will be change from “NO” to “YES” by keeping engine conditions.

(8) Message “Evap Leak Mon. Completed. Test Passed.” is displayed when the test has been completed without malfunction. Evaporative emission system is working property at this time. Please explain to customer that improperly tightened fuel cap can cause to MIL turn on.

No further steps are needed.

(9) Message “Evap Leak Mon. Completed. Test Failed & DTCs Set.” is displayed when a malfunction has been detected during the test. Go to Step 3.

(1 0) Message “Evap Leak Mon. discontinued. Retest again from the first” is displayed when the monitor was discontinued by a certain reason (input vehicle speed, engine speed and engine load was put of the specified range). Turn the ignition switch off once and start monitoring from the beginning.

NOTE: Monitoring will not start unless turning off the ignition switch is turned off once and the engine restarted.

STEP 3. Using scan tool MB991502, check “Fuel tank differential pressure sensor (date list 73)” output.

In this step, the fuel tank differential pressure sensor reading is checked to determine if the fuel tank differential pressure sensor output is within the normal range.

(1) Check the MFI data list item: TANK PRS SNSR 73 (2) Watch the sensor reading. This value varies depending on pressure inside the fuel tank.

(3) Remove the fuel cap.

NOTE: If the fuel cap is not securely tightened, it might have the cause of a leak in the EVAP system and set the DTC P0442.

(4) After the fuel cap has been removed, the pressure sensor reading should be between -0.5 kPa (-0.07 psi) and 0.5 kPa (0.07 psi).

0 If the reading is between -0.5 kPa (-0.07 psi) and 0.5 kPa (0.07 psi), the fuel tank differential pressure sensor circuit is OK. Therefore, go to Step 4.

If the reading is not between -0.5 kPa (-0.07 psi) and 0.5 kPa (0.07 psi), the fuel tank differential pressure sensor is not working properly. Replace the fuel tank differential pressure sensor.

0

STEP 4. Check the fuel vent valve plunger and flapper door operation.

NOTE: When a fuel nozzle is inserted to the fuel tank filler tube and the flapper door is opened, the fuel vent valve is closed (plunger moves towards the top of the neck). When the fuel cap is closed, the fuel cap pushes the plunger back in, which then opens the vent valve. If the flapper door or plunger does not operate properlx the vent valve stays closed even after the fuel cap is closed. This may block the vapor passage. A faulty vent valve plunger may also cause the fuel cap not to seat properly Either of these conditions can set DTC P0442.

(1) Remove the fuel cap.

(2) Push the flapper in to operate the valve.

NOTE: When the flapper is pushed in, the plunger of the valve should move towards the top.

(3) Reinstall and tighten the fuel cap until three clicks are heard.

(4) Remove the cap again and check the protrusion of the plunger to verify if it is pushed back.

*

(5) Distance between the tip of vent valve plunger and that of fuel tank filler tube should be 28 mm (1.1 inches) or more.

0 If the plunger does not return, replace the fuel tank filler tube and securely tighten the cap.

0 If the operation is OK, install and securely tighten the fuel cap.

STEP 5. Using scan tool MB991502, actuator test item 08 : Evaporative Emission Purge Solenoid.

(1) Disconnect the hose connected to the evaporative emission canister from the purge solenoid.

(2) Connect a hand vacuum pump to the nipple where the hose is disconnected at the previous step.

(3) The vacuum should be maintained when vacuum is applied and vacuum should leak when the purge solenoid is activated by the actuator test of scan tool MB991502.

0 If correct, go to Step 6.

0 If not, refer to DTC PO443 (Evaporative Emission Control System Purge Control Valve Circuit Malfunction) on P.13A-57.

STEP 6. Using scan tool MB991502, actuator test item 29 : evaporative Emission Ventilation Solenoid.

(1) Disconnect the hose connected to the vent solenoid valve from the vent solenoid valve.

(2) Connect a hand vacuum pump to the nipple that is disconnected in the previous step.

(3) The vacuum should leak when vacuum is applied, and the vacuum should be maintained when the purge solenoid is activated by the actuator test of scan tool MB991502.

0 If correct, go to Step 7.

0 If not, refer to DTC PO446 (Evaporative Emission Control System Vent Control Malfunction) on

P. 1 3A-58.

tJMOl0l

STEP 7. Check the purge solenoid-to-air intake plenum hose for blockage.

(1) Disconnect the purge solenoid-to-air intake plenum hose at the purge solenoid side.

(2) Connect a hand vacuum pump to the disconnected hose end.

(3) Apply vacuum, and check if the vacuum is not maintained.

0 If not maintained, go to STEP 8.

0 If maintained, replace the hose or intake plenum.

Then go to STEP 9.

STEP 8. Check the purge solenoid-to-air intake plenum hose for vacuum leakage.

(1) Plug the purge solenoid-to-air intake plenum hose at the purge solenoid side.

(2) Disconnect the purge solenoid-to-air intake plenum hose at the air intake plenum side.

(3) Connect a hand vacuum pump to disconnected hose end.

(4) Apply vacuum, and check if the vacuum is maintained.

0 If maintained, go to STEP 9.

0 If not maintained, replace the hose. Then go to STEP 9.

STEP 9. Performance test.

NOT€: Fuel temperature should be lower than 40°C (104°F) during the performance test.

In this step, verify if the EVAP system works properly, or determine which area of the evaporative emission system has a failure.

Caution As a 0 - 6.2 kPa (0 - 0.90 psi) range vacuum gauge is used, the gauge may be broken if excessive vacuum pressure is applied. Do not apply a vacuum of more than 2.9 kPa (0.42 psi).

To achieve the performance test efficiently, a mechanical vacuum gauge [0 - 6.2 kPa (0 - 0.90 psi) range] and scan tool MB991502 should be used, and the engine to generate vacuum.

*

(1) Install a mechanical vacuum gauge [0 - 6.2 kPa (0 - 0.90 psi) range] between the EVAP purge solenoid valve and the purge hose that comes from the evaporative emission canister.

(2) Before starting the performance test, set the vehicle in the following condition.

0 Engine coolant temperature: 80 - 90°C (1 76 - 203” F) 0 Lights and all accessories: OFF 0 Transmission: “N” or “P” position (3) Select the item TANK PRS SNSR (data list 73) on scan tool MB991502 to see the differential pressure sensor output.

(4) Run the engine at idle.

(5) Using locking pliers, pinch the hose between the purge solenoid and the intake plenum to close the purge flow, as a preparation of the performance test.

(6) Using another locking pliers, pinch the vent hose between the evaporative emission canister and the vent solenoid.

Momentary, remove the locking pliers at the purge hose;

this will cause the vacuum build up in the EVAP system.

(7) The engine vacuum comes from the purge port through the purge solenoid.

NOTE: During this operation, the purge solenoid may turn off but will resume operation in about 20 seconds.

Operation of the purge solenoid can be checked by needle fluctuation of the mechanical vacuum gauge.

(8) Watch the vacuum reading on the mechanical vacuum gauge and scan tool MB991502.

(9) When the vacuum reading reaches 2.9 kPa (0.42 psi) on the mechanical vacuum gauge and -2.9 kPa (-0.42 psi) on scan tool MB991502, pinch the hose between the purge solenoid and the intake manifold plenum using another locking pliers; this stops the application of vacuum and seals the EVAP system for the leak test.

NOTE: If there is a system failure, either of both vacuum readings may not reach to the above specifications. In this case, it is not necessary to pinch off the purge hose as shown. Refer to the performance test results table below for further steps.

(10)After an elapsed time of 20 seconds, check the fuel tank differential pressure reading on scan tool MB991502.

OK: Change in pressure reading is 0.4 kPa (0.06 psi) or less [holding -2.5 kPa (-0.36 psi) or morevacuum].

Performance test result table:

SCAN TOOL MB991502 READING

MECHANICAL VACUUM GAUGE READING

Reaches -2.9 kPa (-0.42 psi) and vacuum drops not more than 0.4 kPa (0.06 psi) in 20 seconds.

Reaches 2.9 kPa (0.42 psi).

Does not reach -2.9 kPa (-0.42 psi)."

Reaches 2.9 kPa (0.42 psi).

Does not reach -2.9 kPa (-0.42 psi).

Does not reach 2.9 kPa (0.42 psi).

Reaches -2.9 kPa (-0.42 psi) but vacuum drops more than 0.4 kPa (0.06 psi) in 20 seconds.

Reaches 2.9 kPa (0.42 psi).

NOTE *: If there is a blockage, scan tool MB991502 reading can be a positive value (positive pressure) due to the heat of return fuel from the engine.

STEP 10. Vacuum reading on both the mechanical gauge and scan tool MB991502 reaches the specifications and satisfy the specifications after 20 seconds:

EVAP system is properly working at the moment. The cause of DTC might have been a loose fuel cap and the customer may have already tightened fuel cap causing the MIL to turn on. No further steps are needed.

STEP 11. Vacuum reading on the mechanical gauge reaches 2.9 kPa (0.42 psi) but scan tool MB991502 does not reach -2.9 kPa (-0.42 psi) :

(1) If the vacuum reading on the gauge reaches 2.9 kPa (0.42 psi) but the reading on scan tool MB991502 does not reach -2.9 kPa (-0.42 psi), either a system blockage or a bad differential pressure sensor may be the cause.

(2) To determine if there is a blockage in the system, remove the fuel cap.

GO TO

RESULT

Step 10

Satisfactory.

No leak nor blockage detected.

Step 11

Blockage in the system or bad differential sensor.

Step 13

Large leak in EVAP system.

Small leak in EVAP system.

Step 14

0 If the vacuum reading on the vacuum gauge [at this point 2.9 kPa (0.42 psi)] remains the same, there is a blockage in the system. Go to Step 12.

If the reading drops to about 0 kPa (0 psi), there is no blockage in the EVAP system. The fuel tank differential pressure sensor needs to be replaced.

After replacing the differential pressure sensor, go to Step 15.

0

STEP 12. System blockage inspection.

SOLENOID PURGE *

(1) Disconnect the number 1 and 2 hoses shown in the illustration, check the mechanical vacuum gauge reading.

If the vacuum reading does not drop, then the blockage is not in the fuel tank.

(2) Disconnect one portion of the EVAP system at a time working towards the front of the vehicle until blockage is found (number 1 to 5 hoses in the illustration).

(3) Repair the location of the blockage and go to Step 15.

VENTILATION I S I/

5

I 1 LIQUID SEPARATOR

EVAPO RAT1 VE EMISSION CANISTER FUEL TANK B03'0115

STEP 13. Vacuum readings on both the mechanical gauge and scan tool MB991502 do not reach the specifications [2.9 kPa (0.42 psi) and -2.9 kPa (-0.42 psi)]:

This condition shows that there is a significant leakage in the system. The inspection procedure for the large system leakage is the same as the small leakage test in Step 14.

MFI <I

STEP 14. Vacuum readings on both the mechanical gauge and scan tool MB991502 do not reach the specification [2.9 kPa (0.42 psi) and -2.9 kPa (-0.42 psi)] but do not maintain the vacuum.

This condition shows that there is a slight leakage in the system. Follow the procedure below to locate the source of the leak.

(1) The fuel cap relief valve inspection.

a. Remove the fuel cap and install the fuel tank filler tube adapter in the emission system tester kit in place of the fuel cap.

b. Plug the nipple on the fuel tank filler tube adapter.

c. Repeat the performance test. If the EVAP system holds the vacuum, then the fuel cap is faulty. Replace the fuel cap, and go to Step 15.

(2) To find the vacuum leakage in the system, clamp the number 1 and 2 hoses shown in the illustration. Repeat the performance test. This will determine if the vacuum leak is either in the fuel tank area or in the rest of the system.

NOTE: In this case, as we clamped off the vacuum hose connecting to the fuel tank, scan tool MB991502 reading will not change. Please use the mechanicalgauge reading.

A0320089 I

I

VENTILATION SOL

0 If the EVAP system hold the vacuum leak is in the fuel tank area. To locate the leakage, pressurize the EVAP system to 3.4 kPa (0.49 psi) and look for leaky area using the ultrasonic leak detector in the Evaporative Emission System Tester. After repairing the leakage, go to Step 15.

0 If the vacuum leak still exists, the leak is at other than fuel tank area.

(3) Clamp off the vacuum hose one component at a time working towards the front of the vehicle until leakage is found (number 1 to 5 hoses shown in the illustration).

(4) Repair the leakage at that location and go to Step 15.

LIQUID SEPARATOR .

:VAPOR

EMISSION CANISTER FUEL TANK B03'0115

STEP 15. Confirmation test.

After system failures are repaired, repeat the Evaporative Emission System Leak Monitor test (Step 2) to check that the EVAP system operates correctly.

*

Background 0 The vehicle speed sensor outputs a pulse signal while the vehicle is driven.

0 The engine control module checks whether the pulse signal is output.

Check Area 0 At least 2 seconds have passed since the engine was started 0 Closed throttle position switch OFF 0 Engine speed is not lower than 3000 r/min 0 intake air pipe pressure is 83 kPa (12 psi) or more.

Judgment Criteria 0 Sensor output voltage has not changed (no pulse signal is input) for 2 sec.

OK: 4 8 - 5 2 V

- Measure at the vehicle speed sensor connector A-55.

0 Disconnect the connector, and measure at the harness side.

1. Voltaae between 1 and earth (lanition switch: ON) I I I

~., OK: -Battery positive voltage

2. Voltage between 3 and ground (Ignition switch: ON)

3 Continuity between 2 and ground O K Continuity

NG NG 1 Check t m w Repair

NG 1 Check the following 1 w Repair connector: w I Check trouble symptom.

I

Check the harness wire Repair between the ECM and the vehicle speed sensor . connector.

E p l a c e the ECM

0 Vehicle speed sensor failed 0 Open or shorted vehicle-speed sensor circuit, or loose connector 0 Engine control module failed

Check the following

- Repair connectors: 8-35, 8-63, 4"" Check trouble symptom.

1 between ti;" vehicle 1 speed sensor and ignition switch connector.

Check the ignition switch (Refer to GROUP 54 - Ignition Switch.)

_ _ _ ~

NG

Check the following w Repair connector: 8-37

Check trouble symptom.

Repair

vehicle speed sensor connector

Replace the ECM

+

Check the harness wire between the vehicle speed sensor and the ground, and repair if necessary.

~~

I3A-82

Code No. PO505 Idle Control System Malfunction

~ 3ackground

D If there is a malfunction of the IAC system, the actual engine speed will not be identical to the target engine speed The engine control module checks the difference between the actual engine speed and the target engine speed 2heck Area

Vehicle speed has reached 1 5 km/h (0 93 mph) at least once

D Under the closed loop idle speed control Judgment Criteria

Actual idle speed has continued to be higher than the target idle speed by 300 r/min or more for 10 sec.

Check Area

Vehicle speed has reached 1 5 km/h (0 93 mph) at least once.

During idle speed closed loop control The highest temperature at the last drive is 45°C (113°F) or less

Engine coolant temperature is approx 80°C (176OF) or more Battery voltage is 10 V or more Intake air temperature is -10°C (14°F) or more Judgment Criteria

Actual idle speed has been minimum 200 rimin higher than the target idle speed for ten seconds Check Area 0 During idle speed closed loop control 0 Engine coolant temperature is about 80°C (176°F) or higher 0 Battery voltage is 10 V or higher 0 Power steering switch is off 0 Intake air pipe pressure is 53 kPa (7.7 psi) or less 0 Intake air temperature is -10°C (14'F) or more Judgment Criteria 0 Actual idle speed has been minimum 100 r/min higher than the target idle speed for ten seconds ~

Check the idle air control motor. (Refer to P.13A-156.) -1 NG

NG

Measure at the idle air control motor connector A-51.

Disconnect the connector and measure at the harness side.

0 Voltage between 2 and ground, and 5 and ground (Ignition switch ON) OK: Battery positive voltage

NG D Repair NG Measure at the ECM connector 6-40 F Check the following 0 Disconnect the connector, measure at the harness side.

connector:

0 Voltage between each of 4, 5, 17, 18 and ground (Ignition switch. ON) OK: Battery positive voltage

Repair connector:

I Check trouble symptom.

1 Replace the ECM.

'robable cause

1 Idle air control motor failed

1 Open or shorted idle air control motor circuit, or loose connector

1 Engine control module failed

D Replace

Check the harness wire between MFI relay and idle air control motor connector. Repair, if necessary.

1 A-51

I Check trouble symptom.

Check harness wire between ECM and idle air control motorconnec- 1 tor. Reoair. if necessarv.
