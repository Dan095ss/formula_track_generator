---
type: manual_section
vehicle: '[[Car_Mitsubishi_Mirage_1999]]'
title: Кузов — Door
title_en: Body — Door
chapter_code: '42'
chapter: Кузов
section: Door
section_index: page-21
volume: volume 2
source_pdf: 42 Body.pdf
page_range: 21-41
page_count: 21
topics:
- body
aliases:
- 42 Door
- 42-Door
- Body Door
related_parts: []
related_issues: []
last_verified: '2026-05-08'
tags:
- manual
- body
---

# Кузов — Door

> **Глава:** `42` Body  
> **Источник:** `42 Body.pdf` (стр. 21-41)  
> **Авто:** [[Car_Mitsubishi_Mirage_1999]]

---

c .

42300010032

t GENERAL INFORMATION P OPERATION

Power windows

’ 
- When the power window (main or sub) switch is depressed (UP or DOWN) with the ignition switch in the ON position, current flows through fusible link No. 6 to the power window motor.

This energizes the power window motor, causing the door window glass to open or close.

SERVICE SPECIFICATIONS 42300030076

I

Items Standard value

Door outside handle play mm (in.) 3.6 (.142) or more

Door inside handle play mm (in.) 5.3 (.209) or more

SEALANT 42300060034

k u

Item Specified sealant Remark

Waterproof film 3M ATD Part No. 8625 or equivalent Ribbon sealer

‘SPECIAL TOOLS 42300060066

7- Tool number and name

Supersession

Tool

MB991 502 Scan Tool (MUT-II)

MB991 496-OD

Tool not necessary if scan ETACS-ECU input signal check- tool cMUT-II> is available ing (when using a voltmeter)

MB991 529 Diagnostic trouble code check harness

General service tool 1 Removal of switch, trim, etc.

MB990784 Ornament remover

MB990900-01 Adjustment of door fit

MB990900 or MB991 164 Door adjusting wrench

00003936

- When the power window lock switch is placed in the LOCK (OFF) position, no switch other than the main switch at the driver’s side window can operate the power window motor.

- The power window motor has a circuit breaker that protects the motor from damage caused by excessive current.

Application

ETACS-ECU input signal check- ing

Tool Tool number and name

Supersession

MB991 223 Harness set A:

MB991219 Test harness B:

MB991 220 LED harness C:

MB991 221 LED harness adapter D:

MB991 222 Probe

MB991 223

TROUBLESHOOTING 42700200011

DIAGNOSTIC FUNCTION

INPUT SIGNAL INSPECTION POINTS <VEHICLES WITH ETACS-ECU> When Using the Scan Tool

Connect the scan tool to the data link connector.

1.

Caution The scan tool should be connected or disconnected after turning the ignition switch to the OFF position.

If buzzer of the scan tool sounds once when the each switch is operated (ON/OFF), the ETACS-ECU input signal for that switch circuit system is normal.

2.

Application

Measurement of terminal voltage A: Connector pin contact pres- sure inspection B, C: Power circuit inspection D: Commercial tester connection

When Using the Voltmeter

1.

Use the special tool to connect a voltmeter between the ground terminal and the ETACS terminal of the data link connector.

2.

If the voltmeter indicator deflects once when the each switch is operated (ON/OFF), the ETACS-ECU input signal for that switch circuit system is normal.

x

STANDARD FLOW OF DIAGNOSTIC TROUBLESHOOTING 42700210014

Does not I reoccur Gather information from customer.

1.1 Check trouble symptoms.

- intermittent malfunction.

1 Reoccurs

Refer to the INSPECTION CHART FOR TROUBLE SYMPTOMS.

.

INSPECTION CHART FOR TROUBLE SYMPTOMS 42700180018

Trouble symptom Inspection Reference I procedure page

None of the door lock functions operate.

1

The other door(s) does not lock or unlock by the door lock switch or the front 2 passenger’s side door lock key cylinder. (However, they can be operated by the driver’s inside door lock knob.)

The other door(s) does not lock or unlock by the driver’s inside door lock knob or 3 driver’s side door lock key cylinder.

Some doors do not lock or unlock.

4

INSPECTION PROCEDURE FOR TROUBLE SYMPTOMS

Inspection Procedure 1

1 None of the door lock functions operate.

/ Probable cause I

The cause may be a malfunction of the ETACS-ECU power supply circuit system 
- Malfunction of ETACS-ECU or of the ground circuit system.

- Malfunction of wiring harness or connector I

Voltage between 1 and body ground Voltage between 2 and body ground

-) Check the harnesswire between fusible lmk No.1 or No.2 and J/B, and repair

OK

NG * Repair

Check the following connectors:

B-64, B-65

OK

NG NG

- Check the harness wire between e Repair ETACS-ECU and ground.

Check trouble symptoms.

Replace the ETACS-ECU.

.

if necessary.

OK

Inspection Procedure 2

The other door(s) does not lock or unlock by the door lock Probable cause L switch or the front passenger’s side door lock cylinder.

(However, they can be operated by the driver’s inside door lock knob.)

The door lock switch, the door lock key cylinder switch (R.H.), the ETACS-ECU, 
- Malfunction of door lock switch harness or connector may be defecttve.

- Malfunction of door lock key cylinder switch (R.H.)

NG NG d Check the following connectors:

w Repair G-11, G-02, B-29, B-15, B-69

Measure at the door lock switch connec- tors G-11, G-02.

- Disconnect the connector and measure at the harness side.

<L.H.>

‘OK f Check trouble symptoms.

Check the harness wire between

- Voltage between 3 and body ground <2-door models>

- Voltage between 5 and body ground <4-door models>

- Voltage between 10 and ground <R.H.>

- Voltage between 1 and body ground

- Voltage between 3 and body ground OK: Battery positive voltage

IOK 1 Measure at the door lock key cylinder switch (R.H.) connector G-03.

- Disconnect the connector and

Voltage between 3 and body ground Voltage between 1 and body ground

/ _

OK

Door lock switch continuitycheck (Refer to P.42-40.) J”G~ Replace

~ NG Check the following connectors:

* Repair continuity check. (Refer to P.42-39.) <L.H.> B-29, G-11 +

NG <R.H.> B-15, G-02, G-03

Replace

Check the harness wires between door

Replace the ETACS-ECU.

- Malfunction of ETACS-ECU

- Malfunctron of wiring harness or connector

+I Check the harness wire between lock key cylinder switch (R.H.) and con- nector B-15 and repair if necessary.

Inspection Procedure 3

The other door(s) does not lock or unlock by the driver’s Probable cause inside door lock knob or driver’s side door lock key cylinder.

2”

The front door lock actuator (L.H.), the door lock key cylinder (L.H.), the ETACS-ECU, 
- Malfunction of front door lock actuator (L.H.) harness or connector may be defective.

- Malfunction of door lock key cylinder switch (L.H.)

1K

- Replace the ETACS-ECU.

1

Check the scan tool input signal.

(1) Front lock actuator switch (L.H.) input srgnal 0K:The scan tool buzzer sounds once when the front door lock actuator moves from the locked to the unlocked position, or from the unlocked to the locked position.

(2) Door lock key cylinder switch (L.H.) input signal 0K:The scan tool buzzer sounds once when the door lock key cylinder switch (L.H) is unlocked.

51) NG NG

- Check thefrontdoor w Replace

(Refer to P.42-38.)

OK NG / Check the followinq connectors:

1 * Repair

1 G-16, B-29, B-69

- I

IOK t Check trouble symptoms.

NG c Check the harness wares between the front lock actuator (L.H.) and ETACS-ECU, between front door lock actuator (L.H.) and ground and repair if necessary.

(4 NG

NG * Repair (L.H.). (Refer to P.42-39.) G-12, B-29, B-69 I _ + NG

Replace Check the harness wires between the door lock key cylinder switch (L.H.) and ETACS-ECU, between door lock key cylinder switch (L.H.) and ground, and

Inspection Procedure 4

Some doors do not lock or unlock.

Probable cause

The cause may be a malfunction of the door lock actuator or of a wiring harness 
- Malfunction of door lock actuator or connector.

- Malfunction of wiring harness or connector

NG Check the door lock actuator of the door that does not operate.

b Replace (Front: Refer to P.42-38.) (Rear: Refer to P.42.39.)

OK OK Check the following connectors:

<Front L.H.> G-16, B-29, B-69 <Front R.H.> G-07, B-15, B-69 <Rear L.H.> G-05, E-17, B-69 <Rear R.H.> G-14, E-03, B-69

- Check trouble symptoms.

i NG

Repair

- Malfunction of ETACS-ECU

- Malfunction of wiring harness or connector

NG

Check the harness between the ETACS-ECU and the door lock actuator of the door that does not operate, and repair if necessary.

TROUBLESHOOTING HINTS

Power windows

1. All door windows cannot be operated or closed.

- Check the fusible link No. 6.

- Check the multi-purpose fuse No. 6.

- Check the power window relay.

- Check the power window main switch.

2.

Some door window cannot be opened or closed.

1) Neither power window main nor sub switch is activated.

- Check power window main switch.

- Check defective power window motor.

2) Either power window main or sub switch is inoperative.

- Check inoperative power window switch.

GLASS AND DOORS

Symptom Probable cause 1 Remedy

Water leak through door window glass Incorrect window glass installation

/ Gap at upper window glass

Door window malfunction Incorrect window glass installation

Damaged or faulty regulator

Water leak through door edge Cracked or faulty weatherstrip Replace

Water leak from door center Drain hole clogged

Inadequate waterproof film contact or damage

Door hard to open Incorrect latch or striker adjustment Adjust

Door does not open or close completely Incorrect door installation

Defective door check strap

Door check strap and hinge require grease

Uneven gap between Incorrect door installation Adjust position

Wind noise around Weatherstrip not holding firmly Adjust fit of door

Improperly installed weatherstrip or setting of Repair or replace weatherstrip

Improperly closed door Adjust

Improperly fit door Adjust

Improper clearance between door glass and door Adjust weatherstrip holder

Deformed door Repair or replace

.

4

12300070108

Adjust position

Adjust position

Adjust position

Correct or replace

Remove foreign objects

Correct or replace

Adjust position

Correct or replace

Apply grease

-

HOW TO LOCATE WIND NOISES (1)

Attach cloth tape to every place, such as panel seams, projections, molding seams, glass and body seams, etc.

which might conceivably be the source of wind noise.

Then make a road test to check that the places not covered by tape are not sources of wind noise.

(2)

1610264 I

Remove the strips of tape one by one, making a road test after each is removed, until a wind noise source is discovered.

(3)

Remove A18M0264

When such a place is found, cover it again and repeat the procedure to check if there are any other noise source.

If no others -are found, the last remaining tape is the only source.

(4)

(5)

Ex. Noise produced A18M0265 here

Cut the remaining piece of tape into smaller pieces, attach it again as it was before, and then remove the pieces one by one to narrow down the source.

(6)

cut tape into A18,,,0266 pieces

Check that wind noise occurs when the last remaining tape is removed, and that noise does not occur when it is re-attached.

When the source(s) of the wind noise is finally located, attach butyl tape, body sealer or similar material to obstruct this source as much as possible.

(7)

(3)

.a 16M0267

.

ON-VEHICLE SERVICE A 42300090074

DOOR FIT ADJUSTMENT .

If the clearance between the door and the vehicle body is uneven, affix protective tape to the fender around the hinge and to the edge of the door. Then use the special tool to loosen the door hinge mounting bolts on the body, and adjust the clearance around the door so that it becomes even.

If the door and the body are not flush with each other, use the special tool to loosen the door hinge mounting bolts. Then align the door.

Caution Do not apply more than 98 Nm (72 ft.lbs.) to the special tool (MB991164).

If the door opening and closing is heavy, adjust the meshing of the striker and the door latch (in the longitudinal direction) by adding shims to the striker and by moving the striker up and down or to the left and right.

DOOR WINDOW GLASS ADJUSTMENT 42300100128

Check that the door glass moves securely along the door glass runchannel when the window glass is fully raised and fully lowered. If the glass does not move correctly, adjust bY 1.

the following procedure.

Remove the door trim and the waterproof film. (Refer to P.42-32.) Loosen the mounting screw through the adjusting hole with the door window glass fully closed, and lower the door window glass slightly.

Close the door window glass fully again, and tighten the door glass mounting screw securely through the adjusting , hole.

2.

3.

P

DOOR OUTSIDE HANDLE PLAY CHECK 42300160089

1.

Check that the door outside handle play is within the standard value range.

Standard value (B): 3.6 mm (.142 in.) or more

2.

If the door outside handle play is not within the standard value range, check the door outside handle or the door latch assembly.

Replace, if necessary.

18MOOOa 00004523

CIRCUIT BREAKER (INCORPORATED IN THE POWER WINDOW MOTOR) INSPECTION 429oo17oo

1. Press the power window switch to the UP position to fully close the window glass, and keep pressing the switch for a further 10 seconds.

2.

Release the power window switch from the UP position and immediately press it to the DOWN position.

The condition of the circuit breaker is good if the power window glass starts to move downward within 60 seconds.

DOOR INSIDE HANDLE PLAY CHECK AND ADJUSTMENT I 42300160123

Check that the door inside handle play is within the standard value range.

Standard value (A): 5.3 mm (.209 in.) or more

If the door inside handle play is outside the standard value range, remove the door trim. (Refer to P.42-32.) Loosen the inside handle mounting screws, and then move the inside handle back and forth to adjust the play.

00004524

DOOR ASSEMBLY _ Il

42300220152 REMOVAL AND INSTALLATION .

I I

Post-installation Operation 0 Door Fit Adjustment (Refer to P.42-28.)

I I

Front door

26 20

22 Nm 16 ft.lbs.

Rear door

22 Nm l6 Mbs- 26 Nm 20 l-t.lbs.

22 Nm

16 ft.lbs.

Door assembly removal steps

1. Harness connector

2. Spring pin

3. Door assembly .A4

4. Door upper hinge .A+

5. Door lower hinge

18AOl29

18M0003 00004530

Striker removal steps

6. Striker

7. Striker shim

Door switch removal steps

8. Door switch cap

9. Door switch

INSTALLATION SERVICE POINT

Front Rear

bAdDOOR LOWER HINGE/DOOR UPPER HINGE INSTALLATION

The door hinges differ according to where they are used, so check the identification marks before installation.

Applicable location Identification mark 1

Identifihation mark Identification mark

Front lefl side door

AlEM

Front right side door

Rear left side door

Rear right side door

INSPECTION

DOOR SWITCH CONTINUITY CHECK

Front door switch (L.H.)

Switch Terminal No.

position 1 12 13

Open (ON) 1 0 I A I 0

N

Stroke AlEN

Depressed (OFF) / /

Front door switch (R.H.) and rear door switch

Switch Terminal No.

position t 1 I2

Open (ON)

Depressed (OFF)

Stroke

WA0159

.

Upper hinge Fl

Lower hinge El

Uppeknge El

Lower hinge Fl

Upper hinge Al

Lower hinge _ Kl

Upper hinge Bl

Lower hinge Ll

42300600062

DOOR TRIM AND WATERPROOF FILM _)

REMflVAL AND INSTALLATION _ _I .- I I.__ .I__

-_ .---

--

----

Front door

Sealant:

3M ATD Part. No. 8625 or equivalent

Removal steps

+A, .A4

1. Clio <Vehicles without power win- do&.> Regulator handle <Vehicles without power windows> Escutcheon <Vehicles without pow- er windows> Pull handle box <Vehicles without power windows Power window switch panel <Vehicles with power windows>

.A4 2

.Al 3

4

5

42300430135

8 <2-door models>

18M0252

00004817

NOTE + : Resin clip position

I

6. Power window switch <Vehicles with power windows>

7. Cover

8. Door trim

- 11, Door inside handle

12. Pull handle bracket

13. Waterproof film

BbDY

- Door

Rear door

dOTE * : Resin clip position

Removal steps 4A, .A4 1.

Clip <Vehicles without power win- dows> Regulator handle <Vehicles without power windows> Escutcheon <Vehicles without pow- er windows> Pull handle box Cover

.A4 2

.Al 3

4 7

REMOVAL SERVICE POINT

+A, CLIP REMOVAL

Remove the clip by using a shop towel, and then remove the regulator handle.

18UO430

18UO392 00000124

INSTALLATION SERVICE POINT

,A+ ESCUTCHEON/REGULATOR HANDLE/CLIP

B HoriT line

INSTALLATION

1.

2.

Install the escutcheon and the clip to the regulator handle.

Fully close the front door glass, and install the regulator handle so that it faces as shown in the illustration.

w

C Front of vehicle AlSSO120

.

Sealant:

3M ATD Part. No. 8625 or equivalent

L

18M0023 00004531

8. Door trim

9. Power window switch <Vehicles with power windows>

10. Power window switch panel <Vehicles with power windows>

11. Door inside handle

12. Pull handle bracket

13. Waterproof film

DOOR GLASS AND REGULATOR

REMOVAL AND INSTALLATION s

I I I Pre-removal Operation II) Door Trim and Waterproof Film Removal (Refer ’ ’ to P.42-32.) (2) Door Beltline Inner Weatherstrip Removal (Refer to P.42-41 .)

Front door

<Vehicles with power windows> <Vehicles without .

power windows> +

<Vehicles without 4 power windows> <Vehicles with power windows>

10MQ227

Front window regulator assembly removal steps

1. Door window glass

2. Door window glass holder

3. Window regulator assembly

4. Power window motor

Rear window regulator assembly removal steps

- Window glass runchannel (Refer to P.42-41.)

1. Door window glass

2. Door window glass holder

3. Window regulator assembly

4. Power window motor

I I Post-installation Operation (1) Door Window Glass Adjustment (Refer to P.42-28.) (2) Door Beltline Inner Weatherstrip Installation (Refer to P.42-41 .j (3) Door Trim And Waterproof Film Installation (Refer to P.42-32 .)

Rear door

18MQ228 00004721 ‘c‘

Stationary window glass removal steps

- Window glass runchannel (Refer to P.42-41.)

1. Door window glass

5. Door center sash

6. Stationary window alass and weatherstrip assembly

7. Stationary window glass

8. Stationary window weatherstrip

REMOVAL SERVICE POINT

+A,DOOR CENTER SASH REMOVAL

1.

Remove the door outer opening weatherstrip from the door center sash only.

2.

Remove the door center sash mounting screws, and then remove the door center sash from the door panel.

INSPECTION 42900180052

POWER WINDOW RELAY CONTINUITY CHECK

00004818

POWER WINDOW MOTOR CHECK 42900150053

1.

Connect a battery directly to the motor terminals and check that the motor runs smoothly.

2.

Check that the motor runs in the opposite direction when the batterv is connected with the polarity reversed.

POWER WINDOW SWITCH CONTINUITY CHECK

2-door models

4-door models

16M0263

Main switch

Terminal No.

Power window switch (normal) Power window switch (lock)

UP OFF DOWN UP OFF DOWN

Front (L.H.) 6*‘, 13*2 0 I*i 8*2 0 1

5"l g*2 Y 0 0 I I

9*', 12*2 0

Front (R.H.) 6*‘, 13*2 0 0

7*1 3*2 0

8*‘, 11*2 0 0

9*', 12*2 0

Rear 13 (L.H.)*2 .

0

, 0

2 0 0

12 0

Rear 13 (FW*2 0 0

,4 .

0

6 0 0

12 0

NOTE *I: 2-door *2: 4-door models models

Sub switch

I I I Sub 14 I 0 ~ 0 switch 5

16M0262

DOOR HANDLE AND LATCH 42300460134

REMOVAL AND INSTALLATION

- Door Trim Removal (Refer to P.42-32.) ‘.^I”“““““‘.“‘..

(1) Door Inside Handle Play Check (Refer to P42-29.) (2) Door Outside Handle Play Check (Refer to P.42-29.) (3) Door Trim Installation (Refer to P.42-32.)

Pre-removal Operation

Front door Rear door

4 18M0019 ’

- 18M0020 00004533

Front door handle and door latch assembly removal steps Door check removal steps

1. Door inside handle

1. Door inside handle

- Waterproof film (Refer to P.42-32.)

2. Door outside handle

3. Door lock key cylinder

4. Rear lower sash

5. Door latch assembly

Rear door handle and door latch assembly removal steps

1. Door inside handle

- Waterproof film (Refer to P.42-32.)

- Door center sash (Refer to P.42-34.)

5. Door latch assembly

6. Door lock actuator

7. Door outside handle

.

6

7

8

- Waterproof film (Refer to P-42-32.)

8. Spring pin .A+

9. Door check

_

1

3 A

r

INSTALLATION SERVICE POINT 1

.A+ CHECK INSTALLATION

Install the door check so that the identification mark faces upward.

v

Applicable location Identification mark

\ Identification mark

L.H.

Front door YL XL

A16E0052

R.H.

Front door YR XR

INSPECTION 42300610072

cL.H.>

FRONT LOCK ACTUATOR CHECK

<L.H.>

View A

Lock -

16MOOl 6

<R.H.>

View 6 Unlock

<R.H.>

Rod position Terminal No.

Rod operation

LOCK

- 0 LOCK position - UNLOCK position

UNLOCK Q

- UNLOCK position - LOCK position

2-door models 4-door models

Rear door

- 16L

Rear door

- 16R

UNLOCK position

4 6

REAR LOCK ACTUATOR CHECK 42300520051

<L.H.>

cL.H.>

Rod position / Terminal No.

Rod operation

LOCK Q

- LOCK position - UNLOCK position

UNLOCK

- @ UNLOCK position - LOCK position

<R.H.>

cR.H.>

Rod position Terminal No.

Rod operation

View B

LOCK

- + LOCK position - UNLOCK position

UNLOCK a---Q _ UNLOCK position - LOCK position

L.

B

18M0014 00004526

LOCK KEY CYLINDER SWITCH CONTINUITY CHECK I 42300630085

Switch position L.H.

R.H.

LOCK 0 0 0 0

Neutral (OFF)

10so444

UNLOCK 0 0 0 0

L.H.: Unlock

.

2 3

2 3

Terminal No.

1 2 3 1 2 3

LOCK SWITCH CONTINUITY CHECK 42700120066

<L.H.>

<

NOTE *l: 2-door models *2: 4-door models

2-door models

cR.H.>

Door lock switch Terminal No.

Switch position 1 2 3

LOCK 0 0

OFF

UNLOCK .

0 0

A16M0262 I I h

WINDOW GLASS RUNCHANNEL AND DOOR OPENING WEATHERSTRIP 42300310110

REMOVAL AND INSTALLATION

Front door Rear door

Door inner opening weatherstrip removal steps

- Cowl side trim (Refer to GROUP 52A.)

- Quarter trim <2-door models> (Refer to GROUP 52A.)

- Center pillar lower trim <4-door models> (Refer to GROUP 52A.)

1. Door inner opening weatherstrip

Door outer opening weatherstrip removal

4A, .A4

2. Door outer opening weatherstrip

REMOVAL SERVICE POINT

+A, OUTER OPENING WEATHERSTRIP REMOVAL

Make a tool as shown in the illustration to remove the door opening weatherstrip.

* TSB Revision

.

Door window glass runchannel removal

3. Door window glass runchannel

Door beltline inner weatherstrip removal steps

- Door trim (Refer to P.42-32.)

4. Door beltline inner weatherstrip

Door beltline molding removal

- Door mirror (Refer to GROUP 51.)

5. Door beltline molding
