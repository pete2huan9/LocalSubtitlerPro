# Local Subtitler Pro (v0.2.0)

<p align="center">
  <b>🎬 Modern Desktop AI Video Subtitling, LLM Translation & Lossless Soft-Muxing Workstation</b>
  <br>
  <i>100% Offline & Private · Sentence-by-sentence Golden Alignment · 5 Tailored Scenarios · Bilingual UI</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Release-v0.2.0-blue.svg" alt="Release v0.2.0">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License MIT">
  <img src="https://img.shields.io/badge/Python-3.10%20~%203.14-brightgreen.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/GUI-PyQt6-blueviolet.svg" alt="PyQt6 GUI">
  <img src="https://img.shields.io/badge/ASR-Faster--Whisper-orange.svg" alt="Faster-Whisper">
  <img src="https://img.shields.io/badge/LLM-Ollama-purple.svg" alt="Ollama Local LLM">
</p>

<p align="center">
  <a href="README.md"><b>简体中文</b></a> | <a href="README_EN.md"><b>English Documentation</b></a>
</p>

---

## 🌟 Key Features

* **🚀 Pre-flight Environmental Diagnostic (Self-check)**:
  * Automatically inspects `FFmpeg`, `Ollama` service, local LLMs, and `Whisper` dependencies upon launch.
  * Provides one-click command copy buttons for missing dependencies with smooth countdown transition.
* **🎯 5 Tailored Scenario Tuning Modes**:
  * **🌟 Variety Show**: Dynamic audio normalization (`dynaudnorm`), faint whisper preservation, emotional filler word retention, domain jargon calibration.
  * **🎤 Live & Concert**: Background music suppression, anti-lyrical-hallucination chunking, energetic live stage MC tone.
  * **🎮 Livestream & Vlog**: Adaptive microphone leveling, rapid continuous speech segmentation, gaming & chatroom culture phrasing.
  * **🌸 Anime & Seiyuu**: Japanese honorific nuance preservation (-san/-chan/-senpai), ACG light-novel literary tone.
  * **🎬 Drama & Interview**: Cinematic formal prose, trimmed redundant stutters, standard broadcast timing.
* **🌐 Pure Bilingual Desktop Interface**:
  * Seamless one-click toggle between **🇨🇳 简体中文** and **🇬🇧 English** in the top-right header.
  * Scenarios, languages, monitor statuses, and diagnostics are 100% pure English without leftover Chinese strings.
* **🎞️ Lossless Soft Subtitle Muxing**:
  * Zero video re-encoding (no quality loss, completed in seconds).
  * Muxes soft subtitle tracks into MKV containers, toggleable in PotPlayer, VLC, IINA, etc.
* **⚙️ Foldable Expert Settings**:
  * Clean primary view for casual users (only asks for featured guests/cast names).
  * Expandable expert panel allows power users to tweak Whisper models, Ollama models, and raw system prompts.

---

## 🖥️ Quick Start

### Option 1: Standalone Windows Portable ZIP (No Python Setup)
1. Download `LocalSubtitlerPro-v0.2.0-Windows-x64.zip` from the [Releases Page](https://github.com/Peter/LocalSubtitlerPro/releases);
2. Extract the archive to any directory;
3. Double-click `LocalSubtitlerPro.exe` to launch immediately!

> **Prerequisites**:
> 1. **FFmpeg** installed and in system PATH (run `winget install Gyan.FFmpeg`);
> 2. **Ollama** running locally with a translation model (e.g. `ollama run qwen2.5:14b` or `ollama run qwen2.5:7b`).

---

### Option 2: Running from Source (Developer Mode)

#### 1. Clone the repository
```bash
git clone https://github.com/Peter/LocalSubtitlerPro.git
cd LocalSubtitlerPro
```

#### 2. Create and activate a virtual environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

#### 3. Install dependencies
```powershell
pip install -r requirements.txt
```

#### 4. Launch the desktop GUI
```powershell
python gui_app.py
```
*(Or double-click `run_gui.bat`)*

---

## 🛠️ Building Standalone Windows EXE

This project includes an automated PyInstaller spec configuration and build script:

```powershell
# 1. Install build tools
pip install pyinstaller

# 2. Run the one-click build script
python build_exe.py
```
The output directory will be created at `dist/LocalSubtitlerPro/`, packaged into `LocalSubtitlerPro-v0.2.0-Windows-x64.zip`.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE). Free for personal and commercial use.
