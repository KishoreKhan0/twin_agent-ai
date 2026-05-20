# Simulation

The simulation module creates synthetic industrial sensor data for a conveyor-motor digital twin.

---

## Simulated machine

The MVP simulates:

```text
Factory Line 1 — Conveyor Motor 1
machine_id = line1_motor1
```

The system represents:

- electric motor
- conveyor belt
- bearing assembly
- pulley system
- load variation
- cooling behavior
- throughput behavior

---

## Configuration

The simulator is configured in:

```text
configs/machine_config.yaml
```

The config controls:

- machine ID
- sampling rate
- duration
- random seed
- start time
- sensor normal ranges
- noise levels
- fault start times
- fault durations
- fault severities

---

## Sensor channels

The generated dataset includes:

```text
timestamp
machine_id
temperature_c
vibration_mm_s
rpm
current_a
load_pct
belt_speed_mps
throughput_units_min
ambient_temperature_c
operating_mode
machine_state
fault_label
fault_severity
```

---

## Normal operation

Normal operation includes:

- smooth load variation
- RPM affected by load
- belt speed correlated with RPM
- current correlated with load
- temperature correlated with load and ambient temperature
- throughput correlated with belt speed and load
- random sensor noise

The simulator is deterministic for a fixed random seed.

---

## Fault injection

The simulator supports these fault profiles:

### Bearing wear

Expected pattern:

```text
vibration increases gradually
temperature rises
current increases slightly
rpm can become less stable
```

### Overheating

Expected pattern:

```text
temperature increases strongly
current may rise slightly
cooling-related warning behavior appears
```

### Belt misalignment

Expected pattern:

```text
vibration increases
throughput drops
belt speed becomes unstable
current can increase slightly
```

### Motor overload

Expected pattern:

```text
current rises
temperature rises
rpm may drop
```

### Sensor drift

Expected pattern:

```text
one sensor slowly drifts away from baseline
other sensors remain comparatively stable
```

### Cooling failure

Expected pattern:

```text
temperature rises steadily
current and vibration may remain less affected
```

---

## Default demo

The default configuration generates 60 minutes of data at 1 Hz:

```text
3600 rows
2026-05-20T14:00:00 → 2026-05-20T14:59:59
```

Default fault labels include:

```text
normal
bearing_wear
overheating
belt_misalignment
bearing_wear+overheating
overheating+belt_misalignment
```

---

## Run command

```cmd
python scripts\generate_synthetic_data.py
```

Expected output:

```text
data/generated/sensor_data.csv
```

---

## Technical honesty

The simulator is designed for portfolio-grade experimentation and evaluation. It creates plausible industrial time-series patterns but does not claim to reproduce the full physics of a real conveyor system.
