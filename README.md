# AutoCIRepair: Repository-Level Automation for CI Build Repair using Multi-Agent Systems

## 📌 Overview

**AutoCIRepair** is a Large Language Model (LLM)-powered, multi-agent framework designed to automate the **fault localization** and **patch generation** for Continuous Integration (CI) build failures. This project addresses the challenge of debugging CI pipelines by extracting structured error insights from logs, identifying root causes, and synthesizing code patches that are automatically validated via CI workflow re-execution.

---

## 🔍 Problem Statement

Modern CI pipelines (e.g., GitHub Actions, Jenkins) frequently fail due to:

* Misconfigured YAML files
* Incompatible dependencies
* Faulty code integrations

Diagnosing these failures manually is slow, error-prone, and costly — especially when the build logs are unstructured and large. Existing automated repair systems focus on unit tests or static bugs, but **lack real CI context awareness**.

---

## 🧠 Proposed Solution

AutoCIRepair introduces a **multi-agent system** driven by LLMs and symbolic tools, consisting of three specialized agents:

### 1. **Error Context Extraction Agent**

* Parses raw CI logs using chunk-based tokenized segmentation
* Extracts structured error information: file paths, severity, traceback, job step
* Associates errors with CI workflow stages

### 2. **Debugger Agent**

* Consumes structured error + Git diffs from failed commits
* Suggests suspicious files via diff and log overlap
* Optionally expands call context using AST-based static analysis
* Localizes faults precisely (file/method/line-level)
* Outputs structured bug reports

### 3. **Developer Agent**

* Converts fault-localization output into minimal patch suggestions
* Validates patches by re-running CI via `act` tool (GitHub Actions emulator)
* Converts valid fixes into Git-compatible diff format (`git apply`-ready)

---

## ⚙️ Architecture Diagram

> 🧬 Modular LangChain-based Pipeline
> 📂 Input: `lca-ci-builds-repair` Dataset (real GitHub Actions failures)
> 🧠 Models: `GPT-4o-mini` for each agent
> ♻️ Output: Validated patch diffs with full CI pass

```
CI Logs ───▶ Error Extractor ───▶ Debugger ───▶ Developer ───▶ Patch + CI Pass
                  │               │               │
              Token Chunking    Git Diffs     CI Rerun via `act`
```

---

## 📆 Dataset Used

* **LCA-CI-Builds-Repair** (JetBrains Research):

  * 68 real-world CI failure cases across 32 open-source Python repositories
  * Includes: raw CI logs, commit diffs, YAML workflows, and human-written patch diffs
  * Evaluation based on: Patch success (Pass\@1), structural similarity, and log filtering precision

---

## 🔬 Methodology Summary

| Phase              | Details                                                                  |
| ------------------ | ------------------------------------------------------------------------ |
| Log Chunking       | Handles token limits via segmenting multi-MB logs                        |
| Context Extraction | Uses log patterns (`FATAL`, `Traceback`, `Error`, etc.) and step tracing |
| Git Diff Parsing   | Analyzes changed files between commit and parent                         |
| Fault Localization | Combines error context + diff + call graph reasoning                     |
| Patch Synthesis    | Regenerates files with minimal edits; wraps response in file diff        |
| Validation         | Runs full GitHub Actions CI pipeline using `act`                         |
| Diff Formatting    | Produces Git-usable patch files                                          |

---

## 🧪 Evaluation & Results

| Metric                          | Value                                                  |
| ------------------------------- | ------------------------------------------------------ |
| Pass\@1 (CI Fixed First Try)    | 28 / 68 failures (41.2%)                               |
| Valid Patch Generation          | 100% syntactically valid                               |
| Structural Alignment (vs Human) | \~0.16 token similarity                                |
| Tools Used                      | Python 3.13, GitPython, LangChain, `act` for CI replay |

---

## 📆 Tools & Technologies

* **LLMs**: GPT-4o-mini (April 2024)
* **Framework**: LangChain (Agent orchestration)
* **DevOps**: GitHub Actions, `act` CI runner, GitPython
* **Analysis**: AST parsing (Python), Call Graph Generation, Unified Diff Format
* **Benchmark**: JetBrains LCA CI Repair Dataset

---

## 📊 Key Contributions

* ✅ Repository-level patch synthesis (not just code snippets)
* ✅ End-to-end CI repair loop with actual validation
* ✅ Multi-agent reasoning (Error → Debug → Developer)
* ✅ Integrated AST, YAML, and log reasoning
* ✅ Real-world dataset benchmarking

---

## 🔭 Future Work

* Expand to other CI tools (e.g., Jenkins, GitLab CI)
* Cross-language support (JavaScript, Java, Rust)
* Memory optimization and prompt caching
* Smarter diff merging and test-aware repair

---

## 📀 Authors

**Sumit Kumar**
[i.sumitkumar@outlook.com](mailto:i.sumitkumar@outlook.com)
Master’s in Software Engineering, Concordia University

**Rabeya Khatun Muna**
[rabeykhatunmuna@gmail.com](mailto:rabeykhatunmuna@gmail.com)

---

## 📄 Citation

This project was developed as part of the SOEN 7481 course at Concordia University. Cite the report using:

```
Sumit Kumar, Rabeya Khatun Muna. 2025. Repository-Level Automation for CI Build Repair using Multi-Agent. SOEN 7481’25, Montreal, QC, Canada.
```

> 📄 **Read the full technical report**: [CI\_Build\_Repair\_paper.pdf](./report/CI_Build_Repair_paper.pdf)

---

## ❗Disclaimer

Code for this project is currently private due to collaborative research constraints. Demo or access available upon request.
