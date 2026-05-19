"""
rag/build_knowledge_base.py
────────────────────────────────────────────────────────
Run this script to populate VOLTA's knowledge base.

Usage:
    python rag/build_knowledge_base.py

It will:
1. Ingest all PDFs/TXTs from rag/documents/
2. Scrape free online textbooks (AllAboutCircuits etc.)
3. Store everything in ChromaDB vector store

Add your own PDFs to rag/documents/ before running!
────────────────────────────────────────────────────────
"""

import sys
import time
from pathlib import Path

# Add parent to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.ingestor import (
    DOCUMENTS_DIR,
    FREE_SOURCES,
    get_chroma_collection,
    get_store_stats,
    ingest_file,
    ingest_url,
    add_chunks_to_store,
    load_metadata,
    save_metadata,
    file_hash,
)


def print_banner():
    print("\n" + "=" * 60)
    print("  ⚡ VOLTA — Knowledge Base Builder")
    print("  Phase 2: RAG Ingestion Pipeline")
    print("=" * 60 + "\n")


def check_dependencies() -> bool:
    """Check all required packages are installed."""
    missing = []
    packages = {
        "chromadb": "chromadb",
        "sentence_transformers": "sentence-transformers",
        "pypdf": "pypdf",
        "requests": "requests",
    }
    for module, pip_name in packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(pip_name)

    if missing:
        print("❌ Missing packages. Install with:")
        print(f"   pip install {' '.join(missing)}\n")
        return False

    print("✅ All dependencies installed\n")
    return True


def ingest_local_documents(collection, metadata: dict) -> int:
    """Ingest all PDFs and text files from the documents folder."""
    total = 0
    files = list(DOCUMENTS_DIR.glob("**/*.pdf")) + \
            list(DOCUMENTS_DIR.glob("**/*.txt")) + \
            list(DOCUMENTS_DIR.glob("**/*.md"))

    if not files:
        print("📁 No local documents found in rag/documents/")
        print("   → Add PDFs (textbooks, standards, manuals) to that folder and re-run\n")
        return 0

    print(f"📚 Found {len(files)} local document(s):")

    for path in files:
        fhash = file_hash(path)
        doc_key = str(path)

        # Skip if already ingested with same content
        if metadata.get(doc_key) == fhash:
            print(f"   ⏭  Skipping (unchanged): {path.name}")
            continue

        print(f"   📄 Ingesting: {path.name} ... ", end="", flush=True)

        # Try to detect domain from folder name
        domain = path.parent.name if path.parent != DOCUMENTS_DIR else "General"

        chunks = ingest_file(path, domain=domain)
        if chunks:
            added = add_chunks_to_store(collection, chunks)
            metadata[doc_key] = fhash
            print(f"{added} chunks ✓")
            total += added
        else:
            print("⚠ No text extracted")

    print()
    return total


def ingest_web_sources(collection, metadata: dict) -> int:
    """Scrape free online engineering textbooks and references."""
    total = 0
    print("🌐 Ingesting free online engineering resources:")

    for domain, sources in FREE_SOURCES.items():
        print(f"\n   [{domain}]")
        for source in sources:
            url_key = f"web:{source['url']}"

            # Web sources re-ingested if older than 7 days
            if url_key in metadata:
                age = time.time() - metadata[url_key].get("ingested_at", 0)
                if age < 7 * 24 * 3600:
                    print(f"   ⏭  Skipping (fresh): {source['title']}")
                    continue

            print(f"   🔗 Scraping: {source['title']} ... ", end="", flush=True)

            chunks = ingest_url(
                url=source["url"],
                title=source["title"],
                domain=source["domain"],
            )

            if chunks:
                added = add_chunks_to_store(collection, chunks)
                metadata[url_key] = {
                    "ingested_at": time.time(),
                    "chunks": added,
                }
                print(f"{added} chunks ✓")
                total += added
            else:
                print("⚠ Could not scrape")
                time.sleep(1)

            time.sleep(0.5)  # Be polite to servers

    print()
    return total


def ingest_builtin_knowledge(collection, metadata: dict) -> int:
    """
    Ingest built-in engineering reference text that's always available.
    This covers key formulas, standards references, and domain knowledge
    that VOLTA should always have access to.
    """
    meta_key = "builtin_v2"
    if meta_key in metadata:
        print("⏭  Built-in knowledge already ingested\n")
        return 0

    print("🔧 Ingesting built-in engineering knowledge base...")

    builtin_docs = [
        {
            "domain": "Circuit Analysis",
            "title": "Core Circuit Analysis Formulas",
            "text": """
CIRCUIT ANALYSIS — CORE REFERENCE

OHM'S LAW: V = I × R (Voltage = Current × Resistance)
POWER: P = V × I = I²R = V²/R
KIRCHHOFF'S VOLTAGE LAW (KVL): Sum of all voltages around a closed loop = 0
KIRCHHOFF'S CURRENT LAW (KCL): Sum of currents entering a node = Sum leaving

SERIES CIRCUITS:
- Total resistance: Rt = R1 + R2 + R3 + ...
- Current same through all elements
- Voltage divides: Vn = V_total × (Rn / Rt)

PARALLEL CIRCUITS:
- Total resistance: 1/Rt = 1/R1 + 1/R2 + ...  (Two resistors: Rt = R1×R2/(R1+R2))
- Voltage same across all branches
- Current divides: In = I_total × (Rt / Rn)

THEVENIN'S THEOREM:
- Vth = Open circuit voltage at terminals
- Rth = Resistance seen at terminals with sources zeroed (V→short, I→open)
- Replace complex network with Vth in series with Rth

NORTON'S THEOREM:
- In = Short circuit current at terminals
- Rn = Rth (same as Thevenin)
- Replace complex network with In in parallel with Rn

SUPERPOSITION: Response due to each independent source alone, then sum all

CAPACITORS:
- Q = C × V,  I = C × dV/dt
- Energy stored: E = ½CV²
- In DC steady state: open circuit
- Series: 1/Ct = 1/C1 + 1/C2; Parallel: Ct = C1 + C2

INDUCTORS:
- V = L × dI/dt
- Energy stored: E = ½LI²
- In DC steady state: short circuit
- Series: Lt = L1 + L2; Parallel: 1/Lt = 1/L1 + 1/L2

AC CIRCUITS:
- Impedance: Z = R + jX (j = √-1)
- Inductive reactance: XL = 2πfL = ωL
- Capacitive reactance: XC = 1/(2πfC) = 1/(ωC)
- RLC series resonance: f0 = 1/(2π√LC), Z=R at resonance
- Power factor: PF = cos(θ) = R/|Z|
- Active power: P = V×I×cos(θ) [Watts]
- Reactive power: Q = V×I×sin(θ) [VAR]
- Apparent power: S = V×I [VA]
- S² = P² + Q²
""",
        },
        {
            "domain": "Power Systems",
            "title": "Power Systems Engineering Reference",
            "text": """
POWER SYSTEMS — CORE REFERENCE

THREE-PHASE SYSTEMS:
- Line voltage (VL) = √3 × Phase voltage (Vph) — Star/Wye connection
- Line current (IL) = Phase current (Iph) — Star connection
- Line voltage (VL) = Phase voltage (Vph) — Delta connection
- Line current (IL) = √3 × Phase current (Iph) — Delta connection
- 3-phase power: P = √3 × VL × IL × cos(θ) = 3 × Vph × Iph × cos(θ)

TRANSFORMERS:
- Turns ratio: a = N1/N2 = V1/V2 = I2/I1
- Impedance transformation: Z1 = a² × Z2
- Efficiency: η = Pout/Pin = Pout/(Pout + Pcore + Pcopper)
- Voltage regulation: VR% = (VNL - VFL)/VFL × 100%

MOTORS (INDUCTION):
- Synchronous speed: Ns = 120f/P (rpm), where P = number of poles
- Slip: s = (Ns - Nr)/Ns
- Rotor frequency: fr = s × f
- Efficiency: η = Pshaft / P_electrical_input
- FLA (Full Load Amps): I = P/(√3 × VL × η × PF) for 3-phase
- Starting current typically 600-700% of FLA

CABLE SIZING (IEC 60364 / NEC):
- Derating for temperature, grouping, installation method required
- Voltage drop: ΔV% = (√3 × I × L × (R×cos φ + X×sin φ))/VL × 100%
- Max voltage drop: 3% for lighting, 5% for power (IEC recommendation)

POWER FACTOR CORRECTION:
- Required kVAR: Qc = P × (tan φ1 - tan φ2)
- Capacitor kVAR = V² × 2πf × C × 10⁻³
- PF correction typically to 0.95-0.99 lagging target

SHORT CIRCUIT / FAULT:
- 3-phase fault: Isc = V/(√3 × Zsc)
- Per-unit system: Zpu = Z_actual × Sbase / (Vbase)²
- Equipment rated for available fault current (kA rating)

PROTECTION:
- Overcurrent: IDMT relay — t = TMS × (0.14 / (I/Is)^0.02 - 1) [IEC standard inverse]
- Differential protection: operates when I_in - I_out > threshold
- Earth fault: residual current = IA + IB + IC ≠ 0
""",
        },
        {
            "domain": "Control Systems",
            "title": "Control Systems and PID Reference",
            "text": """
CONTROL SYSTEMS — CORE REFERENCE

TRANSFER FUNCTIONS:
- First order: G(s) = K/(τs + 1), τ = time constant
- Second order: G(s) = ωn²/(s² + 2ζωn·s + ωn²)
  ζ < 1: underdamped (oscillatory)
  ζ = 1: critically damped (fastest without overshoot)
  ζ > 1: overdamped (slow, no overshoot)

PID CONTROLLER:
- Ideal: G(s) = Kp(1 + 1/(Ti·s) + Td·s)
- Standard form: u(t) = Kp·e(t) + Ki·∫e(t)dt + Kd·de(t)/dt
- Proportional (Kp): reduces steady-state error, can cause oscillation
- Integral (Ki): eliminates steady-state error, can cause windup
- Derivative (Kd): improves damping, amplifies noise
- Anti-windup: clamp integrator when output saturates

ZIEGLER-NICHOLS TUNING:
- Step response method (open loop):
  L = dead time, T = time constant, K = process gain
  PID: Kp=1.2T/(K·L), Ti=2L, Td=0.5L
- Ultimate gain method (closed loop):
  Find Ku (gain at oscillation), Tu (period)
  PID: Kp=0.6Ku, Ti=0.5Tu, Td=0.125Tu

STABILITY:
- Routh-Hurwitz: all coefficients positive, no sign change in first column
- Bode: Gain margin > 6dB, Phase margin > 45° for good stability
- Root locus: closed-loop poles must be in left-half s-plane

FREQUENCY RESPONSE:
- Gain crossover frequency: |G(jω)| = 1 (0dB)
- Phase margin = 180° + ∠G(jωgc)
- Gain margin = -20log|G(jωpc)| at phase crossover ωpc

LAPLACE TRANSFORMS (KEY PAIRS):
- Unit step: 1/s
- Ramp: 1/s²
- e^(-at): 1/(s+a)
- sin(ωt): ω/(s²+ω²)
- cos(ωt): s/(s²+ω²)
- Time delay: e^(-Ts)·F(s)
""",
        },
        {
            "domain": "PLC / SCADA",
            "title": "PLC Programming — IEC 61131-3 Reference",
            "text": """
PLC PROGRAMMING — IEC 61131-3 REFERENCE

FIVE STANDARD LANGUAGES:
1. Ladder Diagram (LD) — graphical, based on relay logic
2. Function Block Diagram (FBD) — graphical, data flow
3. Structured Text (ST) — high-level, Pascal-like syntax
4. Instruction List (IL) — low-level, assembler-like
5. Sequential Function Chart (SFC) — state machine / flowchart

STRUCTURED TEXT SYNTAX:
  IF condition THEN
      action;
  ELSIF other_condition THEN
      other_action;
  ELSE
      default_action;
  END_IF;

  FOR i := 0 TO 10 DO
      array[i] := i * 2;
  END_FOR;

  WHILE condition DO
      action;
  END_WHILE;

  CASE state OF
      0: action_0;
      1: action_1;
  ELSE
      default;
  END_CASE;

DATA TYPES:
  BOOL — 1 bit (TRUE/FALSE)
  INT  — 16-bit signed integer (-32768 to 32767)
  DINT — 32-bit signed integer
  REAL — 32-bit floating point
  TIME — duration (T#5s, T#100ms)
  STRING — character string
  ARRAY[0..9] OF INT — array declaration

STANDARD FUNCTION BLOCKS:
  TON  — Timer On Delay: IN, PT (preset time) → Q (output), ET (elapsed)
  TOF  — Timer Off Delay
  TP   — Timer Pulse
  CTU  — Counter Up: CU (clock), R (reset), PV (preset) → Q, CV (count)
  CTD  — Counter Down
  CTUD — Up/Down Counter
  SR   — Set-Reset flip-flop: S1, R → Q1
  RS   — Reset-Set flip-flop: S, R1 → Q1

MOTOR STARTER EXAMPLE (Structured Text):
  (* Forward/Reverse motor control with interlock *)
  IF Start_FWD AND NOT Stop AND NOT Running_REV THEN
      Running_FWD := TRUE;
  END_IF;
  IF Stop OR Overload THEN
      Running_FWD := FALSE;
      Running_REV := FALSE;
  END_IF;
  (* 5 second interlock between F/R *)
  Interlock_Timer(IN := NOT Running_FWD AND NOT Running_REV,
                  PT := T#5s);

MODBUS RTU:
  Function codes: 01=Read Coils, 02=Read Discrete Inputs,
  03=Read Holding Registers, 04=Read Input Registers,
  05=Write Single Coil, 06=Write Single Register,
  15=Write Multiple Coils, 16=Write Multiple Registers
  Frame: Device_Addr | Function | Data | CRC16

SAFETY (IEC 62061 / ISO 13849):
  SIL 1: PFHd < 10⁻⁵/hr
  SIL 2: PFHd < 10⁻⁶/hr
  SIL 3: PFHd < 10⁻⁷/hr
  Performance Level a-e maps to SIL 1-3
""",
        },
        {
            "domain": "Embedded Systems",
            "title": "Embedded Systems and Microcontroller Reference",
            "text": """
EMBEDDED SYSTEMS — CORE REFERENCE

ARDUINO (AVR/ARM):
  Digital I/O: pinMode(pin, INPUT/OUTPUT); digitalWrite(pin, HIGH/LOW); digitalRead(pin)
  Analog: analogRead(pin) → 0-1023 (10-bit ADC, 0-5V); analogWrite(pin, 0-255) [PWM]
  Serial: Serial.begin(9600); Serial.print(); Serial.println(); Serial.read()
  Timing: delay(ms); millis(); micros()
  Interrupts: attachInterrupt(digitalPinToInterrupt(pin), ISR, RISING/FALLING/CHANGE)

ESP32 (MicroPython):
  from machine import Pin, ADC, PWM, I2C, SPI, UART
  Pin: p = Pin(2, Pin.OUT); p.value(1)
  ADC: adc = ADC(Pin(34)); adc.atten(ADC.ATTN_11DB); val = adc.read()  # 0-4095
  PWM: pwm = PWM(Pin(5), freq=1000, duty=512)  # duty 0-1023
  I2C: i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
  WiFi: import network; sta = network.WLAN(network.STA_IF)
  MQTT: from umqtt.simple import MQTTClient

STM32 (HAL C):
  GPIO: HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);
        HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_0);
  ADC:  HAL_ADC_Start(&hadc1); HAL_ADC_PollForConversion(&hadc1, HAL_MAX_DELAY);
        val = HAL_ADC_GetValue(&hadc1);
  UART: HAL_UART_Transmit(&huart1, buf, len, HAL_MAX_DELAY);
        HAL_UART_Receive(&huart1, buf, len, HAL_MAX_DELAY);
  Timer/PWM: HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
             __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, duty);

SENSORS AND INTERFACES:
  4-20mA (current loop): V_sense = I × R_shunt; mA = (ADC/4095) × 20 × (Vref/Vcc)
  PT100 RTD: R(T) = 100 × (1 + 3.9083×10⁻³T - 5.775×10⁻⁷T²)
  Thermocouple Type K: ~41µV/°C, requires cold junction compensation
  I2C addressing: 7-bit (0x00-0x7F), scan with i2c.scan()
  SPI modes: CPOL/CPHA (0,0)=Mode0, (0,1)=Mode1, (1,0)=Mode2, (1,1)=Mode3

COMMUNICATION PROTOCOLS:
  RS-232: ±3-15V, point-to-point, max 15m at 9600 baud
  RS-485: differential ±1.5-5V, multi-drop (32 nodes), 1200m at 9600 baud
  CAN: differential, 1Mbps (1m), 50kbps (500m), priority-based, used in automotive/industrial
  UART frame: [START][D0-D7][PARITY][STOP]
  I2C: 100kHz standard, 400kHz fast, 3.4MHz high-speed; ACK/NACK handshake
""",
        },
        {
            "domain": "Signal Processing",
            "title": "Signal Processing and DSP Reference",
            "text": """
SIGNAL PROCESSING — CORE REFERENCE

FOURIER SERIES (Periodic signals):
  f(t) = a0/2 + Σ[an·cos(nω0t) + bn·sin(nω0t)]
  an = (2/T)∫f(t)cos(nω0t)dt
  bn = (2/T)∫f(t)sin(nω0t)dt

FOURIER TRANSFORM:
  F(ω) = ∫f(t)e^(-jωt)dt
  f(t) = (1/2π)∫F(ω)e^(jωt)dω
  Key pairs: rect → sinc, Gaussian → Gaussian, impulse → 1

SAMPLING THEOREM (Nyquist-Shannon):
  fs ≥ 2 × fmax (must sample at least twice the highest frequency)
  Aliasing occurs if fs < 2×fmax
  Anti-aliasing filter: low-pass at fmax before ADC

DISCRETE FOURIER TRANSFORM (DFT) / FFT:
  X[k] = Σ x[n] × e^(-j2πkn/N), n=0 to N-1
  FFT is O(N log N) vs DFT O(N²)
  Frequency resolution: Δf = fs/N
  In Python: import numpy as np; X = np.fft.fft(x); freqs = np.fft.fftfreq(N, 1/fs)

FILTERS:
  Low-pass: passes frequencies below cutoff fc
  High-pass: passes frequencies above fc
  Band-pass: passes band between f1 and f2
  Notch: rejects narrow band (50/60Hz notch for power line noise)

  RC Low-pass: H(jω) = 1/(1 + jωRC), fc = 1/(2πRC)
  RC High-pass: H(jω) = jωRC/(1 + jωRC), fc = 1/(2πRC)
  2nd order Butterworth: maximally flat passband
  Chebyshev: equiripple passband, sharper rolloff
  Bessel: maximally flat group delay (linear phase)

Z-TRANSFORM:
  X(z) = Σ x[n] × z^(-n)
  Unit delay: z^(-1)
  Stability: all poles inside unit circle |z| < 1
  Bilinear transform (analog→digital): s = 2fs(z-1)/(z+1)

WINDOW FUNCTIONS (for FFT leakage reduction):
  Rectangular: highest leakage, narrowest mainlobe
  Hanning: good general purpose
  Hamming: good for narrowband signals
  Blackman: very low sidelobes, wider mainlobe
  Flat-top: best amplitude accuracy

POWER SPECTRAL DENSITY (PSD):
  Sxx(f) = |X(f)|²/T [W/Hz]
  RMS value = √(∫Sxx(f)df)
""",
        },
    ]

    chunks_all = []
    from rag.ingestor import chunk_text
    for doc in builtin_docs:
        chunks = chunk_text(
            text=doc["text"],
            source=f"builtin:{doc['title']}",
            metadata={"title": doc["title"], "domain": doc["domain"], "type": "builtin"},
        )
        chunks_all.extend(chunks)

    added = add_chunks_to_store(collection, chunks_all)
    metadata[meta_key] = True
    print(f"   ✅ {added} built-in reference chunks ingested\n")
    return added


def main():
    print_banner()

    if not check_dependencies():
        sys.exit(1)

    # Initialize vector store
    print("🗄  Initializing ChromaDB vector store...")
    collection = get_chroma_collection()
    if collection is None:
        print("❌ Could not initialize ChromaDB. Run: pip install chromadb sentence-transformers")
        sys.exit(1)
    print(f"   ✅ Vector store ready at: rag/vectorstore/\n")

    metadata = load_metadata()
    total_chunks = 0

    # 1. Built-in engineering knowledge
    total_chunks += ingest_builtin_knowledge(collection, metadata)

    # 2. Local documents (PDFs, TXT)
    total_chunks += ingest_local_documents(collection, metadata)

    # 3. Free web sources
    answer = input("📡 Scrape free online textbooks? (recommended, ~5 min) [Y/n]: ").strip().lower()
    if answer != "n":
        total_chunks += ingest_web_sources(collection, metadata)

    save_metadata(metadata)

    # Final stats
    stats = get_store_stats()
    print("=" * 60)
    print("✅ KNOWLEDGE BASE BUILD COMPLETE")
    print(f"   Total chunks: {stats['count']:,}")
    print(f"   Domains covered: {', '.join(stats['domains'])}")
    print("=" * 60)
    print("\n🚀 Restart VOLTA to use the knowledge base:")
    print("   python -m streamlit run app.py\n")


if __name__ == "__main__":
    main()
