---
type: manual_section
vehicle: '[[Car_Mitsubishi_Mirage_1999]]'
title: MFI 1.8L (впрыск) — General Information
title_en: MFI 1.8L — General Information
chapter_code: 13B
chapter: MFI 1.8L (впрыск)
section: General Information
section_index: page-2
volume: Volume 1
source_pdf: 13B MFI 1.8L.pdf
page_range: 2-5
page_count: 4
topics:
- fuel_injection
aliases:
- 13B General Information
- 13B-General_Information
- MFI 1.8L General Information
related_parts: []
related_issues: []
last_verified: '2026-05-08'
tags:
- manual
- fuel_injection
---

# MFI 1.8L (впрыск) — General Information

> **Глава:** `13B` MFI 1.8L  
> **Источник:** `13B MFI 1.8L.pdf` (стр. 2-5)  
> **Авто:** [[Car_Mitsubishi_Mirage_1999]]

---

13100010715

The Multiport Fuel Injection System consists of sensors which detect the engine conditions, the ENGINE CONTROL MODULE (ECM) which controls the system based on signals from these sensors, and actuators which operate under the control of the ECM.

The ECM carries out activities such as fuel injection control, idle air control, and ignition timing control.

In addition, the ECM is equipped with several diagnostic test modes which simplify troubleshoot- ing when a problem develops.

FUEL INJECTION CONTROL The injector drive times and injector timing are controlled so that the optimum air/fuel mixture is supplied to the engine to correspond to the continually-changing engine operation conditions.

A single injector is mounted at the intake port of each cylinder. Fuel IS sent under pressure from the fuel tank to the fuel injectors by the fuel pump, with the pressure being regulated by the fuel pressure regulator. The regulated fuel is distributed to each of the injectors.

Fuel injection is normally carried out once for each cylinder for every two rotations of the crankshaft.

The firing order is 1-3-4-2. Each cylinder has a dedicated fuel injector. This is called multiport. The ECM provides a richer airlfuel mixture by carrying out “open-loop” control when the engine is cold or operating under high load conditions in order to maintain engine performance.

In addition, when the engine is under normal operating temperature after warming-up, the ECM controls the air/fuel mixture by using the heated oxygen sensor signal to carry out “closed-loop” control. The closed-loop control achieves the theoretical air/fuel mixture radio where the catalytic converter can obtains the maximum cleaning performance.

IDLE AIR CONTROL The idle speed is kept at the optimum speed by controlling the amount of air that bypasses the throttle valve in accordance with changes in idling conditions and engine load during idling.

The ECM drives the idle air control (IAC) motor to keep the engine running at the pre-set idle target speed in accordance with the engine coolant temperature and air conditioning load. In addition, when the air conditioning switch is turned off and on while the engine is idling, the IAC motor adjusts the thrcttle valve bypass air amount according to the enqine load conditions to avoid fluctuations

in the engine speed.

IGNITION TIMING CONTROL The ignition power transistor located in the ignition primary circuit turns ON and OFF to control the primary current flow to the ignition coil. This controls the ignition timing to provide the optimum ignition timing with respect to the engine operating conditions. The ignition timing is determined by the ECM from the engine speed, intake air volume, engine coolant temperature, and atmospheric pressure.

DIAGNOSTIC TEST MODE

When an abnormality is detected in one of the sensors or actuators related to emission control, the SERVICE ENGINE SOON/MALFUNCTION INDICATOR LAMP illuminates to warn the driver.

When an abnormality is detected in one of the sensors or actuators, a diagnostic trouble code corresponding to the abnormality is stored in the ECM.

The RAM data inside the ECM that is related to the sensors and actuators can be read with the scan tool.

In addition, the actuators can be controlled by the scan tool (MUT-11) under certain circumstances.

OTHER CONTROL FUNCTIONS

1. Fuel Pump Control

Turns the fuel pump relay ON so that current is supplied to the fuel pump while the engine is cranking or running.

2. A/C Compressor Clutch Relay Control Turns the compressor clutch of the A/C ON and OFF.

3. Fan Relay Control

The radiator fan and condenser fan speeds are controlled in response to the engine coolant temperature and vehicle speed.

4. Evaporative Emission Purge Control (Refer to GROUP 17.)

5. EGR Control (Refer to GROUP 17.)

GENERAL SPECIFICATIONS

Items Specifications

-

- Throttle bore mm (in.)

Throttle body 50 (1.97)

Throttle position sensor

Stepper motor (Stepper motor type by-pass air control system with the air volume limiter)

- Closed throttle position switch Rotary contact type, within throttle position sen- sor

Idle air control motor

Hall element type Idle air control valve position sensor

Identification model No.

_ _ _ _ _ ~ E2173172<Federal> E2T73171 <California> Engine control module

Sensors Volume air flow sensor Karman vortex type

Barometric pressure sensor

Intake air temperature sensor

Engine coolant temperature sensor ~ ~ _ _ _ ~ ~ ~

Zirconia type Heated oxygen sensor

/Vehicle<eed sensor Electromagnetic: resistance element type

I Park/Neutral position switch Contact switch type

1 Camshaft position sensor

' brankshaft position sensor

I r

~~ Power steering pressure switch

- I I Actuators

~ Multiport fuel injection (MFI) relay

Fuel pump relay

Injector type and number

-

Injector identification mark CDH210

EGR solenoid Duty cycle type solenoid valve

Evaporative emission purge solenoid Duty cycle type solenoid valve

Regulator pressure kPa (psi) 335 (47.6) pressure regulator

Variable resistor type

Semiconductor type

Thermistor type

Thermistor type

I( I ..-?

Hall'dement type

~~ , ,' Halt element type

Contact switch type

Contact switch type

Contact switch type

Electromagnetic type, 4

MULTIPORT FUEL INJECTION (MFI) SYSTEM DIAGRAM <Vehicles for Federal>

DECIDE ACT I

SENSE

1 +1 Heated oxygen sensor (front) *2 Volume air flow sensor +3 Intake air temperature sensor *4 Throttle position sensor +5 Closed throttle position switch *6 Camshaft position sensor

I

1 +7 Crankshaft position sensor *8 Barometric pressure sensor *9 Engine coolant temperature sensor *lo Heated oxygen sensor (rear)

~ *11 Manifold differential pressure sensor

I *I2Fuel tank differential pressure sensor

I …

Power supply Vehicle speed sensor 0 A/C switch 0 Park/Neutral position switch I

I Ignition switch-ST Power steering pressure switch

*4 *5 Throttle position 43 Idle air control *3 Intake air temperature

A11 Manifold differential pressure sensor -

+3 Idle air control motor I +4 EGR solenoid +5 Evaporative emission ventilation solenoid

0 Fuel pump relay 1 0 Multiport fuel injection (MFI) relay A/C compressor clutch relay I 0 Service Engine Soon/Malfunctionlndicator Lam1

~ 0 Diagnostic output

0 Ignition coil, Ignition power transistor

Volume air flow sensor (with barometric pressure sensor)

so'enoid Evaporative emission canister

6FU2835

<Vehicles for California>

DECIDE ACT

~~ SENSE

~~~ 1

~ module r;

I +1 Injector i +2 Evaporative emission purge solenoid 1 +3 Idle air control motor +4 EGR solenoid +5 Evaporative emission ventilation solenoid

*1 Heated oxygen sensor (front)

Engine control

1 +2 Volume air flow sensor +3 Intake air temperature sensor *4 Throttle position sensor *5 Closed throttle position switch *6 Camshaft position sensor *7 Crankshaft position sensor *€I Barometric pressure sensor *9 Engine coolant temperature sensor +lo Heated oxygen sensor (rear) it1 1 Manifold differential pressure sensor +12 Fuel tank differential pressure sensor

0 Power supply 0 Vehicle speed sensor 0 A/C switch 0 Park/Neutral position switch 0 Power steering pressure switch 0 Ignition switch-ST

*4 *5 Throttle position *3 Idle air control *3 Intake air temperature

ssure sensor

i

10 Heated oxygen sensor (rear)

*1 Heated oxygen sensor (front)

0 Fuel pump relay 0 0 A/C compressor clutch relay 0 Service Engine Soon/Malfunctionlndicator Lami 0 Diagnostic output 0

Multiport fuel injection (MFI) relay

Ignition coil, Ignition power transistor

~~

Volume air flow sensor (with barometric pressure sensor)

6FU2836
