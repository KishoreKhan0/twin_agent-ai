# Sensor Specification Sheet

## Temperature Sensor

The temperature sensor measures motor housing temperature in degrees Celsius.
Normal production values are usually between 40 °C and 75 °C. Values above 82 °C
should be treated as a warning condition.

## Vibration Sensor

The vibration sensor measures vibration velocity in mm/s. Stable operation is
usually between 0.1 mm/s and 0.8 mm/s. Sustained values above 1.4 mm/s indicate
a warning condition.

## Current Sensor

The current sensor measures motor current in amperes. Normal production values
are usually between 5 A and 12 A. Values above 14 A indicate elevated motor load.

## RPM Sensor

The RPM sensor measures motor rotational speed. Normal production values are
usually between 1200 and 1800 RPM. Values outside this band should be compared
against load and belt-speed commands.

## Throughput Sensor

The throughput sensor estimates units per minute. A throughput drop can indicate
belt misalignment, material blockage, belt-speed issues, or upstream/downstream
line constraints.
