# SIH26153 — Cybersecurity Explainability Specification

## Day 4 — Pranshu Workstream

---

## 1. Purpose

This document defines the cybersecurity-side explainability framework for the SIH26153 DDoS forecasting system.

The objective is to explain a model forecast in a way that is:

- technically defensible,
- understandable to cybersecurity judges,
- grounded in the project's existing evidence,
- clearly separated from unsupported model-attribution claims.

The explanation connects:

    Observed Network Traffic
            ↓
    Temporal Network State
            ↓
    Future DDoS Forecast
            ↓
    Early-Warning Interpretation
            ↓
    Cybersecurity Context
            ↓
    MITRE ATT&CK Context
            ↓
    Defensive Decision

This document does not introduce or claim a specific ML attribution technique such as SHAP, LIME, attention, or gradient-based attribution because no such method has been verified as part of the current forecasting implementation.

---

## 2. Current Forecasting Scope

The current SIH26153 implementation focuses on forecasting future DDoS-related activity from CICIDS2017 network-flow sequences.

The verified forecasting configuration uses:

- 100 observed network flows per input sequence.
- 68 network-flow features.
- Episode-based temporal evaluation.
- Held-out test episodes.
- Multiple future forecast horizons.
- Multi-Horizon GRU forecasting.
- DDoS as the primary forecasted attack state.

The model produces separate future-risk probabilities for:

- H50
- H100
- H200
- H500

The model output represents future DDoS-related risk for the selected horizon.

It is not a direct MITRE ATT&CK classification output.

---

## 3. What Does "Explainability" Mean in This Project?

For the current project, cybersecurity explainability means making the forecast understandable through three connected layers.

### Layer 1 — Model Output

Show:

- forecast horizon,
- probability,
- decision threshold,
- alert/forecast status.

Example:

    H100 Forecast Probability: 99.5%
    Decision Threshold: 55%
    Forecast Status: ATTACK

The probability is the model's statistical forecast.

### Layer 2 — Network Behaviour Context

Explain the recent network state using evidence-backed traffic characteristics.

The existing cybersecurity analysis identifies relevant categories.

#### Traffic Volume and Rate

- Flow Packets/s
- Flow Bytes/s
- Fwd Packets/s
- Bwd Packets/s
- Total Fwd Packets
- Total Backward Packets

#### Packet Characteristics

- Packet Length Mean
- Packet Length Std
- Average Packet Size
- Forward packet-length statistics
- Backward packet-length statistics

#### Flow Timing

- Flow Duration
- Flow IAT statistics
- Forward IAT statistics
- Backward IAT statistics

#### TCP Indicators

- SYN Flag Count
- RST Flag Count
- PSH Flag Count
- ACK Flag Count
- FIN Flag Count
- URG Flag Count
- ECE Flag Count

The existing temporal analysis demonstrates measurable changes across compared pre-attack and attack regions.

These characteristics therefore provide useful cybersecurity context for explaining the network state.

---

## 4. Important Interpretation Boundary

The project must not claim that one individual feature independently caused a GRU prediction.

For example, the following statement is NOT supported:

> "The SYN count increased, therefore the GRU predicted DDoS."

A safer interpretation is:

> "The recent network state contains temporal behaviour across multiple network-flow characteristics that is associated with the DDoS episodes represented in the experiment."

The explanation should therefore describe network behaviour patterns, not claim unsupported causal feature attribution.

---

## 5. Detection vs Forecasting

### Detection

Detection asks:

> "Is the network currently under attack?"

A detection system primarily identifies malicious activity that is already present in the observed traffic.

### Forecasting

SIH26153 asks:

> "Given the recent network state, is the network likely to transition toward a future attack state?"

The system therefore uses a 100-flow observation window to represent recent network behaviour and forecasts future DDoS-related activity at multiple horizons.

This distinction is central to the project.

A forecast warning should not automatically be described as proof that an attack is already active.

---

## 6. Cybersecurity Forecast Explanation Flow

The recommended explanation flow is:

    100 Observed Flows
            ↓
    Recent Temporal Network State
            ↓
    Traffic / Packet / Timing / TCP Behaviour
            ↓
    Multi-Horizon GRU
            ↓
    Future DDoS Probability
            ↓
    Horizon + Threshold
            ↓
    Early Warning
            ↓
    DDoS Scenario Interpretation
            ↓
    MITRE ATT&CK Context
            ↓
    Defensive Response

The explanation should always preserve this order.

---

## 7. Early-Warning Interpretation

A high forecast probability is useful because the project evaluates whether warnings can occur before the known attack onset.

The project evaluates:

- forecast probability,
- decision threshold,
- first qualifying warning,
- lead time before attack onset,
- false-alarm behaviour,
- performance across forecast horizons.

Therefore, a cybersecurity explanation can state:

> "The system is generating a future-risk warning before the evaluated DDoS onset."

It should not state:

> "The system has proven that an attack will definitely occur."

Forecasting represents risk, not certainty.

---

## 8. MITRE ATT&CK Interpretation

The primary confirmed MITRE ATT&CK context for the current DDoS scenario is:

    T1498
    Network Denial of Service
            ↓
    TA0040 — Impact
            ↓
    Availability

T1498.001 — Direct Network Flood may be used as the specific sub-technique when the observed traffic provides sufficient support for a direct network-flood interpretation.

T1498.002 — Reflection Amplification is not assigned as a confirmed mapping for the current experiment because the project evidence does not establish a reflection/amplification mechanism.

---

## 9. Model-to-MITRE Separation

The relationship must remain explicitly separated:

    MODEL LAYER

    Temporal network traffic
            ↓
    Future DDoS probability


    CYBERSECURITY INTERPRETATION LAYER

    Observed DDoS scenario
            ↓
    MITRE ATT&CK context

The GRU does NOT directly predict:

    T1498
    T1498.001
    T1498.002

Therefore:

> A forecast probability must not be described as a direct prediction of a MITRE ATT&CK technique ID.

MITRE ATT&CK is used as cybersecurity context for interpreting the forecasted DDoS scenario.

---

## 10. Evidence-Based Traffic Interpretation

The existing analysis reports measurable changes between compared pre-attack and attack regions.

Important observed categories include:

- traffic rates,
- traffic byte rates,
- forward/backward packet counts,
- packet-size statistics,
- flow duration,
- inter-arrival-time characteristics,
- TCP flag behaviour.

These observations support the statement that the network-flow representation contains temporal information associated with the DDoS episodes used in the experiment.

However:

> These are aggregate pre-attack versus attack comparisons and should not be treated as universal numerical signatures for every DDoS attack.

The explanation must retain this limitation.

---

## 11. Judge-Friendly Explanation Template

When demonstrating a forecast, use this structure.

### Step A — What did the model observe?

> "The model receives the recent 100-flow network state represented using 68 network-flow features."

### Step B — What is the model forecasting?

> "The Multi-Horizon GRU estimates the probability of future DDoS-related activity at multiple future horizons."

### Step C — Why is this cybersecurity-relevant?

> "The underlying network-flow analysis shows measurable temporal changes in traffic-rate, packet-size, flow-timing and TCP-related characteristics around the analyzed DDoS episodes."

### Step D — What does the warning mean?

> "A probability above the selected horizon threshold is treated as a forecast warning for that future horizon."

### Step E — How is MITRE used?

> "The forecasted DDoS scenario is then contextualized using MITRE ATT&CK T1498, with T1498.001 used only where the observed behaviour supports direct network flooding."

### Step F — What does it NOT mean?

> "The system does not identify the attacker, directly predict a MITRE technique ID, or prove attacker intent."

---

## 12. Allowed Claims

The following claims are supported by the current project evidence:

- The system forecasts future DDoS-related activity from temporal network traffic.
- The model uses 100-flow observation windows.
- The working representation contains 68 network-flow features.
- Multiple forecast horizons are evaluated.
- The system evaluates early-warning behaviour before attack onset.
- Traffic, packet, timing, and TCP characteristics provide cybersecurity context.
- DDoS activity can be contextualized using MITRE ATT&CK T1498.
- T1498.001 can be used when direct-flood interpretation is supported by the observed scenario.
- The model output and MITRE interpretation are separate layers.
- The forecast should be treated as a future-risk signal rather than certainty.

---

## 13. Claims That Must NOT Be Made

Do not claim:

- The GRU directly predicts MITRE ATT&CK IDs.
- A single feature independently causes a forecast.
- The system identifies the exact attacker.
- The system performs attacker attribution.
- The system proves attacker intent.
- Every DDoS sequence is T1498.001.
- T1498.002 is confirmed for the current experiment.
- The system observes the complete attacker kill chain.
- A high forecast probability guarantees an attack.
- Aggregate feature changes are universal DDoS signatures.
- Mock dashboard factors are real GRU attribution scores.
- SHAP/LIME/attention results exist unless a verified implementation and evaluation are subsequently added.

---

## 14. Current Mock Explainability Data — Important Boundary

The existing frontend contains `defaultFactors` in:

    website/src/data/mock.ts

These include descriptions involving:

- abnormal packet rate,
- connection attempts,
- SYN traffic,
- source IP diversity,
- rolling Isolation Forest scores.

These values are mock/legacy dashboard data and are not verified outputs of the current Multi-Horizon GRU forecasting pipeline.

Therefore they must not be presented to judges as real per-prediction GRU explanations.

Any future replacement should be explicitly connected to the verified forecasting pipeline and should be backed by an appropriate explanation methodology.

---

## 15. Explainability Method Status

Current status:

    SHAP                    → Not verified
    LIME                    → Not verified
    GRU Attention           → Not verified
    Gradient Attribution   → Not verified
    Permutation Importance → Not verified
    Per-prediction feature scores → Not verified

This document intentionally does not fabricate any of these methods.

The next ML-side workstream should determine whether a scientifically appropriate model-level explanation method can be added.

---

## 16. Defensive Interpretation

The purpose of the explanation is not merely to display a probability.

The intended defensive meaning is:

    Recent Network State
            ↓
    Future Risk Estimate
            ↓
    Early Warning
            ↓
    Analyst Awareness
            ↓
    Investigation / Defensive Preparation

A forecast warning can help a defender investigate the network state and prepare an appropriate response before the expected attack horizon.

The system should therefore be presented as a predictive cyber-defence aid, not as an autonomous attacker-identification system.

---

## 17. Dashboard Explanation Structure

For the real forecast page, the recommended judge-facing information hierarchy is:

    Forecast Probability
            ↓
    Forecast Horizon
            ↓
    Threshold / Alert Status
            ↓
    Early-Warning Lead Time
            ↓
    Network Behaviour Context
            ↓
    DDoS Scenario
            ↓
    MITRE ATT&CK Context

Only values actually returned by or supported by the verified pipeline should be labelled as real model output.

Mock/legacy surfaces should remain clearly separated from the real forecast flow.

---

## 18. 30-Second Cybersecurity Explanation

Recommended presentation script:

> "Our system observes the recent network state as a sequence of 100 flows with 68 network-flow features. The Multi-Horizon GRU then forecasts the probability of future DDoS-related activity at different horizons. We interpret that forecast using the temporal changes observed in traffic-rate, packet-size, flow-timing and TCP characteristics. For cybersecurity context, the DDoS scenario is mapped to MITRE ATT&CK T1498, and T1498.001 is used only when direct network-flood behaviour is supported. The important point is that MITRE mapping is an interpretation layer — our model forecasts future DDoS risk; it does not directly predict a MITRE ID or identify an attacker."

---

## 19. Handoff to ML Explainability Workstream

The next ML-side workstream should determine whether a scientifically appropriate model-level explanation method can be added.

The ML workstream should answer:

1. What explanation method is technically appropriate for the current GRU architecture?
2. Can it operate on the `(100, 68)` temporal input without introducing unsupported assumptions?
3. Should explanations be generated per horizon?
4. How should temporal and feature dimensions be aggregated for judge-readable output?
5. Can the explanation be evaluated for stability or consistency?
6. What evidence is required before calling a feature a "contributor"?
7. How can explanation results be kept separate from MITRE interpretation?

No explanation method should be claimed until it is actually implemented, tested, and documented.

---

## 20. Final Cybersecurity Takeaway

The strongest defensible cybersecurity narrative is:

    Temporal Network Traffic
            ↓
    Network-State Representation
            ↓
    Multi-Horizon Forecasting
            ↓
    Future DDoS Risk
            ↓
    Early Warning
            ↓
    Cybersecurity Interpretation
            ↓
    MITRE ATT&CK Context
            ↓
    Defensive Decision Support

The system's value is not that it claims certainty about an attacker.

Its defensible value is that it uses temporal network behaviour to estimate future DDoS risk and translate that forecast into understandable cybersecurity context.

---

## 21. Status

**Day 4 — Pranshu Workstream**

**Status: Cybersecurity Explainability Specification completed at the currently verified evidence level.**

This document is intentionally conservative and should be used as the cybersecurity interpretation baseline for:

- ML explainability work,
- dashboard explanation design,
- SIH presentation,
- judge Q&A,
- final demo choreography.

---
