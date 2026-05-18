"""
utils/session.py
Manages conversation history, session state, and export functionality.
"""

import json
import datetime
from pathlib import Path


HISTORY_DIR = Path("chat_history")


def init_session(st) -> None:
    """Initialize all Streamlit session state variables."""
    defaults = {
        "messages": [],               # Full chat history
        "selected_model": "",         # Current Ollama model
        "temperature": 0.3,           # LLM temperature
        "auto_run_code": True,        # Auto-execute Python code blocks
        "show_system_prompt": False,  # Debug: show system prompt
        "token_count": 0,             # Approximate token usage
        "domain_filter": "All",       # Engineering domain filter
        "session_id": _new_session_id(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _new_session_id() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def add_message(st, role: str, content: str) -> None:
    """Add a message to the session history."""
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.datetime.now().isoformat(),
    })


def get_messages_for_api(st) -> list[dict]:
    """
    Return messages in the format expected by Ollama API.
    Keeps last N messages to avoid context overflow.
    """
    MAX_MESSAGES = 20  # Keep last 20 exchanges (~10 turns)
    messages = st.session_state.messages[-MAX_MESSAGES:]
    return [{"role": m["role"], "content": m["content"]} for m in messages]


def clear_history(st) -> None:
    """Clear conversation history and reset session."""
    st.session_state.messages = []
    st.session_state.token_count = 0
    st.session_state.session_id = _new_session_id()


def export_chat_json(st) -> str:
    """Export full chat history as formatted JSON string."""
    export_data = {
        "session_id": st.session_state.session_id,
        "model": st.session_state.selected_model,
        "exported_at": datetime.datetime.now().isoformat(),
        "messages": st.session_state.messages,
    }
    return json.dumps(export_data, indent=2)


def export_chat_markdown(st) -> str:
    """Export chat history as readable Markdown document."""
    lines = [
        f"# VOLTA — Engineering AI Session",
        f"**Session:** {st.session_state.session_id}",
        f"**Model:** {st.session_state.selected_model}",
        f"**Exported:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
    ]
    for msg in st.session_state.messages:
        role = "👤 You" if msg["role"] == "user" else "⚡ VOLTA"
        ts = msg.get("timestamp", "")[:16].replace("T", " ")
        lines.append(f"### {role} — {ts}")
        lines.append("")
        lines.append(msg["content"])
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


# Quick-start example prompts by domain
EXAMPLE_PROMPTS = {
    "Circuit Analysis": [
        "Calculate the Thevenin equivalent of a circuit with a 12V source, 4Ω and 6Ω resistors in a bridge configuration at terminals A-B",
        "Analyze this RC low-pass filter: R=10kΩ, C=100nF. Find the cutoff frequency, impedance at 1kHz, and plot the Bode diagram in Python",
        "Design a voltage divider to produce 3.3V from a 12V supply. The load draws 50mA. Calculate resistor values and power dissipation",
    ],
    "Power Systems": [
        "A 3-phase, 50Hz, 11kV/415V delta-wye transformer is rated 500kVA. Calculate the full-load line currents on both sides and the turns ratio",
        "Calculate the power factor correction capacitor bank needed to improve a factory's PF from 0.72 lagging to 0.95 for a 200kW, 415V, 3-phase load",
        "Size a circuit breaker and cable for a 75kW, 415V, 3-phase motor with a starting current of 600% and a run time under 10 seconds",
    ],
    "PLC / SCADA": [
        "Write IEC 61131-3 Structured Text code for a motor starter with forward/reverse control, overload protection, and a 5-second interlock delay",
        "Create a Ladder Logic program for a conveyor belt with: start/stop buttons, emergency stop, photocell sensor, and a counter that stops at 100 parts",
        "Write Modbus RTU Python code to read holding registers from a VFD (Schneider ATV320) and display speed, current, and fault codes",
    ],
    "Embedded / Code": [
        "Write Arduino code for a PID temperature controller using a PT100 sensor, SSR relay output, and PID constants Kp=2.0, Ki=0.5, Kd=0.1",
        "Write ESP32 MicroPython code to read a 4-20mA pressure sensor on ADC, convert to engineering units (0-10 bar), and publish via MQTT",
        "Write STM32 HAL C code to configure UART, read a GPS NMEA string, parse latitude/longitude, and output on an I2C OLED display",
    ],
    "Math & Control": [
        "Design a PID controller for a first-order system with transfer function G(s) = 5/(10s+1). Target: zero steady-state error, <10% overshoot, settling time <20s",
        "Compute the FFT of a signal sampled at 10kHz containing 50Hz, 150Hz (3rd harmonic), and 250Hz (5th harmonic) components using Python",
        "Find the Z-transform of a digital filter with difference equation y[n] = 0.5y[n-1] + 0.3x[n] + 0.2x[n-1] and determine its stability",
    ],
}
