# Bekeart — AGV Project

Hardware design summary for a four-wheel differential-drive AGV.

## 1. Weight and chassis

| Parameter | Value |
| --- | --- |
| Expected total AGV weight | 90 kg |
| Additional design allowance | 7–8 kg |
| Preliminary design mass | 97–98 kg |
| Chassis weight | 25 kg |
| Wheel diameter | 152 mm |

## 2. Motors

Four motors planned — **Orange PG56/63ZY125-2440-65K**.

| Parameter | Value |
| --- | --- |
| Voltage | 24 V DC |
| Rated speed | 49 RPM |
| Rated torque | 21 Nm per motor |
| Rated current | 9 A per motor |
| Total rated current | 36 A for four motors |

All four motors use independent motor drivers. Motors should preferably have
factory-fitted encoders for speed feedback to the STM32.

## 3. Motor drivers

Planned: **4 × SmartElex 30S**.

| Parameter | Value |
| --- | --- |
| Continuous current rating | 30 A |
| Peak rating | 85 A (subject to specified duration) |
| Max operating voltage | 28 V |

> **Open blocker.** The battery bank reaches **29.2 V** when fully charged, so the
> SmartElex 30S cannot be connected directly to it. We need either compatible
> higher-voltage drivers or an engineered regulated motor supply. Deferred for now.

## 4. Battery configuration

Eight **Pro-Range LiFePO4** batteries — 12.8 V, 30 Ah each.

Connection: **2S4P** (two in series per string, four strings in parallel).

| Parameter | Result |
| --- | --- |
| Nominal voltage | 25.6 V |
| Capacity | 120 Ah |
| Total energy | 3,072 Wh |
| Fully charged voltage | 29.2 V |
| Estimated battery weight | 25.6 kg |

The manufacturer must confirm that the individual battery BMS units support this
connection. A purpose-built 25.6 V, 120 Ah battery is preferable.

## 5. Battery backup

Target runtime: **6–8 hours**.

Estimated backup at 80% usable battery energy:

| Average power consumption | Backup |
| --- | --- |
| 300 W | 8.2 hours |
| 350 W | 7 hours |
| 400 W | 6.1 hours |
| 500 W | 4.9 hours |

Actual backup depends on motor load, movement, stopping, turning and Jetson usage.

## 6. Jetson Orin Nano

**NVIDIA Jetson Orin Nano 8 GB** for AI and camera processing.

- Power supply: regulated 12 V DC
- Supply capacity: 5 A (as tested)
- A DC-DC buck converter reduces the main battery voltage to 12 V
- No separate battery required

## 7. Encoder feedback

All four motors should preferably have incremental A/B magnetic encoders. The
STM32 uses encoder feedback to:

- Measure actual motor speed
- Synchronize all four motors
- Correct differences between wheel speeds
- Improve straight-line movement and turning

## Assets

- `VID-20261024-WA0018.mp4` — AGV build/footage (4.7 MB)
- `VID-20261027-WA0025.mp4` — AGV build/footage (2.6 MB)

These two clips are published on the portfolio as `public/videos/bekaert-agv-01.mp4`
and `public/videos/bekaert-agv-02.mp4`, so the copies in this folder are the
source of record and are git-ignored to avoid storing the footage twice.

Dashboard screenshots of the platform live in
`public/images/projects/screens/bekaert-agv*.webp`.
