# Regulatory Roadmap — What "Real Medical Device" Actually Requires

This document exists because "do all 100%, make it a real medical device"
is a legitimate goal — but it's not a software task, and pretending
otherwise would set you up to either waste money or, worse, deploy
something that hurts someone and creates real legal liability. This is the
honest map of what stands between this codebase and that goal.

**Nothing in this document is legal advice.** It's a structural overview to
help you talk to the right professionals. Engage a regulatory consultant
and a healthcare/medical-device attorney before spending real money.

---

## 1. What this software is today

- 4 calibrated ML classifiers trained on small-to-medium public research
  datasets (158–1190 patients each), with honest cross-validated accuracy
  reported in `models/training_report.json`.
- 13 implementations of real, named, validated clinical scoring tools
  (qSOFA, PHQ-9, CHA₂DS₂-VASc, GOLD, ABCDE, APRI, WHO anemia criteria,
  etc.), but as *unsupervised software implementations* of tools that were
  validated for use *by a trained clinician interpreting the result*.
- A single-developer demo project with no clinical oversight, no
  institutional backing, and no track record.

This is a legitimate **research/educational prototype** and a reasonable
starting point for a **clinician-facing decision-support tool built with
proper oversight**. It is not currently close to something a patient
should rely on unsupervised.

## 2. Classify what you're actually building

Regulatory requirements depend heavily on which of these you mean:

| Category | Description | Regulatory burden |
|---|---|---|
| **Clinical Decision Support (CDS), non-device** | Tool used by a clinician who reviews underlying data themselves and isn't solely reliant on the software's suggestion | Lower — may qualify for FDA's CDS exemption (21st Century Cures Act, if criteria met) or EU equivalent. Still needs quality processes. |
| **Software as a Medical Device (SaMD)** | Output directly informs a diagnosis/treatment decision without the clinician independently reviewing the underlying basis | Full medical device regulatory pathway |
| **Direct-to-consumer diagnostic** | Patient uses it themselves with no clinician in the loop | Highest burden + product liability exposure; many jurisdictions effectively require this to go through full device clearance regardless of marketing language |

Given the current design (chat/dashboard giving direct "HIGH RISK" verdicts
with no clinician interpretation step), this currently reads as SaMD or
direct-to-consumer territory — the higher-burden categories.

## 3. The actual regulatory pathway (US example — FDA)

1. **Determine device classification** (Class I/II/III) based on risk —
   most diagnostic-support software lands in Class II.
2. **Predicate device search** — find a legally-marketed similar device to
   reference, or prepare for the longer De Novo pathway if there isn't one.
3. **510(k) premarket submission** (Class II) or **De Novo** (no
   predicate) — requires:
   - Software documentation per FDA's premarket software guidance
     (including a defined Software Level of Concern)
   - Verification & validation testing
   - Cybersecurity documentation
   - Clinical validation data demonstrating safety and effectiveness on a
     representative population (not the training data — independent,
     prospective or retrospective validation cohorts)
4. **Quality Management System** — ISO 13485 certification, design
   controls, risk management per ISO 14971, covering the entire software
   lifecycle going forward (not a one-time audit).
5. **Post-market surveillance** — ongoing adverse event monitoring and
   reporting obligations once cleared.

The EU path (CE marking under MDR 2017/745) is structurally similar with
different terminology (Notified Body review, Clinical Evaluation Report,
EUDAMED registration) and is widely considered more demanding for software
specifically since the 2021 MDR transition.

**Realistic timeline:** 18 months to 3+ years. **Realistic cost:** typically
low-to-high six figures USD for a single Class II SaMD pathway, dominated
by clinical validation studies and regulatory consulting/legal fees, not
software engineering.

## 4. Clinical validation — the part code can't shortcut

Cross-validated accuracy on a public research dataset (what
`training_report.json` reports) is necessary but nowhere near sufficient.
Real clinical validation needs:

- **External validation** on data the model never saw during development,
  ideally from different hospitals/populations than the training data, to
  catch overfitting and population bias.
- **Prospective validation** in some cases — testing the model
  going-forward on real incoming cases, not just retrospectively.
- **Subgroup performance analysis** — does it perform equally well across
  age, sex, ethnicity? A model that's 90% accurate overall but performs
  much worse on an underrepresented subgroup is a known, serious failure
  mode regulators specifically look for.
- **Comparison to standard of care** — does using this tool actually
  improve outcomes compared to not using it? This is usually the central
  question an IRB-approved clinical study answers.

This requires an Institutional Review Board (IRB), a clinical site or
partnership with one, and a study design — typically run with an academic
medical center or CRO (contract research organization), not built solo.

## 5. What you can do *right now*, legitimately

These are real, useful next steps that don't require a regulatory
submission:

1. **Partner with a clinician or institution early.** A practicing
   physician (ideally one in the relevant specialty) reviewing the rule
   engines and model outputs is the single highest-value, lowest-cost step
   available to you right now — it's how you'd find a wrong qSOFA cutoff
   or a clinically meaningless feature before a regulator or, worse, a
   patient does.
2. **Position it explicitly as a CDS tool for clinician use**, not a
   consumer diagnosis app. Different risk profile, possibly exempt from
   full SaMD requirements if it meets the Cures Act CDS criteria (this
   needs a lawyer's read on your specific design, not a guess from me).
3. **Get bigger, better, externally-sourced datasets** for the 4 ML
   specialties, and add real external validation once you have them.
4. **Talk to a regulatory consultant for an initial classification
   opinion** before investing further — this is usually a fixed, bounded
   cost (a few thousand dollars) and tells you which path you're actually
   on before you commit to it.
5. **Keep the uncertainty/indeterminate banding and confidence reporting**
   this version added — regulators specifically scrutinize whether
   software overclaims certainty, and software that visibly says "I don't
   know, ask a clinician" is a materially stronger safety case than
   software that always picks a side.

## 6. Bottom line

There is no commit, deploy, or rebrand that turns this into a medical
device. The path is real, walkable, and this codebase is a legitimate
starting point for it — but it runs through clinicians, validation
studies, and regulatory submissions, not through me. Happy to keep
improving the engineering (more rigor, better explainability, more honest
uncertainty handling, cleaner audit trails) for as long as that's useful to
you.
