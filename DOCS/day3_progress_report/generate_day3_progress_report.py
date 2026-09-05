"""
Generate the SIH26153 Day 3 internal team progress report PDF.

Regenerate:
    python DOCS/day3_progress_report/generate_day3_progress_report.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Spacer,
    Table,
    TableStyle,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from pdf_kit import (  # noqa: E402
    BOTTOM,
    CONTENT_W,
    FOREST,
    LEFT,
    PAGE_H,
    PAGE_W,
    PISTA_SOFT,
    RIGHT,
    RULE,
    TOP,
    WHITE,
    P,
    bullets,
    callout,
    draw_cover,
    draw_header_footer,
    flow_diagram,
    heading,
    init_styles,
    kv_table,
    member_banner,
    qa_block,
    simple_table,
    spacer,
    SectionMarker,
)

OUT_PDF = HERE / "SIH26153-Day3-Progress-Report.pdf"


def cover_story():
    story = [Spacer(1, 42)]
    story.append(P("INTERNAL TEAM HANDOFF  ·  DAY 3 COMPLETE", "cover_kicker"))
    story.append(P("AI based Network Attack Forecasting<br/>from Network Traffic Data", "cover_title"))
    story.append(P("SIH Problem <b>SIH26153</b>  ·  Dataset <b>CICIDS2017</b>  ·  04 September 2026", "cover_sub"))
    story.append(P("Final Day 3 Project Progress Report", "h2"))
    story.append(
        P(
            "Ye document public SIH PPT nahi hai. Ye team knowledge + progress handoff hai. "
            "Day 2 baseline already lock ho chuka tha. Ye report sirf Day 3 pe <b>kya verify / complete</b> hua, "
            "uska technical matlab, limitations, aur next stage batati hai.",
            "body",
        )
    )
    story.append(spacer(8))
    team = [
        ["Member", "Role", "Day 3"],
        ["Pranshu", "Cybersecurity / Network Analysis / Attack Intelligence", "100% DONE"],
        ["Pulkit", "Web Dashboard + Backend/API + System Integration", "100% DONE"],
        ["Pragati", "Data Engineering / Dataset Analysis / Temporal Validation", "100% DONE"],
        ["Ankita", "ML / Multi-Horizon GRU", "COMPLETE"],
        ["Riddhi", "ML Evaluation / Metrics / Early Warning / Comparison", "100% DONE"],
        ["Priyanshi", "Python Automation / Reproducibility / Experiment Reliability", "100% DONE"],
    ]
    data = [[P(c, "cell_head" if i == 0 else "cell") for i, c in enumerate(team[0])]]
    for row in team[1:]:
        data.append([P(f"<b>{row[0]}</b>", "cell"), P(row[1], "cell"), P(row[2], "cell_c")])
    t = Table(data, colWidths=[38 / 178 * CONTENT_W, 102 / 178 * CONTENT_W, 38 / 178 * CONTENT_W])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), FOREST),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PISTA_SOFT]),
                ("GRID", (0, 0), (-1, -1), 0.35, RULE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(t)
    story.append(spacer(8))
    story.append(
        callout(
            "finding",
            "Day 3 checkpoint ke mutabik currently <b>sirf Pulkit actively contribute</b> kar rahe hain, "
            "lekin documentation/presentation ke liye original 6-role structure preserve hai. "
            "Is report mein kaam role-wise explain kiya gaya hai, taaki koi bhi member apna section judges ko samjha sake.",
            title="Team operating note",
        )
    )
    story.append(spacer(8))
    story.append(
        kv_table(
            [
                ("Repository", "SIH26153-Network-Attack-Forecasting"),
                ("Branch", "main  ·  origin/main ke saath up to date"),
                ("HEAD", "897ede8 — Add Priyanshi Day 3 reproducibility audit"),
                ("Working tree", "CLEAN"),
                ("Report type", "Internal Day 3 progress + next-stage roadmap"),
                ("Language", "Simple Hinglish  ·  technical terms ke saath"),
            ]
        )
    )
    return story


def toc_story():
    s = []
    s += heading(1, "Table of Contents", "toc")
    s.append(bullets([
        "1.  Is document ka purpose",
        "2.  Executive summary",
        "3.  Factual consistency / contradiction notes",
        "4.  Day 3 overall status",
        "5.  Day 2 baseline vs Day 3 progress",
        "6.  Multi-Horizon TEST classification results",
        "7.  Operational early warning",
        "8.  Baseline / model comparison",
        "9.  H500 investigation",
        "10. Backend + frontend integration",
        "11. Browser runtime verification",
        "12. Cybersecurity / MITRE ATT&amp;CK interpretation",
        "13. Reproducibility + pipeline audit",
        "14. Important limitations",
        "15–20.  Six member sections",
        "21. Next stage / Day 4 roadmap",
        "22. SIH PPT / presentation preparation",
        "23. Final project status + next milestone",
    ]))
    return s


def purpose_story():
    s = []
    s += heading(1, "1. Is document ka purpose", "purpose")
    s.append(
        P(
            "Day 2 pe model, evaluator, backend foundation, aur data validation lock ho chuke the. "
            "Day 3 ka sawal ye tha: kya ye components independently audit + runtime-verify ho sakte hain, "
            "bina metrics chhupaye, bina TEST pe tune kiye, bina fake completeness ke?",
            "body",
        )
    )
    s.append(bullets([
        "Har member Day 3 contribution 30 seconds mein explain kar sake.",
        "Verified numbers ek hi jagah hon — PPT aur baat match kare.",
        "COMPLETED / VERIFIED / PARTIAL / LIMITATION / NEXT STAGE mix na hon.",
        "Day 2 kaam ko Day 3 ka naya result mat samajhna.",
    ]))
    return s


def exec_story():
    s = []
    s += heading(1, "2. Executive summary", "exec")
    s.append(
        callout(
            "day3",
            "Day 3 complete hai. Project ab “model + components exist” se aage badh ke "
            "<b>pipeline, evaluation logic, cybersecurity interpretation, aur real offline demo</b> "
            "independently audit/verify ho chuke hain.",
        )
    )
    s.append(
        P(
            "Model sirf ye nahi bata raha ki abhi attack hai ya nahi. "
            "Wo last 100 flows dekh kar next 50 / 100 / 200 / 500 flows par future attack-state ke chances predict karta hai. "
            "Day 3 ne is story ko MITRE context, H500 ki honest limitation, reproducibility gates, "
            "aur browser-verified Attack Forecast demo se joda.",
            "body",
        )
    )
    s.append(P("Day 3 pe kya lock hua", "h2"))
    s.append(bullets([
        "<b>Pranshu:</b> MITRE ATT&amp;CK DDoS mapping — T1498 / TA0040; T1498.001 only where behaviour supports; T1498.002 not assigned. File: DOCS/mitre-attack-ddos-mapping.md (commit 2df7d44).",
        "<b>Pragati:</b> Pipeline/tensor integrity re-audit — shapes (13515/2703/2703, 100, 68), 18,921 metadata rows, splits 1–15 / 16–18 / 19–21, 68 features.",
        "<b>Priyanshi:</b> Internal pipeline reproducibility PASS; fresh-clone PARTIAL. File: ml/reports/priyanshi_day3_reproducibility_automation_audit.txt (commit 897ede8).",
        "<b>Riddhi:</b> Evaluator protocol re-confirmed. Older LR vs GRU V1 vs GRU V2 now defensible apples-to-apples (273 windows). Multi-Horizon alag configuration hai — ek table mein merge mat karo.",
        "<b>Ankita:</b> H500 FAR investigation COMPLETE. Operating point 0.35 validation-selected hai. TEST pe retune nahi. H500 exploratory/research horizon.",
        "<b>Pulkit:</b> Real FastAPI + Attack Forecast runtime + npm build PASS + browser localhost:5173/forecast verification.",
    ]))
    s.append(
        callout(
            "limitation",
            "H500 FAR = <b>0.9933</b>. Ranking signal hai (ROC-AUC 0.7644, PR-AUC 0.8423), lekin current operating point low-FAR alerting ke liye unsuitable hai. "
            "Operational narrative H50/H100/H200 prioritize kare.",
        )
    )
    return s


def qc_story():
    s = []
    s += heading(1, "3. Factual consistency notes", "qc")
    s.append(
        P(
            "PDF se pehle git, reports, backend, frontend, aur Day 3 checkpoint cross-check kiye. "
            "Neeche wala point ek <b>asli contradiction</b> hai — silently ek version choose nahi kiya gaya.",
            "body",
        )
    )
    s.append(P("3.1 CONTRADICTION — episode attack-start examples", "h2"))
    s.append(
        P(
            "Day 3 prompt ke operational examples ye numbers dete hain: "
            "Episode 19 attack <b>36910</b> / warning 36709 / lead 201; "
            "Episode 20 attack <b>38910</b> / warning 38799 / lead 111; "
            "Episode 21 attack <b>40910</b> / warning 40909 / lead 1.",
            "body",
        )
    )
    s.append(
        P(
            "Wahi prompt ke browser section mein Episode 20 attack start = <b>39000</b> likha hai. "
            "Repo ki Multi-Horizon early-warning report "
            "(<b>ml/reports/multihorizon_early_warning_report.txt</b>, commit d3c663e ke baad) "
            "verified metadata use karti hai: Episode 19 = <b>37000</b>, 20 = <b>39000</b>, 21 = <b>41000</b>. "
            "Backend demo bhi Episode 20 start 39000 se match karta hai.",
            "body",
        )
    )
    s.append(
        P(
            "36910 / 38910 / 40910 <b>GRU V1</b> early-warning report mein hain "
            "(<b>ml/reports/gru_early_warning_report.txt</b>). Ye Multi-Horizon TEST examples nahi hain.",
            "body",
        )
    )
    s.append(
        callout(
            "warning",
            "Dono sources neeche <b>alag labeled tables</b> mein hain. Unhe merge mat karo. "
            "Multi-Horizon / demo ke liye 37000 / 39000 / 41000 authoritative hain. "
            "V1 examples ko MH result mat bolo.",
            title="Contradiction — not silently resolved",
        )
    )
    s.append(P("3.2 Jo contradiction nahi, documentation gap hai", "h2"))
    s.append(bullets([
        "<b>H500 threshold trade-off TEST numbers</b> (0.40 / 0.45 / 0.50) dedicated committed report file mein nahi mile. Priyanshi Day 3 audit confirm karta hai ki H500 operating-point alag se investigate hua. Numbers Day 3 checkpoint se hain; repo unhe contradict nahi karta. Source labeled rahega.",
        "<b>Riddhi protocol audit</b> ka alag Day 3 report file git mein nahi hai. LR / GRU V1 / GRU V2 existing reports 273 windows, 30 positive / 243 negative share karte hain. Checkpoint kehta hai protocol ab apples-to-apples verified hai. Dedicated file na hone ko fake file se fill nahi kiya.",
        "<b>Pragati Day 3</b> ka alag naya report file nahi; findings existing tensor/window validation reports + Day 3 checkpoint se match karte hain.",
        "<b>requirements.txt / dependency manifest</b> repo mein nahi hai. Priyanshi audit yahi kehta hai. Fake manifest nahi banaya.",
    ]))
    s.append(P("3.3 Jo claim nahi kiya jayega", "h2"))
    s.append(bullets([
        "/traffic-stream, /alerts, /model-stats real endpoints nahi.",
        "Poora dashboard real-data driven nahi.",
        "GRU MITRE ID predict nahi karta.",
        "Perfect leakage-free preprocessing nahi.",
        "H500 operationally reliable nahi.",
        "Live production monitoring nahi — offline demonstrator.",
        "Is PDF ko already committed mat samajhna jab tak git commit na ho.",
    ]))
    return s


def status_story():
    s = []
    s += heading(1, "4. Day 3 overall status", "status")
    s.append(simple_table(
        ["Member", "Day 3 completed scope", "Status", "Honest leftover"],
        [
            ["Pranshu", "MITRE T1498 mapping document", "100% DONE", "T1498.001 not universal; T1498.002 not assigned"],
            ["Pulkit", "Runtime + build + browser demo verify", "100% DONE", "Other SOC pages still mock"],
            ["Pragati", "Pipeline/tensor/split integrity re-audit", "100% DONE", "Global-median leakage still documented"],
            ["Ankita", "H500 FAR investigation, no cosmetic retrain", "COMPLETE", "H500 exploratory only"],
            ["Riddhi", "Evaluator protocol + older 273-window comparison", "100% DONE", "MH vs single-horizon still different setup"],
            ["Priyanshi", "Internal repro PASS; fresh-clone PARTIAL", "100% DONE", "No deps manifest / runner / README ML section"],
        ],
        col_widths=[0.14 * CONTENT_W, 0.32 * CONTENT_W, 0.16 * CONTENT_W, 0.38 * CONTENT_W],
        header_left=True,
    ))
    s.append(P("Day 3 workstreams complete/audited. Next stage alag labelled hai.", "caption"))
    return s


def progress_story():
    s = []
    s += heading(1, "5. Day 2 baseline vs Day 3 technical progress", "progress")
    s.append(P("Day 2 ne foundation diya. Day 3 ne usi foundation ko audit + interpret + runtime-verify kiya. Restart nahi hua.", "body"))
    s.append(simple_table(
        ["Layer", "Day 2 baseline (already done)", "Day 3 added"],
        [
            ["Model", "MH GRU trained, thresholds locked", "H500 operating-point investigation; no retrain"],
            ["Evaluation", "TEST metrics + early-warning evaluator", "Protocol audit; LR/V1/V2 273-window comparability"],
            ["Data", "Windows 18 OK; tensors 59 OK", "Pipeline/script hard-gate re-audit"],
            ["Repro", "Seed 42 rerun + matching hashes", "Internal PASS; fresh-clone PARTIAL documented"],
            ["Cyber", "Attack-pattern narrative; MITRE pending", "Verified T1498 mapping document"],
            ["System", "4 real APIs + Attack Forecast wired", "Browser runtime + production build verified"],
        ],
        col_widths=[0.16 * CONTENT_W, 0.42 * CONTENT_W, 0.42 * CONTENT_W],
        header_left=True,
    ))
    s.append(spacer(4))
    s.append(flow_diagram(
        ["CICIDS2017", "Working set", "68 features", "100-flow windows"],
        "End-to-end forecasting pipeline",
    ))
    s.append(flow_diagram(
        ["MH GRU", "H50 / H100 / H200 / H500", "Risk / forecast", "MITRE context"],
    ))
    s.append(flow_diagram(
        ["TRAIN", "VALIDATION thresholds", "TEST once", "Metrics + early warning"],
        "Evaluation flow — TEST pe threshold tune nahi",
    ))
    s.append(flow_diagram(
        ["Past 100 flows", "Future 50", "Future 100", "Future 200 / 500"],
        "Forecasting concept",
    ))
    return s


def metrics_story():
    s = []
    s += heading(1, "6. Multi-Horizon TEST classification results", "metrics")
    s.append(P(
        "Ye Day 2 se locked TEST numbers hain. Day 3 ne unhe change nahi kiya. "
        "Precision/Recall/F1/Accuracy thresholded predictions se. ROC-AUC/PR-AUC probabilities se. "
        "FAR = FP / (FP + TN). Thresholds VALIDATION se: 0.30 / 0.55 / 0.45 / 0.35.",
        "body",
    ))
    s.append(simple_table(
        ["Horizon", "Precision", "Recall", "F1", "Accuracy", "ROC-AUC", "PR-AUC", "FAR"],
        [
            ["H50", "0.2573", "1.0000", "0.4093", "0.8398", "0.9455", "0.3681", "0.1696"],
            ["H100", "0.4941", "0.9833", "0.6577", "0.8864", "0.9492", "0.7019", "0.1257"],
            ["H200", "0.7572", "0.8317", "0.7927", "0.9034", "0.9225", "0.7726", "0.0761"],
            ["H500", "0.5566", "1.0000", "0.7151", "0.5579", "0.7644", "0.8423", "0.9933"],
        ],
        col_widths=[CONTENT_W / 8] * 8,
        highlight_last=True,
    ))
    s.append(P("Source: ml/reports/multihorizon_gru_training_report.txt. H500 row highlighted.", "caption"))
    s.append(simple_table(
        ["Horizon", "TN", "FP", "FN", "TP", "Positives", "Negatives"],
        [
            ["H50", "2120", "433", "0", "150", "150", "2,553"],
            ["H100", "2101", "302", "5", "295", "300", "2,403"],
            ["H200", "1943", "160", "101", "499", "600", "2,103"],
            ["H500", "8", "1195", "0", "1500", "1,500", "1,203"],
        ],
        highlight_last=True,
    ))
    s.append(callout(
        "limitation",
        "H500: 2703 TEST rows; target 0=1203, 1=1500; predicted 0=8, 1=2695; FP=1195; TN=8; TP=1500; FN=0; FAR=0.9933. "
        "Recall 1.0 isliye kyunki almost har window ATTACK predict ho rahi hai. Operational alerting ke liye unreliable.",
    ))
    return s


def early_story():
    s = []
    s += heading(1, "7. Operational early warning", "early")
    s.append(P(
        "Early warning ka matlab sirf ye nahi hai ki model ne attack ko positive bola. "
        "Humein dekhna hota hai ki warning actual attack start hone se <b>PEHLE</b> aayi ya nahi. "
        "Warning at/after attack start positive-lead nahi maani jaati.",
        "body",
    ))
    s.append(callout(
        "finding",
        "<b>“First warning true-positive forecast thi”</b> aur <b>“warning attack start se pehle aayi”</b> "
        "do alag concepts hain. Merge mat karo. MH report: H50 0/3, H100 1/3, H200 1/3, H500 0/3 first warnings also true-positive forecasts.",
    ))
    s.append(simple_table(
        ["Horizon", "Warning rate", "Mean lead", "Median lead", "≥50 success", "≥100 success", "FAR"],
        [
            ["H50", "100%", "198.7", "202", "100%", "66.7%", "0.1696"],
            ["H100", "100%", "329.3", "189", "100%", "66.7%", "0.1257"],
            ["H200", "100%", "341", "207", "100%", "66.7%", "0.0761"],
            ["H500", "100%", "901", "901", "100%", "100%", "0.9933"],
        ],
        highlight_last=True,
    ))
    s.append(P("Sample = 3 TEST episodes only. Lead-time success genuinely early warnings par.", "caption"))
    s.append(P("7.1 Multi-Horizon H50 examples (authoritative for MH / demo)", "h2"))
    s.append(simple_table(
        ["Episode", "Attack start", "H50 first warning", "Lead", "H50 probability"],
        [
            ["19", "37000", "36704", "296", "0.372099"],
            ["20", "39000", "38798", "202", "0.321912"],
            ["21", "41000", "40902", "98", "0.324796"],
        ],
    ))
    s.append(P("Source: ml/reports/multihorizon_early_warning_report.txt. n=3, generalize mat karo.", "caption"))
    s.append(P("7.2 GRU V1 examples (alag evaluator — mix na karo)", "h2"))
    s.append(simple_table(
        ["Episode", "Attack start", "Warning", "Lead"],
        [
            ["19", "36910", "36709", "201"],
            ["20", "38910", "38799", "111"],
            ["21", "40910", "40909", "1"],
        ],
    ))
    s.append(P("Source: ml/reports/gru_early_warning_report.txt (GRU V1, threshold 0.65). Ye MH numbers nahi hain.", "caption"))
    s.append(callout(
        "limitation",
        "H500 warning rate 100% aur lead 901 dikh sakta hai, lekin FAR 99.33% ke saath ye operationally unreliable hai. "
        "“Best early warning” mat bolo.",
    ))
    return s


def compare_story():
    s = []
    s += heading(1, "8. Baseline / model comparison", "compare")
    s.append(P(
        "Day 3 protocol audit ke baad purana single-horizon comparison defensible hai, "
        "kyunki teenon reports same TEST size share karte hain. "
        "Multi-Horizon ko isi table mein dump mat karo.",
        "body",
    ))
    s.append(P("Verified apples-to-apples baseline comparison", "h2"))
    s.append(simple_table(
        ["Model", "F1", "ROC-AUC", "PR-AUC", "FAR", "TEST windows"],
        [
            ["Logistic Regression", "0.4091", "0.8514", "0.3014", "0.1646", "273"],
            ["GRU V1", "0.6667", "0.9444", "0.5370", "0.1235", "273"],
            ["GRU V2", "0.6818", "0.9329", "0.5420", "0.1152", "273"],
        ],
    ))
    s.append(P(
        "Shared protocol (existing reports se verified): 273 TEST windows, 100-flow observation, 68 features, "
        "episode-based split, 30 positive / 243 negative. LR = window mean+std + logistic. "
        "GRU V1/V2 = sequence GRU, next-100 target. Dedicated Day 3 audit file git mein nahi; numbers inteen reports se hain.",
        "caption",
    ))
    s.append(P("Multi-Horizon GRU horizon-specific evaluation (alag configuration)", "h2"))
    s.append(simple_table(
        ["Horizon", "F1", "ROC-AUC", "PR-AUC", "FAR", "TEST windows"],
        [
            ["H50", "0.4093", "0.9455", "0.3681", "0.1696", "2,703"],
            ["H100", "0.6577", "0.9492", "0.7019", "0.1257", "2,703"],
            ["H200", "0.7927", "0.9225", "0.7726", "0.0761", "2,703"],
            ["H500", "0.7151", "0.7644", "0.8423", "0.9933", "2,703"],
        ],
        highlight_last=True,
    ))
    s.append(callout(
        "presentation",
        "PPT mein do tables rakho. “MH H200 F1 0.79 isliye V2 se better hai” — aisa direct rank mat ghoshit karo, "
        "kyunki targets/window counts alag hain.",
    ))
    return s


def h500_story():
    s = []
    s += heading(1, "9. H500 investigation (Ankita — Day 3)", "h500")
    s.append(P(
        "Purpose cosmetic TEST metric improve karna nahi tha. "
        "Purpose tha: H500 FAR 0.9933 ko samajhna, bina TEST pe threshold tune kiye, bina model retrain kiye.",
        "body",
    ))
    s.append(kv_table([
        ("TEST rows", "2,703"),
        ("Target 0 / 1", "1,203 / 1,500"),
        ("Predicted 0 / 1", "8 / 2,695"),
        ("TN / FP / FN / TP", "8 / 1,195 / 0 / 1,500"),
        ("Selected threshold", "0.35  (VALIDATION F1 only)"),
        ("ROC-AUC / PR-AUC", "0.7644 / 0.8423"),
        ("Current FAR", "0.9933"),
    ]))
    s.append(P("TEST operating-point trade-off (Day 3 investigation; TEST pe selected threshold nahi badla)", "h2"))
    s.append(simple_table(
        ["Threshold", "Precision", "Recall", "F1", "FAR", "Note"],
        [
            ["0.35 (selected)", "0.5566", "1.0000", "0.7151", "0.9933", "Current locked point"],
            ["0.40", "0.6372", "0.8113", "0.7138", "0.5761", "Exploratory only"],
            ["0.45", "0.9372", "0.4573", "0.6147", "0.0382", "Exploratory only"],
            ["0.50", "0.9886", "0.4053", "0.5749", "0.0058", "Exploratory only"],
        ],
        col_widths=[0.20 * CONTENT_W, 0.14 * CONTENT_W, 0.14 * CONTENT_W, 0.14 * CONTENT_W, 0.14 * CONTENT_W, 0.24 * CONTENT_W],
        header_left=True,
    ))
    s.append(P(
        "Ye trade-off dikhata hai ki FAR ghatane ke liye recall toot-ta hai. "
        "0.45/0.50 ko naya official threshold mat banao — wo TEST dekh ke choose lagenga. "
        "Locked point 0.35 hi hai.",
        "caption",
    ))
    s.append(callout(
        "verified",
        "H500 mein genuine ranking signal hai, lekin current operating point reliable low-FAR alert ke liye unsuitable hai. "
        "Treat as long-range exploratory/research horizon. Operational story: H50/H100/H200.",
    ))
    s.append(callout(
        "next",
        "Possible future (labelled): calibration, temporal robustness, improved operating-point selection on VALIDATION. "
        "Retrain only with principled methodology. TEST pe tune nahi.",
    ))
    return s


def system_story():
    s = []
    s += heading(1, "10. Backend + frontend integration", "system")
    s.append(P(
        "Day 2 ne FastAPI wiring diya. Day 3 ne runtime, TypeScript/Vite production build, aur real page contract verify kiya. "
        "Naye fake endpoints nahi add kiye.",
        "body",
    ))
    s.append(kv_table([
        ("API", "FastAPI + Uvicorn"),
        ("Python / Torch", "3.13.15  ·  PyTorch 2.13.0+cpu"),
        ("FastAPI / Uvicorn", "0.141.1  ·  0.52.4"),
        ("Frontend", "React / Vite / TypeScript"),
        ("Inference class", "MultiHorizonGRUInference"),
        ("Checkpoint", "ml/models/multihorizon_gru.pt"),
        ("Runtime", "CPU / offline · model.eval() · torch.no_grad()"),
        ("Input gate", "exact 100×68, finite values required"),
        ("npm run build", "PASS (TypeScript PASS, Vite production PASS)"),
        ("Non-blocking warning", "Some chunks &gt; 500 kB after minification — failure nahi"),
    ]))
    s.append(simple_table(
        ["Method", "Path", "Status"],
        [
            ["GET", "/health", "REAL"],
            ["GET", "/model-status", "REAL"],
            ["GET", "/demo-sequence", "REAL"],
            ["POST", "/predict", "REAL"],
            ["—", "/traffic-stream, /alerts, /model-stats", "NOT implemented as real APIs"],
        ],
        col_widths=[0.16 * CONTENT_W, 0.40 * CONTENT_W, 0.44 * CONTENT_W],
        header_left=True,
    ))
    s.append(spacer(4))
    s.append(flow_diagram(
        ["AttackForecast.tsx", "GET /demo-sequence", "POST /predict", "PredictionCard"],
        "Real frontend/backend flow",
    ))
    s.append(P("Files: backend/main.py, ml/inference/multihorizon_gru_inference.py, website/src/pages/AttackForecast.tsx, website/src/components/forecast/MultiHorizonPredictionCard.tsx, website/src/types/index.ts, website/src/services/api.ts.", "caption"))
    return s


def browser_story():
    s = []
    s += heading(1, "11. Browser runtime verification", "browser")
    s.append(P(
        "Real frontend localhost:5173/forecast par open hua. Runtime verification PASS. "
        "Ye live packet capture nahi hai — held-out TEST sequence ka offline demo hai.",
        "body",
    ))
    s.append(simple_table(
        ["Field", "Verified value"],
        [
            ["Route", "/forecast"],
            ["Test index / Window", "1691 / 17909"],
            ["Episode", "20"],
            ["Observation flows", "38790–38889 (length 100)"],
            ["Source", "CICIDS2017 held-out TEST sequence"],
            ["H50 / H100 / H200 / H500", "97.9% / 99.5% / 99.5% / 98.2%"],
            ["Predictions", "ATTACK / ATTACK / ATTACK / ATTACK"],
            ["Thresholds", "30% / 55% / 45% / 35%"],
            ["Episode 20 attack start", "flow 39000  — window PRE-ATTACK hai"],
        ],
        col_widths=[0.34 * CONTENT_W, 0.66 * CONTENT_W],
        header_left=True,
    ))
    s.append(callout(
        "presentation",
        "Sequence khud already-attack nahi hai. Attack 39000 par start hota hai; observation 38889 par khatam. "
        "Har horizon ka ground-truth target automatically positive nahi. "
        "Sahi line: model is pre-attack TEST example par four future horizons ke liye positive attack-state likelihood forecast karta hai.",
    ))
    s.append(P("REAL vs MOCK", "h2"))
    s.append(simple_table(
        ["Surface", "Day 3 status"],
        [
            ["Attack Forecast + MultiHorizonPredictionCard", "REAL model inference"],
            ["/health, /model-status, /demo-sequence, /predict", "REAL FastAPI"],
            ["Dashboard, LiveTraffic, ThreatIntelligence, ModelPerformance", "MOCK / simulation-backed"],
            ["Alerts page", "MOCK getAlerts()"],
        ],
        col_widths=[0.52 * CONTENT_W, 0.48 * CONTENT_W],
        header_left=True,
    ))
    return s


def mitre_story():
    s = []
    s += heading(1, "12. Cybersecurity / MITRE ATT&amp;CK interpretation", "mitre")
    s.append(P(
        "Verified file: <b>DOCS/mitre-attack-ddos-mapping.md</b> · commit <b>2df7d44</b>. "
        "Day 2 pe mapping pending thi. Day 3 pe conservative, evidence-level mapping complete hui.",
        "body",
    ))
    s.append(kv_table([
        ("Primary technique", "T1498 — Network Denial of Service"),
        ("Tactic", "Impact / TA0040"),
        ("Impact type", "Availability"),
        ("T1498.001 Direct Network Flood", "Only where observed behaviour supports it"),
        ("T1498.002 Reflection Amplification", "NOT assigned — sufficient evidence nahi"),
        ("Model relationship", "GRU MITRE ID output nahi karta; interpretation layer alag hai"),
    ]))
    s.append(flow_diagram(
        ["Forecast", "Attack-state likelihood", "DDoS interpretation", "MITRE context"],
        "Cybersecurity interpretation flow",
    ))
    s.append(callout(
        "verified",
        "Sahi narrative: forecasting model future attack-state likelihood predict karta hai; "
        "cybersecurity interpretation observed/forecasted behaviour ko ATT&amp;CK context se map karti hai.",
    ))
    s.append(callout(
        "warning",
        "Mat bolo: attacker identity, GRU se direct MITRE-ID prediction, universal T1498.001, complete kill-chain visibility.",
    ))
    return s


def repro_story():
    s = []
    s += heading(1, "13. Reproducibility + pipeline audit", "repro")
    s.append(P(
        "Priyanshi: <b>ml/reports/priyanshi_day3_reproducibility_automation_audit.txt</b> · commit <b>897ede8</b>. "
        "Pragati Day 3: usi pipeline ki data/tensor integrity re-audit.",
        "body",
    ))
    s.append(simple_table(
        ["Check", "Verified value"],
        [
            ["Internal pipeline reproducibility", "PASS"],
            ["Fresh-clone reproducibility", "PARTIAL / hardening required"],
            ["X_train / val / test", "(13515, 100, 68) / (2703, 100, 68) / (2703, 100, 68)"],
            ["Dtype", "float32, finite"],
            ["Metadata rows", "18,921  (multihorizon_sequence_metadata.csv)"],
            ["Splits", "TRAIN 1–15 · VAL 16–18 · TEST 19–21 · no overlap"],
            ["Features", "68 after removing 10 constant columns"],
            ["NaN / Inf after prep", "0 / 0"],
            ["Observation length", "100 flows"],
            ["Forecast boundary", "forecast_start = observation_end + 1"],
        ],
        col_widths=[0.40 * CONTENT_W, 0.60 * CONTENT_W],
        header_left=True,
    ))
    s.append(P("Hard gates (Priyanshi audit)", "h2"))
    s.append(bullets([
        "Feature prep: required columns / remaining NaN / Inf → ValueError, phir output.",
        "Window creation: invalid split, empty output, DDoS-in-observation → ValueError.",
        "Tensor builder: NaN/Inf, shapes, binary labels, metadata count, forecast boundary, observation length, split/overlap — fail par tensors write nahi.",
        "Training: tensor shapes, label lengths, test metadata alignment, TRAIN-only weights, VAL-only thresholds, TEST isolation, checkpoint required.",
    ]))
    s.append(callout(
        "limitation",
        "Fresh clone aaj complete reproduce nahi kar sakta bina extra knowledge ke: no Python dependency manifest, "
        "no complete dataset setup guide, no complete README ML reproduction section, no central pipeline runner. "
        "Fake requirements.txt is report ke liye nahi banaya.",
    ))
    s.append(P("Preprocessing leakage caveat (Day 2 se retained)", "h2"))
    s.append(callout(
        "warning",
        "Pipeline mein preprocessing-statistics leakage risk hai kyunki median statistics Inf→NaN ke baad globally, split se pehle compute hote hain. "
        "Held-out TEST rows ko imputation ki zaroorat nahi padi, isliye unke existing feature values is issue se directly change nahi hue. "
        "Limitation documented hai; future pipeline revision mein harden karna hai. Perfectly leakage-free mat bolo. "
        "Sirf is issue ki wajah se retraining automatically required — aisa mat bolo.",
    ))
    return s


def limits_story():
    s = []
    s += heading(1, "14. Important limitations / honest findings", "limits")
    s.append(bullets([
        "H500 FAR 0.9933 — operationally unreliable at locked threshold 0.35.",
        "Early-warning n=3 TEST episodes — large-sample claim nahi.",
        "MH vs LR/GRU V1/V2 alag evaluation configurations.",
        "Global median imputation leakage risk (TEST values directly unaltered).",
        "Fresh-clone reproducibility PARTIAL.",
        "Dashboard majority still mock.",
        "Offline demonstrator, live SOC nahi.",
        "MITRE mapping interpretation layer hai, model output nahi.",
        "Episode attack-start numbers V1 vs MH mix nahi karne.",
        "No attacker attribution / complete kill chain.",
    ]))
    return s


def member_pranshu():
    s = [PageBreak(), member_banner("PRANSHU", "Cybersecurity / Network Analysis / Attack Intelligence", "Day 3: 100% DONE")]
    s += heading(1, "15. Pranshu — Day 3 work + next responsibilities", "m_pranshu")
    s.append(P("A. Role", "h2"))
    s.append(P("Forecast ko defence language dena: DDoS behaviour, attack-stage, MITRE context, detection vs forecasting.", "body"))
    s.append(P("B. Day 3 objective", "h2"))
    s.append(P("Day 2 pe mapping pending thi. Day 3 pe evidence-backed MITRE document, bina overclaim ke.", "body"))
    s.append(P("C. Actually complete", "h2"))
    s.append(P("DOCS/mitre-attack-ddos-mapping.md, commit 2df7d44. T1498 / TA0040 / Availability. T1498.001 conditional. T1498.002 not assigned. Confirmed vs not-claimed lists. Presentation wording. Predictive cyber-defence takeaway.", "body"))
    s.append(P("D. Simple Hinglish", "h2"))
    s.append(P(
        "Model T1498 number nahi thookta. Wo kehta hai: future DDoS-state ke chances kitne hain. "
        "Analyst layer kehta hai: ye scenario Network Denial of Service (T1498) ke under aata hai, Impact tactic, availability hit. "
        "Direct flood dikhe to T1498.001. Reflection/amplification ka evidence nahi, isliye T1498.002 nahi.",
        "body",
    ))
    s.append(P("E. Files", "h2"))
    s.append(bullets(["DOCS/mitre-attack-ddos-mapping.md", "DOCS/attack-patterns-and-traffic-signatures.md (Day 2 baseline)", "Git 2df7d44"]))
    s.append(P("F–G. Why it matters + remember", "h2"))
    s.append(P("Judges ko “F1 0.79” se pehle story chahiye. Yaad: interpretation layer; no attribution; H500 ko MITRE success mat banao; demo pre-attack hai.", "body"))
    s.append(P("H–I. Next", "h2"))
    s.append(P("Explainability copy: input pattern → temporal state → probability → horizon → MITRE context. 6-slide PPT ka cyber slide. Expected: 1-page judge script + allowed/not-allowed claims list.", "body"))
    s.append(P("J–K. Q&amp;A", "h2"))
    s.extend(qa_block([
        ("MITRE mapping ho gayi?", "Haan, Day 3 document complete hai. Primary T1498. T1498.001 sirf jab behaviour support kare. T1498.002 assigned nahi."),
        ("Model MITRE ID predict karta hai?", "Nahi. Model future DDoS likelihood. Mapping interpretation layer hai."),
        ("Detection aur forecasting?", "Detection: abhi attack hai? Forecasting: aage horizon mein attack-state ke chances."),
        ("Attacker kaun hai?", "Hum attribution nahi karte."),
        ("Kill chain poora dikhta hai?", "Nahi. Hum DDoS-onset transition tak interpret karte hain."),
        ("Demo par 4/4 ATTACK matlab T1498 confirm?", "Nahi. Wo forecast probabilities hain, technique classification nahi."),
        ("H500 901 lead ko MITRE early-warning bolo?", "Nahi. FAR 99.33% hai."),
    ]))
    return s


def member_pulkit():
    s = [PageBreak(), member_banner("PULKIT", "Web Dashboard + Backend/API + System Integration", "Day 3: 100% DONE")]
    s += heading(1, "16. Pulkit — Day 3 work + next responsibilities", "m_pulkit")
    s.append(P("A. Role", "h2"))
    s.append(P("Trained checkpoint ko demonstrable offline system banana: FastAPI, frontend contract, Attack Forecast page.", "body"))
    s.append(P("B. Day 3 objective", "h2"))
    s.append(P("Day 2 wiring ko runtime + production-build + browser se verify karna. Fake completeness nahi.", "body"))
    s.append(P("C. Completed", "h2"))
    s.append(P(
        "Four real endpoints confirmed. MultiHorizonGRUInference CPU/eval/no_grad, 100×68 + finite checks, checkpoint thresholds. "
        "AttackForecast: getDemoSequence → GET /demo-sequence → predict → POST /predict → card. "
        "npm run build PASS; TS PASS; Vite PASS; 500kB chunk warning non-blocking. "
        "Browser /forecast: 97.9 / 99.5 / 99.5 / 98.2, all ATTACK, pre-attack episode 20 window.",
        "body",
    ))
    s.append(P("D. Simple Hinglish", "h2"))
    s.append(P("Frontend 100×68 numbers bhejta hai. Backend GRU se 4 probabilities nikalta hai, validation thresholds se 0/1. Demo sequence TEST tensor ka fixed index 1691 hai, isliye offline repeatable hai.", "body"))
    s.append(P("E. Files", "h2"))
    s.append(bullets(["backend/main.py", "ml/inference/multihorizon_gru_inference.py", "website/src/pages/AttackForecast.tsx", "website/src/components/forecast/MultiHorizonPredictionCard.tsx", "website/src/services/api.ts", "website/src/types/index.ts"]))
    s.append(P("F–G. Why + remember", "h2"))
    s.append(P("Bina verified demo ke judges reports hi dekhenge. Yaad: 4 real APIs only; Attack Forecast real; baaki mock; demo pre-attack; chunk warning failure nahi.", "body"))
    s.append(P("H–I. Next", "h2"))
    s.append(P("Decide which mock surfaces actually need real APIs for final demo. Real vs mock labels. Judge flow: health → model-status → demo-sequence → predict → explanation. Deliverable: demo choreography + mock/real map.", "body"))
    s.append(P("J–K. Q&amp;A", "h2"))
    s.extend(qa_block([
        ("Kaunse real APIs hain?", "GET /health, GET /model-status, GET /demo-sequence, POST /predict."),
        ("Dashboard live hai?", "Poora nahi. /forecast real model. Dashboard/LiveTraffic/ModelPerformance mock."),
        ("Build fail to nahi hua?", "npm run build PASS. 500kB chunk warning non-blocking."),
        ("Demo kahan se aata hai?", "Held-out TEST index 1691, window 17909, episode 20, flows 38790–38889."),
        ("Ye already attack hai?", "Nahi. Attack start 39000. Window pre-attack hai."),
        ("GPU chahiye?", "Nahi. CPU inference."),
        ("Agar 100×68 na ho?", "POST /predict 422. NaN/Inf reject."),
    ]))
    return s


def member_pragati():
    s = [PageBreak(), member_banner("PRAGATI", "Data Engineering / Dataset Analysis / Temporal Validation", "Day 3: 100% DONE")]
    s += heading(1, "17. Pragati — Day 3 work + next responsibilities", "m_pragati")
    s.append(P("A. Role", "h2"))
    s.append(P("Data ko model-safe temporal windows banana aur leakage/split integrity check karna.", "body"))
    s.append(P("B–C. Day 3", "h2"))
    s.append(P(
        "Core scripts re-audited: create_ddos_working_set.py, prepare_ddos_features.py, "
        "create_multihorizon_forecasting_windows.py, build_multihorizon_sequence_tensors.py. "
        "Tensors float32 finite; metadata 18,921; columns window_id through y500; splits 1–15/16–18/19–21; "
        "68 features; 10 constants removed; NaN=0 Inf=0; forecast starts after observation; length 100.",
        "body",
    ))
    s.append(P("D. Simple Hinglish", "h2"))
    s.append(P(
        "Raw CICIDS ko seedha model mein nahi dalte. Episodes banate hain, 100-flow past window, future horizon targets. "
        "Split episode-level hai. Observation ke andar DDoS allowed nahi. "
        "Median abhi bhi split se pehle global hai — risk documented, TEST rows impute nahi hue.",
        "body",
    ))
    s.append(P("E. Files", "h2"))
    s.append(bullets([
        "ml/scripts/create_ddos_working_set.py, prepare_ddos_features.py",
        "ml/scripts/create_multihorizon_forecasting_windows.py, build_multihorizon_sequence_tensors.py",
        "ml/scripts/validate_multihorizon_windows.py, validate_multihorizon_sequence_tensors.py",
        "ml/reports/multihorizon_validation_report.txt, multihorizon_tensor_validation_report.txt",
    ]))
    s.append(P("F–G. Why + remember", "h2"))
    s.append(P("Galat split = saare metrics bekaar. Yaad: 42k working set ≠ 5k sample audit; TEST 19–21; leakage caveat; observation DDoS = 0.", "body"))
    s.append(P("H–I. Next", "h2"))
    s.append(P("Explainability ke liye 68-feature judge-readable pack. Future: TRAIN-only median design (implement tabhi jab team decide kare). Deliverable: split/leakage one-pager.", "body"))
    s.append(P("J–K. Q&amp;A", "h2"))
    s.extend(qa_block([
        ("Split kaise hai?", "Episode-wise. TRAIN 1–15, VAL 16–18, TEST 19–21. Overlap nahi."),
        ("Tensor shape?", "(N, 100, 68). Train 13515, val/test 2703. float32 finite."),
        ("68 features kaise?", "10 constant columns hataaye. Metadata X mein nahi."),
        ("Leakage?", "Global median split se pehle. TEST ko impute nahi karna pada. Perfectly leakage-free nahi kahenge."),
        ("Observation mein attack?", "Validation: observation DDoS = 0. Forecast observation ke baad start."),
        ("Windows kitni?", "18,921 metadata rows, 901 per episode × 21."),
        ("dataset_audit_report.txt 42k hai?", "Nahi. Wo 5,000-row sample audit hai. Mix mat karo."),
    ]))
    return s


def member_ankita():
    s = [PageBreak(), member_banner("ANKITA", "ML / Multi-Horizon GRU", "Day 3: COMPLETE")]
    s += heading(1, "18. Ankita — Day 3 work + next responsibilities", "m_ankita")
    s.append(P("A. Role", "h2"))
    s.append(P("Multi-Horizon GRU owner: shared encoder + four future heads.", "body"))
    s.append(P("B. Day 3 objective", "h2"))
    s.append(P("H500 FAR 0.9933 ko investigate karna — cosmetic fix nahi, TEST retune nahi, silent retrain nahi.", "body"))
    s.append(P("C. Completed", "h2"))
    s.append(P(
        "Prediction distribution, target-wise probabilities, threshold trade-offs, VAL vs TEST shift implications, "
        "episode-wise/operational reading. Locked threshold 0.35. Ranking signal present; operating point poor. "
        "Recommendation: H500 exploratory; operational H50/H100/H200.",
        "body",
    ))
    s.append(P("D. Simple Hinglish", "h2"))
    s.append(P(
        "H500 almost saari windows ko ATTACK bol deta hai (2695/2703). Isliye recall 1.0, FAR 0.9933. "
        "Agar threshold 0.50 kar do to FAR 0.0058 ho sakta hai lekin recall 0.4053 — aur ye TEST dekh ke choose karna cheating hogi. "
        "Isliye 0.35 lock, limitation openly.",
        "body",
    ))
    s.append(P("E. Files / sources", "h2"))
    s.append(bullets([
        "ml/scripts/train_multihorizon_gru.py (Day 2 baseline, Day 3 unchanged)",
        "ml/reports/multihorizon_gru_training_report.txt",
        "ml/reports/priyanshi_day3_reproducibility_automation_audit.txt §17 H500 note",
        "Day 3 checkpoint trade-off table (dedicated H500 report file git mein nahi)",
    ]))
    s.append(P("F–G. Why + remember", "h2"))
    s.append(P("Honesty SIH ka defence hai. Yaad: thresholds 0.30/0.55/0.45/0.35; best epoch 1; H200 balanced classification; H500 exploratory; seed 42 CPU.", "body"))
    s.append(P("H–I. Next", "h2"))
    s.append(P("Calibration / VAL-only operating point / temporal robustness — agar team kare to Priyanshi protocol se. Deliverable: written H500 decision already done; next is optional principled experiment, TEST-hidden.", "body"))
    s.append(P("J–K. Q&amp;A", "h2"))
    s.extend(qa_block([
        ("H500 F1 0.7151 achha nahi?", "F1 akela nahi. FAR 0.9933 operational fail hai."),
        ("Threshold TEST pe badla?", "Nahi. 0.35 validation-selected. Trade-off sirf diagnosis."),
        ("Retrain kyun nahi kiya?", "Cosmetic FAR fix ke liye retrain justified nahi."),
        ("ROC-AUC 0.7644 ka matlab?", "Ranking signal hai, lekin 0.35 pe almost sab positive."),
        ("Kaunsa horizon demo mein?", "Operational: H50/H100/H200. H500 research/long-range, limitation ke saath."),
        ("Best epoch 1?", "Day 2 training: val loss epoch 1 ke baad nahi sudhri. Day 3 ne model change nahi kiya."),
        ("Input?", "(100, 68) sequence, 4 heads."),
    ]))
    return s


def member_riddhi():
    s = [PageBreak(), member_banner("RIDDHI", "ML Evaluation / Metrics / Early Warning / Comparison", "Day 3: 100% DONE")]
    s += heading(1, "19. Riddhi — Day 3 work + next responsibilities", "m_riddhi")
    s.append(P("A. Role", "h2"))
    s.append(P("Numbers ki referee: TEST protocol, FAR, early-warning vs classification, fair comparison boundaries.", "body"))
    s.append(P("B–C. Day 3", "h2"))
    s.append(P(
        "Evaluator behaviour re-confirmed: TEST 19–21; VAL thresholds reused; no TEST retune; "
        "thresholded vs probability metrics split; FAR=FP/(FP+TN); early warning only if first warning before attack start; "
        "horizon comparison temporal, not F1 ranking; artifacts unmodified. "
        "Older LR/V1/V2: same 273 windows / 30 pos / 243 neg — apples-to-apples under that protocol. "
        "MH 2703-window horizon-specific eval alag table.",
        "body",
    ))
    s.append(P("D. Simple Hinglish", "h2"))
    s.append(P(
        "Do alag sawal: (1) is window ka future target positive tha kya? — classification. "
        "(2) episode mein pehli warning attack se pehle aayi kya? — early warning. "
        "Pehli warning true-positive forecast ho, ye teesra alag count hai.",
        "body",
    ))
    s.append(P("E. Files", "h2"))
    s.append(bullets([
        "ml/scripts/evaluate_multihorizon_early_warning.py",
        "ml/reports/multihorizon_early_warning_report.txt",
        "ml/reports/forecasting_baseline_report.txt, gru_forecasting_report.txt, gru_forecasting_v2_report.txt",
        "ml/reports/gru_early_warning_report.txt — V1 examples only",
    ]))
    s.append(P("F–G. Why + remember", "h2"))
    s.append(P("Overclaim se project tut-ta hai. Yaad: n=3; V1 36910 vs MH 37000 mix nahi; two comparison tables; H500 FAR visible.", "body"))
    s.append(P("H–I. Next", "h2"))
    s.append(P("PPT appendix: two tables + glossary (FAR, lead, true-positive-first-warning). Deliverable: judge-facing metric legend.", "body"))
    s.append(P("J–K. Q&amp;A", "h2"))
    s.extend(qa_block([
        ("TEST pe threshold tune?", "Nahi. 0.30/0.55/0.45/0.35 validation-selected."),
        ("FAR?", "FP/(FP+TN). H500 = 0.9933."),
        ("100% warning rate perfect?", "Nahi. 3/3 episodes pe koi early warning. Quality FAR/precision se."),
        ("V1 201-flow example MH hai?", "Nahi. Wo GRU V1 report hai. MH episode 19 attack 37000, H50 lead 296."),
        ("LR vs GRU fair?", "Day 3: haan, 273-window single-horizon protocol. MH usme mix nahi."),
        ("Evaluator ne model change kiya?", "Nahi. Read-only."),
        ("True-positive first warning vs early?", "Alag. Early = before attack start. True-positive forecast = us window ka target bhi 1."),
    ]))
    return s


def member_priyanshi():
    s = [PageBreak(), member_banner("PRIYANSHI", "Python Automation / Reproducibility / Experiment Reliability", "Day 3: 100% DONE")]
    s += heading(1, "20. Priyanshi — Day 3 work + next responsibilities", "m_priyanshi")
    s.append(P("A. Role", "h2"))
    s.append(P("Experiment kal dubara chale to same result aaye, aur fresh clone ke gaps honestly dikhein.", "body"))
    s.append(P("B–C. Day 3", "h2"))
    s.append(P(
        "Full script-by-script audit. Internal pipeline PASS. Fresh-clone PARTIAL. "
        "Chain: raw → working set → validate → features → windows → validate → tensors → validate → train → model/preds/report. "
        "Hard gates documented. H500 note: TEST pe FAR mat “fix” karo. No fake dependency files.",
        "body",
    ))
    s.append(P("D. Simple Hinglish", "h2"))
    s.append(P(
        "Internal PASS ka matlab: isi machine/workflow par gates aur seed logic strong hain. "
        "PARTIAL ka matlab: naya clone dataset, packages, aur command order document ke bina atak sakta hai. "
        "Dono status ek saath true hain.",
        "body",
    ))
    s.append(P("E. File", "h2"))
    s.append(bullets(["ml/reports/priyanshi_day3_reproducibility_automation_audit.txt", "Git 897ede8 (current HEAD)"]))
    s.append(P("F–G. Why + remember", "h2"))
    s.append(P("Repro judges ko screenshot se pipeline alag karti hai. Yaad: seed 42 Day 2; Day 3 audit PASS/PARTIAL; no requirements.txt yet; don’t commit raw CICIDS.", "body"))
    s.append(P("H–I. Next", "h2"))
    s.append(P("Hardening (labelled future): dependency manifest, dataset setup doc, README ML section, central runner that orchestrates existing scripts. Optional finite-value check in train script. Deliverable: those docs/runner when team starts Day 4 — not fake-filled now.", "body"))
    s.append(P("J–K. Q&amp;A", "h2"))
    s.extend(qa_block([
        ("Reproducible hai kya?", "Internal pipeline: PASS. Fresh clone: PARTIAL."),
        ("Kya missing hai?", "Dependency manifest, dataset setup guide, README ML section, central runner."),
        ("TEST training mein?", "Nahi. TRAIN weights, VAL thresholds, TEST last."),
        ("H500 FAR script se fix?", "Audit mana karta hai TEST pe threshold change karke."),
        ("Tensors fail hon to?", "Builder RuntimeError, files write nahi."),
        ("Raw data git mein?", "Nahi. Intentionally gitignored."),
        ("Day 2 hash rerun?", "Day 2 PASS. Day 3 ne cosmetic retrain nahi kiya."),
    ]))
    return s


def next_story():
    s = []
    s += heading(1, "21. Next stage / Day 4 roadmap", "next")
    s.append(P("Ye Day 3 future work nahi hai. Day 3 complete hai. Neeche continuation priorities hain.", "body"))
    s.append(simple_table(
        ["#", "Priority", "Who", "Output"],
        [
            ["1", "Explainability (input → state → forecast → MITRE)", "Pranshu + Pragati + Pulkit UI if shown", "Judge-friendly explanation, no fake SHAP claims"],
            ["2", "H500: calibration / VAL operating point / shift", "Ankita + Riddhi; Priyanshi if rerun", "No TEST tune; optional principled experiment"],
            ["3", "Backend only if demo needs it", "Pulkit", "traffic/alerts/stats — only if required"],
            ["4", "Dashboard hardening, real vs mock labels", "Pulkit", "Critical mock replace gradually"],
            ["5", "Offline demo choreography", "Pulkit + Priyanshi + Pranshu copy", "Deterministic judge flow"],
            ["6", "Final SIH PPT — exactly 6 slides", "All six roles", "Simple story + honest limits"],
            ["7", "Presentation rehearsal", "All", "Each person: work, why, limit, next"],
        ],
        col_widths=[0.07 * CONTENT_W, 0.32 * CONTENT_W, 0.28 * CONTENT_W, 0.33 * CONTENT_W],
        header_left=True,
    ))
    s.append(callout("next", "Pehle explainability + 6-slide PPT. H500 ko chhupa ke PPT mat banao."))
    return s


def ppt_story():
    s = []
    s += heading(1, "22. SIH PPT / presentation preparation", "ppt")
    s.append(P("Exactly 6 slides. Technical dump nahi. Offline demonstrator honesty ke saath.", "body"))
    s.append(bullets([
        "1. Problem: late detection vs forecasting need",
        "2. Idea: 100 flows → H50/H100/H200/H500",
        "3. Evidence: episode split, TEST 19–21, H200 balanced, H500 FAR 0.9933 limitation",
        "4. System: real /forecast demo, 4 APIs, pre-attack TEST window",
        "5. Cyber: T1498 interpretation layer, not model output",
        "6. Limits + next: mock pages, leakage caveat, explainability",
    ]))
    s.append(kv_table([
        ("Pranshu", "Forecast → T1498 context. Model MITRE ID nahi bolta."),
        ("Pulkit", "4 real APIs, /forecast live, baaki mock, demo pre-attack."),
        ("Pragati", "Episode split, 100×68, leakage caveat, 0 observation DDoS."),
        ("Ankita", "4-head GRU, VAL thresholds, H500 exploratory."),
        ("Riddhi", "TEST protocol, FAR, early ≠ F1, two comparison tables."),
        ("Priyanshi", "Internal PASS, fresh-clone PARTIAL, seed/gates."),
    ]))
    s.append(callout(
        "presentation",
        "PPT mein mat likho: live production, perfectly leakage-free, all pages real, H500 best, "
        "GRU predicts T1498, attacker ID, 273-vs-2703 as one ranking.",
    ))
    return s


def close_story():
    s = []
    s += heading(1, "23. Final project status + next milestone", "close")
    s.append(P(
        "Day 3 milestone <b>achieved</b>: audited pipeline + honest H500 + MITRE interpretation + "
        "real offline browser demo + clean git checkpoint 897ede8. "
        "Next milestone: 6-slide PPT + explainability + demo choreography.",
        "body",
    ))
    s.append(KeepTogether([simple_table(
        ["Layer", "Day 3 state", "Next milestone"],
        [
            ["Cyber", "T1498 mapping documented", "Judge script + explainability language"],
            ["Data", "Pipeline/tensor gates re-audited", "Optional TRAIN-only median design"],
            ["Model", "H500 investigated, not cosmetically fixed", "Optional VAL-only calibration"],
            ["Eval", "Protocol + 273-window baseline labelled", "Two-table PPT appendix"],
            ["Repro", "Internal PASS / clone PARTIAL", "Manifest + README + runner"],
            ["System", "Browser-verified /forecast", "Mock/real hardening as needed"],
        ],
        col_widths=[0.16 * CONTENT_W, 0.42 * CONTENT_W, 0.42 * CONTENT_W],
        header_left=True,
    )]))
    s.append(spacer(8))
    s.append(callout(
        "day3",
        "Team bottom line: model future horizons forecast karta hai; H200 currently sabse balanced TEST classification; "
        "H500 FAR 0.9933 ke bina mat present karo; Attack Forecast real hai, poora dashboard nahi; "
        "MITRE interpretation hai, model ID nahi; TEST episodes 19–21; demo window pre-attack (episode 20 start 39000).",
        title="Team bottom line",
    ))
    s.append(spacer(8))
    s.append(P("Appendix — locked facts", "h2"))
    s.append(kv_table([
        ("HEAD", "897ede8"),
        ("MITRE file", "DOCS/mitre-attack-ddos-mapping.md"),
        ("Priyanshi audit", "ml/reports/priyanshi_day3_reproducibility_automation_audit.txt"),
        ("Thresholds", "H50 0.30 · H100 0.55 · H200 0.45 · H500 0.35"),
        ("H200 F1 / FAR", "0.7927 / 0.0761"),
        ("H500 FAR", "0.9933"),
        ("Real APIs", "/health · /model-status · /demo-sequence · /predict"),
        ("Browser demo", "H50 97.9% · H100 99.5% · H200 99.5% · H500 98.2% · all ATTACK"),
        ("This PDF source", "DOCS/day3_progress_report/generate_day3_progress_report.py"),
    ]))
    s.append(spacer(8))
    s.append(P("End of Day 3 internal progress report. Next stage isi “next” column se start hoga.", "small"))
    return s


def build_story():
    story = []
    story += cover_story()
    story.append(NextPageTemplate("body"))
    story.append(PageBreak())
    for part in (
        toc_story,
        purpose_story,
        exec_story,
        qc_story,
        status_story,
        progress_story,
        metrics_story,
        early_story,
        compare_story,
        h500_story,
        system_story,
        browser_story,
        mitre_story,
        repro_story,
        limits_story,
        member_pranshu,
        member_pulkit,
        member_pragati,
        member_ankita,
        member_riddhi,
        member_priyanshi,
        next_story,
        ppt_story,
        close_story,
    ):
        story += part()
        story.append(spacer(4))
    return story


def main() -> None:
    init_styles()
    SectionMarker.registry.clear()
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(OUT_PDF),
        pagesize=(PAGE_W, PAGE_H),
        title="SIH26153 Day 3 Progress Report — Internal Team Handoff",
        author="SIH26153 Team",
        subject="Day 3 progress + next-stage roadmap",
    )
    cover_frame = Frame(28 * mm, 24 * mm, PAGE_W - 28 * mm - 16 * mm, PAGE_H - 42 * mm - 24 * mm, id="cover")
    body_frame = Frame(LEFT, BOTTOM + 4 * mm, CONTENT_W, PAGE_H - TOP - BOTTOM - 2 * mm, id="body")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover_frame], onPage=draw_cover),
        PageTemplate(id="body", frames=[body_frame], onPage=draw_header_footer),
    ])
    doc.build(build_story())
    print(f"Wrote {OUT_PDF}")
    print(f"Size bytes: {OUT_PDF.stat().st_size}")


if __name__ == "__main__":
    main()
