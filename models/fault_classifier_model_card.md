# TwinAgent AI Fault Classifier Model Card

## Purpose

This model predicts the dominant fault type from rolling windows of simulated industrial sensor data.

## Training summary

- Windows: 359
- Train windows: 269
- Test windows: 90
- Feature count: 70
- Classes: 7
- Accuracy: 0.9333
- Macro F1: 0.7888
- Weighted F1: 0.9332

## Weak classes to monitor

- `cooling_failure` — F1 `0.2857`, support `3`
- `motor_overload` — F1 `1.0`, support `4`
- `overheating` — F1 `0.4444`, support `5`
- `sensor_drift` — F1 `0.8`, support `3`

## Top feature importances

| Rank | Feature | Sensor | Statistic | Importance |
|---:|---|---|---|---:|
| 1 | health_score_mean | health_score | mean | 0.05415386 |
| 2 | rpm_range | rpm | range | 0.0411498 |
| 3 | vibration_mm_s_max | vibration_mm_s | max | 0.03999769 |
| 4 | vibration_mm_s_mean | vibration_mm_s | mean | 0.03778506 |
| 5 | vibration_mm_s_last | vibration_mm_s | last | 0.03561667 |
| 6 | health_score_last | health_score | last | 0.03554304 |
| 7 | temperature_c_last | temperature_c | last | 0.03433853 |
| 8 | belt_speed_mps_min | belt_speed_mps | min | 0.0337081 |
| 9 | rpm_min | rpm | min | 0.03135081 |
| 10 | rpm_mean | rpm | mean | 0.03044219 |
| 11 | rpm_max | rpm | max | 0.02837301 |
| 12 | rpm_std | rpm | std | 0.02681641 |
| 13 | temperature_c_max | temperature_c | max | 0.02665091 |
| 14 | current_a_max | current_a | max | 0.02600373 |
| 15 | health_score_max | health_score | max | 0.02438872 |
| 16 | belt_speed_mps_mean | belt_speed_mps | mean | 0.02270849 |
| 17 | ambient_temperature_c_max | ambient_temperature_c | max | 0.02224541 |
| 18 | temperature_c_mean | temperature_c | mean | 0.02207276 |
| 19 | rpm_last | rpm | last | 0.02084829 |
| 20 | ambient_temperature_c_mean | ambient_temperature_c | mean | 0.01967124 |
| 21 | temperature_c_min | temperature_c | min | 0.01934782 |
| 22 | health_score_min | health_score | min | 0.01828051 |
| 23 | current_a_mean | current_a | mean | 0.01806009 |
| 24 | ambient_temperature_c_last | ambient_temperature_c | last | 0.01679438 |
| 25 | ambient_temperature_c_min | ambient_temperature_c | min | 0.01678104 |

## Prediction audit summary

- Prediction windows: 359
- Low-confidence threshold: 0.6
- Low-confidence windows: 10
- Low-confidence rate: 0.0279
- Incorrect windows: 6
- Error rate: 0.0167

## Limitations

- The model is trained on synthetic data, not certified production data.
- Weak classes with low support should not be overclaimed.
- Predictions should support, not replace, technician inspection decisions.
- Data drift should be monitored before using the model on new machines or real assets.
