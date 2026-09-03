"""
Generate the SIH26153 Day 2 internal team progress report PDF.

Regenerate:
    python docs/day2_progress_report/generate_day2_progress_report.py
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
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pdf_kit import (  # noqa: E402
    BOTTOM,
    CONTENT_W,
    FOREST,
    FOREST_DARK,
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
    heading,
    init_styles,
    kv_table,
    member_banner,
    qa_block,
    simple_table,
    spacer,
    SectionMarker,
)

OUT_PDF = ROOT / "SIH26153-Day2-Progress-Report.pdf"


def cover_story():
    story = [Spacer(1, 42)]
    story.append(P("INTERNAL TEAM HANDOFF  ·  DAY 2 OF BUILD", "cover_kicker"))
    story.append(P("AI based Network Attack Forecasting<br/>from Network Traffic Data", "cover_title"))
    story.append(P("SIH Problem <b>SIH26153</b>  ·  Dataset <b>CICIDS2017</b>  ·  03 September 2026", "cover_sub"))
    story.append(P("Final Day 2 Project Progress Report", "h2"))
    story.append(
        P(
            "Ye document ek public SIH PPT nahi hai. Ye team ke liye knowledge + progress "
            "handoff hai: Day 2 pe kya complete hua, uska technical matlab kya hai, "
            "aur Day 3 pe kisko kya karna hai.",
            "body",
        )
    )
    story.append(spacer(8))

    team = [
        ["Member", "Role", "Day 2"],
        ["Pranshu", "Cybersecurity / Network Analysis / Attack Intelligence", "100% DONE"],
        ["Pulkit", "Web Dashboard + Backend/API + System Integration", "100% DONE"],
        ["Pragati", "Data Engineering / Dataset Analysis / Temporal Validation", "100% DONE"],
        ["Ankita", "ML / Multi-Horizon GRU", "100% DONE"],
        ["Riddhi", "ML Evaluation / Metrics / Early Warning / Comparison", "100% DONE"],
        ["Priyanshi", "Python Automation / Reproducibility / Experiment Reliability", "100% DONE"],
    ]
    data = [[P(c, "cell_head" if i == 0 else "cell") for i, c in enumerate(row)] for row in [team[0]]]
    for row in team[1:]:
        data.append(
            [
                P(f"<b>{row[0]}</b>", "cell"),
                P(row[1], "cell"),
                P(row[2], "cell_c"),
            ]
        )
    t = Table(data, colWidths=[32, 108, 38])
    # widths in mm-ish points: use CONTENT_W
    t = Table(data, colWidths=[38 / 178 * CONTENT_W, 102 / 178 * CONTENT_W, 38 / 178 * CONTENT_W])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), FOREST),
                ("BACKGROUND", (0, 1), (-1, -1), WHITE),
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
    story.append(spacer(10))
    story.append(
        callout(
            "finding",
            "Is report ki source of truth repo files + git history + verified Day 2 checkpoint hai. "
            "Jo cheez files se prove nahi hoti, wo yahan complete kaam ki tarah nahi likhi gayi. "
            "Planned / future work alag se labelled hai.",
            title="Kaise padhein",
        )
    )
    story.append(spacer(10))
    story.append(
        kv_table(
            [
                ("Repository", "SIH26153-Network-Attack-Forecasting"),
                ("Branch", "main  (origin/main ke saath up to date, working tree clean)"),
                ("Latest commit", "40189cb — Add Priyanshi Day 2 reproducibility report"),
                ("Report type", "Internal Day 2 progress + Day 3 roadmap"),
                ("Language", "Simple Hinglish  ·  technical terms ke saath"),
            ]
        )
    )
    return story


def toc_story():
    s = []
    s += heading(1, "Table of Contents", "toc")
    s.append(
        P(
            "Har member ko pehle apna section padhna chahiye, phir shared results, phir Day 3 roadmap.",
            "body",
        )
    )
    items = [
        "1.  Is document ka purpose",
        "2.  Executive summary",
        "3.  Factual consistency notes  (kya mix nahi karna)",
        "4.  Overall Day 2 status",
        "5.  Technical progress  — data, model, evaluation, system",
        "6.  Multi-Horizon TEST classification results",
        "7.  Operational early-warning results",
        "8.  Baseline / model comparison  (protocol caveat ke saath)",
        "9.  Backend + frontend verified state",
        "10. Git / project state",
        "11. Pranshu — Day 2 work + Day 3 responsibilities",
        "12. Pulkit — Day 2 work + Day 3 responsibilities",
        "13. Pragati — Day 2 work + Day 3 responsibilities",
        "14. Ankita — Day 2 work + Day 3 responsibilities",
        "15. Riddhi — Day 2 work + Day 3 responsibilities",
        "16. Priyanshi — Day 2 work + Day 3 responsibilities",
        "17. Day 3 roadmap",
        "18. SIH presentation preparation",
        "19. Final project status / next milestone",
    ]
    s.append(bullets(items))
    return s


def purpose_story():
    s = []
    s += heading(1, "1. Is document ka purpose", "purpose")
    s.append(
        P(
            "Ye report team ko ye clearly batane ke liye hai ki Day 2 pe kaam <b>complete</b> ho chuka hai, "
            "us complete kaam ka <b>technical matlab</b> kya hai, aur Day 3 continuation mein "
            "har person ko <b>kya naya</b> karna hai. Day 2 wala kaam dobara start nahi karna hai.",
            "body",
        )
    )
    s.append(
        bullets(
            [
                "Har member Day 2 contribution explain kar sake — team ke saamne aur judges ke saamne.",
                "Shared numbers ek hi jagah verified form mein rahein, taaki PPT aur baat match kare.",
                "Mock vs real, TEST vs VALIDATION, classification vs early-warning — ye mix na hon.",
                "Day 3 priorities role-aligned hon, overload na hon.",
            ]
        )
    )
    s.append(
        callout(
            "warning",
            "Agar koi judge / teammate poochhe “tumhara kaam kya tha?”, to generic line mat bolo. "
            "Apne section ke files, numbers, aur 2–3 honest limitations yaad rakhna.",
        )
    )
    return s


def exec_story():
    s = []
    s += heading(1, "2. Executive summary", "exec")
    s.append(
        P(
            "Day 2 ka core result ye hai: project ab sirf static IDS idea nahi raha. "
            "Ek <b>Multi-Horizon GRU</b> trained hai jo last 100 flows dekh kar next 50 / 100 / 200 / 500 "
            "flows par future DDoS state predict karta hai. Held-out TEST episodes 19–21 par "
            "classification aur temporal early-warning dono evaluate ho chuke hain. "
            "Real FastAPI inference Attack Forecast page se connected hai. "
            "Reproducibility rerun ne same checkpoint aur same TEST metrics reproduce kiye.",
            "body",
        )
    )
    s.append(P("Short mein Day 2 kya lock ho gaya", "h2"))
    s.append(
        bullets(
            [
                "<b>Data:</b> 21 episodes, 42,000 rows working set, 68 model features, TRAIN 1–15 / VAL 16–18 / TEST 19–21. Multi-horizon window validation <b>18 OK, 0 WARNING, 0 FAIL</b>.",
                "<b>Model:</b> Shared 2-layer GRU, alag heads H50/H100/H200/H500. Best epoch = 1, best validation loss = 1.895873, early stop epoch 9. Seed = 42, CPU.",
                "<b>Thresholds:</b> VALIDATION se select — 0.30 / 0.55 / 0.45 / 0.35. TEST par retune nahi hua.",
                "<b>Best current horizon (classification balance):</b> H200 — F1 0.7927, FAR 0.0761.",
                "<b>Sabse badi limitation:</b> H500 FAR = <b>0.9933</b>. Recall strong hai, lekin false alarms almost saari negatives par. Operationally unreliable.",
                "<b>System:</b> Real endpoints sirf <b>GET /health, GET /model-status, GET /demo-sequence, POST /predict</b>. Attack Forecast page real model use karti hai. Baaki dashboard pages abhi mock/simulation backed ho sakte hain.",
                "<b>Reproducibility:</b> Controlled rerun + identical SHA-256 hashes. Priyanshi Day 2 audit PASS.",
            ]
        )
    )
    s.append(
        callout(
            "limitation",
            "H500 ko “901 flows pehle warning” bol ke mat becho. Warning rate 100% hai, lekin FAR 99.33% hai — "
            "matlab model almost pehle se ATTACK bol deta hai. Ye Day 3 ki pehli operational problem hai.",
            title="H500 ko honestly rakho",
        )
    )
    s.append(spacer(4))
    s.append(
        callout(
            "verified",
            "Demo sequence (TEST index 1691, window 17909, episode 20, flows 38790–38889) pre-attack hai. "
            "Episode 20 ka attack start verified metadata mein <b>flow 39000</b> hai. "
            "Live /predict output: H50 97.9%, H100 99.5%, H200 99.5%, H500 98.2% — saari ATTACK. "
            "Isse ye mat samajhna ki is window ke saare horizon targets positive hain.",
        )
    )
    return s


def qc_story():
    s = []
    s += heading(1, "3. Factual consistency notes", "qc")
    s.append(
        P(
            "PDF generate karne se pehle repo files, reports, aur git history cross-check kiye gaye. "
            "Neeche wale points isliye likhe hain taaki koi member galat number mix na kar de.",
            "body",
        )
    )
    s.append(P("3.1 Episode examples — V1 numbers vs Multi-Horizon numbers", "h2"))
    s.append(
        P(
            "Purane GRU V1 early-warning report mein TEST examples ye hain: "
            "Episode 19 attack 36910 / warning 36709 / 201 flows early; "
            "Episode 20 attack 38910 / warning 38799 / 111 flows early; "
            "Episode 21 attack 40910 / warning 40909 / 1 flow early. "
            "Ye <b>GRU V1</b> evaluator ke numbers hain.",
            "body",
        )
    )
    s.append(
        P(
            "Multi-Horizon Day 2 evaluator (<b>ml/reports/multihorizon_early_warning_report.txt</b>, "
            "commit d3c663e ke baad) verified temporal metadata use karta hai: "
            "Episode 19 attack <b>37000</b>, Episode 20 attack <b>39000</b>, Episode 21 attack <b>41000</b>. "
            "Backend demo comment bhi Episode 20 start = 39000 ke saath match karta hai. "
            "<b>Is report mein Multi-Horizon verified numbers hi authoritative hain.</b> "
            "V1 examples ko Multi-Horizon result mat banao.",
            "body",
        )
    )
    s.append(
        callout(
            "warning",
            "Do alag evaluators ke attack-start definitions mix mat karo. "
            "Judges ke saamne Multi-Horizon ke liye 37000 / 39000 / 41000 hi bolo.",
        )
    )
    s.append(P("3.2 MITRE ATT&amp;CK mapping — Day 2 status honest rakho", "h2"))
    s.append(
        P(
            "Pranshu ka Day 2 document <b>DOCS/attack-patterns-and-traffic-signatures.md</b> "
            "attack behaviour, forecasting vs detection, aur DDoS traffic interpretation cover karta hai. "
            "Wahi document clearly likhta hai ki repo mein dedicated MITRE ATT&amp;CK mapping abhi verified nahi hai, "
            "aur unsupported technique IDs assign nahi kiye gaye. "
            "Isliye Day 2 complete is sense mein hai ki cybersecurity narrative + honest mapping status document ho gaya. "
            "<b>Formal ATT&amp;CK technique mapping Day 3 ka pending deliverable hai, completed mapping nahi.</b>",
            "body",
        )
    )
    s.append(P("3.3 dataset_audit_report.txt ko 42k working set mat samajhna", "h2"))
    s.append(
        P(
            "<b>ml/reports/dataset_audit_report.txt</b> 5,000 rows / 79 columns wale sample audit ka report hai "
            "(BENIGN / FTP-Patator / SSH-Patator). Day 2 DDoS working set alag hai: 42,000 rows. "
            "Dono files ko ek dusre se replace mat karo.",
            "body",
        )
    )
    s.append(P("3.4 Baseline comparison abhi apples-to-apples nahi hai", "h2"))
    s.append(
        P(
            "Logistic Regression, GRU V1, GRU V2 TEST reports ~273 windows dikhate hain "
            "(243 negative + 30 positive). Multi-Horizon GRU TEST 2,703 windows use karta hai. "
            "Numbers side-by-side table mein hain, lekin <b>final scientific comparability audit Day 3 ka kaam hai</b>.",
            "body",
        )
    )
    s.append(P("3.5 Jo is report mein claim nahi kiya gaya", "h2"))
    s.append(
        bullets(
            [
                "<b>/traffic-stream, /alerts, /model-stats</b> real FastAPI endpoints nahi hain.",
                "Poora dashboard real-data driven nahi hai — sirf Attack Forecast page verified real-model driven hai.",
                "Preprocessing leakage-free nahi hai — global median imputation split se pehle hoti hai.",
                "TEST thresholds retune nahi hue — aisa claim galat hoga.",
                "Koi naya git commit is report ke liye invent nahi kiya gaya.",
                "H500 FAR 0.9933 hide / soften nahi kiya gaya.",
            ]
        )
    )
    return s


def status_story():
    s = []
    s += heading(1, "4. Overall Day 2 status", "status")
    rows = [
        ["Pranshu", "Cyber intelligence narrative + DDoS interpretation", "100%", "Formal MITRE IDs still pending"],
        ["Pulkit", "FastAPI + Attack Forecast real inference", "100%", "Other pages still mock-backed"],
        ["Pragati", "CICIDS working-set + multihorizon validation", "100%", "Median-imputation leakage risk documented"],
        ["Ankita", "Multi-Horizon GRU train + thresholds + inference-ready", "100%", "H500 FAR 0.9933; best epoch = 1"],
        ["Riddhi", "TEST metrics + early-warning evaluator audit", "100%", "Comparison protocol audit is Day 3"],
        ["Priyanshi", "Seed / split / hash / controlled rerun", "100%", "Keep Day 3 reruns equally controlled"],
    ]
    s.append(
        simple_table(
            ["Member", "Day 2 completed scope", "Status", "Honest leftover / limit"],
            rows,
            col_widths=[
                0.14 * CONTENT_W,
                0.34 * CONTENT_W,
                0.12 * CONTENT_W,
                0.40 * CONTENT_W,
            ],
            header_left=True,
        )
    )
    s.append(P("Saare 6 members ka assigned Day 2 scope complete mark kiya gaya hai. Day 3 usi foundation par continue hoga.", "caption"))
    s.append(
        callout(
            "verified",
            "Riddhi Day 2 evaluator fully audited hai aur status <b>100% DONE</b> hai. "
            "TEST episodes strictly 19, 20, 21. Validation thresholds reuse. TEST retune nahi.",
        )
    )
    return s


def tech_story():
    s = []
    s += heading(1, "5. Technical progress", "tech")
    s.append(P("5.1 Forecasting idea — simple language", "h2"))
    s.append(
        P(
            "Model sirf ye nahi bata raha ki <b>abhi</b> attack chal raha hai ya nahi. "
            "Wo last 100 consecutive flows (68 features each) dekhta hai, phir multiple future horizons par "
            "predict karta hai ki aage DDoS state develop hone ke chances kitne hain. "
            "Yahi cheez project ko static classifier se hata ke predictive cyber-defence banati hai.",
            "body",
        )
    )
    s.append(
        kv_table(
            [
                ("Observation window", "100 flows  ·  ye past hai, future nahi"),
                ("Horizons", "next 50, 100, 200, 500 flows"),
                ("Target meaning", "Us future span mein koi DDoS flow aayega ya nahi (binary)"),
                ("Safety check", "Observation window ke andar DDoS allowed nahi — validation: 0 DDoS in observation"),
                ("Split unit", "Complete episodes, random rows nahi"),
            ]
        )
    )
    s.append(P("5.2 Data / temporal structure (Pragati — verified)", "h2"))
    s.append(
        simple_table(
            ["Item", "Verified value"],
            [
                ["Raw working-set rows", "42,000"],
                ["Raw working-set columns (with episode metadata)", "82"],
                ["Constant columns removed", "10"],
                ["Model features", "68"],
                ["Label balance", "21,000 BENIGN + 21,000 DDoS"],
                ["Episode design", "1000 pre-attack + 1000 attack flows"],
                ["TRAIN / VAL / TEST", "episodes 1–15 / 16–18 / 19–21"],
                ["Windows", "18,921  (901 per episode × 21)"],
                ["Tensor shapes", "TRAIN (13515, 100, 68) · VAL/TEST (2703, 100, 68)"],
                ["Missing values in raw working set", "0"],
                ["Duplicate complete rows", "0"],
                ["Inf in raw data", "12 Inf in Flow Bytes/s and Flow Packets/s, 6 BENIGN/pre_attack rows"],
                ["Multihorizon window validation", "18 OK, 0 WARNING, 0 FAIL"],
                ["Tensor validation", "59 OK, 0 WARNING, 0 FAIL"],
            ],
            col_widths=[0.46 * CONTENT_W, 0.54 * CONTENT_W],
            header_left=True,
        )
    )
    s.append(spacer(4))
    s.append(
        callout(
            "warning",
            "<b>Preprocessing-statistics leakage risk:</b> <b>ml/scripts/prepare_ddos_features.py</b> "
            "Inf→NaN ke baad global column medians compute karta hai, split se pehle. "
            "Held-out TEST feature values mein 0 rows imputation ke liye chahiye the, isliye existing TEST "
            "values is issue se directly alter nahi hue. Dataset ko “perfectly leakage-free” mat bolo. "
            "Is issue ki wajah se retraining required — aisa claim mat karo.",
        )
    )
    s.append(P("5.3 Multi-Horizon GRU configuration (Ankita — verified)", "h2"))
    s.append(
        simple_table(
            ["Config", "Value"],
            [
                ["Input", "68 features × 100 flow sequence"],
                ["Hidden size", "96"],
                ["GRU layers", "2"],
                ["Dropout", "0.30"],
                ["Normalization", "LayerNorm on last GRU state"],
                ["Shared block", "96 → 48 ReLU + Dropout"],
                ["Heads", "Separate linear heads: H50 / H100 / H200 / H500"],
                ["Batch size", "64"],
                ["Learning rate", "1e-3 (Adam)"],
                ["Max epochs / patience", "60 / 8"],
                ["Gradient clipping", "1.0"],
                ["Seed / device", "42 / CPU"],
                ["pos_weight source", "TRAIN only"],
                ["Threshold source", "VALIDATION only"],
            ],
            col_widths=[0.38 * CONTENT_W, 0.62 * CONTENT_W],
            header_left=True,
        )
    )
    s.append(
        P(
            "Training behaviour: epoch 1 par validation loss 1.895873 best rahi. Uske baad validation loss kharab hoti gayi. "
            "Patience 8 complete hone par epoch 9 pe early stopping. Best checkpoint restore = epoch 1.",
            "body",
        )
    )
    s.append(
        kv_table(
            [
                ("H50 threshold", "0.30  (validation F1 0.6502)"),
                ("H100 threshold", "0.55  (validation F1 0.9028)"),
                ("H200 threshold", "0.45  (validation F1 0.7179)"),
                ("H500 threshold", "0.35  (validation F1 0.7161)"),
            ]
        )
    )
    return s


def metrics_story():
    s = []
    s += heading(1, "6. Multi-Horizon TEST classification results", "metrics")
    s.append(
        P(
            "Ye table <b>window-level forecasting classification</b> hai. "
            "Precision / Recall / F1 / Accuracy thresholded predictions se aate hain. "
            "ROC-AUC aur PR-AUC continuous probabilities se. "
            "FAR = FP / (FP + TN). TEST thresholds retune nahi hue.",
            "body",
        )
    )
    s.append(
        simple_table(
            ["Horizon", "Precision", "Recall", "F1", "Accuracy", "ROC-AUC", "PR-AUC", "FAR"],
            [
                ["H50", "0.2573", "1.0000", "0.4093", "0.8398", "0.9455", "0.3681", "0.1696"],
                ["H100", "0.4941", "0.9833", "0.6577", "0.8864", "0.9492", "0.7019", "0.1257"],
                ["H200", "0.7572", "0.8317", "0.7927", "0.9034", "0.9225", "0.7726", "0.0761"],
                ["H500", "0.5566", "1.0000", "0.7151", "0.5579", "0.7644", "0.8423", "0.9933"],
            ],
            col_widths=[CONTENT_W / 8] * 8,
            highlight_last=True,
        )
    )
    s.append(P("Source: ml/reports/multihorizon_gru_training_report.txt and the audited Riddhi evaluator. H500 row highlighted because FAR is extreme.", "caption"))
    s.append(
        simple_table(
            ["Horizon", "TN", "FP", "FN", "TP", "Positives", "Negatives"],
            [
                ["H50", "2120", "433", "0", "150", "150", "2,553"],
                ["H100", "2101", "302", "5", "295", "300", "2,403"],
                ["H200", "1943", "160", "101", "499", "600", "2,103"],
                ["H500", "8", "1195", "0", "1500", "1,500", "1,203"],
            ],
            highlight_last=True,
        )
    )
    s.append(
        callout(
            "limitation",
            "H500: TN sirf 8, FP 1195, FN 0, TP 1500. Recall 1.0 isliye hai kyunki almost har window ATTACK predict ho rahi hai. "
            "Accuracy 0.5579 almost class prior jaisi hai. PR-AUC 0.8423 dekh ke FAR mat chhupao.",
        )
    )
    s.append(
        P(
            "Operational reading, simple language: H50 almost saari future attacks pakad leta hai lekin bahut extra alarms deta hai "
            "(precision 0.2573). H200 abhi sabse balanced classification picture deta hai. "
            "H100 high recall ke saath beech ka tradeoff hai. H500 currently demo ke liye dangerous hai.",
            "body",
        )
    )
    return s


def early_story():
    s = []
    s += heading(1, "7. Operational early-warning results", "early")
    s.append(
        P(
            "Early warning classification F1 se alag concept hai. "
            "Warning tabhi positive-lead early warning count hoti hai jab first qualifying warning "
            "<b>attack start se pehle</b> aaye. Warning at/after attack start positive-lead nahi maani jaati.",
            "body",
        )
    )
    s.append(
        callout(
            "finding",
            "<b>“First warning true-positive forecast thi”</b> aur <b>“warning attack start se pehle aayi”</b> "
            "do alag baatein hain. Unhe ek metric mat banao. "
            "H50: 3/3 episodes early warned, lekin 0/3 first warnings true-positive forecasts thin. "
            "H100: 1/3, H200: 1/3, H500: 0/3 first warnings also true-positive forecasts.",
        )
    )
    s.append(
        simple_table(
            ["Horizon", "Warning rate", "Mean lead", "Median lead", "≥50 success", "≥100 success", "FAR"],
            [
                ["H50", "100%", "198.7", "202", "100%", "66.7%", "0.1696"],
                ["H100", "100%", "329.3", "189", "100%", "66.7%", "0.1257"],
                ["H200", "100%", "341", "207", "100%", "66.7%", "0.0761"],
                ["H500", "100%", "901", "901", "100%", "100%", "0.9933"],
            ],
            highlight_last=True,
        )
    )
    s.append(P("Lead-time success rates sirf genuinely early warnings par. Sample = 3 TEST episodes only.", "caption"))
    s.append(P("7.1 Multi-Horizon H50 episode examples (n = 3, generalize mat karo)", "h2"))
    s.append(
        simple_table(
            ["Episode", "Attack start", "H50 first warning", "Lead (flows)", "H50 probability"],
            [
                ["19", "37000", "36704", "296", "0.372099"],
                ["20", "39000", "38798", "202", "0.321912"],
                ["21", "41000", "40902", "98", "0.324796"],
            ],
        )
    )
    s.append(
        P(
            "Ye sirf 3 held-out TEST episodes ke examples hain. Inse large-sample claim mat banao. "
            "Episode 21 par H50 lead sirf 98 flows hai — har episode pe same early margin nahi milta.",
            "body",
        )
    )
    s.append(
        callout(
            "warning",
            "GRU V1 report ke 36910 / 201-flow examples yahan Multi-Horizon result nahi hain. "
            "Agar PPT mein V1 vs Multi-Horizon dono dikhao, labels alag rakho.",
        )
    )
    s.append(
        callout(
            "limitation",
            "H500 har episode par pehle usable window se warning de deta hai (lead 901). "
            "Saath mein FAR 99.33% hai. Isliye H500 ko “sabse best early warning” bolna galat hoga.",
        )
    )
    return s


def compare_story():
    s = []
    s += heading(1, "8. Baseline / model comparison", "compare")
    s.append(
        P(
            "Verified published numbers neeche hain. Inhe reference ke liye rakho, "
            "lekin abhi final apples-to-apples scientific ranking mat ghoshit karo.",
            "body",
        )
    )
    s.append(
        simple_table(
            ["Model", "F1", "ROC-AUC", "PR-AUC", "FAR", "TEST size (from report)"],
            [
                ["Logistic Regression", "0.4091", "0.8514", "0.3014", "0.1646", "273 windows"],
                ["GRU V1", "0.6667", "0.9444", "0.5370", "0.1235", "273 windows"],
                ["GRU V2", "0.6818", "0.9329", "0.5420", "0.1152", "273 windows"],
                ["MH GRU H50", "0.4093", "0.9455", "0.3681", "0.1696", "2,703 windows"],
                ["MH GRU H100", "0.6577", "0.9492", "0.7019", "0.1257", "2,703 windows"],
                ["MH GRU H200", "0.7927", "0.9225", "0.7726", "0.0761", "2,703 windows"],
                ["MH GRU H500", "0.7151", "0.7644", "0.8423", "0.9933", "2,703 windows"],
            ],
            col_widths=[
                0.20 * CONTENT_W,
                0.12 * CONTENT_W,
                0.14 * CONTENT_W,
                0.14 * CONTENT_W,
                0.12 * CONTENT_W,
                0.28 * CONTENT_W,
            ],
            highlight_last=True,
        )
    )
    s.append(
        callout(
            "day3",
            "Day 3 priority 1: exact evaluation protocols verify karo — same split, same horizon definition, "
            "same metric codepath. Jo difference nikle, document karo. Tabhi defensible comparison table banegi.",
        )
    )
    return s


def system_story():
    s = []
    s += heading(1, "9. Backend + frontend verified state", "system")
    s.append(P("9.1 Runtime", "h2"))
    s.append(
        kv_table(
            [
                ("API", "FastAPI + Uvicorn"),
                ("Python", "3.13.15"),
                ("PyTorch", "2.13.0+cpu"),
                ("FastAPI", "0.141.1"),
                ("Uvicorn", "0.52.4"),
                ("Frontend", "React / Vite / TypeScript  ·  npm run build succeeds"),
            ]
        )
    )
    s.append(P("9.2 Real FastAPI endpoints — sirf ye four", "h2"))
    s.append(
        simple_table(
            ["Method", "Path", "Kaam"],
            [
                ["GET", "/health", "Process alive?  {status: ok}"],
                ["GET", "/model-status", "Model loaded, horizons, validation thresholds"],
                ["GET", "/demo-sequence", "Fixed held-out TEST sequence for offline demo"],
                ["POST", "/predict", "100×68 sequence → probabilities, thresholds, 0/1 predictions"],
            ],
            col_widths=[0.14 * CONTENT_W, 0.22 * CONTENT_W, 0.64 * CONTENT_W],
            header_left=True,
        )
    )
    s.append(
        callout(
            "warning",
            "/traffic-stream, /alerts, aur /model-stats currently real backend endpoints nahi hain. "
            "Frontend mein related pages mock/simulation data use kar sakte hain. Unhe live API mat bolo.",
        )
    )
    s.append(P("9.3 Offline demo sequence", "h2"))
    s.append(
        simple_table(
            ["Field", "Value"],
            [
                ["Test index", "1691"],
                ["Window ID", "17909"],
                ["Episode", "20"],
                ["Observation flows", "38790–38889"],
                ["Observation length", "100"],
                ["Source", "CICIDS2017 held-out TEST tensor"],
                ["Mode", "offline_demo"],
                ["Episode 20 attack start", "39000  (pre-attack window)"],
                ["Real /predict", "H50 97.9% · H100 99.5% · H200 99.5% · H500 98.2%"],
                ["Decisions", "All four = ATTACK"],
                ["Thresholds shown", "30% / 55% / 45% / 35%"],
            ],
            col_widths=[0.34 * CONTENT_W, 0.66 * CONTENT_W],
            header_left=True,
        )
    )
    s.append(
        P(
            "Observation 38889 par khatam hoti hai, attack 39000 par start. "
            "Isliye short horizons ka ground-truth target automatically positive nahi hota. "
            "Model ne phir bhi 4/4 ATTACK diya — demo interpretation mein “target bhi 4/4 positive tha” mat bolo.",
            "body",
        )
    )
    s.append(P("9.4 Frontend pages — real vs mock", "h2"))
    s.append(
        simple_table(
            ["Page", "Day 2 data source"],
            [
                ["Attack Forecast (/forecast)", "Real: GET /demo-sequence + POST /predict"],
                ["Dashboard (/)", "Simulation / mock-backed (useSimulation, mock defaults)"],
                ["Live Traffic (/traffic)", "Simulation / mock-backed"],
                ["Threat Intelligence (/intelligence)", "Mock API helpers + simulation"],
                ["Model Performance (/model)", "Mock getModelMetrics()"],
                ["Alerts (/alerts)", "Mock getAlerts()"],
            ],
            col_widths=[0.40 * CONTENT_W, 0.60 * CONTENT_W],
            header_left=True,
        )
    )
    return s


def git_story():
    s = []
    s += heading(1, "10. Git / project state", "git")
    s.append(
        P(
            "Branch <b>main</b>, origin ke saath up to date, working tree clean. "
            "Neeche wale commits actually git mein maujood hain. Koi naya Day 2 audit commit invent nahi kiya.",
            "body",
        )
    )
    s.append(
        simple_table(
            ["Commit", "Message", "Day 2 meaning"],
            [
                ["40189cb", "Add Priyanshi Day 2 reproducibility report", "Reproducibility audit locked"],
                ["bb79579", "Connect dashboard to real multi-horizon GRU", "Attack Forecast real inference"],
                ["cd1b786", "Add FastAPI inference backend", "health / model-status / demo-sequence / predict"],
                ["d3c663e", "Fix multi-horizon evaluation and temporal metadata", "TEST metadata + evaluator alignment"],
                ["1f7a0fc", "Add standalone multi-horizon GRU inference", "Inference class used by backend"],
                ["412e1fb", "Merge PR #2 feature/pranshu-day2", "Cybersecurity narrative document"],
            ],
            col_widths=[0.16 * CONTENT_W, 0.42 * CONTENT_W, 0.42 * CONTENT_W],
            header_left=True,
        )
    )
    s.append(P("Related hashes (Priyanshi controlled rerun, byte-identical):", "h3"))
    s.append(
        KeepTogether(
            [
                kv_table(
                    [
                        (
                            "Model SHA-256",
                            "<font name='Consolas' size='7.2'>88e354922577f9f5076a7416d682c47a81c626262071d34044f585f233f78019</font>",
                        ),
                        (
                            "Predictions SHA-256",
                            "<font name='Consolas' size='7.2'>dc5692fd425338772a4feed08b86d2bd10ea4507205888391d88bfafbd360ab8</font>",
                        ),
                        (
                            "Training report SHA-256",
                            "<font name='Consolas' size='7.2'>dd6731c1d7e91e5d3479c62973098f82ff3e5795265939cd3e5ee583497c619b</font>",
                        ),
                    ],
                    key_w=48 * mm,
                )
            ]
        )
    )
    return s


def member_pranshu():
    s = [PageBreak(), member_banner("PRANSHU", "Cybersecurity / Network Analysis / Attack Intelligence", "100% DONE")]
    s += heading(1, "11. Pranshu — Day 2 work + Day 3 responsibilities", "m_pranshu")
    s.append(P("A. Role in the project", "h2"))
    s.append(
        P(
            "Pranshu ka kaam model ko “ML toy” nahi, predictive cyber-defence story banana hai. "
            "Wo team ko ye samjhate hain ki CICIDS2017 DDoS traffic mein kya badalta hai, "
            "forecast ka defence meaning kya hai, aur detection vs forecasting mein farq kya hai.",
            "body",
        )
    )
    s.append(P("B. Day 2 ke responsibilities", "h2"))
    s.append(
        bullets(
            [
                "Network attack behaviour aur DDoS patterns/signatures samajhna",
                "Attack progression / timeline interpretation",
                "Forecasting output ka cybersecurity meaning",
                "MITRE ATT&amp;CK mapping — honest status ke saath",
                "Project ko static IDS ki jagah forecasting narrative dena",
            ]
        )
    )
    s.append(P("C. Day 2 pe actually kya complete hua", "h2"))
    s.append(
        P(
            "Verified document: <b>DOCS/attack-patterns-and-traffic-signatures.md</b> (commit c6235c5 / merge 412e1fb). "
            "Usme DDoS traffic behaviour, detection-vs-forecast distinction, H500 FAR caution, "
            "aur dashboard terminology recommendations hain. "
            "Formal MITRE technique IDs assign nahi kiye gaye — document khud kehta hai mapping abhi verified nahi.",
            "body",
        )
    )
    s.append(P("D. Simple technical explanation", "h2"))
    s.append(
        P(
            "IDS style system poochhta hai: “kya ye flow abhi attack hai?” "
            "Hamara system poochhta hai: “abhi jo 100 flows dekhe, unke baad next 50/100/200/500 flows mein "
            "DDoS state aane ke chances kya hain?” "
            "DDoS achanak magic nahi hota. Traffic ke volume, packet rates, aur backward/forward balance mein "
            "temporal change hota hai. TEST episodes 19–21 par feature analysis dikhati hai ki attack phase mein "
            "Flow Packets/s aur Flow Bytes/s jaise signals pre-attack se kaafi shift hote hain. "
            "Ye shift ko model sequence se seekhta hai. Phir bhi ek feature ko universal DDoS signature mat bolo.",
            "body",
        )
    )
    s.append(P("E. Related files / results", "h2"))
    s.append(
        bullets(
            [
                "DOCS/attack-patterns-and-traffic-signatures.md",
                "ml/reports/ddos_temporal_feature_analysis.txt",
                "ml/reports/ddos_sequence_analysis.txt",
                "ml/reports/multihorizon_early_warning_report.txt  (interpretation, not ownership of metrics code)",
            ]
        )
    )
    s.append(P("F. Overall SIH solution mein kyun zaroori", "h2"))
    s.append(
        P(
            "Judges ko numbers se pehle story chahiye: input traffic → future risk → defender action. "
            "Bina cybersecurity meaning ke H200 F1 0.79 sirf exam score lagta hai. "
            "Pranshu ki story us score ko defence decision se jodti hai.",
            "body",
        )
    )
    s.append(P("G. Presentation ke liye yaad rakho", "h2"))
    s.append(
        bullets(
            [
                "Detection ≠ forecasting. Demo window pre-attack ho sakti hai.",
                "H500 ko best lead-time mat bolo. FAR 0.9933 openly bolo.",
                "MITRE IDs tabhi bolo jab Day 3 pe verified mapping ho. Abhi “mapping pending, narrative ready” bolo.",
                "3 TEST episodes — large real-world generalization claim mat karo.",
            ]
        )
    )
    s.append(P("H. Day 3 responsibility", "h2"))
    s.append(
        P(
            "Forecasting explainability + cybersecurity narrative integration. "
            "Model output ko understandable network/attack signals se jodna, "
            "aur verified MITRE ATT&amp;CK mapping draft banana — sirf wahi techniques jo evidence se support hon.",
            "body",
        )
    )
    s.append(P("I. Day 3 deliverables", "h2"))
    s.append(
        bullets(
            [
                "Judge-facing 1-page “forecast → DDoS stage → recommended response” note",
                "Verified MITRE mapping table (technique, evidence, confidence: high/medium/low)",
                "H50/H100/H200/H500 ka cyber meaning, including H500 limitation language",
                "Likely judge questions ke short answers, is report ke numbers se aligned",
            ]
        )
    )
    s.append(P("J–K. Likely questions + short answers", "h2"))
    s.extend(
        qa_block(
            [
                (
                    "Ye project IDS se alag kaise hai?",
                    "IDS current attack detect karta hai. Hum future horizon par attack state forecast karte hain, observation window mein DDoS dekh ke nahi.",
                ),
                (
                    "DDoS yahan kaise dikhta hai?",
                    "CICIDS2017 DDoS episodes mein traffic pattern pre-attack se attack phase tak shift hota hai — rates, sizes, directionality. Feature analysis TEST episodes par measurable change dikhati hai. Single feature ko magic signature nahi kahenge.",
                ),
                (
                    "MITRE mapping ho gayi kya?",
                    "Day 2 pe narrative aur honest status document hua. Dedicated technique-ID mapping repo mein verified nahi thi. Day 3 pe evidence-backed mapping aayegi, guesswork nahi.",
                ),
                (
                    "H500 901 flows early hai, to best nahi hai kya?",
                    "Nahi. FAR 99.33% hai. Wo almost hamesha alarm bajaata hai. Operationally unreliable.",
                ),
                (
                    "Demo par 4/4 ATTACK aaya, matlab attack already start tha?",
                    "Nahi. Episode 20 demo window 38790–38889 hai, attack start 39000. Ye forecast hai, current confirmed attack nahi.",
                ),
                (
                    "Kitne attack types handle ho rahe hain?",
                    "Current working pipeline DDoS forecasting par focused hai, full 15-class CICIDS IDS nahi.",
                ),
                (
                    "Agar false alarm aaye to defender kya kare?",
                    "Horizon, threshold, FAR, aur lead-time saath padhna. H200 currently zyada usable classification tradeoff deta hai. Alert ko confirmed incident mat treat karo.",
                ),
            ]
        )
    )
    return s


def member_pulkit():
    s = [PageBreak(), member_banner("PULKIT", "Web Dashboard + Backend/API + System Integration", "100% DONE for assigned Day 2 scope")]
    s += heading(1, "12. Pulkit — Day 2 work + Day 3 responsibilities", "m_pulkit")
    s.append(P("A. Role in the project", "h2"))
    s.append(
        P(
            "Pulkit trained model ko demonstrable system banate hain: FastAPI backend, frontend data contract, "
            "aur Attack Forecast page par real inference. Offline demo ke liye fixed TEST sequence bhi unhi ke layer mein hai.",
            "body",
        )
    )
    s.append(P("B. Day 2 ke responsibilities", "h2"))
    s.append(
        bullets(
            [
                "Dashboard integration aur frontend/backend contract",
                "Real model inference: /predict, /health, /model-status, /demo-sequence",
                "Multi-Horizon GRU output ko Attack Forecast page se jodna",
                "Mock vs real distinction maintain karna",
                "Offline demonstration ke liye system tayyar karna",
            ]
        )
    )
    s.append(P("C. Actually complete kya hua", "h2"))
    s.append(
        P(
            "backend/main.py FastAPI app: model load, four real endpoints, CORS localhost:5173. "
            "ml/inference/multihorizon_gru_inference.py checkpoint se architecture, weights, horizons, thresholds load karta hai. "
            "website/src/pages/AttackForecast.tsx demo sequence lata hai aur /predict call karta hai. "
            "website/src/services/api.ts clearly likhta hai ki baaki dashboard endpoints mock-backed hain. "
            "Commits: cd1b786 backend, bb79579 dashboard connect.",
            "body",
        )
    )
    s.append(P("D. Simple technical explanation", "h2"))
    s.append(
        P(
            "Frontend 100 rows × 68 numbers bhejta hai. Backend check karta hai: exactly 100 rows, har row 68 finite features. "
            "PyTorch GRU logits → sigmoid probabilities → validation thresholds se 0/1. "
            "Demo sequence disk se random nahi banti; TEST tensor ka index 1691 fix hai, isliye offline demo repeatable hai.",
            "body",
        )
    )
    s.append(P("E. Important files", "h2"))
    s.append(
        bullets(
            [
                "backend/main.py",
                "ml/inference/multihorizon_gru_inference.py",
                "website/src/pages/AttackForecast.tsx",
                "website/src/components/forecast/MultiHorizonPredictionCard.tsx",
                "website/src/services/api.ts",
                "website/src/data/mock.ts  (abhi bhi kai pages yahi use karte hain)",
            ]
        )
    )
    s.append(P("F. SIH solution mein kyun zaroori", "h2"))
    s.append(
        P(
            "Bina working demo ke judges sirf reports dekhenge. Pulkit ka layer trained .pt file ko "
            "screen par repeatable forecast banata hai. Ye offline demonstrable system ka backbone hai.",
            "body",
        )
    )
    s.append(P("G. Presentation memory", "h2"))
    s.append(
        bullets(
            [
                "Real endpoints ke naam yaad rakho — four hi hain.",
                "Attack Forecast real hai; Dashboard/LiveTraffic/ModelPerformance ko real mat bolo.",
                "Demo pre-attack TEST window hai, live packet capture nahi.",
                "npm run build succeed hota hai — frontend compile-ready hai.",
            ]
        )
    )
    s.append(P("H–I. Day 3 objective, work, deliverables", "h2"))
    s.append(
        P(
            "Backend/API completion decision + dashboard hardening + offline demo flow polish. "
            "Har naya endpoint tabhi real banao jab demo ko genuinely chahiye. Contract saaf rakho.",
            "body",
        )
    )
    s.append(
        bullets(
            [
                "Likho: kaunse remaining features real hone chahiye (traffic stream / alerts / model stats) aur kaunse mock reh sakte hain",
                "UI par Real vs Mock badge/label jahan development ke dauraan mix ho sakta hai",
                "Judge flow: health → model-status → demo-sequence → predict → four horizons",
                "Agar alerts real karni hon to /predict se derived, fake random alerts nahi",
            ]
        )
    )
    s.append(P("J–K. Likely questions + short answers", "h2"))
    s.extend(
        qa_block(
            [
                (
                    "Backend mein kaunse real APIs hain?",
                    "GET /health, GET /model-status, GET /demo-sequence, POST /predict. Aur koi traffic-stream/alerts/model-stats real endpoint abhi nahi.",
                ),
                (
                    "Dashboard poora live model se chalta hai kya?",
                    "Nahi. Attack Forecast real Multi-Horizon GRU use karti hai. Baaki kai pages mock/simulation hain.",
                ),
                (
                    "Demo sequence kahan se aati hai?",
                    "Held-out TEST tensor, index 1691, window 17909, episode 20, flows 38790–38889. Offline, deterministic.",
                ),
                (
                    "Model CPU pe hai ya GPU?",
                    "Inference CPU pe load hota hai. Training bhi CPU pe hui thi.",
                ),
                (
                    "Agar sequence 100×68 na ho to?",
                    "POST /predict 422 deta hai. NaN/Inf bhi reject hote hain.",
                ),
                (
                    "Thresholds frontend hardcode karta hai kya?",
                    "Model checkpoint ke validation thresholds backend response mein aate hain: 0.30 / 0.55 / 0.45 / 0.35.",
                ),
                (
                    "Offline demo kaise repeat hoga?",
                    "Same TEST index, same checkpoint, same seed-trained weights. /demo-sequence hamesha wahi window dega.",
                ),
            ]
        )
    )
    return s


def member_pragati():
    s = [PageBreak(), member_banner("PRAGATI", "Data Engineering / Dataset Analysis / Temporal Validation", "100% DONE")]
    s += heading(1, "13. Pragati — Day 2 work + Day 3 responsibilities", "m_pragati")
    s.append(P("A. Role in the project", "h2"))
    s.append(
        P(
            "Pragati data ko model-safe banati hain: CICIDS2017 se DDoS working set, episode structure, "
            "leakage checks, feature prep, scaling understanding, aur temporal sequence validation. "
            "Agar ye layer galat ho to saare metrics meaning lose kar dete hain.",
            "body",
        )
    )
    s.append(P("B–C. Day 2 responsibilities aur completed work", "h2"))
    s.append(
        P(
            "Working set 21 episodes ka hai, har episode 1000 pre-attack + 1000 attack. "
            "Label balance 21k/21k. 10 constant columns hata kar 68 features. "
            "Windows validation 18 OK / 0 WARNING / 0 FAIL. Tensor validation 59 OK. "
            "Observation windows mein 0 DDoS — ye early-warning safety ke liye critical hai. "
            "Inf handling aur global-median leakage risk audit karke document kiya, chhupaya nahi.",
            "body",
        )
    )
    s.append(P("D. Simple technical explanation", "h2"))
    s.append(
        P(
            "CICIDS raw capture ko seedha model mein nahi dalte. Pehle meaningful DDoS episodes nikalte hain, "
            "har attack se pehle 1000 BENIGN flows rakhte hain, phir sliding 100-flow observation windows banate hain. "
            "Target future horizon mein DDoS aaya ya nahi. Split episode-level hai, isliye future episode ka pattern "
            "train rows ke beech leak nahi hona chahiye. Scaling TRAIN par fit hoti hai "
            "(ml/scripts/scale_ddos_features.py). Lekin median imputation currently full frame par hai — ye woh caveat hai.",
            "body",
        )
    )
    s.append(P("E. Files", "h2"))
    s.append(
        bullets(
            [
                "ml/scripts/create_ddos_working_set.py, validate_ddos_working_set.py",
                "ml/scripts/prepare_ddos_features.py, scale_ddos_features.py, split_ddos_dataset.py",
                "ml/scripts/create_multihorizon_forecasting_windows.py, validate_multihorizon_windows.py",
                "ml/scripts/build_multihorizon_sequence_tensors.py, validate_multihorizon_sequence_tensors.py",
                "ml/reports/ddos_feature_preparation.txt, multihorizon_validation_report.txt, multihorizon_tensor_validation_report.txt",
            ]
        )
    )
    s.append(P("F–G. Why it matters + presentation memory", "h2"))
    s.append(
        P(
            "Judges poochhenge: leakage to nahi, TEST dekh ke to nahi seekha, time order toot to nahi. "
            "Pragati ke answers yahin se aate hain. Yaad rakho: 42k working set ≠ dataset_audit_report.txt ka 5k sample. "
            "Leakage risk admit karo, saath mein bolo TEST rows ko impute karne ki zaroorat nahi padi.",
            "body",
        )
    )
    s.append(P("H–I. Day 3", "h2"))
    s.append(
        P(
            "Riddhi ke comparison audit ke liye split/horizon definitions freeze karke likhna. "
            "Median-imputation leakage ke liye TRAIN-only fix ka design (implement tabhi jab team decide kare; silent retrain nahi). "
            "Explainability ke liye feature-level temporal evidence pack (already analyzed TEST features se, naya fake result nahi).",
            "body",
        )
    )
    s.append(
        bullets(
            [
                "One-pager: exact TRAIN/VAL/TEST rules for every model artifact",
                "Leakage note: current risk, TEST impact = 0 rows imputed, recommended TRAIN-only median",
                "Feature list (68) + constant-column list (10) judge-readable form mein",
            ]
        )
    )
    s.append(P("J–K. Likely questions + short answers", "h2"))
    s.extend(
        qa_block(
            [
                (
                    "Data split kaise hua?",
                    "Episode-wise. TRAIN 1–15, VALIDATION 16–18, TEST 19–21. Random shuffle of mixed episodes nahi.",
                ),
                (
                    "Observation window mein attack aa sakta hai kya?",
                    "Multi-horizon validation: observation windows containing DDoS = 0. Forecast region observation ke baad start hoti hai.",
                ),
                (
                    "68 features kaise aaye?",
                    "Working set se 10 constant columns hataaye. Model un 68 numeric traffic features par chalta hai, plus metadata alag.",
                ),
                (
                    "Inf / missing ka kya kiya?",
                    "Raw working set mein missing 0. 12 Inf values Flow Bytes/s aur Flow Packets/s mein, 6 BENIGN/pre_attack rows. Inf→NaN, phir median impute. Remaining Inf 0.",
                ),
                (
                    "Leakage hai kya?",
                    "Risk hai: median statistics split se pehle global compute hue. TEST mein impute karne layak rows 0 thin, isliye TEST values directly change nahi hue. Perfectly leakage-free nahi kahenge.",
                ),
                (
                    "42,000 rows original CICIDS ka full set hai?",
                    "Nahi. Ye DDoS-focused working set hai: 21 constructed episodes. Full CICIDS million-plus rows ka subset/design hai.",
                ),
                (
                    "Windows 18,921 kaise?",
                    "21 episodes × 901 valid 100-flow windows each, taaki H500 bhi episode ke andar rahe.",
                ),
            ]
        )
    )
    return s


def member_ankita():
    s = [PageBreak(), member_banner("ANKITA", "ML / Multi-Horizon GRU", "100% DONE")]
    s += heading(1, "14. Ankita — Day 2 work + Day 3 responsibilities", "m_ankita")
    s.append(P("A. Role in the project", "h2"))
    s.append(
        P(
            "Ankita forecasting model ki owner hain. Shared GRU encoder recent traffic state represent karta hai, "
            "phir char alag heads alag future distances par attack probability dete hain.",
            "body",
        )
    )
    s.append(P("B–C. Day 2 completed work", "h2"))
    s.append(
        P(
            "ml/scripts/train_multihorizon_gru.py se training, validation threshold search, TEST evaluation, "
            "checkpoint ml/models/multihorizon_gru.pt, predictions CSV, aur training report. "
            "Inference class usi architecture ko load karti hai. Best epoch 1, val loss 1.895873, stop at 9. "
            "Priyanshi ke rerun ne yahi behaviour reproduce kiya.",
            "body",
        )
    )
    s.append(P("D. Simple technical explanation", "h2"))
    s.append(
        P(
            "GRU sequence model hai — pehle flow se last flow tak hidden state update hoti hai. "
            "Last state (96-d) LayerNorm se stabilize hoti hai, 48-d shared ReLU block se guzarti hai, "
            "phir H50/H100/H200/H500 ke alag linear heads logit dete hain. "
            "Loss har horizon ka binary task hai, TRAIN pos_weight se imbalance handle hoti hai "
            "(H50 pos_weight 17.02, H500 0.802 — kyunki H500 pe positives zyada hain). "
            "Threshold F1 grid-search VALIDATION par, TEST ek baar end mein.",
            "body",
        )
    )
    s.append(
        P(
            "Best epoch 1 ka simple matlab: model ne pehle epoch ke baad validation par improve nahi kiya. "
            "Training loss girti rahi, validation loss nahi — overfitting ka signal. Early stopping ne epoch-1 "
            "checkpoint wapas liya. Ye failure nahi, honest training outcome hai.",
            "body",
        )
    )
    s.append(P("E. Files / artifacts", "h2"))
    s.append(
        bullets(
            [
                "ml/scripts/train_multihorizon_gru.py",
                "ml/reports/multihorizon_gru_training_report.txt",
                "ml/models/multihorizon_gru.pt",
                "ml/inference/multihorizon_gru_inference.py",
                "ml/processed/multihorizon_gru_test_predictions.csv  (artifact; hash verified)",
            ]
        )
    )
    s.append(P("F–G. Why it matters + what to remember", "h2"))
    s.append(
        P(
            "Ankita ka model SIH problem statement ka centre hai: multi-horizon forecasting. "
            "Judges se H500 ko defend mat karo as success. H200 ko current balanced classification result bolo. "
            "Thresholds yaad: 0.30 / 0.55 / 0.45 / 0.35. Seed 42. CPU. Observation 100.",
            "body",
        )
    )
    s.append(P("H–I. Day 3", "h2"))
    s.append(
        P(
            "H500 FAR investigation. Recalibrate / retain-with-limitation / drop-from-demo — decision evidence ke saath. "
            "Metrics silent manipulate nahi. Agar naya run ho to Priyanshi ke reproducibility protocol se.",
            "body",
        )
    )
    s.append(
        bullets(
            [
                "H500 error analysis: kahan FP cluster hota hai (almost everywhere, TN=8)",
                "Written recommendation: demo default horizon set (likely emphasize H100/H200)",
                "If recalibration: validation-only, TEST last, report both old and new",
            ]
        )
    )
    s.append(P("J–K. Likely questions + short answers", "h2"))
    s.extend(
        qa_block(
            [
                (
                    "Multi-horizon ka matlab?",
                    "Ek observation se char future distances: 50, 100, 200, 500 flows. Shared encoder, separate heads.",
                ),
                (
                    "Kyun GRU, LSTM/Transformer kyun nahi?",
                    "Day 2 pe verified trained forecasting model ye GRU hai, sequence length 100, CPU-friendly. Doosre architectures ka Day 2 trained replacement claim nahi karenge.",
                ),
                (
                    "Best epoch 1 kyun?",
                    "Val loss epoch 1 ke baad improve nahi hui. Patience 8 ke baad early stop, best checkpoint restore.",
                ),
                (
                    "Thresholds TEST dekh ke set kiye?",
                    "Nahi. VALIDATION F1 grid 0.10–0.95. TEST ek baar, baad mein.",
                ),
                (
                    "H500 F1 0.7151 achha nahi hai kya?",
                    "F1 akela enough nahi. FAR 0.9933 hai. Almost har negative pe alarm. Operationally fail.",
                ),
                (
                    "Input shape kya hai?",
                    "(batch, 100, 68). Demo ek sequence: (1, 100, 68).",
                ),
                (
                    "Class imbalance kaise handle hui?",
                    "Horizon-wise pos_weight TRAIN counts se. H50 rare positives, high weight. H500 positives majority-ish, weight &lt; 1.",
                ),
                (
                    "Kya retraining Day 2 leakage fix ke liye hui?",
                    "Nahi. Leakage documented hai, retraining required nahi ghoshit ki gayi.",
                ),
            ]
        )
    )
    return s


def member_riddhi():
    s = [PageBreak(), member_banner("RIDDHI", "ML Evaluation / Metrics / Early Warning / Model Comparison", "100% DONE")]
    s += heading(1, "15. Riddhi — Day 2 work + Day 3 responsibilities", "m_riddhi")
    s.append(P("A. Role in the project", "h2"))
    s.append(
        P(
            "Riddhi numbers ki referee hain. Model train ho jane ke baad bhi galat metric story project ko "
            "overclaim karwa sakti hai. Unka kaam: reusable evaluation, TEST-only protocol, "
            "classification vs early-warning alag rakhna, aur baselines ke published numbers collect karna.",
            "body",
        )
    )
    s.append(P("B–C. Completed Day 2 work", "h2"))
    s.append(
        P(
            "evaluate_multihorizon_early_warning.py read-only evaluator hai. Predictions/tensors/models modify nahi. "
            "TEST episodes strictly 19–21. Validation thresholds reuse. "
            "Classification table aur temporal early-warning table alag. "
            "Logistic / GRU V1 / GRU V2 ke existing reports se metrics liye gaye, lekin protocol sameness abhi final-audit pending hai.",
            "body",
        )
    )
    s.append(P("D. Evaluator behaviour — simple language", "h2"))
    s.append(
        bullets(
            [
                "Precision/Recall/F1/Accuracy: thresholded 0/1 predictions",
                "ROC-AUC / PR-AUC: continuous probabilities",
                "FAR = FP / (FP + TN), false alarm among actual negatives",
                "first_warning_flow = observation_end_position of earliest window jahan pred=1 and prob≥threshold",
                "lead = attack_start − first_warning_flow; sirf lead &gt; 0 count",
                "Horizon comparison table explicitly temporal early-warning hai, F1 ranking nahi",
                "“first warning was a true-positive forecast” alag count hai (H50: 0/3, H100: 1/3, H200: 1/3, H500: 0/3)",
            ]
        )
    )
    s.append(P("E. Files", "h2"))
    s.append(
        bullets(
            [
                "ml/scripts/evaluate_multihorizon_early_warning.py",
                "ml/reports/multihorizon_early_warning_report.txt",
                "ml/reports/forecasting_baseline_report.txt",
                "ml/reports/gru_forecasting_report.txt, gru_forecasting_v2_report.txt",
                "Older V1/V2 early-warning reports — mix na karein with MH attack-start metadata",
            ]
        )
    )
    s.append(P("F–G. Why it matters + memory", "h2"))
    s.append(
        P(
            "SIH mein overclaim se project tut-ta hai. Riddhi ke rules judges ke sawal ka defence hain: "
            "TEST peek nahi kiya, threshold TEST pe tune nahi, n=3 episodes, H500 FAR openly reported. "
            "V1 ke 201-flow example ko MH example mat banao.",
            "body",
        )
    )
    s.append(P("H–I. Day 3", "h2"))
    s.append(
        P(
            "Final apples-to-apples evaluation audit. Har model ke liye: split, window definition, horizon, "
            "threshold policy, metric code. Differences document. Tab defensible comparison table.",
            "body",
        )
    )
    s.append(
        bullets(
            [
                "Protocol matrix: LR vs GRU V1 vs GRU V2 vs MH GRU",
                "If incomparable: clearly say so, do not average unlike metrics",
                "Keep classification vs lead-time as two tables in the PPT appendix",
            ]
        )
    )
    s.append(P("J–K. Likely questions + short answers", "h2"))
    s.extend(
        qa_block(
            [
                (
                    "TEST dekh ke threshold choose kiya kya?",
                    "Nahi. Thresholds validation-selected hain: 0.30/0.55/0.45/0.35. TEST evaluate once afterwards.",
                ),
                (
                    "FAR kya hota hai?",
                    "False Alarm Rate = FP/(FP+TN). Negatives mein se kitne galat alarm. H500 par 0.9933.",
                ),
                (
                    "100% warning rate ka matlab model perfect hai?",
                    "Nahi. 3/3 episodes pe koi na koi early warning aa gayi. Quality FAR, precision, aur true-positive-first-warning se judti hai.",
                ),
                (
                    "Early warning aur F1 mein farq?",
                    "F1 har TEST window ki classification. Early warning episode-level: attack se kitne flows pehle pehli valid warning aayi.",
                ),
                (
                    "Kyun sirf 3 episodes?",
                    "Held-out TEST episodes 19–21 yahi hain. Small sample. Generalize nahi karenge.",
                ),
                (
                    "Kya evaluator ne model change kiya?",
                    "Nahi. Read-only on saved predictions and verified temporal metadata.",
                ),
                (
                    "LR vs GRU vs MH fair comparison hai?",
                    "Abhi nahi claim karenge. TEST sizes 273 vs 2703. Day 3 protocol audit ke baad hi defensible ranking.",
                ),
                (
                    "Episode 21 pe 1 flow early tha kya?",
                    "Wo GRU V1 report ka example hai (attack 40910, warning 40909). Multi-Horizon H50 par episode 21 lead 98 flows hai, attack start 41000.",
                ),
            ]
        )
    )
    return s


def member_priyanshi():
    s = [PageBreak(), member_banner("PRIYANSHI", "Python Automation / Reproducibility / Experiment Reliability", "100% DONE")]
    s += heading(1, "16. Priyanshi — Day 2 work + Day 3 responsibilities", "m_priyanshi")
    s.append(P("A. Role in the project", "h2"))
    s.append(
        P(
            "Priyanshi ensure karti hain ki experiment kal dobara chale to same result aaye. "
            "Seed, DataLoader, feature order, splits, pos_weight source, threshold policy, artifact hashes. "
            "SIH mein “hamare laptop pe ek baar aa gaya” enough nahi.",
            "body",
        )
    )
    s.append(P("B–C. Completed Day 2 work", "h2"))
    s.append(
        P(
            "Verified report: ml/reports/priyanshi_day2_reproducibility_report.txt (commit 40189cb). "
            "Status PASS. Seed 42. NumPy/PyTorch seeds, CUDA deterministic flags when available, "
            "dedicated DataLoader generator, train shuffle with that generator, val/test no shuffle. "
            "Feature order episode_id + sequence_position. Split overlap checks. "
            "Controlled rerun: best epoch 1, val loss 1.895873, stop epoch 9, same TEST metrics, identical SHA-256.",
            "body",
        )
    )
    s.append(P("D. Simple technical explanation", "h2"))
    s.append(
        P(
            "Neural net training thoda random ho sakta hai: weight init, shuffle, dropout. "
            "Seed lock karne se wahi random sequence repeat hoti hai. "
            "Agar DataLoader alag generator use kare to seed toot jata hai — isliye dedicated generator SEED=42 se set hai. "
            "Hash check ka matlab: files byte-for-byte same, sirf “lagbhag same F1” nahi.",
            "body",
        )
    )
    s.append(P("E. Files", "h2"))
    s.append(
        bullets(
            [
                "ml/reports/priyanshi_day2_reproducibility_report.txt",
                "ml/scripts/train_multihorizon_gru.py  (seed + DataLoader + TRAIN pos_weight + VAL thresholds)",
                "ml/scripts/validate_multihorizon_sequence_tensors.py  (split / order / overlap)",
            ]
        )
    )
    s.append(P("F–G. Why it matters + memory", "h2"))
    s.append(
        P(
            "Reproducibility judges ko confidence deti hai ki result screenshot nahi, pipeline hai. "
            "Hashes yaad rakhne ki zaroorat nahi word-for-word, lekin report ka PASS status aur seed 42 zaroor. "
            "Source tensors reproducibility audit ke dauraan intentionally modify nahi hue.",
            "body",
        )
    )
    s.append(P("H–I. Day 3", "h2"))
    s.append(
        P(
            "Agar Ankita H500 ke liye koi controlled experiment kare, ya Riddhi comparison recompute kare, "
            "to Priyanshi rerun safety: kya overwrite hoga, kya naya filename, hash before/after. "
            "Offline demo repeatability checklist: same checkpoint, same TEST index, same API output.",
            "body",
        )
    )
    s.append(
        bullets(
            [
                "Day 3 experiment log template (command, seed, hashes, whether TEST was touched)",
                "Demo repeatability note for Pulkit’s judge flow",
                "Do not overwrite multihorizon_gru.pt unless a named new artifact is agreed",
            ]
        )
    )
    s.append(P("J–K. Likely questions + short answers", "h2"))
    s.extend(
        qa_block(
            [
                (
                    "Seed kya hai?",
                    "42. Training script NumPy, PyTorch, aur DataLoader generator isi se lock karti hai.",
                ),
                (
                    "Rerun pe same result aaya?",
                    "Haan. Best epoch 1, val loss 1.895873, early stop 9, same TEST metrics, same SHA-256 hashes.",
                ),
                (
                    "TEST training mein use hua?",
                    "Nahi. pos_weight TRAIN only. Thresholds VALIDATION only. TEST last evaluation.",
                ),
                (
                    "Hash kyun zaroori?",
                    "Floating metrics round-off se “same” lag sakte hain. SHA-256 byte identity prove karta hai.",
                ),
                (
                    "Shuffle to hota hai training mein?",
                    "Haan, lekin seeded generator se. Validation/Test shuffle=False.",
                ),
                (
                    "Kya original dataset change hua audit mein?",
                    "Nahi. Report kehta hai source dataset/tensors intentionally modify nahi hue.",
                ),
                (
                    "Agar Day 3 pe naya model bane to?",
                    "Naya filename, naya report, naya hash. Silent overwrite of the Day 2 checkpoint nahi.",
                ),
            ]
        )
    )
    return s


def day3_story():
    s = []
    s += heading(1, "17. Day 3 roadmap", "day3")
    s.append(
        P(
            "Day 3 restart nahi hai. Day 2 ke locked artifacts par continuation hai: "
            "better evaluation honesty, H500 ka operational decision, explainability, "
            "cyber narrative, selected real APIs, dashboard hardening, offline demo, PPT.",
            "body",
        )
    )
    s.append(P("Priority order", "h2"))
    priorities = [
        [
            "1",
            "Apples-to-apples evaluation audit",
            "Riddhi lead, Pragati split evidence, Priyanshi rerun safety",
            "Defensible comparison table, documented protocol differences",
        ],
        [
            "2",
            "H500 operational improvement / limitation",
            "Ankita lead, Riddhi metrics, Priyanshi if rerun",
            "Written decision: retain / recalibrate / demo-limit. No silent metric edits",
        ],
        [
            "3",
            "Forecasting explainability",
            "Pranshu + Pragati features, Ankita model view, Pulkit UI if shown",
            "Judge-readable “why this forecast” notes, not fake SHAP claims",
        ],
        [
            "4",
            "Cybersecurity narrative + MITRE",
            "Pranshu",
            "Evidence-backed ATT&amp;CK table + forecast-to-response story",
        ],
        [
            "5",
            "Backend/API completion decisions",
            "Pulkit",
            "Which remaining endpoints become real; clean contract",
        ],
        [
            "6",
            "Dashboard hardening",
            "Pulkit, with Pranshu copy for risk language",
            "Real vs mock labels; clearer multi-horizon visuals",
        ],
        [
            "7",
            "Offline demo preparation",
            "Pulkit + Priyanshi repeatability, Ankita model freeze",
            "Repeatable input → prediction → horizon → risk → explanation flow",
        ],
        [
            "8",
            "SIH PPT / presentation prep",
            "All six, role-aligned speaking points",
            "Simple story + honest limits + per-member Q&amp;A",
        ],
    ]
    s.append(
        simple_table(
            ["#", "Priority", "Who", "Expected output"],
            priorities,
            col_widths=[0.07 * CONTENT_W, 0.28 * CONTENT_W, 0.28 * CONTENT_W, 0.37 * CONTENT_W],
            header_left=True,
        )
    )
    s.append(spacer(6))
    s.append(callout("day3", "Pehle comparison audit aur H500 honesty. PPT unke bina overclaim ho jayegi."))
    s.append(P("Day 3 member assignment (aligned roles, no random extra work)", "h2"))
    s.append(
        simple_table(
            ["Member", "Day 3 objective", "Explain to judges"],
            [
                ["Pranshu", "Narrative + verified MITRE + horizon meaning", "Forecast ka defence meaning, H500 limit, mapping status"],
                ["Pulkit", "API decisions, mock/real UI, demo choreography", "4 real endpoints, Attack Forecast live, baaki mock"],
                ["Pragati", "Protocol/split freeze + leakage note + feature pack", "Episode split, 0 observation DDoS, leakage caveat"],
                ["Ankita", "H500 investigation + demo horizon recommendation", "GRU design, thresholds, why epoch 1, H500 FAR"],
                ["Riddhi", "Comparability audit + two-table metric discipline", "TEST protocol, FAR, early-warning ≠ F1"],
                ["Priyanshi", "Rerun safety + demo repeatability + artifact freeze", "Seed 42, hashes, TEST not used in training"],
            ],
            col_widths=[0.16 * CONTENT_W, 0.42 * CONTENT_W, 0.42 * CONTENT_W],
            header_left=True,
        )
    )
    return s


def ppt_story():
    s = []
    s += heading(1, "18. SIH presentation preparation", "ppt")
    s.append(
        P(
            "PPT technical dump nahi honi chahiye. Story ye hai: "
            "network traffic se future attack state forecast, multiple horizons, "
            "held-out TEST par evidence, working offline demo, honest limitations.",
            "body",
        )
    )
    s.append(P("Suggested 7-beat story", "h2"))
    s.append(
        bullets(
            [
                "Problem: attacks ko sirf start hone ke baad catch karna late hai.",
                "Idea: last 100 flows se next 50/100/200/500 forecast.",
                "Data honesty: episode split, no observation DDoS, leakage caveat.",
                "Model: Multi-Horizon GRU, validation thresholds, TEST once.",
                "Results: H200 strongest balanced classification; H500 FAR 99.33% limitation.",
                "System: real Attack Forecast demo, not a fake live SOC.",
                "Next: explainability, fair comparison, demo polish.",
            ]
        )
    )
    s.append(P("Har member 30-second version", "h2"))
    s.append(
        kv_table(
            [
                ("Pranshu", "Main forecast ko DDoS behaviour se jodta hoon, IDS nahi forecasting."),
                ("Pulkit", "Main model ko FastAPI + Attack Forecast page se demo-ready karta hoon."),
                ("Pragati", "Main data ko temporally valid windows aur episode split mein convert karti hoon."),
                ("Ankita", "Main 4-horizon GRU train karti hoon jo future attack state predict kare."),
                ("Riddhi", "Main TEST metrics aur early-warning ko alag-alag, leakage-safe evaluate karti hoon."),
                ("Priyanshi", "Main ensure karti hoon ki wahi seed, wahi split, wahi hash dubara aaye."),
            ]
        )
    )
    s.append(spacer(4))
    s.append(
        callout(
            "warning",
            "PPT mein mat likho: live production network, perfectly leakage-free, all dashboard pages real, "
            "H500 best early-warning, MITRE mapping complete, ya 273-vs-2703 comparison as final proof.",
        )
    )
    return s


def close_story():
    s = []
    s += heading(1, "19. Final project status / next milestone", "close")
    s.append(
        P(
            "Day 2 milestone <b>achieved</b>: predictive multi-horizon model + audited TEST metrics + "
            "reproducible checkpoint + real inference demo path. "
            "Day 3 milestone: judge-ready honesty layer — comparable evaluation, H500 decision, "
            "explainable cyber story, cleaner demo.",
            "body",
        )
    )
    s.append(
        KeepTogether(
            [
                simple_table(
                    ["Layer", "Day 2 state", "Day 3 next milestone"],
                    [
                        ["Data", "Validated 21-episode working set, 18 OK window audit", "Leakage note + protocol freeze"],
                        ["Model", "MH GRU trained, thresholds locked, epoch-1 checkpoint", "H500 decision without metric hiding"],
                        ["Evaluation", "TEST classification + early-warning, n=3", "Apples-to-apples audit"],
                        ["System", "4 real APIs, Attack Forecast connected", "Selective remaining APIs + mock labels"],
                        ["Story", "Forecast vs IDS document; MITRE IDs pending", "Verified mapping + judge script"],
                        ["Reliability", "Seed 42 rerun + matching hashes", "Freeze demo artifacts"],
                    ],
                    col_widths=[0.18 * CONTENT_W, 0.42 * CONTENT_W, 0.40 * CONTENT_W],
                    header_left=True,
                )
            ]
        )
    )
    s.append(spacer(8))
    s.append(
        callout(
            "verified",
            "Agar koi teammate sirf ek cheez yaad kare: model future horizons forecast karta hai; "
            "H200 currently sabse balanced TEST classification deta hai; H500 ko FAR 0.9933 ke bina mat present karo; "
            "Attack Forecast real hai, poora dashboard nahi; TEST episodes sirf 19–21 hain.",
            title="Team bottom line",
        )
    )
    s.append(spacer(8))
    s.append(P("Appendix — key locked facts", "h2"))
    s.append(
        kv_table(
            [
                ("Problem", "SIH26153 — AI based Network Attack Forecasting"),
                ("Dataset", "CICIDS2017 DDoS working set"),
                ("TEST episodes", "19, 20, 21"),
                ("Thresholds", "H50 0.30 · H100 0.55 · H200 0.45 · H500 0.35"),
                ("Best epoch / val loss", "1 / 1.895873"),
                ("H200 TEST F1 / FAR", "0.7927 / 0.0761"),
                ("H500 TEST FAR", "0.9933"),
                ("Real APIs", "/health · /model-status · /demo-sequence · /predict"),
                ("Demo window", "Episode 20, flows 38790–38889, pre-attack vs start 39000"),
                ("This PDF source", "docs/day2_progress_report/generate_day2_progress_report.py"),
            ]
        )
    )
    s.append(spacer(10))
    s.append(
        P(
            "End of Day 2 internal progress report. Day 3 isi document ke “next” column se start hoga, "
            "completed Day 2 work ko rewrite karke nahi.",
            "small",
        )
    )
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
        tech_story,
        metrics_story,
        early_story,
        compare_story,
        system_story,
        git_story,
        member_pranshu,
        member_pulkit,
        member_pragati,
        member_ankita,
        member_riddhi,
        member_priyanshi,
        day3_story,
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
        title="SIH26153 Day 2 Progress Report — Internal Team Handoff",
        author="SIH26153 Team",
        subject="Day 2 progress + Day 3 roadmap",
    )

    cover_frame = Frame(
        28 * mm,
        24 * mm,
        PAGE_W - 28 * mm - 16 * mm,
        PAGE_H - 42 * mm - 24 * mm,
        id="cover",
    )
    body_frame = Frame(LEFT, BOTTOM + 4 * mm, CONTENT_W, PAGE_H - TOP - BOTTOM - 2 * mm, id="body")

    doc.addPageTemplates(
        [
            PageTemplate(id="cover", frames=[cover_frame], onPage=draw_cover),
            PageTemplate(id="body", frames=[body_frame], onPage=draw_header_footer),
        ]
    )

    doc.build(build_story())
    print(f"Wrote {OUT_PDF}")
    print(f"Size bytes: {OUT_PDF.stat().st_size}")


if __name__ == "__main__":
    main()
