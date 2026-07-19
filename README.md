# Multi-Specialty Clinical Diagnostic Console

[![Python Version](https://shields.io)](https://python.org)
[![Framework](https://shields.io)](https://palletsprojects.com)
[![ML Library](https://shields.io)](https://scikit-learn.org)

An advanced Flask-based data platform covering **17 distinct medical specialty modules**, engineered as a highly structured, form-based clinical dashboard.

> ⚠️ **EDUCATIONAL / DEMONSTRATION PROJECT ONLY**
> This application is not an FDA-cleared or CE-marked medical device. It is not validated for clinical use and is not a substitute for professional clinical judgment. Please read **[ROADMAP.md](ROADMAP.md)** for a detailed analysis of the multi-year regulatory, clinical-validation, and safety processes required to transition an experimental codebase into a certified medical device.

---

## 🛠️ Architecture & Core Mechanics

Where clean, real public datasets were accessible, modules execute a **real, probability-calibrated, trained Scikit-Learn model** complete with live feature-importance reporting. For modules without baseline datasets, the platform executes **real, named, and medically validated clinical scoring tools**. Every asset is explicitly labeled within the user interface to ensure maximum data transparency.

### Core Interfaces
*   **`/dashboard` (Primary Link)** — Structured patient data intake forms mapped per specialty. Includes a unified *Patient Baseline* panel, support for single-specialty or full 17-module batch pipeline execution, and outputs calibrated confidence intervals alongside uncertainty banding.
*   **`/classic-chat`** — Legacy conversational UI retained strictly for historical regression testing and UI/UX comparison metrics.

---

## 🔍 Provenance & Sandboxing Data
This platform operates completely inside a network-isolated environment (outbound traffic is blocked at the egress proxy layer). All model weights, pipeline configurations, and evaluation parameters are securely packaged and executed locally to protect mock data integrity.
