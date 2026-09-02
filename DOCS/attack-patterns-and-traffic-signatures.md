# SIH26153 — Attack Patterns and Network Traffic Signatures



## 1. Purpose



This document captures the cybersecurity-side interpretation of the network traffic used in the SIH26153 forecasting system.



The objective is to document:



- DDoS-related traffic behavior observed in CICIDS2017.

- Measurable changes in network-flow features around DDoS attack periods.

- Relevant traffic indicators that can support temporal attack forecasting.

- The distinction between detecting an ongoing attack and forecasting an upcoming attack.

- How the observed behavior can be connected to the project's predictive cybersecurity narrative.



This document is based on the existing CICIDS2017 analysis and forecasting reports in the repository. It does not claim that individual features are independently sufficient to identify DDoS attacks.



---



## 2. Dataset Context



The project uses the CICIDS2017 dataset.



The repository's feature documentation reports:



- Total rows: 2,830,743

- Total columns: 80

- Label column: `Label`

- Unique attack/traffic labels: 15



The major classes include:



- BENIGN

- DDoS

- DoS Hulk

- DoS GoldenEye

- DoS slowloris

- DoS Slowhttptest

- PortScan

- Bot

- FTP-Patator

- SSH-Patator

- Infiltration

- Web attacks

- Heartbleed



For the current forecasting experiments, the main focus is DDoS traffic.



The feature documentation identifies flow-level network measurements such as:



- Flow Duration

- Total Fwd Packets

- Total Backward Packets

- Total Length of Fwd Packets

- Total Length of Bwd Packets

- Flow Bytes/s

- Flow Packets/s

- Fwd Packets/s

- Bwd Packets/s

- Packet Length Mean

- Packet Length Std

- SYN Flag Count

- RST Flag Count

- ACK Flag Count

- Average Packet Size

- Flow IAT statistics

- Active/Idle statistics



The final forecasting feature preparation reduced the working representation to 68 features after removing constant features and handling infinite/missing values.



---



## 3. Observed DDoS Traffic Behavior



The repository contains a temporal feature analysis comparing pre-attack and attack traffic across held-out test episodes 19, 20, and 21.



The analysis was specifically performed to determine whether network-flow features show measurable temporal changes around DDoS attack onset.



### 3.1 Combined Test-Episode Changes



| Feature | Pre-Attack Mean | Attack Mean | Percentage Change |

|---|---:|---:|---:|

| Flow Packets/s | 36,250.22 | 132.67 | -99.63% |

| Flow Bytes/s | 934,753.0 | 24,314.31 | -97.40% |

| Total Fwd Packets | 2.859 | 4.335 | +51.64% |

| Total Backward Packets | 4.312 | 0.782 | -81.86% |

| SYN Flag Count | 0.150 | 0.000 | -100.00% |

| Packet Length Mean | 377.579 | 202.206 | -46.45% |

| Packet Length Std | 795.867 | 405.254 | -49.08% |

| Flow Duration | 11,797,700 | 4,508,377 | -61.79% |

| Fwd Packets/s | 33,599.70 | 92.03 | -99.73% |

| Bwd Packets/s | 2,650.52 | 40.64 | -98.47% |

| Total Length of Fwd Packets | 3,575.71 | 27.26 | -99.24% |

| Total Length of Bwd Packets | 57.99 | 1,764.28 | +2,942.62% |

| Average Packet Size | 423.520 | 228.374 | -46.08% |



These values show that the network-flow representation changes substantially between the pre-attack and attack portions of the analyzed test episodes.



### 3.2 Important Interpretation



The strongest observed changes include:



- Very large decreases in `Flow Packets/s`.

- Very large decreases in `Fwd Packets/s`.

- Very large decreases in `Bwd Packets/s`.

- A large decrease in `Flow Bytes/s`.

- A large decrease in total forward-packet length.

- A large increase in total backward-packet length.

- Changes in packet-size statistics.

- Changes in flow duration.

- A measurable change in SYN flag behavior.



These observations demonstrate that the network-flow feature space contains temporal information associated with the DDoS episodes used in the experiment.



However, these are \*\*aggregate pre-attack vs attack comparisons\*\*. They should not be interpreted as saying that every DDoS attack will always produce exactly the same numerical pattern.



---



## 4. Relevant Traffic Indicators for Forecasting



The current analysis suggests several categories of network behavior that are useful for the forecasting model.



### 4.1 Traffic Volume and Rate



Relevant measurements include:



- Flow Packets/s

- Flow Bytes/s

- Fwd Packets/s

- Bwd Packets/s

- Total Fwd Packets

- Total Backward Packets



These measurements describe the amount and rate of traffic observed within network flows.



The temporal analysis shows substantial changes in several of these values around the analyzed DDoS periods.



### 4.2 Packet Size Characteristics



Relevant measurements include:



- Packet Length Mean

- Packet Length Std

- Average Packet Size

- Fwd Packet Length statistics

- Bwd Packet Length statistics



The test-episode analysis shows measurable changes in packet-size characteristics between the compared traffic regions.



### 4.3 Flow Timing Characteristics



Relevant measurements include:



- Flow Duration

- Flow IAT Mean

- Flow IAT Std

- Flow IAT Max

- Flow IAT Min

- Forward IAT statistics

- Backward IAT statistics



These features provide information about the temporal structure of network flows.



### 4.4 TCP Flag Indicators



Relevant measurements include:



- SYN Flag Count

- RST Flag Count

- PSH Flag Count

- ACK Flag Count

- FIN Flag Count

- URG Flag Count

- ECE Flag Count



The current temporal analysis specifically reports a change in SYN Flag Count across the compared pre-attack and attack regions.



---



## 5. Attack Pattern: DDoS



### Pattern



The current project focuses on forecasting DDoS activity from network-flow sequences.



The repository's sequence analysis identifies multiple contiguous DDoS regions in the CICIDS2017 Friday DDoS traffic.



The sequence analysis reports:



- 225,745 total rows.

- 45 contiguous label regions.

- 22 DDoS regions.

- The first major DDoS region begins at sequence position 18,883.

- The final listed DDoS region ends at sequence position 197,542.

- One anomalous DDoS region contains only 3 flows.



This demonstrates that the dataset contains temporally contiguous attack episodes rather than only isolated independent attack records.



### Cybersecurity Relevance



For a forecasting system, contiguous attack episodes are important because the model can observe the network state leading up to an attack rather than only classifying an already-known attack flow.



The project therefore treats network traffic as a sequence of observations.



---



## 6. Detection vs Forecasting



### Traditional Detection



A conventional intrusion-detection approach generally asks:



> "Is the network currently under attack?"



The classifier receives the current or recent traffic representation and produces an attack/non-attack decision.



### Forecasting



The SIH26153 objective is different:



> "Given the recent network state, is the network likely to transition toward an attack state?"



The forecasting system uses an observation window of previous network-flow observations and attempts to predict a future attack state.



This distinction is central to the project.



A model that performs well at detecting traffic after an attack has already started does not automatically demonstrate useful forecasting.



Therefore, the project evaluates:



- Classification performance.

- Temporal warning behavior.

- Lead time before attack onset.

- False alarm behavior.

- Performance across different forecast horizons.



---



## 7. Current Forecasting Baseline



The repository contains a Logistic Regression temporal baseline.



Configuration:



- Representation: mean + standard deviation over a 100-flow observation window.

- Selected threshold: 0.90.



Test results:



| Metric | Logistic Regression |

|---|---:|

| Precision | 0.3103 |

| Recall | 0.6000 |

| F1 | 0.4091 |

| ROC-AUC | 0.8514 |

| PR-AUC | 0.3014 |

| False Alarm Rate | 0.1646 |



This provides the baseline against which the neural forecasting model can be compared.



---



## 8. GRU V2 Forecasting Result



The repository also contains the GRU V2 forecasting experiment.



Configuration:



- Input shape: `(1365, 100, 68)`

- Observation window: 100 flows

- Features: 68

- Hidden size: 96

- GRU layers: 2

- Dropout: 0.3

- Learning rate: 0.0005

- Weight decay: 0.0001

- Selected threshold: 0.4000



Test results:



| Metric | GRU V2 |

|---|---:|

| Precision | 0.5172 |

| Recall | 1.0000 |

| F1 | 0.6818 |

| ROC-AUC | 0.9329 |

| PR-AUC | 0.5420 |

| False Alarm Rate | 0.1152 |



Compared with the Logistic Regression baseline, GRU V2 shows:



- Higher F1: 0.6818 vs 0.4091.

- Higher ROC-AUC: 0.9329 vs 0.8514.

- Lower False Alarm Rate: 0.1152 vs 0.1646.

- Higher recall: 1.0000 vs 0.6000.



This supports the project's claim that sequence modeling provides a stronger forecasting representation than the current statistical Logistic Regression baseline on this experiment.



It does not, by itself, prove that the model will generalize to every network environment.



---



## 9. Why Temporal Context Matters



The forecasting model receives sequences rather than treating each observation as completely independent.



A 100-flow observation window allows the model to use the recent evolution of multiple network-flow features.



This is important because an upcoming attack may be associated with a changing pattern across multiple observations rather than one isolated feature value.



The temporal feature analysis provides evidence that several network-flow characteristics differ between pre-attack and attack regions.



The GRU architecture is therefore used to model sequential information that a simple aggregated baseline does not explicitly represent.



---



## 10. Early-Warning Evidence



The repository contains early-warning analysis for held-out test episodes.



For the GRU forecasting analysis:



| Episode | Attack Start | First Warning | Lead Time |

|---|---:|---:|---:|

| 19 | 36,910 | 36,709 | 201 flows |

| 20 | 38,910 | 38,799 | 111 flows |

| 21 | 40,910 | 40,909 | 1 flow |



The model produced an early warning in all three held-out episodes, but the lead time varied substantially.



Therefore:



> A 100% warning rate on these three episodes should not be presented as proof of consistently useful early warning.



The episode-level lead-time distribution must be reported alongside the warning rate.



---



## 11. Multi-Horizon Forecasting



The repository also contains multi-horizon forecasting analysis for 50, 100, 200, and 500-flow forecast horizons.



The operational analysis reports:



| Horizon | Warning Rate | Mean Lead | Median Lead | >=100 Flow Early |

|---|---:|---:|---:|---:|

| 50 | 100% | 198.7 | 202 | 66.7% |

| 100 | 100% | 329.3 | 189 | 66.7% |

| 200 | 100% | 341.0 | 207 | 66.7% |

| 500 | 100% | 901.0 | 901 | 100% |



The 200-flow horizon had:



- F1: 0.7927

- Precision: 0.7572

- Recall: 0.8317

- ROC-AUC: 0.9225

- PR-AUC: 0.7726

- False Alarm Rate: 0.0761



The 500-flow horizon requires particular caution:



- Its reported mean lead was 901 flows.

- Its False Alarm Rate was 0.9933.

- Warnings fired at the first pre-attack window in the analyzed episodes.



Therefore, the 500-flow result should \*\*not\*\* be presented simply as "the best 901-flow early warning." Its false-alarm behavior makes it operationally poor in the current experiment.



Also, this operational multi-horizon analysis should not be confused with a fully trained multi-horizon GRU result unless a separate training report confirms that training.



---



## 12. MITRE ATT\&CK Mapping Status



The current repository does not contain a dedicated MITRE ATT\&CK mapping document.



Therefore, this document does not assign unsupported MITRE ATT\&CK technique IDs to the observed CICIDS2017 DDoS traffic.



The intended cybersecurity narrative is:



\*\*Observed network-flow behavior → temporal state representation → forecast of future attack state → explainable alert → attack-stage interpretation.\*\*



A formal MITRE ATT\&CK mapping should be added only after the relevant technique/behavior mapping has been explicitly verified.



---



## 13. Detection-to-Forecasting Narrative



The system can be presented as a progression:



### Step 1 — Observe



Collect recent network-flow observations.



### Step 2 — Represent



Convert the recent traffic into the model's 68-feature representation.



### Step 3 — Model Temporal State



Use sequential observations to represent the recent network state.



### Step 4 — Forecast



Estimate the probability of a future DDoS-related state.



### Step 5 — Evaluate Warning Quality



Measure:



- Whether an attack was warned about.

- How many flows before attack onset the warning occurred.

- False alarms.

- Precision/recall/F1.

- ROC-AUC and PR-AUC.

- Performance across forecast horizons.



### Step 6 — Explain



Expose the network indicators contributing to the predicted future state and connect the result to the cybersecurity interpretation.



This is the core distinction between a static IDS-style classifier and the intended predictive-defense system.



---



## 14. Cybersecurity Interpretation for the Dashboard



The dashboard should distinguish between:



### Current Attack Status



"What is happening now?"



and



### Forecasted Attack Risk



"What is likely to happen in the future based on the observed network trajectory?"



The forecast view should therefore avoid displaying a prediction as though it were a confirmed current attack.



Recommended terminology:



- `Current State`

- `Forecast Probability`

- `Forecast Horizon`

- `Warning Lead Time`

- `Confidence / Threshold`

- `Top Contributing Features`

- `Attack Scenario`

- `Alert Status`



Any mock dashboard values must remain clearly separated from real model outputs until the backend integration is complete.



---



## 15. Limitations



The current cybersecurity analysis has several important limitations:



1\. The early-warning evaluation uses only three held-out test episodes.

2\. A high warning rate does not guarantee useful lead time.

3\. Lead time varies significantly between episodes.

4\. The 500-flow horizon currently has an extremely high false-alarm rate.

5\. The current evidence is focused primarily on DDoS traffic.

6\. Aggregate feature differences should not be interpreted as universal DDoS signatures.

7\. CICIDS2017 flow data and the current experimental setup do not establish generalization to live production networks.

8\. A dedicated MITRE ATT\&CK mapping has not yet been verified in the repository.

9\. The dashboard is currently separated from the real ML backend and should not present mock values as live predictions.



---



## 16. Current Cybersecurity Takeaway



The existing experiments provide evidence that DDoS-related network-flow sequences contain measurable temporal changes and that GRU-based sequence modeling can outperform the current Logistic Regression temporal baseline on the held-out experiment.



The strongest cybersecurity argument is therefore not:



> "The model detects DDoS with high accuracy."



Instead, the stronger argument is:



> "The system learns temporal network-state patterns from recent traffic and uses them to estimate whether the network is moving toward a future DDoS state, while evaluating warning lead time and false-alarm behavior."



This framing is aligned with the predictive-defense objective of SIH26153 and avoids presenting a conventional static IDS classifier as a world model.

