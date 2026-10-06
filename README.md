# Local Subtitler Pro (v0.2.0)

<p align="center">
  <b>🎬 现代化本地 AI 视频字幕转写、大模型翻译与无损软字幕封装桌面工作台</b>
  <br>
  <i>100% 本地离线运行 · 隐私安全 · 逐句跟读级对齐 · 5大场景定制 · 中英双语界面</i>
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
  <a href="README_EN.md"><b>English Documentation</b></a> | <a href="README.md"><b>简体中文</b></a>
</p>

---

## 🌟 核心特性 (Key Features)

* **🚀 启动前置环境自检与智能诊断 (Pre-flight Checks)**：
  * 启动时自动检查 `FFmpeg` 媒体引擎、`Ollama` AI 服务、翻译大模型与 `Whisper` 依赖环境；
  * 提供一键复制修复指令，全部就绪后平滑进入主工作台。
* **🎯 五大通用场景情境定制 (Tailored Scenarios)**：
  * **演艺/偶像综艺 (Variety Show)**：开启动态弱音增益，捕捉轻声细语，保留自然口癖与情绪，自动校准行业术语；
  * **现场舞台/演唱会 (Live & Concert)**：抑制高噪伴奏混杂，抗歌曲节奏重叠，舞台互动煽动感语调；
  * **网络直播/Vlog杂谈 (Livestream & Vlog)**：自适应麦克风收音与快速碎碎念，深度适配弹幕文化与网络热梗；
  * **二次元/声优番组 (Anime & Seiyuu)**：保留日系敬语体系与称谓美感（桑/酱/前辈），轻小说/ACG 典雅文风；
  * **影视剧集/正规访谈 (Drama & Interview)**：信达雅书面语标准，精简冗余沉吟碎词，影视级考究文笔。
* **🌐 全量纯正中英双语界面 (Pure Bilingual UI)**：
  * 界面右上角一键切换 **🇨🇳 简体中文** 与 **🇬🇧 English**；
  * 场景、源语言/目标语言、状态栏、自检卡片全方位纯英文/纯中文呈现，无中英混杂。
* **🎞️ 零损耗软字幕封装 (Lossless Soft Subtitle Muxing)**：
  * 原视频画面零次重新编码（无画质损耗，数秒内完成）；
  * 封装为标准 `.mkv` 软字幕轨道，可在 PotPlayer、VLC、IINA 等播放器中自由开关、切换双语或调整字体。
* **⚙️ 折叠式专家底层设置 (Foldable Expert Settings)**：
  * 一级界面告别生硬的技术术语与代码提示词，普通用户仅需输入“本期出演人员/嘉宾”即可；
  * 资深用户可一键展开专家设置，自由微调底层 Whisper 模型、Ollama 翻译模型及 Raw System Prompt。

---

## 🖥️ 快速开始 (Quick Start)

### 方式一：下载 Windows 独立运行版 (无需配置 Python)
1. 从 [Releases 页面](https://github.com/Peter/LocalSubtitlerPro/releases) 下载最新版本的便携压缩包：`LocalSubtitlerPro-v0.2.0-Windows-x64.zip`；
2. 解压到任意英文目录；
3. 双击 `LocalSubtitlerPro.exe` 即可直接运行！

> **前置要求**：
> 1. 系统中已安装 **FFmpeg** 并加入系统环境变量 PATH（推荐执行 `winget install Gyan.FFmpeg`）；
> 2. 已启动本地 **Ollama** 服务并拉取了翻译模型（如执行 `ollama run qwen2.5:14b` 或 `ollama run qwen2.5:7b`）。

---

### 方式二：从源码运行 (开发者模式)

#### 1. 克隆代码仓库
```bash
git clone https://github.com/Peter/LocalSubtitlerPro.git
cd LocalSubtitlerPro
```

#### 2. 创建并激活虚拟环境
```powershell
python -m venv venv
.\venv\Scripts\activate
```

#### 3. 安装依赖项
```powershell
pip install -r requirements.txt
```

#### 4. 启动 GUI 桌面应用
```powershell
python gui_app.py
```
*(或直接双击运行目录下的 `run_gui.bat`)*

---

## 🛠️ 打包为独立 Windows EXE

本项目提供全自动 PyInstaller 构建规格配置与一键打包脚本：

```powershell
# 1. 安装打包工具
pip install pyinstaller

# 2. 执行一键打包脚本
python build_exe.py
```
构建成功后，绿色发布目录将自动输出至 `dist/LocalSubtitlerPro/`，并自动打包生成 `LocalSubtitlerPro-v0.2.0-Windows-x64.zip`。

---

## 架构简图 (Architecture)

```text
┌────────────────────────────────────────────────────────┐
│               PyQt6 GUI 桌面客户端 (gui_app.py)          │
│   [启动前置自检] -> [视频拖拽区] -> [场景情境定制]       │
└───────────────────────────┬────────────────────────────┘
                            │ 后台 QThread 异步调度
                            ▼
┌────────────────────────────────────────────────────────┐
│             核心业务流水线 (video_subtitler.py)         │
│  [1/4] FFmpeg 动态音频增益 (dynaudnorm 捕捉轻声呢喃)    │
│  [2/4] Faster-Whisper ASR 语音识别 (2.0s~5.5s 黄金切分) │
│  [3/4] Ollama 本地大模型 上下文逐句地道翻译            │
│  [4/4] FFmpeg 封装多轨道中日双语软字幕 (无损 MKV)       │
└────────────────────────────────────────────────────────┘
```

---

## 🤝 贡献与反馈 (Contributing)

欢迎提交 Issue 与 Pull Request！
1. Fork 本仓库并新建特性分支 (`git checkout -b feat/amazing-feature`)；
2. 提交您的修改 (`git commit -m 'Add amazing feature'`)；
3. 推送到远程分支 (`git push origin feat/amazing-feature`)；
4. 发起 Pull Request。

---

## 📄 开源许可证 (License)

本项目基于 [MIT License](LICENSE) 开源。欢迎自由使用、学习与商业化衍生。
