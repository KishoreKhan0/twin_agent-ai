# TwinAgent AI Fleet Demo Summary

## Fleet overview

- Machines: 12
- Sensor rows: 43200
- Incidents: 80
- Time range: `2026-05-20T14:00:00` to `2026-05-21T03:49:59`
- Long incident segmentation: {'enabled': True, 'long_incident_threshold_seconds': 420, 'target_segment_seconds': 300, 'max_segments_per_incident': 6}

## Machine summary

| Machine | Line | Rows | Incidents | Latest health | Min health | Latest risk | Suspected faults |
|---|---:|---:|---:|---:|---:|---|---|
| line1_motor1 | line1 | 3600 | 4 | 100 | 27 | healthy | bearing_wear |
| line1_motor2 | line1 | 3600 | 7 | 100 | 25 | healthy | bearing_wear, current_anomaly |
| line2_motor1 | line2 | 3600 | 3 | 100 | 31 | healthy | bearing_wear |
| line2_motor2 | line2 | 3600 | 7 | 100 | 25 | healthy | bearing_wear, current_anomaly |
| line3_motor1 | line3 | 3600 | 5 | 100 | 25 | healthy | bearing_wear |
| line3_motor2 | line3 | 3600 | 8 | 99 | 25 | healthy | bearing_wear, current_anomaly |
| line4_motor1 | line4 | 3600 | 7 | 100 | 25 | healthy | bearing_wear, current_anomaly |
| line4_motor2 | line4 | 3600 | 8 | 99 | 25 | healthy | bearing_wear, current_anomaly |
| line5_motor1 | line5 | 3600 | 5 | 100 | 25 | healthy | bearing_wear |
| line5_motor2 | line5 | 3600 | 8 | 98 | 25 | healthy | bearing_wear, current_anomaly |
| line6_motor1 | line6 | 3600 | 8 | 100 | 25 | healthy | bearing_wear, current_anomaly |
| line6_motor2 | line6 | 3600 | 10 | 97 | 25 | healthy | bearing_wear, current_anomaly |

## Incidents

- `FLEET-M01-0001-S01` | `line1_motor1` | high | bearing_wear | `2026-05-20T14:37:22` → `2026-05-20T14:42:16` | episode 1/4
- `FLEET-M01-0001-S02` | `line1_motor1` | high | bearing_wear | `2026-05-20T14:42:16` → `2026-05-20T14:47:10` | episode 2/4
- `FLEET-M01-0001-S03` | `line1_motor1` | high | bearing_wear | `2026-05-20T14:47:10` → `2026-05-20T14:52:05` | episode 3/4
- `FLEET-M01-0001-S04` | `line1_motor1` | high | bearing_wear | `2026-05-20T14:52:05` → `2026-05-20T14:56:59` | episode 4/4
- `FLEET-M02-0001` | `line1_motor2` | low | current_anomaly | `2026-05-20T15:14:32` → `2026-05-20T15:14:58`
- `FLEET-M02-0002` | `line1_motor2` | low | current_anomaly | `2026-05-20T15:26:39` → `2026-05-20T15:27:22`
- `FLEET-M02-0003-S01` | `line1_motor2` | high | bearing_wear | `2026-05-20T15:42:44` → `2026-05-20T15:47:35` | episode 1/5
- `FLEET-M02-0003-S02` | `line1_motor2` | high | bearing_wear | `2026-05-20T15:47:35` → `2026-05-20T15:52:26` | episode 2/5
- `FLEET-M02-0003-S03` | `line1_motor2` | high | bearing_wear | `2026-05-20T15:52:26` → `2026-05-20T15:57:17` | episode 3/5
- `FLEET-M02-0003-S04` | `line1_motor2` | high | bearing_wear | `2026-05-20T15:57:17` → `2026-05-20T16:02:08` | episode 4/5
- `FLEET-M02-0003-S05` | `line1_motor2` | high | bearing_wear | `2026-05-20T16:02:08` → `2026-05-20T16:06:59` | episode 5/5
- `FLEET-M03-0001-S01` | `line2_motor1` | high | bearing_wear | `2026-05-20T16:59:23` → `2026-05-20T17:04:11` | episode 1/2
- `FLEET-M03-0001-S02` | `line2_motor1` | high | bearing_wear | `2026-05-20T17:04:11` → `2026-05-20T17:08:59` | episode 2/2
- `FLEET-M03-0002` | `line2_motor1` | medium | bearing_wear | `2026-05-20T17:11:50` → `2026-05-20T17:16:59`
- `FLEET-M04-0001` | `line2_motor2` | medium | current_anomaly | `2026-05-20T17:33:22` → `2026-05-20T17:35:41`
- `FLEET-M04-0002` | `line2_motor2` | low | current_anomaly | `2026-05-20T17:46:39` → `2026-05-20T17:50:59`
- `FLEET-M04-0003-S01` | `line2_motor2` | high | bearing_wear | `2026-05-20T18:02:07` → `2026-05-20T18:07:05` | episode 1/5
- `FLEET-M04-0003-S02` | `line2_motor2` | high | bearing_wear | `2026-05-20T18:07:05` → `2026-05-20T18:12:04` | episode 2/5
- `FLEET-M04-0003-S03` | `line2_motor2` | high | bearing_wear | `2026-05-20T18:12:04` → `2026-05-20T18:17:02` | episode 3/5
- `FLEET-M04-0003-S04` | `line2_motor2` | high | bearing_wear | `2026-05-20T18:17:02` → `2026-05-20T18:22:01` | episode 4/5
- `FLEET-M04-0003-S05` | `line2_motor2` | high | bearing_wear | `2026-05-20T18:22:01` → `2026-05-20T18:26:59` | episode 5/5
- `FLEET-M05-0001-S01` | `line3_motor1` | high | bearing_wear | `2026-05-20T19:16:17` → `2026-05-20T19:20:25` | episode 1/5
- `FLEET-M05-0001-S02` | `line3_motor1` | high | bearing_wear | `2026-05-20T19:20:25` → `2026-05-20T19:24:34` | episode 2/5
- `FLEET-M05-0001-S03` | `line3_motor1` | high | bearing_wear | `2026-05-20T19:24:34` → `2026-05-20T19:28:42` | episode 3/5
- `FLEET-M05-0001-S04` | `line3_motor1` | high | bearing_wear | `2026-05-20T19:28:42` → `2026-05-20T19:32:51` | episode 4/5
- `FLEET-M05-0001-S05` | `line3_motor1` | high | bearing_wear | `2026-05-20T19:32:51` → `2026-05-20T19:36:59` | episode 5/5
- `FLEET-M06-0001` | `line3_motor2` | medium | current_anomaly | `2026-05-20T19:50:31` → `2026-05-20T19:55:56`
- `FLEET-M06-0002` | `line3_motor2` | medium | current_anomaly | `2026-05-20T20:06:12` → `2026-05-20T20:11:24`
- `FLEET-M06-0003-S01` | `line3_motor2` | high | bearing_wear | `2026-05-20T20:21:59` → `2026-05-20T20:26:09` | episode 1/6
- `FLEET-M06-0003-S02` | `line3_motor2` | high | bearing_wear | `2026-05-20T20:26:09` → `2026-05-20T20:30:19` | episode 2/6
- `FLEET-M06-0003-S03` | `line3_motor2` | high | bearing_wear | `2026-05-20T20:30:19` → `2026-05-20T20:34:29` | episode 3/6
- `FLEET-M06-0003-S04` | `line3_motor2` | high | bearing_wear | `2026-05-20T20:34:29` → `2026-05-20T20:38:39` | episode 4/6
- `FLEET-M06-0003-S05` | `line3_motor2` | high | bearing_wear | `2026-05-20T20:38:39` → `2026-05-20T20:42:49` | episode 5/6
- `FLEET-M06-0003-S06` | `line3_motor2` | high | bearing_wear | `2026-05-20T20:42:49` → `2026-05-20T20:46:59` | episode 6/6
- `FLEET-M07-0001` | `line4_motor1` | low | current_anomaly | `2026-05-20T21:04:32` → `2026-05-20T21:04:55`
- `FLEET-M07-0002` | `line4_motor1` | low | current_anomaly | `2026-05-20T21:33:05` → `2026-05-20T21:33:33`
- `FLEET-M07-0003-S01` | `line4_motor1` | high | bearing_wear | `2026-05-20T21:35:51` → `2026-05-20T21:40:05` | episode 1/5
- `FLEET-M07-0003-S02` | `line4_motor1` | high | bearing_wear | `2026-05-20T21:40:05` → `2026-05-20T21:44:18` | episode 2/5
- `FLEET-M07-0003-S03` | `line4_motor1` | high | bearing_wear | `2026-05-20T21:44:18` → `2026-05-20T21:48:32` | episode 3/5
- `FLEET-M07-0003-S04` | `line4_motor1` | high | bearing_wear | `2026-05-20T21:48:32` → `2026-05-20T21:52:45` | episode 4/5
- `FLEET-M07-0003-S05` | `line4_motor1` | high | bearing_wear | `2026-05-20T21:52:45` → `2026-05-20T21:56:59` | episode 5/5
- `FLEET-M08-0001` | `line4_motor2` | medium | current_anomaly | `2026-05-20T22:10:22` → `2026-05-20T22:16:04`
- `FLEET-M08-0002` | `line4_motor2` | medium | current_anomaly | `2026-05-20T22:25:51` → `2026-05-20T22:31:41`
- `FLEET-M08-0003-S01` | `line4_motor2` | high | bearing_wear | `2026-05-20T22:41:05` → `2026-05-20T22:45:24` | episode 1/6
- `FLEET-M08-0003-S02` | `line4_motor2` | high | bearing_wear | `2026-05-20T22:45:24` → `2026-05-20T22:49:43` | episode 2/6
- `FLEET-M08-0003-S03` | `line4_motor2` | high | bearing_wear | `2026-05-20T22:49:43` → `2026-05-20T22:54:02` | episode 3/6
- `FLEET-M08-0003-S04` | `line4_motor2` | high | bearing_wear | `2026-05-20T22:54:02` → `2026-05-20T22:58:21` | episode 4/6
- `FLEET-M08-0003-S05` | `line4_motor2` | high | bearing_wear | `2026-05-20T22:58:21` → `2026-05-20T23:02:40` | episode 5/6
- `FLEET-M08-0003-S06` | `line4_motor2` | high | bearing_wear | `2026-05-20T23:02:40` → `2026-05-20T23:06:59` | episode 6/6
- `FLEET-M09-0001-S01` | `line5_motor1` | high | bearing_wear | `2026-05-20T23:56:04` → `2026-05-21T00:00:15` | episode 1/5
- `FLEET-M09-0001-S02` | `line5_motor1` | high | bearing_wear | `2026-05-21T00:00:15` → `2026-05-21T00:04:26` | episode 2/5
- `FLEET-M09-0001-S03` | `line5_motor1` | high | bearing_wear | `2026-05-21T00:04:26` → `2026-05-21T00:08:37` | episode 3/5
- `FLEET-M09-0001-S04` | `line5_motor1` | high | bearing_wear | `2026-05-21T00:08:37` → `2026-05-21T00:12:48` | episode 4/5
- `FLEET-M09-0001-S05` | `line5_motor1` | high | bearing_wear | `2026-05-21T00:12:48` → `2026-05-21T00:16:59` | episode 5/5
- `FLEET-M10-0001` | `line5_motor2` | medium | bearing_wear | `2026-05-21T00:30:22` → `2026-05-21T00:37:08`
- `FLEET-M10-0002` | `line5_motor2` | medium | current_anomaly | `2026-05-21T00:45:25` → `2026-05-21T00:52:02`
- `FLEET-M10-0003-S01` | `line5_motor2` | high | bearing_wear | `2026-05-21T01:00:33` → `2026-05-21T01:04:57` | episode 1/6
- `FLEET-M10-0003-S02` | `line5_motor2` | high | bearing_wear | `2026-05-21T01:04:57` → `2026-05-21T01:09:22` | episode 2/6
- `FLEET-M10-0003-S03` | `line5_motor2` | high | bearing_wear | `2026-05-21T01:09:22` → `2026-05-21T01:13:46` | episode 3/6
- `FLEET-M10-0003-S04` | `line5_motor2` | high | bearing_wear | `2026-05-21T01:13:46` → `2026-05-21T01:18:10` | episode 4/6
- `FLEET-M10-0003-S05` | `line5_motor2` | high | bearing_wear | `2026-05-21T01:18:10` → `2026-05-21T01:22:35` | episode 5/6
- `FLEET-M10-0003-S06` | `line5_motor2` | high | bearing_wear | `2026-05-21T01:22:35` → `2026-05-21T01:26:59` | episode 6/6
- `FLEET-M11-0001` | `line6_motor1` | medium | current_anomaly | `2026-05-21T01:44:11` → `2026-05-21T01:45:41`
- `FLEET-M11-0002` | `line6_motor1` | low | current_anomaly | `2026-05-21T01:56:39` → `2026-05-21T01:58:05`
- `FLEET-M11-0003` | `line6_motor1` | low | current_anomaly | `2026-05-21T02:00:17` → `2026-05-21T02:00:40`
- `FLEET-M11-0004-S01` | `line6_motor1` | high | bearing_wear | `2026-05-21T02:12:07` → `2026-05-21T02:17:05` | episode 1/5
- `FLEET-M11-0004-S02` | `line6_motor1` | high | bearing_wear | `2026-05-21T02:17:05` → `2026-05-21T02:22:04` | episode 2/5
- `FLEET-M11-0004-S03` | `line6_motor1` | high | bearing_wear | `2026-05-21T02:22:04` → `2026-05-21T02:27:02` | episode 3/5
- `FLEET-M11-0004-S04` | `line6_motor1` | high | bearing_wear | `2026-05-21T02:27:02` → `2026-05-21T02:32:01` | episode 4/5
- `FLEET-M11-0004-S05` | `line6_motor1` | high | bearing_wear | `2026-05-21T02:32:01` → `2026-05-21T02:36:59` | episode 5/5
- `FLEET-M12-0001-S01` | `line6_motor2` | medium | bearing_wear | `2026-05-21T02:50:05` → `2026-05-21T02:54:41` | episode 1/2
- `FLEET-M12-0001-S02` | `line6_motor2` | medium | bearing_wear | `2026-05-21T02:54:41` → `2026-05-21T02:59:18` | episode 2/2
- `FLEET-M12-0002-S01` | `line6_motor2` | medium | current_anomaly | `2026-05-21T03:05:25` → `2026-05-21T03:08:55` | episode 1/2
- `FLEET-M12-0002-S02` | `line6_motor2` | medium | current_anomaly | `2026-05-21T03:08:55` → `2026-05-21T03:12:26` | episode 2/2
- `FLEET-M12-0003-S01` | `line6_motor2` | high | bearing_wear | `2026-05-21T03:18:41` → `2026-05-21T03:23:24` | episode 1/6
- `FLEET-M12-0003-S02` | `line6_motor2` | high | bearing_wear | `2026-05-21T03:23:24` → `2026-05-21T03:28:07` | episode 2/6
- `FLEET-M12-0003-S03` | `line6_motor2` | high | bearing_wear | `2026-05-21T03:28:07` → `2026-05-21T03:32:50` | episode 3/6
- `FLEET-M12-0003-S04` | `line6_motor2` | high | bearing_wear | `2026-05-21T03:32:50` → `2026-05-21T03:37:33` | episode 4/6
- `FLEET-M12-0003-S05` | `line6_motor2` | high | bearing_wear | `2026-05-21T03:37:33` → `2026-05-21T03:42:16` | episode 5/6
- `FLEET-M12-0003-S06` | `line6_motor2` | high | bearing_wear | `2026-05-21T03:42:16` → `2026-05-21T03:46:59` | episode 6/6
