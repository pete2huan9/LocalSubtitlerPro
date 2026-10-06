#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Video Subtitle Automation Pipeline & Core Engine
Supports:
- Dynamic Loudness Normalization (dynaudnorm)
- Zero-Loss Whisper Recognition & Golden Duration Merging (2.0s - 5.5s)
- 5 Tailored Scenario Presets (Idol Variety, Concert, Livestream, Anime, Drama)
- Robust Local LLM Translation with Auto-Retry (Ollama)
- Soft Subtitle Muxing (MKV / MP4)
- Complete API for GUI integration (Prerequisites check, progress callbacks, cancellation)
"""

import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

__version__ = "0.2.0"

import re
import sys
import time
import json
import wave
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

try:
    import numpy as np
    import requests
    from tqdm import tqdm
    from faster_whisper import WhisperModel
except ImportError:
    pass

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.json"

# ==============================================================================
# 五大场景预设配置库 (Scenario Presets)
# ==============================================================================
PRESETS: Dict[str, Dict[str, Any]] = {
    "idol_variety": {
        "id": "idol_variety",
        "name": "🌟 演艺/偶像综艺 (Variety Show)",
        "tag": "真人秀 / 娱乐访谈 / 演艺日常",
        "description": "针对演艺综艺杂音与轻声语境优化。增强微弱人声，保留自然口癖习惯与真实情感，自动校准行业圈内术语。",
        "vad_filter": False,
        "dynaudnorm": True,
        "target_min": 2.0,
        "target_max": 5.5,
        "initial_prompt": "バラエティ, 番組, 劇場公演, 休養, 選抜, センター, 総選挙, 握手会, お話し会, キャプテン, チーム, 推し, 推しメン, あの, なんか, そうなんですよ, 嬉しかったです",
        "system_prompt": (
            "你是资深演艺与综艺字幕组主翻译。请将输入的日文台词逐句翻译为地道、传神、生动的简体中文字幕：\n"
            "【核心翻译准则】：\n"
            "1. 【保留灵魂语气词与情绪】：妥善传达说话者害羞、真诚的情感与自然口语语气。\n"
            "2. 【专有词与ASR谐音纠错】：根据综艺情境精准识别行业术语与圈内用词，若遇到ASR音近识别偏差，请结合上下文常识自动纠错后翻译。\n"
            "3. 保持编号严格对应，不要添加任何额外废话或开场白。"
        )
    },
    "concert_live": {
        "id": "concert_live",
        "name": "🎤 现场舞台/演唱会 (Live & Concert)",
        "tag": "现场Live / 舞台演出 / 音乐互动",
        "description": "针对伴奏背景声强化人声提取，抑制音乐伴奏混杂；优化单句时长，翻译贴合现场舞台互动与欢呼气氛。",
        "vad_filter": True,
        "dynaudnorm": True,
        "target_min": 1.5,
        "target_max": 4.0,
        "initial_prompt": "コンサート, ライブ, 音楽, ステージ, アンコール, MC, ファン, 会場, 盛り上がって, 一緒に, ありがとう, 叫べ",
        "system_prompt": (
            "你是专业演唱会及舞台现场字幕翻译。请将输入的台词逐句翻译为富有现场感染力、元气满满的简体中文字幕：\n"
            "1. 贴合舞台 MC 互动语境，生动传神传达台上台下呼应与激动情绪。\n"
            "2. 若遇歌词或舞台口号，语言富有节律与表现力。\n"
            "3. 严格按序号输出对应翻译，不添加额外说明。"
        )
    },
    "livestream_vlog": {
        "id": "livestream_vlog",
        "name": "🎮 网络直播/Vlog杂谈 (Livestream & Vlog)",
        "tag": "个人直播 / 游戏实况 / 日常Vlog",
        "description": "适应个人麦克风与快速连环说话，停顿容差适中；翻译采用现代接地气网感，适配网络交流与流行用语。",
        "vad_filter": False,
        "dynaudnorm": True,
        "target_min": 1.8,
        "target_max": 5.0,
        "initial_prompt": "配信, 雑談, チャンネル登録, 高評価, スパチャ, コメント, リスナー, 今日は, あの, えーと, 草, やばい, マジで",
        "system_prompt": (
            "你是熟悉网络流行语与主播文化的现代字幕翻译。请将输入的台词逐句翻译为生动接地气、带有当代网感的简体中文字幕：\n"
            "1. 口语化自然流畅，契合主播与粉丝日常弹幕互动的轻松聊天语境。\n"
            "2. 准确翻译游戏术语、网络热梗与口语缩写。\n"
            "3. 严格按序号输出对应翻译。"
        )
    },
    "anime_seiyuu": {
        "id": "anime_seiyuu",
        "name": "🌸 二次元/声优番组 (Anime & Seiyuu)",
        "tag": "声优广播 / 动画特典 / ACG生放送",
        "description": "保留原声高频细节，兼顾敬语体系与称谓习惯；采用典雅二次元汉化风格，生动传达角色与语境魅力。",
        "vad_filter": False,
        "dynaudnorm": False,
        "target_min": 2.0,
        "target_max": 5.0,
        "initial_prompt": "声優, ラジオ, アニメ, アフレコ, キャラクター, 先輩, 後輩, イベント, リスナー, さん, ちゃん, 先生, 第1話",
        "system_prompt": (
            "你是资深 ACG 及声优广播字幕翻译。请将输入的台词逐句翻译为符合二次元语境、优雅地道的简体中文字幕：\n"
            "1. 圈内人名与称谓遵循汉化习惯（如保留XX桑、XX酱、XX前辈等称谓美感）。\n"
            "2. 风格贴合声优访谈与广播剧生动语气，敬语与吐槽恰如其分。\n"
            "3. 严格按序号输出对应翻译。"
        )
    },
    "drama_interview": {
        "id": "drama_interview",
        "name": "🎬 影视剧集/正规访谈 (Drama & Interview)",
        "tag": "影视剧集 / 纪录片 / 正式专访",
        "description": "追求信达雅书面语与影视剧规范。启用精准断句，适当弱化多余无意义沉吟，行文工整沉稳、契合影视标准。",
        "vad_filter": True,
        "dynaudnorm": False,
        "target_min": 2.5,
        "target_max": 6.0,
        "initial_prompt": "インタビュー, 取材, ドキュメンタリー, 映画, ドラマ, 監督, 撮影, 物語, 現場, 歴史, 社会, 感謝",
        "system_prompt": (
            "你是影视剧与纪录片专业字幕翻译。请将输入的台词逐句翻译为工整凝练、信达雅的影视级简体中文字幕：\n"
            "1. 语言典雅考究，符合正式对话与纪录片沉稳的语言规范。\n"
            "2. 适当提炼长句，精简无实际意义的沉吟与口语碎词。\n"
            "3. 严格按序号输出对应翻译。"
        )
    }
}


def load_config() -> Dict[str, Any]:
    default_config = {
        "whisper_model": "large-v3-turbo",
        "language": "ja",
        "target_lang": "zh",
        "device": "cpu",
        "compute_type": "int8",
        "cpu_threads": 12,
        "preset": "idol_variety",
        "vad_filter": False,
        "dynaudnorm": True,
        "initial_prompt": PRESETS["idol_variety"]["initial_prompt"],
        "system_prompt": PRESETS["idol_variety"]["system_prompt"],
        "llm_model": "qwen2.5:14b",
        "ollama_url": "http://127.0.0.1:11434",
        "batch_size": 8,
        "bilingual": True,
        "output_format": "mkv"
    }
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                default_config.update(cfg)
        except Exception:
            pass
    return default_config


def save_config(cfg: Dict[str, Any]):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def check_prerequisites() -> Dict[str, Dict[str, Any]]:
    """
    检查本地四大核心依赖：FFmpeg、Ollama 服务、翻译大模型、Whisper 库。
    """
    checks = {}

    # 1. FFmpeg
    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin:
        checks["ffmpeg"] = {
            "passed": True,
            "title": "FFmpeg 媒体处理引擎",
            "detail": f"已就绪: {ffmpeg_bin}",
            "fix_guide": "",
            "command": ""
        }
    else:
        checks["ffmpeg"] = {
            "passed": False,
            "title": "FFmpeg 媒体处理引擎",
            "detail": "系统 PATH 中未检测到 ffmpeg.exe",
            "fix_guide": "请下载 FFmpeg 并将其 bin 目录添加至系统环境变量 PATH 中，或安装至 C:\\Program Files\\ffmpeg\\bin",
            "command": "winget install Gyan.FFmpeg"
        }

    # 2. Ollama 服务
    ollama_ok = False
    installed_models = []
    try:
        res = requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
        if res.status_code == 200:
            ollama_ok = True
            data = res.json()
            installed_models = [m["name"] for m in data.get("models", [])]
    except Exception:
        pass

    if ollama_ok:
        checks["ollama_service"] = {
            "passed": True,
            "title": "Ollama 本地大模型服务",
            "detail": "服务正常运行中 (127.0.0.1:11434)",
            "fix_guide": "",
            "command": ""
        }
    else:
        checks["ollama_service"] = {
            "passed": False,
            "title": "Ollama 本地大模型服务",
            "detail": "未能连接到 Ollama 服务 (127.0.0.1:11434)",
            "fix_guide": "请确保已安装 Ollama 并在后台启动（可在开始菜单搜索 Ollama 启动）。",
            "command": "ollama serve"
        }

    # 3. 翻译大模型检测
    if not ollama_ok:
        checks["ollama_model"] = {
            "passed": False,
            "title": "本地翻译大模型 (LLM)",
            "detail": "等待 Ollama 服务启动后检测模型",
            "fix_guide": "启动 Ollama 后将自动检查可用模型",
            "command": "ollama run qwen2.5:14b"
        }
    elif installed_models:
        model_names_str = ", ".join(installed_models[:3]) + (" 等" if len(installed_models) > 3 else "")
        checks["ollama_model"] = {
            "passed": True,
            "title": "本地翻译大模型 (LLM)",
            "detail": f"已检测到可用模型: {model_names_str}",
            "models": installed_models,
            "fix_guide": "",
            "command": ""
        }
    else:
        checks["ollama_model"] = {
            "passed": False,
            "title": "本地翻译大模型 (LLM)",
            "detail": "Ollama 服务已运行，但尚未下载任何模型",
            "fix_guide": "推荐拉取高性能翻译模型 Qwen2.5-14B，请在命令行中执行：",
            "command": "ollama run qwen2.5:14b"
        }

    # 4. Whisper 库检测
    whisper_ok = False
    try:
        import faster_whisper
        whisper_ok = True
        checks["whisper"] = {
            "passed": True,
            "title": "Faster-Whisper 语音识别引擎",
            "detail": "Python 库与 CTranslate2 后端加载正常",
            "fix_guide": "",
            "command": ""
        }
    except Exception as e:
        checks["whisper"] = {
            "passed": False,
            "title": "Faster-Whisper 语音识别引擎",
            "detail": f"模块加载异常: {e}",
            "fix_guide": "请在虚拟环境中安装 faster-whisper 依赖：",
            "command": "pip install faster-whisper"
        }

    return checks


def get_installed_ollama_models(ollama_url: str = "http://127.0.0.1:11434") -> List[str]:
    try:
        res = requests.get(f"{ollama_url}/api/tags", timeout=3)
        if res.status_code == 200:
            return [m["name"] for m in res.json().get("models", [])]
    except Exception:
        pass
    return []


def format_timestamp(seconds: float) -> str:
    total_ms = int(round(max(seconds, 0.0) * 1000))
    hrs, rem = divmod(total_ms, 3600 * 1000)
    mins, rem = divmod(rem, 60 * 1000)
    secs, millis = divmod(rem, 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def extract_audio(video_path: Path, output_audio: Path, dynaudnorm: bool = True, log_cb: Optional[Callable[[str], None]] = None):
    msg = f"正在从视频抽取音轨并预处理 (动态增益={dynaudnorm})..."
    if log_cb:
        log_cb(msg)
    else:
        print(f"\n[1/4] {msg}")

    af_filters = ["dynaudnorm=p=0.9:m=15:g=15"] if dynaudnorm else []
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",
        "-ar", "16000",
        "-ac", "1",
    ]
    if af_filters:
        cmd.extend(["-af", ",".join(af_filters)])
    cmd.extend(["-c:a", "pcm_s16le", str(output_audio)])

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if log_cb:
        log_cb("✓ 音频提取与优化完成。")


def load_wav_as_numpy(wav_path: Path) -> np.ndarray:
    with wave.open(str(wav_path), "rb") as wf:
        sampwidth = wf.getsampwidth()
        frames = wf.readframes(wf.getnframes())

    if sampwidth == 2:
        return np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 4:
        return np.frombuffer(frames, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        return np.frombuffer(frames, dtype=np.uint8).astype(np.float32) / 128.0 - 1.0


def merge_semantic_subtitles(raw_segments: list, target_min: float = 2.0, target_max: float = 5.5) -> List[Dict[str, Any]]:
    """
    黄金时长语义合并器：
    - 严格将单句时长控制在 target_min ~ target_max 区间；
    - 将破碎短词（如 "あの"、"そう"、"それのおかげで"）智能并入对应主从句。
    """
    res = []
    cur = None

    for seg in raw_segments:
        text = seg.text.strip().replace(" ", "")
        if not text:
            continue
        if cur is None:
            cur = {"start": seg.start, "end": seg.end, "text": text}
            continue

        gap = seg.start - cur["end"]
        merged_dur = seg.end - cur["start"]
        cur_dur = cur["end"] - cur["start"]

        should_merge = False
        if merged_dur <= target_max:
            if cur_dur < target_min and gap < 2.0:
                should_merge = True
            elif any(cur["text"].endswith(t) for t in ("のおかげで", "した時に", "そうなの", "なんか", "おしから", "おし")) and gap < 1.5:
                should_merge = True

        if should_merge:
            cur["end"] = seg.end
            cur["text"] = cur["text"] + " " + text
        else:
            res.append(cur)
            cur = {"start": seg.start, "end": seg.end, "text": text}

    if cur:
        res.append(cur)

    for idx, s in enumerate(res, 1):
        s["index"] = idx

    return res


def transcribe_audio(
    audio_path: Path,
    cfg: Dict[str, Any],
    log_cb: Optional[Callable[[str], None]] = None,
    progress_cb: Optional[Callable[[int, str], None]] = None,
    cancel_check: Optional[Callable[[], bool]] = None
) -> List[Dict[str, Any]]:
    model_name = cfg.get("whisper_model", "large-v3-turbo")
    device = cfg.get("device", "cpu")
    compute_type = cfg.get("compute_type", "int8")
    cpu_threads = cfg.get("cpu_threads", 12)
    language = cfg.get("language", "ja")
    initial_prompt = cfg.get("initial_prompt", "")
    vad_filter = cfg.get("vad_filter", False)
    target_min = float(cfg.get("target_min", 2.0))
    target_max = float(cfg.get("target_max", 5.5))

    msg = f"加载 Whisper [{model_name}] (设备={device}, 精度={compute_type}, 线程={cpu_threads}, VAD={vad_filter})..."
    if log_cb:
        log_cb(msg)

    audio_data = load_wav_as_numpy(audio_path)
    audio_duration = len(audio_data) / 16000.0

    model = WhisperModel(
        model_name,
        device=device,
        compute_type=compute_type,
        cpu_threads=cpu_threads
    )

    if log_cb:
        log_cb(f"开始 ASR 语音识别 (音频总时长: {audio_duration:.1f} 秒)...")

    segments, info = model.transcribe(
        audio_data,
        language=language if language != "auto" else None,
        beam_size=5,
        vad_filter=vad_filter,
        initial_prompt=initial_prompt
    )

    if log_cb:
        log_cb(f"检测语言: {info.language} (可信度: {info.language_probability:.2f})")

    raw_segments = []
    for seg in segments:
        if cancel_check and cancel_check():
            raise InterruptedError("用户取消了任务")
        raw_segments.append(seg)
        if progress_cb and audio_duration > 0:
            # 语音识别占总体进度的 25% ~ 65%
            pct = 25 + int((seg.end / audio_duration) * 40)
            progress_cb(min(pct, 65), f"ASR 转写中: {seg.end:.1f}s / {audio_duration:.1f}s")

    subtitles = merge_semantic_subtitles(raw_segments, target_min=target_min, target_max=target_max)
    if log_cb:
        log_cb(f"✓ 语音识别与黄金时长断句完成，生成 {len(subtitles)} 条精炼字幕。")
    return subtitles


def translate_with_ollama(
    subtitles: List[Dict[str, Any]],
    cfg: Dict[str, Any],
    log_cb: Optional[Callable[[str], None]] = None,
    progress_cb: Optional[Callable[[int, str], None]] = None,
    cancel_check: Optional[Callable[[], bool]] = None
) -> List[str]:
    ollama_url = cfg.get("ollama_url", "http://127.0.0.1:11434")
    model_name = cfg.get("llm_model", "qwen2.5:14b")
    batch_size = int(cfg.get("batch_size", 8))
    system_prompt = cfg.get("system_prompt", PRESETS["idol_variety"]["system_prompt"])

    total = len(subtitles)
    if log_cb:
        log_cb(f"连接本地 Ollama [{model_name}] 进行语境翻译 (共 {total} 条字幕，批次大小 {batch_size})...")

    translated_texts = []
    
    total_batches = (total + batch_size - 1) // batch_size
    batch_num = 0

    for i in range(0, total, batch_size):
        if cancel_check and cancel_check():
            raise InterruptedError("用户取消了任务")

        batch_num += 1
        batch = subtitles[i:i + batch_size]
        batch_prompt = "\n".join([f"{item['index']}: {item['text']}" for item in batch])

        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请翻译以下台词，严格对应原序号输出：\n{batch_prompt}"}
            ],
            "stream": False,
            "keep_alive": "10m",
            "options": {"temperature": 0.2}
        }

        line_map = {}
        for attempt in range(1, 4):
            if cancel_check and cancel_check():
                raise InterruptedError("用户取消了任务")
            try:
                res = requests.post(f"{ollama_url}/api/chat", json=payload, timeout=90)
                if res.status_code == 200:
                    content = res.json().get("message", {}).get("content", "")
                    for line in content.strip().split("\n"):
                        m = re.match(r"^\s*\[?(\d+)\]?\s*[:：.、\]]\s*(.*)$", line.strip())
                        if m:
                            line_map[int(m.group(1))] = m.group(2).strip()
                    if line_map:
                        break
                time.sleep(1.5)
            except Exception as e:
                if attempt == 3 and log_cb:
                    log_cb(f"⚠ 批次 {batch_num} 翻译超时重试失败: {e}")
                time.sleep(1.5)

        for item in batch:
            idx = item["index"]
            trans = line_map.get(idx)
            if trans and trans != item["text"]:
                translated_texts.append(trans)
            else:
                translated_texts.append(item["text"])

        if progress_cb:
            # 翻译占总体进度的 65% ~ 90%
            pct = 65 + int((batch_num / total_batches) * 25)
            progress_cb(min(pct, 90), f"翻译中: 批次 {batch_num}/{total_batches} ({min(i + batch_size, total)}/{total}条)")

    if log_cb:
        log_cb(f"✓ 大模型翻译完成，共处理 {len(translated_texts)} 条台词。")
    return translated_texts


def write_srt(subtitles: List[Dict[str, Any]], translations: List[str], output_path: Path, bilingual: bool = True, log_cb: Optional[Callable[[str], None]] = None):
    with open(output_path, "w", encoding="utf-8") as f:
        for idx, item in enumerate(subtitles):
            f.write(f"{item['index']}\n")
            f.write(f"{format_timestamp(item['start'])} --> {format_timestamp(item['end'])}\n")
            zh_text = translations[idx] if idx < len(translations) else item["text"]
            if bilingual and zh_text != item["text"]:
                f.write(f"{zh_text}\n{item['text']}\n\n")
            else:
                f.write(f"{zh_text}\n\n")

    msg = f"✓ 独立字幕已保存: {output_path.name}"
    if log_cb:
        log_cb(msg)
    else:
        print(f" -> {msg}")


def mux_subtitles(video_path: Path, srt_path: Path, output_video: Path, log_cb: Optional[Callable[[str], None]] = None):
    msg = f"正在封装软字幕至视频轨道 ({output_video.name})..."
    if log_cb:
        log_cb(msg)
    else:
        print(f"\n[4/4] {msg}")

    is_mp4 = output_video.suffix.lower() == ".mp4"
    sub_codec = "mov_text" if is_mp4 else "srt"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(srt_path),
        "-map", "0:v?", "-map", "0:a?", "-map", "1:0",
        "-c", "copy",
        "-c:s", sub_codec,
        "-metadata:s:s:0", "language=chi",
        "-metadata:s:s:0", "title=中日双语字幕 (可切换/隐藏)",
        "-disposition:s:0", "default",
        str(output_video)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if log_cb:
        log_cb(f"✓ 封装完成！输出视频: {output_video.name}")


def run_pipeline(
    video_path: Path,
    config: Dict[str, Any],
    log_cb: Optional[Callable[[str], None]] = None,
    progress_cb: Optional[Callable[[int, str], None]] = None,
    cancel_check: Optional[Callable[[], bool]] = None
) -> Dict[str, Any]:
    """
    供 GUI 或脚本调用的一站式完整字幕流水线。
    """
    input_video = Path(video_path).resolve()
    if not input_video.exists():
        raise FileNotFoundError(f"未找到输入视频文件: {input_video}")

    work_dir = input_video.parent
    base_name = input_video.stem
    temp_audio = work_dir / f"{base_name}_temp_norm.wav"
    output_srt = work_dir / f"{base_name}.srt"
    output_format = config.get("output_format", "mkv")
    output_video = work_dir / f"{base_name}_subtitled.{output_format}"

    start_time = time.time()

    try:
        # 阶段 1: 抽取并优化音频 (0% -> 25%)
        if progress_cb:
            progress_cb(5, "[1/4] 抽取音频轨道并执行轻声增益...")
        dynaudnorm = config.get("dynaudnorm", True)
        extract_audio(input_video, temp_audio, dynaudnorm=dynaudnorm, log_cb=log_cb)
        if progress_cb:
            progress_cb(25, "[1/4] 音频提取就绪，启动语音识别引擎...")

        # 阶段 2: ASR 转写 (25% -> 65%)
        subtitles = transcribe_audio(
            temp_audio,
            config,
            log_cb=log_cb,
            progress_cb=progress_cb,
            cancel_check=cancel_check
        )

        if not subtitles:
            raise ValueError("在音频中未能检测到有效对白。")

        # 阶段 3: 本地大模型翻译 (65% -> 90%)
        if progress_cb:
            progress_cb(65, "[3/4] 启动本地大模型语境翻译...")
        if config.get("skip_translate", False):
            translations = [item["text"] for item in subtitles]
            if log_cb:
                log_cb("已根据设置跳过翻译，保留原文。")
        else:
            translations = translate_with_ollama(
                subtitles,
                config,
                log_cb=log_cb,
                progress_cb=progress_cb,
                cancel_check=cancel_check
            )

        # 写入 SRT
        bilingual = config.get("bilingual", True)
        write_srt(subtitles, translations, output_srt, bilingual=bilingual, log_cb=log_cb)

        # 阶段 4: 封装视频 (90% -> 100%)
        if progress_cb:
            progress_cb(92, "[4/4] 正在将字幕轨道封装进视频...")
        mux_subtitles(input_video, output_srt, output_video, log_cb=log_cb)

        if progress_cb:
            progress_cb(100, "🎉 全部完成！软字幕视频已就绪。")

        elapsed = time.time() - start_time
        return {
            "status": "success",
            "srt_path": output_srt,
            "video_path": output_video,
            "subtitles_count": len(subtitles),
            "elapsed_seconds": elapsed
        }

    finally:
        if temp_audio.exists():
            try:
                temp_audio.unlink()
            except Exception:
                pass


def main():
    cfg = load_config()

    parser = argparse.ArgumentParser(description="本地 AI 视频字幕翻译与封装工具 (CLI)")
    parser.add_argument("--video", "-v", required=True, help="输入视频完整路径")
    parser.add_argument("--preset", default="idol_variety", choices=list(PRESETS.keys()), help="选择场景预设")
    parser.add_argument("--whisper-model", default=cfg["whisper_model"])
    parser.add_argument("--llm-model", default=cfg["llm_model"])
    parser.add_argument("--bilingual", action="store_true", default=cfg.get("bilingual", True))
    parser.add_argument("--format", choices=["mkv", "mp4"], default=cfg.get("output_format", "mkv"))
    parser.add_argument("--skip-translate", action="store_true")
    
    args = parser.parse_args()

    # 应用场景预设覆盖
    preset_data = PRESETS.get(args.preset, PRESETS["idol_variety"])
    cfg.update(preset_data)
    cfg["whisper_model"] = args.whisper_model
    cfg["llm_model"] = args.llm_model
    cfg["bilingual"] = args.bilingual
    cfg["output_format"] = args.format
    cfg["skip_translate"] = args.skip_translate

    res = run_pipeline(Path(args.video), cfg)
    print(f"\n[完成] 耗时 {res['elapsed_seconds']:.1f} 秒，字幕已生成: {res['video_path']}")


if __name__ == "__main__":
    main()
