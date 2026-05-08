---
type: manual_section
vehicle: '[[Car_Mitsubishi_Mirage_1999]]'
title: MFI 1.5L (впрыск) — General Information
title_en: MFI 1.5L — General Information
chapter_code: 13A
chapter: MFI 1.5L (впрыск)
section: General Information
section_index: page-3
volume: Volume 1
source_pdf: 13A MFI 1.5L.pdf
page_range: 3-6
page_count: 4
topics:
- fuel_injection
aliases:
- 13A General Information
- 13A-General_Information
- MFI 1.5L General Information
related_parts: []
related_issues: []
last_verified: '2026-05-08'
tags:
- manual
- fuel_injection
---

# MFI 1.5L (впрыск) — General Information

> **Глава:** `13A` MFI 1.5L  
> **Источник:** `13A MFI 1.5L.pdf` (стр. 3-6)  
> **Авто:** [[Car_Mitsubishi_Mirage_1999]]

---

The Multiport Fuel Injection System consists of sensors which detect the engine conditions, the ENGINE CONTROL MODULE (ECM) which controls the system based on signals from these sensors, and actuators which operate under the control of the ECM.

The ECM carries out activities such as fuel injection control, idle air control, and ignition timing control.

In addition, the ECM is equipped with several diagnostic test modes which simplify troubleshoot- ing when a prqblem develops.

FUEL INJECTION CONTROL The injector drive times and injector timing are controlled so that the optimum air/fuel mixture is supplied to the engine to correspond to the continually-changing engine operation conditions.

A single injector is mounted at the intake port of each cylinder. Fuel is sent under pressure from the fuel tank to the fuel injectors by the fuel pump, with the pressure being regulated by the fuel pressure regulator. The regulated fuel is distributed to each of the injectors.

Fuel injection is normally carried out once for each cylinder for every two rotations of the crankshaft.

The firing order is 1-3-4-2. Each cylinder has a dedicated fuel injector. This is called multiport. The ECM provides a richer air/fuel mixture by carrying out “open-loop’’ control when the engine is cold or operating under high load conditions in order to maintain engine performance.

In addition, when the engine is under normal operating temperature after warming-up, the ECM controls the air/fuel mixture by using the heated oxygen sensor signal to carry out ”closed-loop” control. The closed-loop control achieves the theoretical air/fuel mixture ratio where the catalytic converter can obtains the maximum cleaning performance.

IDLE AIR CONTROL The idle speed is kept at the optimum speed by controlling the amount of air that bypasses the throttle valve in accordance with changes in idling conditions and engine load during idling.

The ECM drives the idle air control (IAC) motor to keep the engine running at the pre-set idle target speed in accordance with the engine coolant temperature and air conditioning load. In addition, when the air conditioning switch is turned off and

13100010708

on while the engine is idling, the IAC motor adjusts the throttle valve bypass air amount according to the engine load conditions to avoid fluctuations in the engine speed.

IGNITION TIMING CONTROL The ignition power transistor located in the ignition primary circuit turns ON and OFF to control the primary current flow to the ignition coil. This controls the ignition timing to provide the optimum ignition timing with respect to the engine operating conditions. The ignition timing is determined by the ECM from the engine speed, intake air volume, engine coolant temperature, and atmospheric pressure.

DIAGNOSTIC TEST MODE

When an abnormality is detected in one of the sensors or actuators related to emission control, the SERVICE ENGINE SOON/MALFUNCTION INDICATOR LAMP illuminates to warn the driver.

When an abnormality is detected in one of the sensors or actuators, a diagnostic trouble code corresponding to the abnormality is stored in the ECM.

The RAM data inside the ECM that is related to the sensors and actuators can be read with the scan tool.

In addition, the actuators can be controlled by the Scan tool (MUT-11) under certain circumstances.

OTHER CONTROL FUNCTIONS .

1.

Fuel Pump Control Turns the fuel pump relay ON so that current is supplied to the fuel pump while the engine is cranking or running.

A/C Compressor Clutch Relay Control Turns the compressor clutch of the A/C ON and OFF.

Fan Relay Control The radiator fan and condenser fan speeds are controlled in response to the engine coolant temperature and vehicle speed.

Evaporative Emission Purge Control (Refer to GROUP 17.) EGR Control (Refer to GROUP 17.)

2.

3.

4.

5.

GENERAL SPECIFICATIONS

Items

Throttle bore mm (in.)

Throttle body

Throttle position sensor ~-

Idle air control motor Stepper motor (Stepper motor type by-pass air control system with the air volume limiter)

Closed throttle position switch

Idle air control valve position sensor

Identification model No.

Engine control module (ECM)

Manifold absolute pressure sensor

Sensors

Intake air temperature sensor

Engine coolant temperature sensor

Heated oxygen sensor 1 Zirconia type

Park/Neutral position switch

Camshaft position sensor

Crankshaft position sensor

Power steering pressure switch

Multiport fuel injection (MFI) relay 1 Contact switch type

Actuators

Fuel pump relay ~ Contact switch type

Injector type and number I Electromagnetic type, 4

EGR solenoid

Evaporative emission purge solenoid

Regulator pressure kPa (psi) Fuel pressure regulator

Specifications

46 (1.81)

Variable resistor type

Rotary contact type, within throttle position sensor

--

Hall element type

E2T69284 <Federal> E2T69283 <California>

Semiconductor type

Thermistor type

Thermistor type

Contact switch type

Hall element type

Hall element type

Contact switch type

Duty cycle type solenoid valve

Duty cycle type solenoid valve

335 (47.6)

MULTIPORT FUEL INJECTION (MFI) SYSTEM DIAGRAM <Vehicles for Federal>

SENSE

*1 Heated oxygen sensor (front) *2 Intake air temperature sensor *3 Throttle position sensor *4 Closed throttle position switch *5 Camshaft position sensor *6 Crankshaft position sensor *7 Engine coolant temperature sensor *8 Heated oxygen sensor (rear) +9 Manifold absolute pressure sensor h10Fuel tank differential pressure sensor

…

0 Power supply 0 Vehicle speed sensor 0 AIC switch 0 Park/Neutral position switch 0 Power steering pressure switch 0 Ignition switch-ST

*3,**4 Throttle position sensor (with closed throttle position switch) A2 Intake air temperature sensor +3 Idle air control motor 4

A9 Manifold absolute Air cleaner pressure sensor

perature sensor

emission 1FU 1 2 7 4 canister Distributor sensor

+3 Idle air control motor +4 EGR solenoid +5 Evaporative emission ventilation solenoid

.

…

0 Fuel pump relay 0 Multiport fuel injection (MFI) relay 0 A/C compressor clutch relay 0 Service Engine Soon/Malfunction Indicator Lamr 0 Diagnostic output 0 Ignition coil, Ignition power transistor

*2 Evaporative emission purge solenoid

*lo Fuel tank differential pressure sensor

<Vehicles for California>

SENSE DECIDE

c3 Engine control module +1 Injector +2 Evaporative emission purge solenoid +3 Idle air control motor +4 EGR solenoid +5 Evaporative emission venblation solenoid

*1 Heated oxygen sensor (front) *2 Intake air temperature sensor *3 Throttle position sensor *4 Closed throttle position switch +5 Camshaft position sensor +6 Crankshaft position sensor *7 Engine coolant temperature sensor *8 Heated oxygen sensor (rear) *9 Manifold absolute pressure sensor *1 OFuel tank differential pressure sensor

. _ .

0 Power supply 0 Vehicle speed sensor 0 A/C switch 0 Park/Neutral position switch 0 Power steering pressure switch 0 lqnition switch-ST

*3, *4 Throttle position sensor (with closed throttle position switch)

A2 Intake air 4 temperature

A9 Manifo pressu

*1 Heated oxygen sensor

-.r

(front) I il +2 Evaporative emission purge solenoid

Evaporative emission 1 FU12?5 sensor (rear) canister

ACT

0 Fuel pump relay 0 Multiport fuel injection (MFI) relay 0 A/C compressor clutch relay 0 Service Engine Soon/Malfunction Indicator Lamp 0 Diagnostic output 0 Ignition coil, Ignition power transistor

A

+3 Idle air control motor

*lo Fuel tank differential pressure sensor 4
