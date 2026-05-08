---
type: manual_section
vehicle: '[[Car_Mitsubishi_Mirage_1999]]'
title: Антиблокировочная система (ABS) — Troubleshooting
title_en: Anti lock braking — Troubleshooting
chapter_code: 35B
chapter: Антиблокировочная система (ABS)
section: Troubleshooting
section_index: page-20
volume: volume 2
source_pdf: 35B Anti lock braking.pdf
page_range: 20-25
page_count: 6
topics:
- brakes
- abs
- diagnostics
aliases:
- 35B Troubleshooting
- 35B-Troubleshooting
- Anti lock braking Troubleshooting
related_parts: []
related_issues: []
last_verified: '2026-05-08'
tags:
- manual
- brakes
- abs
---

# Антиблокировочная система (ABS) — Troubleshooting

> **Глава:** `35B` Anti lock braking  
> **Источник:** `35B Anti lock braking.pdf` (стр. 20-25)  
> **Авто:** [[Car_Mitsubishi_Mirage_1999]]

---

ABS <FWD>

- Troubleshooting

Inspection Procedure 3

When ignition key is turned to “ON” (engine stopped), Probable cause ABS warning light does not illuminate.

The cause may be: an open circuit in the light power supply circuit, a blown light 
- Blown fuse bulb, anopencircuit in both thecircuit betweenthe ABS warmng lightand the ABS-ECU.

- Burnt out ABS warning light bulb

Refer to GROUP 00 - Inspection Ser- vice Points for Blown Fuse.

Check whether the ABS warning light Replace the ABS warntng light bulb.

bulb is burnt out.

- Ignition switch:

ON

- Does the ABS warning light

ECU and connector B-08. Reparr rf nec-

Inspection Procedure 4

Even after the engine is stat-ted, the ABS warning light Probable cause ~ remains illuminated.

The cause is probably a short-circuit in the ABS warning light illumination circuit.

- Malfunction of combinatron meter

NOTE This trouble symptom is limited to cases where communication with the scan tool is possible (ABS-ECU power supply is normal) and the diagnostic trouble code is a normal diagnostic trouble code.

- Disconnect connector B-08

- Does the ABS warnmg light remain illuminated?

!No

Yes

- DisconnectABS-ECU connectorB-30andvalverelayconnector

- A-46.

- Ignition switch:

ON

- Does the ABS warnrng light swatch off?

1 No 1

Check the harness between the combination meter and the ABS- ECU. Repair if necessary.

- Malfunction of wiring harness or connector

Replace the combrnation meter.

- Malfunctton of ABS-ECU 0 Malfunction of winng harness

- Reolace the combinatron meter.

-W Replace the ABS-ECU.

.

ABS cFWD>

- Troubleshooting

Inspection Procedure 5

When the ignition key is turned to “START”, the ABS Probable cause warning light does not illuminate.

Current does not flow in the ABS-ECU when the ignition switch IS turned to “START”.

- Malfunction of wiring harness or connector Current flows in the ABS warning lrght even when the Ignition switch is turned to 
- Malfunction of ABS-ECU “START”.

Therefore, the valve relay, which current is supplred through the ABS-ECU, turns off when the ignition switch is at “START”.

However, the warning lrght circuit of the valve relay must turn on in turn. So the cause must be a defective circuit on valve relay side.

Disconnect valve relay connector

Disconnect ABS-ECU connector

- Voltage between valve relay harness-side connector terminal (5) and body ground OK:

System voltage

1 OK NG Check the following connector:

, A-46

* Repair

I OK

NG

w Check the harness between the valve relay and earth. and repair if necessary.

Inspection Procedure 6

After the ignition key is turned to “ON”, the ABS warning Probable cause light blinks twice, and when turned to “START”, it illuminates. When returned to “ON”, the light flashes once, and then switches off.

The ABS-ECU causes the ABS warning light to illuminate during the initial check 
- Malfunction of wiring harness or connector (approx.

3 seconds), During the initial check, the valve relay turns from off to on, 
- Malfunction of ABS-ECU off and back to on agarn. If there IS an open circuit in the harness between the ABS-ECU and the ABS warning light, the light will illuminate only when the valve relay is OFF during valve relay test, etc.

NG c

Check the harness between the com-

A-46.

- Disconnect ABS-ECU connector B-30.

- Ignition switch:

ON

- Voltage between ABS-ECU har- ness-side connector terminal (44) and body ground OK:

System voltage I -..

E 4 UK NG Check the following connector:

* Repair / B-30 t OK 1 Check trouble symptoms.

Replace the ABS-ECU.

Inspection Procedure 7

Brake operation is abnormal.

Probable cause

This varies depending on the driving conditions and the road surface condrtrons, so l problem diagnostic trouble is difficult.

However, if a normal diagnostic trouble code Improper installation of wheel speed sensor

is displayed, carry out the following inspection.

NG F Repair

Wheel speed sensor output voltage in- spectron (Refer to P.358-27.) Wheel speed sensor inspection (Refer

1 NG *j to P.358-39.) , OK f- Replace the wheel speed sensor.

/OK f

Hydraulic unit check (Refer to P.358-28.) Rotor Inspection (Refer to P.35B-40.)

vice.)Refer to GROUP 27 - On-vehicle

OK 1 > NG = Repair A-09,A-38, E-12, E-l 8, B-53, E-10. B-48 /

‘OK t @

- Incorrect sensor harness contact 0 Foreign material adhering to wheel speed sensor

- Malfunction of wheel speed sensor

- Malfunction of rotor

- Malfunctron of wheel bearing

- Malfunctron of hydraulrc unit

- Malfunction of ABS-ECU

I

.

ABS cFWD>

- Troubleshooting

DATA LIST REFERENCE TABLE

The following items can be read by the scan tool from the ABS-ECU input data.

1. When the system is normal

Item No.

Check item Checking requirements Normal value

11 Front-right wheel speed sensor Perform a test run Vehicle speeds displayed on the 12 Front-left wheel speed sensor speedometer and scan tool 13 Rear-right wheel speed sensor are identical.

14 Rear-left wheel speed sensor

16 ABS-ECU power supply Ignition switch power supply voltage and valve 9-l 6 V voltage monitor voltage

33 Stop light switch Depress the brake pedal.

ON

Release the brake pedal.

OFF

2.

When the ABS-ECU shut off ABS operation.

When the diagnostic trouble system stops the ABS-ECU, the scan tool display data will be unreliable.

ACTUATOR TEST REFERENCE TABLE 35201160032

The scan tool activates the following actuators for testing.

NOTE

I. ‘ +-xi ,

If the ABS-ECU runs down, actuator testing cannot be carried out.

Actuator testing is only possible when the vehicle is stationary. If the vehicle speed during actuator testing exceeds 10 km/h (6 mph), forced actuation will be canceled.

During the actuator test, the ABS warning light will illuminate and the anti-lock control will be cancelled.

1.

2.

3.

ACTUATOR TEST SPECIFICATIONS

Activation pattern

No.

/ Item

01 Solenoid valve for front-left Solenoid valves and pump wheel motors in the hydraulic unit

!$z;

2TT

Solenoid valve

02 Solenoid valve for front-right (s’mple inspection mode) wheel

/’

48 ms j 8ms

-

03 Solenoid valve for rear-left wheel

04 Solenoid valve for rear-right wheel

NOTE A: Hydraulic pressure increase B: Hydraulic pressure holds C: Hydraulic pressure decrease

35201150084

CHECK AT ABS-ECU 35201180113

TERMINAL VOLTAGE CHECK CHART

1. Measure the voltages between terminals (15), (25) and (42) (ground terminals) and each respective terminal.

NOTE ’ Do not measure terminal voltage for approx. 3 seconds after the ignition switch is turned on. The ABS-ECU performs the initial check for that period.

2.

The terminal layouts are shown in the illustrations below.

Con- Signal Checking requirements Normal nectar condition termi- nal No.

Output to rear-right so- Ignition switch: ON (When solenoid valve is off) System voltage “,%a- ._

14 Output to front-left sole- noid valve (OUT)

15 Output to rear-right so- lenoid valve (OUT)

16 Output to front-left solenoid valve (IN)

Memory power supply Always System voltage

25

ABS-ECU power supply Ignition switch: ON System voltage

26

Ignition switch: START ov

Input from diagnostic Connect the scan tool.

ov indication selection Do not connect the scan tool.

Approx. 12 V

33

Valve relay monitor Ignition switch: ON System voltage

34

Motor monitor Ignition switch: ON Motor is on.

System voltage

35

Output to rear-left Ignition switch: ON (When solenoid valve is off) System voltage solenoid valve (OUT)

37

38 Output to front-right solenoid valve (IN)

40 Input from stop light Ignition switch: ON Stop light switch ON switch Stop light switch OFF

t4Y0076

Motor is off.

0.5V or less

System voltage

1 V or less

.

Signal Checking requirements

Con- nector termi- nal No.

Connect the scan tool.

Serial communication with scan tool

41

Scan tool

Do not connect the scan tool.

1 V or less

Ignition switch; ON The relay is on.

2 V or less

Output to valve relay

42

Ignition switch: ON Motor is on.

2 V or less

Output to motor relay

43

Ignition switch: ON The light is switched off.

System voltage

44

Output to ABS warning light

Ignition switch: ON (When solenoid valve is off) System voltage

Output to rear-left solenoid valve (IN)

45

Output to front-right solenoid valve (OUT)

46

RESISTANCE AND CONTINUITY BETWEEN HARNESS-SIDE CONNECTOR TERMINALS

Turn the ignition switch off and disconnect the ABS-ECU connectors before checking resistance and continuity.

Check them between the terminals indicated in the table below.

The terminal layouts are shown in the illustrations below.

1.

2.

3.

Signal

Connector terminal No.

ABS-ECU ground

2 - Body ground

Front-left wheel speed sensor

6-l 9

Rear-right wheel speed sensor

Rear-left wheel speed sensor

ABS-ECU ground

17 - Body ground

31 - Body ground

39 - Body ground

Normal condition

The relay is off. The system runs down.

System voltage

Motor is off.

System voltage

The light is illuminated.

3 V or less

14YOO77

Normal condition

Continuity

1.4 - 1.8 kQ

1.4 - 1.8 kQ

1.4 - 1.8 kS2

Continuity
