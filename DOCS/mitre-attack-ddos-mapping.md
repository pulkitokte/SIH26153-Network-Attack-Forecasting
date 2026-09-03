# MITRE ATT&CK Mapping — DDoS Forecasting

## 1. Purpose

This document defines the verified MITRE ATT&CK interpretation for the current SIH26153 DDoS forecasting scope.

The purpose is to connect:

**Observed network-flow behavior → temporal network-state representation → future DDoS forecast → cybersecurity interpretation**

This mapping is intended to support the project's predictive cyber-defence narrative.

The mapping does not claim that the forecasting model independently identifies every adversary technique or attack procedure.

---

## 2. Current Project Scope

The current SIH26153 implementation focuses on forecasting DDoS activity from CICIDS2017 network-flow sequences.

The current forecasting experiments use:

- 100-flow observation windows.
- 68 network-flow features.
- Episode-based temporal evaluation.
- Held-out test episodes.
- Multiple forecast horizons in the Multi-Horizon GRU experiment.
- DDoS as the primary forecasted attack state.

The model estimates whether a future DDoS-related state is likely based on the recent network state.

---

## 3. Verified MITRE ATT&CK Mapping

### Primary Technique

**Technique ID:** T1498

**Technique Name:** Network Denial of Service

**Tactic:** Impact (TA0040)

**Impact Type:** Availability

MITRE ATT&CK defines Network Denial of Service as activity intended to degrade or block the availability of targeted resources through network-level denial-of-service behavior.

MITRE explicitly includes distributed denial-of-service (DDoS) within the scope of Network Denial of Service.

Therefore:

```text
DDoS forecasting scope
        ↓
Network Denial of Service
        ↓
T1498
        ↓
Impact (TA0040)
        ↓
Availability
```

## 4. Specific Sub-Technique

### T1498.001 — Direct Network Flood

T1498.001 is the MITRE ATT&CK sub-technique for Network Denial of Service involving direct high-volume network traffic sent toward a target.

For the current project, this is the relevant sub-technique when the observed DDoS traffic behavior supports a direct network-flood interpretation.

The mapping should be treated as cybersecurity context derived from the analyzed attack scenario, not as a direct output of the forecasting model.

Therefore:

**T1498.001 is used as the specific sub-technique when the observed network behavior provides sufficient support for direct network flooding.**

---


## 5. Reflection Amplification

### T1498.002 — Reflection Amplification

T1498.002 describes Network Denial of Service performed through third-party intermediary systems that reflect and potentially amplify traffic toward a target.

The current project does not have sufficient verified evidence to claim that the analyzed CICIDS2017 DDoS traffic specifically represents reflection-amplification behavior.

Therefore:

**T1498.002 is NOT assigned as a confirmed mapping for the current experiment.**

This avoids over-interpreting the dataset.

---

## 6. Mapping to Observed Network Behavior

The existing cybersecurity analysis identifies measurable changes in network-flow characteristics around the analyzed DDoS periods.

Relevant feature categories include:

### Traffic Volume and Rate

- Flow Packets/s
- Flow Bytes/s
- Fwd Packets/s
- Bwd Packets/s
- Total Fwd Packets
- Total Backward Packets

### Packet Characteristics

- Packet Length Mean
- Packet Length Std
- Average Packet Size
- Forward packet-length statistics
- Backward packet-length statistics

### Flow Timing

- Flow Duration
- Flow IAT Mean
- Flow IAT Std
- Flow IAT Max
- Flow IAT Min
- Forward IAT statistics
- Backward IAT statistics

### TCP Indicators

- SYN Flag Count
- RST Flag Count
- PSH Flag Count
- ACK Flag Count
- FIN Flag Count
- URG Flag Count
- ECE Flag Count

The existing analysis demonstrates that several of these network-flow measurements change substantially between compared pre-attack and attack regions.

These changes provide temporal network-state evidence associated with the DDoS episodes used in the experiment.

They should not be interpreted as universal numerical signatures of every DDoS attack.

---

## 7. Forecasting Interpretation

The important distinction is that the project is not simply mapping an already-observed attack to MITRE ATT&CK.

The intended workflow is:

```text
Recent network traffic
        ↓
68-feature temporal representation
        ↓
Temporal network-state modeling
        ↓
Future DDoS probability
        ↓
Forecast warning
        ↓
Cybersecurity interpretation
        ↓
MITRE ATT&CK context

```

## 8. Detection vs Forecasting

Detection answers whether malicious activity is already present in observed traffic.

Forecasting asks whether the current temporal network state provides evidence that an attack is likely to occur in a future horizon.

For this project, the model output is therefore interpreted as a future-risk signal rather than proof that an attack is currently active.

## 9. Attack-Stage Interpretation

The current cybersecurity interpretation focuses on the transition toward a DDoS event rather than claiming a complete attacker kill chain.

The practical stage representation is:

```text
Normal / pre-attack traffic
        ↓
Temporal changes in network behavior
        ↓
Increasing forecast probability
        ↓
Early warning
        ↓
Potential DDoS onset
        ↓
Network Denial of Service
```

The mapping to MITRE ATT&CK is applied at the technique/context level. The project does not claim visibility into every preceding attacker action.

## 10. Evidence Supporting Forecasting Narrative

The forecasting narrative is supported by the temporal evaluation performed on held-out CICIDS2017 episodes.

Relevant evidence includes:

- 100-flow observation windows are used to represent recent network state.
- Future horizons of 50, 100, 200, and 500 flows are evaluated.
- Episode-based train/validation/test splitting preserves temporal separation.
- The Multi-Horizon GRU produces separate probabilities for each future horizon.
- Operational early-warning analysis evaluates whether warnings occur before attack onset.
- The test set contains held-out episodes rather than random row-level leakage.

These results support a predictive-network-state interpretation, while not proving that every high-probability prediction corresponds to a specific MITRE sub-technique.

## 11. Current Model-to-MITRE Relationship

The relationship between the ML model and MITRE ATT&CK is intentionally separated into two layers:

1. **Model layer:** forecasts future DDoS probability from temporal network traffic.
2. **Cybersecurity interpretation layer:** contextualizes the forecast using the observed DDoS scenario and the appropriate ATT&CK technique.

The model does not directly output a MITRE ATT&CK technique ID.

Therefore, a forecast probability should not be described as a direct prediction of T1498.001.

## 12. Dashboard Representation

The dashboard should expose the following cybersecurity context alongside the forecast:

- Current Network State
- Forecast Probability
- Forecast Horizon
- Warning Lead Time
- Decision Threshold
- Alert Status
- Attack Scenario
- MITRE ATT&CK Technique
- Top Contributing Features

Recommended presentation flow:

```text
Network Traffic
      ↓
Forecast Probability
      ↓
Early Warning
      ↓
Attack Scenario
      ↓
MITRE ATT&CK Context
      ↓
Explainability
```

The MITRE field should be presented as cybersecurity context, not as an independently learned classification output.

## 13. Explainability Boundary

Feature-level explanations can describe which network-flow characteristics contributed to the model forecast.

They should not be presented as proof of attacker intent, attribution, or exact execution of a MITRE sub-technique.

A safe interpretation is:

```text
Model evidence
      ↓
Observed network behavior
      ↓
Cybersecurity interpretation
      ↓
MITRE ATT&CK context
```

This preserves the distinction between statistical model evidence and analyst-level cybersecurity interpretation.

## 14. What Is Confirmed

The following points are currently supported by the project evidence:

- The dataset scope includes DDoS traffic from CICIDS2017.
- The feature pipeline produces 68 usable network-flow features.
- The forecasting model uses temporal sequences of 100 observed flows.
- Multiple future horizons are evaluated: 50, 100, 200, and 500 flows.
- The primary ATT&CK technique relevant to the DDoS scenario is T1498, Network Denial of Service.
- T1498 belongs to the Impact tactic, TA0040, and concerns availability impact.
- T1498.001, Direct Network Flood, is the relevant sub-technique when the observed behavior supports direct high-volume traffic toward the target.

## 15. What Is Not Claimed

The project does not currently claim:

- Exact attacker identity or attribution.
- That every DDoS flow sequence represents T1498.001 specifically.
- Reflection Amplification (T1498.002) without evidence of an intermediary/reflection mechanism.
- That the GRU directly predicts MITRE ATT&CK technique IDs.
- That a high forecast probability alone proves ATT&CK technique execution.
- Complete visibility into the attacker kill chain.

These boundaries should remain explicit in the SIH presentation and documentation.

## 16. Recommended SIH Presentation Statement

Recommended wording:

> Our model forecasts the probability of future DDoS activity from temporal network traffic. We then provide cybersecurity context by mapping the observed DDoS scenario to the relevant MITRE ATT&CK technique, primarily T1498 Network Denial of Service. Where the observed traffic supports a direct network-flood interpretation, we use T1498.001. This mapping is an interpretation layer, not a direct output of the forecasting model.

## 17. Current Status

**Status: Day 3 — Cybersecurity / MITRE mapping completed at the documented evidence level.**

The mapping is intentionally conservative. The primary confirmed technique is T1498, with T1498.001 used only where the observed network behavior supports the direct-flood interpretation. T1498.002 is not assigned because the current project evidence does not establish reflection or amplification infrastructure.

## 18. Source

Primary external reference:

- MITRE ATT&CK — T1498 Network Denial of Service
- MITRE ATT&CK — T1498.001 Direct Network Flood
- MITRE ATT&CK — T1498.002 Reflection Amplification

Project evidence:

- `DOCS/attack-patterns-and-traffic-signatures.md`
- CICIDS2017 DDoS feature and temporal evaluation artifacts
- Multi-Horizon GRU evaluation and prediction artifacts

## 19. Final Cybersecurity Takeaway

The project should present the DDoS forecasting system as a **predictive cyber-defence pipeline**:

```text
Temporal Network Traffic
        ↓
Network-State Representation
        ↓
Multi-Horizon Forecasting
        ↓
Early Warning
        ↓
DDoS Scenario Interpretation
        ↓
MITRE ATT&CK Context
        ↓
Explainable Cyber Defence Decision
```

The strongest claim is not that the system identifies an attacker with certainty. The strongest defensible claim is that it uses temporal network behavior to forecast future DDoS risk and translates that forecast into actionable cybersecurity context.

