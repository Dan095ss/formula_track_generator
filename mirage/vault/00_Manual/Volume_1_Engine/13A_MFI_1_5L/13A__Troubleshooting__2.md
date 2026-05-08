---
type: manual_section
vehicle: '[[Car_Mitsubishi_Mirage_1999]]'
title: MFI 1.5L (впрыск) — Troubleshooting
title_en: MFI 1.5L — Troubleshooting
chapter_code: 13A
chapter: MFI 1.5L (впрыск)
section: Troubleshooting
section_index: page-12
volume: Volume 1
source_pdf: 13A MFI 1.5L.pdf
page_range: 12-70
page_count: 59
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
> **Источник:** `13A MFI 1.5L.pdf` (стр. 12-70)  
> **Авто:** [[Car_Mitsubishi_Mirage_1999]]

---

NOTE 0 When the ECM monitored the powertrain mal-

1. After the Engine Control Module (ECM) detects function three times* and detected no malfunc- a malfunction, the Service Engine Soon/Mal- tion.

function Indicator Lamp illuminates when the *:

In this case, “one time” indicates from en- engine is next turned on and the same malfunc- gine start to stop.

tion is re-detected.

For misfiring or a fuel trim malfunction, when However, for items marked with a ‘*”, the Ser- driving conditions (engine speed, engine cool- vice Engine Soon/Malfunction Indicator Lamp ant temperature, etc.) are similar to those when illuminates on the first detection of the malfunc- the malfunction was first recorded.

tion.

2. After the Service Engine Soon/Malfunction Indi- cator Lamp illuminates, it will be switched off under the following conditions.

Caution If the Service Engine Soon/Malfunction Indicator Lamp illuminates because of a malfunction of the ECM, transmission between the scan tool and the ECM cannot occur. In this case, the diagnostic trouble code cannot be read.

0

ON-BOARD DIAGNOSTICS The engine control module monitors the input/out- put signals (some signals all the time and others under specified conditions) of the engine control module.

When a malfunction continues for a specified time or longer after the irregular signal is initially moni- tored, the engine control module judges that a mal- function has occurred.

After the engine control module first detects a mal- function, a diagnostic trouble code is recorded when the engine is restarted and the same malfunction is re-detected. However, for items marked with a '*", a diagnostic trouble code is recorded on the first detection of the malfunction.

There are 48 diagnostic items. The diagnostic re- sults can be read out with a scan tool.

Since memorization of the diagnostic trouble codes is backed up directly by the battery, the diagnostic results are memorized even if the ignition key is turned off. The diagnostic trouble codes will, howev- er, be erased when the battery terminal or the en- gine control module connector is disconnected.

Data

Engine coolant temperature

Engine speed

Vehicle speed

Long-term fuel compensation (Long-term fuel trim)

Short-term fuel compensation (Short-term fuel trim)

Fuel control condition

Calculation load value

Diagnostic trouble code during data recording

In addition, the diagnostic trouble code can also be erased by turning the ignition switch to ON and sending the diagnostic trouble code erase signal from the scan tool to the engine control module.

Caution If the sensor connector is disconnected with the ignition switch turned on, the diagnostic trouble code is memorized. In this case, send the diagnostic trouble code erase signal to the engine control module in order to erase the diagnostic memory.

The 48 diagnostic items are all indicated sequentially from the smallest code number.

The engine control module records the engine oper- ating condition when the diagnostic trouble code is set. This data is called "Freeze-frame" data.

This data can be read by using the scan tool, and can then be used in simulation tests for trouble- shooting. Data items are as follows.

Unit

"C or O F

r/m i n

km/h or mph

%

%

0 Open loop 0 Closed loop 0 Open loop-drive condition 0 Open loop-DTC set 0 Closed loop-O2 (rear) failed

I3A-I 4

OBD-I1 DRIVE CYCLE All kinds of diagnostic trouble codes can be monitored by carrying out a short drive in accordance with the following 6 drive cycle patterns. In other words, doing such a drive allows to regenerate any kind of trouble which involves illuminating the Service Engine Soon/Malfunction Indicator Lamp and to check the repair procedure has eliminated the trouble (the Service Engine Soon/Malfunction Indicator Lamp is no longer illuminated).

Caution Two mechanics should always get on the vehicle when carrying out a drive test.

Catalytic converter monitor (P0420, P0421) Test req ui rementdproced ure

1. All of the following requirements should be met when carrying out a drive test.

(1) Atmospheric temperature: - 1 0" C (1 4" F) or more (2) Condition of An:

0 Selector lever position: D range

(3) A/C switch: OFF

2. One trip monitor will be completed by driving according to the steps below (from start to switch off).

It will take 20 minutes.

*I: Start the engine, and accelerate gradually to 72 km/h (45 mph) or more.

*2: Preparation period; continue driving between 72 and 97 km/h (45 and 60 mph) for 300 seconds.

Brake may be applied for this period if it continues for only a few seconds.

*3: Decelerate to 56 - 64 km/h (35 - 40 mph).

+4: Drive between 56 and 64 km/h (35 and 40 mph) at a constant throttle angle (by not moving the throttle pedal as much as possible) for 90 seconds or more during monitor.

*5: Decelerate with the throttle valve fully closed (Brake may be applied for this period). After the vehicle is being decelerated for ten seconds, accelerate gradually to 56 - 64 km/h (35 - 40 6:

Decelerate and stop the vehicle. Then turn off the ignition switch.

mph).

Drive cycle pattern

300 sec or more

T T T Full Full Full Full Full deceleration deceleration deceleration deceleration deceleration 7 F U 19 5 6

Caution Vehicle speed and throttle opening angle should be within the shaded rage.

Evaporative emission control system leak monitor (P0442, P0450, P0455) Test requirements/procedure

1. All of the following requirements should be met when carrying out a drive test.

(1) Engine coolant temperature: 45°C (113°F) or less (before starting drive test, engine stopped) (2) Atmospheric temperature: 5°C (41°F) or more, 45°C (113°F) or less (3) Condition of W:

0 0 Overdrive switch: ON

2. One trip monitor will be completed by driving according to the steps below (from start to switch off).

Selector lever position: D range

, (It takes approx. 8 minutes.) *l:

Check that both engine coolant temperature and air intake temperature satisfy requirement 1 (engine stopped).

*2: Monitor preparation period; Start the engine, and accelerate to 89 - 97 km/h (55 - 60 mph).

For this period, acceleration, deceleration, or braking may be carried out.

Continue driving between 89 and 97 km/h (55 and 60 mph) for 200 seconds or more. For this period, braking or throttle operation may be carried out if vehicle speed is within the specified value.

+3:Drive between 89 and 97 km/h (55 and 60 mph) at a constant throttle angle (by not moving the throttle pedal as much as possible) for 150 seconds or more during monitor. Moreover, do not turn the steering wheel suddenly.

*4: Decelerate and stop the vehicle. After stop, turn off the ignition switch.

Drive cycle pattern

n

-

97 (60)

-

Vehicle speed 64 (40) km/h (mph)

-

32 (20)

*1

- H I I I I I I

0

I I Ignition switch: OFF t Engine start

I I t

I

I I

I 1 k-----l I I

100

<Reference> Throttle angle (%) 50

I I I

0

Caution Drive within the shaded area in the graph above.

7FU1957

Heated oxygen sensor monitor (PO1 30, PO1 36) Test req ui rementdproced ure

1. Test requirements/procedure

(1) Engine coolant temperature: 80°C (176°F) or more (Engine fully warmed up) (2) Atmospheric temperature: -1 0°C (1 4" F) or more (3) Condition of A/T:

0 Selector lever position: D range

2. One trip monitor will be completed by driving according to the steps below (from start to switch off).

It will take 5 minutes.

*1: After warming up the engine, turn off the ignition switch.

*2: Start the engine, and accelerate to 56 - 64 km/h (35 - 40 mph).

+3: Drive between 56 and 64 km/h (35 and 40 mph) at a constant throttle angle (by not moving

the throttle pedal as much as possible) for 120 seconds or more during monitor. Moreover, do not turn the steering wheel suddenly.

*4: Decelerate and stop the vehicle. Then turn off the ignition switch.

Drive cycle pattern

120 sec. or more 56 - 64 km/h (35 - 40 mph) , MR4thsDeed I

(40) 64 1 Vehicle speed km/h (mph)

I-

- 1

During monitor

I I I t I Ignition switch:

t i Engine start I I I I I I I r I I

0

100

<Reference> Throttle opening angle (%)

50

I U I I I I

0

Caution Vehicle speed and throttle opening angle should be within the shaded rage.

OFF

7FU1958

*

Exhaust gas recirculation (EGR) system monitor (P0400) Test requ i rements/proced ure

1. All of the following requirements should be met when carrying out a drive test.

(1) Engine coolant temperature: 80°C (176°F) or more (Engine fully warmed up) (2) Atmospheric temperature: 5°C (41°F) or more (3) Condition of A/T

0 Selector lever position: D range

(4) A/C switch: OFF

2. One trip monitor will be completed by driving according to the steps below (from start to switch off).

It will take approx. 10 minutes.

' *l: After warming up, turn off the ignition switch.

~ 2 :

Start the engine, and accelerate to 56 - 64 km/h (35 - 40 mph).

+3: Close the throttle fully from 2000 - 3000 r/min with the clutch engaged cM/T>, and then decelerate to 900 r/min without applying brakes. Moreover, do not turn the steering wheel or switch on or off the lights.

*4: Accelerate to 56 - 64 km/h (35 - 40 mph), and continue driving for 20 seconds. (After 1st monitor (deceleration), wait for 20 seconds or more until the next monitor (deceleration) starts). Then repeat +3 and *4 steps eight times.

*5: Decelerate and stop. Then turn off the ignition switch.

Drive cycle pattern

56 - 64 km/h (35 - 40 mph)

I MTT. 4th speed 2o set. or +3: Do not decelerate suddenly.

I l 
- I I I 1 I I I I I I 1 I I I I 1 I I

I I I I / I 1

100 -

<Reference> Throttle opening 50 - angle (%)

0 -

Full Full Full Full decel- decel- decel- decel- eration eration eration eration

Caution Vehicle speed should be within the shaded rage.

v 7th monitqr I

v=\ monit+

\I

I I I I t

I I

I I I I I 1 Full decel-

I Ignition I switch: OFF

Full 7FU1959 decel- eration

eration

MFI <I

Fuel trim monitor (P0170) Test requirements/procedure

1. All of the following requirements should be met when carrying out a drive test.

(1) Engine coolant temperature: 80°C - 97°C (176 - 207°F) (Engine fully warmed up) (2) Atmospheric temperature: -10°C (14°F) or more, 60°C (140°F) or less (3) Condition of Am

0 Selector lever position: D range

2. One trip monitor will be completed by driving according to the steps below (from start to switch off).

It will take 35 minutes.

*l:

After warming up the engine, turn off the ignition switch.

*2: Start the engine, and accelerate to 89 - 97 km/h (55 - 60 mph).

+3: Drive between 89 and 97 km/h (55 and 60 mph) for 30 minutes or more during monitor. Moreover,

do not drive the vehicle at the constant speed range for 120 seconds or more. (Accelerate or decelerate lightly within the 120 seconds. Brake may be applied, but avoid decelerating or accelerating suddenly).

*4: Decelerate and stop the vehicle. Then turn off the ignition switch.

Drive cycle pattern

30 min. or more 89 - 97 km/h (55 - 60 rnph) M/T: 5th speed I

Vehicle speed km/h (mph)

<Reference> Throttle opening angle (%)

O '

-

Caution Vehicle speed and throttle opening angle should be within the shaded rage.

OFF

7FU1960

Other

monitors Misfire (P0300, P0301, P0302, P0303, P0304) Evaporative emission control system (P0440) Idle air control system (P0505) Excessive time to enter closed loop fuel control (PO1 25) Throttle position sensor (PO1 20) Manifold absolute pressure circuit malfunction (PO1 05) Intake air temperature sensor (PO1 10) Serial communication link <A/T> (P1600) Crankshaft position sensor (P0335) Camshaft position sensor (P0340)

0

0

0 0

0 0

0 0 0 0

Test requirements/procedure

1. All of the following requirements should be met when carrying out a drive test.

(1) Engine coolant temperature: 80°C (176°F) or more (Engine fully warmed up) (2) Atmospheric temperature: 5°C (41°F) or more

- (3) Condition of A/T:

0 Selector lever position: D range

2. One trip monitor will be completed by driving according to the steps below (from start to switch off).

It will take approx. 10 minutes.

*l:

After warming up, turn off the ignition switch.

*2: Start the engine, accelerate to 56 - 64 km/h (35 - 40 mph), continue driving for 300 seconds or more at that speed range and stop. Moreover, brake or throttle may be applied for this period.

*3: After stopping the vehicle, continue idling for 300 seconds or more, and then turn off the ignition switch. Moreover, the vehicle should be set to the following conditions for idling.

N C switch: OFF 0 Lights, electric cooling fan and all accessories: OFF 0 Transaxle: Neutral (A/T for P range) 0 Steering wheel: Straight-forward position

Engine coolant temperature sensor (PO1 15) Closed throttle position switch (PO51 0) Generator FR terminal circuit (P1500) 0 2 sensor circuit (P0130, P0136) 0 2 sensor heater circuit (P0135, P0141) EGR solenoid (P0403) Evaporative emission purge solenoid (P0443) Injector circuit (P0201, P0202, P0203, P0204) Evaporative emission ventilation solenoid (P0446)

0

0

0

Drive cycle pattern

4 D

*2

(40)

Vehicle speed km/h (mph)

300 sec.

- transaxle: Neutral

32 (20)

<Reference> Throttle opening angle (“h)

c NOTE Drive according to the graph above.

Idling

4 *

*3

READINESS TEST STATUS The ECM monitors the following main diagnosis items and records whether the evaluation passing or failing in the past.

These records can be read with a scan tool. (When using MUT-11, “Complete” will appear to indicate that the evaluation has been completed.) These records will all be reset if the battery terminal is disconnected or the DTC are erased, etc.

To complete the readiness test statu3 which has been reset, the “OBD-I1 Drive Cycle” related to a diagnosis item should be carried out.

NOTE If the vehicle is normal, the readiness test status will be complete by carrying out the “OBD-11 Drive Cycle” once. If the ECM detects a malfunction of the vehicle, the readiness test status will be complete by carrying out the “OBD-I1 Drive Cycle” twice. In addition, after all readiness test status are complete, a DTC should be interrogated. If a DTC is stored, perform repair by referring to the relevant DTC procedures.

Then complete the readiness test status by repeating the “OBD-I1 Drive Cycle”. If a DTC is not stored, no further action will be needed.

0 Catalyst: P0420, PO421 Evaporative system: P0442, PO455 0

Heated oxygen sensor: P0130, PO136 Heated oxygen sensor heater: P0135, PO141

0 EGR system: PO400

HOW TO READ AND ERASE DIAGNOSTIC TROUBLE CODES Caution

1. If battery voltage is low, diagnostic trouble codes may not be output. Be sure to check the battery and charging system before continuing.

2. If the battery is disconnected or if the engine control module connector is disconnected, the diagnostic trouble code memory will be erased. Do not discon- nect the battery or engine control module until after the diagnostic trouble codes are recorded.

3. Turn the ignition switch off before connecting or dis- connecting the scan tool.

NOTE If a DTC is erased, its “freeze frame” data will be also erased and the readiness test status will be reset. If necessary, take a note of the “freeze frame” data before erasing the DTC.

1. Connect the scan tool to the data link connector, and read the diagnostic trouble codes.

2. Repair the malfunction while referring to the INSPECTION CHART FOR DIAGNOSTIC TROUBLE CODES.

3. Turn the ignition switch to OFF and then back to ON again.

4. Erase the diagnostic trouble codes using the scan tool.

5. Confirm that the diagnostic trouble code reading is normal.

I /

- AOOM0053

PROVISIONAL DTCs [MUT-I1 OBD-I1 Test Mode - Results (Mode 5)] MUT-I1 will display the Provisional DTCs reported by ECM if the ECM detects some malfunction for “Misfire”, “Fuel System” and “Comprehensive” monitoring during a SINGLE Driving Cycle.

The intended use of this data is to assist the technician after a vehicle repair, and after clearing diagnostic information, by reporting test result after a SINGLE Driving Cycle.

Note that the test results reported by this mode do not necessarily indicate a faulty component/system. If test results indicate a failure after ADDITIONAL (consecutive) driving, then the MIL will be illuminated and a DTC will set.

DIAGNOSTIC BY DIAGNOSTIC TEST MODE I1 (INCREASED SENSITIVITY) When mode I1 is selected with MUT-11, the Service Engine Soon/Malfunction Indicator Lamp will light when the ECM first detects the trouble. (Note that this is only for engine related trouble.) At the same time, the relevant diagnostic trouble codes will be registered.

In respect to the comprehensive component electrical faults (opens/shorts), the time for the DTC to be registered after the fault occurrence is shortened (4 sec. + 1 sec.) With this, the confirmation of the trouble symptom and the confirmation after completing repairs can be reduced.

To return to the normal mode I after mode I1 has been selected once, the ignition switch must be turned OFF once or mode I must be reselected with the MUT-11. The DTC, readiness test status and freeze frame data, etc., will be erased when mode I is returned to, so record these if necessary.

(1) Using the scan tool, changeover the diagnostic test mode of the engine control module to DIAGNOSTIC TEST MODE 11. (INCREASED SENSITIVITY) (2) Road test the vehicle.

‘

(3) Read the diagnostic trouble code in the same manner as “READ OUT OF DIAGNOSTIC TROUBLE CODE” and repair the malfunctioning part.

(4) Turn OFF the ignition switch to change the ECM from the diagnostic test mode I1 to the diagnostic test mode I.

NOTE Turning OFF the ignition switch will cause the ECM to changeover from the diagnostic test mode I1 to diagnostic test mode I.

INSPECTION USING SCAN TOOL DATA LIST AND ACTUA- TOR TESTING

1. Carry out inspection by means of the data list and the actuator test function.

If there is an abnormality, check and repair the chassis harnesses and components.

2. After repairing, re-check using the scan tool and check to be sure that the abnormal input and output have re- turned to normal as a result of the repairs.

3. Erase the diagnostic trouble code@).

4.

Remove the scan tool.

5. Start the engine again and road test to confirm that the problem is eliminated.

NOTE Refer to P.13A-122 for Data list.

Refer to P.13A-127 for Actuator tests.

/ A O O M 0 0 5 3

FA1 L-SAFE/BACKUP FUNCTION TABLE 131 OO910206

- When the main sensor malfunctions are detected by the diagnostic test mode, the vehicle is controlled by means of the following defaults.

Intake air temperature I--- sensor

Control contents during malfunction

Malfunctioning item

Uses the throttle position sensor signal and engine speed signal (crankshaft pasition sensor signal) for basic injector drive time and basic ignition timing from the pre-set mapping.

Fixes the IAC motor in the appointed position so idle air control is not performed.

Manifold absolute pressure sensor

1.

2.

Controls as if the intake air temperature is 25°C (77°F).

Throttle position sensor (TPS) tion sensor signal.

No increase in fuel injection amount during acceleration due to the unreliable throttle posi-

Controls as if the engine coolant temperature is 80°C (176°F).

Engine coolant temperature sensor

Camshaft position I sensor

Injects fuel into the cylinders in the order 1-3-4-2 with irregulartiming. (After the ignition switch is turned to ON, the No. 1 cylinder top dead center is not detected at all.)

Heated oxygen I sensor <front> I Air/fuel ratio closed loop control is not performed

Heated oxygen sensor <rear>

Performs the closed loop control of the air/fuel ratio by using only the signal of the heated oxygen sensor (front) installed on the front side of the catalytic converter.

Generator FR terminal

No generator output suppression control is performed for the electrical

I Misfire detection The ECM stops supplying fuel to the cylinder with the highest misfiring rate if a misfiring that could damage the catalytic converter is detected.

INSPECTION CHART FOR DIAGNOSTIC TROUBLE CODES (FAULT TREE) 13100870740

Memory Check items (Remedy) Reference Page

DTC No.

Diagnostic items

Retained PO

05 Manifold Absolute Pressure Circuit Malfunction 0 Harness and connector (If harness and connector are normal, replace manifold absolute pressure sensor assembly.)

- PO 10 0 Harness and connector 0 Intake air temperature sensor Retained Intake Air Temperature Circuit Malfunction

- ~ 0 Harness and connector 0 Engine coolant temperature sensor

Retained PO1 15

Engine Coolant Temperature Circuit Malfunction

PO1 20 Throttle Position Circuit Malfunction Retained 1 3A-3 1 0 Harness and connector 0 Throttle position sensor 0 Closed throttle position switch

Retained PO1 25 Excessive Time to Enter Closed Loop Fuel Control*

0 0 2 sensor (front) 0 0 2 sensor harness and

0 Injector connector

PO1 30 0 2 Sensor Circuit Malfunction (Sensor 1) 0 Harness and connector [If harness and connector are normal, replace 0 2 sensor (front) .]

0 Harness and connector 0 0 2 sensor (front) heater Retained

PO1 35 0 2 Sensor Heater Circuit Malfunction (Sensor 1)

PO1 36 0 2 Sensor Circuit Malfunction (Sensor 2) 0 Harness and connector 0 O2 sensor (rear) Retained

0 Harness and connector 0 O2 sensor (rear) heater Retained PO1 41

0 2 Sensor Heater Circuit Malfunction (Sensor 2)

PO1 70 Fuel Trim Malfunction Injector Fuel pressure Intake air leaks Engine coolant temperature sensor Intake air temperature sensor Manifold absolute pressure sensor 0 2 Sensor Exhaust manifold cracks

PO201 Injector Circuit Malfunction - Cylinder 1 0 Harness and connector 0 Injector Retained

PO202 Injector Circuit Malfunction - Cylinder 2

PO203 Injector Circuit Malfunction - Cylinder 3

Injector Circuit Malfunction - Cylinder 4 PO204

Retained

Retained

* 1344-25

Memory Reference Page DTC No.

Check items (Remedy) Diagnostic items

Ignition coil Ignition power transistor Spark plug Ignition circuit Injector 0 2 Sensor Compression Timing belt Crankshaft position sensor Air intake Fuel pressure Crankshaft position sensor circuit and connector

PO300 Random Misfire Detected 0 0 0 0 0 0 0 0 0 0 0 0

PO301 Cylinder 1 Misfire Detected 0 0 0 0 0 0 0 0 0 0 0 0

Ignition coil Ignition power transistor Spark plug Ignition circuit Injector 0 2 Sensor Compression Timing belt Crankshaft position sensor Air intake Fuel pressure Crankshaft position sensor circuit and connector

PO302 Cylinder 2 Misfire Detected

PO303 Cylinder 3 Misfire Detected

PO304 Cylinder 4 Misfire Detected

~ 0

Retained PO335 Crankshaft Position Sensor Circuit Malfunction

Harness and connector (If harness and connector are normal, replace crankshaft position sensor.)

PO340 Camshaft Position Sensor Circuit Malfunction 0 Harness and connector (if harness and connector are normal, replace camshaft position sensor.)

L / 0 Harness and connector 0 EGR valve 0 EGR solenoid 0 EGR valve control vacuum 0 Manifold absolute pressure sensor

Retained PO400 Exhaust Gas Recirculation Flow Malfunction

PO403 Exhaust Gas Recirculation Solenoid Malfunction 0 Harness and connector 0 EGR solenoid Retained

Retained PO420 Catalyst Efficiency Below Threshold <Federal >

0 Exhaust manifold (Replace the catalytic converter if there is no cracks, etc.)

Retained PO42 1 Warm Up Catalyst Efficiency Below Threshold <California>

0 Exhaust manifold (Replace the catalytic converter if there is no cracks, etc.)

PO442 Evaporative Emission Control System Leak Detected 0 Harness and connector 0 Evaporative emission purge

solenoid

0 Evaporative emission ventilation

solenoid

0 Vacuum hoses routing

Retained

Retained

Retained

Retained

Retained I PO443 Evaporative Emission Control System Purge Control Valve Circuit Malfunc- tion I

~ Diagnostic items Reference Page

Check items (Remedy)

0 Harness and connector 0 Evaporative emission purge solenoid

Evaporative Emission Control System Vent Control Malfunction 0 Harness and connector 0 Evaporative emission ventilation solenoid

Retained PO446

Evaporative Emission Control System Pressure Sensor Malfunction 0 Harness and connector 0 Fuel tank differential pressure sensor

PO450

Evaporative Emission Control System Leak Detected (Gross Leak) 0 Harness and connector 0 Evaporative emission ventilation solenoid

PO455

Vehicle Speed Sensor Malfunction 0 Harness and connector 0 Vehicle speed sensor Retained

PO500

Idle Control System Malfunction 0 Harness connector 0 Idle air control motor Retained

PO505

Closed Throttle Position Switch Mal- function 0 Harness and connector 0 Closed throttle position switch Retained

PO510

0 Harness and connector 0 Power steering pressure switch Retained Power Steering Pressure Sensor Circuit Range/Performance

Transmission Range Sensor Circuit Malfunction (PRND2L Input) 0 Harness and connector 0 Park/Neutral position switch Retained 13A-a4

Retained PO71 0

Transmission Fluid Temperature Sen- sor Circuit Malfunction 0 Harness and connector 0 Transaxle fluid temperature sensor

lnputlturbine Speed Sensor Circuit Malfunction 0 Harness and connector 0 Pulse generator Retained

PO71 5

Output Speed Sensor Circuit Malfunction 0 Harness and connector 0 Pulse generator Retained 13A-as

PO720

Engine Speed Input Circuit Malfunction 0 Harness and connector Retained

PO725

0 Harness and connector 0 Torque converter clutch solenoid Retained Torque Converter Clutch System Malfunction

PO740

Shift Solenoid A Malfunction 0 Harness and connector 0 Low-reverse solenoid Retained

PO750

Shift Solenoid 6 Malfunction 0 Harness and connector 0 Underdrive solenoid Retained

PO755

Shift Solenoid C Malfunction 0 Harness and connector 0 Second solenoid Retained

PO760

Shift Solenoid D Malfunction 0 Harness and connector 0 Overdrive solenoid Retained i 3 ~ - a 6

PO765

Generator FR Terminal Circuit Mal- function 0 Harness and connector Retained

P1500

Serial communication link malfunction 0 Harness and connector Retained i 3 ~ - 8 a

P1600

P1720

Vehicle Speed Sensor Signal Line Malfunction 0 Harness and connector Retained

A n Control Relay Malfunction 0 Harness and connector 0 AD control relay Retained

P1751

Memory

Retained

Retained 1 3A-7 1

DTC No.

Diagnostic items

Check items (Remedy) Memory Reference

0 Harness and connector Retained Page

P1795 Throttle Position Input Circuit Malfunction

NOTE 1.

Do not replace the engine control module (ECM) until a thorough terminal check reveals there are no short/open circuits.

After the ECM detects a malfunction, a diagnostic trouble code is recorded the next time the engine started and the same malfunction is re-detected. However, for items marked with a ‘‘JC”, the diagnostic trouble code is recorded on the first detection of the malfunction.

0 2 : Heated oxygen sensor Sensor 1 : indicates sensors which are mounted closest to the engine.

Sensor 2 : indicates sensors which are mounted next-closest to the engine.

2.

3.

4.

5.

INSPECTION PROCEDURE FOR DIAGNOSTIC TROUBLE CODES

Code No.PO105 Manifold Absolute Pressure Circuit Malfunction

Background 0 The manifold absolute pressure sensor outputs a voltage which corresponds to the intake manifold plenum pressure 0 The engine control module checks whether this voltage is within a specified range Check Area

Ignition Switch ON Judgment Criteria 0 Sensor output voltage has continued to be 4 5 V or higher [corresponding to an absolute pressure of 115 kPa (17 psi) or higher] or higher for 2 sec.

Check Area 0 Throttle position sensor voltage is not lower than 1 25 V, or 0 Engine speed is not higher than 4000 r/min Judgment Criteria

Sensor output voltage has continued to be 0 2 V or lower [corresponding to an absolute pressure of 4 9 kPa (0 7 psi) or lower] for 2 sec Check Area 0 Throttle position sensor voltage is 0 8 V or lower

Engine speed is not higher than 2000 r/min Judgment Criteria 0 Sensor output voltage is 4 V or more for 2 seconds Check Area 0 Throttle position sensor voltage is 3 5 V or more.

Engine speed is 2000 r/min or more Judgment Criteria

Sensor output voltage is 1 1 V or less for 2 seconds

-

JG

Measure at the manifold absolute pressure sensor connector A-49.

0 Disconnect the con- nector, and measure at the harness side.

Voltage between 3 and ground (ignition switch: ON)

Measure at the manifold absolute pressure sensor connector A-49.

Measure with the connector connected.

(Use the test harness:

M6991348)

0 Voltage between 1 and ground (Engine:

Idling)

between the ECM and manifold absolute pres- sure sensor connector 1 OK

OK: 4.8 - 5.2 V

OK. 0 9 - 1.5V

0 Continuity between 2 and ground OK: Continuitv

0 Voltage between 1 and ground O K If the accelera- tor pedal is de- pressed sud- denly from idle speed, the volt- age increases momentarily from 0.9 - 1.5 V.

NG + Repair 1

connector: A-49

NG Check trouble svmdom.

c , .

rlG --

Measure at the ECM con- nector. 6-37.

0 Measure with the connector connected.

0 Voltage between 85 and ground (Engine:

idling) OK: 0.9 - 1.5 V

Check the harness wire between the ECM and manifold absolute pres- sure sensor connector, and repair if necessary.

Check trouble symptom.

Replace the ECM.

Probable cause

0 Manifold absolute pressure sensor failed 0 Open or shorted manifold absolute pressure sensor circuit, or loose connector.

0 Engine control module failed.

Check the following

- Repair connector: B-37

1 Check trouble symptom. I

+ Repair

Eeplace the ECM.

Check the harness wire between the ECM and manifold absolute pres- sure sensor connector.

+ Repair

!OK Check the manifoldabso- lute pressure hose be- tween the manifold abso- lute pressure sensor and intake manifold plenum.

NG

+ Repair

*

Code No. PO110 intake Air Temperature Circuit Malfunction

Background 0 The intake air temperature sensor converts the intake air temperature to a voltage and outputs it 0 The engine control module checks whether the voltage is within a specified range.

Check Area 0 2 sec or more have passed since the starting sequence was completed Judgment Criteria 0 Sensor output voltage has continued to be 4.6 V or higher [corresponding to an intake air temperature of -45°C (-49°F) or lower] for 2 sec, or 0 Sensor output voltage has continued to be 0 2 V or lower [corresponding to an intake air temperature of 125°C (257°F) or higher] for 2 sec.

Replace the intake air tem- perature

Measure at the intake air temperature sensor connector A-43 0 Disconnect the connector, and measure at the harness side.

0 Voltage between 1 and ground ' (Ignition switch: ON) OK: 4.5-4.9 V 0 Continuity between 2 and ground OK: Continuity ECM and the intake air temperature sensor connector.

Check the following connector:

Repair A 4 3

Replace the ECM.

I Check trouble symptom.

NG

1 Reolace the ECM.

Probable cause

0 Intake air temperature sensor failed 0 Open or shorted intake air temperature sensor circuit, or loose connector 0 Engine control module failed

Code No. PO115 Engine Coolant Temperature Circuit Malfunction

Background 0 The engine coolant temperature sensor converts the engine coolant temperature to a voltage and outputs it 0 The engine control module checks whether the voltage IS within a specified range In addition, it checks that the engine coolant temperature (signal) does not drop while the engine is warming up Check Area At least 2 seconds have passed since the ignition switch was turned on or the starting sequence was completed Judgment Criteria 0 Sensor output voltage has continued to be 4 6 V or higher [corresponding to a coolant temperature of -45°C (-49°F) or lower] for 2 sec, or 0 Sensor output voltage has continued to be 0 1 V or lower [corresponding to a coolant temperature of 140°C (284'F) or higher] for 2 sec Check Area Judgment Criteria 0 Sensor output voltage increased from a value lower than 1 6 V to a value higher than 1 6 V [Coolant temperature decreases from a higher than 40°C (104°F) temperature to a lower than 40°C (104°F) temperature.] 0 then the sensor output voltage has continued to be 1 6 V or higher for 5 min Check Area Judgment Criteria 0 About 60 - 300 sec have passed for the engine coolant temperature to rise to about 40°C (104°F) after starting sequence was completed 0 However, time is not counted when fuel is shut off Check Area 0 Engine coolant temperature was 20°C (68°F) <Federal> or 7°C (446°F) <California> or more immediately before the engine was stopped at the last drive 0 Engine coolanttemperatureis 20°C (68°F) <Federal>or 7°C (44 6°F) <California> or more when the engine is started Judgement Criteria 0 Engine coolant temperature fluctuates within 1 "C (1 8°F) after 5 minutes have passed since the engine was started 0 However, time is not counted in any of the following conditions (1) Intake air temperature is 60°C (140°F) or higher (2) Engine speed is 1,500 r/min or higher (3) Intake manifold pressure is 40 kPa (5 8 psi) or lower (4) During fuel shut-off operation.

0 Monitored only once per trip

NG * Replace sensor. (Refer to P.13A-152.)

OK I Measure at the engine coolant temperature sensor connector A-60.

0 Disconnect the connector, and measure at the harness side.

Voltage between 1 and ground (Ignition switch. ON) OK: 4.5-4.9 V 0 Continuity between 2 and ground OK: Continuity !

OK

L 
- Check the following connector: 8-37

Repair i OK

I o t r o u b l e p t o m .

ECM and the engine coolant tempera- ture sensor connector.

~ ~ _ _ _

Check trouble symptom.

Replace the ECM.

Probable cause

Engine coolant temperature sensor failed Open or shorted engine coolant temperature sensor circuit, or loose connector Engine control module failed

Code No. PO120 Throttle Position Circuit Malfunction

~ ~~ Background 0 The throttle position sensor outputs a voltage which is proportional to the throttle valve opening angle 0 The engine control module checks whetherthe voltageoutput by the throttle position sensor is within a specified range In addition, it checks that the voltage output does not become too large while the engine is idling Check Area

At least 2 seconds have passed since the engine was started.

Judgment Criteria 0 With the close throttle position switch set to ON, the sensor output voltage has continued to be 2 V or higher for 2 sec, or 0 Sensor output voltage has continued to be 0 2 V or lower for 2 sec Check Area 0 At least 2 seconds have passed since the engine was started 0 Engine speed is 3000 r/min or less.

0 Intake air pipe pressure is 48 kPa (7 0 psi) or less.

Judgment Criteria 0 Sensor output voltage has continued to be 4.6 V or higher for 2 sec Check Area 0 At least 2 seconds have passed since the engine was started.

0 Engine speed is 2000 r/min or more 0 Intake air pipe pressure is 53 kPa (7.7 psi) or more Judgment Criteria 0 Sensor output voltage is 0 8 V or less for 2 seconds.

switch system

26 Closed throttle position switch system (Refer to P 13A-109, INSPECTION OK: With the throttle valve at the idle position: ON With the throttle valve slightly open OFF

Replace (Refer to P13A-153.)

Measure at the throttle position sensor connector A-52.

Disconnect the connector. and I measure at the harness side.

I I 0 Voltage between 1 and ground (Ignition switch ON) OK: 4.8-5.2 V 0 Continuity between 4 and ground OK: Continuitv

t I Check trouble symptom

ECM and the throttle position sensor

Check the throttle position sensor output circuit. (Refer to P.13A-120, IN- SPECTION PROCEDURE 47.)

I Replace the ECM.

1

Probable cause

0 Throttle position sensor failed or misadlusted 0 Openor shortedthrottlepositionsensorcircuit, or loose connector Closed throttle position switch malfunction 0 Closed throttle position switch signal wire shorted

0 Engine control module failed

Repair

Repair

Code No. PO125 Excessive Time to Enter Closed Loop Fuel Control

Background 0 The MFI system reduces exhaust emissions by means of closed-loop fuel control 0 The engine control module checks the time taken until closed-loop fuel control commences Check Area 0 At least 2 seconds have passed since the engine was started 0 Engine coolant temperature is higher than 80°C (176°F) 0 Engine speed is at between about 1,800 and 4,000 r/min

Intake air pipe pressure is 24 kPa (3 5 psi) - 77 kPa (11 psi) 0 Engine operating within the air-fuel ratio feedback zone 0 Monitoring time 30 sec Judgment Criteria 0 Multiport fuel injection system doesn’t enter the closed loop control within about 30 sec 0 Monitored only once per trip

j h t h e h e a t e d oxygen sensor (front). ( R

- 1 NG

t Replace _ ~ _ _ _ _

OK NG

1 Check the Injector (Refer to P.13A-155.)

---+ Repair

I O K I NG Check the harness wire between the ECM and the injectorconnec- tor.

Repair

OK

Check the fuel pressure (Refer to P.13A-144.) l°K Check intake system vacuum leak 0 Check for exhaust leaks (oxygen sensor installation section, cracks in exhaust manifold, cracks in front pipe, etc ) 0 Check for clogging of the fuel filter and fuel line.

Check the fuel pump (insufficient discharge rate).

Replace the ECM.

- ~~

Probable cause

0 Heated oxygen sensor failed 0 Injector failed 0 Fuel pressure regulator failed 0 Fuel pump failed 0 Fuel filter is clogged 0 Intake system vacuum leak 0 Exhaust leak 0 Engine control module failed .

Repair

- Replace

Code No. PO130 Heated Oxygen Sensor Circuit Malfunc- tion (Sensor 1)

Background 0 When the heated oxygen sensor begins to deteriorate, the oxygen sensor signal response becomes poor 0 The engine control module forcibly varies the air/fuel mixture to make it leaner and richer and checks the response speed of the heated oxygen sensor.

In addition, the engine control module also checks for an open circuit in the heated oxygen sensor output line.

Check Area 0 Coolant temperature sensor normal 0 Heated oxygen sensor signal voltage has continued to be 0 2 V or lower for 3 min or more after the starting sequence was completed 0 Engine coolant temperature is higher than 80°C (176°F).

0 Engine speed is higher than 1200 rlmin

Intake air pressure is not lower than 40 kPa (5 8 psi)

0 Monitoring time 7 seconds 0 Volumetric efficiencbt 1s not lower than 25% Judgment Criteria 0 Input voltage supplied to the engine control module interface circuit is not lower than 4 5 V when 5 V is applied to the heated oxygen sensor output line via a resistor 0 Monitored only once per trip Check Area 0 Engine coolant temperature is not lower than 50°C (122°F) 0 Engine speed is between 1600 and 3000 rimin cM/T> or 1400 and 3200 r/rnin <A/T> 0 Intake air pipe pressure is 27 kPa (3 9 psi) - 67 kPa (9 8 psi) 0 Intake air temperature is -10°C (14°F) or more 0 Under the closed loop air-fuel control 0 Vehicle speed is 30 km/h (18 7 mph) or higher 0 Throttle valve opening angle (TPS output voltage) fluctuates within 0 11 7 V every 250 milliseconds 0 Monitoring Time 5 - 20 sec Judgment Criteria 0 When the air-fuel ratio is forcibly changed (lean to rich and rich to lean), the heated oxygen sensor signal doesn’t provide response within 1 2 sec or 0 The heated oxygen sensor sends ‘’lean’’ and “rich signals alternately nine times or less for ten seconds Monitored only three times per trip

NOTE If the sensor switch time is longer than the Judgment Criteria due to the MUT-I1 OBD-I1 test Mode - H02S Test Results, it is assumed that the heated oxygen sensor has deteriorated If it is short, it is assumed that the harness wire is broken or has a short circuit If the heated oxygen sensor signal voltage has not changed even once (lean/rich) after the DTC was erased, the sensor switch time will display as 0 seconds

_- \ (front). (Refer to P 13A-154.) NG OK

Replace Check trouble symptom.

Repair ECM and the heated oxygen sensor

Replace the oxygen sensor (front).

1 Check trouble symptom.

lNG

1 Replace the ECM.

I

Probable cause

0 Heated oxygen sensor deteriorated 0 Open circuit in heated oxygen sensor output line 0 Engine control module failed

Code No. PO135 Heated Oxygen Sensor Heater Circuit Malfunction (Sensor 1)

Background 0 The engine control module checks whether the heater current is within a specified range when the heater is energized Check Area 0 Engine coolant temperature is 2OoC (68°F) or higher.

0 The heated oxygen sensor heater is on 0 Battery voltage is between 11 and 16 V Judgment Criteria 0 Heater current of the front heated oxygen sensor heater (Sensor 1) has continued to be lower than 0.2 A or higher than 3.5 A for 6 sec 0 Monitored only once per trip.

NG Measure at the heated oxvgen sensor Check the harness wire between the 1 (front) connectors A-67, A-83.

0 Disconnect the connector, and measure at the harness side 0 Voltage between 1 and ground

heated oxygen sensor (front) and the MFI relay connector. Repair, if neces-

NG + Check the following connectors:

* Repair A-67. A-83

measure at the harness side 0 Voltage between 60 and ground (Ignition switch: ON) OK: Battery positive voltage

Check trouble symptom.

IoK

ECM and the heated oxygen sensor

f I i NG Check the following connector:

B-38

+ Repair

I Check trouble svmDtom.

I

Probable cause

0 Open or shorted oxygen sensor heater circuit 0 Open circuit in oxygen sensor heater 0 Engine control module failed

Code No. PO136 Heated Oxygen Sensor Circuit Malfunc- tion (Sensor 2)

Background 0 The engine controls module checks for an open circuit in the heated oxygen sensor output line Check Area 0 Coolant temperature sensor: normal 0 Heated oxygen sensor signal voltage has continued to be 0 1 V or lower for 3 min or more after the starting sequence was completed 0 Engine coolant temperature is not lower than 80°C (176°F) 0 Engine speed is higher than 1200 r/min 0 Intake air pressure is not lower than -40 kPa (-5 8 psi).

0 Monitoring time 7 sec Judgment Criteria 0 Input voltage supplied to the engine control module interface circuit is not lower than 4 5 V when 5 V is applied to the heated oxygen sensor output line via a resistor 0 Monitored only once per trip Check Area 0 Oxygen sensor signal voltage has been 0 1 V or less for 3 minutes after the engine was started 0 Engine coolant temperature is about 80°C (176°F) or higher.

0 Engine speed is about 1,200 rpm or higher 0 Intake manifold pressure is 40 kPa (5 8 psi) or higher 0 At least 20 seconds have passed since fuel shut-off control was released 0 Oxygen sensor (front) output voltage is 0 5 V or higher.

0 Monitoring time 10 seconds Judgement Criteria 0 Making the air-fuel ratio 15% richer doesn't result in raising the heated oxygen sensor output voltage beyond 0 1 V.

Monitored once per trip Check Area 0 Engine coolant temperature is about 80°C (176'F) or more 0 The heated oxygen sensor (front) is operating.

0 The engine runs for at least ten seconds when air-fuel ratio is rich 0 The heated oxygen sensor (rear) output voltage is 0 4 V or higher before fuel shut-off commences 0 While fuel is being shut off Judgment Criteria 0 At least 1 second has passed before heated oxygen sensor (rear) output voltage falls to 0 15 - 0 40 V or 0 At least 3 seconds have passed before the heated oxygen sensor (rear) output voltage falls to 0 15 V or less

OK Check the heatedoxygen sensor (rear).

(Refer to P.13A-154.) c Repair A-67. A-83. B-37 1"" Replace Check trouble symptom.

Repair ECM and the heated oxygen sensor

Replace the heated oxygen sensor

Check trouble symptom.

Replace the ECM.

Probable cause

0 Heated oxygen sensor failed 0 Open circuit in heated oxygen sensor output line 0 Engine control module failed

Code No. PO141 Heated Oxygen Sensor Heater Circuit Malfunction (Sensor 2)

Background 0 The engine control module checks whether the heater current is within a specified range when the heater is energized Check Area 0 Engine coolant temperature is 20°C (68°F) or more.

0 The heated oxygen sensor heater is on 0 Battery voltage is between 11 and 16 V Judgment Criteria 0 Heater current of the front heated oxygen sensor heater (Sensor 2) has continued to be lower than 0.2 A or higher than 3 5 A for 6 sec.

0 Monitored only once per trip

NG - Replace

r- Check the heatedoxygen sensor (rear).

(Refer to P.13A-154.) i°K Measure at the heated oxygen sensor (rear) connectors A-83, 8-45.

0 Disconnect the connector, and measure at the harness side.

<Federal> 0 Voltage between 3 and ground (Ignition switch: ON) OK: Battery positive voltage <California> 0 Voltage between 1 and ground (Ignition switch: ON) OK: Battery positive voltage

heated oxygen sensor (rear) and the MFI relay connector. Repair, if neces-

I I OK

Disconnect the connector, and A-83, B-45 measure at the harness side.

0 Voltage between 54 and ground (Ignition switch. ON) OK: Battery positive voltage I Check trouble symptom.

I N G

Check the harness wire between the ECM and the heated oxygen sensor

4 Repair

B-38

Check trouble symptom.

Replace the ECM.

~

Probable cause

0 Open or shorted oxygen sensor heater circuit 0 Open circuit in oxygen sensor heater 0 Engine control module failed

--t Repair

Code No. PO170 Fuel Trim Malfunction ~ ~ _ _ _ _ ~ ~ _ _ _ _ _ Background 0 If a malfunction occurs in the fuel system, the fuel trim value becomes too large or too small The engine control module checks whether the fuel trim value is within a specified range.

Check Area

Under the closed loop air-fuel ratio control 0 Engine coolant temperature is -10°C (14°F) or higher 0 Intake air temperature -10°C (14°F) or more Intake manifold pressure is 48 kPa (7 0 psi) or higher Judgment Criteria

Long-range fuel correction has continued to be higher than +12.5% or lower than

-12 5% for 5 sec.

Short-range fuel correction has continued to be higher than +lo% or lower than

-10% for 5 sec

SCAN TOOL Data list 13 Intake air temperature sensor (Refer to P13A-122.)

- - _____

w 32 Manifold absolute pressure sensor (Refer to P.13A-122.)

I

SCAN TOOL Data list h 81 Long-term fuel compensation (Refer to P.13A-122.)

4 Less than zero

0 Check for fuel leaks from injector.

0 Check for entry of foreign matter (water, kerosene, etc.) into the fuel.

1OK

1 Replace the ECM

Probable cause

0 Injector failed 0 Incorrect fuel pressure 0 Air drawn in from gaps in gasket seals, etc.

0 Heated oxygen sensor failed 0 Engine coolant temperature sensor failed 0 Intake air temperature sensor failed 0 Manifold absolute pressure sensor failed 0 Exhaust leak 0 Use of incorrect fuel 0 Engine control module failed

Check the intake air temperature circuit malfunction (Refer to

L

TROUBLE CODE PO110) P.13A-29, INSPECTION PROCEDURE FOR DIAGNOSTIC

Check the engine coolant temperature circuit malfunction (Refer

TROUBLE CODE PO115) to P.13A-30, INSPECTION PROCEDURE FOR DIAGNOSTIC

Check the manifold absolute pressure circuit malfunction (Refer

TROUBLE CODE P0105) to P 13A-28, INSPECTION PROCEDURE FOR DIAGNOSTIC

Check if air was drawn into the intake system.

* Repair

T 0 Check for clogging of the injector 0 Check for clogging of the fuel filter and fuel line.

0 Check the fuel pump (insufficient discharge rate).

0 Check for exhaust leaks (oxygen sensor installation section, cracks in exhaust manifold, cracks in front pipe, etc.).

0 Check for entry of foreign matter (water, kerosene, etc ) into the fuel.

1OK FplaceJheECM

Code No. P0201, P0202, P0203, PO204 Injector Circuit Malfunction (Cylinder-1 , Cylinder-2, Cylinder-3, Cylin- der4)

Background 0 A surge voltage is generated when the injectors are driven and the current flowing to the injector coil is shut off.

The engine control module checks this surge voltage Check Area

Engine speed is between 50 and 1000 r/min.

Throttle position sensor output voltage is lower than 1 0 V Judgment Criteria 0 Injector coil surge voltage (more than system voltege +2 V) has not been detected for 2 sec.

NG

1 Check the iniector (Refer to P.13A-155.) t Replace

Measure at the injector connectors A-70, A-71, A-72, A-73 0 Disconnect the connector, and measure at the harness side.

0 Voltage between 1 and ground. (Ignition switch. ON) OK: Battery positive voltage

Check the injector control circuit.

(Refer to P.13A-121 INSPECTION PROCEDURE48)

Probable cause

0 Injector failed 0 0 Engine control module failed Open or shorted injector circuit, or loose connector

Repair connectors: A-70, A-71, A-72, A-73

NG

1 tor. Repair, if necessary.

I

Code No. PO300 Random Misfire Detected

Background

If amisfiringoccurswhiletheengineis running,theenginespeedsuddenlychanges The engine control module checks for changes in the engine speed Check Area

5 sec or more have passed after the engine was started 0 Engine speed is between 500 and 6500 r/min Engine coolant temperature is -10°C (14°F) or more Intake air temperature -10°C (14°F) or more 0 Adaptive learning is complete for the vane which generates a crankshaft position signal 0 While the engine is running, excluding gear shifting, deceleration, sudden acceleration/deceleration and A/C compressor switching Judgment Criteria (change in the angular acceleration of the crankshaft is used for misfire detection ) 0 Misfire has occurred in the engine more than allowed (1 8%) per 200 revolutions [when the catalyst temperature is higher than 950°C (1742"F)I or 0 Misfire has occurred in the engine more than allowed (1 8%) per 1 000 revolutions (Misfire exceeding 1 5 times the limit of emission standard )

*

-

SCAN TOOL Data list 22 Crankshaft position sensor (Refer to P.13A-122.) 0 Crankshaft position sensor wave form check

OK: Constant pulse range .

Engine speed: stable

1

NG c Replace

NG c Repair A-70, A-71, A-72, A-73, B-40 4 OK

NG Check the harness wire between the EC

- Repair

-~

4 OK

SCAN TOOL Data list 81 Long-term fuel compensation (Refer to P.13A-122)

~ _ _ _ _ _ _ ~ _ _

SCAN TOOL Data list 82 Short-term fuel compensation (Refer to P.13A-122)

1 SCAN TOOL Data list

- NG

i 0 K

1 21 Engine coolant temperature sensor (Refer to P.13A-122.)

OK i Check the following items 0 Check the ignition coil, spark plugs, spark plug cables.

0 Check the compression pressure 0 Check the timing belt for jumping teeth 0 Check the EGR system and EGR valve.

~~ ~~

Probable cause

0 Ignition system related part@) failed 0 Poor crankshaft position sensor signal 0 Incorrect air/fuel ratio 0 Low compression pressure 0 Engine coolant temperature sensor failed 0 Timing belt teeth jumped 0 Injector failed 0 EGR valve failed 0 Engine control module failed

Check the following

- Repair connectors: A-82, B-37

- Check the fuel trim malfunction (Refer to P.13A-37, INSPECTION I PROCEDURE FOR DIAGNOSTIC TROUBLE CODE P0170) 1

---I Check the engine coolant temperature circuit malfunction (Refer 1 to p.i3~-30, TNSPECTION PROCEDURE FOR DIAGNOSTIC TROUBLE CODE PO115)

Code No. P0301, P0302, P0303, P0304, Misfire Detected (Cylinder-1 , Cylinder-2, Cylinder-3, Cylinder-4)

Background 0 If a misfiringoccurs while theengine is running, the enginespeed suddenly changes.

0 The engine control module checks for changes in the engine speed.

Check Area 0 5 sec or more have passed after the engine was started 0 Engine speed is between 500 and 6500 r/min.

0 Engine coolant temperature is -10°C (14°F) or more.

0 Intake air temperature -10°C (14OF) or more 0 Adaptive learning is complete for the vane which generates a crankshaft position signal.

0 While the engine is running, excluding gear shifting, deceleration, sudden acceleration/deceleration and A/C compressor switching.

Judgment Criteria (change in the augular acceleration of the crankshaft is used for misfire detection ) 0 Misfire has occurred in the engine more than allowed (1 8%) per 200 revolutions [when the catalyst temperature is higher than 950°C (1742@F)] or 0 Misfire has occurred in the engine more than allowed (1 8%) per 1,000 revolutions (Misfire exceeding 1 5 times the limit of emission standard )

NG * Replace

NG - Repair !OK

A-70, A-71, A-72, A-73, 8-40

NG 1 Check t h Repair

!OK

0 Check the following items Check the spark plugs, spark plug cables.

Probable cause

0 Ignition system related part(s) failed 0 Low compression pressure 0 Injector failed 0 Engine control module failed

'

Code No. P0335Frankshaft Position Sensor Circuit Malfunction

Background 0 When the engine is running, the crankshaft position sensor outputs a pulse signal 0 The engine control module checks whether the pulse signal is input while the engine is cranking.

Check Area

Engine is being cranked Judgment Criteria 0 Sensor output voltage has not changed (no pulse signal IS input) for 2 sec Check Area Judgment Criteria

Normal signal patternhas not been inputfor cylinder identificationfrom thecrankshaft position sensor siqnal and camshaft position sensor signal for 2 sec

-

OK

Measure at the crankshaft position sensor connector A-82

+

Measure with the connector connected. (Use the test harness: MD998478 ) Voltage between 2 (black clip) and ground (Engine:

cranking) O K 0.4-4.0 V Voltage between 2 (black clip) and ground (Engine:

idling) OK: 1.5-2 5 V

Measure at the crankshaft position sensor connector A-82

Disconnect the connector, and measure at toe harness side 1 Voltage between 3 and ground (Ignition switch. ON) OK Battery positive voltage 2 Voltage between 2 and ground (Ignition switch ON)

OK: 48-52 V

i [ Check trouble'symptom.

3 Continuity between 1 and ground OK: Continuity 1 OK

nector: A-82

between the ECM and the crankshaft position sensor connector 1 OK I Replace the ECM.

L~ Check the harness wire between the crankshaft position sensor and the around. Repair. if necessary.

b 1 OK

I Check trouble symptom.

I Replace the crankshaft position sensor.

ING

Probable cause

0 Crankshaft position sensor failed 0 Open or shorted crankshaft position sensor circuit, or loose connector 0 Engine control module failed

Replace the ECM.

Check the harness wire between the crankshaft position sensor and the MFI relav connector. ReDair. if necessarv.

nector: 8-37

NG

Code No. PO340 Camshaft Position Sensor Circuit Malfunction

Background 0 When the engine is running the camshaft position sensor outputs a pulse signal 0 The engine control module checks whether the pulse signal is input Check Area

Engine speed is 50 r/min or higher Judgment Criteria 0 Sensor output voltage has not changed (no pulse signal is input) for 2 sec.

Check Area 0 Engine speed is 50 rlmin or higher Judgment Criteria 0 Normal signal pattern has not been inputfor cylinder identificationfrom the crankshaft position sensor and camshaft position sensor signal for 2 sec

OK

- 1 Replace the ECM.

Measure with the connector connected Voltage between 5 and ground (Engine cranking) OK: 0.4-3.0 V Voltage between 5 and ground (Engine idling)

1 NG Measure at the distributor connector A-61.

Disconnect the connector, and measure at the harness side

1. Voltage between 6 and ground (Ignition switch ON) OK: Battery positive voltage

2. Voltage between 5 and ground (Ignition switch ON) OK: 48-52 V

3. Continuity between 7 and ground OK: Continuity OK Check trouble symptom

Replace the distributor.

Probable cause

0 Camshaft position sensor malfunction 0

Open or shorted camshaft position sensor circuit or loose connector

0 Engine control module failed

Check the harness wire between the camshaft position sensor and the MFI relay connector Repair, if necessary

Check the harness wire be- tween the ECM and the dis- tributor connector.

Replace the ECM

-~ ~~

*

Code No. PO400 Exhaust Gas Recirculation Flow Malfunction

Background 0 When the EGR solenoid switches from OFF to ON while the engine is running, EGR gas flows The engine control module checks how the EGR gas flow signal changes Check Area 0 After at least 20 seconds have passed since the last monitor finished.

0 Engine coolant temperature is higher than 80°C (176°F) 0 Engine speed is between 1500 and 2000 r/min <MP> or 1000 and 2000 r/min <A/T> 0 Intake air temperature is 5°C (41°F) or more Vehicle speed is 30 km/h (18 7 mph) or higher 0 At least 90 seconds have passed since manifold differential pressure sensor output voltage fluctuated 1 5 V or higher 0 Closed throttle position switch ON 0 Intake air pipe pressure is 35 kPa (5 0 psi) or less <M/f>, or 47 kPa (6 8 psi) or less <An> 0 While fuel is being shut off <MP> 0 Monitoring Time 2 sec Judgment Criteria 0 The fluctuation in the intake system IS low when the EGR solenoid is turned ON 0 Monitored only three times per trip

c 32 Manifold absolute pressure sensor (Refer to P.13A-122) I

1 Check the EGR valve and EGR route for clogging, and clean. I

Probable cause

0 EGR valve does not open EGR control vacuum is too low 0 EGR solenoid failed 0 Open or shorted EGR solenoid circuit, or loose connector 0 Manifold absolute pressure sensor failed 0 Engine control module failed

Check the EGR solenoid (Refer to GROUP 17 - Emission Control

Replace

Check the following items.

0 Vacuum hoses 0 EGR port vacuum 0 EGR valve (Refer to GROUP 17 - Emission Control System.)

Check the manifold absolute pressure circuit malfunction (Refer to P.13A-28, INSPECTION PROCEDURE FOR DIAGNOSTIC TROUBLE CODE P0105)

Code No. PO403 Exhaust Gas Recirculation solenoid Malfunction

Background 0 The engine control module checks current flows in the EGR solenoid drive circuit when the solenoid is ON and OFF Check Area 0 Battery voltage is not lower than 10 V.

Judgment Criteria 0 Solenoid coil surge voltage (more than system voltage +2V) is not detected when the EGR solenoid is turned on/off 0 Monitored only once per trip

NG - Check the harness wire between MFI relay and solenoid valve connector, and repair if necessary _ _ ~ _ _ _ _ ~

Measure at the EGR solenoid connector A-48.

0 Disconnect the connector and measure at the harness side 0 Voltage between 1 and ground (Ignition switch. ON) OK: Battery positive voltage

1 Check t

- 1 NG - Check the following con- nector: A-48 Measure at the ECM connector 8-40, 0 Disconnect the connector and measure at the harness

side.

OK: Battery positive voltaqe 0 Voltage between 6 and ground (Ignition switch ON)

* Repair t OK

I nector: B40i OK 1

1 Check trouble symptom

NG

LReplace the ECM.

~ ~ _ _ _

Probable cause

0 EGR solenoid failed.

0

Open or shorted evaporative EGR solenotd circuit, or loose connector.

0 Engine control module failed.

Repair

Check trouble symptom.

Check the harness wire between ECM and solenoid valve connector, and repair if necessary.

Code No. PO420 Catalyst System Efficiency Below Threshold

Background

The signal from the heated oxygen sensor which follows the catalytic converter differsfrom that which precedes the catalytic converter That is because the catalytic converter purifies exhaust gas When the catalytic converter has deteriorated, the signal from the heated oxygen sensor which follows the catalytic converter becomes similar to that which precedes the catalytic converter 0 The engine control module checks the outputs of the heated oxygen sensor signals Check Area

Engine speed is not higher than 2,600 r/min.

Intake air temperature IS -10°C (14°F) or more Intake air pressure is between 20 and 63 kPa (2 9 and 9 2 psi) <M/T> or between 24 and 63 kPa (3 5 and 9 2 psi) <An>.

Closed throttle position switch. OFF 0 Under the closed loop air-fuel ratio control 0 Vehicle speed is 1 5 km/h (0 93 mph) or higher

Monitoring time 140 sec Judgment Criteria

Fault in the oxygen sensor (rear) signal and oxygen sensor (front) signal.

I Check the exhaust manifold for cracks and leaks.

c---

NG

-

__c Replace

59 Heated oxygen sensor (rear)

Transaxle. 2nd gear <M/T>, L range <A/T> Drive with wide open throttle OK: 600 - 1000 mV

-

SCAN TOOL Data list 11 Heated oxygen sensor (front)

Sudden racing OK: 600 - 1000 mV

-

SCAN TOOL Data list 11 Heated oxygen sensor (front)

Engine: 2000 r/min OK: The switch between 0 - 400 - 600 - 1000 mV is 15 or more times in 10 sec.

t- .

Replace the heated oxygen sensor (rear)

1 Check the trouble symptom.

I Replace the catalytic converter.

1 Check trouble symptom.

NG

1 Replace the ECM.

Probable cause

0 Catalytic converter deteriorated 0 Heated oxygen sensor failed 0 Engine control module failed

Check the heated oxygen sensor circuit malfunction (sensor 2) (Refer to P.13A-35, INSPECTION PROCEDURE FOR DIAGNOS- TIC TROUBLE CODE P0136)

Check the heated oxygen sensor circuit malfunction (sensor 1) (Refer to P.13A-33, INSPECTION PROCEDURE FOR DIAGNOS- TIC TROUBLE CODE P0130)

Replace the heated oxygen sensor (front)

Code No. PO421 Warm Up Catalyst Efficiency Below Threshold

Background 0 The signal from the heated oxygen sensor which follows the catalytic converter differs from that which precedes the catalytic converter That is because the catalytic converter purifies exhaust gas When the catalytic converter has deteriorated, the signal from the heated oxygen sensor which follows the catalytic converter becomes similar to that which precedes the catalytic converter The enginecontrol module checks the outputs of the heated oxygen sensor signals Check Area 0 Engine speed is not higher than 2250 r/min

Intake air temperature is -10°C (14OF) or more Intake air pressure is between 20 and 63 kPa (2 9 and 9 2 psi) <M/T> or between 24 and 63 kPa (3.5 and 9 2 psi) <A/l> Closed throttle position switch OFF 0 Under the closed loop air-fuel ratio control

Vehicle speed is 1 5 km/h (0 93 mph) or higher 0 Monitoring time 140 sec Judgment Criteria

Fault in the oxygen sensor (rear) signal and oxygen sensor (front) signal

NG 1 Check the exhaust m a n i f o p + Replace

. .--e 59 Heated oxygen sensor (rear) 0 Transaxle: 2nd gear <M/T>, L range <A/T>

SCAN TOOL Data list

--A

11 Heated oxygen sensor (front) 0 Sudden racing OK: 600 - 1000 mV

~ TIC TROUBLE CODE P0130) i°K SCAN TOOL Data list 11 Heated oxygen sensor (front) 0 Engine: 2000 rimin OK: The switch between 0 ._ 400 - 600 - 1000 mV IS 15 or more times in 10 sec

NG Replace the heated oxygen sensor (front)

I Replace the heated oxygen sensor (rear) I

Check the trouble symptom

I NG

I Replace the catalvtic converter.

I

I Check trouble symptom.

7 iNG

1 Replace the ECM.

Probable cause

0 Catalytic converter deteriorated 0 Heated oxygen sensor failed 0 Engine control module failed

Check the heated oxygen sensor circuit malfunction (sensor 2) (Refer to P.13A-35, INSPECTION PROCEDURE FOR DIAGNOS- TIC TROUBLE CODE PO136)

Check the heated oxygen sensor circuit malfunction (sensor 1)

(Refer to P 13A-33, INSPECTION PROCEDURE FOR DIAGNOS-

Code No.

1 PO442 Evaporative Emission Control System Leak Detected

System Diagram

INTAKE MANIFOLD m

-T PURGE SOLENOID

VENTllATlON SOLENOID

EVAPORATIVE EMISSION FUEL TANK CANISTER

~~~~ ~ EVAPORATIVE EMISSION CANISTER

B13MOO99

FUEL VENT VALVE

A031011 5

TECHNICAL DESCRIPTION

0 The ECM turns on the evaporative emission ventilation solenoid which shuts off the evaporative emission canister outlet port. Then the evaporative emission purge solenoid is driven. As a result, the fuel system will be set into a negative pressure.

When the fuel system reaches negative pressure, the evaporative emission purge solenoid is turned “off,” and the fuel system are sealed. As the fuel pressure inside the fuel tank changes, the ECM judges if there is a leak in the fuel system.

DTC SET CONDITIONS Check Area At least sixteen minutes have passed since the starting sequence was completed.

Engine coolant temperature higher than 60°C (1 40” F).

Engine speed is 1,600 r/min or more.

Power steering pressure switch: “OFF.” Barometric pressure is higher than 76 kPa (11 psi).

Volumetric efficiency is at between 20 and 80 percent.

The engine coolant temperature is 30°C (86°F) or less when the engine is started.

Intake air temperature is higher than 5°C (41°F).

The pressure rise when the evaporative emission purge solenoid and evapcrr’alive emission ventilation solenoid are closed is less than 451 Pa (0.065 psi).

OVERVIEW OF TROUBLESHOOTING

0 To determine the cause of DTC P0442, a performance test is needed. The performance test uses a mechanical vacuum gauge and scan tool MB991502 set on the fuel tank differential pressure sensor (TANK PRS SNSR 73). The mechanical gauge reading is used to verify scan tool MB991502 reading. A comparison of the mechanical gauge to scan tool MB991502 determines the problem in the system.

Prior to doing the performance test, several simple inspections are needed to exclude some possibilities of the symptom.

0

0 The pressure fluctuation width is less than 647 Pa (0.094 psi).

0 At least twenty seconds have passed since pressure fluctuation detection commenced.

0 Fuel tank differential pressure sensor output voltage is 1 - 4 volts.

0 Intake air temperature is 30°C (86°F) or less when the engine started.

0 Vehicle speed is 30 km/h (18.7 mph) or more.

0 Monitoring time: 75 - 125 seconds

Judgment Criteria

0 Internal pressure of the fuel tank has changed more than 843 Pa (0.122 psi) in 20 seconds after the tank and vapor line were closed.

TROUBLESHOOTING HINTS The most likelv causes for this code to be set are:

0 0 0 0 0 0 0 0 0

Loose fuel cap.

Fuel cap relief pressure is incorrect.

Evaporative emission canister seal is faulty.

Evaporative emission canister is clogged.

Fuel vent valve failed.

Purge line or vapor line is clogged.

Fuel tank, purge line or vapor line seal failed.

Evaporative emission purge solenoid failed.

Evaporative emission ventilation solenoid failed.

Fuel tank differential pressure sensor failed.

Engine coolant temperature sensor failed.

Intake air temperature sensor failed.

Power steering pressure switch failed.

Use of incorrect fuel.

0 0 0 a 0

DIAGNOSIS Required Special Tool:

MB991502: Scan Tool (MUT-11)

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

(6) Keep the idling position during the monitor.

NOTE: If the engine speed does not reach 2,000 r/min during the monitor test, adjustment of the Speed Adjusting Screw may be needed. Refer to F! 13A-143 for the adjustment procedure.

I

(7) Item “In Progress” is displayed during the monitor. Keep the engine speed and load within the defined range. Scan tool MB991502 shows these items on the screen.

Item “In Progress” will be change from “NO” to “YES” by keeping engine conditions.

(8) Message “Evap Leak Mon. Completed. Test Passed.” is displaved when the test has been completed without

malfunction. Evaporative emission system is working property at this time. Please explain to customer that improperly tightened fuel cap can cause to MIL turn on.

No further steps are needed.

(9) Message “Evap Leak Mon. Completed. Test Failed & DTCs Set.” is displayed when a malfunction has been detected durina the test. Go to Step 3.

MFI <I

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

0 If not, refer to DTC PO443 (Evaporative Emission Control System Purge Control Valve Circuit Malfunction) on P. 13A-57.

i

STEP 6. Using scan tool MB991502, actuator test item 29 : evaporative Emission Ventilation Solenoid.

(1) Disconnect the hose connected to the vent solenoid valve from the evaporative emission canister.

(2) Connect a hand vacuum pump to the hose that is disconnected in the previous step.

(3) The vacuum should leak when vacuum is applied, and the vacuum should be maintained when the purge solenoid is activated by the actuator test of scan tool MB991502.

0 If correct, go to Step 7.

If not, refer to DTC PO446 (Evaporative Emission Control System Vent Control Malfunction) on

P. 1 3A-58.

13M0101

STEP 7. Check the purge solenoid-to-air intake plenum hose for blockage.

(1 ) Disconnect the purge solenoid-to-air intake plenum hose at the purge solenoid side.

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

NOTE: Fuel temperature should be lower than 40" C (1 04" F) during the performance test.

In this step, verify if the EVAP system works properly, or determine which area of the evaporative emission system has a failure.

Caution As a 0 - 6.2 kPa (0 - 0.90 psi) range vacuum gauge is used, the gauge may be broken if excessive vacuum pressure is applied. Do not apply a vacuum of more than 2.9 kPa (0.42 psi).

To achieve the performance test efficiently, a mechanical vacuum gauge [0 - 6.2 kPa (0 - 0.90 psi) range] and scan tool MB991502 should be used, and the engine to generate vacuum.

(1) Install a mechanical vacuum gauge [0 - 6.2 kPa (0 - 0.90 psi) range] between the EVAP purge solenoid valve and the purge hose that comes from the evaporative emission canister, (2) Before starting the performance test, set the vehicle in the following condition.

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

NOTE: If there is a svstem failure, either of both vacuum readings may not reach to the above specifications. In this case, it is not necessary to pinch off the purge hose as shown. Refer to the performance test results table below for further steps.

(10)After an elapsed time of 20 seconds, check the fuel tank differential pressure reading on scan tool MB991502.

OK: Change in pressure reading is 0.4 kPa (0.06 psi) or less [holding -2.5 kPa (-0.36 psi) or more vacuum].

Performance test result table:

MECHANICAL VACUUM GAUGE READING

SCAN TOOL MB991502 READING

Reaches 2.9 kPa (0.42 psi).

Reaches -2.9 kPa (-0.42 psi) and vacuum drops not more than 0.4 kPa (0.06 psi) in 20 seconds.

Reaches 2.9 kPa (0.42 psi).

Does not reach -2.9 kPa (-0.42 psi).*

Does not reach -2.9 kPa (-0.42 psi).

Does not reach 2.9 kPa (0.42 psi).

Reaches 2.9 kPa (0.42 psi).

Reaches -2.9 kPa (-0.42 psi) but vacuum drops more than 0.4 kPa (0.06 psi) in 20 seconds.

NOTE *: If there is a blockage, scan tool MB991502 reading can be a positive value (positive pressure) due to the heat of return fuel from the engine.

STEP 10. Vacuum reading on both the mechanical gauge and scan tool MB991502 reaches the specifications and satisfy the specifications after 20 seconds:

EVAP system is properly working at the moment. The cause of DTC might have been a loose fuel cap and the customer may have already tightened fuel cap causing the MIL to turn on. No further steps are needed.

STEP 11. Vacuum reading on the mechanical gauge reaches 2.9 kPa (0.42 psi) but scan tool MB991502 does not reach -2.9 kPa (-0.42 psi) :

(1) If the vacuum reading on the gauge reaches 2.9 kPa (0.42 psi) but the reading on scan tool MB991502 does not reach -2.9 kPa (-0.42 psi), either a system blockage or a bad differential pressure sensor may be the cause.

(2) To determine if there is a blockage in the system, remove the fuel caD.

RESULT

GO TO

Satisfactory.

No leak nor blockage detected.

Step 10

Step 11

Blockage in the system or bad differential sensor.

Large leak in EVAP system.

Step 13

Small leak in EVAP system.

Step 14

0 If the vacuum reading on the vacuum gauge [at this point 2.9 kPa (0.42 psi)] remains the same, there is a blockage in the system. Go to Step 12.

If the reading drops to about 0 kPa (0 psi), there is no blockage in the EVAP system. The fuel tank differential pressure sensor needs to be replaced.

After replacing the differential pressure sensor, go to Step 15.

0

STEP 12. System blockage inspection.

(1) Disconnect the number 1 and 2 hoses shown in the illustration, check the mechanical vacuum gauge reading.

If the vacuum reading does not drop, then the blockage is not in the fuel tank.

(2) Disconnect one portion of the EVAP system at a time working towards the front of the vehicle until blockage is found (number 1 to 5 hoses in the illustration).

(3) Repair the location of the blockage and go to Step 15.

PURGE c+ SOLENOID

V S

(-1 ' U EVAPORATIVE EMISSION CANISTER FUEL TANK B03'01 15 -

STEP 13. Vacuum readings on both the mechanical gauge and scan tool MB991502 do not reach the specifications [2.9 kPa (0.42 psi) and -2.9 kPa (-0.42 psi)]:

This condition shows that there is a significant leakage in the system. The inspection procedure for the large system leakage is the same as the small leakage test in Step 14.

STEP 14. Vacuum readings on both the mechanical gauge and scan tool MB991502 do not reach the specification [2.9 kPa (0.42 psi) and -2.9 kPa (-0.42 psi)] but do not maintain the vacuum.

This condition shows that there is a slight leakage in the system. Follow the procedure below to locate the source of the leak.

(1) The fuel cap relief valve inspection.

a. Remove the fuel cap and install the fuel tank filler tube adapter in the emission system tester kit in place of the fuel cap.

b. Plug the nipple on the fuel tank filler tube adapter.

c. Repeat the performance test. If the EVAP system holds the vacuum, then the fuel cap is faulty. Replace the fuel cap, and go to Step 15.

(2) To find the vacuum leakage in the system, clamp the number 1 and 2 hoses shown in the illustration. Repeat the performance test. This will determine if the vacuum leak is either in the fuel tank area or in the rest of the system.

PURGE c+ SOLENOID VENTllATlON J 5

NOTE: In this case, as we clamped off the vacuum hose connecting to the fuel tank, scan tool MB991502 reading will not change. Please use the mechanicalgauge reading.

If the EVAP system hold the vacuum leak is in the fuel tank area. To locate the leakage, pressurize the EVAP system to 3.4 kPa (0.49 psi) and look for leaky area using the ultrasonic leak detector in the Evaporative Emission System Tester. After repairing the leakage, go to Step 15.

If the vacuum leak still exists, the leak is at other than fuel tank area.

(3) Clamp off the vacuum hose one component at a time working towards the front of the vehicle until leakage is found (number 1 to 5 hoses shown in the illustration).

(4) Repair the leakage at that location and go to Step 15.

I LIQUID SEPARATOR

e

(-1 ' EVAPOF W E EMISSION CANISTER FUEL TANK 603'0115

STEP 15. Confirmation test.

After system failures are repaired, repeat the Evaporative Emission System Leak Monitor test (Step 2) to check that the EVAP system operates correctly.

*

Code No. PO443 Evaporative Emission Control System Purge Control Valve Circuit Malfunction

~ Background 0 The engine control module checks current flows in the evaporative emission purge solenoid (No 1) drive circuit when the solenoid is ON and OFF Check Area 0 Battery voltage is not lower than 10 V Judgment Criteria 0 Solenoid coil surge voltage (more than system voltage +2 V) is not detected when the EVAP purge solenoid is turned onioff.

0 Monitored only once per trip

Replace NG

0 Voltage between 2 and ground (Ignition switch: ON) OK: Battery positive voltage

Measure at the ECM connector 8-40, 0 Disconnect the connector and measure at the harness side.

0 Voltaae between 9 and around (lanltion switch ON)

1 OK: Gattery positive voKage ' " ' I I Check trouble symptom.

I 1 NG Check the harness wire between ECM and solenoid valve connector.

ReDair. if necessarv.

Check the following con- nector: 8-40

+ Repair

1 Check trouble symptom

Replace the ECM.

-~

I Probable cause

0 Evaporative emission purge solenoid failed 0 Open or shorted evaporative emission purge solenoid circuit, or loose connector 0 Engine control module failed

Code No. PO446 Evaporative Emission Control System Vent Control Malfunction Probable cause

[Comment] Background 0 The engine control module checks current flows in the evaporative emission ventilation solenoid drive circuit when the solenoid is ON and OFF Check Area

Battery voltage IS 10 V or higher.

Judgment Criteria 0 Solenoid coil surge voltage (system voltage t2 v) is not detected when the EVAP emission vent solenoid is turned on/off Monitored only once per trip

1 b Replace NG

(Refer to GROUP 17 - Emission Control System.)

- - ~ _ _ _ _

Measure at the evaporative emission ventilation solenoid connector F-19.

---t Checkthe harnesswire between MFI relay and solenoidvalveconnector.

Disconnect the connector and measure at the harness side.

Voltage between 2 and ground (Ignition switch, ON) OK: Batterv positive voltaqe

- I OK Measure at the ECM connector B-38.

NG

-

Disconnect the connector and measure at the harness side.

Voltage between 55 and ground (Ignition switch: ON) OK: Battery positive voltage I

1 NG Check trouble symptom.

I-] Replace the ECM.

1

0 Evaporative emission ventilation solenoid failed.

0 Open or shorted evaporative emission ventilation solenoid circuit, or loose connector 0 Engine control module failed

~ ReDair. if necessarv.

+ Repair Check the following con- nectors: B-36, E-13, F-19

1 Check trouble svmDtom.

I I NG Check the harness wire between ECM and solenoid valve connector.

Repair, if necessary.

*

I Code No.

~ PO450 Evaporative Emission Control System Pressure Sensor Malfunction

Fuel Tank Differential Pressure Sensor Circuit

(E-23)

(B-36)

(858)

ENGINE CONTROL MODULE (ECM) I 1310085 I CONNECTOR: B-36 CONNECTOR: E-22- \ I

FUEL TANK DIFFERENTIAL PRESSURE SENSOR

3

Y 9

I4

I

CONNECTOR: E-23

CIRCUIT OPERATION

0 A 5-volt voltage is supplied to the power terminal of the fuel tank differential pressure sensor (terminal 3) from the ECM (terminal 81). The ground terminal (terminal 2) is grounded with the ECM (terminal 92).

A voltage proportional to the pressure in the fuel tank is sent from the output terminal of the fuel tank differential pressure sensor (terminal 1) to the ECM (terminal 61).

0

DTC SET CONDITIONS Check Area

0 Intake air temperature is higher than 5°C (41 OF).

0 Engine speed is higher than 1,600 r/min.

0 Volumetric efficiency is between 20 and 80 percent.

Judgement Criteria

0 The sensor output voltage is more than 4 volts for 10 seconds even if the evaporative emission purge solenoid is driven at a 100 percent duty when the intake air temperature is between 5 and 45°C (41 - 113°F).

or 0

The sensor output voltage is less than 1 volt for 10 seconds even if the evaporative emission purge solenoid is not driven when the intake air temperature is 5°C (41 OF) or more.

Check Area

0 The throttle valve is closed.

0 0 Engine speed is 840 r/min or less.

Vehicle speed is 1.5 km/h (0.93 mph) or less.

CONNECTORS: B-37, 8-38 I

TECHNICAL DESCRIPTION

0 The fuel tank differential pressure sensor outputs the voltage in proportion to the pressure in the fuel tank (differential pressure against the barometric pressure).

The ECM checks whether the output voltage of the fuel tank differential pressure sensor is with in the specified range.

0

Judgement Criteria

0 The events are counted 20 times or more that sudden pressure fluctuation of at least 0.2 volts is detected for 25 milliseconds or more.

0 The above events are detected continuous eight times during normal driving condition.

NOTE: If the number of the pressure fluctuation does not reach 20 during one engine idling, the count number will be reset to zero. In addition, the count number will be also reset to zero if the ignition switch is turned off.

NOTE: The engine control module determines that the engine has deflected from the idle operation if all of the following conditions are met.

0 Engine speed is higher than 2,500 r/min.

0 Vehicle speed is 15 km/h (9.3 mph) or more.

0 Volumetric efficiency is 55 percent or more.

TROUBLESHOOTING HINTS The most likely causes for this code to be set are:

0 Fuel tank differential pressure sensor failed.

0 Open or shorted fuel tank differential pressure sensor circuit, or loose connector.

0 ECM failed.

OVERVIEW OF TROUBLESHOOTING

0 DTC PO450 can be set if either of the following conditions occur:

1. Faulty fuel tank differential pressure sensor, related circuit, or ECM.

2. Faulty fuel tank filler tube vent valve or blocked vapor line.

If the fuel tank filler tube vent valve is faulty and stays closed or the vapor line is blocked, the pressure inside the fuel tank is increased as the evaporative fuel is not purged especially at hot ambient temperatures. Once the pressure inside the fuel tank reaches 6 kPa, the sensor output voltage also reaches and remains 4.5 volts. This will set DTC P0450.

To check a system blockage, do a performance test which uses a mechanical vacuum gauge and scan tool MB991502 (MUT-11) set on the fuel tank differential pressure sensor (TANK PRS SNSR 73). The mechanical gauge reading is used to verify scan tool MB991502 reading. A comparison of the mechanical gauge to scan tool MB991502 determines the problem in the system.

0

0

’

DIAGNOSIS Required Special Tool:

MB991502: Scan Tool (MUT-11)

Caution To prevent damage to scan tool MB991502, turn the ignition switch off before connecting or disconnecting scan tool MB991502.

In this procedure, scan tool MB991502 should be used in the metric mode (showing the value in kPa). If not, set scan tool MB991502 by selecting the “System Setup” at the main menu.

STEP 1. Using scan tool MB991502, check “Fuel tank differential pressure sensor (date list 73)” output.

In this step, check the fuel tank differential pressure sensor reading to determine if the fuel tank differential pressuresensor is operating correctly.

(1) Check the MFI data list item: TANK PRS SNSR 73 (2) Watch the sensor reading. This value varies depending on pressure inside the fuel tank.

(3) Remove the fuel cap.

(4) After the fuel cap has been removed, the pressure sensor reading should be between -0.5 kPa (-0.07 psi) and 0.5 kPa (0.07 psi).

0 If the reading is between -0.5 kPa (-0.07 psi) and 0.5 kPa (0.07 psi), the DTC could be caused by an intermittent electrical malfunction, or by a blockage in the EVAP system. Go to step 2.

If the reading is not between -0.5 kPa (-0.07 psi) and 0.5 kPa (0.07 psi), there is an electrical malfunction. Go to step 9.

0

STEP 2. Check the fuel vent valve plunger and flapper door operation.

NOTE: When a fuel nozzle is inserted to the fuel tank filler tube and the flapper door is opened, the fuel vent valve is closed (plunger moves towards the top of the neck). When the fuel cap is closed, the fuel cap pushes the plunger back in, which then opens the vent valve. If the flapper door or plunger does not operate properly, the vent valve stays closed even after the fuel cap is closed. This may block the vapor passage and set the DTC P0450.

(1) Remove the fuel cap.

(2) Push the flapper in to operate the valve.

NOTE: When the flapper is pushed in, the plunger of the valve should move towards the top.

(3) Reinstall and tighten the fuel cap until three clicks are heard.

(4) Remove the cap again and check the protrusion of the plunger to verify if it is pushed back.

(5) The distance between the tip of vent valve plunger and that of fuel tank filler tube should be 28 mm (1.1 inches) or more.

/I V0381AA

STEP 3. Evaporative Emission System Leak Monitor Test using scan tool MB991502.

NOTE: This monitor is carried out at an engine speed of 1,600 r/min or more, transmission is in “N” or “R” position.

The engine speed has to be automatically adjusted.

(1) Erase the DTCs using scan tool MB991502. Ensure that the fuel cap is securely tightened.

(2) Select “System Test” and press “YES” key.

(3) Select “Evap Leak Mon” and press “YES” key.

(4) If “Evap Leak Mon” is selected before starting the engine, “Engine must be running.” is displayed. In this case, start the engine and then select “Evap Leak Mon” again.

(5) If “Keep the TPS in idle position. during the test.” is displayed, the ECM or PCM adjusts engine speed automatically. A manual adjustment for engine speed is not needed.

If the plunger does not return, replace the fuel tank filler tube and securely tighten the cap.

If the operation is OK, install and securely tighten the fuel cap.

Go to Step 3.

(6) Keep the idling position during the monitor.

NOTE: If the engine speed does not reach 2,000 r/min during the monitor test, adjustment of the Speed Adjusting Screw may be needed. Refer to /? 13A-143 for the adjustment procedure.

(7) Item “In Progress” is displayed during the monitor. Keep the engine speed and load within the defined range. Scan tool MB991502 shows these items on the screen.

Item “In Progress” will be change from “NO” to “YES” by keeping engine conditions.

(8) Message “Evap Leak Mon. Completed. Test Passed.” is displayed when the test has been completed without malfunction. Evaporative emission system is working property at the moment. Please explain to customer that improperly tightened fuel cap can cause to turn MIL on.

No further steps are needed.

(9) Message “Evap Leak Mon. Completed. Test Failed & DTCs Set.” is displayed when a malfunction has been detected during the test. Go to Step 4.

(1 0)Message “Evap Leak Mon. discontinued. Retest again from the first” is displayed when the monitor was discontinued by a certain reason (input vehicle speed, engine speed and engine load was put of the specified range). Turn the ignition switch off once and start the monitor from the beginning.

NOTE: The monitor will not start unless turning off the ignition switch once and restart the engine.

STEP 4. Check the purge solenoid-to-air intake plenum hose for blockage.

(1) Disconnect the purge solenoid-to-air intake plenum hose at the purge solenoid side.

(2) Connect a hand vacuum pump to the disconnected hose end.

(3) Apply vacuum, and check if the vacuum is not maintained.

0 If not maintained, go to STEP 5.

0 If maintained, replace the hose or intake plenum.

Then go to STEP 6.

STEP 5. Check the purge solenoid-to-air intake plenum hose for vacuum leakage.

(1) Plug the purge solenoid-to-air intake plenum hose at the purge solenoid side.

(2) Disconnect the purge solenoid-to-air intake plenum hose at the air intake plenum side.

(3) Connect a hand vacuum pump to disconnected hose end.

(4) Apply vacuum, and check if the vacuum is maintained.

0 If maintained, go to STEP 6.

0 If not maintained, replace the hose. Then go to STEP 6.

STEP 6. Performance test.

NOTE: Fuel temperature should be lower than 40°C (104°F) during the performance test.

In this step, verify if the EVAP system works properly, or determine which area of the evaporative emission system has a failure.

Caution As a 0 - 6.2 kPa (0 - 0.90 psi) range vacuum gauge is used, the gauge may be broken if excessive vacuum pressure is applied. Do not apply a vacuum of more than 2.9 kPa (0.42 psi).

To achieve the performance test efficiently, a mechanical vacuum gauge [0 - 6.2 kPa (0 - 0.90 psi) range] and scan tool MB991502 should be used, and the engine to generate vacuum.

(1) Install a mechanical vacuum gauge [0 - 6.2 kPa (0 - 0.90 psi) range] between the EVAP purge solenoid valve and the purge hose that comes from the evaporative emission canister.

(2) Before starting the performance test, set the vehicle in the following condition.

0 Engine coolant temperature: 80 - 90°C (1 76 - 203” F) 0 Lights and all accessories: OFF 0 Transmission: “N” or “P” position

(3) Select the item TANK PRS SNSR (data list 73) on scan tool MB991502 to see the fuel tank differential pressure sensor output.

(4) Run the engine at idle.

(5) Using locking pliers, pinch the hose between the purge solenoid and the intake plenum to close the purge flow, as a preparation of the performance test.

(6) Using another locking pliers, pinch the vent hose between the evaporative emission canister and the vent solenoid.

Momentary, remove the locking pliers at the purge hose;

this will cause the vacuum build up in the EVAP system.

(7) The engine vacuum comes from the purge port through the purge solenoid.

NOTE: During this operation, the purge solenoid may turn off but will resume in operation in about 20 seconds.

Operation of the purge solenoid can be checked by needle fluctuation of the mechanical vacuum gauge.

(8) Watcn the -vacuum reading on the mechanical vacuum gauge and scan tool MB991502.

(9) When the vacuum reading reaches 2.9 kPa (0.42 psi) on the mechanical vacuum gauge and -2.9 kPa (-0.42 psi) on scan tool MB991502, pinch the hose between the purge solenoid and the intake manifold plenum using another locking pliers; this stops the application of vacuum and seals the EVAP system for the leak test.

NOTE: If there is a system failure, either of both vacuum readings may not reach to the above specifications. In this case, it is not necessary to pinch off the purge hose as shown. Refer to the performance test results table below for further steps.

(10)After an elapsed time of 20 seconds, check the fuel tank differential pressure reading on scan tool MB991502.

OK: Change in pressure reading is 0.4 kPa (0.06 psi) or less [holding -2.5 kPa (-0.36 psi) or more vacuum].

Performance test result table:

SCAN TOOL MB991502 READING

MECHANICAL VACUUM GAUGE READING

Reaches -2.9 kPa (-0.42 psi) and vacuum drops not more than 0.4 kPa (0.06 psi) in 20 seconds.

Reaches 2.9 kPa (0.42 psi).

Does not reach -2.9 kPa (-0.42 psi).*

Reaches 2.9 kPa (0.42 psi).

Does not reach -2.9 kPa (-0.42 psi).

Does not reach 2.9 kPa (0.42 psi).

Reaches -2.9 kPa (-0.42 psi) but vacuum drops more than 0.4 kPa (0.06 psi) in 20 seconds.

Reaches 2.9 kPa (0.42 psi).

NOTE *: If there is a blockage, scan tool MB991502 reading can be positive value (positive pressure) due to heat of return fuel from the engine.

I STEP 7. Vacuum reading on both the mechanical gauge and scan tool MB991502 reaches the specifications and satisfy the specifications after 20 seconds:

EVAP system is properly working at the moment. The cause is an intermittent electrical wiring problem. Refer to GROUP 00, How to Use Troubleshooting/lnspection Service Points.

STEP 8. Vacuum reading on the mechanical gauge reaches 2.9 kPa (0.42 psi) but scan tool MB991502 does not reach -2.9 kPa (-0.42 psi) :

(1) If the vacuum reading on the gauge reaches 2.9 kPa (0.42 psi) but the reading on scan tool ME3991502 does not reach -2.9 kPa (-0.42 psi), either a system blockage or a bad differential pressure sensor may be the cause.

(2) To determine if there is a blockage in the system, remove the fuel cap.

0

GO TO

RESULT

Step 7

Satisfactory.

No leak nor blockage detected.

Blockage in the system or ba'd differential pressure sensor.

Step 8

Step 11

Large leak in EVAP system.

Step 12

Small leak in EVAP system.

If the vacuum reading on the vacuum gauge [at this point 2.9 kPa (0.42 psi)] remain the same, there is a blockage in the system, and go to Step 8.

If the reading drops to about 0 kPa (0 psi), there is no blockage in the EVAP system. Then the fuel tank differential pressure sensor need to be tested.

Go to Step 9.

‘

STEP 9. Check the fuel tank differential pressure sensor.

(1) Remove the floor carpet and floor cover.

(2) Remove the fuel tank differential pressure sensor. Do not disconnect the connector at this point.

(3) Connect the fuel tank differential pressure sensor to a hand vacuum pump and mechanical vacuum gauge [0

- 6.2 kPa (0 - 0.90 psi) range].

(4) Turn the ignition switch “ON.” (5) Using the scan tool, check MFI data list item 73: TANK PRS SNSR while applying vacuum.

i f / w V0414AA

If not correct, go to Step 13.

If correct, it can be assumed that this malfunction is caused by an intermittent electrical wiring problem. Refer to GROUP

00. How to Use Troubleshooting/lnspection Service Points.

STEP 10. System blockage inspection.

(1) Disconnect the number 1 and 2 hoses shown in the illustration, check the mechanical vacuum gauge reading.

If the vacuum reading does not drop, then the blockage is not in the fuel tank.

(2) Disconnect one portion of the EVAP system at a time working towards the front of the vehicle until blockage is found (number 1 to 5 hoses in the illustration).

(3) Repair the location of the blockage and go to Step 12.

PURGE SOLENOID c *

VENT1 LATl ON S 5

EVAPORATIVE EMISSION CANISTER FUEL TANK B03’0115

STEP 11. Vacuum readings on both the mechanical gauge and scan tool MB991502 do not reach the specifications [2.9 kPa (0.42 psi) and -2.9 kPa (-0.42 psi)]:

This condition shows that there is a significant leakage in the system. The inspection procedure for the large system leakage is the same as the small leakage test in Step 12.

1 f 0.1

1349-68

STEP 12. Vacuum readings on both the mechanical gauge and scan tool MB991502 do not reach the specification [2.9 kPa (0.42 psi) and -2.9 kPa (-0.42 psi)] but do not maintain the vacuum.

This condition shows that there is a slight leakage in the system. Follow the procedure below to locate the source of the leak.

(1) The fuel cap relief valve inspection.

a. Remove the fuel cap and install the fuel tank filler tube adapter in the emission system tester kit in place of the fuel cap.

b. Plug the nipple on the fuel tank filler tube adapter.

c. Repeat the performance test. If the EVAP system holds the vacuum, then the fuel cap is faulty. Replace the fuel cap, and go to Step 18.

(2) To find the vacuum leakage in the system, clamp the number 1 and 2 hoses shown in the illustration. Repeat the performance test. This will determine if the vacuum leak is either in the fuel tank area or in the rest of the system.

NOTE: In this case, as we clamped off the vacuum hose connecting to the fuel tank, scan tool MB99 1502 reading will not change. Please use the mechanicalgauge reading.

1 A0320089

V S / 5

- I-] ’ EVAPORATIVE EMISSION CANISTER FUEL TANK B03’0115

0 If the EVAP system hold the vacuum leak is in the fuel tank area. To locate the leakage, pressurize the EVAP system to 3.4 kPa (0.49 psi) and look for leaky area using the ultrasonic leak detector in the Evaporative Emission System Tester. After repairing the leakage, go to Step 18.

0 If the vacuum leak still exists, the leak is at other than fuel tank area.

(3) Clamp off the vacuum hose one component at a time working towards the front of the vehicle until leakage is found (number 1 to 5 hoses shown in the illustration).

(4) Repair the location of the leakage and go to Step 18.

STEP 13. Check the circuits at fuel tank differential pressure sensor connector E-23.

(1) Disconnect connector E-23 and measure at the harness side.

(2) Turn the ignition switch “ON.” (3) Measure voltage between terminal 3 and ground.

0 Voltage should be between 4.8 and 5.2 volts.

(4) Turn the ignition switch “OFF.”

E-23 HARNESS SIDE CONNECTOR

T 6 0 8 7 A A

(5) Check for continuity between terminal 2 and ground.

0 If all checks above meet the specifications, go to Step 14.

If any check above do not meet the specifications, go to Step 16.

E-23 HARNESS SIDE CONNECTOR

T 6 0 8 8 A A

I CONNECTOR: E-23

STEP 14. Check the harness wire between fuel tank differential pressure sensor connector E-23 (terminal

1) and ECM connector 6-38 (terminal 61).

NOTE: Check the wire after checking intermediate connectors B-36 and E-22. If intermediate connectors 8-36 and E-22 are faulty, repair or replace them. Refer to GROUP OOE, Harness Connector Inspection. Then go to Step 18.

If the wire between fuel tank differential pressure sensor connector E-23 (terminal 1) and ECM connector 6-38 (terminal

61) is not damaged, go to Step 15.

If the wire between fuel tank differential pressure sensor connector E-23 (terminal 1) and ECM connector B-38 (terminal

61) is damaged, repair it. Then go to Step 18.

B16MO440

CONNECTORS: B-37, B-38

I I CONNECTOR: E-23

STEP 15. Check harness connector E-23 at the fuel tank differential pressure sensor for damage.

If harness connector E-23 is damaged, repair or replace it.

Refer to GROUP OOE, Harness Connector Inspection.

If harness connector E-23 is not damaged, check ECM connectors B-37 and 8-38, and repair or replace as required.

Refer to GROUP OOE, Harness Connector Inspection. If ECM connectors B-37 and B-38 are in good condition, replace the ECM. Then go to Step 18.

I B16M0440 I

There should be continuity (0 B).

I CONNECTOR: E-23

-

STEP 16. Check the harness wire between fuel tank differential pressure sensor connector E-23 and ECM connectors 8-37 and B-38.

NOTE: Check the wire after checking the intermediate connectors 8-36 and E-22. If the intermediate connectors B-36 and E-22 are faulty, repair or replace them. Refer to GROUP OOE. Harness Connector Inspection. Then go to Step 18.

If the wire between fuel tank differential pressure sensor connector E-23 and ECM connectors B-37 and B-38 are not damaged, go to Step 17.

B16MO440

If the wire between fuel tank differential pressure sensor connector E-23 and ECM connectors B-37 and 8-38 are damaged, repair it. Then go to Step 18.

I CONNECTORS: 8-37. B-38

STEP 17. Check harness connectors 8-37 and B-38 at the ECM.

If harness connectors B-37 and 8-38 are damaged, repair or replace it. Refer to GROUP OOE, Harness Connector Inspection.

if harness connectors B-37 and 8-38 are not damaged, replace the ECM. Then go to Step 18.

STEP 18. Confirmation test.

After system failures are repaired, repeat the Evaporative Emission System Leak Monitor test (Step 3) to check that the EVAP system operates correctly.
