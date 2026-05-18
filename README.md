# ⚡ VOLTA — AI Assistant for Electrical & Computer Engineers

<div align="center">

![VOLTA Banner](https://img.shields.io/badge/VOLTA-Electrical%20AI%20Assistant-orange?style=for-the-badge&logo=lightning&logoColor=white)

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg?style=flat-square&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=flat-square)](https://ollama.com)
[![DeepSeek](https://img.shields.io/badge/DeepSeek--R1-7B-purple?style=flat-square)](https://github.com/deepseek-ai)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/brijeshpatel271/volta-elec-ai/pulls)

**100% Free · Runs Locally · No API Keys · No Cloud · No Cost · Ever.**

*A free, locally-hosted AI engineering expert that handles circuit analysis, PLC/SCADA programming, control systems, signal processing, 3D design guidance, embedded coding, and more — all through a conversational interface.*

[🚀 Get Started](#-quick-start) · [✨ Features](#-features) · [🏗 Architecture](#-architecture) · [📄 Research Paper](#-research-paper) · [🤝 Contributing](#-contributing)

</div>

---

## 🎯 What is VOLTA?

VOLTA (**V**ersatile **O**pen-source **L**LM for **T**echnical **A**ssistance) is a specialized AI assistant designed from the ground up for **electrical and computer engineers**.

Unlike ChatGPT or other general-purpose AI tools, VOLTA:

- 🧠 **Thinks like an engineer** — asks clarifying questions, shows step-by-step math, cites IEC/IEEE standards
- 🐍 **Runs code for you** — writes and executes SciPy, NumPy, SymPy, Matplotlib instantly
- 🔒 **Stays on your machine** — no data sent to any server, ever
- 💸 **Costs nothing** — built entirely on free, open-source tools
- 📚 **Knows your domain** — circuit analysis, PLC ladder logic, Bode plots, PCB design, SCADA, embedded C/Python

> **Built by an engineer, for engineers.** VOLTA started as a Masters research project and grew into a full open-source platform.

---

## ✨ Features

### 🤖 AI Engineering Expert
- Covers **20+ ECE domains**: circuits, power systems, control theory, signal processing, PLC, SCADA, embedded, PCB, 3D design
- Custom-engineered system prompt that makes the AI behave as a senior electrical engineer
- Always shows **step-by-step mathematical derivations**
- Recommends **specific components with part numbers**
- References **IEC, IEEE, and NFPA standards** where applicable

### 🐍 Live Python Code Execution
- VOLTA writes SciPy / NumPy / SymPy / Matplotlib code **and runs it instantly**
- Plots and numerical results appear inline in the chat
- Sandboxed execution — safe and isolated from your system

### 💬 Clean Chat Interface
- Streaming token-by-token responses (like ChatGPT)
- **15+ pre-built example prompts** across all ECE domains
- Model switcher — hot-swap between any local Ollama model
- Temperature control — tune for precision (0.2) vs creativity (0.7)
- Session export to **Markdown** for engineering notebooks

### 🔒 100% Private & Offline
- All inference runs locally via **Ollama + DeepSeek-R1 7B**
- Zero cloud dependency after initial model download
- Your queries never leave your machine

### 📄 Backed by Research
- Full **IEEE-format journal paper** included in `/paper`
- Documented architecture, evaluation, and Phase 2 roadmap
- Citable for academic work

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────┐
│              VOLTA System Architecture               │
├─────────────────────────────────────────────────────┤
│  Layer 4: Streamlit Web Interface                   │
│           Chat UI · Streaming · Export · Examples   │
├─────────────────────────────────────────────────────┤
│  Layer 3: Tool Integration                          │
│           Python Executor · SciPy · SymPy · Plots  │
├─────────────────────────────────────────────────────┤
│  Layer 2: Domain Knowledge Engineering              │
│           ECE System Prompt · 20+ Domains           │
├─────────────────────────────────────────────────────┤
│  Layer 1: Local LLM (Ollama + DeepSeek-R1 7B)      │
│           Offline · Private · Free                  │
└─────────────────────────────────────────────────────┘
```

### Free Tool Stack vs Commercial Equivalents

| Function | VOLTA (Free) | Commercial Equivalent |
|---|---|---|
| LLM Inference | DeepSeek-R1 7B via Ollama | OpenAI GPT-4, Claude API |
| Math & Simulation | Python + NumPy + SciPy + SymPy | MATLAB |
| Circuit Simulation | Ngspice / LTspice | PSpice (Cadence) |
| Control Systems | Python-control | MATLAB Control Toolbox |
| PCB Design | KiCad | Altium Designer |
| 3D Modeling | FreeCAD / OpenSCAD | SolidWorks |
| PLC Programming | OpenPLC Runtime | TIA Portal (Siemens) |
| SCADA | ScadaBR / OpenSCADA | Wonderware / Ignition |
| Web Interface | Streamlit | Custom / Proprietary |
| RAG Pipeline *(Phase 2)* | LlamaIndex + ChromaDB | Azure AI Search |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- 8GB RAM minimum (16GB recommended)
- [Ollama](https://ollama.com/download) installed

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/brijeshpatel271/volta-elec-ai.git
cd volta-elec-ai

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Download the AI model (~4.7 GB, one time only)
ollama pull deepseek-r1:7b

# 4. Start Ollama server (keep this terminal open)
ollama serve

# 5. Launch VOLTA in a new terminal
python -m streamlit run app.py
```

Your browser opens at **http://localhost:8501** automatically. ⚡

> **Low RAM?** Use the lighter model instead: `ollama pull deepseek-r1:1.5b`

---

## 💡 Example Prompts to Try

Once VOLTA is running, try these in the chat:

```
⚡ Circuit Analysis
"Calculate the Thevenin equivalent of a 12V source with 4Ω and 6Ω resistors"

🏭 PLC Programming  
"Write IEC 61131-3 ladder logic for a motor starter with forward/reverse control"

📊 Control Systems
"Plot the Bode diagram for a 2nd order system with ωn=10 rad/s and ζ=0.5"

🔌 Power Systems
"Design a transformer for 11kV to 415V, 500kVA, calculate all parameters"

💻 Embedded Systems
"Write Arduino PID controller code for a temperature sensor"

📡 Signal Processing
"Design a Butterworth low-pass filter at 1kHz cutoff, order 4"
```

---

## 📁 Project Structure

```
volta-elec-ai/
├── app.py                      ← Main Streamlit application
├── requirements.txt            ← Python dependencies
├── prompts/
│   └── system_prompt.py        ← Engineering expert persona & rules
├── utils/
│   ├── ollama_client.py        ← Local Ollama LLM connection
│   ├── code_executor.py        ← Sandboxed Python runner
│   └── session.py              ← Chat history & export
├── paper/
│   └── VOLTA_Journal_Paper.docx ← IEEE-format research paper
├── LICENSE                     ← MIT License
└── README.md                   ← This file
```

---

## 🗺 Roadmap

### ✅ Phase 1 — MVP (Complete)
- [x] Local LLM via Ollama + DeepSeek-R1
- [x] ECE domain system prompt (20+ areas)
- [x] Sandboxed Python code execution
- [x] Streamlit chat interface with streaming
- [x] Session export to Markdown
- [x] IEEE journal paper

### 🔄 Phase 2 — RAG Knowledge Base (In Progress)
- [ ] IEEE/IEC standards ingestion
- [ ] Open-access textbook integration (Chapman, Nilsson)
- [ ] PLC manufacturer manuals (Siemens, Allen-Bradley)
- [ ] LlamaIndex + ChromaDB vector pipeline
- [ ] Citation display in responses

### 🔮 Phase 3 — Advanced Tools
- [ ] KiCad schematic generation API
- [ ] OpenPLC ladder logic export
- [ ] Improved UI with dark engineering theme
- [ ] Multi-user support
- [ ] Mobile-friendly interface

---

## 📄 Research Paper

A full **IEEE-format journal paper** documenting VOLTA's architecture, implementation, and evaluation is included in the `/paper` directory.

**Title:** *VOLTA: An Open-Source AI-Powered Engineering Assistant for Electrical and Computer Engineering Education and Practice*

**Author:** Brijesh K. Patel, Graduate Student, Electrical & Computer Engineering

**Abstract:** This paper presents VOLTA, a free, locally-hosted AI assistant designed specifically for ECE tasks. VOLTA integrates domain-specific system prompting, sandboxed Python code execution, and a multi-layer RAG architecture to provide expert-level responses across circuit analysis, PLC/SCADA programming, signal processing, control systems, and 3D/PCB design guidance...

📥 **[Download Paper](paper/VOLTA_Journal_Paper.docx)**

### Cite This Work

```bibtex
@misc{patel2026volta,
  title   = {VOLTA: An Open-Source AI-Powered Engineering Assistant 
              for Electrical and Computer Engineering Education and Practice},
  author  = {Patel, Brijesh K.},
  year    = {2026},
  url     = {https://github.com/brijeshpatel271/volta-elec-ai},
  note    = {GitHub repository, MIT License}
}
```

---

## 🤝 Contributing

Contributions are very welcome! VOLTA is a research project and community tool.

```bash
# Fork the repo, then:
git checkout -b feature/your-feature-name
git commit -m "Add your feature"
git push origin feature/your-feature-name
# Open a Pull Request
```

**Good first contributions:**
- Add new example prompts to the library
- Improve the UI design
- Add support for new Ollama models
- Write domain-specific test cases
- Translate the README

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

You are free to use, modify, and distribute VOLTA for any purpose, including commercial use, as long as the original license is included.

---

## 🙏 Acknowledgments

VOLTA is built on the shoulders of these amazing open-source projects:

- [Ollama](https://ollama.com) — Local LLM serving
- [DeepSeek-R1](https://github.com/deepseek-ai/DeepSeek-R1) — The reasoning model powering VOLTA
- [Streamlit](https://streamlit.io) — Web interface framework
- [LlamaIndex](https://llamaindex.ai) — RAG pipeline (Phase 2)
- [ChromaDB](https://www.trychroma.com) — Vector database (Phase 2)
- [SciPy](https://scipy.org) / [NumPy](https://numpy.org) / [SymPy](https://sympy.org) — Scientific computing

---

<div align="center">

**⭐ If VOLTA helps you, please star the repo — it helps others find it!**

Made with ❤️ by [Brijesh K. Patel](https://github.com/brijeshpatel271)

*Graduate Student · Electrical & Computer Engineering*

</div>
