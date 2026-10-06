#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Video Subtitler Pro - Modern PyQt6 Desktop Application
Features:
- Bilingual UI (中英文自由切换, Chinese & English)
- Context-aware tailored scenario tuning (针对性情境定制，告别生硬底层 Prompt/Hotwords)
- Foldable Expert Settings (收纳底层提示词与模型微调，一级界面清新整洁)
- Pre-flight diagnostic checker (FFmpeg, Ollama, Models, Whisper)
- Drag & Drop video selection
- Asynchronous QThread background worker (Zero UI freeze)
- Real-time progress bar, timestamped log console, and one-click play/open
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List

__version__ = "0.2.0"

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt6.QtGui import QIcon, QFont, QColor, QDragEnterEvent, QDropEvent, QDesktopServices
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit, QProgressBar,
    QCheckBox, QFileDialog, QGroupBox, QStackedWidget, QFrame,
    QSplitter, QMessageBox, QScrollArea, QSizePolicy
)

# 导入底层核心逻辑与预设
try:
    import video_subtitler as core
except ImportError:
    from . import video_subtitler as core


# ==============================================================================
# 多语言国际化字典 (i18n Dictionary)
# ==============================================================================
I18N = {
    "zh": {
        "app_title": "本地 AI 视频字幕翻译与封装工作台 v0.2.0 (Local Subtitler Pro)",
        "diag_title": "🚀 本地 AI 运行环境自检与诊断",
        "diag_subtitle": "确保本地媒体引擎、Ollama 服务及模型就绪，享受安全、完全离线的字幕生成体验。",
        "diag_passed": "✅ 所有前置依赖检测通过！",
        "diag_failed": "⚠ 检测到部分依赖未就绪，请参考上方提示配置或修复。",
        "btn_enter": "进入主工作台 ➔",
        "btn_pause_timer": "⏸ 暂停自动跳转",
        "btn_recheck": "🔄 重新检测",
        "btn_copy_cmd": "📋 复制修复指令",
        "copy_success_title": "已复制",
        "copy_success_msg": "已将修复命令复制到剪贴板:\n\n",
        "top_diag_btn": "🛠️ 运行环境自检",
        "status_ready": "🟢 本地离线引擎就绪",
        
        # 视频选择区
        "sec_video": "1. 选择待处理视频",
        "drop_title": "拖拽视频文件到此区域，或点击下方按钮选择视频",
        "drop_loaded": "🎬 已载入: ",
        "drop_hint": "支持 MP4, MKV, MOV, TS, FLV, WEBM 等常见视频格式",
        "input_placeholder": "可直接将视频拖入上方区域，或在此粘贴视频路径...",
        "btn_browse": "📁 浏览文件...",
        "btn_clear": "✕ 清除",
        "waiting_video": "等待选择视频...",
        "file_selected_info": "✓ 已选择: {name} (大小: {size})",

        # 场景与定制区
        "sec_scenario": "2. 场景模式与针对性情境定制",
        "preset_label": "场景模式:",
        "src_lang_label": "视频原语种:",
        "tgt_lang_label": "翻译目标语言:",
        "extra_names_label": "本期出演人员 / 嘉宾 (可选追加):",
        "extra_names_placeholder": "例如: 出演嘉宾名、角色名、专有名词 (逗号分隔，可选追加)",
        "badges_header": "💡 针对性自动化策略:",
        "strategy_label": "AI 策略解读:",

        # 选项开关
        "chk_bilingual": "双语对照字幕 (原语言+中文)",
        "chk_mux": "封装软字幕至 MKV 视频 (播放器可随时开关)",
        "chk_dynaudnorm": "人声动态增强 (捕捉轻声细语与气声)",
        "chk_skip_trans": "跳过大模型翻译 (仅识别原文)",

        # 专家底层设置折叠
        "btn_expert_expand": "⚙️ 展开专家高级设置 (模型与底层微调) ▼",
        "btn_expert_collapse": "⚙️ 收起专家高级设置 ▲",
        "whisper_model_label": "Whisper 识别模型:",
        "ollama_model_label": "Ollama 翻译模型:",
        "refresh_models_tip": "刷新本地 Ollama 模型列表",
        "raw_hotwords_label": "底层合并热词库 (Raw Hotwords):",
        "raw_prompt_label": "底层系统提示词 (Raw Prompt):",

        # 执行监控
        "sec_exec": "3. 执行生成与实时监控",
        "stage_ready": "就绪，等待启动...",
        "stage_starting": "🚀 正在启动后台任务...",
        "btn_start": "🚀 开始生成字幕 (Start Pipeline)",
        "btn_cancel": "⏹ 终止任务",
        "btn_open_folder": "📂 打开所在目录",
        "btn_play_video": "▶️ 播放成品视频",
        "task_done_title": "生成完成",
        "task_done_msg": "视频处理完成！\n\n已成功生成字幕并封装输出：\n{name}\n\n可在下方点击「播放视频」或「打开所在目录」。",
        "warn_no_video": "请先选择或拖拽有效的视频文件！",
        "err_title": "发生错误",
        "err_msg_prefix": "处理视频时发生错误:\n",
        "lang_name": "界面语言: "
    },
    "en": {
        "app_title": "Local Video Subtitler Pro v0.2.0 (AI Powered)",
        "diag_title": "🚀 Local AI Pre-flight Environment Diagnostic",
        "diag_subtitle": "Ensure local media engine, Ollama service and models are ready for safe, offline subtitle generation.",
        "diag_passed": "✅ All pre-flight checks passed successfully!",
        "diag_failed": "⚠ Some dependencies missing. Please refer to instructions above.",
        "btn_enter": "Enter Workspace ➔",
        "btn_pause_timer": "⏸ Pause Auto-entry",
        "btn_recheck": "🔄 Re-check",
        "btn_copy_cmd": "📋 Copy Command",
        "copy_success_title": "Copied",
        "copy_success_msg": "Command copied to clipboard:\n\n",
        "top_diag_btn": "🛠️ Diagnostics",
        "status_ready": "🟢 Local Offline Engines Ready",

        # Video Section
        "sec_video": "1. Select Video File",
        "drop_title": "Drag & drop video here, or click Browse below",
        "drop_loaded": "🎬 Loaded: ",
        "drop_hint": "Supports MP4, MKV, MOV, TS, FLV, WEBM and more",
        "input_placeholder": "Drag video above or paste file path here...",
        "btn_browse": "📁 Browse...",
        "btn_clear": "✕ Clear",
        "waiting_video": "Waiting for video file...",
        "file_selected_info": "✓ Selected: {name} (Size: {size})",

        # Scenario Section
        "sec_scenario": "2. Scenario Mode & Tailored Tuning",
        "preset_label": "Scenario Mode:",
        "src_lang_label": "Source Language:",
        "tgt_lang_label": "Target Language:",
        "extra_names_label": "Featured Cast / Guests (Optional):",
        "extra_names_placeholder": "e.g., Guest names, character names, specific keywords (comma-separated, optional)",
        "badges_header": "💡 Automated Tailored Strategies:",
        "strategy_label": "AI Strategy Details:",

        # Options
        "chk_bilingual": "Bilingual Subtitles (Source + Target)",
        "chk_mux": "Mux Soft Subtitles into MKV (Toggleable in player)",
        "chk_dynaudnorm": "Dynamic Vocal Boost (Capture faint speech & whispers)",
        "chk_skip_trans": "Skip Translation (ASR Transcription only)",

        # Expert Settings
        "btn_expert_expand": "⚙️ Expand Expert Settings (Models & Raw Prompts) ▼",
        "btn_expert_collapse": "⚙️ Collapse Expert Settings ▲",
        "whisper_model_label": "Whisper Model:",
        "ollama_model_label": "Ollama LLM Model:",
        "refresh_models_tip": "Refresh local Ollama model list",
        "raw_hotwords_label": "Raw Injected Hotwords String:",
        "raw_prompt_label": "Raw LLM System Prompt:",

        # Execution Section
        "sec_exec": "3. Execution & Live Monitor",
        "stage_ready": "Ready, waiting to start...",
        "stage_starting": "🚀 Starting background pipeline...",
        "btn_start": "🚀 Start Subtitle Generation",
        "btn_cancel": "⏹ Cancel Task",
        "btn_open_folder": "📂 Open Output Folder",
        "btn_play_video": "▶️ Play Subtitled Video",
        "task_done_title": "Task Finished",
        "task_done_msg": "Video processing finished!\n\nSuccessfully generated and muxed subtitles into:\n{name}\n\nClick 'Play Video' or 'Open Output Folder' below.",
        "warn_no_video": "Please select or drop a valid video file first!",
        "err_title": "Error Occurred",
        "err_msg_prefix": "An error occurred during processing:\n",
        "lang_name": "UI Language: "
    }
}

# 场景预设的针对性多语言元数据
SCENARIO_META = {
    "idol_variety": {
        "name_zh": "🌟 演艺/偶像综艺",
        "tag_zh": "真人秀 / 娱乐访谈 / 演艺日常",
        "name_en": "🌟 Variety Show",
        "tag_en": "Reality Show / Talk Show / Daily Vlog",
        "badges_zh": ["✨ 弱音动态增益", "🗣️ 口语与情绪保留", "🛡️ 行业专属用语校准"],
        "badges_en": ["✨ Dynamic Vocal Boost", "🗣️ Colloquial Tone Kept", "🛡️ Domain Jargon Guard"],
        "desc_zh": "针对演艺综艺杂音与轻声语境优化。增强微弱人声，保留自然口癖习惯与真实情感，自动校准行业圈内术语。",
        "desc_en": "Optimized for variety shows. Boosts faint whispers, preserves colloquial speech nuances, and accurately calibrates industry-specific jargon."
    },
    "concert_live": {
        "name_zh": "🎤 现场舞台/演唱会",
        "tag_zh": "现场Live / 舞台演出 / 音乐互动",
        "name_en": "🎤 Live & Concert",
        "tag_en": "Live Stage / Music Festival / Concert MC",
        "badges_zh": ["🔊 伴奏降噪抑制", "⚡ 防歌曲混杂断句", "🎉 舞台互动感染力"],
        "badges_en": ["🔊 Background Music Damping", "⚡ Anti-Overlap Chunking", "🎉 Stage Interaction Tone"],
        "desc_zh": "针对伴奏背景声强化人声提取，抑制音乐伴奏混杂；优化单句时长，翻译贴合现场舞台互动与欢呼气氛。",
        "desc_en": "Reinforces vocals over loud music accompaniment, eliminates lyrical overlap, and captures energetic live stage interactions."
    },
    "livestream_vlog": {
        "name_zh": "🎮 网络直播/Vlog杂谈",
        "tag_zh": "个人直播 / 游戏实况 / 日常Vlog",
        "name_en": "🎮 Livestream & Vlog",
        "tag_en": "Personal Stream / Gaming / Casual Vlog",
        "badges_zh": ["🎙️ 自适应麦克风收音", "💬 网络用语与互动优化", "⚡ 高速碎碎念断句"],
        "badges_en": ["🎙️ Adaptive Mic Leveling", "💬 Internet Culture Adaptation", "⚡ Rapid Speech Segmentation"],
        "desc_zh": "适应个人麦克风与快速连环说话，停顿容差适中；翻译采用现代接地气网感，适配网络交流与流行用语。",
        "desc_en": "Tailored for streamers and vloggers. Adapts to rapid chatter, casual colloquialisms, and internet cultural nuances."
    },
    "anime_seiyuu": {
        "name_zh": "🌸 二次元/声优番组",
        "tag_zh": "声优广播 / 动画特典 / ACG生放送",
        "name_en": "🌸 Anime & Seiyuu",
        "tag_en": "Radio Drama / Anime Special / ACG Event",
        "badges_zh": ["🌸 角色称谓与敬语保留", "📖 轻小说/二次元文风", "🎙️ 声优圈语感润色"],
        "badges_en": ["🌸 Character Honorifics Kept", "📖 Light-Novel Style", "🎙️ Voice Actor Tone Polishing"],
        "desc_zh": "保留原声高频细节，兼顾敬语体系与称谓习惯；采用典雅二次元汉化风格，生动传达角色与语境魅力。",
        "desc_en": "Preserves honorific nuances and delivers elegant ACG translation style matching character and voice actor contexts."
    },
    "drama_interview": {
        "name_zh": "🎬 影视剧集/正规访谈",
        "tag_zh": "影视剧集 / 纪录片 / 正式专访",
        "name_en": "🎬 Drama & Interview",
        "tag_en": "TV Drama / Documentary / Formal Interview",
        "badges_zh": ["📜 影视级书面语标准", "✂️ 精简冗余口语碎词", "🎬 影视规范断句"],
        "badges_en": ["📜 Cinematic Standard Prose", "✂️ Trimmed Redundant Stutters", "🎬 Standard Drama Timing"],
        "desc_zh": "追求信达雅书面语与影视剧规范。启用精准断句，适当弱化多余无意义沉吟，行文工整沉稳、契合影视标准。",
        "desc_en": "Formal cinematic standard. Polished written prose, elegant pacing, and omission of meaningless vocal hesitation."
    }
}


# ==============================================================================
# 现代化暗色主题 QSS 样式表
# ==============================================================================
DARK_STYLE = """
QWidget {
    background-color: #1a1b26;
    color: #c0caf5;
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #2f354a;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
    color: #7aa2f7;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background-color: #1a1b26;
}

QPushButton {
    background-color: #24283b;
    border: 1px solid #3b4261;
    border-radius: 6px;
    padding: 6px 14px;
    color: #c0caf5;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #2f3549;
    border-color: #7aa2f7;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #1f2335;
}
QPushButton:disabled {
    background-color: #1e2030;
    border-color: #282a36;
    color: #565f89;
}

QPushButton#primaryBtn {
    background-color: #7aa2f7;
    border: 1px solid #7aa2f7;
    color: #15161e;
    font-weight: bold;
    font-size: 14px;
    padding: 8px 18px;
}
QPushButton#primaryBtn:hover {
    background-color: #89b4fa;
    border-color: #89b4fa;
}
QPushButton#primaryBtn:disabled {
    background-color: #3b4261;
    border-color: #3b4261;
    color: #787c99;
}

QPushButton#cancelBtn {
    background-color: #f7768e;
    border: 1px solid #f7768e;
    color: #15161e;
    font-weight: bold;
}
QPushButton#cancelBtn:hover {
    background-color: #ff9eaf;
}

QPushButton#textToggleBtn {
    background-color: transparent;
    border: none;
    color: #7aa2f7;
    text-align: left;
    font-size: 12px;
    padding: 4px 0;
}
QPushButton#textToggleBtn:hover {
    color: #bb9af7;
    text-decoration: underline;
}

QLineEdit, QTextEdit, QComboBox {
    background-color: #16161e;
    border: 1px solid #2f354a;
    border-radius: 6px;
    padding: 6px 8px;
    color: #c0caf5;
    selection-background-color: #3d59a1;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #7aa2f7;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #16161e;
    border: 1px solid #2f354a;
    selection-background-color: #3d59a1;
    selection-color: #ffffff;
}

QProgressBar {
    border: 1px solid #2f354a;
    border-radius: 6px;
    text-align: center;
    background-color: #16161e;
    color: #ffffff;
    font-weight: bold;
}
QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7aa2f7, stop:1 #bb9af7);
    border-radius: 5px;
}

QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #3b4261;
    background-color: #16161e;
}
QCheckBox::indicator:checked {
    background-color: #7aa2f7;
    border-color: #7aa2f7;
}

QScrollBar:vertical {
    background: #16161e;
    width: 8px;
    border-radius: 4px;
}
QScrollBar:handle:vertical {
    background: #3b4261;
    border-radius: 4px;
}
QScrollBar:handle:vertical:hover {
    background: #7aa2f7;
}
"""


# ==============================================================================
# 后台多线程工作流 Worker
# ==============================================================================
class SubtitleWorker(QThread):
    sig_log = pyqtSignal(str)
    sig_progress = pyqtSignal(int, str)
    sig_finished = pyqtSignal(dict)
    sig_error = pyqtSignal(str)

    def __init__(self, video_path: Path, config: Dict[str, Any]):
        super().__init__()
        self.video_path = video_path
        self.config = config
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

    def check_cancel(self) -> bool:
        return self.is_cancelled

    def run(self):
        try:
            def log_callback(msg: str):
                self.sig_log.emit(msg)

            def progress_callback(pct: int, text: str):
                self.sig_progress.emit(pct, text)

            res = core.run_pipeline(
                self.video_path,
                self.config,
                log_cb=log_callback,
                progress_cb=progress_callback,
                cancel_check=self.check_cancel
            )
            self.sig_finished.emit(res)
        except InterruptedError:
            self.sig_log.emit("⏹️ 任务已被用户主动终止。")
            self.sig_progress.emit(0, "任务已中止")
        except Exception as e:
            self.sig_error.emit(str(e))


# ==============================================================================
# 拖拽视频卡片控件
# ==============================================================================
class DropVideoArea(QFrame):
    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropArea")
        self.setStyleSheet("""
            QFrame#dropArea {
                border: 2px dashed #3b4261;
                border-radius: 10px;
                background-color: #16161e;
                min-height: 75px;
            }
            QFrame#dropArea:hover {
                border: 2px dashed #7aa2f7;
                background-color: #1f2335;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(15, 8, 15, 8)

        self.label_icon = QLabel("🎬", self)
        self.label_icon.setStyleSheet("font-size: 24px; background: transparent;")
        self.label_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_icon)

        self.label_text = QLabel("", self)
        self.label_text.setStyleSheet("color: #7aa2f7; font-weight: bold; background: transparent;")
        self.label_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_text)

        self.label_hint = QLabel("", self)
        self.label_hint.setStyleSheet("color: #565f89; font-size: 11px; background: transparent;")
        self.label_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_hint)

    def update_texts(self, title: str, hint: str):
        self.label_text.setText(title)
        self.label_hint.setText(hint)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                ext = Path(file_path).suffix.lower()
                if ext in [".mp4", ".mkv", ".mov", ".avi", ".flv", ".webm", ".ts", ".m4v"]:
                    event.acceptProposedAction()
                    self.setStyleSheet("""
                        QFrame#dropArea {
                            border: 2px dashed #9ece6a;
                            background-color: #1f2d3d;
                        }
                    """)
                    return
        event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame#dropArea {
                border: 2px dashed #3b4261;
                border-radius: 10px;
                background-color: #16161e;
                min-height: 75px;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.file_dropped.emit(file_path)
            event.acceptProposedAction()
        self.dragLeaveEvent(None)


# ==============================================================================
# 启动前置环境自检页面 (Pre-flight Diagnostic Page)
# ==============================================================================
class DiagnosticPage(QWidget):
    enter_main_signal = pyqtSignal()

    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self.main_win = main_win
        self.all_passed = False
        self.countdown_val = 4
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_countdown_tick)
        self.init_ui()

    def tr_text(self, key: str) -> str:
        lang = self.main_win.current_lang
        return I18N.get(lang, I18N["zh"]).get(key, "")

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 25, 40, 25)
        main_layout.setSpacing(16)

        # 头部标题与语言切换
        top_row = QHBoxLayout()
        header_layout = QVBoxLayout()
        self.title_lbl = QLabel(self.tr_text("diag_title"), self)
        self.title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #7aa2f7;")
        self.subtitle_lbl = QLabel(self.tr_text("diag_subtitle"), self)
        self.subtitle_lbl.setStyleSheet("color: #a9b1d6; font-size: 13px;")
        header_layout.addWidget(self.title_lbl)
        header_layout.addWidget(self.subtitle_lbl)
        top_row.addLayout(header_layout)

        top_row.addStretch()

        # 语言选择下拉框
        lang_box = QHBoxLayout()
        self.lbl_lang = QLabel(self.tr_text("lang_name"), self)
        self.lbl_lang.setStyleSheet("color: #7aa2f7; font-weight: 500;")
        lang_box.addWidget(self.lbl_lang)

        self.combo_lang_switch = QComboBox(self)
        self.combo_lang_switch.addItem("🇨🇳 简体中文", "zh")
        self.combo_lang_switch.addItem("🇬🇧 English", "en")
        self.combo_lang_switch.currentIndexChanged.connect(self.on_lang_switch_changed)
        lang_box.addWidget(self.combo_lang_switch)
        top_row.addLayout(lang_box)

        main_layout.addLayout(top_row)

        # 检查项卡片容器
        self.cards_container = QVBoxLayout()
        self.cards_container.setSpacing(10)
        main_layout.addLayout(self.cards_container)

        main_layout.addStretch()

        # 底部操作栏
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(15)

        self.status_lbl = QLabel("", self)
        self.status_lbl.setStyleSheet("font-size: 13px; color: #9ece6a;")
        footer_layout.addWidget(self.status_lbl)

        footer_layout.addStretch()

        self.btn_pause_timer = QPushButton(self.tr_text("btn_pause_timer"), self)
        self.btn_pause_timer.setVisible(False)
        self.btn_pause_timer.clicked.connect(self.pause_countdown)
        footer_layout.addWidget(self.btn_pause_timer)

        self.btn_recheck = QPushButton(self.tr_text("btn_recheck"), self)
        self.btn_recheck.clicked.connect(self.run_checks)
        footer_layout.addWidget(self.btn_recheck)

        self.btn_enter = QPushButton(self.tr_text("btn_enter"), self)
        self.btn_enter.setObjectName("primaryBtn")
        self.btn_enter.clicked.connect(self.on_enter_clicked)
        footer_layout.addWidget(self.btn_enter)

        main_layout.addLayout(footer_layout)

    def on_lang_switch_changed(self, idx: int):
        code = self.combo_lang_switch.currentData()
        if code and code != self.main_win.current_lang:
            self.main_win.set_language(code)

    def retranslate_ui(self):
        self.title_lbl.setText(self.tr_text("diag_title"))
        self.subtitle_lbl.setText(self.tr_text("diag_subtitle"))
        self.lbl_lang.setText(self.tr_text("lang_name"))
        self.btn_pause_timer.setText(self.tr_text("btn_pause_timer"))
        self.btn_recheck.setText(self.tr_text("btn_recheck"))
        self.btn_enter.setText(self.tr_text("btn_enter"))
        # 同步下拉框索引
        cur_code = self.main_win.current_lang
        idx = self.combo_lang_switch.findData(cur_code)
        if idx >= 0 and self.combo_lang_switch.currentIndex() != idx:
            self.combo_lang_switch.blockSignals(True)
            self.combo_lang_switch.setCurrentIndex(idx)
            self.combo_lang_switch.blockSignals(False)
        self.run_checks()

    def pause_countdown(self):
        self.timer.stop()
        self.btn_pause_timer.setVisible(False)
        self.btn_enter.setText(self.tr_text("btn_enter"))

    def run_checks(self):
        self.timer.stop()
        self.btn_pause_timer.setVisible(False)
        while self.cards_container.count():
            item = self.cards_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        checks = core.check_prerequisites()
        all_ok = True

        for key, info in checks.items():
            if not info["passed"]:
                all_ok = False
            card = self.create_check_card(info)
            self.cards_container.addWidget(card)

        self.all_passed = all_ok
        if all_ok:
            self.status_lbl.setText(self.tr_text("diag_passed"))
            self.status_lbl.setStyleSheet("font-weight: bold; color: #9ece6a;")
            self.btn_enter.setEnabled(True)
            self.countdown_val = 4
            self.btn_enter.setText(f"{self.tr_text('btn_enter')} ({self.countdown_val}s)")
            self.btn_pause_timer.setVisible(True)
            self.timer.start(1000)
        else:
            self.status_lbl.setText(self.tr_text("diag_failed"))
            self.status_lbl.setStyleSheet("font-weight: bold; color: #f7768e;")
            self.btn_enter.setText(self.tr_text("btn_enter"))
            self.btn_enter.setEnabled(True)

    def create_check_card(self, info: Dict[str, Any]) -> QFrame:
        card = QFrame(self)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #16161e;
                border: 1px solid {'#9ece6a' if info['passed'] else '#f7768e'};
                border-radius: 8px;
                padding: 10px 14px;
            }}
        """)
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(6)
        c_layout.setContentsMargins(10, 8, 10, 8)

        h_row = QHBoxLayout()
        status_icon = "✅" if info["passed"] else "❌"
        is_en = self.main_win.current_lang == "en"
        status_text = ("Ready" if info["passed"] else "Missing") if is_en else ("正常就绪" if info["passed"] else "未就绪 / 缺失")
        status_color = "#9ece6a" if info["passed"] else "#f7768e"

        title_map_en = {
            "FFmpeg 媒体处理引擎": "FFmpeg Media Processing Engine",
            "Ollama 本地大模型服务": "Ollama Local LLM Service",
            "本地翻译大模型 (LLM)": "Local Translation Model (LLM)",
            "Faster-Whisper 语音识别引擎": "Faster-Whisper Speech Recognition Engine"
        }
        card_title = title_map_en.get(info['title'], info['title']) if is_en else info['title']

        title_lbl = QLabel(f"{status_icon} <b>{card_title}</b>", card)
        title_lbl.setStyleSheet("font-size: 14px;")
        h_row.addWidget(title_lbl)

        badge = QLabel(f"[{status_text}]", card)
        badge.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        h_row.addWidget(badge)
        h_row.addStretch()

        if info.get("command"):
            cmd_btn = QPushButton(self.tr_text("btn_copy_cmd"), card)
            cmd_btn.setStyleSheet("font-size: 11px; padding: 2px 8px;")
            cmd_btn.clicked.connect(lambda _, c=info["command"]: self.copy_command(c))
            h_row.addWidget(cmd_btn)

        c_layout.addLayout(h_row)

        detail_text = info["detail"]
        if is_en and info["passed"]:
            if "服务正常运行中" in detail_text:
                detail_text = "Service running normally (127.0.0.1:11434)"
            elif "已检测到可用模型" in detail_text:
                detail_text = detail_text.replace("已检测到可用模型:", "Detected available models:").replace("等", "etc.")
            elif "已就绪" in detail_text:
                detail_text = detail_text.replace("已就绪:", "Ready:")
            elif "Python 库与 CTranslate2" in detail_text:
                detail_text = "Python library & CTranslate2 backend loaded successfully"

        detail_lbl = QLabel(detail_text, card)
        detail_lbl.setStyleSheet("color: #a9b1d6; font-size: 12px;")
        c_layout.addWidget(detail_lbl)

        if not info["passed"] and info.get("fix_guide"):
            guide_lbl = QLabel(f"💡 {'Solution:' if is_en else '解决方法:'} {info['fix_guide']}", card)
            guide_lbl.setStyleSheet("color: #e0af68; font-size: 12px;")
            c_layout.addWidget(guide_lbl)

        return card

    def copy_command(self, cmd_text: str):
        clipboard = QApplication.clipboard()
        clipboard.setText(cmd_text)
        QMessageBox.information(self, self.tr_text("copy_success_title"), f"{self.tr_text('copy_success_msg')}{cmd_text}")

    def on_countdown_tick(self):
        self.countdown_val -= 1
        if self.countdown_val <= 0:
            self.timer.stop()
            self.enter_main_signal.emit()
        else:
            self.btn_enter.setText(f"{self.tr_text('btn_enter')} ({self.countdown_val}s)")

    def on_enter_clicked(self):
        self.timer.stop()
        self.enter_main_signal.emit()


# ==============================================================================
# 主工作台页面 (Main Workspace)
# ==============================================================================
class WorkspacePage(QWidget):
    back_to_diag_signal = pyqtSignal()

    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self.main_win = main_win
        self.selected_video_path: Optional[Path] = None
        self.worker: Optional[SubtitleWorker] = None
        self.last_result: Optional[dict] = None
        self.cfg = core.load_config()
        self.is_expert_expanded = False
        self.init_ui()
        self.load_initial_values()

    def tr_text(self, key: str, **kwargs) -> str:
        lang = self.main_win.current_lang
        raw = I18N.get(lang, I18N["zh"]).get(key, "")
        if kwargs:
            try:
                return raw.format(**kwargs)
            except Exception:
                return raw
        return raw

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 12, 18, 12)
        main_layout.setSpacing(10)

        # 1. 顶栏：软件标题、语言切换与返回环境诊断
        top_bar = QHBoxLayout()
        self.lbl_app_title = QLabel(self.tr_text("app_title"), self)
        self.lbl_app_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7aa2f7;")
        top_bar.addWidget(self.lbl_app_title)

        top_bar.addStretch()

        # 语言切换
        self.combo_ws_lang = QComboBox(self)
        self.combo_ws_lang.addItem("🇨🇳 简体中文", "zh")
        self.combo_ws_lang.addItem("🇬🇧 English", "en")
        self.combo_ws_lang.currentIndexChanged.connect(self.on_lang_switch_changed)
        top_bar.addWidget(self.combo_ws_lang)

        self.btn_back_diag = QPushButton(self.tr_text("top_diag_btn"), self)
        self.btn_back_diag.clicked.connect(self.back_to_diag_signal.emit)
        top_bar.addWidget(self.btn_back_diag)
        main_layout.addLayout(top_bar)

        # 2. 视频选择区 (拖拽 + 浏览)
        self.video_group = QGroupBox(self.tr_text("sec_video"))
        vg_layout = QVBoxLayout(self.video_group)
        vg_layout.setSpacing(6)

        self.drop_area = DropVideoArea(self)
        self.drop_area.file_dropped.connect(self.set_video_file)
        vg_layout.addWidget(self.drop_area)

        file_row = QHBoxLayout()
        self.line_video_path = QLineEdit(self)
        self.line_video_path.setPlaceholderText(self.tr_text("input_placeholder"))
        self.line_video_path.textChanged.connect(self.on_path_manual_changed)
        file_row.addWidget(self.line_video_path)

        self.btn_browse = QPushButton(self.tr_text("btn_browse"), self)
        self.btn_browse.clicked.connect(self.browse_video_file)
        file_row.addWidget(self.btn_browse)

        self.btn_clear = QPushButton(self.tr_text("btn_clear"), self)
        self.btn_clear.clicked.connect(self.clear_video_file)
        file_row.addWidget(self.btn_clear)

        vg_layout.addLayout(file_row)

        self.lbl_file_info = QLabel(self.tr_text("waiting_video"), self)
        self.lbl_file_info.setStyleSheet("color: #7982a9; font-size: 11px;")
        vg_layout.addWidget(self.lbl_file_info)

        main_layout.addWidget(self.video_group)

        # 3. 场景模式与针对性情境定制区 (取代生硬的Prompt/Hotwords)
        self.scenario_group = QGroupBox(self.tr_text("sec_scenario"))
        sg_layout = QVBoxLayout(self.scenario_group)
        sg_layout.setSpacing(8)

        # 场景选择与语言行
        scene_row = QHBoxLayout()
        scene_row.setSpacing(10)

        self.lbl_preset = QLabel(self.tr_text("preset_label"), self)
        scene_row.addWidget(self.lbl_preset)

        self.combo_preset = QComboBox(self)
        self.combo_preset.currentIndexChanged.connect(self.on_preset_changed)
        scene_row.addWidget(self.combo_preset, 2)

        self.lbl_src_lang = QLabel(self.tr_text("src_lang_label"), self)
        scene_row.addWidget(self.lbl_src_lang)
        self.combo_lang = QComboBox(self)
        scene_row.addWidget(self.combo_lang, 1)

        self.lbl_tgt_lang = QLabel(self.tr_text("tgt_lang_label"), self)
        scene_row.addWidget(self.lbl_tgt_lang)
        self.combo_target_lang = QComboBox(self)
        scene_row.addWidget(self.combo_target_lang, 1)

        sg_layout.addLayout(scene_row)

        # 场景专属情境卡片 (Context Card with Badges)
        self.card_context = QFrame(self)
        self.card_context.setStyleSheet("""
            QFrame {
                background-color: #16161e;
                border: 1px solid #2f354a;
                border-radius: 8px;
                padding: 6px 10px;
            }
        """)
        card_layout = QVBoxLayout(self.card_context)
        card_layout.setSpacing(6)

        # 针对性策略徽章行 (Badges)
        badges_row = QHBoxLayout()
        self.lbl_badges_title = QLabel(self.tr_text("badges_header"), self.card_context)
        self.lbl_badges_title.setStyleSheet("font-weight: bold; color: #7aa2f7; font-size: 12px;")
        badges_row.addWidget(self.lbl_badges_title)

        self.badges_container = QHBoxLayout()
        self.badges_container.setSpacing(6)
        badges_row.addLayout(self.badges_container)
        badges_row.addStretch()
        card_layout.addLayout(badges_row)

        # 策略通俗说明
        self.lbl_strategy_desc = QLabel("", self.card_context)
        self.lbl_strategy_desc.setWordWrap(True)
        self.lbl_strategy_desc.setStyleSheet("color: #a9b1d6; font-size: 12px;")
        card_layout.addWidget(self.lbl_strategy_desc)

        # 针对性出演嘉宾/特有人名输入 (Friendly Entity Input)
        guest_row = QHBoxLayout()
        self.lbl_extra_names = QLabel(self.tr_text("extra_names_label"), self.card_context)
        self.lbl_extra_names.setStyleSheet("color: #e0af68; font-weight: 500;")
        guest_row.addWidget(self.lbl_extra_names)

        self.edit_extra_names = QLineEdit(self.card_context)
        self.edit_extra_names.setPlaceholderText(self.tr_text("extra_names_placeholder"))
        self.edit_extra_names.textChanged.connect(self.on_extra_names_changed)
        guest_row.addWidget(self.edit_extra_names, 1)

        card_layout.addLayout(guest_row)
        sg_layout.addWidget(self.card_context)

        # 开关选项行
        options_row = QHBoxLayout()
        self.chk_bilingual = QCheckBox(self.tr_text("chk_bilingual"), self)
        self.chk_bilingual.setChecked(True)
        options_row.addWidget(self.chk_bilingual)

        self.chk_mux = QCheckBox(self.tr_text("chk_mux"), self)
        self.chk_mux.setChecked(True)
        options_row.addWidget(self.chk_mux)

        self.chk_dynaudnorm = QCheckBox(self.tr_text("chk_dynaudnorm"), self)
        self.chk_dynaudnorm.setChecked(True)
        options_row.addWidget(self.chk_dynaudnorm)

        self.chk_skip_trans = QCheckBox(self.tr_text("chk_skip_trans"), self)
        self.chk_skip_trans.setChecked(False)
        options_row.addWidget(self.chk_skip_trans)

        options_row.addStretch()
        sg_layout.addLayout(options_row)

        # 折叠式「专家底层设置」按钮
        self.btn_toggle_expert = QPushButton(self.tr_text("btn_expert_expand"), self)
        self.btn_toggle_expert.setObjectName("textToggleBtn")
        self.btn_toggle_expert.clicked.connect(self.toggle_expert_settings)
        sg_layout.addWidget(self.btn_toggle_expert)

        # 专家底层设置容器 (折叠收纳)
        self.widget_expert = QFrame(self)
        self.widget_expert.setVisible(False)
        self.widget_expert.setStyleSheet("""
            QFrame {
                background-color: #13141c;
                border: 1px dashed #3b4261;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        expert_layout = QVBoxLayout(self.widget_expert)
        expert_layout.setSpacing(6)

        models_row = QHBoxLayout()
        self.lbl_whisper_model = QLabel(self.tr_text("whisper_model_label"), self.widget_expert)
        models_row.addWidget(self.lbl_whisper_model)
        self.combo_whisper = QComboBox(self.widget_expert)
        self.combo_whisper.addItems(["large-v3-turbo", "large-v3", "medium", "small"])
        models_row.addWidget(self.combo_whisper, 1)

        self.lbl_ollama_model = QLabel(self.tr_text("ollama_model_label"), self.widget_expert)
        models_row.addWidget(self.lbl_ollama_model)
        self.combo_ollama = QComboBox(self.widget_expert)
        models_row.addWidget(self.combo_ollama, 1)

        self.btn_refresh_models = QPushButton("🔄", self.widget_expert)
        self.btn_refresh_models.setToolTip(self.tr_text("refresh_models_tip"))
        self.btn_refresh_models.clicked.connect(self.refresh_ollama_models)
        models_row.addWidget(self.btn_refresh_models)
        expert_layout.addLayout(models_row)

        # 底层热词与Prompt微调
        raw_hw_row = QHBoxLayout()
        self.lbl_raw_hw = QLabel(self.tr_text("raw_hotwords_label"), self.widget_expert)
        raw_hw_row.addWidget(self.lbl_raw_hw)
        self.edit_raw_hotwords = QLineEdit(self.widget_expert)
        raw_hw_row.addWidget(self.edit_raw_hotwords, 1)
        expert_layout.addLayout(raw_hw_row)

        raw_p_row = QHBoxLayout()
        self.lbl_raw_p = QLabel(self.tr_text("raw_prompt_label"), self.widget_expert)
        raw_p_row.addWidget(self.lbl_raw_p)
        self.edit_raw_prompt = QLineEdit(self.widget_expert)
        raw_p_row.addWidget(self.edit_raw_prompt, 1)
        expert_layout.addLayout(raw_p_row)

        sg_layout.addWidget(self.widget_expert)

        main_layout.addWidget(self.scenario_group)

        # 4. 执行控制与实时监控
        self.exec_group = QGroupBox(self.tr_text("sec_exec"))
        eg_layout = QVBoxLayout(self.exec_group)
        eg_layout.setSpacing(6)

        prog_row = QHBoxLayout()
        self.lbl_stage = QLabel(self.tr_text("stage_ready"), self)
        self.lbl_stage.setStyleSheet("font-weight: bold; color: #7aa2f7;")
        prog_row.addWidget(self.lbl_stage)
        prog_row.addStretch()
        eg_layout.addLayout(prog_row)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(16)
        eg_layout.addWidget(self.progress_bar)

        self.console_log = QTextEdit(self)
        self.console_log.setReadOnly(True)
        self.console_log.setStyleSheet("""
            background-color: #13141c;
            color: #79d4b0;
            font-family: "Consolas", "Courier New", monospace;
            font-size: 12px;
            border: 1px solid #232534;
        """)
        self.console_log.setMinimumHeight(110)
        eg_layout.addWidget(self.console_log)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_start = QPushButton(self.tr_text("btn_start"), self)
        self.btn_start.setObjectName("primaryBtn")
        self.btn_start.setFixedHeight(36)
        self.btn_start.clicked.connect(self.start_pipeline)
        btn_row.addWidget(self.btn_start, 2)

        self.btn_cancel = QPushButton(self.tr_text("btn_cancel"), self)
        self.btn_cancel.setObjectName("cancelBtn")
        self.btn_cancel.setFixedHeight(36)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_pipeline)
        btn_row.addWidget(self.btn_cancel, 1)

        self.btn_open_folder = QPushButton(self.tr_text("btn_open_folder"), self)
        self.btn_open_folder.setFixedHeight(36)
        self.btn_open_folder.setEnabled(False)
        self.btn_open_folder.clicked.connect(self.open_output_folder)
        btn_row.addWidget(self.btn_open_folder, 1)

        self.btn_play_video = QPushButton(self.tr_text("btn_play_video"), self)
        self.btn_play_video.setFixedHeight(36)
        self.btn_play_video.setEnabled(False)
        self.btn_play_video.clicked.connect(self.play_subtitled_video)
        btn_row.addWidget(self.btn_play_video, 1)

        eg_layout.addLayout(btn_row)
        main_layout.addWidget(self.exec_group)

    def on_lang_switch_changed(self, idx: int):
        code = self.combo_ws_lang.currentData()
        if code and code != self.main_win.current_lang:
            self.main_win.set_language(code)

    def update_dropdown_languages(self):
        is_en = self.main_win.current_lang == "en"

        # 1. 场景模式下拉框 (Scenario Presets)
        cur_preset = self.combo_preset.currentData()
        self.combo_preset.blockSignals(True)
        self.combo_preset.clear()
        for p_id in core.PRESETS.keys():
            meta = SCENARIO_META.get(p_id, {})
            if is_en:
                p_text = f"{meta.get('name_en', p_id)} - {meta.get('tag_en', '')}"
            else:
                p_text = f"{meta.get('name_zh', p_id)} - {meta.get('tag_zh', '')}"
            self.combo_preset.addItem(p_text, p_id)
        if cur_preset:
            idx = self.combo_preset.findData(cur_preset)
            if idx >= 0:
                self.combo_preset.setCurrentIndex(idx)
        self.combo_preset.blockSignals(False)

        # 2. 源语言下拉框 (Source Language)
        cur_src = self.combo_lang.currentData()
        self.combo_lang.blockSignals(True)
        self.combo_lang.clear()
        src_items = [
            ("Japanese (ja)" if is_en else "日语 (ja)", "ja"),
            ("English (en)" if is_en else "英语 (en)", "en"),
            ("Korean (ko)" if is_en else "韩语 (ko)", "ko"),
            ("Cantonese (yue)" if is_en else "粤语 (yue)", "yue"),
            ("Auto Detect (auto)" if is_en else "自动检测 (auto)", "auto"),
        ]
        for text, val in src_items:
            self.combo_lang.addItem(text, val)
        if cur_src:
            idx = self.combo_lang.findData(cur_src)
            if idx >= 0:
                self.combo_lang.setCurrentIndex(idx)
        self.combo_lang.blockSignals(False)

        # 3. 目标语言下拉框 (Target Language)
        cur_tgt = self.combo_target_lang.currentData()
        self.combo_target_lang.blockSignals(True)
        self.combo_target_lang.clear()
        tgt_items = [
            ("Simplified Chinese (zh)" if is_en else "简体中文 (zh)", "zh"),
            ("Traditional Chinese (zh-TW)" if is_en else "繁体中文 (zh-TW)", "zh-tw"),
            ("English (en)" if is_en else "英语 (en)", "en"),
        ]
        for text, val in tgt_items:
            self.combo_target_lang.addItem(text, val)
        if cur_tgt:
            idx = self.combo_target_lang.findData(cur_tgt)
            if idx >= 0:
                self.combo_target_lang.setCurrentIndex(idx)
        self.combo_target_lang.blockSignals(False)

    def retranslate_ui(self):
        cur_code = self.main_win.current_lang
        idx = self.combo_ws_lang.findData(cur_code)
        if idx >= 0 and self.combo_ws_lang.currentIndex() != idx:
            self.combo_ws_lang.blockSignals(True)
            self.combo_ws_lang.setCurrentIndex(idx)
            self.combo_ws_lang.blockSignals(False)

        self.lbl_app_title.setText(self.tr_text("app_title"))
        self.btn_back_diag.setText(self.tr_text("top_diag_btn"))
        self.video_group.setTitle(self.tr_text("sec_video"))
        self.line_video_path.setPlaceholderText(self.tr_text("input_placeholder"))
        self.btn_browse.setText(self.tr_text("btn_browse"))
        self.btn_clear.setText(self.tr_text("btn_clear"))

        if not self.selected_video_path:
            self.lbl_file_info.setText(self.tr_text("waiting_video"))
            self.drop_area.update_texts(self.tr_text("drop_title"), self.tr_text("drop_hint"))
        else:
            size_bytes = self.selected_video_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            size_str = f"{size_mb / 1024:.2f} GB" if size_mb >= 1024 else f"{size_mb:.1f} MB"
            self.lbl_file_info.setText(self.tr_text("file_selected_info", name=self.selected_video_path.name, size=size_str))
            self.drop_area.update_texts(f"{self.tr_text('drop_loaded')}{self.selected_video_path.name}", self.tr_text("drop_hint"))

        self.scenario_group.setTitle(self.tr_text("sec_scenario"))
        self.lbl_preset.setText(self.tr_text("preset_label"))
        self.lbl_src_lang.setText(self.tr_text("src_lang_label"))
        self.lbl_tgt_lang.setText(self.tr_text("tgt_lang_label"))
        self.lbl_badges_title.setText(self.tr_text("badges_header"))
        self.lbl_extra_names.setText(self.tr_text("extra_names_label"))
        self.edit_extra_names.setPlaceholderText(self.tr_text("extra_names_placeholder"))

        # 同步下拉框纯中文/纯英文文本
        self.update_dropdown_languages()

        self.chk_bilingual.setText(self.tr_text("chk_bilingual"))
        self.chk_mux.setText(self.tr_text("chk_mux"))
        self.chk_dynaudnorm.setText(self.tr_text("chk_dynaudnorm"))
        self.chk_skip_trans.setText(self.tr_text("chk_skip_trans"))

        self.btn_toggle_expert.setText(
            self.tr_text("btn_expert_collapse") if self.is_expert_expanded else self.tr_text("btn_expert_expand")
        )
        self.lbl_whisper_model.setText(self.tr_text("whisper_model_label"))
        self.lbl_ollama_model.setText(self.tr_text("ollama_model_label"))
        self.lbl_raw_hw.setText(self.tr_text("raw_hotwords_label"))
        self.lbl_raw_p.setText(self.tr_text("raw_prompt_label"))

        self.exec_group.setTitle(self.tr_text("sec_exec"))
        self.btn_start.setText(self.tr_text("btn_start"))
        self.btn_cancel.setText(self.tr_text("btn_cancel"))
        self.btn_open_folder.setText(self.tr_text("btn_open_folder"))
        self.btn_play_video.setText(self.tr_text("btn_play_video"))

        # 同步执行监控状态文字
        if not (self.worker and self.worker.isRunning()):
            self.lbl_stage.setText(self.tr_text("stage_ready"))

        # 刷新场景徽章与描述
        self.on_preset_changed(self.combo_preset.currentIndex())

    def toggle_expert_settings(self):
        self.is_expert_expanded = not self.is_expert_expanded
        self.widget_expert.setVisible(self.is_expert_expanded)
        self.btn_toggle_expert.setText(
            self.tr_text("btn_expert_collapse") if self.is_expert_expanded else self.tr_text("btn_expert_expand")
        )

    def load_initial_values(self):
        self.refresh_ollama_models()
        self.on_preset_changed(0)
        self.retranslate_ui()

    def refresh_ollama_models(self):
        current_sel = self.combo_ollama.currentText()
        self.combo_ollama.clear()
        models = core.get_installed_ollama_models(self.cfg.get("ollama_url", "http://127.0.0.1:11434"))
        if not models:
            self.combo_ollama.addItem("qwen2.5:14b")
        else:
            for m in models:
                self.combo_ollama.addItem(m)
        if current_sel and self.combo_ollama.findText(current_sel) >= 0:
            self.combo_ollama.setCurrentText(current_sel)
        elif self.combo_ollama.findText("qwen2.5:14b") >= 0:
            self.combo_ollama.setCurrentText("qwen2.5:14b")

    def on_preset_changed(self, index: int):
        preset_id = self.combo_preset.currentData()
        if not preset_id or preset_id not in core.PRESETS:
            return
        p_info = core.PRESETS[preset_id]
        meta = SCENARIO_META.get(preset_id, {})
        is_en = self.main_win.current_lang == "en"

        # 渲染徽章
        while self.badges_container.count():
            item = self.badges_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        badges_list = meta.get("badges_en" if is_en else "badges_zh", [])
        for b_text in badges_list:
            pill = QLabel(f" {b_text} ", self.card_context)
            pill.setStyleSheet("""
                background-color: #24283b;
                color: #7dcfff;
                border: 1px solid #3b4261;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 11px;
                font-weight: 500;
            """)
            self.badges_container.addWidget(pill)

        # 描述说明
        desc_text = meta.get("desc_en" if is_en else "desc_zh", p_info["description"])
        self.lbl_strategy_desc.setText(desc_text)

        # 动态音频增强开关
        self.chk_dynaudnorm.setChecked(p_info["dynaudnorm"])

        # 同步底层专家设置
        self.update_raw_fields(p_info)

    def on_extra_names_changed(self, text: str):
        preset_id = self.combo_preset.currentData()
        if preset_id and preset_id in core.PRESETS:
            p_info = core.PRESETS[preset_id]
            self.update_raw_fields(p_info)

    def update_raw_fields(self, p_info: dict):
        base_hw = p_info["initial_prompt"]
        extra = self.edit_extra_names.text().strip()
        if extra:
            combined_hw = f"{extra}, {base_hw}"
        else:
            combined_hw = base_hw

        self.edit_raw_hotwords.setText(combined_hw)
        self.edit_raw_prompt.setText(p_info["system_prompt"])

    def browse_video_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件" if self.main_win.current_lang == "zh" else "Select Video File",
            "",
            "视频文件 (*.mp4 *.mkv *.mov *.avi *.flv *.webm *.ts *.m4v);;所有文件 (*.*)"
        )
        if file_path:
            self.set_video_file(file_path)

    def on_path_manual_changed(self, text: str):
        clean_text = text.strip().strip('"').strip("'")
        if clean_text and Path(clean_text).exists() and Path(clean_text).is_file():
            self.set_video_file(clean_text)

    def set_video_file(self, file_path: str):
        path_obj = Path(file_path).resolve()
        if not path_obj.exists():
            return
        self.selected_video_path = path_obj
        self.line_video_path.setText(str(path_obj))
        
        size_bytes = path_obj.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        size_str = f"{size_mb / 1024:.2f} GB" if size_mb >= 1024 else f"{size_mb:.1f} MB"

        self.lbl_file_info.setText(self.tr_text("file_selected_info", name=path_obj.name, size=size_str))
        self.lbl_file_info.setStyleSheet("color: #9ece6a; font-weight: bold; font-size: 11px;")
        self.drop_area.update_texts(f"{self.tr_text('drop_loaded')}{path_obj.name}", self.tr_text("drop_hint"))

    def clear_video_file(self):
        self.selected_video_path = None
        self.line_video_path.clear()
        self.lbl_file_info.setText(self.tr_text("waiting_video"))
        self.lbl_file_info.setStyleSheet("color: #7982a9; font-size: 11px;")
        self.drop_area.update_texts(self.tr_text("drop_title"), self.tr_text("drop_hint"))

    def log(self, text: str):
        timestamp = time.strftime("[%H:%M:%S] ")
        self.console_log.append(f"{timestamp}{text}")
        cursor = self.console_log.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.console_log.setTextCursor(cursor)

    def start_pipeline(self):
        if not self.selected_video_path or not self.selected_video_path.exists():
            QMessageBox.warning(self, "提示" if self.main_win.current_lang == "zh" else "Notice", self.tr_text("warn_no_video"))
            return

        preset_id = self.combo_preset.currentData()
        preset_data = core.PRESETS.get(preset_id, core.PRESETS["idol_variety"]).copy()

        user_cfg = self.cfg.copy()
        user_cfg.update(preset_data)

        user_cfg["language"] = self.combo_lang.currentData()
        user_cfg["whisper_model"] = self.combo_whisper.currentText()
        user_cfg["llm_model"] = self.combo_ollama.currentText().split(" ")[0]
        user_cfg["initial_prompt"] = self.edit_raw_hotwords.text().strip()
        user_cfg["system_prompt"] = self.edit_raw_prompt.text().strip()
        user_cfg["dynaudnorm"] = self.chk_dynaudnorm.isChecked()
        user_cfg["bilingual"] = self.chk_bilingual.isChecked()
        user_cfg["skip_translate"] = self.chk_skip_trans.isChecked()
        user_cfg["output_format"] = "mkv" if self.chk_mux.isChecked() else "mkv"

        self.btn_start.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.btn_open_folder.setEnabled(False)
        self.btn_play_video.setEnabled(False)
        self.progress_bar.setValue(0)
        self.lbl_stage.setText(self.tr_text("stage_starting"))
        self.console_log.clear()

        self.log(f"开始处理视频: {self.selected_video_path.name}")
        self.log(f"场景模式: {preset_data['name']}")
        self.log(f"ASR 模型: {user_cfg['whisper_model']} | 翻译模型: {user_cfg['llm_model']}")

        self.worker = SubtitleWorker(self.selected_video_path, user_cfg)
        self.worker.sig_log.connect(self.log)
        self.worker.sig_progress.connect(self.on_worker_progress)
        self.worker.sig_finished.connect(self.on_worker_finished)
        self.worker.sig_error.connect(self.on_worker_error)
        self.worker.start()

    def cancel_pipeline(self):
        if self.worker and self.worker.isRunning():
            self.lbl_stage.setText("正在取消任务..." if self.main_win.current_lang == "zh" else "Cancelling task...")
            self.worker.cancel()
            self.btn_cancel.setEnabled(False)

    def on_worker_progress(self, pct: int, text: str):
        self.progress_bar.setValue(pct)
        self.lbl_stage.setText(text)

    def on_worker_finished(self, result: dict):
        self.last_result = result
        self.btn_start.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.btn_open_folder.setEnabled(True)
        self.btn_play_video.setEnabled(True)
        self.progress_bar.setValue(100)
        self.lbl_stage.setText("🎉 完成！" if self.main_win.current_lang == "zh" else "🎉 Finished!")
        self.log(f"全部完成！字幕条数: {result['subtitles_count']} 条 | 耗时: {result['elapsed_seconds']:.1f}s")
        QMessageBox.information(
            self,
            self.tr_text("task_done_title"),
            self.tr_text("task_done_msg", name=result['video_path'].name)
        )

    def on_worker_error(self, err_msg: str):
        self.btn_start.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.lbl_stage.setText("❌ 出错" if self.main_win.current_lang == "zh" else "❌ Error")
        self.log(f"【错误】处理异常: {err_msg}")
        QMessageBox.critical(self, self.tr_text("err_title"), f"{self.tr_text('err_msg_prefix')}{err_msg}")

    def open_output_folder(self):
        target = None
        if self.last_result and "video_path" in self.last_result:
            target = self.last_result["video_path"].parent
        elif self.selected_video_path:
            target = self.selected_video_path.parent

        if target and target.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))

    def play_subtitled_video(self):
        if self.last_result and "video_path" in self.last_result:
            v_path = self.last_result["video_path"]
            if v_path.exists():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(v_path)))


# ==============================================================================
# 顶层主窗口 (Stacked Window)
# ==============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_lang = "zh"
        self.setWindowTitle("本地 AI 视频字幕翻译与封装工作台 (Local Subtitler Pro)")
        self.resize(1040, 830)
        self.setMinimumSize(940, 720)

        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        self.diag_page = DiagnosticPage(self)
        self.diag_page.enter_main_signal.connect(self.go_to_workspace)
        self.stack.addWidget(self.diag_page)

        self.workspace_page = WorkspacePage(self)
        self.workspace_page.back_to_diag_signal.connect(self.go_to_diagnostic)
        self.stack.addWidget(self.workspace_page)

        self.stack.setCurrentIndex(0)
        self.diag_page.run_checks()

    def set_language(self, lang_code: str):
        if lang_code in ("zh", "en"):
            self.current_lang = lang_code
            self.setWindowTitle(I18N[lang_code]["app_title"])
            self.diag_page.retranslate_ui()
            self.workspace_page.retranslate_ui()

    def go_to_workspace(self):
        self.stack.setCurrentIndex(1)

    def go_to_diagnostic(self):
        self.stack.setCurrentIndex(0)
        self.diag_page.run_checks()


def setup_exception_hook():
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        import traceback
        err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        crash_log = Path(__file__).resolve().parent / "gui_crash.log"
        try:
            with open(crash_log, "a", encoding="utf-8") as f:
                f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Unhandled Exception:\n{err_msg}\n")
        except Exception:
            pass
        print(f"[Crash] {err_msg}", file=sys.stderr)
        try:
            QMessageBox.critical(None, "程序运行异常", f"程序遇到未捕获的错误：\n\n{err_msg}")
        except Exception:
            pass
    sys.excepthook = handle_exception


def main():
    setup_exception_hook()
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
