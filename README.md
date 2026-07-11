# 🧠 Algothink Chaos Engine

An experimental rule-based quantitative market-research prototype for automated NSE stock scanning, price-shape analysis, signal auditing, and evidence collection.

> **Project Status:** Active Development — Phase 1 Baseline Prototype

---

## 📌 Overview

Algothink Chaos Engine explores the following research cycle:

```text
PREDICT → AUDIT → LEARN → IMPROVE
```

The current prototype automatically retrieves market data for a selected group of NSE-listed stocks, converts recent price movements into normalized shapes, compares those shapes with stored outcome patterns using Dynamic Time Warping (DTW), and displays the latest results through a Streamlit dashboard.

The project originally began as a Google Sheets and Apps Script experiment. It later evolved into local Python experiments and then into the current GitHub Actions and Streamlit-based architecture.

---

## ⚙️ Current Working Features

- Automated market-data retrieval using Yahoo Finance
- Automated scanning of a selected NSE stock universe
- 14-day price-shape extraction
- Z-score-based price-pattern normalization
- Dynamic Time Warping (DTW) pattern comparison
- Experimental signal generation
- Fixed experimental target and stop-loss levels
- Automated morning scan at **8:45 AM IST**
- Automated evening audit at **3:45 PM IST**
- Scheduled execution using GitHub Actions
- JSON-based current signal and pattern-memory storage
- Automatic repository updates through GitHub Actions
- Streamlit dashboard for viewing current signals and price shapes

---

## 🔄 Current Workflow

```text
Yahoo Finance Market Data
             ↓
     Morning Market Scan
             ↓
   Price-Shape Extraction
             ↓
    DTW Pattern Comparison
             ↓
 Experimental Signal Output
             ↓
      signals.json Update
             ↓
      Evening Audit
             ↓
  lesson_ledger.json Update
             ↓
    Streamlit Dashboard
```

The morning workflow runs before the normal NSE trading session, while the evening audit runs after the normal market close.

---

## 📁 Current Project Structure

```text
stock-predictor-quant/
│
├── .github/
│   └── workflows/
│
├── app.py
├── production_pipeline.py
├── download_data.py
├── process_geometry.py
├── chaos_engine.py
├── evaluate_probability.py
├── market_memory.db
├── signals.json
├── lesson_ledger.json
└── .gitignore
```

---

## ⚠️ Current Limitations

This repository contains an early experimental baseline that is still under development.

Current limitations include:

- Successfully processed stocks currently begin with a default `BUY` verdict unless rejected by stored pattern memory.
- The current signal logic does not yet use a complete trend, momentum, RSI, volume, volatility, or confidence-scoring system.
- A new morning run can replace the previous contents of `signals.json`.
- Permanent prediction and outcome history has not yet been implemented.
- The current lesson ledger stores limited pattern information rather than complete contextual lessons.
- Successful patterns are not currently stored as lessons.
- Long-term performance metrics are not yet available.
- Target, stop-loss, and time-stop values are fixed experimental assumptions.
- NSE holiday handling is currently limited.
- The current system is a rule-based research prototype, not a trained machine-learning model.

---

# 🗺️ Development Roadmap

## Phase 1 — Rule-Based Evidence Engine

**Status: Current Phase**

The current goal is to improve the working baseline while collecting reliable evidence.

### Planned Improvements

- Add explainable rule-based scoring
- Evaluate trend, momentum, RSI, volume, volatility, and recent returns
- Replace the default `BUY` behavior with evidence-based verdicts
- Preserve permanent prediction history
- Store actual market outcomes separately
- Compare predictions with actual outcomes
- Store contextual lessons without overwriting previous evidence
- Record successful, failed, and stagnant outcomes
- Track suitable performance metrics over time
- Improve market-calendar and holiday handling
- Add dependency management and automated testing
- Add a separate personal portfolio-tracking section

### Phase 1 Goal

> Build an explainable system that collects reliable evidence, preserves its history, and improves through recorded outcomes.

---

## Phase 2 — Evidence-Improved Prototype

**Status: Future Work**

Phase 2 will begin only after sufficient evidence has been collected during Phase 1.

### Planned Work

- Study the evidence collected during Phase 1
- Identify useful, weak, and misleading rules
- Improve scoring weights and decision thresholds
- Evaluate whether DTW lesson memory improves future decisions
- Review target, stop-loss, and holding-period assumptions
- Backtest improved rules
- Compare the improved prototype with the original Phase 1 baseline
- Test improvements using unseen market periods

### Phase 2 Goal

> Build and evaluate an improved prototype based on evidence collected during Phase 1.

The current roadmap ends at Phase 2. Any later direction will be decided only after sufficient evidence has been collected and evaluated.

---

## 🧪 Project Evolution

```text
Google Sheets + Apps Script Experiment
                  ↓
       Local Python Experiments
                  ↓
      GitHub Actions Automation
                  ↓
        Streamlit Dashboard
```

The original spreadsheet experiment used Google Sheets, Google APIs, Yahoo Finance data, Apps Script, and scheduled morning and evening triggers.

The project was later moved from Google Sheets to Python and GitHub to support more maintainable automation, structured experimentation, evidence collection, and future development.

---

## 🚧 Development Status

This project is actively evolving.

Features listed under **Current Working Features** are part of the present prototype. Features listed under the **Development Roadmap** are planned and should not be interpreted as currently implemented.

---

## ⚖️ Disclaimer

> **This project is intended solely for educational, research, and experimental purposes.**

The signals, verdicts, targets, stop-losses, audits, patterns, lessons, and dashboard outputs generated by this project are experimental and unvalidated research outputs.

They do not constitute financial, investment, trading, or professional advice and should not be used as the basis for real-money financial decisions.

Past observations, simulated outcomes, experimental results, and historical patterns do not guarantee future performance.
