# Feature Documentation

- Total rows: **2,830,743**
- Total columns: **80**
- Label column: `Label`
- Class distribution:

| Class | Count | % |
|---|---|---|
| BENIGN | 2,273,097 | 80.30% |
| DoS Hulk | 231,073 | 8.16% |
| PortScan | 158,930 | 5.61% |
| DDoS | 128,027 | 4.52% |
| DoS GoldenEye | 10,293 | 0.36% |
| FTP-Patator | 7,938 | 0.28% |
| SSH-Patator | 5,897 | 0.21% |
| DoS slowloris | 5,796 | 0.20% |
| DoS Slowhttptest | 5,499 | 0.19% |
| Bot | 1,966 | 0.07% |
| Web Attack � Brute Force | 1,507 | 0.05% |
| Web Attack � XSS | 652 | 0.02% |
| Infiltration | 36 | 0.00% |
| Web Attack � Sql Injection | 21 | 0.00% |
| Heartbleed | 11 | 0.00% |

## Column Summary

| # | Column | Dtype | Non-Null | Nulls | Unique | Min | Max |
|---|---|---|---|---|---|---|---|
| 1 | Destination Port | int64 | 2,830,743 | 0 | 53,805 | 0 | 6.55e+04 |
| 2 | Flow Duration | int64 | 2,830,743 | 0 | 1,050,899 | -13 | 1.2e+08 |
| 3 | Total Fwd Packets | int64 | 2,830,743 | 0 | 1,432 | 1 | 2.2e+05 |
| 4 | Total Backward Packets | int64 | 2,830,743 | 0 | 1,747 | 0 | 2.92e+05 |
| 5 | Total Length of Fwd Packets | int64 | 2,830,743 | 0 | 17,928 | 0 | 1.29e+07 |
| 6 | Total Length of Bwd Packets | int64 | 2,830,743 | 0 | 64,698 | 0 | 6.55e+08 |
| 7 | Fwd Packet Length Max | int64 | 2,830,743 | 0 | 5,279 | 0 | 2.48e+04 |
| 8 | Fwd Packet Length Min | int64 | 2,830,743 | 0 | 384 | 0 | 2.32e+03 |
| 9 | Fwd Packet Length Mean | float64 | 2,830,743 | 0 | 99,716 | 0 | 5.94e+03 |
| 10 | Fwd Packet Length Std | float64 | 2,830,743 | 0 | 253,909 | 0 | 7.13e+03 |
| 11 | Bwd Packet Length Max | int64 | 2,830,743 | 0 | 4,838 | 0 | 1.95e+04 |
| 12 | Bwd Packet Length Min | int64 | 2,830,743 | 0 | 583 | 0 | 2.9e+03 |
| 13 | Bwd Packet Length Mean | float64 | 2,830,743 | 0 | 147,614 | 0 | 5.8e+03 |
| 14 | Bwd Packet Length Std | float64 | 2,830,743 | 0 | 248,869 | 0 | 8.19e+03 |
| 15 | Flow Bytes/s | float64 | 2,829,385 | 1,358 | 1,593,908 | -2.61e+08 | inf |
| 16 | Flow Packets/s | float64 | 2,830,743 | 0 | 1,240,164 | -2e+06 | inf |
| 17 | Flow IAT Mean | float64 | 2,830,743 | 0 | 1,166,311 | -13 | 1.2e+08 |
| 18 | Flow IAT Std | float64 | 2,830,743 | 0 | 1,056,642 | 0 | 8.48e+07 |
| 19 | Flow IAT Max | int64 | 2,830,743 | 0 | 580,289 | -13 | 1.2e+08 |
| 20 | Flow IAT Min | int64 | 2,830,743 | 0 | 136,316 | -14 | 1.2e+08 |
| 21 | Fwd IAT Total | int64 | 2,830,743 | 0 | 493,098 | 0 | 1.2e+08 |
| 22 | Fwd IAT Mean | float64 | 2,830,743 | 0 | 737,737 | 0 | 1.2e+08 |
| 23 | Fwd IAT Std | float64 | 2,830,743 | 0 | 700,313 | 0 | 8.46e+07 |
| 24 | Fwd IAT Max | int64 | 2,830,743 | 0 | 437,316 | 0 | 1.2e+08 |
| 25 | Fwd IAT Min | int64 | 2,830,743 | 0 | 110,631 | -12 | 1.2e+08 |
| 26 | Bwd IAT Total | int64 | 2,830,743 | 0 | 414,928 | 0 | 1.2e+08 |
| 27 | Bwd IAT Mean | float64 | 2,830,743 | 0 | 670,824 | 0 | 1.2e+08 |
| 28 | Bwd IAT Std | float64 | 2,830,743 | 0 | 709,042 | 0 | 8.44e+07 |
| 29 | Bwd IAT Max | int64 | 2,830,743 | 0 | 368,285 | 0 | 1.2e+08 |
| 30 | Bwd IAT Min | int64 | 2,830,743 | 0 | 66,074 | 0 | 1.2e+08 |
| 31 | Fwd PSH Flags | int64 | 2,830,743 | 0 | 2 | 0 | 1 |
| 32 | Bwd PSH Flags | int64 | 2,830,743 | 0 | 1 | 0 | 0 |
| 33 | Fwd URG Flags | int64 | 2,830,743 | 0 | 2 | 0 | 1 |
| 34 | Bwd URG Flags | int64 | 2,830,743 | 0 | 1 | 0 | 0 |
| 35 | Fwd Header Length | int64 | 2,830,743 | 0 | 3,771 | -3.22e+10 | 4.64e+06 |
| 36 | Bwd Header Length | int64 | 2,830,743 | 0 | 3,945 | -1.07e+09 | 5.84e+06 |
| 37 | Fwd Packets/s | float64 | 2,830,743 | 0 | 1,220,423 | 0 | 3e+06 |
| 38 | Bwd Packets/s | float64 | 2,830,743 | 0 | 1,107,886 | 0 | 2e+06 |
| 39 | Min Packet Length | int64 | 2,830,743 | 0 | 215 | 0 | 1.45e+03 |
| 40 | Max Packet Length | int64 | 2,830,743 | 0 | 5,708 | 0 | 2.48e+04 |
| 41 | Packet Length Mean | float64 | 2,830,743 | 0 | 215,826 | 0 | 3.34e+03 |
| 42 | Packet Length Std | float64 | 2,830,743 | 0 | 412,246 | 0 | 4.73e+03 |
| 43 | Packet Length Variance | float64 | 2,830,743 | 0 | 405,565 | 0 | 2.24e+07 |
| 44 | FIN Flag Count | int64 | 2,830,743 | 0 | 2 | 0 | 1 |
| 45 | SYN Flag Count | int64 | 2,830,743 | 0 | 2 | 0 | 1 |
| 46 | RST Flag Count | int64 | 2,830,743 | 0 | 2 | 0 | 1 |
| 47 | PSH Flag Count | int64 | 2,830,743 | 0 | 2 | 0 | 1 |
| 48 | ACK Flag Count | int64 | 2,830,743 | 0 | 2 | 0 | 1 |
| 49 | URG Flag Count | int64 | 2,830,743 | 0 | 2 | 0 | 1 |
| 50 | CWE Flag Count | int64 | 2,830,743 | 0 | 2 | 0 | 1 |
| 51 | ECE Flag Count | int64 | 2,830,743 | 0 | 2 | 0 | 1 |
| 52 | Down/Up Ratio | int64 | 2,830,743 | 0 | 31 | 0 | 156 |
| 53 | Average Packet Size | float64 | 2,830,743 | 0 | 212,207 | 0 | 3.89e+03 |
| 54 | Avg Fwd Segment Size | float64 | 2,830,743 | 0 | 99,716 | 0 | 5.94e+03 |
| 55 | Avg Bwd Segment Size | float64 | 2,830,743 | 0 | 147,611 | 0 | 5.8e+03 |
| 56 | Fwd Header Length.1 | int64 | 2,830,743 | 0 | 3,771 | -3.22e+10 | 4.64e+06 |
| 57 | Fwd Avg Bytes/Bulk | int64 | 2,830,743 | 0 | 1 | 0 | 0 |
| 58 | Fwd Avg Packets/Bulk | int64 | 2,830,743 | 0 | 1 | 0 | 0 |
| 59 | Fwd Avg Bulk Rate | int64 | 2,830,743 | 0 | 1 | 0 | 0 |
| 60 | Bwd Avg Bytes/Bulk | int64 | 2,830,743 | 0 | 1 | 0 | 0 |
| 61 | Bwd Avg Packets/Bulk | int64 | 2,830,743 | 0 | 1 | 0 | 0 |
| 62 | Bwd Avg Bulk Rate | int64 | 2,830,743 | 0 | 1 | 0 | 0 |
| 63 | Subflow Fwd Packets | int64 | 2,830,743 | 0 | 1,432 | 1 | 2.2e+05 |
| 64 | Subflow Fwd Bytes | int64 | 2,830,743 | 0 | 17,928 | 0 | 1.29e+07 |
| 65 | Subflow Bwd Packets | int64 | 2,830,743 | 0 | 1,747 | 0 | 2.92e+05 |
| 66 | Subflow Bwd Bytes | int64 | 2,830,743 | 0 | 64,738 | 0 | 6.55e+08 |
| 67 | Init_Win_bytes_forward | int64 | 2,830,743 | 0 | 12,151 | -1 | 6.55e+04 |
| 68 | Init_Win_bytes_backward | int64 | 2,830,743 | 0 | 13,112 | -1 | 6.55e+04 |
| 69 | act_data_pkt_fwd | int64 | 2,830,743 | 0 | 1,093 | 0 | 2.14e+05 |
| 70 | min_seg_size_forward | int64 | 2,830,743 | 0 | 28 | -5.37e+08 | 138 |
| 71 | Active Mean | float64 | 2,830,743 | 0 | 326,325 | 0 | 1.1e+08 |
| 72 | Active Std | float64 | 2,830,743 | 0 | 202,826 | 0 | 7.42e+07 |
| 73 | Active Max | int64 | 2,830,743 | 0 | 299,565 | 0 | 1.1e+08 |
| 74 | Active Min | int64 | 2,830,743 | 0 | 175,670 | 0 | 1.1e+08 |
| 75 | Idle Mean | float64 | 2,830,743 | 0 | 222,016 | 0 | 1.2e+08 |
| 76 | Idle Std | float64 | 2,830,743 | 0 | 197,616 | 0 | 7.69e+07 |
| 77 | Idle Max | int64 | 2,830,743 | 0 | 149,737 | 0 | 1.2e+08 |
| 78 | Idle Min | int64 | 2,830,743 | 0 | 223,888 | 0 | 1.2e+08 |
| 79 | Label | object | 2,830,743 | 0 | 15 | ['BENIGN'] |  |
| 80 | __source_file__ | object | 2,830,743 | 0 | 8 | ['Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv'] |  |

## Data Quality Notes

- Columns with infinite values: ['Flow Bytes/s', 'Flow Packets/s']
- Columns with missing values: ['Flow Bytes/s']
- Constant / zero-variance columns (candidates to drop): ['Bwd PSH Flags', 'Bwd URG Flags', 'Fwd Avg Bytes/Bulk', 'Fwd Avg Packets/Bulk', 'Fwd Avg Bulk Rate', 'Bwd Avg Bytes/Bulk', 'Bwd Avg Packets/Bulk', 'Bwd Avg Bulk Rate']