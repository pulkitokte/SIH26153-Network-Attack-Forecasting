# SIH26153 - PRIYANSHI DAY 4
# REPRODUCIBLE EXPLAINABILITY AUDIT

---

## 1. Audit Role

**Role:** Priyanshi - Reproducibility & Automation

**Scope:** Reproducibility of the verified local temporal feature perturbation
explanation method used with the frozen Multi-Horizon GRU.

---

## 2. Objective

The objective of this audit is to verify that the explainability procedure:

1. Uses the same frozen production checkpoint.
2. Reconstructs the model using the checkpoint-stored architecture.
3. Uses the same 68-feature tensor representation.
4. Uses a TRAIN-derived per-feature median baseline.
5. Perturbs only the selected input feature at the selected timestep.
6. Produces deterministic outputs across repeated executions.
7. Produces base probabilities identical to production inference.
8. Does not require model retraining or parameter modification.

The explanation is treated as **local model-sensitivity evidence**, not
causal attribution or universal feature importance.

---

## 3. Verified Explainability Method

The verified method is:

**Local Temporal Feature Perturbation using a per-feature training-tensor
median baseline.**

For a selected forecast sequence:

1. Start with the original held-out TEST sequence.
2. Select one feature and one timestep.
3. Replace that feature value with the corresponding feature's median
   calculated from the TRAIN tensor.
4. Run the unchanged frozen Multi-Horizon GRU.
5. Record the perturbed H50, H100, H200, and H500 probabilities.
6. Calculate:

   Delta P = P_perturbed - P_original

The result is local and sample-specific.

---

## 4. Checkpoint Provenance

Current checkpoint:

`ml/models/multihorizon_gru.pt`

Verified SHA-256:

`88e354922577f9f5076a7416d682c47a81c626262071d34044f585f233f78019`

Checkpoint-stored architecture:

- input_size = 68
- hidden_size = 96
- num_layers = 2
- dropout = 0.30

Checkpoint-stored horizons:

- H50
- H100
- H200
- H500

Checkpoint-stored thresholds:

- H50 = 0.30
- H100 = 0.55
- H200 = 0.45
- H500 = 0.35

Checkpoint seed:

`42`

The checkpoint contains the model state dictionary.

---

## 5. Tensor and Feature Provenance

Verified tensor shapes:

- TRAIN: `(13515, 100, 68)`
- TEST: `(2703, 100, 68)`

Therefore:

- observation length = 100 flows
- feature count = 68

The tensor-builder derives model features from the prepared feature dataset
after excluding the declared metadata columns:

- Label
- episode_id
- sequence_phase
- sequence_position

The builder explicitly enforces an expected feature count of 68 and rejects
forecast-target/metadata leakage.

Rows are deterministically ordered by:

- episode_id
- sequence_position

The repository's existing Day 4 evaluation audit identifies:

**Feature 67 = Idle Min**

---

## 6. TRAIN-Derived Perturbation Baseline

The perturbation baseline is calculated from the TRAIN tensor only:

`median(X_train, axis=(0, 1))`

For the verified explanation example:

- Feature index = 67
- Feature name = Idle Min
- Timestep = 96
- TRAIN median = `6.022658e+06`

The TEST sequence itself is not used to calculate the baseline.

---

## 7. Deterministic Explanation Verification

Verified TEST sequence:

`X_test[200]`

Original production probabilities:

| Horizon | Probability |
|---|---:|
| H50 | 0.080975152552 |
| H100 | 0.581500947475 |
| H200 | 0.548313021660 |
| H500 | 0.498043715954 |

After replacing Feature 67 (`Idle Min`) at timestep 96 with the
TRAIN-derived median:

| Horizon | Perturbed Probability |
|---|---:|
| H50 | 0.049446344376 |
| H100 | 0.488006532192 |
| H200 | 0.492049425840 |
| H500 | 0.483064830303 |

---

## 8. Repeated-Run Reproducibility

The exact same perturbation was executed three times using:

- the same TEST sequence
- the same TRAIN-derived median
- the same feature index
- the same timestep
- the same frozen checkpoint
- the same production inference implementation

All three repetitions produced identical probabilities.

Repeat-to-repeat difference:

`0.000e+00` for every horizon.

Verified perturbed probabilities:

| Horizon | Perturbed Probability |
|---|---:|
| H50 | 0.049446344376 |
| H100 | 0.488006532192 |
| H200 | 0.492049425840 |
| H500 | 0.483064830303 |

**Result: PASS**

---

## 9. Delta Reproducibility

Verified probability deltas:

| Horizon | Delta |
|---|---:|
| H50 | -0.031528808177 |
| H100 | -0.093494415283 |
| H200 | -0.056263595819 |
| H500 | -0.014978885651 |

The same perturbation produced identical deltas across repetitions.

**Result: PASS**

---

## 10. Production Inference Consistency

The unperturbed explanation base probabilities were compared with the
production inference output for the same TEST sequence.

Production:

| Horizon | Probability |
|---|---:|
| H50 | 0.080975152552 |
| H100 | 0.581500947475 |
| H200 | 0.548313021660 |
| H500 | 0.498043715954 |

Explanation base:

| Horizon | Probability |
|---|---:|
| H50 | 0.080975152552 |
| H100 | 0.581500947475 |
| H200 | 0.548313021660 |
| H500 | 0.498043715954 |

Exact comparison:

`BASE MATCH: True`

**Result: PASS**

---

## 11. Checkpoint Reconstruction Consistency

The model was independently reconstructed from:

- checkpoint architecture
- checkpoint model_state_dict

The reconstructed model was evaluated on the same TEST sequence.

The resulting probabilities exactly matched the production inference
probabilities for all four horizons.

Exact comparison:

`CHECKPOINT RECONSTRUCTION MATCH: True`

**Result: PASS**

---

## 12. Inference-Safety Evidence

The production inference implementation uses:

- `model.eval()`
- `torch.no_grad()`
- CPU inference
- finite-input validation
- fixed expected input shape `(100, 68)`

The explainability procedure changes the input sequence for the
perturbation and re-runs the frozen model. It does not require retraining,
optimizer updates, or model-parameter modification.

---

## 13. Reproducibility Evidence Summary

| Audit Check | Result |
|---|---|
| Frozen checkpoint identity verified | PASS |
| Checkpoint architecture verified | PASS |
| Tensor feature count verified | PASS |
| TRAIN/TEST tensor dimensionality verified | PASS |
| TRAIN-derived median baseline verified | PASS |
| Feature 67 = Idle Min evidence verified | PASS |
| Explanation regenerated independently | PASS |
| Three repeated runs identical | PASS |
| Delta reproducibility | PASS |
| Explanation base = production inference | PASS |
| Checkpoint reconstruction = production inference | PASS |

---

## 14. Important Interpretation Boundary

The perturbation delta measures an observed change in the model's predicted
probability after replacing one input value with a selected baseline.

It does **not** establish:

- causal importance
- universal feature importance
- that the feature caused the attack
- that the feature is globally dominant
- that the explanation generalizes to every TEST sequence

The explanation should therefore be presented as:

**local model-sensitivity evidence for the specific forecast instance.**

---

## 15. Relationship to Day 3 Reproducibility

The Day 3 audit established strong internal ML reproducibility controls,
including:

- fixed random seed
- deterministic training configuration
- seeded DataLoader behavior
- fixed episode-based splits
- TEST isolation from threshold selection
- tensor integrity validation
- metadata alignment checks
- controlled checkpointing

Day 4 extends this reproducibility evidence from the forecasting pipeline
to the verified local explainability procedure.

Fresh-clone reproducibility remains a separate repository-level concern
because dependency, dataset setup, README, and orchestration gaps identified
during Day 3 have not been resolved by this explainability audit.

---

## 16. Final Conclusion

The verified local temporal feature perturbation explanation procedure is:

- deterministic
- reproducible
- production-consistent
- checkpoint-consistent
- based on a TRAIN-derived perturbation baseline
- applicable to the frozen Multi-Horizon GRU

The same explanation can be regenerated from the same repository artifacts
and produces identical probability changes across repeated executions.

Therefore:

**PRIYANSHI DAY 4 REPRODUCIBLE EXPLAINABILITY AUDIT = PASS**

The method should be presented as **local model-sensitivity evidence**, not
as causal attribution or universal feature importance.

---

## 17. Day 4 Status

**Role:** Priyanshi - Reproducibility & Automation

**Workstream:** Reproducible Explainability Pipeline

**Status:** COMPLETE

