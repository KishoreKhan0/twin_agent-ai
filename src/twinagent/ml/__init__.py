"""Machine-learning utilities for TwinAgent AI."""

from twinagent.ml.diagnosis_reconciliation import (
    DiagnosisReconciliationConfig,
    DiagnosisReconciliationResult,
    export_reconciled_incident_diagnoses,
    reconcile_incident_diagnosis,
    reconcile_incident_diagnoses,
)
from twinagent.ml.explainability import (
    ExplainabilityConfig,
    ExplainabilityResult,
    analyze_prediction_errors,
    export_fault_classifier_explainability,
    extract_feature_importance,
)
from twinagent.ml.fault_classifier import (
    FaultClassifierConfig,
    FaultClassifierTrainingResult,
    predict_fault_windows,
    train_fault_classifier,
)
from twinagent.ml.features import (
    DEFAULT_SENSOR_COLUMNS,
    build_window_features,
    normalize_fault_label,
)
from twinagent.ml.incident_diagnosis import (
    IncidentMLDiagnosis,
    enrich_incidents_with_ml,
    export_ml_incident_diagnosis,
)

__all__ = [
    "DEFAULT_SENSOR_COLUMNS",
    "DiagnosisReconciliationConfig",
    "DiagnosisReconciliationResult",
    "ExplainabilityConfig",
    "ExplainabilityResult",
    "FaultClassifierConfig",
    "FaultClassifierTrainingResult",
    "IncidentMLDiagnosis",
    "analyze_prediction_errors",
    "build_window_features",
    "enrich_incidents_with_ml",
    "export_fault_classifier_explainability",
    "export_ml_incident_diagnosis",
    "export_reconciled_incident_diagnoses",
    "extract_feature_importance",
    "normalize_fault_label",
    "predict_fault_windows",
    "reconcile_incident_diagnosis",
    "reconcile_incident_diagnoses",
    "train_fault_classifier",
]
