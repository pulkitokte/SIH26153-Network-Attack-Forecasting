# Riddhi Day 4 — Explanation Evaluation Audit



## SIH26153 — AI Based Network Attack Forecasting from Network Traffic Data



*\*Workstream:** Explanation Evaluation  

*\*Role:** Riddhi  

*\*Day:** Day 4  

*\*Status:** COMPLETE at verified evaluation level



---



# 1. Purpose



This document evaluates the validity, consistency, stability, and reproducibility of the local temporal feature perturbation explanation method used with the frozen Multi-Horizon GRU.



The evaluation focuses on whether the explanation:



- corresponds to measurable changes in model probability,

- behaves consistently across nearby timesteps,

- remains observable across multiple held-out TEST sequences,

- behaves separately across forecast horizons,

- matches the production inference path,

- is reproducible,

- and remains within safe interpretation boundaries.



The evaluation does not attempt to establish feature causality, attacker intent, or universal DDoS feature importance.



---



# 2. Explanation Method Under Evaluation



The evaluated method is:



*\*Local Temporal Feature Perturbation using a per-feature training-tensor median baseline.**



For one selected feature at one selected timestep:



1\. Start with the original held-out TEST sequence.

2\. Record the original Multi-Horizon GRU probabilities.

3\. Replace one feature value at one timestep with that feature's training-tensor median.

4\. Run the same frozen GRU again.

5\. Record the perturbed probabilities.

6\. Calculate:



\\\[

\\Delta P = P\_{\\text{perturbed}} - P\_{\\text{original}}

\\]



The resulting delta is interpreted as local model sensitivity.



A negative delta means that replacing the observed value with the baseline reduced the model probability.



A positive delta means that the replacement increased the model probability.



The magnitude describes the observed probability change for that particular perturbation.



---



# 3. Evaluation Criteria



The explanation method was evaluated using the following criteria:



| Criterion | Purpose | Result |

|---|---|---|

| Numerical faithfulness | Verify delta calculation | PASS |

| Temporal stability | Check nearby timestep behaviour | COMPLETE |

| Sample stability | Check multiple held-out TEST sequences | COMPLETE |

| Horizon consistency | Evaluate H50/H100/H200/H500 separately | COMPLETE |

| Production consistency | Compare explanation path with production inference | PASS |

| Reproducibility | Repeat identical perturbations | PASS |

| Interpretation safety | Prevent causal/universal claims | PASS |



---



# 4. Numerical Faithfulness Audit



## 4.1 Test Configuration



The numerical faithfulness audit used:



- TEST sequence index: 200

- Timesteps: 95, 96, 97, 98, 99

- Features:

&#x20; - Feature 20 — Fwd IAT Total

&#x20; - Feature 25 — Bwd IAT Total

&#x20; - Feature 65 — Idle Std

&#x20; - Feature 67 — Idle Min

- Horizons:

&#x20; - H50

&#x20; - H100

&#x20; - H200

&#x20; - H500



Training-tensor medians were used as perturbation baselines.



---



## 4.2 Base Probabilities



For TEST sequence 200:



| Horizon | Base probability |

|---|---:|

| H50 | 0.080975152552 |

| H100 | 0.581500947475 |

| H200 | 0.548313021660 |

| H500 | 0.498043715954 |



---



## 4.3 Numerical Consistency



Every tested perturbation produced:



- a valid perturbed probability,

- a correctly calculated delta,

- numerical reconstruction error of `0.000e+00`.



The audit reported:



*\*FINAL VERDICT: PASS**



Therefore, the delta calculation is numerically consistent for the evaluated perturbations.



---



# 5. Representative Local Effect



The strongest observed local effect in the numerical audit was:



*\*Feature 67 — Idle Min at timestep 96**



| Horizon | Base | Perturbed | Delta |

|---|---:|---:|---:|

| H50 | 0.080975152552 | 0.049446344376 | -0.031528808177 |

| H100 | 0.581500947475 | 0.488006532192 | -0.093494415283 |

| H200 | 0.548313021660 | 0.492049425840 | -0.056263595819 |

| H500 | 0.498043715954 | 0.483064830303 | -0.014978885651 |



This demonstrates that the same local perturbation can affect different forecast horizons by different magnitudes.



---



# 6. Temporal Stability Audit



## 6.1 Configuration



Temporal stability was evaluated on:



- TEST sequence: 200

- Timesteps: 95–99

- Features:

&#x20; - Fwd IAT Total

&#x20; - Bwd IAT Total

&#x20; - Idle Std

&#x20; - Idle Min

- Horizons: H50, H100, H200, H500



---



## 6.2 Findings



### Fwd IAT Total



Fwd IAT Total showed zero observed probability change across the evaluated timesteps for this selected sequence.



This should not be interpreted as global model insensitivity to the feature.



It only means that the tested local perturbations did not change the probability for this sequence and timestep range.



### Bwd IAT Total



Bwd IAT Total showed measurable sensitivity across all five evaluated timesteps.



For H50 and H100, the observed deltas remained negative.



For H200, the sign changed from positive at earlier timesteps to negative at later timesteps.



For H500, the observed deltas remained positive.



This demonstrates horizon- and timestep-dependent local sensitivity.



### Idle Std



Idle Std showed zero observed probability change across the evaluated timesteps for this selected sequence.



Again, this is a local observation rather than a global feature-importance conclusion.



### Idle Min



Idle Min showed the strongest local effect around timesteps 96–97.



At timestep 96:



- H50 delta = -0.031528808177

- H100 delta = -0.093494415283

- H200 delta = -0.056263595819

- H500 delta = -0.014978885651



At timestep 97, the effect remained negative but with lower magnitude.



At timesteps 98–99, the tested perturbation produced zero observed change.



---



# 7. Temporal Stability Interpretation



The temporal audit demonstrates that local explanation effects can be:



- persistent across nearby timesteps,

- localized to particular timesteps,

- horizon-dependent,

- and context-dependent.



Therefore, the explanation should be presented as:



*\*local temporal model sensitivity**



rather than:



*\*a universal feature contribution.**



The observed results do not justify a causal interpretation.



---



# 8. Sample Stability Audit



## 8.1 Test Sequences



Sample stability was evaluated using eight held-out TEST sequences:



- 0

- 100

- 200

- 500

- 1000

- 1500

- 2000

- 2500



The same four candidate features and final timesteps 95–99 were evaluated.



---



# 9. Cross-Sample Strongest Feature Frequency



## H50



- Bwd IAT Total: 4/8 samples

- Idle Min: 3/8 samples

- Fwd IAT Total: 1/8 samples



## H100



- Bwd IAT Total: 4/8 samples

- Idle Min: 3/8 samples

- Fwd IAT Total: 1/8 samples



## H200



- Bwd IAT Total: 5/8 samples

- Idle Min: 3/8 samples



## H500



- Bwd IAT Total: 5/8 samples

- Idle Min: 3/8 samples



---



# 10. Sample-Level Findings



The strongest local feature was not identical across all TEST sequences.



Examples:



- TEST sequence 200 was dominated by Idle Min for all four horizons.

- TEST sequences 0, 100, 1000, and 2500 frequently showed Bwd IAT Total as the strongest local effect.

- TEST sequence 500 showed Fwd IAT Total as strongest for H50/H100 but Bwd IAT Total for H200/H500.

- TEST sequences 1500 and 2000 showed Idle Min as the strongest local effect.



The direction of the delta also varied between samples.



This confirms that the explanation is not a fixed global feature ranking.



---



# 11. Sample Stability Interpretation



Repeated sensitivity across multiple held-out TEST sequences supports the use of the method as:



*\*sample-specific model-sensitivity evidence.**



However, differences in:



- strongest feature,

- effect magnitude,

- timestep,

- and effect direction



show that the model response is context-dependent.



Therefore, the explanation should remain attached to the specific forecast instance being explained.



A feature appearing frequently as a strong local effect must not automatically be described as a universal DDoS indicator.



---



# 12. Production Consistency Audit



## 12.1 Configuration



Production consistency was checked using:



- TEST sequence index: 200

- Feature: Idle Min

- Feature index: 67

- Timestep: 96

- Baseline: training-tensor median

- Checkpoint: `ml/models/multihorizon\_gru.pt`



---



## 12.2 Production vs Explanation Base Probability



| Horizon | Production | Explanation | Difference | Result |

|---|---:|---:|---:|---|

| H50 | 0.080975152552 | 0.080975152552 | 0.000e+00 | PASS |

| H100 | 0.581500947475 | 0.581500947475 | 0.000e+00 | PASS |

| H200 | 0.548313021660 | 0.548313021660 | 0.000e+00 | PASS |

| H500 | 0.498043715954 | 0.498043715954 | 0.000e+00 | PASS |



The explanation base probabilities exactly matched the production inference probabilities.



---



# 13. Reproducibility Audit



The same perturbation was executed three times:



*\*Idle Min at timestep 96 → replace with training median**



All three repetitions produced identical probabilities:



| Horizon | Perturbed probability |

|---|---:|

| H50 | 0.049446344376 |

| H100 | 0.488006532192 |

| H200 | 0.492049425840 |

| H500 | 0.483064830303 |



Repeat-to-repeat differences were:



*\*0.000e+00 for every horizon.**



---



# 14. Delta Reproducibility



The same perturbation produced identical deltas across all repetitions:



| Horizon | Delta |

|---|---:|

| H50 | -0.031528808177 |

| H100 | -0.093494415283 |

| H200 | -0.056263595819 |

| H500 | -0.014978885651 |



All repeated delta comparisons passed.



Therefore:



*\*Reproducibility = PASS**



---



# 15. Threshold and Prediction Consistency



The production probability-to-threshold mapping was also checked.



| Horizon | Probability | Threshold | Prediction | Result |

|---|---:|---:|---:|---|

| H50 | 0.080975152552 | 0.30 | 0 | PASS |

| H100 | 0.581500947475 | 0.55 | 1 | PASS |

| H200 | 0.548313021660 | 0.45 | 1 | PASS |

| H500 | 0.498043715954 | 0.35 | 1 | PASS |



The stored production predictions were consistent with the corresponding thresholds.



---



# 16. Overall Evaluation Result



| Evaluation Area | Verdict |

|---|---|

| Numerical faithfulness | **PASS** |

| Temporal stability | **COMPLETE** |

| Sample stability | **COMPLETE** |

| Cross-horizon evaluation | **COMPLETE** |

| Production consistency | **PASS** |

| Reproducibility | **PASS** |

| Interpretation safety | **PASS** |



---



# 17. Scientific Interpretation



The evaluated explanation method provides evidence of local model sensitivity for the frozen Multi-Horizon GRU.



The audits show that:



1\. Perturbations produce measurable probability changes.

2\. The probability deltas are numerically consistent.

3\. Local effects can persist across nearby timesteps.

4\. Effects can differ between forecast horizons.

5\. Effects can differ between held-out TEST sequences.

6\. The strongest local feature is not fixed across all samples.

7\. The same perturbation is reproducible.

8\. The explanation base output matches the production inference path.



Together, these findings support using the method as a:



*\*local, sample-specific, horizon-aware explanation mechanism.**



---



# 18. Interpretation Boundaries



The following claims are NOT supported by these audits:



- A feature independently causes a DDoS attack.

- A feature independently causes the GRU prediction.

- A feature is a universal DDoS signature.

- A feature is globally the most important feature.

- The explanation identifies attacker intent.

- The explanation attributes activity to a specific attacker.

- The explanation directly predicts a MITRE ATT&CK technique.

- A local perturbation delta is equivalent to causal importance.



These claims must not appear in the dashboard, PPT, demo narration, or project report.



---



# 19. Safe Judge-Facing Explanation



A judge-facing explanation should use wording such as:



> “The model forecast is based on the temporal pattern across the observed network-flow window. For this specific forecast, local perturbation analysis shows which observed feature-time combinations the frozen GRU is most sensitive to. The effect is horizon-dependent and sample-specific, so these are model-sensitivity signals rather than causal attack indicators.”



---



# 20. Relationship to Cybersecurity Interpretation



The explanation layer must remain separate from the cybersecurity interpretation layer.



The correct conceptual flow is:



*\*Observed network traffic**



→ **Temporal model forecast**



→ **Future attack probability**



→ **Local model-sensitivity explanation**



→ **Network behaviour interpretation**



→ **MITRE ATT&CK context where evidence supports it**



The explanation does not itself assign a MITRE technique.



Cybersecurity interpretation and MITRE mapping must remain evidence-based and separate from model attribution.



---



# 21. Relationship to Forecasting



The system is a forecasting system rather than a simple static IDS classifier.



The explanation therefore describes how the frozen model responds to the observed temporal input when forecasting future attack probability.



The explanation should not be described as proof that an attack has already occurred.



---



# 22. Limitations



The current evaluation has several important limitations:



1\. Sample stability was evaluated on eight selected held-out TEST sequences rather than the complete TEST set.

2\. Temporal stability was evaluated on a local timestep range of 95–99.

3\. Only selected features were evaluated in these audits.

4\. The perturbation baseline is a per-feature training-tensor median.

5\. Local perturbation effects depend on the selected baseline.

6\. The method is local rather than a global feature-importance method.

7\. The observed sensitivity does not imply causality.

8\. The current evidence does not establish universal DDoS signatures.

9\. Different horizons can respond differently to the same feature perturbation.

10\. H500 remains subject to the previously documented long-range calibration and operating-point limitations.



These limitations should be preserved in final project documentation.



---



# 23. Final Riddhi Verdict



*\*Riddhi Day 4 Explanation Evaluation = COMPLETE**



The explanation evaluation pipeline has passed the key verification checks available at this stage.



The strongest supported conclusion is:



> **The local temporal feature-perturbation explanation method is numerically faithful, reproducible, production-consistent, and capable of revealing sample- and horizon-dependent model sensitivity on held-out TEST sequences.**



The method should be presented as **local model-sensitivity evidence**, not as causal attribution or universal feature importance.



---



# 24. Handoff to Next Workstream



Riddhi's evaluation findings are ready for integration with:



- the ML explainability implementation,

- the cybersecurity explanation specification,

- backend explanation output,

- dashboard explanation UI,

- demo narration,

- and final SIH PPT.



Any future implementation must preserve the interpretation boundaries documented in this report.



---



## Status



*\*Riddhi Day 4 — 100% COMPLETE at verified evaluation level.**

