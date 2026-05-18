# ⚡ VOLTA — Electrical Engineering AI Assistant
### Phase 1 MVP · 100% Free · Runs Locally

VOLTA is your AI-powered electrical and computer engineering expert.  
It runs entirely on your machine — no API costs, no data sent to the cloud.

---

## 🗂 Project Structure

```
elec_ai/
├── app.py                      ← Main Streamlit application (run this)
├── requirements.txt            ← Python dependencies
├── prompts/
│   └── system_prompt.py        ← Engineering expert persona & rules
├── utils/
│   ├── ollama_client.py        ← Talks to local Ollama LLM server
│   ├── code_executor.py        ← Safely runs Python math/simulation code
│   └── session.py              ← Chat history, exports, example prompts
└── README.md                   ← This file
```

---

## 🚀 Setup (one time only)

### Step 1 — Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Install Ollama
Download and install from: https://ollama.com/download  
Available for Windows, macOS, and Linux.

### Step 3 — Download an AI model
Open a terminal and run ONE of these (pick based on your PC's RAM):

```bash
# BEST for engineering/math (8GB RAM minimum recommended)
ollama pull deepseek-r1:7b

# Lighter option (4GB RAM)
ollama pull deepseek-r1:1.5b

# Alternative: Meta LLaMA (8GB RAM)
ollama pull llama3.1:8b

# Fast, lightweight (4GB RAM)
ollama pull mistral:7b
```

> **Which model to choose?**
> - DeepSeek-R1 is the strongest for STEM reasoning and math
> - LLaMA 3.1 is great for code generation
> - Mistral is fastest if your computer is slower

### Step 4 — Start Ollama server
```bash
ollama serve
```
Leave this terminal window open.

### Step 5 — Launch VOLTA
Open a new terminal in this folder and run:
```bash
streamlit run app.py
```

Your browser will open automatically at **http://localhost:8501** ⚡

---

## 💡 What VOLTA Can Do (Phase 1)

| Capability | Examples |
|---|---|
| **Circuit Math** | Thevenin/Norton, mesh analysis, power factor, impedance |
| **Power Systems** | Transformer sizing, cable sizing, motor starting, 3-phase |
| **Control Systems** | PID design, Bode plots, root locus, Laplace transforms |
| **Signal Processing** | FFT, filters, Z-transform, sampling |
| **PLC Code** | IEC 61131-3 Ladder, Structured Text, Function Block |
| **SCADA** | Modbus RTU/TCP, OPC-UA, HMI design, protocol setup |
| **Embedded Code** | Arduino, ESP32, STM32 — C/C++/MicroPython |
| **Python Math** | Auto-runs NumPy/SciPy/SymPy/matplotlib code |
| **Component Selection** | Recommends real parts with part numbers and sources |
| **Design Guidance** | KiCad PCB, FreeCAD enclosures, wiring diagrams |

---

## 🔢 Python Code Execution

When VOLTA generates Python code (e.g., to plot a Bode diagram or solve a circuit),
the app automatically runs it and shows the output and charts — just like Jupyter Notebook.

**Libraries available in the executor:**
- `numpy` (np) — arrays, linear algebra
- `scipy` — signal processing, optimization, control
- `sympy` (sp) — symbolic math (Laplace, Z-transforms, algebra)
- `matplotlib` (plt) — plotting

Example: ask VOLTA to "Plot the frequency response of a 2nd order RLC band-pass filter"
and it will write and execute the Python code, showing the Bode plot.

---

## ⚙️ Configuration

All settings are in the sidebar:
- **Model**: Select any Ollama model you have installed
- **Temperature**: 0.2–0.4 for precise engineering answers, higher for brainstorming
- **Auto-run code**: Toggle automatic Python execution on/off
- **Domain filter**: Focus example prompts on a specific domain
- **Export**: Download your session as Markdown

---

## 🛣 What's Coming (Phase 2 & 3)

- **Phase 2**: RAG knowledge base — feed VOLTA textbooks, IEEE standards, datasheets
- **Phase 3**: Tool integrations — KiCad scripting, OpenPLC code push, FreeCAD API
- **Phase 4**: Cloud deployment on Hugging Face Spaces (still free)

---

## 🐛 Troubleshooting

**"Ollama offline" in sidebar**
→ Run `ollama serve` in a terminal and keep it open.

**No models in dropdown**
→ Run `ollama pull deepseek-r1:7b` to download a model first.

**App won't start**
→ Make sure you installed requirements: `pip install -r requirements.txt`

**Responses are slow**
→ Normal for first response (model loads into RAM). Subsequent answers are faster.
→ Try a smaller model like `deepseek-r1:1.5b` or `mistral:7b`.

**Out of memory error**
→ Close other apps, or switch to a smaller model variant.

---

## 📦 Free Tools VOLTA Knows About

| Task | Free Tool | Link |
|---|---|---|
| PCB design | KiCad | https://kicad.org |
| 3D CAD | FreeCAD | https://freecad.org |
| Circuit simulation | LTspice | https://www.analog.com/ltspice |
| PLC programming | OpenPLC | https://openplcproject.com |
| SCADA | ScadaBR | https://www.scadabr.com.br |
| Math (MATLAB alternative) | Python + SciPy | https://scipy.org |
| Symbolic math | SymPy | https://sympy.org |
| Embedded dev | PlatformIO | https://platformio.org |

---

*VOLTA — built for engineers, by engineers. 100% local. 100% free.*
