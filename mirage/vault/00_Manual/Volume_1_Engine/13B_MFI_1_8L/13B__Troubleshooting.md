---
type: manual_section
vehicle: '[[Car_Mitsubishi_Mirage_1999]]'
title: MFI 1.8L (впрыск) — Troubleshooting
title_en: MFI 1.8L — Troubleshooting
chapter_code: 13B
chapter: MFI 1.8L (впрыск)
section: Troubleshooting
section_index: page-8
volume: Volume 1
source_pdf: 13B MFI 1.8L.pdf
page_range: 8-64
page_count: 57
topics:
- fuel_injection
- diagnostics
aliases:
- 13B Troubleshooting
- 13B-Troubleshooting
- MFI 1.8L Troubleshooting
related_parts: []
related_issues: []
last_verified: '2026-05-08'
tags:
- manual
- fuel_injection
---

# MFI 1.8L (впрыск) — Troubleshooting

> **Глава:** `13B` MFI 1.8L  
> **Источник:** `13B MFI 1.8L.pdf` (стр. 8-64)  
> **Авто:** [[Car_Mitsubishi_Mirage_1999]]

---

TROUBLESHOOTING 13100850430

DIAGNOSTIC TROUBLESHOOTING FLOW

customer.

~-

~ _ _ _ _ _ ~ _ _

1 I ~ ---

I Reoccurs Does not reoccur.

1

i Read the diagnostic trouble code (Refer to P.138-19.) Read the diagnostic trouble code (Refer to P.13B-19.)

~ ~~ code displayed.

r- code displayed

-

-7-

L _ _ _ ~ ~

---

No diagnostic trouble code Diagnostic trouble Diagnostic trouble I No diagnostic trouble displayed or communication A ~ _ - _ _ _ _ _ _ _ -

I 1

~~ Record the diagnostic trouble code, erase the I diagnosis code memory (Refer to P.13B-19.) -

-J 1 Recheck trouble symptom.

Y

Read the diagnostictrouble codes. (Refer to P.138-19.) 1

Diagnostic trouble code displayed No diagnostic trouble code displayed.

;Refer to the INSPECTION CHART F O R z N O S T c - 1 PROUBLE CODES (Refer to P.138-22) ~ iNTERMl~~N~MALFUNCTIONS (Refer to C R O U i O ’ How to Cope with Intermittent Malfunctions) ~

--

, code displayed.

-I Service' Engine Soonl Malfunction Indicator DIAGNOSTIC TEST MODE 13100860655

SERVICE ENGINE SOON/MALFU N CTlON INDICATOR LAMP Among the on-board diagnostic items, a Service Engine Soon/ Malfunction Indicator Lamp illuminates to notify the driver of an emission control malfunction.

However, when an irregular signal returns to normal and the engine control module judges that it has returned to normal, the Service Engine Soon/Malfunction Indicator Lamp is switched off.

Moreover, when the ignition switch is turned off, the lamp is switched off. Even ifthe ignition switch is turned on again, the lamp does not illuminate until the malfunction is detected.

Immediately after the ignition switch is turned on, the Service Engine Soon/Malfunction Indicator Lamp is lit for 5 seconds to indicate that the Service Engine Soon/Malfunction Indicator Lamp operates normally.

Items Indicated by the Service Engine Soon/Malfunction ldicator Lamp

~- DCT No.

~ Items

- --77

-

-~ Engine control module (ECM) malfunction _ _ _ ~ P 0 1 0 0 i u m e air flow circuit malfunction

- _ _ ~ p0105- T o m e t r i c pressure circuit malfunction

~-

- p~ ~ ~~ ~

-~ ~- ~- ~-

PO110 1 Intake air temperature circuit malfunction

Pol 1 5 7 E n g i n e coolant temperature circuit malfunction

PO1 20 1 Throttle position circuit malfunction

_ _ _ ~ _ _ _ _ ~ a

-T

~~~

PO1 2 5 * T s s i v e t i m e to enter closed loop fuel control

PO1 30

Heated oxygen sensor ci

Heated oxygen sensor heater circuit malfunction (sensor 1) ~- p ~ ~ _ ~ ~ _ _

_p-- ~~~

PT36-heated oxygen sensor circuit malfunction (sensor 2)

Heated oxygen sensor heater circuit malfunction (sensor 2)

PO1 41

Fuel trim malfunction __-____ ~

PO1 70

PO201 ~ Injector circuit malfunction cylinder-1

PO202 1 Injector circuit malfunction cylinder-2

~-

- ~- ~

-

- ~p

-

- ~

- p

P 0 2 0 3 Y e c t o r circuit malfunction cylinder3

PO204 -'injector

- circuit _ _ p ~ malfunction ~~~~ cylinder4

- ~- _ _ _

- ~

-

E 3 O h T n d o m misfire detected

-~ ppp-pp____--- ~ _

- ~-

P0301*iCvlinder 1 misfire detected

~ _ _ _ _ _ -__-- 7

-p ~ ~ _ _ _ _ _ p p ~ ~

- p

- _ _ _ ~ … ---- ~ ~~ ~

~- P0302~ ~ Cylinder 2 misfire detected

~

- -_____-~- -~ -

-~

P 0 3 0 3 n C y l i n d e r 3 misfire detected

_ ~ p

- p p ~

-

P0304* 1 Cylinder 4 misfire detected

~-

- ~ _ _ _ v-

- p ~ ~

-- -

PO335 1 Crankshaft position sensor circuit malfunction

~

- p

-_____ ~- ~

PO340 Camshaft position sensor circuit malfunction

PO400 Exhaust gas recirculation flow malfunction

PO403 Exhaust gas recirculation solenoid malfunction

I DCT NO.

Items

_ _ ~ _ _ _ ~ __ __ Catalyst system efficiency below threshold <Federal>

~~ up catalyst efficiency below threshold <California>

- PO442 t PO443

~ Evaporative emission control system leak detected

~ Evaporative emission control system purge control valve circuit malfunction

- ~ _ ~ _ _ _ _ _ _ _ _ _ _ _ ~ ~ _ _ _ _ _ ~ ~

I Evaporative emission control system vent control malfunction

PO446

’ Evaporative emission control system pressure sensor malfunction

-~ ~ ~~

PO450

I Evaporative emission control system leak detected (Gross leak)

_ _ _ _ _ _ ~ _ _ _ _ _ _ _ _ ~ .

PO455

Idle control system malfunction

Closed throttle position switch malfunction

- ~~ , PO51 0

I PO551 r Po705

1 Power steering pressure sensor circuit range/performance

Transmission range sensor circuit malfunction (PRND2L input)

I PO71 0 , Transmission fluid temperature sensor circuit malfunction

~ ~~~ ~~ ~~ ~ ~ lnputlturbine speed sensor circuit malfunction _______________~

PO71 5

PO720 ~ Output speed sensor circuit malfunction

I 1 PO725 I Engine speed input circuit malfunction

~ ~ _ _ _ _ _ ~ ~ ~

I PO740 ’ Torque converter clutch system malfunction I I PO750 ~ Shift solenoid A malfunction I I PO755 1 Shift solenoid B malfunction I

PO760 ~ Shift solenoid C malfunction

I ~ 7 G i f t solenoid D malfunction

Serial communication link malfunction

P1600

I P1751 , A F control relay malfunction

- 1

Throttle position input circuit malfunction

P1795

MFI <I

,Y * ”-..*.we .-

ON-BOARD DIAGNOSTICS

1 The engine control module monitors the input/out- put signals (some signals all the time and others under specified conditions) of the engine control module.

When a malfunction continues for a specified time or longer after the irregular signal is initially moni- tored, the engine control module judges that a mal- function has occurred.

After the engine control module first detects a mal- function, a diagnostic trouble code is recorded when the engine is restarted and the same malfunction is re-detected. However, for items marked with a ‘*”, a diagnostic trouble code is recorded on the first detection of the malfunction.

There are 49 diagnostic items. The diagnostic re- sults can be read out with a scan tool.

Since memorization of the diagnostic trouble codes is backed up directly by the battery, the diagnostic results are memorized even if the ignition key is turned off. The diagnostic trouble codes will, howev- er, be erased when the battery terminal or the en- gine control module connector is disconnected.

Data 
- Unit

Diagnostic trouble code during data recording

-

In addition, the diagnostic trouble code can also be erased by turning the ignition switch to ON and sending the diagnostic trouble code erase signal from the scan tool to the engine control module.

Caution If the sensor connector is disconnected with the ignition switch turned on, the diagnostic trouble code is memorized. In this case, send the diagnostic trouble code erase signal to the engine control module in order to erase the diagnostic memory.

The 49 diagnostic items are all indicated sequential- ly from the smallest code number.

The engine control module records the engine oper- ating condition when the diagnostic trouble code is set. This data is called “Freeze-frame” data.

This data can be read by using the scan tool, and can then be used in simulation tests for trouble- shooting. Data items are as follows.

0 Closed loop 0 Open loop-drive condition 0 Open loop-DTC set

I

OBD-I1 DRIVE CYCLE All kinds of diagnostic trouble codes can be monitored by carrying out a short drive in accordance with the following 6 drive cycle patterns. In other words, doing such a drive allows to regenerate any kind of trouble which involves illuminating the Service Engine Soon/Malfunction Indicator Lamp and to check the repair procedure has eliminated the trouble (the Service Engine Soon/Malfunction Indicator Lamp is no longer illuminated).

Caution Two mechanics should always get on the vehicle when carrying out a drive test.

Catalytic converter monitor (P0420, P0421) Test requirements/procedure

1. All of the following requirements should be met when carrying out a drive test.

(1) Atmospheric temperature: -10°C (14°F) or more (2) Condition of A/T

0 Selector lever position: D range

(3) A/C switch: OFF

2. One trip monitor will be completed by driving according to the steps below (from start to switch off).

It will take 20 minutes.

*1: Start the engine, and accelerate gradually to 72 km/h (45 mph) or more.

*2: Preparation period; continue driving between 72 and 97 km/h (45 and 60 mph) for 300 seconds.

Brake may be applied for this period if it continues for only a few seconds.

*3: Decelerate to 56 - 64 km/h (35 - 40 mph).

+4: Drive between 56 and 64 km/h (35 and 40 mph) at a constant throttle angle (by not moving the throttle pedal as much as possible) for 90 seconds or more during monitor.

*5: Decelerate with the throttle valve fully closed (Brake may be applied for this period). After the vehicle is being decelerated for ten seconds, accelerate gradually to 56 - 64 km/h (35 - 40 6:

Decelerate and stop the vehicle. Then turn off the ignition switch.

mph).

Drive cycle pattern

300 sec or more

90 sec. or more

Full Full Full Full Full deceleration deceleration deceleration deceleration deceleration 7 F U 1 9 5 6

Caution Vehicle speed and throttle opening angle should be within the shaded rage.

MFI <I

Evaporative emission control system leak monitor (P0422, P0450, P0455) rest requirements/procedure /, 1.

All of the following requirements should be met when carrying out a drive test.

(1) Engine coolant temperature: 45°C (113°F) or less (before starting drive test, engine stopped) (2) Atmospheric temperature: 5°C (41°F) or more, 45°C (113°F) or less (3) Condition of A/T:

0 0 Overdrive switch: ON One trip monitor will be completed by driving according to the steps below (from start to switch off).

(It takes approx. 8 minutes.) *1: Check that both engine coolant temperature and air intake temperature satisfy requirement 1 (engine stopped).

*2: Monitor preparation period; Start the engine, and accelerate to 89 - 97 km/h (55 - 60 mph).

For this period, acceleration, deceleration, or braking may be carried out.

Continue driving between 89 and 97 km/h (55 and 60 mph) for 200 seconds or more. For this period, braking or throttle operation may be carried out if vehicle speed is within the specified value.

+3:Drive between 89 and 97 km/h (55 and 60 mph) at a constant throttle angle (by not moving the throttle pedal as much as possible) for 150 seconds or more during monitor. Moreover, do not turn the steering wheel suddenly.

*4: Decelerate and stop the vehicle. After stop, turn off the ignition switch.

Selector lever position: D range

2.

Drive cycle pattern

i 97 (60) -

Vehicle speed 64 (40) km/h (mph)

32 (20)

I I I I I I

I ;

Ignition switch: OFF t Engine start

I I I t

Caution

~ Drive within the shaded area in the graph above.

7FU1957

' " A

Heated oxygen sensor monitor (PO1 30, PO1 36) Test requirements/procedure Test requirements/procedure (1) Engine coolant temperature: 80°C (176°F) or more (Engine fully warmed up) (2) Atmospheric temperature: -1 0°C (1 4" F) or more (3) Condition of An:

0 Selector lever position: D range

One trip monitor will be completed by driving according to the steps below (from start to switch off).

It will take 5 minutes.

*I: After warming up the engine, turn off the ignition switch.

*2: Start the engine, and accelerate to 56 - 64 km/h (35 - 40 mph).

+3: Drive between 56 and 64 km/h (35 and 40 mph) at a constant throttle angle (by not moving the throttle pedal as much as possible) for 120 seconds or more during monitor. Moreover, do not turn the steering wheel suddenly.

*4: Decelerate and stop the vehicle. Then turn off the ignition switch.

Drive cycle pattern

4 D

0 L *l

- u

50t I h

I

loo r

I I I I

<Reference> Throttle opening angle (%)

Caution Vehicle speed and throttle opening angle should be within the shaded rage.

I I I t I ignition switch:

I

OFF

I I

7FU1958

i 3 ~ - I 5

Exhaust gas recirculation (EGR) system monitor (P0400) rest req u i rementslproced ure

1

1. All of the following requirements should be met when carrying out a drive test.

(1) Engine coolant temperature: 80°C (176°F) or more (Engine fully warmed up) (2) Atmospheric temperature: 5°C (41°F) or more (3) Condition of A/T:

0 Selector lever position: D range

(4) A/C switch: OFF

2. One trip monitor will be completed by driving according to the steps below (from start to switch off).

It will take approx. 10 minutes.

*l: After warming up, turn off the ignition switch.

*2: Start the engine, and accelerate to 56 - 64 km/h (35 - 40 mph).

+3: Close the throttle fully from 2000 - 3000 r/min with the clutch engaged cM/T>, and then decelerate to 900 r/min without applying brakes. Moreover, do not turn the steering wheel or switch on or off the lights.

*4: Accelerate to 56 - 64 km/h (35 - 40 mph), and continue driving for 20 seconds. (After 1st monitor (deceleration), wait for 20 seconds or more until the next monitor (deceleration) starts). Then repeat +3 and *4 steps eight times.

*5: Decelerate and stop. Then turn off the ignition switch.

Drive cycle pattern

56 - 64 km/h (35 - 40 rnph) M/T: 4th speed . Do not decelerate suddenly.

20 sec. or more

-,- Vehicle speed km/h (rnPi-0

I I I I I I 1

100

<Reference> Throttle opening 50 angle (%)

0

Full Full Full Full decel- decel- decel- decel- eration eration eration eration

Caution Vehicle speed should be within the shaded rage.

1 1 I t Ignition switch: OFF

I 1 I I I I I 1 I I I I I I I I I I I I I

Full Full 7FU1959 decel- decel- eration eration

Fuel trim monitor (P0170) Test requirements/procedure

1. All of the following requirements should be met when carrying out a drive test.

(1) Engine coolant temperature: 80°C - 97°C (176 - 207°F) (Engine fully warmed up) (2) Atmospheric temperature: -10°C (14°F) or more, 60°C (140°F) or less (3) Condition of 4/T

0 Selector lever position: D range

2. One trip monitor will be completed by driving according to the steps below (from start to switch off).

It will take 35 minutes.

kl: After warming up the engine, turn off the ignition switch.

*2: Start the engine, and accelerate to 89 - 97 km/h (55 - 60 mph).

+3: Drive between 89 and 97 km/h (55 and 60 mph) for 30 minutes or more during monitor. Moreover, do not drive the vehicle at the constant speed range for 120 seconds or more. (Accelerate or decelerate lightly within the 120 seconds. Brake may be applied, but avoid decelerating or accelerating suddenly).

*4: Decelerate and stop the vehicle. Then turn off the ignition switch.

Drive cycle pattern

30 min or more 89 - 97 km/h (55 - 60 mph) M/T:

5th speed

Vehicle speed km/h (rnph)

<Reference> Throttle opening angle (%)

5 0 ~ 0

Caution Vehicle speed and throttle opening angle should be within the shaded rage.

I I

Ignition I switch:

OFF

I I I

7FU1960

Other monitors

0 Misfire (P0300, P0301, P0302, P0303,

/' P0304)

0 Evaporative emission control system (P0440) 0 Idle air control system (P0505) 0 Manifold differential pressure sensor (P1400) 0 Excessive time to enter closed loop fuel control (POI 25) Throttle position sensor (P0120) 0 Barometric pressure sensor (PO1 05) 0 Intake air temperature sensor (POIIO) 0 Serial communication link <A/T> (P1600) Crankshaft position sensor (P0335) Camshaft position sensor (P0340)

Test req uirementdproced u re

1. All of the following requirements should be met when carrying out a drive test.

(1) Engine coolant temperature: 80°C (176°F) or more (Engine fully warmed up) (2) Atmospheric temperature: 5°C (41°F) or more (3) Condition of A/T

Selector lever position: D range

2. One trip monitor will be completed by driving according to the steps below (from start to switch off).

It will take approx. 10 minutes.

*l: After warming up, turn off the ignition switch.

*2: Start the engine, accelerate to 56 - 64 km/h (35 - 40 mph), continue driving for 300 seconds or more at that speed range and stop. Moreover, brake or throttle may be applied for this period.

*3: After stopping the vehicle, continue idling for 300 seconds or more, and then turn off the ignition switch. Moreover, the vehicle should be set to the following conditions for idling.

A/C switch: OFF

I Lights, electric cooling fan and all accessories: OFF

Transaxle: Neutral (A/T for P range) Steering wheel: Straight-forward position

Volume air flow sensor (PO1 00) Engine coolant temperature sensor (PO1 15) Closed throttle position switch (PO51 0) Generator FR terminal circuit (PI 500) 0 2 sensor circuit (P0130, P0136) 0 2 sensor heater circuit (P0135, P0141) EGR solenoid (P0430) Evaporative emission purge solenoid (P0443) Injector circuit (P0201, P0202, P0203, P0204) Evaporative emission ventilation solenoid (P0446)

0 0

0

0

i":..

I

Drive cycle pattern

- b

Vehicle speed km/h (mph)

I 100 r

<Reference> Throttle opening angle (%)

NOTE Drive according to the graph above.

4 c

*3

7FU1961

i 3 ~ - 1

READINESS TEST STATUS The ECM monitors the following main diagnosis items and records whether the evaluation passing or failing in the past.

These records can be read with a scan tool. (When using MUT-11, “Complete” will appear to indicate that the evaluation has been completed.) These records will all be reset if the battery terminal is disconnected or the DTC are erased, etc.

To complete the readiness test status which has been reset, the “OBD-I1 Drive Cycle” related to a diagnosis item should be carried out.

NOTE If the vehicle is normal, the readiness test status will be complete by carrying out the “OBD-I1 Drive Cycle” once. If the ECM detects a malfunction of the vehicle, the readiness test status will be complete by carrying out the “OBD-I1 Drive Cycle” twice. In addition, after all readiness test status are complete, a DTC should be interrogated. If a DTC is stored, perform repair by referring to the relevant DTC procedures.

Then complete the readiness test status by repeating the “OBD-I1 Drive Cycle”. If a DTC is not stored, no further action will be neede.

0 Catalyst: P0420, PO421 0 Evaporative system: P0442, PO455 0

Heated oxygen sensor: P0130, PO136 Heated oxygen sensor heater: P0135, PO141

0 EGR system: PO400

4

HOW TO READ AND ERASE DIAGNOSTIC TROUBLE CODES Caution

1. If battery voltage is low, diagnostic trouble codes may not be output. Be sure to check the battery and charging system before continuing.

2.

If the battery is disconnected or if the engine control module connector is disconnected, the diagnostic trouble code memory will be erased. Do not discon- nect the battery or engine control module until after the diagnostic trouble codes are recorded.

3. Turn the ignition switch off before connecting or dis- connecting the scan tool.

NOTE If a DTC is erased, its “freeze frame” data will be also erased and the readiness test status will be reset. If necessary, take a note of the “freeze frame” data before erasing the DTC.

1. Connect the scan tool to the data link connector, and read the diagnostic trouble codes.

2. Repair the malfunction while referring to the INSPECTION CHART FOR DIAGNOSTIC TROUBLE CODES.

3. Turn the ignition switch to OFF and then back to ON again .

4. Erase the diagnostic trouble codes using the scan tool.

5. Confirm that the diagnostic trouble code reading show is normal.

I AOOM0053

PROVISIONAL DTCs [MUT-I1 OBD-I1 Test Mode - Results (Mode 5)] MUT-I1 will display the Provisional DTCs reported by ECM if the ECM detects some malfunction for “Misfire”, “Fuel System” and “Comprehensive” monitoring during a SINGLE Driving Cycle.

The intended use of this data is to assist the technician after a vehicle repair, and after clearing diagnostic information, by reporting test result after a SINGLE Driving Cycle.

Note that the test results reported by this mode do not necessarily indicate a faulty component/system. If test results indicate a failure after ADDITIONAL (consecutive) driving, then the MIL will be illuminated and a DTC will set.

QIAGNOSTIC BY DIAGNOSTIC TEST MODE I1 (INCREASED SENSITIVITY) When mode I1 is selected with MUT-11, the Service Engine Soon/Malfunction Indicator Lamp will light when the ECM first detects the trouble. (Note that this is only for engine related trouble.) At the same time, the relevant diagnostic trouble codes will be registered.

In respect to the comprehensive component electrical faults (opens/shorts), the time for the DTC to be registered after the fault occurrence is shortened (4 sec. + 1 sec.) With this, the confirmation of the trouble symptom and the confirmation after completing repairs can be reduced.

To return to the normal mode I after mode I1 has been selected once, the ignition switch must be turned OFF once or mode I must be reselected with the MUT-11. The DTC, readiness test status and freeze frame data, etc., will be erased when mode I is returned to, so record these if necessary.

(1) Using the scan tool, changeover the diagnostic test mode of the engine control module to DIAGNOSTIC TEST MODE 11. (INCREASED SENSITIVITY) (2) Road test the vehicle.

(3) Read the diagnostic trouble code in the same manner as “READ OUT OF DIAGNOSTIC TROUBLE CODE” and repair the malfunctioning part.

(4) Turn OFF the ignition switch.

NOTE Turning OFF the ignition switch will cause the ECM to changeover from the diagnostic test mode I1 to the diagnostic test mode I.

i 3 ~ - 2

Carry out inspection by means of the data list and the actuator test function.

If there is an abnormality, check and repair the chassis harnesses and components.

After repairing, re-check using the scan tool and check to be sure that the abnormal input and output have re- turned to normal as a result of the repairs.

Erase the diagnostic trouble code@).

Remove the scan tool.

Start the engine again and road test to confirm that the problem is eliminated.

NOTE Refer to P.13B-125 for Data list.

Refer to P.13B-130 for Actuator tests.

4.

5.

AOOM0053

FAIL-SAFE/BACKUP FUNCTION TABLE 13100910213 When the main sensor malfunctions are detected by the diagnostic test mode, the vehicle is controlled by means of the following defaults.

Control contents during malfunction

Malfunctioning item

Volume air flow sensor

Uses the throttle position sensor signal and engine speed signal (crankshaft position sensor signal) for basic injector drive time and basic ignition timing from the pre-set mapping.

Fixes the IAC motor in the appointed position so idle air control is not performed.

1.

2.

~~ ~ ~~~ ~~

Intake air temperature sensor

Controls as if the intake air temperature is 25°C (77°F).

Throttle position sensor (TPS)

No increase in fuel injection amount during acceleration due to the unreliable throttle posi- tion sensor signal.

- -~

~~

Engine coolant temperature sensor

Controls as if the engine coolant temperature is 80°C (176°F).

Camshaft position sensor

Injects fuel into the cylinders in the order 1-3-4-2 with irregulartiming. (After the ignition switch is turned to ON, the No. 1 cylinder top dead center is not detected at all.)

Controls as if the barometric pressure is 101 kPa (30 in.Hg) (sea level).

Barometric pressure sensor

Heated oxygen sensor <front>

Air/fuel ratio closed loop control is not performed

Performs the closed loop control of the air/fuel ratio by using only the signal of the heated oxygen sensor (front) installed on the front side of the catalytic converter.

Heated oxygen sensor <rear>

Generator FR terminal

No generator output suppression control is performed for the electrical load (to be oper- ated as an ordinary generator).

~~~~~ ~ ~ -~~

Misfire detection

The ECM stops supplying fuel to the cylinder with the highest misfiring rate if a misfiring that could damage the catalytic converter is detected.

'

INSPECTION CHART FOR DIAGNOSTIC TROUBLE CODES (FAULT TREE) 13100870757

~ Memory 1 Reference DTC No.

1 Diagnostic items 1 Check items (Remedy)

PO1 00 Volume Air Flow Circuit Malfunction 0 Harness and connector (If harness and connector are normal, replace volume air flow sensor assembly.)

PO1 05 Barometric Pressure Circuit Malfunction 0 Harness and connector (If harness and connector are normal, replace volume air flow sensor assembly.)

Retained i 13B-28 PO1 10 Intake Air Temperature Circuit Malfunction

0 Harness and connector 0 Intake air temperature sensor

~ - ~ _ _ _ _ _ ~

- I PO115

-

0 Harness and connector 0 Engine coolant temperature sensor

Engine Coolant Temperature Circuit Malfunction

R e t a i n e v PO1 20 Throttle Position Circuit Malfunction 0 Harness and connector 0 Throttle position sensor 0 Closed throttle position switch

0 2 sensor harness and connector !

Retained ~ 138-31

_ _

- ~ ~ _ _

- ~ ~

PO1 25 Excessive Time to Enter Closed Loop Fuel Control*

0 0 2 sensor (front) 0 0 Injector

PO1 30 0 2 Sensor Circuit Malfunction (Sensor 1) 0 Harness and connector [If harness and connector are normal, replace 0 2 sensor (front).]

0 Harness and connector e 0 2 sensor (front) heater Retained ~ 138-33

PO1 35 0 2 Sensor Heater Circuit Malfunction (Sensor 1)

PO1 36 Q2 Sensor Circuit Malfunction ' 0 Harness and connector

1 0 0 2 sensor (rear) (Sensor 2)

_ _ _ ~ t PO1 41

0 2 Sensor Heater Circuit To-Harness and connector Malfunction I 0 2 sensor (rear) heater (Sensor 2)

PO1 70 I Fuel Trim Malfunction 0 Volume air flow sensor output frequency Injector Fuel pressure Intake air leaks Engine coolant temperature sensor Intake air temperature sensor Barometric pressure sensor 0 2 Sensor Exhaust manifold cracks

I PO202

Retained ~ 138-37 0 Harness and connector 0 Injector Injector Circuit Malfunction - Cylinder 1

I Injector Circuit Malfunction - ' Cylinder 2

PO203 Injector Circuit Malfunction - ~

~ Cylinder3 I

' Injector Circuit Malfunction:

-1 ___-

Cylinder 4

Retained' ' 138-27

I

Retained 1 138-32

~

Retained

Retained

Diagnostic items I Check items (Remedy) I Memory

PO300 I :

Random Misfire Detected

Ignition coil Ignition power transistor Spark plug Ignition circuit Injector 0 2 Sensor Compression Ti m ing be1 t Crankshaft position sensor Air intake Fuel pressure Crankshaft position sensor circuit and connector

0 0

I 0

I .

0

Cylinder 1 Misfire Detected :

1 .

PO301

Ignition coil Ignition power transistor Spark plug Ignition circuit Injector 0 2 Sensor Compression Timing belt Crankshaft position sensor Air intake Fuel pressure Crankshaft position sensor circuit and connector

PO302 ~:

Cylinder 2 Misfire Detected

~ ~ ~- Cylinder 3 Misfire Detected PO303

PO304 Cylinder 4 Misfire Detected ~ l o

Retained PO335

(If harness and connector are normal, replace crankshaft position sensor.)

Malfunction

PO340 , F* Retained

PO400 Retained Exhaust Gas Recirculation Flow Malfunction

~ 0 EGR solenoid

' 0 EGR valve control vacuum I 0 Manifold differential pressure

I sensor

PO403 Retained

0 Harness and connector EGR solenoid

Exhaust Gas Recirculation Sole- noid Malfunction

~~

-

~~

PO420 Retained

PO421 Retained Warm Up Catalyst Efficiency Below Threshold <California>

0 Exhaust manifold (Replace the catalytic converter if there is no cracks, etc.)

PO442 Evaporative Emission Control System Leak Detected 0 Harness and connector 0 Evaporative emission purge

solenoid

0 Evaporative emission ventilation

solenoid

0 Vacuum hoses routing

Reference

E!age-

Retained

_ _ ~ _ _

- Retained

Retained

;*

---.- I..

I

Diagnostic items 1 Check items (Remedy) Memory eference age

DTC No.

Evaporative Emission Control ~ 0 Harness and connector Retained System Purge Control Valve Circuit Malfunction

PO443

0 Evaporative emission purge

solenoid _ _ _ ~ ~ ~ _ _

~~ PO446

~ ~~

0 Harness and connector 0 Evaporative emission ventilation

Evaporative Emission Control System Vent Control Malfunction

solenoid

Evaporative Emission Control System Pressure Sensor Malfunc- tion

0 Harness and connector 0 Fuel tank differential pressure

PO450

sensor

Evaporative Emission Control System Leak Detected (Gross Leak)

0 Harness and connector 0 Evaporative emission ventilation

PO455

solenoid

Vehicle Speed Sensor Malfunction Retained

0 Harness and connector 0 Vehicle speed sensor

PO500

Idle Control System Malfunction

PO505

0 Harness connector 0 Idle air control motor

Closed Throttle Position Switch ~ 0 Harness and connector Malfunction 1 0 Closed throttle position switch

PO510

Power Steering Pressure Sensor Circuit Range/Performance 0 Harness and connector 0 Power steering pressure switch

PO551

-__~ ~- -

Transmission Range Sensor Cir- cuit Malfunction (PRND2L Input) Retained

0 Harness and connector 0 Park/Neutral position switch

PO705

-- ~

PO71 0

_____- ~~ lnputlturbine Speed Sensor

~~ ~ 0 Harness and connector

PO71 5

0 Harness and connector 0 Pulse generator Output Speed Sensor Circuit Malfunction

PO720

Engine Speed Input Circuit i 0 Harness and connector Malfunction

~

-

PO725

Torque Converter Clutch System Harness and connector Malfunction Torque converter clutch solenoid

PO740

~____

Shift Solenoid A Malfunction 1 0 Harness and connector

~ 0 Low-reverse solenoid Retained

PO750

Shift Solenoid 8 Malfunction 0 Harness and connector 0 Underdrive solenoid

PO755

Shift Solenoid D and connector ~- ~ 1 0 Second solenoid

Shift Solenoid C Malfunction 0 Harness and connector

PO760

PO765

Overdrive solenoid

Manifold Differential Pressure 0 Harness and connector (MDP) Sensor Circuit Malfunction 1 0 MDP sensor Retained

P1400

Retained 0 Harness and connector Generator FR Terminal Circuit Malfunction

P1500

-___

-

~~

P1600

Serial Communication Link Malfunction

0 Harness and connector

~ _ _ _ _ ~ _ _ _

-__

P1720

Vehicle Speed Sensor Signal Line Malfunction

0 Harness and connector

~~

Retained

Retained

Retained

-~

Retained

Retained

Retained

-~

* Retained

Retained

Retained

Retained

Retained

Retained

Retained

Retained

Retained

Retained

-

-

i 3 ~ - 2 5

A .%"%, *-/

I DTC No.

' Diagnostic items Check items (Remedy)

I 1 ~ ~ _ _ _ _

- _ _ _ _ ~ _ _ A,T Control Relay Malfunction ' 0 Harness and connector

~ 0 A/T control relay

- 7 - ~~ Retained 138-89 1 I Malfunction 1 I P1795

' Throttle Position Input 0 Harness and connector

NOTE

1. Do not replace the engine control module (ECM) until a thorough terminal check reveals there are no short/open circuits.

2. After the ECM detects a malfunction, a diagnostic trouble code is recorded the next time the engine started and the same malfunction is re-detected. However, for items marked with a "*", the diagnostic trouble code is recorded on the first detection of the malfunction.

3. 0 2 : Heated oxygen sensor

4. Sensor 1 : indicates sensors which are mounted closest to the engine.

5. Sensor 2 : indicates sensors which are mounted next-closest to the engine.

~ Retained 1 138-89

: ' h

' ReDlace the ECM. -

INSPECTION PROCEDURE FOR DIAGNOSTIC TROUBLE CODES

Code No. PO100 Volume Air Flow Circuit Malfunction I Probable cause

Background 0 While the engine is running, the volume air flow sensor outputs a pulse signal which corresponds to the volume of air flow.

0 The engine control module checks whether the frequency of this signal output by the volume air flow sensor while the engine is running at or above the set value Check Area 0 Engine speed is not lower than 500 r/min.

Judgment Criteria 0 Sensor output frequency has continued to be 3.3 Hz or lower for 2 sec Check Area 0 Throttle position sensor voltage is 2V or lower.

0 Engine speed is not higher than 2000 rlmin.

Judgment Criteria 0 Sensor output frequency has continued to be 800 Hz or higher for 2 sec Check Area 0 Throttle position sensor voltage is 1 5 V or more 0 Engine speed is 2000 r/min or more.

Judgment Criteria 0 Sensor output frequency is 60 Hz or less for 2 seconds.

-~ Check the volume air flow sensor

- circuit (Refer to P13B-123, IN- 7 SPECTION PROCEDURE 47 ) i connected.

(Use the test 1 harness: MB991709).

1 . Voltage between 3 and ground 2. NG (Engine: idling)

0 Measure with the connector

OK: 2.2-3.2 V ~

2. Voltage between 7 and ground OK: 0-1 V (Engine idling) i 69v1_3,000 r/min) 1

0 Voltage between 19 and connected.

ground (Ignition switch ON) , OK. 6 - 9 V

~-

1 OK I

d

1 NG Replace the ECM.

0 Volume air flow sensor failed 0 Open or shorted volume airflow sensor circuit, or loose connector 0 Engine control module failed

ReDair

i A-58

Check trouble symptom.

I

Repair I

1

1 Replace thevolumeairflow sensor. 1

i 3 ~ 2

I Code No. PO105 Barometric Pressure Circuit Malfunction

- Background 0 The barometric pressure sensor outputs a voltage which corresponds to the barometric pressure 0 The engine control module checks whether this voltage is within a specified range Check Area 0 2 sec or more have passed since the starting sequence was completed 0 Battery voltage is not lower than 8V Judgment Criteria 0 Sensor output voltage has continued to be 4 5V or higher [corresponding to a barometric pressure of 114 kPa (17 psi) or higher] for 10 sec, or 0 Sensor output voltage has continued to be 0 195V or lower [corresponding to a barometric pressure of 50 kPa (7.4 psi) or lower] for 10 sec.

_______~ Measure at the volume air flow sen-

Measure at the volume air flow CNG+

sensor connector A-58

sor connector A-58 0 Measure with the connector connected (Use the test harness MB991709) 0 Voltage between 2 and ground (Ignition switch ON) O K 3 7-4 3 v [Altitude 0 m (0 ft )] 32-38 V [Altitude 1,200 m (3,937 ft )I

OK: Continuity I ~-

1 OK 1 S a s u r e T t the ECM connector

1 8-37

1 0 Measure with the connector

1 - connected.

* Voltage between 65 and ground (Ignition switch ON) OK: 3 7-4 3 V [Altitude 0 m (0 ft.)]

~ 32-38 V ' [(Altitude 1,200 m (3,937 ft )I 2

d Check the harness wire between 1 the ECM and the barometric pres- 1 sure sensor connector. Repair, if , necessary.

Probable cause

0 Barometric pressure sensor failed 0 Open or shorted barometric pressure sensor circuit, or loose connector 0 Engine control module failed

NG Check the followi-

- Repair

the ECM and the barometric pres- sure sensor connector.

- I

Code No. PO110 Intake Air Temperature Circuit Malfunction

0 Intake air temperature sensor failed 0 Open or shorted intake air temperature sensor circuit, or loose connector 0 Engine control module failed

-lL=1 Replace the volume air flow sensor.

1 Check the intake air temperature sen- 7-

~

- _ _ ~ ~ ~~ Background 0 The intake air temperature sensor converts the intake air temperature to a voltage and outputs it 0 The engine control module checks whether the voltage IS within a specified range Check Area 0 2 sec or more have passed since the starting sequence was completed.

Judgment Criteria 0 Sensor output voltage has continued to be 4 6V or higher [corresponding to an intake air temperature of -45°C (-49°F) or lower] for 2 sec, or 0 Sensor output voltage has continued to be 0 2V or lower [corresponding to an intake air temperature of 125°C (257°F) or higher] for 2 sec.

1 sor (Refer to P.138-148)

1

- I

Check the following connector:

fNG-

-_- Repair I , OK

connector A-58 0 Disconnect the connector, and measure at the harness side 0 Voltage between 6 and ground (Ignition switch ON) OK: 4 5 4 9 V 0 Continuity between 5 and ground

Check the harness wire between the ECM and the intake air temperature sensor connector.

~~ Replace the ECM.

-

Probable cause

-4 Repair

""- .

~

' Code No. PO115 Engine Coolant Temperature Circuit Malfunction

Background 0 The engine coolant temperature sensor converts the engine coolant temperature to a voltage and outputs it 0 The engine control module checks whether the voltage is within a specified range In addition, it checks that the engine coolant temperature (signal) does not drop while the engine is warming up Check Area 0 At least 2 seconds have passed since the ignition switch was turned on or the starting sequence was completed Judgment Criteria 0 Sensor output voltage has continued to be 4 6V or higher [corresponding to a coolant temperature of -45°C (-49°F) or lower] for 2 sec, or 0 Sensor output voltage has continued to be 0 1V or lower [corresponding to a coolant temperature of 140°C (284'F) or higher] for 2 sec Check Area Judgment Criteria 0 Sensor output voltage increased from a value lower than 1 6V to a value higher than 16V [Coolant temperature decreases from a higher than 40°C (104°F) temperature to a lower than 40°C (1 04°F) temperature ] 0 Then the sensor output voltage has continued to be 1 6V or higher for 5 min Check Area Judgment Criteria 0 About 5 min or more have passed for the engine coolant temperature to rise to about 40°C (104°F) after starting sequence was completed Note that time must not be counted when average output frequency of the volume air flow sensor is 70 Hz or lower, or when fuel is being shut off Check Area 0 Engine coolant temperature was 20°C (68°F) <Federal> or 7°C (446°F) <California> or more immediately before the engine was stopped at the last drive 0 Engine coolant temperatureis higher than 20°C (68°F) <Federal>or 7°C (44 6°F) <California> when the engine IS started Judgement Criteria 0 Engine coolant temperature fluctuates within 1°C (1 8°F) after 5 minutes have passed since the engine was started C However, time is not counted in any of the following conditions.

(1) Intake air temperature is 60°C (14OOF) or higher (2) Engine speed is 1,50Or/min or higher (3) Volumetric efficiency is 25% or lower (4) During fuel shut-off operation 0 Monitored only once per trip

1 sensor (Refer to 7 138-148.) I

NG ~ _ _ _ _ [Check the engine coolant temperature Replace

Check the following connector:

-1 NG

OK

*Repair 1537-

0 Disconnect the connector, and

I measure at the harness side.

1 Checktrouble s y m p t o m 2

~ 0 Voltage between 1 and ground (Ignition switch ON) OK: 4 5 4 9 V

1 Check the harness

~ 0 Continuity between 2 and ground

1 OK: Continuity I

i ECM and the engine coolant temperature sensor connector.

1 L -

-

+ Repair ' OK

I

A-60

OK 1

I

~ t F a c e the ECM

I A 1 Check troub-mptom.

i NG 1 ReDlace the ECM.

I

Probable cause

0 Engine coolant temperature sensor failed 0 Open or shorted engine coolant temperature sensor circuit, or loose connector 0 Engine control module failed

OK

between the 'F- Repair

I :” ’!

Code No. PO1 20 Throttle Position Circuit Malfunction

~ Background 0 The throttle position sensor outputs a voltage which is proportional to the throttle valve opening angle 0 The enginecontrol modulechecks whetherthevoltageoutput by the throttleposition sensor is within a specified range In addition, it checks that the voltage output does not become too large while the engine is idling Check Area 0 At least 2 seconds have passed after the engine was started Judgment Criteria 0 With the close throttle position switch set to ON, the sensor output voltage has continued to be 2V or higher for 2 sec, or 0 Sensor output voltage has continued to be 0 2V or lower for 2 sec Check Area 0 At least 2 seconds have passed after the engine was started 0 Engine speed is 3000 r/min or less 0 Volume efficiency IS 30% or less Judgment Criteria 0 Sensor output voltage has continued to be 4 6V or higher for 2 sec Check Area 0 At least 2 seconds have passed after the engine was started 0 Engine speed is 2000 r/min or more 0 Volume efficiency is 60 % or more.

Judgment Criteria 0 Sensor output voltage is 0 8 V or less for 2 seconds

system OK: With the throttle valve at the idle - I Check the closed throttle position I switch system (Refer to P.13B-110, INSPECTION , PROCEDURE 30 ) 1 i

NG SCAN TOOL Data list

126 Closed throttle position switch

1 position ON

I ?zn: trF;hrottle valve slightly ~ r , OK

Check the throttle- N G Replace I (Refer to P13B-1:AK 1 *- E ; k the following connector: --“;--C Repair _ _ ~ ~ ~ Measure at the throttle position sensor connector A-52.

0 Disconnect the connector, and measure at the harness side.

Voltage between 1 and ground (Ignition switch. ON) OK: 4.8-5 2 V 0 Continuity between 4 and ground OK: Continuity

E F k trouble =torn

joheclc the harness w i r e - b e W x p - Repair , ECM and the throttle position sensor

~~ ~ OK

~~ ‘ OK 1 F e t k E C M . 7

connector

1 Check the throttle position sensor

1

SPECTION PROCEDURE 48) 1

1 output circuit (Refer to P.138-123, IN-

Probable cause

~ ~ ~ _ _ _ _ _ _ _ _

- ~ 0 Throttle position sensor failed or misadjusted 0 Open or shorted throttle position sensor circuit, or loose connector 0 Closed throttle position switch malfunction 0 Closed throttle position switch signal wire shorted

Engine control module failed

I

i 3 ~ - 3

' Code No. PO125 Excessive Time to Enter Closed Loop I Probable cause Fuel Control

Background 0 The MFI system reduces exhaust emissions by means of closed-loop fuel control.

0 The engine control module checks the time taken until closed-loop fuel control commences Check Area 0 At least 2 seconds have passed after the engine started 0 Engine coolant temperature is higher than 80°C (176OF) 0 Engine speed is at between about 1800 and 3500 r/min.

0 Volumetric efficiency is 16% - 62%.

0 Engine operating within the air-fuel ratio feedback zone 0 Monitoring time. 30 sec Judgment Criteria 0 Multiport fuel injection system doesn't enter the closed loop control within about 30 sec 0 Monitored only once per trip

NG I t h e heated oxygen sensor (front). (Refer to P13B-150.) I

- + Replace

r c h i i o w i n g connectors:

F't Repair

,OK

1 A-67, A-83, B-37

,OK

, NG ' Check the harness wire between the ECM and the heated oxygen ~ = Repair sensor (front) connector.

, NG + -* Replace +OK

1 Check the Injector. (Refer to P13B-152)

~~~

- ' OK 7 NG

rcXcthefoliowing connectors:

I

- C Repair

~ Check the harness wire between the-

- Repair

A-70, A-71, A-72, A-73 A .

,OK NG :

*)

1 tor.

I

1 OK

~ Check the fuel pressure. (Refer to P.13B-144.) I

Check intake system vacuum leak.

0 Check for exhaust leaks (oxygen sensor installation section, ' cracks in exhaust manifold, cracks in front pipe, etc.) 0 Check for clogging of the fuel filter and fuel line.

Checkthe fuel pump (insufficient

1 OK 7

~ Replace the ECM.

i---

-

_ _

0 Heated oxygen sensor failed 0 Injector failed 0 Fuel pressure regulator failed 0 Fuel pump failed 0 Fuel filter is clogged 0 Intake system vacuum leak 0 Exhaust leak 0 Engine control module failed.

2 . J f

Code No. PO130 Oxygen Sensor Circuit Malfunction (Sensor 1)

Background

When the heated oxygen sensor begins to deteriorate, the oxygen sensor signal response becomes poor.

The engine control module forcibly varies the air/fuel mixture to make it leaner and richer and checks the response speed of the heated oxygen sensor In addition, the engine control module also checks for an open circuit in the heated oxygen sensor output line Check Area

Coolant temperature sensor normal Heated oxygen sensor signal voltage has continued to be 0 2V or lower for 3 min or more after the starting sequence was completed Engine coolant temperature is higher than 80°C (176°F) Engine speed is higher than 1200 r/min Volumetric efficiency is not lower than 25% Monitoring time 7 sec Judgment Criteria

Input voltage supplied to the engine control module interface circuit is not lower than 4 5V when 5V is applied to the heated oxygen sensor output line via a resistor 0 Monitored only once per trip Check Area

Engine coolant temperature is not lower than 50°C (122°F) Engine speed is between 1600 and 3000 r/min <M/T> or 1400 and 3000 r/min <AD> Volumetric efficiency is 22 - 60% <M/T> or 25 - 60% <A/T>

Intake air temperature is -10°C (14°F) or more Atmospheric pressure is 76 kPa (11 psi) or more 0 Under the closed loop air-fuel control Vehicle speed is 30 km/h (18 7 mph) or higher Throttle valve opening angle (TPS output voltage) fluctuates within 0 11 7V every 250 milliseconds Monitoring Time 5 - 20 sec Judgment Criteria 0 When the air-fuel ratio IS forcibly changed (lean to rich and rich to lean), the heated oxygen sensor signal doesn’t provide response within 1 2 sec.

or

The heated oxygen sensor sends “lean” and “rich” signals alternately nine times or less for ten seconds Monitored only three times per trip

NOTE. If the sensor switch time is longer than the Judgment Criteria due to the MUT-I1 OBD-I1 test Mode - H02S Test Results, it is assumed that the heated oxygen sensor has deteriorated If it is short, it is assumed that the harness wire is broken or has a short circuit If the heated oxygen sensor signal voltage has not changed even once (leanlrich) after the DTC was erased, the sensor switch time will display as 0 seconds

~

- Repair A-67, A-83, B-37 L---_ , ~~~~~ ~- , NG

NG ~- OK Check the heated oxygen sensor W-rCheck the following connectors:

(front). (Refer to P 138-150.)

Replace zheck

-~ trouble symptom.

1

’ NG 1

ECM and the heated oxygen sensor r h e c k t h e r n e s s wire betw

/(front) connector.

I OK

1 Replace the oxygen sensor (front).

I

- 7- i

Ehecktrouble symptom.

j

1

~ Replace the ECM. -7

Probable cause

Heated oxygen sensor deteriorated Open circuit in heated oxygen sensor output line Engine control module failed

hG

' Code No. PO135 Oxygen Sensor Heater Circuit Malfunction (Sensor 1)

Background 0 The engine control module checks whether the heater current is within a specified range when the heater is energized.

Check Area 0 Engine coolant temperature is 20°C (68°F) or higher 0 The heated oxygen sensor heater is on 0 Battery voltage is between 11 and 16V Judgment Criteria 0 Heater current of the front heated oxygen sensor heater (Sensor 1) has continued to be 0 2A or lower or 3 5A or higher for 6 sec.

0 Monitored only once per trip

Check the heated oxygen sensor

- Replace (front). (Refer to P 13B-150) -"G

-~

NG

---I Check the harness wire between the

Measure at the heated oxygen sensor (front) connectors A-67, A-83 0 Disconnect the connector, and measure at the harness side 0 Voltage between 1 and ground (Ignition switch ON) O K Battery positive voltage

1 heated oxygen sensor (front) and the

1 MFI relay connector. Repair, if neces-

1 sary.

I

~~~~~

1 OK I NG WCM connectZZi?

1 measure at the harness side ' 0 Voltage between 60 and ground (Ignition switch ON)

0 Disconnect the connector, and A-67, A-83

1 OK: Battery positive voltage ,

1 NG I-- I Check the harness wire between the] ECM and the heated oxygen sensor (front) connector Repair, if necessary

bNG- Repair 1

--__._________ Check the following connector:

B-38

OK

1 Check trouble symptom.

tNG

- replace the^^.

Probable cause

0 Open or shorted oxygen sensor heater circuit 0 Open circuit in oxygen sensor heater 0 Engine control module failed

w-

Code No. PO136 Oxygen Sensor Circuit Malfunction (Sensor 2)

Background 0 The engine controls module checks for an open circuit in the heated oxygen sensor output line Check Area 0 Coolant temperature sensor. normal 0 Heated oxygen sensor signal voltage has continued to be 0 1V or lower for 3 min or more after the starting sequence was completed.

0 Engine coolant temperature is not lower than 80°C (176°F) 0 Engine speed is higher than 1200 r/min 0 Volumetric efficiency is not lower than 25% 0 Monitoring time 7 sec Judgment Criteria 0 Input voltage supplied to the engine control module interface circuit is not lower than 4 5V when 5V is applied to the heated oxygen sensor output line via a resistor 0 Monitored only once per trip Check Area 0 Heated oxygen sensor (rear) signal voltage remains 0 1V or less for at least 3 minutes after the engine is started 0 Engine coolant temperature is about 80°C (176°F) or higher 0 Engine speed is about 1,200 rpm or higher 0 Volumetric efficiency is 25% or higher 0 Output frequency of the volume air flow sensor is 113 Hz or higher 0 At least 20 seconds have passed since fuel supply shut-off control was released 0 Output voltage of the oxygen sensor (front) is 0 5V or higher 0 Monitoring time 10 seconds.

Judgement Criteria 0 Making the air-fuel ratio 15% richer doesn't result in raising the heated oxygen sensor output voltage beyond 0 1V 0 Monitored only once per trip Check Area 0 Engine coolant temperature is about 80°C (176°F) or higher 0 Barometric pressure is 76 kPa (11 psi) or higher 0 The heated oxygen sensor (front) is operating 0 The engine runs for at least 10 seconds when air-fuel ratio is rich 0 The heated oxygen sensor (rear) outputvoltage is 0 4V or more before fuel shut-off commences 0 While fuel is being shut off Judgement Criteria 0 At least 1 second has passed before heated oxygen sensor (rear) output voltage falls to 0 15 - 0 40V or 0 At least 3 seconds have passed before the heated oxygen sensor (rear) output voltage falls to 0 15V or less

1 A-67, A-83, 8-37

I (Refer to P.138-150.)

I NG ' OK 1 1

-

~ Check trouble symptom.

I 2 - ___ _ _ - ___ NG

- - Replace NG

I Check the harness wire between the I -- Repair

- ECM and the heated oxygen sensor 1

(rear) connector.

Lp- ' OK

r k i x y g e n sensor ~ I

_ _ ~

w Check trouble symptom.

I

Probable cause

Heated oxygen sensor failed Open circuit in heated oxygen sensor output line Engine control module failed

i

-

~~~~ ~

- ~ ~

-~ ~ ~~~~ Background

The engine control module checks whether the heater current is within a specified range when the heater is energized.

Check Area

Engine coolant temperature is 20°C (68°F) or higher.

The heated oxygen sensor heater is on.

Battery voltage is between 11 and 16V Judgment Criteria

Heater current of the front heated oxygen sensor heater (Sensor 2) has continued to be 0 2 A or lower or 3 5 A or higher for 6 sec

Monitored only once per trip.

NG - Replace

Check the heatedoxygen sensor (rear).

(Refer to P13B-150) - L ~-

-~

NG 4' Check the harness wire between the

s t the heated oxygen sensor

1 heated oxygen sensor (rear) and the , MFI relay connector. Repair, if neces- sary.

I

I (rear) connectors A-83, 8-45

Disconnect the connector, and measure at the harness side.

<Federal> 0 Voltage between 3 and ground (Ignition switch: ON) OK: Battery positive voltage <California>

Voltage between 1 and ground (Ignition switch ON) OK: Battery positive voltage

T K ~~~

-

Check the following connectors 7 lNG-m Repair NG

~ A-83, B-45 ,

Measure at the ECM connector 8-38 1 Disconnect the connector, and measure at the harness side.

~~~

-

OK

1 0 Voltage between 54 and ground (Ignition switch: ON) , OK: Battery positive voltage

1 =trouble symptom.

~ _ _

' NG

Check the harness wire between the ECM and the heated oxygen sensor 1 Repair, if necessaryd

~~ t rCheck the f o l l o w i n ~ l ~

- Repair

1 8-38

pheck trouble symptom.

1

1 I NG-

[Repiace the ECM.

~ Probable cause

0 Open or shorted oxygen sensor heater circuit

Open circuit in oxygen sensor heater Engine control module failed

-

Code No. PO170 Fuel Trim Malfunction

Background 0 If a malfunction occurs in the fuel system, the fuel trim value becomes too large or too small.

0 The engine control module checks whether the fuel trim value is within a specified range Check Area 0 Under the closed loop air-fuel ratio control Engine coolant temperature is -10°C (14°F) or higher 0 Intake air temperature -10°C (14OF) or more 0 Atmospheric pressure is 76 kPa (11 psi) or more.

0 Output frequency of the volume air flow sensor is 113 Hz or higher Judgment Criteria 0 Long-range fuel correction has continued to be t i 2 5% or higher or -12 5% or lower for 10 sec.

0 Short-range fuel correction has continued to be +7 4% or higher -7 4% or lower for 10 sec.

NG I-* ?heck the intake air temperature circuit malfunction (Refer to SCAN TOOL Data list 13 Intake air temperature sensor (Refer to P13B-125) 1 1 P 138-28, INSPECTION PROCEDUREFOR- TROUBLE CODE P0110)

-----

-~

1 OK

1 NG c

~ NG i

I F T O O L Data list c 125 Barometric pressure sensor (Refer to P13B-125)

NG I OK 1

1 Check the injector (Refer to P.13B-152.) ** Replace

~~~~ 7 0 K 1 NG Check the following connecto-

- Repair A-70, A-71, A-72, A-73, B-40

I

1 OK 1- ~ NG

~ tor.

* Repair I

I Check the harness wire between the ECM and the injector c o m e 4

i Check the fuel pressure (Refer to P.13B-144.) I

NG More OK

IthangrodCheck if air was drawn I--

1 81 Long-term fuel compensation (Refer to P.138-125.)

Is fuel trim more or less than zero?

No

- -~ 0 Check for fuel leaks from injector.

Check for entry of

1 Less tthan zero SCAN TOOL Data= 12 Volume air flow sensor (Refer to P.13B-125.) 0 Does the tester indi- cate more than the standard value?

cyes Replace the volume air flow sensor.

~ foreign matter (water, kerosene, etc.) into

I the fuel.

1 OK 1

1 Replace the ECM

Probable cause ~ I

Volume air flow sensor failed Injector failed Incorrect fuel pressure Air drawn in from gaps in gasket seals, etc.

Heated oxygen sensor failed Engine coolant temperature sensor failed Intake air temperature sensor failed Barometric pressure sensor failed Exhaust leak Use of incorrect fuel Engine control module failed

0 0 0 0 0 0 0 0 0 0 0

Check the engine coolanfie- to P 13B-29, INSPECTION PROCEDURE FOR DIAGNOSTIC TROUBLE CODE PO115)

-~

TROUBLE CODE P0105) I P.138-27, INSPECTION PROCEDURE FOR DIAGNOSTIC

Check the barometric pressure circuit malfunction (Refer to

- Repair

into the intake system.

i ~~- 1 OK

1 Nn SCAN TOOL Data list 12 Volume air flow sensor (Refer to P.13B-125.) 0 Does the tester indi- cate less than the standard value?

1 Yes

0 Check for clogging of the injector 0 Check for clogging of the fuel filter and fuel line 0 Check the fuel pump (insufficient discharge rate) 0 Check for exhaust leaks (oxygen sensor installation section, cracks in exhaust manifold, cracks in front pipe, etc ) 0 Check for entry of foreign matter (water, kerosene, etc) into the fuel

~

- -2

Replace the volume air flow sensor

~ ~ ___- I Code No. P0201, P0202, P0203rP0204 Injector Circuit Malfunction (Cylinder-I , Cylinder-2, Cylinder-3, Cylin- der-4)

Background

A surge voltage is generated when the injectors are driven and the current flowing to the injector coil is shut off.

The engine control module checks this surge voltage Check Area 0 Engine speed is between 50 and 1000 r/min.

0 Throttle position sensor output voltage is lower than 1 16V Judgment Criteria 0 Inlector coil surge voltage (more than system voltage +2V) has not been detected for 2 sec

- NG Replace

~ E E c k L h e injector (Refer to P 138-1 52.)

]OK

- 1 NG Measure at the injector connectors A-70 A-71 A-72 A-73 0 Disconnect the connector, and measire at ;he harness side Voltage between 1 and ground (Ignition switch. ON) 1 OK: Battery positive voltage

-2 ~ _ _ ~ _ _ _ _ _ _

1 OK

Check the injector control circuit I (Refer to P.136-124, INSPECTION PROCEDURE49) L-- ~ _ _ _ _ _ _ _ _ _ _ _ ~ ~

Probable cause

0 Injector failed

Open or shorted injector circuit, or loose connector 0 Engine control module failed

connectors:

LA-70, A-71, A-72, A-73 1

-~ _ _ _ ~ _ _ _ _ _ I p h e c k trouble symptom ~ - - 1NG

~

- 1 1 tor. Repair, if necessary

Check harness wire between the MFI relay and the injectorconnec-

;'

Check Area 0 5 sec or more have passed after the engine was started 0 Low cornpression pressure 0 Engine coolant temperature sensor failed

SCAN TOOL Data list 22 Crankshaft position sensor (Refer to P.13B-125.) 0 Crankshaft position sensor wave form check 0 Engine speed stable OK: Constant pulse range _ _ ~

- Repair connectors:

I A-82. B-37

-~

Repair tOK Check the harness wire between the ECM and the Crankshaft Position Sen- I yconnector.

' OK 7

~ i ' Check if the Crankshaft I Position Sensor and

s'

I Check the following connectors:

1

- Replace

1 Position Sensor I

- 7 NG , Check the injector (Refer to P.13B-152.)

NG - Repair

-J I A-70, A-71, A-72, A-73, B-40 Lppp I OK .-

~

- _ _ ~ ~

I Check the harnesswire betweenthe ECM andthe injectorconnector - Repair ~ _ _ _ _ _ _ . _ ~ ~ _ _ _ _ _

tOK ~ ~ D a ~ s t 81 Long-term fuel compensation (Refer to P.13B-125) IF 1 I ,OK 7

NG Check the fuel trim malfunction (Refer to P 13B-36, INSPECTION r EROCEDURE ~ _ _ ~ _ _ _ _ - FOR DIAGNOSTIC TROUBLE CODE P0170)

I SCAN TOOL Data list

~ 82 Short-term fuel compensation (Refer to P136-125.)

,OK NG ~ ~-

-~ SCAN TOOL Data list 21 Engine coolant temperature sensor (Refer to P 136-125)

-- ~~ ~~

-~ -~ ____-I

I OK 7 Check the following items 0 Check the ignition coil, spark plugs, spark plug cables.

~ _ _ _ ~

- ~

0 Check the compression pressure 0 Check the timing belt for jumping teeth 0 Check the EGR system and EGR valve.

L--.

~~

- ~~~~

sensing plate are installed properly

OK c

- ~

1 I Replace the- Crankshaft j

~

Check the engine coolant temperature circuit malfunction (Refer I to P.138-29, INSPECTION PROCEDURE FOR DIAGNOSTIC , TROUBLE CODE P0115) I

Lyr

I Code No. P0301, P0302, P0303, P0304, Misfire Detected (Cylinder-1 , Cylinder-2, Cylinder-3, Cylinder-4) ~ ~ ~ ~

- ~ ~ ~ _ _ _ Background 0 If amisfinngoccurswhiletheengineis running,theenginespeedsuddenlychanges.

0 The engine control module checks for changes in the engine speed Check Area 0 5 sec or more have passed after the engine was started 0 Engine speed is between 500 and 6500 r/min 0 Engine coolant temperature is -lO°C (14°F) or more 0 Intake air temperature -10°C (14°F) or more 0 Atmospheric pressure is 76 kPa (11 psi) or more 0 Adaptive learning is complete for the vane which generates a crankshaft position signal 0 While the engine is running, excluding gear shifting, deceleration, sudden acceleration/deceleration and A/C compressor switching Judgment Criteria (change in the augular acceleration of the crankshaft is used for misfire detection ) 0 Misfire has occurred in the engine more than allowed (2 0%) per 200 revolutions [when the catalyst temperature is higher than 950°C (1 742"F)I or 0 Misfire has occurred more frequently that the allowed number of times (2%) during 1000 motor revolutions (Misfire exceeding 1 5 times the limit of emission standard )

v NG 1 Check the injector (Refer to P.138-152.) + Replace OK 1 ~ _ _ ~ ~

- Check the following connectors:

[NG- Repair I A-70. A-71. A-72, A-73, 8-40 L

-d OK

-- NG 1 Check the harness wire betweentheECMandthein]ectokonnector - Repair

- ~~ OK 1 Check the following items.

0 Check the spark plugs, spark plug cables.

l o Check the compression pressure.

~

Probable cause

Ignition system related part(s) failed

0 0 Low compression pressure 0 Injector failed 0 Engine control module failed

t-"

Code No. PO335 Crankshaft Position Sensor Circuit Malfunction

Background 0 When the engine is running, the crankshaft position sensor outputs a pulse signal 0 The engine control module checks whether the pulse signal is input while the engine is cranking Check Area 0 Engine is being cranked Judgment Criteria 0 Sensor output voltage has not changed (no pulse signal is input) for 2 sec.

Check Area Judgment Criteria 0 Normal signal pattern has not beeninputforcylinderidentificationfrom thecrankshaft position sensor siqnal and camshaft position sensor signal for 2 sec

harness MD998478 ) 0 Voltage between 2 (black clip) and ground (Engine.

' cranking)

-~ I.Measureatthecranl*shatts~tionsensorconnectorA-82. 'K-pplace 7

-~ the ECM.

Measure with the connector connected (Use the test ~ I

~ 0 ~ !

~ a ~ ~ ~ ~ n 2 (black clip) and ground (Engine

1 :Fg'1525V

I NG 1 at the crankshaft position sensor connector A-82 1.'- the connector, and measure at the harness

' 2 NG-

1. Voltage between 3 and ground (Ignition switch ON) 1 OK: Battery positive voltage I 2 Voltage between 2 and ground (Ignition switch ON) OK: 48-52 V

I OK: Continuity

3. Continuity between 1 and ground

- OK v ' Check the following 'F- Repair

j 1 Check troubli symptom.

1

I i NG 1 NG

, A

conector:

-____

~ A-82

' OK 1 ___p_

1 Check trouble symptom.

I

- ~ _ - _ _ p

' NG 1 pp.__._ ~~ L

I Replace the crankshaft position sensor.

L-

-~

- ~ p

- _ 1

Probable cause

0 Crankshaft position sensor failed 0 Open or shorted crankshaft position Sensor circuit, or loose connector 0 Engine control module failed

the MFI relay connector Repair, if necessary.

_~

I Check the harness wire - Repair between the ECM and the

~ crankshaft position sen- , sor connector ] OK

1-

-

i Replace the ECM.

' Check the harness wire between the crankshaft position

, sensor and the ground Repair, if necessary

- A

' Code No. PO340 Camshaft Position Sensor Circuit I Probable cause Malfunction

Background 0 When the engine is running, the camshaft position sensor outputs a pulse signal 0 The engine control module checks whether the pulse signal is input Check Area 0 Engine speed is about 50rimin or higher Judgment Criteria 0 Sensor output voltage has not changed (no pulse signal is input) for 2 sec Check Area 0 Engine speed is about 50rimin or higher Judgment Criteria 0 Normal signal pattern has not been inputfor cylinder identificationfrom thecrankshaft position sensor and camshaft position sensor signal for 2 sec

-_____ Measure at the camshaft position sensor connector A-65.

0 Measure with the connector connected.

0 Voltage between 2 and ground (Engine cranking) OK: 04-30 V 0 Voltage between 2 and ground (Engine idling) OK: 05-20 V _ _ _ _ ~ ~

~ _ _ _ _ ~

- ~~ OK

-+ Replace the ECM.

1

~ Check the harness wire between the camshaft position sensor and Measure at the camshaft poiition sensor connector A-65. LNG - 0 Disconnect the connector, and measure at the harness side relay connector. Repair, if necessary.

~ ~ 1

~

-- NG

-_-

2. NG

Check t h e following k- Repair +I conector:

I

1. Voltage between 3 and ground (Ignition switch: ON) OK: Battery positive voltage

2. Voltage between 2 and ground (Ignition switch. ON)

~ 1

- 1 3 NG B-37 OK 7 Check trouble symptfl:]

3. Continuity between 1 and ground OK: 4 8-5 2 V

- _ _ OK: Continuity

-~ ~ ' OK

~~ 1 NG Check the following I c Repair conector: 4 ' W

L Check trouble symptom 1 NG

1 Replace the camshaft position sensor.

I

*[Check the harness wire between the camshaft position sensor and 1 the ground Repair, if necessary.

0 Camshaft position sensor malfunction 0 Open or shorted camshaft position sensor circuit or loose connector 0 Engine control module failed

I

I NG

1 connector 4 OK

Replace the ECM ____.

~

- _ _ _ _ - ~ ~ _ _ _ _ ~

-

-

!"- '

Code No. PO400 Exhaust Gas Recirculation Flow Malfunction

Background

When the EGR solenoid switches from OFF to ON while the engine is running, EGR gas flows The engine control module checks how the EGR gas flow signal changes Check Area

At least 20 seconds have passed after the last monitor finished.

Engine coolant temperature is higher than 80°C (176°F) Engine speed is between 1000 and 2000 r/min <M/T> or 1000 and 1700 r/min <An> Intake air temperature is 5°C (41°F) or more Atmospheric pressure is 76 kPa (11 psi) or more Vehicle speed is 30 kmih (18 7 rnph) or higher At least ninety seconds have passed stnce manifold differential pressure sensor output voltage fluctuated 1 5V or more Closed throttle position switch ON Volumetric efficiency 15% <M/T> or 25% <W> or less Fuel is being shut off <M/T> 0 Monitoring Time 2 sec Judgment Criteria

The fluctuation in the intake system is low when the EGR solenoid is turned ON.

0 Monitored only three times per trip

I Check the EGR system (Refer to GROUP 17 - Emission Control i - - d Check the EGR solenoid (Refer to GROUP 17 - Emission Control L System ) ~ System) I

~-

-_ ~ NG

- _ _ _ _ ~ _ _ _ _ _

OK

I

I 1 r z z NG Check the manifold differential pressure sensor circuit malfunction 1

1 95 Manifold differential pressure sensor (Refer to P.138-125.) TI (Referto P.13B-86, lNSPECTlON PROCEDURE FOR DMGNOS- , TIC TROUBLE CODE P1400) I OK ~ . _ _ _ _ - _

Check the EGR valve and EGR route for clogging, and clean.

i

-_ ~~~ _ _ ~ _ _ _ ---A

Probable cause

- -

- --

- EGR valve does not open EGR control vacuum IS too low EGR solenoid failed 0 Open or shorted EGR solenoid circuit, or loose connector Manifold differential pressure sensor failed Engine control module failed

1 NG 7 i°K Replace

7

Check the following items.

I

Vacuum hoses

I EGR port vacuum

EGR valve (Refer to GROUP 17 - Emission Control System )

~ . _ _ _ _ _ _ _ ~ ~ ~

i

' Code No. PO403 Exhaust Gas Recirculation Solenoid

~

- p

- Malfunction

Background

The engine control module checks current flows in the EGR solenoid drive circuit when the solenoid is ON and OFF Check Area

Battery voltage is not lower than 1OV.

Judgment Criteria

Solenoid coil surge voltage (more than system voltage +2V) is not detected when the EGR solenoid is turned on/off

Monitored only once per trip

1 Check the EGR solenoid. (Refer to GROUP 17 - Em==

- Control System.) L I OK 1

-Measure at the EG%- solenoid connector A-48.

~ z' Battery positive voltage 1 OK NG 1

Disconnect the connector and measure at the harness

Voltage between 1 and ground (Ignition swrtch. ON)

~ ~~ _____- _____ Measure at the ECM connector B-40.

I Disconnect the connector and measure at the harness 1

Voltage between 6 and ground (Ignition switch: ON)

OK

Repair 1

-~ I OK 1 /

1 Check trouble svmptom.

1 ReDlace the ECM.

i

Probable cause

EGR solenoid failed.

Open or shorted evaporative EGR solenoid circuit, or loose connector.

Engine control module failed.

Replace

Check the harness wire between MFI relay and solenoid valve connector, and repair if necessary.

~~p

NG

I 1 -

- -- , Check trouble symptom.

N G v

~ Check the harness wire between ECM and solenoid valve connector, 1

1 and repair if necessary.

I

Code No. PO420 Catalyst System Efficiency Below Th res ho I d

Background 0 The signal from the heated oxygen sensor which follows the catalytic converter differs from that which precedes the catalytic converter That is because the catalytic converter purifies exhaust gas When the catalytic converter has deteriorated, the signal from the heated oxygen sensor which follows the catalytic converter becomes similar to that which precedes the catalytic converter 0 The enginecontrol module checks the outputs of the heated oxygen sensor signals Check Area 0 Engine speed is not higher than 3000 r/min 0 Volume air flow sensor output frequency is between 69 and 144 Hz 0 Intake air temperature is -10°C (14°F) or more 0 Atmospheric pressure is 76 kPa (11 psi) or more.

0 Closed throttle position switch OFF 0 Under the closed loop air-fuel ratio control 0 Vehicle speed is 1.5 km/h (0.93 mph) or higher 0 Monitoring time 140 sec Judgment Criteria 0 Fault in the oxygen sensor (rear) signal and oxygen sensor (front) signal

NG Check the exhaust manifold (For cracks and leaks.) Replace OK-- 1 SCAN TOOL Data list 59 Heated oxygen sensor (rear) 0 Transaxle: 2nd gear <MTT>, L range <A/T> 0 Drive with wide open throttle O K 600 - 1000 mV

~ ~ ~ _ _ _ _ _

i 4 OK

1 SCAN TOOL Data list ~

~ Check the oxygen sensor circuit maGnction (sensor 1) (Refer ~

- ~

- r t o 3 2 , INSPECTION PROCEDURE FOR DIAGNOSTIC

11 Heated oxygen sensor (front) 0 Sudden racing F O U B L E CODE P0130) - LR:place the heated oxygen sensor (front)

1 OK: 600 - 1000 mV

OK: The switch between 0 - 400 - 600 - 1000 mV is 15 7 Data list

I 11 Heated oxygen sensor (front) Engine 2000 r/min

or more times in 10 sec.

1 OK 1

I

-~ ~ Replace the heated oxygen sensor (rear)

I t

i Check the trouble symptom 7 I

-- _.

- NG T I Replace the catalytic converter

I

- J 1 Check trouble symptom L---- Y G

P e T j e E C M . - ~ 1

Probable cause

0 Catalytic converter deteriorated 0 Heated oxygen sensor failed 0 Engine control module failed

-

MFI <I

' Code No. PO421 Warm Up Catalyst Efficiency Below Threshold

-____ Background 0 The signal from the heated oxygen sensor which follows the catalytic converter differs from that which precedes the catalytic converter That is because the catalytic converter purifies exhaust gas When the catalytic converter has deteriorated, the signal from the heated oxygen sensor which follows the catalytic converter becomes similar to that which precedes the catalytic converter 0 The enginecontrol module checks the outputs of the heated oxygen sensor signals.

Check Area 0 Engine speed is not higher than 3000 r/min 0 Volume air flow sensor output frequency is between 69 and 144 Hz 0 Intake air temperature is -10°C (14°F) or more.

0 Atmospheric pressure is 76 kPa (11 psi) or more.

0 Closed throttle position switch OFF 0 Under the closed loop air-fuel ratio control 0 Vehicle speed is 1 5 km/h (0 93 mph) or higher 0 Monitoring time 140 sec Judgment Criteria 0 Fault in the heated oxygen sensor (rear) signal and heated oxygen sensor (front) signal

NG p h e c k the exhaust manlroldcForcracksandleaks.,---1E -- Replace OK

Redace the catalvtic converter.

I

1

/symptom.

I I

1 NG

1 Replace the ECM.

- ~~~

Probable cause

0 Catalytic converter deteriorated 0 Heated oxygen sensor failed 0 Engine control module failed

“‘>c

Code No.

1 Evaporative Emission Control System Leak Detected I PO442

System Diagram

INTAKE MANIFOLD rn

VENTILATION SOLENOID

I EVAPORATIVE EM I351 ON CAiL I STE R

A0310115 FUEL TANK

I EVAPORATIVE EMISSION CANISTER

1 PURGE SOLENOID

FUEL VENT VALVE

i3B-47 _ _ _ _ _ ~ ~

TECHNICAL DESCRIPT!BN

B The ECM turns on the evaporative emission ventilation solenoid which shuts off the evaporative emission canister outlet port. Then the evaporative emission purge solenoid is driven. As a result, the fuel system will be set into a negative pressure.

When the fuel system reaches negative pressure, the evaporative emission purge solenoid is turned “off,” and the fuel system are sealed. As the fuel pressure inside the fuel tank changes, the ECM judges if there is a leak in the fuel system.

DTC SET CONDITIONS Check Area At least sixteen minutes have passed since the starting sequence was completed.

Engine coolant temperature higher than 60°C (1 40 ” F) .

Engine speed is 1,600 rlmin or more.

Power steering pressure switch: “OFF.” Barometric pressure is higher than 76 kPa (11 psi).

Volumetric efficiency is at between 20 and 80 percent.

The engine coolant temperature is 30°C (86°F) or less when the engine is started.

Intake air temperature is higher than 5°C (41 OF).

The pressure rise when the evaporative emission purge solenoid and evaporative emission ventilation solenoid are closed is less than 451 Pa (0.065 psi).

OVERVIEW OF TROUBLESHOOTING

0 To determine the cause of DTC P0442, a performance test is needed. The performance test uses a mechanical vacuum gauge and scan tool MB991502 set on the fuel tank differential pressure sensor (TANK PRS SNSR 73). The mechanical gauge reading is used to verify scan tool MB991502 reading. A comparison of the mechanical gauge to scan tool MB991502 determines the problem in the system.

Prior to doing the performance test, several simple inspections are needed to exclude some possibilities of the symptom.

0

0 The pressure fluctuation width is less than 647 Pa (0.094 psi).

At least twenty seconds have passed since pressure fluctuation detection commenced.

0 Fuel tank differential pressure sensor output voltage is 1 - 4 volts.

0 Intake air temperature is 30°C (86°F) or less when the engine started.

0 Vehicle speed is 30 km/h (18.7 mph) or more.

Monitoring time: 75 - 125 seconds

Judgment Criteria

0 Internal pressure of the fuel tank has changed more than 843 Pa (0.122 psi) in 20 seconds after the tank and vapor line were closed.

TROUBLESHOOTING HINTS The most likely causes for this code to be set are:

0 Loose fuel cap.

0 Fuel cap relief pressure is incorrect.

0 Evaporative emission canister seal is faulty.

Evaporative emission canister is clogged.

0 Fuel vent valve failed.

0 Purge line or vapor line is clogged.

0 Fuel tank, purge line or vapor line seal failed.

0 Evaporative emission purge solenoid failed.

0 Evaporative emission ventilation solenoid failed.

Fuel tank differential pressure sensor failed.

e Engine coolant temperature sensor failed.

0 Intake air temperature sensor failed.

0 Power steering pressure switch failed.

0 Use of incorrect fuel.

DIAGNOSIS Required Special Tool:

MB991502: Scan Tool (MUT-11)

Caution To prevent damage to scan tool MB991502, turn the ignition switch off before connecting or disconnecting scan tool MB991502.

In this procedure, scan tool MB991502 should be used in the metric mode (showing the value in kPa). If not, set scan tool MB991502 by selecting the “System Setup” at the main menu.

J

STEP 1. Check for other DTCs.

If any other DTCs are set, please check those DTCs first then follow the steps below.

STEP 2. Evaporative Emission System Leak Monitor Test using scan tool MB991502.

NOTE: This monitor is carried out at an engine speed of 1,600 r/min or more, transmission is in “N” or “R” position.

The engine speed has to be automatically adjusted.

(1) Erase the DTCs using scan tool MB991502. Ensure that the fuel cap is securely tightened.

(2) Select “System Test” and press “YES” key.

(3) Select “Evap Leak Mon” and press “YES” key.

(4) If “Evap Leak Mon” is selected before starting the engine, “Engine must be running.” is displayed. In this case, start the engine and then select “Evap Leak Mon” again.

(5) if “Keep the TPS in idle position. during the test.” is displayed, the ECM adjusts engine speed automatically.

A manual adjustment for engine speed is not needed.

(6) Keep the idling position during the monitor.

NOTE: If the engine speed does not reach 2,000 r/min during the monitor test, adjustment of the Speed Adjusting Screw may be needed. Refer to /?138-143 for the adjistment procedure.

(7) Item ‘‘In Progress” is displayed during the monitor. Keep the engine speed and load within the defined range. Scan tool ME3991502 shows these items on the screen.

Item “In Progress” will be change from “NO” to “YES” by keeping engine conditions.

(8) Message “Evap Leak Mon. Completed. Test Passed.” is displayed when the test has been completed without malfunction. Evaporative emission system is working property at this time. Please explain to customer that improperly tightened fuel cap can cause to MIL turn on.

No further steps are needed.

(9) Message “Evap Leak Mon. Completed. Test Failed & DTCs Set.” is displayed when a malfunction has been detected during the test. Go to Step 3.

(10) Message “Evap Leak Mon. discontinued. Retest again from the first” is displayed when the monitor was discontinued by a certain reason (input vehicle speed, engine speed and engine load was put of the specified range). Turn the ignition switch off once and start monitoring from the beginning.

NOTE: Monitoring will not start unless turning off the ignition switch is turned off once and the engine restarted.

STEP 3. Using scan tool MB991502, check “Fuel tank differential pressure sensor (date list 73)” output.

In this step, the fuel tank differential pressure sensor reading is checked to determine if the fuel tank differential pressure sensor output is within the normal range.

Check’the MFI data list item: TANK PRS SNSR 73 Watch the sensor reading. This value varies depending on pressure inside the fuel tank.

Remove the fuel cap.

NOTE: If the fuel cap is not securely tightened, it might have the cause of a leak in the EVAP system and set the DTC P0442.

After the fuel cap has been removed, the pressure sensor reading should be between -0.5 kPa (-0.07 psi) and 0.5 kPa (0.07 psi).

0 If the reading is between -0.5 kPa (-0.07 psi) and 0.5 kPa (0.07 psi), the fuel tank differential pressure sensor circuit is OK. Therefore, go to Step 4.

If the reading is not between -0.5 kPa (-0.07 psi) and 0.5 kPa (0.07 psi), the fuel tank differential pressure sensor is not working properly. Replace the fuel tank differential pressure sensor.

STEP 4. Check the fuel vent valve plunger and flapper door operation.

NOTE: When a fuel nozzle is inserted to the fuel tank filler tube and the flapper door is opened, the fuel vent valve is closed (plunger moves towards the top of the neck). When the fuel cap is closed, the fuel cap pushes the plunger back in, which then opens the vent valve. If the flapper door or plunger does not operate properlx the vent valve stays closed even after the fuel cap is closed. This may block the vapor passage. A faulty vent valve plunger may also cause the fuel cap not to seat properly. Either of these conditions can set DTC P0442.

(1) Remove the fuel cap.

(2) Push the flapper in to operate the valve.

NOTE: When the flapper is pushed in, the plunger of the valve should move towards the top.

(3) Reinstall and tighten the fuel cap until three clicks are heard.

(4) Remove the cap again and check the protrusion of the plunger to verify if it is pushed back.

‘ V0381

~~

f " " - ;

__y _ .

(5) Distance between the tip of vent valve plunger and that of fuel tank filler tube should be 28 mm (1.1 inches) or more.

0 If the plunger does not return, replace the fuel tank filler tube and securely tighten the cap.

0 If the operation is OK, install and securely tighten the fuel cap.

STEP 5. Using scan tool MB991502, actuator test item 08 : Evaporative Emission Purge Solenoid.

(1) Disconnect the hose connected to the evaporative emission canister from the purge solenoid.

(2) Connect a hand vacuum pump to the nipple where the hose is disconnected at the previous step.

(3) The vacuum should be maintained when vacuum is applied and vacuum should leak when the purge solenoid is activated by the actuator test of scan tool MB991502.

If correct, go to Step 6.

0 If not, refer to DTC PO443 (Evaporative Emission Control System Purge Control Valve Circuit Malfunction) on P.13B-56.

STEP 6. Using scan tool MB991502, actuator test item 29 : evaporative Emission Ventilation Solenoid.

(1) Disconnect the hose connected to the vent solenoid valve from the evaporative emission canister.

(2) Connect a hand vacuum pump to the hose that is disconnected in the previous step.

(3) The vacuum should leak when vacuum is applied, and the vacuum should be maintained when the purge solenoid is activated by the actuator test of scan tool MB991502.

0 If correct, go to Step 7.

0 If not, refer to DTC PO446 (Evaporative Emission Control System Vent Control Malfunction) on

P. 13B-57.

13M0101

U I . " 1 … 114*.v".-- .

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

NOTE: Fuel temperature should be lower than 40°C (104°F) during the performance test.

In this step, verify if the EVAP system works properly, or determine which area of the evaporative emission system has a failure.

Caution As a 0 - 6.2 kPa (0 - 0.90 psi) range vacuum gauge is used, the gauge may be broken if excessive vacuum pressure is applied. Do not apply a vacuum of more than 2.9 kPa (0.42 psi).

To achieve the performance test efficiently, a mechanical vacuum gauge [0 - 6.2 kPa (0 - 0.90 psi) range] and scan tool MB991502 should be used, and the engine to generate vacu um .

i : J ’

(1) Install a mechanical vacuum gauge [0 - 6.2 kPa (0 - 0.90 psi) range] between the EVAP purge solenoid valve and the purge hose that comes from the evaporative emission canister.

(2) Before starting the performance test, set the vehicle in the following condition.

0 Engine coolant temperature: 80 - 90°C (1 76 - 203°F) 0 Lights and all accessories: OFF 0 Transmission: “N” or “P” position (3) Select the item TANK PRS SNSR (data lisf 73) on scan tool MB991502 to see the differential pressure sensor output.

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

,

NOTE: If there Is a system failure, either of both vacuum readings may not reach to the above specifications. In this case, it Is not necessary to pinch off the purge hose as shown. Refer to the performance test results table below for further steps.

(10)After an elapsed time of 20 seconds, check the fuel tank differential pressure reading on scan tool MB991502.

OK: Change in pressure reading is 0.4 kPa (0.06 psi) or less [holding -2.5 kPa (-0.36 psi) or more vacuum].

Performance test result table:

MECHANICAL VACUUM GAUGE READING

SCAN TOOL MB991502 READING

Reaches 2.9 kPa (0.42 psi).

Reaches -2.9 kPa (-0.42 psi) and vacuum drops not more than 0.4 kPa (0.06 psi) in 20 seconds.

Reaches 2.9 kPa (0.42 psi).

Does not reach -2.9 kPa (-0.42 psi).*

Does not reach 2.9 kPa (0.42 psi).

Does not reach -2.9 kPa (-0.42 psi).

Reaches 2.9 kPa (0.42 psi).

Reaches -2.9 kPa (-0.42 psi) but vacuum drops more than 0.4 kPa (0.06 psi) in 20 seconds.

NOTE

*: If there is a blockage, scan tool MB991502 reading can be a positive value (positive pressure) due to the heat of return fuel from the engine.

STEP 10. Vacuum reading on both the mechanical gauge and scan tool MB991502 reaches the specifications and satisfy the specifications after 20 seconds:

EVAP system is properly working at the moment. The cause of DTC might have been a loose fuel cap and the customer may have already tightened fuel cap causing the MIL to turn on. No further steps are needed.

RESULT

GO TO

Satisfactory.

No leak nor blockage detected.

Blockage in the system or I Step 11 bad differential sensor.

I , Large leak in EVAP system.

! Step 13

~

Small leak in EVAP system.

i

STEP 11. Vacuum reading on the mechanical gauge reaches 2.9 kPa (0.42 psi) but scan tool MB991502 does not reach -2.9 kPa (-0.42 psi) :

(1) If the vacuum reading on the gauge reaches 2.9 kPa (0.42 psi) but the reading on scan tool MB991502 does not reach -2.9 kPa (-0.42 psi), either a system blockage or a bad differential pressure sensor may be the cause.

(2) To determine if there is a blockage in the system, remove the fuel cap.

0 If the vacuum reading on the vacuum gauge [at this point 2.9 kPa (0.42 psi)] remains the same, there is a blockage in the system. Go to Step 12.

If the reading drops to about 0 kPa (0 psi), there is no blockage in the EVAP system. The fuel tank differential pressure sensor needs to be replaced.

After replacing the differential pressure sensor, go to Step 15.

STEP 12. System blockage inspection.

(1) Disconnect the number 1 and 2 hoses shown in the illustration, check the mechanical vacuum gauge reading.

If the vacuum reading does not drop, then the blockage is not in the fuel tank.

(2) Qisconnect one portion of the EVAP system at a time working towards the front of the vehicle until blockage is found (number 1 to 5 hoses in the illustration).

(3) Repair the location of the blockage and go to Step 15.

I I rn

x PURGE SOLENOID

VENTILATION I 5

IVAPORATIVE !MISSION CANISTER FUEL TANK B03'0115

STEP 13. Vacuum readings on both the mechanical gauge and scan tool MB591502 do not reach the specifications [2.9 kPa (0.42 psi) and -2.9 kPa (-0.42 psi)] :

This condition shows that there is a significant leakage in the system. The inspection procedure for the large system leakage is the same as the small leakage test in Step 14.

STEP 14. Vacuum readings on both the mechanical gauge and scan tool MB991502 do not reach the specification [2.9 kPa (0.42 psi) and -2.9 kPa (-0.42 psi)] but do not maintain the vacuum.

This condition shows that there is a slight leakage in the system. Follow the procedure below to locate the source of the leak.

(1) The fuel cap relief valve inspection.

a. Remove the fuel cap and install the fuel tank filler tube adapter in the emission system tester kit in place of the fuel cap.

b. Plug the nipple on the fuel tank filler tube adapter.

c. Repeat the performance test. If the EVAP system holds the vacuum, then the fuel cap is faulty. Replace the fuel cap, and go to Step 15.

A03Z0089

(2) To find the vacuum leakage in the system, clamp the number 1 and 2 hoses shown in the illustration. Repeat the performance test. This will determine if the vacuum leak is either in the fuel tank area or in the rest of the system.

NOTE: In this case, as we clamped off the vacuum hose connecting to the fuel tank, scan tool MB991502 reading will not change. Please use the mechanicalgauge reading.

0 If the EVAP system hold the vacuum leak is in the fuel tank area. To locate the leakage, pressurize the EVAP system to 3.4 kPa (0.49 psi) and look for leaky area using the ultrasonic leak detector in the Evaporative Emission System Tester. After repairing the leakage, go to Step 15.

VENTILATION SOL

I LIQUID SEPARATOR

If the vacuum leak still exists, the leak is at other than fuel tank area.

(3) Clamp off the vacuum hose one component at a time working towards the front of the vehicle until leakage is found (number 1 to 5 hoses shown in the illustration).

(4) Repair the leakage at that location and go to Step 15.

!VAPOR

:MISSION CANISTER FUEL TANK B03'0115

STEP 15. Confirmation test.

After system failures are repaired, repeat the Evaporative Emission System Leak Monitor test (Step 2) to check that the EVAP system operates correctly.

-_I

- __ ----

- - -

Code No. PO443 Evaporative Emission Control System Purge Control Valve Circuit Malfunction

Background 0 The engine control module checks current flows in the evaporative emission purge solenoid (No 1) drive circuit when the solenoid is ON and OFF.

Check Area 0 Battery voltage is not lower than 1OV Judgment Criteria 0 Solenoid coil surge voltage (more than system voltage +2V) is not detected when the EVAP purge solenoid is turned on/off.

0 Monitored only once per trip

- Replace

NG

~ (Refer to GROUP 17 - Emission Control System )-

----

-~

_ _ _ _ _ ~ f OK evaporative emission purge solenoid con- ~-~

1 L ~ ~ _ _ _ _ _ ~ side OK: Battery positive _____ voltage OK __ lN

-1 Check the harnesswire between MFI relay and solenoidvalve connector.

0 Disconnect the connector and measure at the harness

0 Voltage between 2 and ground (Ignition switch: ON)

1

1 Measure at the ECM connector 8-40, 0 Disconnect the connector and measure at the harness

Voltage between 9 and ground (Ignition switch. ON) OK: Battery Dositive voltaae

I . .

L- ~~~

- -L

- ____I I Check trouble symptom.

' NG 7 ' Check the harness wire between ECM and solenoid valve connector.

Probable cause

~ ~ ~- 0 Evaporative emission purge solenoid failed 0 Open or shorted evaporative emission purge solenoid circuit, or loose connector 0 Engine control module failed

1 Repair, if necessary.

+ Repair connector:

I OK

~ Repair, if necessary

--- - I Code No. PO446 Evaporative Emission Control System Vent Control Malfunction

~~ _ _ ~ ~ ~ ~ [Comment] Background 0 The engine control module checks current flows in the evaporative emission ventilation solenoid drive circuit when the solenoid is ON and OFF Check Area 0 Battery voltage is 10 V or higher.

Judgment Criteria 0 Solenoid coil surge voltage (system voltage +2 V) is not detected when the EVAP emission vent solenoid is turned on/off.

0 Monitored only once per trip.

1 Check the evaporative emission purge solenoid.

1 NG- Replace

Probable cause

~ ~ ~ _ _ _ _ _ _ 0 Evaporative emission ventilation solenoid failed.

0 Open or shorted evaporative emission ventilation solenoid circuit, or loose connector 0 Engine control module failed.

Check the harness wire between MFI relay and solenoidvalve connector.

I Repair. if necessarv.

- - Repair

Check the following con- -~ NG nectors: B-36. E-13. F-19

' OK 1

Repair, if necessary ~

-

- ~

1

Code No.

I PO450

I Evaporative Emission Control System Pressure Sensor

~ Malfunction

Fuel Tank Differential Pressure Sensor Circuit

FUEL TANK DIFFERENTIAL PRESSURE SENSOR

1310085

I CONNECTOR: B-36

CONNECTOR: E-23 I

B16MO440 I

CIR CU IT OPE RATION

0 A 5-volt voltage is supplied to the powerterminal of the fuel tank differential pressure sensor (terminal 3) from the ECM (terminal 81). The ground terminal (terminal 2) is grounded with

1 the ECM (terminal 92).

0

A voltage proportional to the pressure in the fuel tank is sent from the output terminal of the fuel tank differential pressure sensor (terminal 1) to the ECM (terminal 61).

TECHNICAL DESCRIPTION

0 The fuel tank differential pressure sensor outputs the voltage in proportion to the pressure in the fuel tank (differential pressure against the barometric pressure).

The ECM checks whether the output voltage of the fuel tank differential pressure sensor is with in the specified range.

0

DTC SET CONDITIONS Check Area

0 Intake air temperature is higher than 5°C (41 OF).

0 Engine speed is higher than 1,600 r/min.

0 Volumetric efficiency is between 20 and 80 percent.

Judgement Criteria

0 The sensor output voltage is more than 4 volts for 10 seconds even if the evaporative emission purge solenoid is driven at a 100 percent duty when the intake air temperature is between 5 and 45°C (41 - 113°F).

1 or

1 CONNECTOR: E-22 { / \ I

CONNECTORS: 8-37, B-38

1 / B16M0264

0 The sensor output voltage is less than 1 volt for 10 seconds even if the evaporative emission purge solenoid is not driven when the intake air temperature is 5°C (41°F) or more.

Check Area

The throttle valve is closed.

Engine speed is 840 r/min or less.

Vehicle speed is 1.5 km/h (0.93 mph) or less.

0 0 0

Judgement Criteria The events are counted 20 times or more that sudden pressure fluctuation of at least 0.2 volts is detected for 25 milliseconds or more.

The above events are detected continuous eight times during normal driving condition.

0

0

NOTE: If the number of the pressure fluctuation does not reach 20 during one engine idling, the count number will be reset to zero. In addition, the count number will be also reset to zero if the ignition switch is turned off.

NOTE: The engine control module determines that the engine has deflected from the idle operation if all of the following conditions are met.

0 Engine speed is higher than 2,500 r/min.

0 Vehicle speed is 15 km/h (9.3 mph) or more.

0 Volumetric efficiency is 55 percent or more.

TROUBLESHOOTING HINTS The most likely causes for this code to be set are:

0 Fuel tank differential pressure sensor failed.

0 Open or shorted fuel tank differential pressure sensor circuit, or loose connector.

0 ECM failed.

i ___- ”_._

- _

- ._ - OVERVIEW OF TROUBLESHOOTING

0 DTC PO450 can be set if either of the following conditions occur:

1. Faulty fuel tank differential pressure sensor, related circuit, or ECM.

2. Faulty fuel tank filler tube vent valve or blocked vapor line.

If the fuel tank filler tube vent valve is faulty and stays closed or the vapor line is blocked, the pressure inside the fuel tank is increased as the evaporative fuel is not purged especially at hot ambient temperatures. Once the pressure inside the fuel tank reaches 6 kPa, the sensor output voltage also reaches and remains 4.5 volts. This will set DTC P0450.

To check a system blockage, do a performance test which uses a mechanical vacuum gauge and scan tool MB991502 (MUT-11) set on the fuel tank differential pressure sensor (TANK PRS SNSR 73). The mechanical gauge reading is used to verify scan tool MB991502 reading. A comparison of the mechanical gauge to scan tool MB991502 determines the problem in the system.

0

DIAGNOSIS Required Special Tool:

MB991502: Scan Tool (MUT-11)

Caution To prevent damage to scan tool MB991502, turn the ignition switch off before connecting or disconnecting scan tool MB991502.

In this procedure, scan tool MB991502 should be used in the metric mode (showing the value in kPa). If not, set scan tool MB991502 by selecting the “System Setup” at the main menu.

STEP 1. Using scan tool MB991502, check “Fuel tank differential pressure sensor (date list 73)” output.

In this step, check the fuel tank differential pressure sensor reading to determine if the fuel tank differential pressuresensor is operating correctly.

(1) Check the MFI data list item: TANK PRS SNSR 73 (2) Watch the sensor reading. This value varies depending on pressure inside the fuel tank.

(3) Remove the fuel cap.

(4) After the fuel cap has been removed, the pressure sensor readincl should be between -0.5 kPa (-0.07 psi) and

0.5 0

0

kFa (0.07 psi).

If the reading is between -0.5 kPa (-0.07 psi) and 0.5 kPa (0.07 psi), the DTC could be caused by an intermittent electrical malfunction, or by a blockage in the EVAP system. Go to step 2.

If the reading is not between -0.5 kPa (-0.07 psi) and 0.5 kPa (0.07 psi), there is an electrical malfunction. Go to step 9.

. 1 -

--.“.= MFI

-_. 4.8L _^.

STEP 2. Check the fuel vent valve plunger and flapper door operation.

NOTE: When a fuel nozzle is inserted to the fuel tank filler tube and the flapper door is opened, the fuel vent valve is closed (plunger moves towards the top of the neck). When the fuel cap is closed, the fuel cap pushes the plunger back in, which then opens the vent valve. If the flapper door or plunger does not operate properlx the vent valve stays closed even after the fuel cap is closed. This may block the vapor passage and set the DTC P0450.

(1) Remove the fuel cap.

(2) Push the flapper in to operate the valve.

NOTE: When the flapper is pushed in, the plunger of the valve should move towards the top.

(3) Reinstall and tighten the fuel cap until three clicks are heard.

(4) Remove the cap again and check the protrusion of the plunger to verify if it is pushed back.

(5) The distance between the tip of vent valve plunger and that of fuel tank filler tube should be 28 mm (1.1 inches) or more.

0 If the plunger does not return, replace the fuel tank filler tube and securely tighten the cap.

0 If the operation is OK, install and securely tighten

N .

V0381AA

STEP 3. Evaporative Emission System Leak Monitor Test using scan tool MB991502.

NOTE: This monitor is carried out at an engine speed of 1,600 r/min or more, transmission is in “N” or “R” position.

The engine speed has to be automatically adjusted.

(1) Erase the DTCs using scan tool MB991502. Ensure that the fuel cap is securely tightened.

(2) Select “System Test” and press “YES” key.

(3) Select “Evap Leak Mon” and press “YES” key.

(4) If “Evap beak Mon” is selected before starting the engine, “Engine must be running.” is displayed. In this case, start the engine and then select “Evap Leak Mon” again.

(5) If “Keep the TPS in idle position. during the test.” is displayed, the ECM or PCM adjusts engine speed automatically. A manual adjustment for engine speed is not needed.

(6) Keep the idling position during the monitor.

NOTE: If the engine speed does not reach 2,000 r/min during the monitor test, adjustment of the SpeedAdjusting Screw may be needed. Refer to P13B-143 for the adjustment procedure.

(7) Item “In Progress” is displayed during the monitor. Keep the engine speed and load within the defined range. Scan tool MB991502 shows these items on the screen.

Item “In Progress” will be change from “NO” to “YES” by keeping engine conditions.

-

(8) Message “Evap Leak Mon. Completed. Test Passed.” is displayed when the test has been completed without malfunction. Evaporative emission system is working property at the moment. Please explain to customer that improperly tightened fuel cap can cause to turn MIL on.

No further steps are needed.

(9) Message “Evap Leak Mon. Completed. Test Failed 8.

DTCs Set.” is displayed when a malfunction has been detected during the test. Go to Step 4.

(1 0) Message “Evap Leak Mon. discontinued. Retest again from the first” is displayed when the monitor was discontinued by a certain reason (input vehicle speed, engine speed and engine load was put of the specified range). Turn the ignition switch off once and start the monitor from the beginning.

NOTE: The monitor will not start unless turning off the ignition switch once and restart the engine.

STEP 4. Check the purge solenoid-to-air intake plenum hose for blockage.

(1) Disconnect the purge solenoid-to-air intake plenum hose at the purge solenoid side.

(2) Connect a hand vacuum pump to the disconnected hose end.

(3) Apply vacuum, and check if the vacuum is not maintained.

0 If not maintained, go to STEP 5.

0 If maintained, replace the hose or intake plenum.

Then go to STEP 6.

-

STEP 5. Check the purge solenoid-to-air intake plenum hose for vacuum leakage.

(1) Plug the purge solenoid-to-air intake plenum hose at the purge solenoid side.

(2) Disconnect the purge solenoid-to-air intake plenum hose at the air intake plenum side.

(3) Connect a hand vacuum pump to disconnected hose end.

(4) Apply vacuum, and check if the vacuum is maintained.

0 If maintained, go to STEP 6.

0 If not maintained, replace the hose. Then go to STEP

STEP 6. Performance test.

NOTE: Fuel temperature should be lower than 40°C (104°F) during the performance test.

In this step, verify if the EVAP system works properly, or determine which area of the evaporative emission system has a failure.

J i

Caution As a 0 - 6.2 kPa (0 - 0.90 psi) range vacuum gauge is used, the gauge may be broken if excessive vacuum pressure is applied. Do not apply a vacuum of more than 2.9 kPa (0.42 psi).

To achieve the performance test efficiently, a mechanical vacuum gauge [0 - 6.2 kPa (0 - 0.90 psi) range] and scan tool MB991502 should be used, and the engine to generate vacuum.

Install a mechanical vacuum gauge [0 - 6.2 kPa (0 - 0.90 psi) range] kjetween the EVAP purge solenoid valve and the purge hose that comes from the evaporative emission canister.

Before starting the pedormance test, set the vehicle in the following condition.

Engine coolznt temperature: 80 - 90°C (176 - 203°F) Lights and all accessories: OFF 0 Transmission: “N” or “P” position Select the item TANK PRS SNSR (data list 73) on scan tool MB991502 to see the fuel tank differential pressure sensor output.

Run the engirrcr at idle.

Using locking pliers, pinch the hose between the purge solenoid and the intake plenum to close the purge flow, as a preparation of the performance test.

(6) Using another locking pliers, pinch the vent hose between the evaporative emission canister and the vent solenoid.

Momentary, remove the locking pliers at the purge hose;

this will cause the vacuum build up in the EVAP system.

(7) The engine vacuum comes from the purge port through the purge solenoid.

NOTE: During this operation, the purge solenoid may turn off but will resume in operation in about 20 seconds.

Operation of the purge solenoid can be checked by needle fluctuation of the mechanical vacuum gauge.

(8) Watch the vacuum reading on the mechanical vacuum gauge and scan tool MB991502.

(9) When the vacuum reading reaches 2.9 kPa (0.42 psi) on the mechanical vacuum gauge and -2.9 kPa (-0.42 psi) on scan tool MB991502, pinch the hose between the purge solenoid and the intake manifold plenum using another locking pliers; this stops the application of vacuum and seals the EVAP system for the leak test.

NOTE: If there is a system failure, either of both vacuum readings may not reach to the above specifications. In this case, it is not necessary to pinch off the purge hose as shown. Refer to the performance test results table below for further steps.

(5O)After an elapsed time of 20 seconds, check the fuel tank differential pressure reading on scan tool MB991502.

OK: Change in pressure reading is 0.4 kPa (0.06 psi) or less [holding -2.5 kPa (-0.36 psi) or more vacuum].

Performance test result table:

MECHANICAL VACUUM GAUGE READING

SCAN TOOL MB991502 READING

Reaches 2.9 kPa (0.42 psi).

Reaches -2.9 kPa (-0.42 psi) and vacuum drops not more than 0.4 kPa (0.06 psi) in 20 seconds.

Does not reach -2.9 kPa (-0.42 psi).* _ _ _ _ ~

- _______

Reaches 2.9 kPa (0.42 psi).

Does not reach 2.9 kPa (0.42 psi).

Does not reach -2.9 kPa (-0.42 psi).

Reaches 2.9 kPa (0.42 psi).

Reaches -2.9 kPa (-0.42 psi) but vacuum drops more than 0.4 kPa (0.06 psi) in 20 seconds.

NOTE *: If there is a blockage, scan tool MB991502 reading can be positive value (positive pressure) due to heat of return fuel frorn the engine.

j RESULT

Satisfactory.

1 Step 7 No leak nor blockage detected. 1

Blockage in the system or bad ' Step 8 differential pressure sensor.

1

Large leak in EVAP system.

~ Step 11

Small leak in EVAP system.

1 Step 12

~
