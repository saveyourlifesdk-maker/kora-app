# -*- coding: utf-8 -*-
"""
KORA AI ENGINE - PRODUCTION CLIENT & T4 SERVER
Fix: Crash-Proof Threading, Safe File I/O, Auto RGB Optimization,
Custom Device Gallery Selector & Screen Isolation
"""

import os
import sys
import io
import time
import json
import base64
import random
import threading
import urllib.request
import urllib.error
import ssl
import re
import webbrowser

# ================================================================
# 1. WINDOWS HIGH-DPI AWARENESS (Clear & Sharp UI)
# ================================================================
if sys.platform == 'win32' or os.name == 'nt':
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.stencilview import StencilView
from kivy.uix.scatter import Scatter
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import AsyncImage
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, StringProperty, BooleanProperty

try:
    from PIL import Image
    HAS_PIL = True
except Exception:
    HAS_PIL = False

Window.clearcolor = (0.015, 0.02, 0.027, 1)
Window.softinput_mode = 'below_target'

# ================================================================
# 2. COLAB BACKEND ENGINE (Clean Dependency Loading)
# ================================================================
COLAB_SERVER_CODE = r'''# ================================================================
# 🚀 KORA TRUE 4K IMAGE & 10s HD VIDEO AI ENGINE (AUDIO PRESERVED)
# ================================================================
import os, sys, subprocess

print("⏳ [1/5] पुराने प्रोसेस और पोर्ट 5000 साफ हो रहे हैं...")
os.system("fuser -k 5000/tcp || true")
os.system("pkill -f ngrok || true")

packages = [
    "onnx", "onnxruntime", "insightface", "flask",
    "flask-cors", "pillow", "opencv-python-headless", "pyngrok"
]
subprocess.check_call(["apt-get", "update", "-qq"])
subprocess.check_call(["apt-get", "install", "-y", "-qq", "ffmpeg"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--no-cache-dir"] + packages)

import time, uuid, shutil, threading, io, cv2, torch, numpy as np
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import insightface
from insightface.app import FaceAnalysis
from pyngrok import ngrok

NGROK_TOKEN = "3KMAkgJseCsVlJw0nR3fouTTMjd_3739Uv9AdzjRzVEi3DtK3"
FIXED_DOMAIN = "unpack-stick-robe.ngrok-free.dev"

UPLOAD_DIR = "/tmp/kora_uploads"
OUTPUT_DIR = "/tmp/kora_outputs"
MODEL_DIR = "/root/.insightface/models"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{MODEL_DIR}/buffalo_l", exist_ok=True)

if not os.path.exists(f"{MODEL_DIR}/buffalo_l/w600k_r50.onnx"):
    os.system("curl -L --progress-bar -o /tmp/buffalo_l.zip https://huggingface.co/huaquan/buffalo_l/resolve/main/buffalo_l.zip")
    os.system("unzip -q -o /tmp/buffalo_l.zip -d /tmp/buf_ext/")
    for root, _, files in os.walk("/tmp/buf_ext"):
        for f in files:
            if f.endswith(".onnx"):
                shutil.copy(os.path.join(root, f), f"{MODEL_DIR}/buffalo_l/")

if not os.path.exists(f"{MODEL_DIR}/inswapper_128.onnx"):
    os.system(f"curl -L --progress-bar -o {MODEL_DIR}/inswapper_128.onnx https://huggingface.co/xingren23/comfyflow-models/resolve/main/insightface/inswapper_128.onnx")

providers = ['CPUExecutionProvider']

app_face = FaceAnalysis(name='buffalo_l', providers=providers)
app_face.prepare(ctx_id=-1, det_size=(640, 640))

swapper = insightface.model_zoo.get_model(
    f"{MODEL_DIR}/inswapper_128.onnx",
    download=False,
    providers=providers
)

print("✅ AI इंजन तैयार है (Image + Video Mode)")

server = Flask(__name__)
CORS(server)

JOBS = {}

def get_target_dims(ratio_str, res_str):
    dims_table = {
        "720p": {"9:16": (720, 1280), "1:1": (720, 720), "16:9": (1280, 720), "4:5": (720, 900), "3:4": (720, 960)},
        "1080p": {"9:16": (1080, 1920), "1:1": (1080, 1080), "16:9": (1920, 1080), "4:5": (1080, 1350), "3:4": (1080, 1440)},
        "2K": {"9:16": (1440, 2560), "1:1": (1440, 1440), "16:9": (2560, 1440), "4:5": (1440, 1800), "3:4": (1440, 1920)},
        "4K": {"9:16": (2160, 3840), "1:1": (2160, 2160), "16:9": (3840, 2160), "4:5": (2160, 2700), "3:4": (2160, 2880)}
    }
    r = "16:9" if "16:9" in ratio_str else ("1:1" if "1:1" in ratio_str else ("4:5" if "4:5" in ratio_str else ("3:4" if "3:4" in ratio_str else "9:16")))
    res = "4K" if "4K" in res_str else ("2K" if "2K" in res_str else ("1080p" if "1080p" in res_str else "720p"))
    return dims_table.get(res, {}).get(r, (720, 1280))

def fit_frame(frame, tw, th):
    fh, fw = frame.shape[:2]
    target_aspect = tw / float(th)
    frame_aspect = fw / float(fh)
    if frame_aspect > target_aspect:
        nw = int(fh * target_aspect)
        sx = max(0, (fw - nw) // 2)
        cropped = frame[:, sx:sx + nw]
    else:
        nh = int(fw / target_aspect)
        sy = max(0, (fh - nh) // 2)
        cropped = frame[sy:sy + nh, :]
    return cv2.resize(cropped, (tw, th), interpolation=cv2.INTER_LANCZOS4 if tw > fw else cv2.INTER_AREA)

def get_largest_face(faces):
    if not faces: return None
    return max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))

# ================= VIDEO PROCESSING WORKER =================
def execute_video_swap(job_id, in_vid, m_path, f_path, ratio, resolution):
    try:
        JOBS[job_id] = {"status": "processing", "progress": 5, "error": None}
        tw, th = get_target_dims(ratio, resolution)

        # Source Faces Extraction
        m_source, f_source = None, None
        if m_path and os.path.exists(m_path):
            img_m = cv2.imread(m_path)
            if img_m is not None:
                faces = app_face.get(img_m)
                m_source = get_largest_face(faces)

        if f_path and os.path.exists(f_path):
            img_f = cv2.imread(f_path)
            if img_f is not None:
                faces = app_face.get(img_f)
                f_source = get_largest_face(faces)

        if not m_source and not f_source:
            JOBS[job_id] = {
                "status": "failed",
                "progress": 0,
                "error": "फोटो में कोई इंसानी चेहरा नहीं मिला! कृपया किसी इंसान की फोटो चुनें (जानवर की नहीं)।"
            }
            return

        cap = cv2.VideoCapture(in_vid)
        if not cap.isOpened():
            JOBS[job_id] = {"status": "failed", "progress": 0, "error": "वीडियो फ़ाइल लोड नहीं हो सकी"}
            return

        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or int(fps * 10)
        max_process = min(total_frames, int(fps * 10))

        raw_swap_path = os.path.join(OUTPUT_DIR, f"{job_id}_raw.mp4")
        final_mp4_path = os.path.join(OUTPUT_DIR, f"{job_id}_final.mp4")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(raw_swap_path, fourcc, fps, (tw, th))

        single_source = m_source if m_source else f_source

        frame_idx = 0
        while cap.isOpened() and frame_idx < max_process:
            ret, frame = cap.read()
            if not ret: break

            frame = fit_frame(frame, tw, th)
            detected = app_face.get(frame)

            for face in detected:
                if m_source and f_source:
                    if face.gender == 1 and m_source:
                        frame = swapper.get(frame, face, m_source, paste_back=True)
                    elif face.gender == 0 and f_source:
                        frame = swapper.get(frame, face, f_source, paste_back=True)
                else:
                    frame = swapper.get(frame, face, single_source, paste_back=True)

            writer.write(frame)
            frame_idx += 1
            JOBS[job_id]["progress"] = int(5 + (frame_idx / float(max_process)) * 82)

        cap.release()
        writer.release()
        JOBS[job_id]["progress"] = 90

        # FFmpeg Audio Sync (ओरिजिनल आवाज जोड़ना)
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", raw_swap_path, "-i", in_vid,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
            "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0?",
            "-shortest", final_mp4_path
        ]
        res = subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode != 0 or not os.path.exists(final_mp4_path):
            shutil.move(raw_swap_path, final_mp4_path)
        else:
            if os.path.exists(raw_swap_path): os.remove(raw_swap_path)

        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["progress"] = 100
        JOBS[job_id]["file"] = final_mp4_path

    except Exception as exc:
        JOBS[job_id] = {"status": "failed", "progress": 0, "error": str(exc)}

# ================= API ROUTES =================
@server.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "online"}), 200

@server.route('/api/swap_image', methods=['POST'])
def swap_image():
    try:
        if 'source' not in request.files or 'target' not in request.files:
            return jsonify({"error": "फ़ोटो प्राप्त नहीं हुई"}), 400

        ratio = request.form.get('ratio', '9:16')
        res = request.form.get('resolution', '4K Ultra HD')
        tw, th = get_target_dims(ratio, res)

        s_bytes = np.frombuffer(request.files['source'].read(), np.uint8)
        t_bytes = np.frombuffer(request.files['target'].read(), np.uint8)

        s_img = cv2.imdecode(s_bytes, cv2.IMREAD_COLOR)
        t_img = cv2.imdecode(t_bytes, cv2.IMREAD_COLOR)

        s_faces = app_face.get(s_img)
        t_faces = app_face.get(t_img)

        source_face = get_largest_face(s_faces)
        target_face = get_largest_face(t_faces)

        if not source_face:
            return jsonify({"error": "Face Image में कोई इंसानी चेहरा नहीं मिला!"}), 422
        if not target_face:
            return jsonify({"error": "Target Image में कोई इंसानी चेहरा नहीं मिला!"}), 422

        target_canvas = t_img.copy()
        swapped = swapper.get(target_canvas, target_face, source_face, paste_back=True)
        final_img = fit_frame(swapped, tw, th)

        _, buf = cv2.imencode('.jpg', final_img, [int(cv2.IMWRITE_JPEG_QUALITY), 96])
        return send_file(io.BytesIO(buf.tobytes()), mimetype='image/jpeg')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@server.route('/api/swap_video', methods=['POST'])
def swap_video_async():
    try:
        if 'video' not in request.files:
            return jsonify({"error": "वीडियो फ़ाइल प्राप्त नहीं हुई"}), 400

        job_id = str(uuid.uuid4())[:12]
        vid_file = request.files['video']
        in_vid = os.path.join(UPLOAD_DIR, f"{job_id}_input.mp4")
        vid_file.save(in_vid)

        m_path = None
        if 'm_face' in request.files:
            m_path = os.path.join(UPLOAD_DIR, f"{job_id}_m.jpg")
            request.files['m_face'].save(m_path)

        f_path = None
        if 'f_face' in request.files:
            f_path = os.path.join(UPLOAD_DIR, f"{job_id}_f.jpg")
            request.files['f_face'].save(f_path)

        ratio = request.form.get('ratio', '9:16')
        res = request.form.get('resolution', '720p HD')

        threading.Thread(
            target=execute_video_swap,
            args=(job_id, in_vid, m_path, f_path, ratio, res),
            daemon=True
        ).start()

        return jsonify({"job_id": job_id, "status": "queued"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@server.route('/api/job_status/<job_id>', methods=['GET'])
def get_status(job_id):
    info = JOBS.get(job_id)
    if not info:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(info), 200

@server.route('/api/job_download/<job_id>', methods=['GET'])
def download_result(job_id):
    info = JOBS.get(job_id)
    if not info or info.get('status') != 'completed':
        return jsonify({"error": "Result not ready"}), 400
    return send_file(info['file'], mimetype='video/mp4', as_attachment=True, download_name=f"kora_swap_{job_id}.mp4")

print("⏳ Ngrok टनल शुरू हो रही है...")
threading.Thread(target=lambda: server.run(host='0.0.0.0', port=5000), daemon=True).start()
time.sleep(2)

try: ngrok.kill()
except: pass

ngrok.set_auth_token(NGROK_TOKEN)
tunnel = ngrok.connect(5000, domain=FIXED_DOMAIN)
print("\n" + "="*60)
print(f"🎉 100% फुल वीडियो + इमेज सर्वर ऑनलाइन है: {tunnel.public_url}")
print("="*60 + "\n")

while True:
    time.sleep(60)
'''

ACTIVE_FONT = "Roboto"
try:
    if platform == 'android':
        sys_dir = "/system/fonts"
        if os.path.exists(sys_dir):
            for f in os.listdir(sys_dir):
                if any(x in f.lower() for x in ["devanagari", "hindi", "droidsansfallback"]):
                    LabelBase.register(name='KoraFont', fn_regular=os.path.join(sys_dir, f))
                    ACTIVE_FONT = 'KoraFont'
                    break
    elif platform == 'win':
        for wf in ["C:/Windows/Fonts/Nirmala.ttf", "C:/Windows/Fonts/mangal.ttf", "C:/Windows/Fonts/segoeui.ttf"]:
            if os.path.exists(wf):
                LabelBase.register(name='KoraFont', fn_regular=wf)
                ACTIVE_FONT = 'KoraFont'
                break
except Exception:
    ACTIVE_FONT = "Roboto"

KV = '''
<KoraHeaderBtn@Button>:
    background_normal: ''
    background_down: ''
    background_color: (0, 0, 0, 0)
    size_hint: (None, None)
    size: (dp(74), dp(32))
    bold: True
    font_size: '12sp'
    color: (0, 0, 0, 1) if self.state == 'down' else (0.0, 0.88, 1.0, 1)
    canvas.before:
        Color:
            rgba: (1, 1, 1, 1) if self.state == 'down' else (0.08, 0.10, 0.14, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(6)]
        Color:
            rgba: (1, 1, 1, 1) if self.state == 'down' else (0.0, 0.88, 1.0, 0.6)
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(6))
            width: dp(1.2)

<RefreshHeaderBtn@Button>:
    background_normal: ''
    background_down: ''
    background_color: (0, 0, 0, 0)
    size_hint: (None, None)
    size: (dp(82), dp(32))
    bold: True
    font_size: '11sp'
    color: (0, 0, 0, 1) if self.state == 'down' else (1.0, 0.65, 0.1, 1)
    canvas.before:
        Color:
            rgba: (1, 1, 1, 1) if self.state == 'down' else (0.08, 0.10, 0.14, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(6)]
        Color:
            rgba: (1, 1, 1, 1) if self.state == 'down' else (1.0, 0.65, 0.1, 0.7)
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(6))
            width: dp(1.2)

<StatusLED@ButtonBehavior+Widget>:
    is_online: False
    size_hint: (None, None)
    size: (dp(24), dp(24))
    canvas:
        Color:
            rgba: (0.0, 1.0, 0.45, 0.25) if self.is_online else (1.0, 0.25, 0.25, 0.25)
        Ellipse:
            pos: (self.center_x - dp(10), self.center_y - dp(10))
            size: (dp(20), dp(20))
        Color:
            rgba: (0.1, 1.0, 0.45, 1) if self.is_online else (1.0, 0.25, 0.25, 1)
        Ellipse:
            pos: (self.center_x - dp(5), self.center_y - dp(5))
            size: (dp(10), dp(10))

<NeonProgressCircle>:
    size_hint: (None, None)
    size: (dp(90), dp(90))
    canvas:
        Color:
            rgba: (1, 1, 1, 0.12)
        Line:
            circle: (self.center_x, self.center_y, dp(36))
            width: dp(4)
        Color:
            rgba: (0.0, 0.9, 1.0, 0.95)
        Line:
            circle: (self.center_x, self.center_y, dp(36), 0, min(360, root.progress * 3.6))
            width: dp(3.8)
            cap: 'round'

<UploadCard@ButtonBehavior+BoxLayout>:
    has_image: False
    orientation: 'vertical'
    padding: dp(6)
    canvas.before:
        Color:
            rgba: (0.04, 0.05, 0.07, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]
        Color:
            rgba: (0.0, 0.88, 1.0, 0.9) if self.has_image else (0.18, 0.22, 0.28, 0.6)
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(8))
            width: dp(1.4)

<ActionPillBtn@Button>:
    background_normal: ''
    background_down: ''
    background_color: (0, 0, 0, 0)
    bold: True
    canvas.before:
        Color:
            rgba: (0.0, 0.85, 0.45, 0.95) if self.state != 'down' else (1, 1, 1, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(6)]

<DownloadArrowBtn@Button>:
    background_normal: ''
    background_down: ''
    background_color: (0, 0, 0, 0)
    canvas.before:
        Color:
            rgba: (0.08, 0.10, 0.14, 0.9) if self.state != 'down' else (0.0, 0.88, 1.0, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(6)]
        Color:
            rgba: (0.35, 0.42, 0.52, 0.9)
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(6))
            width: dp(1.2)
    canvas.after:
        Color:
            rgba: (0.0, 0.95, 1.0, 1) if self.state != 'down' else (0, 0, 0, 1)
        Line:
            points: [self.center_x, self.top - dp(9), self.center_x, self.y + dp(12)]
            width: dp(2)
        Line:
            points: [self.center_x - dp(5), self.y + dp(16), self.center_x, self.y + dp(11), self.center_x + dp(5), self.y + dp(16)]
            width: dp(2)
            joint: 'round'
            cap: 'round'
        Line:
            points: [self.center_x - dp(6), self.y + dp(8), self.center_x + dp(6), self.y + dp(8)]
            width: dp(2)
            cap: 'round'

<ZoomableImageContainer@StencilView>:
    image_source: ''
    canvas.before:
        Color:
            rgba: (0.02, 0.03, 0.04, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]

    Scatter:
        id: scatter
        do_rotation: False
        do_translation: False
        do_scale: True
        scale_min: 1.0
        scale_max: 5.0
        size_hint: (None, None)
        size: root.size
        center: root.center
        auto_bring_to_front: False

        AsyncImage:
            id: main_img
            source: root.image_source
            size: scatter.size
            opacity: 1 if root.image_source else 0
            allow_stretch: True
            keep_ratio: True
            mipmap: True

<GalleryItem@ButtonBehavior+FloatLayout>:
    thumb_path: ''
    is_video: False
    size_hint_y: None
    height: dp(100)
    canvas.before:
        Color:
            rgba: (0.06, 0.08, 0.11, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(6)]
    AsyncImage:
        source: root.thumb_path
        size_hint: (1, 1)
        pos_hint: {'x': 0, 'y': 0}
        allow_stretch: True
        keep_ratio: False
    BoxLayout:
        size_hint: (1, None)
        height: dp(18)
        pos_hint: {'x': 0, 'y': 0}
        opacity: 1 if root.is_video else 0
        canvas.before:
            Color:
                rgba: (0, 0, 0, 0.7)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "▶ VIDEO"
            font_size: '9sp'
            bold: True
            color: (0.0, 1.0, 0.6, 1)

BoxLayout:
    orientation: 'vertical'

    # TOP HEADER
    BoxLayout:
        size_hint_y: None
        height: dp(52)
        padding: [dp(10), dp(8)]
        spacing: dp(8)
        canvas.before:
            Color:
                rgba: (0.03, 0.04, 0.06, 1)
            Rectangle:
                pos: self.pos
                size: self.size
            Color:
                rgba: (0.16, 0.20, 0.26, 1)
            Line:
                points: [self.x, self.y, self.right, self.y]
                width: dp(1.2)

        KoraHeaderBtn:
            text: "KORA"
            pos_hint: {'center_y': 0.5}
            on_release: app.toggle_sidebar()

        RefreshHeaderBtn:
            text: "REFRESH"
            pos_hint: {'center_y': 0.5}
            on_release: app.reset_all_screens()

        Label:
            id: status_label
            text: "[b]- Ready -[/b]"
            markup: True
            font_size: '13sp'
            color: (0.0, 0.88, 1.0, 1)

        StatusLED:
            id: led_indicator
            is_online: False
            pos_hint: {'center_y': 0.5}
            on_release: app.ping_server()

    # MAIN WORKSPACE
    BoxLayout:
        orientation: 'horizontal'

        # LEFT SIDEBAR
        BoxLayout:
            id: left_sidebar
            orientation: 'vertical'
            size_hint_x: None
            width: dp(190) if app.sidebar_open else 0
            opacity: 1 if app.sidebar_open else 0
            disabled: not app.sidebar_open
            padding: [dp(6), dp(8)]
            spacing: dp(4)
            canvas.before:
                Color:
                    rgba: (0.04, 0.05, 0.07, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: (0.16, 0.20, 0.26, 1)
                Line:
                    points: [self.right, self.y, self.right, self.top]
                    width: dp(1)

            ScrollView:
                do_scroll_x: False
                bar_width: 0
                BoxLayout:
                    id: menu_container
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(4)

            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: dp(34)
                padding: [dp(4), dp(2)]
                canvas.before:
                    Color:
                        rgba: (0.08, 0.10, 0.14, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(6)]
                Label:
                    text: "[color=71767b]ENGINE[/color] [b][color=00d2ff]PRO AUDIO v3[/color][/b]"
                    markup: True
                    font_size: '9.5sp'

        # RIGHT PLAYGROUND FEED
        BoxLayout:
            orientation: 'vertical'
            canvas.before:
                Color:
                    rgba: (0.02, 0.025, 0.035, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size

            # 1. FACESWAP TERMINAL
            BoxLayout:
                id: faceswap_header_box
                orientation: 'vertical'
                size_hint_y: None
                height: dp(150) if app.current_tool == 'FACESWAP' else 0
                opacity: 1 if app.current_tool == 'FACESWAP' else 0
                disabled: app.current_tool != 'FACESWAP'
                padding: [dp(10), dp(6)]
                spacing: dp(4)
                canvas.before:
                    Color:
                        rgba: (0.04, 0.05, 0.07, 1)
                    Rectangle:
                        pos: self.pos
                        size: self.size
                    Color:
                        rgba: (0.16, 0.20, 0.26, 0.8)
                    Line:
                        points: [self.x, self.y, self.right, self.y]
                        width: dp(1)

                BoxLayout:
                    orientation: 'horizontal'
                    spacing: dp(12)

                    BoxLayout:
                        orientation: 'vertical'
                        spacing: dp(4)
                        UploadCard:
                            has_image: bool(app.real_img_path)
                            on_release: app.open_media_selector('real', is_video=False)
                            FloatLayout:
                                AsyncImage:
                                    source: app.real_img_path
                                    opacity: 1 if app.real_img_path else 0
                                    allow_stretch: True
                                    keep_ratio: True
                                    mipmap: True
                                    pos_hint: {'x': 0, 'y': 0}
                                    size_hint: (1, 1)
                                Label:
                                    text: "🖼️ Tap to Select" if not app.real_img_path else ""
                                    font_size: '11sp'
                                    color: (0.6, 0.65, 0.75, 1)
                                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                        Label:
                            text: "[b]Target Image[/b]"
                            markup: True
                            font_size: '11sp'
                            color: (0.0, 0.88, 1.0, 1)
                            size_hint_y: None
                            height: dp(16)
                            halign: 'center'

                    BoxLayout:
                        orientation: 'vertical'
                        spacing: dp(4)
                        UploadCard:
                            has_image: bool(app.face_img_path)
                            on_release: app.open_media_selector('face', is_video=False)
                            FloatLayout:
                                AsyncImage:
                                    source: app.face_img_path
                                    opacity: 1 if app.face_img_path else 0
                                    allow_stretch: True
                                    keep_ratio: True
                                    mipmap: True
                                    pos_hint: {'x': 0, 'y': 0}
                                    size_hint: (1, 1)
                                Label:
                                    text: "👤 Tap to Select" if not app.face_img_path else ""
                                    font_size: '11sp'
                                    color: (0.6, 0.65, 0.75, 1)
                                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                        Label:
                            text: "[b]Face Image[/b]"
                            markup: True
                            font_size: '11sp'
                            color: (0.0, 0.88, 1.0, 1)
                            size_hint_y: None
                            height: dp(16)
                            halign: 'center'

            # 2. DEEPFAKE TERMINAL
            BoxLayout:
                id: deepfake_header_box
                orientation: 'vertical'
                size_hint_y: None
                height: dp(230) if app.current_tool == 'DEEPFAKE' else 0
                opacity: 1 if app.current_tool == 'DEEPFAKE' else 0
                disabled: app.current_tool != 'DEEPFAKE'
                padding: [dp(10), dp(6)]
                spacing: dp(6)
                canvas.before:
                    Color:
                        rgba: (0.04, 0.05, 0.07, 1)
                    Rectangle:
                        pos: self.pos
                        size: self.size
                    Color:
                        rgba: (0.16, 0.20, 0.26, 0.8)
                    Line:
                        points: [self.x, self.y, self.right, self.y]
                        width: dp(1)

                BoxLayout:
                    orientation: 'horizontal'
                    spacing: dp(12)
                    size_hint_y: 0.58

                    BoxLayout:
                        orientation: 'vertical'
                        spacing: dp(3)
                        UploadCard:
                            has_image: bool(app.deepfake_m_path)
                            on_release: app.open_media_selector('df_m', is_video=False)
                            FloatLayout:
                                AsyncImage:
                                    source: app.deepfake_m_path
                                    opacity: 1 if app.deepfake_m_path else 0
                                    allow_stretch: True
                                    keep_ratio: True
                                    mipmap: True
                                    pos_hint: {'x': 0, 'y': 0}
                                    size_hint: (1, 1)
                                Label:
                                    text: "👨 Select Male" if not app.deepfake_m_path else ""
                                    font_size: '10sp'
                                    color: (0.6, 0.65, 0.75, 1)
                                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                        Label:
                            text: "[b]M CHARACTOR (MALE)[/b]"
                            markup: True
                            font_size: '10sp'
                            color: (0.0, 0.88, 1.0, 1)
                            size_hint_y: None
                            height: dp(14)
                            halign: 'center'

                    BoxLayout:
                        orientation: 'vertical'
                        spacing: dp(3)
                        UploadCard:
                            has_image: bool(app.deepfake_f_path)
                            on_release: app.open_media_selector('df_f', is_video=False)
                            FloatLayout:
                                AsyncImage:
                                    source: app.deepfake_f_path
                                    opacity: 1 if app.deepfake_f_path else 0
                                    allow_stretch: True
                                    keep_ratio: True
                                    mipmap: True
                                    pos_hint: {'x': 0, 'y': 0}
                                    size_hint: (1, 1)
                                Label:
                                    text: "👩 Select Female" if not app.deepfake_f_path else ""
                                    font_size: '10sp'
                                    color: (0.6, 0.65, 0.75, 1)
                                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                        Label:
                            text: "[b]F CHARACTOR (FEMALE)[/b]"
                            markup: True
                            font_size: '10sp'
                            color: (1.0, 0.45, 0.78, 1)
                            size_hint_y: None
                            height: dp(14)
                            halign: 'center'

                # RAW VIDEO CONTAINER
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: 0.42
                    spacing: dp(2)
                    FloatLayout:
                        canvas.before:
                            Color:
                                rgba: (0.04, 0.05, 0.07, 1)
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(8)]
                            Color:
                                rgba: (0.0, 0.88, 1.0, 0.9) if app.deepfake_video_path else (0.18, 0.22, 0.28, 0.6)
                            Line:
                                rounded_rectangle: (self.x, self.y, self.width, self.height, dp(8))
                                width: dp(1.4)

                        AsyncImage:
                            source: app.deepfake_video_thumb
                            opacity: 1 if app.deepfake_video_thumb else 0
                            allow_stretch: True
                            keep_ratio: True
                            mipmap: True
                            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                            size_hint: (0.95, 0.95)

                        Button:
                            text: "📹 Tap to select Raw Video"
                            font_size: '11sp'
                            bold: True
                            color: (0.5, 0.55, 0.65, 1)
                            background_normal: ''
                            background_color: (0, 0, 0, 0)
                            pos_hint: {'x': 0, 'y': 0}
                            size_hint: (1, 1)
                            opacity: 0 if app.deepfake_video_path else 1
                            disabled: bool(app.deepfake_video_path)
                            on_release: app.open_media_selector('df_video', is_video=True)

                        Button:
                            text: "▶ PLAY"
                            bold: True
                            font_size: '11sp'
                            color: (1, 1, 1, 1)
                            background_normal: ''
                            background_color: (0.0, 0.78, 0.45, 0.92)
                            size_hint: (None, None)
                            size: (dp(74), dp(28))
                            pos_hint: {'center_x': 0.35, 'center_y': 0.5}
                            opacity: 1 if app.deepfake_video_path else 0
                            disabled: not bool(app.deepfake_video_path)
                            on_release: app.play_video(app.deepfake_video_path)

                        Button:
                            text: "📁 Change"
                            bold: True
                            font_size: '10.5sp'
                            color: (1, 1, 1, 1)
                            background_normal: ''
                            background_color: (0.12, 0.48, 0.88, 0.92)
                            size_hint: (None, None)
                            size: (dp(74), dp(28))
                            pos_hint: {'center_x': 0.65, 'center_y': 0.5}
                            opacity: 1 if app.deepfake_video_path else 0
                            disabled: not bool(app.deepfake_video_path)
                            on_release: app.open_media_selector('df_video', is_video=True)

                    Label:
                        text: "[b]RAW VIDEO[/b]" + (f" [color=00d2ff]({app.selected_ratio})[/color]" if app.deepfake_video_path else "")
                        markup: True
                        font_size: '10sp'
                        color: (0.0, 1.0, 0.6, 1)
                        size_hint_y: None
                        height: dp(14)
                        halign: 'center'

            # 3. PLAYGROUND VIEWPORT
            BoxLayout:
                orientation: 'vertical'
                padding: [dp(10), dp(6)]
                spacing: dp(6)

                BoxLayout:
                    size_hint_y: None
                    height: dp(36)
                    orientation: 'vertical'
                    spacing: dp(2)
                    Label:
                        text: "[b][color=ffffff]PLAY[/color] [color=00d2ff]Ground[/color][/b]"
                        markup: True
                        font_size: '17sp'
                    Label:
                        text: ('Tool: ' + app.current_tool) + ' • Ratio: ' + app.selected_ratio + ' • Res: ' + app.selected_resolution
                        font_size: '10sp'
                        color: (0.0, 0.88, 1.0, 0.85)

                BoxLayout:
                    orientation: 'vertical'
                    padding: dp(8)
                    spacing: dp(6)
                    canvas.before:
                        Color:
                            rgba: (0.03, 0.04, 0.06, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(10)]
                        Color:
                            rgba: (0.85, 0.2, 0.2, 1) if app.is_error else ((0.0, 0.88, 1.0, 0.85) if (app.active_display_image or app.active_display_video) else ((1, 1, 1, 0.7) if app.is_loading else (0.16, 0.20, 0.26, 0.8)))
                        Line:
                            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(10))
                            width: dp(1.5)

                    BoxLayout:
                        size_hint_y: None
                        height: dp(18)
                        Label:
                            text: '[b]KORA RESULT[/b]'
                            markup: True
                            font_size: '10sp'
                            color: (0.0, 0.88, 1.0, 1) if not app.is_error else (1, 0.35, 0.35, 1)
                            halign: 'left'
                            text_size: self.size
                        Label:
                            text: app.selected_ratio + ' • ' + app.selected_resolution
                            font_size: '10sp'
                            bold: True
                            color: (0.0, 1.0, 0.5, 1) if (app.active_display_image or app.active_display_video) else (0.45, 0.52, 0.62, 1)
                            halign: 'right'
                            text_size: self.size

                    FloatLayout:
                        ZoomableImageContainer:
                            id: zoom_container
                            image_source: app.active_display_image
                            pos_hint: {'x': 0, 'y': 0}
                            size_hint: (1, 1)

                        BoxLayout:
                            orientation: 'vertical'
                            opacity: 1 if app.is_loading else 0
                            disabled: not app.is_loading
                            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                            size_hint: (None, None)
                            size: (dp(130), dp(130))
                            spacing: dp(8)

                            FloatLayout:
                                size_hint: (None, None)
                                size: (dp(90), dp(90))
                                pos_hint: {'center_x': 0.5}

                                NeonProgressCircle:
                                    progress: app.progress_val
                                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                                Label:
                                    text: str(int(app.progress_val)) + "%"
                                    font_size: '15sp'
                                    bold: True
                                    color: (1, 1, 1, 1)
                                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                            Label:
                                text: app.server_task_msg
                                font_size: '11sp'
                                color: (0.9, 0.95, 1, 0.9)
                                halign: 'center'
                                size_hint_y: None
                                height: dp(18)

                        Label:
                            text: app.status_msg
                            opacity: 0 if (app.active_display_image or app.active_display_video or app.is_loading) else 1
                            font_name: app.hindi_font_name
                            halign: 'center'
                            valign: 'middle'
                            font_size: '12sp'
                            color: (1.0, 0.45, 0.45, 1) if app.is_error else (0.5, 0.55, 0.65, 1)
                            text_size: self.width - dp(24), None
                            size_hint: (1, 1)
                            pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                        Button:
                            text: "▶ Play Video"
                            bold: True
                            font_size: '11sp'
                            size_hint: (None, None)
                            size: (dp(95), dp(34))
                            pos_hint: {'center_x': 0.5, 'y': 0.04}
                            opacity: 1 if (app.current_tool == 'DEEPFAKE' and app.active_display_video) else 0
                            disabled: not bool(app.current_tool == 'DEEPFAKE' and app.active_display_video)
                            background_normal: ''
                            background_color: (0.0, 0.85, 0.45, 0.92)
                            color: (1, 1, 1, 1)
                            on_release: app.play_video(app.active_display_video)

                        DownloadArrowBtn:
                            opacity: 1 if (app.active_display_image or app.active_display_video) else 0
                            disabled: not bool(app.active_display_image or app.active_display_video)
                            size_hint: (None, None)
                            size: (dp(34), dp(34))
                            pos_hint: {'right': 0.96, 'y': 0.04}
                            on_release: app.save_final_result()

            # 4. BOTTOM ACTION BAR
            BoxLayout:
                id: bottom_bar
                size_hint_y: None
                height: dp(58) if app.current_tool in ('FACESWAP', 'DEEPFAKE') else 0
                opacity: 1 if app.current_tool in ('FACESWAP', 'DEEPFAKE') else 0
                disabled: app.current_tool not in ('FACESWAP', 'DEEPFAKE')
                padding: [dp(10), dp(6)]
                canvas.before:
                    Color:
                        rgba: (0.03, 0.04, 0.05, 1)
                    Rectangle:
                        pos: self.pos
                        size: self.size

                ActionPillBtn:
                    text: ("⚡ GENERATE HD DEEPFAKE (AUDIO PRESERVED)" if app.current_tool == 'DEEPFAKE' else "⚡ GENERATE 4K FACESWAP")
                    size_hint: (1, None)
                    height: dp(42)
                    font_size: '12sp'
                    pos_hint: {'center_y': 0.5}
                    on_release: app.generate()
'''

class NeonProgressCircle(Widget):
    progress = NumericProperty(0)

class ZoomableImageContainer(StencilView):
    image_source = StringProperty('')

class GalleryItem(ButtonBehavior, FloatLayout):
    thumb_path = StringProperty('')
    is_video = BooleanProperty(False)

class KoraApp(App):
    current_tool = StringProperty("HOME")
    sidebar_open = BooleanProperty(False)
    colab_open = BooleanProperty(True)
    setting_open = BooleanProperty(False)

    selected_ratio = StringProperty("9:16")
    selected_resolution = StringProperty("1080p FHD")
    colab_url = StringProperty("https://unpack-stick-robe.ngrok-free.dev")

    # Inputs - FaceSwap
    real_img_path = StringProperty("")
    face_img_path = StringProperty("")

    # Inputs - Deepfake
    deepfake_m_path = StringProperty("")
    deepfake_f_path = StringProperty("")
    deepfake_video_path = StringProperty("")
    deepfake_video_thumb = StringProperty("")

    # Tool-Specific Isolated Results (स्क्रीन अलग-अलग रखने के लिए)
    faceswap_result_img = StringProperty("")
    deepfake_result_vid = StringProperty("")
    deepfake_result_thumb = StringProperty("")

    # Active Viewport Properties
    active_display_image = StringProperty("")
    active_display_video = StringProperty("")

    is_loading = BooleanProperty(False)
    is_error = BooleanProperty(False)
    progress_val = NumericProperty(0)
    server_task_msg = StringProperty("Initializing AI Job...")
    status_msg = StringProperty("प्लेग्राउंड तैयार है - टूल चुनें")

    hindi_font_name = StringProperty(ACTIVE_FONT)
    gallery_pop = None

    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        os.makedirs(self.user_data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.user_data_dir, "v_thumbs"), exist_ok=True)
        os.makedirs(os.path.join(self.user_data_dir, "uploads"), exist_ok=True)

        self.request_android_permissions()
        self.render_sidebar()
        Clock.schedule_once(lambda dt: self.ping_server(), 1.0)

    def request_android_permissions(self, callback=None):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                perms = [
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    "android.permission.READ_MEDIA_IMAGES",
                    "android.permission.READ_MEDIA_VIDEO"
                ]
                request_permissions(perms, callback=callback if callback else lambda p, g: None)
            except Exception:
                if callback: callback([], [])

    # ================= REFRESH BUTTON (ALL SCREENS RESET) =================
    def reset_all_screens(self):
        """हेडर के REFRESH बटन से सारी स्क्रीन खाली करना"""
        self.real_img_path = ""
        self.face_img_path = ""
        self.deepfake_m_path = ""
        self.deepfake_f_path = ""
        self.deepfake_video_path = ""
        self.deepfake_video_thumb = ""

        self.faceswap_result_img = ""
        self.deepfake_result_vid = ""
        self.deepfake_result_thumb = ""

        self.active_display_image = ""
        self.active_display_video = ""

        self.is_loading = False
        self.is_error = False
        self.progress_val = 0
        self.server_task_msg = "Ready"
        self.status_msg = "प्लेग्राउंड रीसेट हो गया है - नया काम शुरू करें"

        try:
            sc = self.root.ids.zoom_container.ids.scatter
            sc.scale = 1.0
            sc.center = self.root.ids.zoom_container.center
        except Exception:
            pass

        self.toast("All Screens Refreshed!")

    def toggle_sidebar(self):
        sb = self.root.ids.left_sidebar
        self.sidebar_open = not self.sidebar_open
        Animation(width=dp(190) if self.sidebar_open else 0, opacity=1.0 if self.sidebar_open else 0.0, d=0.18).start(sb)

    def ping_server(self):
        def _worker():
            url = f"{self.colab_url.rstrip('/')}/api/health"
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request(url, headers={'User-Agent': 'KoraApp/3.1', 'ngrok-skip-browser-warning': '1'})
                with urllib.request.urlopen(req, timeout=5, context=ctx) as r:
                    if r.status == 200:
                        Clock.schedule_once(lambda dt: self._set_online(True), 0)
                        return
            except Exception:
                pass
            Clock.schedule_once(lambda dt: self._set_online(False), 0)

        threading.Thread(target=_worker, daemon=True).start()

    def _set_online(self, state):
        led = self.root.ids.led_indicator
        lbl = self.root.ids.status_label
        led.is_online = state
        lbl.text = "[b]- Online -[/b]" if state else "[b]- Offline -[/b]"
        lbl.color = (0, 1, 0.45, 1) if state else (1, 0.35, 0.35, 1)

    def render_sidebar(self):
        container = self.root.ids.menu_container
        container.clear_widgets()

        tools = ["COLAB SETUP", "FACESWAP", "DEEPFAKE", "SETTING"]

        for tool in tools:
            is_active = (self.current_tool == tool)
            btn = Button(
                text=f"•  {tool}",
                size_hint_y=None,
                height=dp(38),
                background_normal='',
                background_down='',
                background_color=(0.14, 0.20, 0.28, 1) if is_active else (0.07, 0.09, 0.12, 1),
                color=(0, 0.88, 1, 1) if is_active else (0.8, 0.85, 0.95, 1),
                bold=True,
                font_size='11sp',
                halign='left',
                valign='middle'
            )
            btn.bind(size=lambda s, w: setattr(s, 'text_size', (s.width - dp(10), None)))
            btn.bind(on_release=lambda x, t=tool: self.click_tool(t))
            container.add_widget(btn)

            if tool == "COLAB SETUP" and self.colab_open:
                c_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(165), spacing=dp(5), padding=[dp(4), dp(6), dp(4), dp(4)])

                b0 = Button(text="STEP 1: Open Google Colab", size_hint_y=None, height=dp(30), background_normal='', background_color=(0.85, 0.45, 0.05, 1), color=(1,1,1,1), bold=True, font_size='9.5sp')
                b0.bind(on_release=lambda x: webbrowser.open("https://colab.research.google.com/#create=true"))

                b1 = Button(text="STEP 2: Copy Server Code", size_hint_y=None, height=dp(30), background_normal='', background_color=(0.12, 0.45, 0.85, 1), color=(1,1,1,1), bold=True, font_size='9.5sp')
                b1.bind(on_release=lambda x: (Clipboard.copy(COLAB_SERVER_CODE), self.toast("T4 Server कोड कॉपी हुआ!")))

                url_inp = TextInput(text=self.colab_url, hint_text="Domain...", foreground_color=(0, 1, 0.45, 1), background_color=(0.02, 0.03, 0.05, 1), size_hint_y=None, height=dp(30), font_size='9sp', multiline=False)
                url_inp.bind(text=lambda ins, val: setattr(self, 'colab_url', val))

                b3 = Button(text="Connect GPU Server", size_hint_y=None, height=dp(30), background_normal='', background_color=(0.10, 0.65, 0.40, 1), color=(1,1,1,1), bold=True, font_size='9.5sp')
                b3.bind(on_release=lambda x: self.ping_server())

                c_box.add_widget(b0); c_box.add_widget(b1); c_box.add_widget(url_inp); c_box.add_widget(b3)
                container.add_widget(c_box)

            if tool == "SETTING" and self.setting_open:
                s_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(85), spacing=dp(5), padding=[dp(4), dp(6), dp(4), dp(4)])

                sb1 = Button(text=f"Ratio: {self.selected_ratio}", size_hint_y=None, height=dp(34), background_normal='', background_color=(0.12, 0.16, 0.22, 1), color=(0, 0.88, 1, 1), bold=True, font_size='10sp')
                sb1.bind(on_release=lambda x: self.pop_picker("Select Aspect Ratio", ["16:9 (Landscape)", "9:16 (Vertical)", "1:1 (Square)", "4:5 (Insta)", "3:4 (Portrait)"], self.set_r))

                sb2 = Button(text=f"Res: {self.selected_resolution}", size_hint_y=None, height=dp(34), background_normal='', background_color=(0.12, 0.16, 0.22, 1), color=(0, 0.88, 1, 1), bold=True, font_size='10sp')
                sb2.bind(on_release=lambda x: self.pop_picker("Select Resolution", ["4K Ultra HD", "2K QHD", "1080p FHD", "720p HD"], self.set_res))

                s_box.add_widget(sb1); s_box.add_widget(sb2)
                container.add_widget(s_box)

    def click_tool(self, tool_name):
        self.current_tool = tool_name
        if tool_name == "COLAB SETUP":
            self.colab_open = not self.colab_open
            self.setting_open = False
        elif tool_name == "SETTING":
            self.setting_open = not self.setting_open
            self.colab_open = False
        else:
            self.setting_open = False
            self.colab_open = False

        self._sync_viewport_for_tool(tool_name)
        self.render_sidebar()

    def _sync_viewport_for_tool(self, tool_name):
        """जब टूल बदला जाए तो स्क्रीन मिक्स न हो"""
        if tool_name == 'FACESWAP':
            self.active_display_image = self.faceswap_result_img
            self.active_display_video = ""
            self.status_msg = "🎉 4K FaceSwap तैयार है!" if self.faceswap_result_img else "Target और Face Image चुनें"
        elif tool_name == 'DEEPFAKE':
            self.active_display_image = self.deepfake_result_thumb
            self.active_display_video = self.deepfake_result_vid
            self.status_msg = "🎉 10s HD Deepfake तैयार है (Audio Preserved)!" if self.deepfake_result_vid else "Raw Video और Character Face चुनें"
        else:
            self.active_display_image = ""
            self.active_display_video = ""
            self.status_msg = "प्लेग्राउंड तैयार है - टूल चुनें"

    def set_r(self, v):
        self.selected_ratio = v.split()[0]
        self.render_sidebar()
        self.toast(f"Ratio: {self.selected_ratio}")

    def set_res(self, v):
        self.selected_resolution = v
        self.render_sidebar()
        self.toast(f"Resolution: {self.selected_resolution}")

    def pop_picker(self, title, items, callback):
        box = BoxLayout(orientation='vertical', spacing=dp(6), padding=dp(8))
        pop = Popup(title=title, content=box, size_hint=(0.85, 0.48), title_color=(0, 0.88, 1, 1))
        for item in items:
            b = Button(text=item, size_hint_y=None, height=dp(36), background_normal='', background_color=(0.12, 0.16, 0.22, 1), color=(1, 1, 1, 1), bold=True, font_size='11sp')
            def _bind_click(val=item):
                callback(val)
                pop.dismiss()
            b.bind(on_release=lambda btn, val=item: _bind_click(val))
            box.add_widget(b)
        pop.open()

    # ================= WORKING GALLERY FORMULA =================
    def get_video_thumbnail(self, v_path):
        try:
            cache_dir = os.path.join(self.user_data_dir, "v_thumbs")
            os.makedirs(cache_dir, exist_ok=True)
            thumb_path = os.path.join(cache_dir, f"t_{abs(hash(v_path))}.jpg")
            if os.path.exists(thumb_path):
                return thumb_path

            if platform == 'android':
                try:
                    from jnius import autoclass
                    ThumbnailUtils = autoclass('android.media.ThumbnailUtils')
                    MediaStoreVideoThumbnails = autoclass('android.provider.MediaStore$Video$Thumbnails')
                    CompressFormat = autoclass('android.graphics.Bitmap$CompressFormat')
                    FileOutputStream = autoclass('java.io.FileOutputStream')

                    bm = ThumbnailUtils.createVideoThumbnail(v_path, MediaStoreVideoThumbnails.MINI_KIND)
                    if bm:
                        fos = FileOutputStream(thumb_path)
                        bm.compress(CompressFormat.JPEG, 75, fos)
                        fos.close()
                        return thumb_path
                except Exception:
                    pass

            try:
                import cv2
                cap = cv2.VideoCapture(v_path)
                ret, frame = cap.read()
                cap.release()
                if ret and frame is not None:
                    cv2.imwrite(thumb_path, frame)
                    return thumb_path
            except Exception:
                pass
        except Exception:
            pass
        return ""

    def open_system_gallery_intent(self, is_video, custom_callback):
        if platform == 'android':
            try:
                from android import activity
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')

                intent = Intent(Intent.ACTION_GET_CONTENT)
                intent.setType("video/*" if is_video else "image/*")

                def on_activity_result(request_code, result_code, data):
                    if request_code == 2002 and result_code == -1 and data:
                        try:
                            uri = data.getData()
                            copied = self.copy_android_uri(uri, is_video)
                            target_p = copied if copied else str(uri.getPath())
                            if custom_callback:
                                Clock.schedule_once(lambda dt: custom_callback(target_p), 0)
                        except Exception:
                            pass
                    activity.unbind(on_activity_result=on_activity_result)

                activity.bind(on_activity_result=on_activity_result)
                PythonActivity.mActivity.startActivityForResult(intent, 2002)
                return True
            except Exception:
                pass
        elif platform == 'win':
            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                types = [("Video Files", "*.mp4;*.mkv;*.mov;*.avi;*.webm")] if is_video else [("Image Files", "*.jpg;*.jpeg;*.png;*.webp")]
                path = filedialog.askopenfilename(parent=root, title="Select File", filetypes=types)
                root.destroy()
                if path and os.path.exists(path) and custom_callback:
                    Clock.schedule_once(lambda dt: custom_callback(path), 0)
                    return True
            except Exception:
                pass
        return False

    def copy_android_uri(self, uri, is_video):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            cr = PythonActivity.mActivity.getContentResolver()
            in_stream = cr.openInputStream(uri)
            if in_stream:
                ext = ".mp4" if is_video else ".jpg"
                out_path = os.path.join(self.user_data_dir, "uploads", f"media_{int(time.time()*1000)}{ext}")
                FileOutputStream = autoclass('java.io.FileOutputStream')
                out_stream = FileOutputStream(out_path)
                Byte = autoclass('java.lang.Byte')
                Array = autoclass('java.lang.reflect.Array')
                buf = Array.newInstance(Byte.TYPE, 65536)
                while True:
                    read_n = in_stream.read(buf)
                    if read_n <= 0: break
                    out_stream.write(buf, 0, read_n)
                out_stream.flush()
                out_stream.close()
                in_stream.close()
                return out_path
        except Exception:
            pass
        return None

    def open_media_selector(self, key_type, is_video=False):
        self.open_all_phone_media(
            is_video=is_video,
            custom_callback=lambda p: self._on_file_selected(key_type, p, is_video)
        )

    def open_all_phone_media(self, custom_callback=None, is_video=False):
        self.request_android_permissions()

        valid_exts = ('.mp4', '.mkv', '.mov', '.avi', '.webm', '.3gp') if is_video else ('.jpg', '.jpeg', '.png', '.webp', '.bmp')

        if platform == 'android':
            base_search_paths = [
                "/storage/emulated/0/DCIM",
                "/storage/emulated/0/Pictures",
                "/storage/emulated/0/Download",
                "/storage/emulated/0/Downloads",
                "/storage/emulated/0/Movies",
                "/storage/emulated/0/Video",
                "/storage/emulated/0/Videos",
                "/storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images",
                "/storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Video",
                "/storage/emulated/0/WhatsApp/Media/WhatsApp Images",
                "/storage/emulated/0/WhatsApp/Media/WhatsApp Video"
            ]
        else:
            home = os.path.expanduser('~')
            base_search_paths = [
                os.path.join(home, 'Pictures'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Videos'),
                os.path.join(home, 'Desktop')
            ]

        all_files = []
        albums = {"All": []}

        for root_p in base_search_paths:
            if os.path.exists(root_p):
                try:
                    for root, dirs, files in os.walk(root_p):
                        folder_name = os.path.basename(root)
                        for f in files:
                            if f.lower().endswith(valid_exts):
                                full_p = os.path.join(root, f)
                                all_files.append(full_p)
                                if folder_name not in albums:
                                    albums[folder_name] = []
                                albums[folder_name].append(full_p)
                        if len(all_files) >= 300:
                            break
                except Exception:
                    pass

        all_files = list(dict.fromkeys(all_files))
        all_files.sort(key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)
        albums["All"] = all_files
        albums = {k: v for k, v in albums.items() if len(v) > 0}

        main_box = BoxLayout(orientation='vertical', spacing=dp(6), padding=dp(8))

        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(36), spacing=dp(6))
        sys_gal_btn = Button(
            text="📂 Open Device Gallery",
            size_hint_x=None,
            width=dp(150),
            background_normal='',
            background_color=(0.12, 0.45, 0.85, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size='10sp'
        )
        def on_sys_gal(x):
            if self.open_system_gallery_intent(is_video, custom_callback):
                if self.gallery_pop:
                    self.gallery_pop.dismiss()
        sys_gal_btn.bind(on_release=on_sys_gal)
        top_bar.add_widget(sys_gal_btn)

        tabs_scroll = ScrollView(size_hint_y=None, height=dp(36), do_scroll_y=False)
        tabs = BoxLayout(size_hint_x=None, spacing=dp(6))
        tabs.bind(minimum_width=tabs.setter('width'))
        tabs_scroll.add_widget(tabs)
        top_bar.add_widget(tabs_scroll)
        main_box.add_widget(top_bar)

        grid = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, row_default_height=dp(100), row_force_default=True)
        grid.bind(minimum_height=grid.setter('height'))
        scroll = ScrollView(do_scroll_x=False)
        scroll.add_widget(grid)

        def load_folder_items(file_list):
            grid.clear_widgets()
            if not file_list:
                grid.add_widget(Label(text="No files found", font_size='11sp', color=(0.5, 0.55, 0.65, 1)))
                return

            for fpath in file_list[:90]:
                thumb_to_show = self.get_video_thumbnail(fpath) if is_video else fpath
                item = GalleryItem(thumb_path=thumb_to_show, is_video=is_video)
                def on_pick(ins, p=fpath):
                    if custom_callback:
                        custom_callback(p)
                    if self.gallery_pop:
                        self.gallery_pop.dismiss()
                item.bind(on_release=on_pick)
                grid.add_widget(item)

        for folder_title, path_list in albums.items():
            t_btn = Button(
                text=f"{folder_title} ({len(path_list)})", 
                size_hint_x=None, 
                width=dp(110), 
                font_size='10sp', 
                background_normal='', 
                background_color=(0.10, 0.14, 0.20, 1), 
                color=(0.0, 0.85, 1.0, 1), 
                bold=True
            )
            t_btn.bind(on_release=lambda x, pl=path_list: load_folder_items(pl))
            tabs.add_widget(t_btn)

        main_box.add_widget(scroll)

        c_btn = Button(text="Cancel", size_hint_y=None, height=dp(34), background_normal='', background_color=(0.18, 0.22, 0.28, 1), bold=True)
        c_btn.bind(on_release=lambda x: self.gallery_pop.dismiss())
        main_box.add_widget(c_btn)

        load_folder_items(albums.get("All", []))
        self.gallery_pop = Popup(title="Select Media", content=main_box, size_hint=(0.95, 0.88), title_color=(0, 0.88, 1, 1))
        self.gallery_pop.open()

    def _on_file_selected(self, key, path, is_video):
        if not path or not os.path.exists(path):
            self.toast("फ़ाइल नहीं मिली!")
            return

        if key == 'real':
            self.real_img_path = path
            self.toast("Target Image Selected!")
        elif key == 'face':
            self.face_img_path = path
            self.toast("Face Image Selected!")
        elif key == 'df_m':
            self.deepfake_m_path = path
            self.toast("Male Face Selected!")
        elif key == 'df_f':
            self.deepfake_f_path = path
            self.toast("Female Face Selected!")
        elif key == 'df_video':
            self.deepfake_video_path = path
            self.deepfake_video_thumb = self.get_video_thumbnail(path)
            self.detect_video_aspect(path)
            self.toast("Raw Video Selected!")

    def detect_video_aspect(self, path):
        w, h, rot = 0, 0, 0
        if platform == 'android':
            try:
                from jnius import autoclass
                retriever = autoclass('android.media.MediaMetadataRetriever')()
                retriever.setDataSource(path)
                w_s = retriever.extractMetadata(18)
                h_s = retriever.extractMetadata(19)
                r_s = retriever.extractMetadata(24)
                if w_s and h_s: w, h = int(w_s), int(h_s)
                if r_s: rot = int(r_s)
                retriever.release()
            except Exception: pass

        if w == 0 or h == 0:
            try:
                import cv2
                cap = cv2.VideoCapture(path)
                if cap.isOpened():
                    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    cap.release()
            except Exception: pass

        if rot in (90, 270):
            w, h = h, w

        if w > 0 and h > 0:
            aspect = w / float(h)
            if aspect <= 0.65:
                self.selected_ratio = "9:16"
            elif aspect <= 0.88:
                self.selected_ratio = "4:5"
            elif aspect <= 1.25:
                self.selected_ratio = "1:1"
            else:
                self.selected_ratio = "16:9"
            self.toast(f"Ratio Detected: {self.selected_ratio}")
            self.render_sidebar()

    def play_video(self, v_path):
        if not v_path or not os.path.exists(v_path):
            self.toast("Video not found!")
            return
        if platform == 'android':
            try:
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                File = autoclass('java.io.File')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                StrictMode = autoclass('android.os.StrictMode')
                builder = autoclass('android.os.StrictMode$VmPolicy$Builder')()
                StrictMode.setVmPolicy(builder.build())
                intent = Intent(Intent.ACTION_VIEW)
                intent.setDataAndType(Uri.fromFile(File(v_path)), "video/*")
                PythonActivity.mActivity.startActivity(intent)
                return
            except Exception:
                self.toast("Playback error")
        elif platform == 'win':
            try:
                os.startfile(v_path)
            except Exception:
                pass
        else:
            try:
                import subprocess
                subprocess.Popen(['xdg-open', v_path])
            except Exception:
                pass

    # ================= SAFE IMAGE CONVERTER =================
    def _read_image_clean(self, path):
        """Converts image to clean RGB JPEG bytes to prevent crash on phone/PC"""
        if HAS_PIL:
            try:
                im = Image.open(path)
                if im.mode != 'RGB':
                    im = im.convert('RGB')
                im.thumbnail((1920, 1920), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                im.save(buf, format='JPEG', quality=95)
                return buf.getvalue()
            except Exception:
                pass
        with open(path, 'rb') as f:
            return f.read()

    # ================= PIPELINE GENERATOR =================
    def generate(self):
        if self.current_tool == 'FACESWAP':
            if not self.real_img_path or not self.face_img_path:
                self.toast("Target Image और Face Image दोनों चुनें!")
                return
            self._start_progress_state("Processing 4K Neural FaceSwap...")
            threading.Thread(target=self._run_image_pipeline, daemon=True).start()

        elif self.current_tool == 'DEEPFAKE':
            if not self.deepfake_video_path:
                self.toast("कृपया RAW VIDEO चुनें!")
                return
            if not self.deepfake_m_path and not self.deepfake_f_path:
                self.toast("कम से कम एक Face (M या F) चुनें!")
                return
            self._start_progress_state("Uploading Video & Audio Stream...")
            threading.Thread(target=self._run_video_pipeline, daemon=True).start()

    def _start_progress_state(self, msg):
        self.is_loading = True
        self.is_error = False
        self.progress_val = 10
        self.server_task_msg = msg

    def _run_image_pipeline(self):
        try:
            url = f"{self.colab_url.rstrip('/')}/api/swap_image"
            boundary = f"----KoraForm{int(time.time())}"
            body = bytearray()

            def add_text_field(name, val):
                body.extend(f'--{boundary}\r\n'.encode('utf-8'))
                body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode('utf-8'))
                body.extend(f'{val}\r\n'.encode('utf-8'))

            def add_file_field(name, filename, data_bytes):
                body.extend(f'--{boundary}\r\n'.encode('utf-8'))
                body.extend(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode('utf-8'))
                body.extend(f'Content-Type: image/jpeg\r\n\r\n'.encode('utf-8'))
                body.extend(data_bytes)
                body.extend(b'\r\n')

            add_text_field('ratio', self.selected_ratio)
            add_text_field('resolution', self.selected_resolution)
            add_file_field('source', 'source.jpg', self._read_image_clean(self.face_img_path))
            add_file_field('target', 'target.jpg', self._read_image_clean(self.real_img_path))
            body.extend(f'--{boundary}--\r\n'.encode('utf-8'))

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            req = urllib.request.Request(url, data=bytes(body), headers={
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'User-Agent': 'KoraApp/3.1',
                'ngrok-skip-browser-warning': '1'
            })

            Clock.schedule_once(lambda dt: setattr(self, 'progress_val', 45), 0)

            with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
                data = resp.read()

            save_file = os.path.join(self.user_data_dir, f"swap_{int(time.time())}.jpg")
            with open(save_file, "wb") as f:
                f.write(data)

            Clock.schedule_once(lambda dt, p=save_file: self._on_pipeline_success(p, is_video=False), 0)

        except urllib.error.HTTPError as he:
            err_msg = f"HTTP Error {he.code}"
            try:
                err_body = json.loads(he.read().decode('utf-8'))
                err_msg = err_body.get('error', err_msg)
            except Exception:
                pass
            Clock.schedule_once(lambda dt, m=err_msg: self._on_pipeline_failure(m), 0)
        except urllib.error.URLError:
            Clock.schedule_once(lambda dt, m="सर्वर से संपर्क नहीं हो सका। Colab चेक करें": self._on_pipeline_failure(m), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt, m=str(e): self._on_pipeline_failure(m), 0)

    def _run_video_pipeline(self):
        try:
            url = f"{self.colab_url.rstrip('/')}/api/swap_video"
            boundary = f"----KoraForm{int(time.time())}"
            body = bytearray()

            def add_text_field(name, val):
                body.extend(f'--{boundary}\r\n'.encode('utf-8'))
                body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode('utf-8'))
                body.extend(f'{val}\r\n'.encode('utf-8'))

            def add_file_bytes(name, filename, data_bytes, ctype):
                body.extend(f'--{boundary}\r\n'.encode('utf-8'))
                body.extend(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode('utf-8'))
                body.extend(f'Content-Type: {ctype}\r\n\r\n'.encode('utf-8'))
                body.extend(data_bytes)
                body.extend(b'\r\n')

            add_text_field('ratio', self.selected_ratio)
            add_text_field('resolution', self.selected_resolution)

            with open(self.deepfake_video_path, 'rb') as vf:
                add_file_bytes('video', os.path.basename(self.deepfake_video_path), vf.read(), 'video/mp4')

            if self.deepfake_m_path:
                add_file_bytes('m_face', 'm_face.jpg', self._read_image_clean(self.deepfake_m_path), 'image/jpeg')
            if self.deepfake_f_path:
                add_file_bytes('f_face', 'f_face.jpg', self._read_image_clean(self.deepfake_f_path), 'image/jpeg')

            body.extend(f'--{boundary}--\r\n'.encode('utf-8'))

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            req = urllib.request.Request(url, data=bytes(body), headers={
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'User-Agent': 'KoraApp/3.1',
                'ngrok-skip-browser-warning': '1'
            })

            with urllib.request.urlopen(req, timeout=180, context=ctx) as resp:
                resp_data = json.loads(resp.read().decode('utf-8'))
                job_id = resp_data.get('job_id')

            if not job_id:
                raise Exception("Failed to queue job on server")

            Clock.schedule_once(lambda dt: setattr(self, 'server_task_msg', "Rendering Frames on T4 GPU..."), 0)

            while True:
                time.sleep(1.2)
                st_url = f"{self.colab_url.rstrip('/')}/api/job_status/{job_id}"
                st_req = urllib.request.Request(st_url, headers={'User-Agent': 'KoraApp/3.1', 'ngrok-skip-browser-warning': '1'})
                with urllib.request.urlopen(st_req, timeout=15, context=ctx) as s_resp:
                    st_json = json.loads(s_resp.read().decode('utf-8'))
                    prog = st_json.get('progress', 0)
                    status = st_json.get('status')
                    Clock.schedule_once(lambda dt, p=prog: setattr(self, 'progress_val', p), 0)

                    if status == 'completed':
                        Clock.schedule_once(lambda dt: setattr(self, 'server_task_msg', "Downloading Final HD Video..."), 0)
                        down_url = f"{self.colab_url.rstrip('/')}/api/job_download/{job_id}"
                        down_req = urllib.request.Request(down_url, headers={'User-Agent': 'KoraApp/3.1', 'ngrok-skip-browser-warning': '1'})
                        out_path = os.path.join(self.user_data_dir, f"deepfake_{int(time.time())}.mp4")
                        with urllib.request.urlopen(down_req, timeout=120, context=ctx) as dl_resp, open(out_path, "wb") as out_f:
                            out_f.write(dl_resp.read())

                        Clock.schedule_once(lambda dt, p=out_path: self._on_pipeline_success(p, is_video=True), 0)
                        break
                    elif status == 'failed':
                        raise Exception(st_json.get('error', 'Processing failed on GPU'))

        except urllib.error.HTTPError as he:
            err_msg = f"HTTP Error {he.code}"
            try:
                err_body = json.loads(he.read().decode('utf-8'))
                err_msg = err_body.get('error', err_msg)
            except Exception:
                pass
            Clock.schedule_once(lambda dt, m=err_msg: self._on_pipeline_failure(m), 0)
        except urllib.error.URLError:
            Clock.schedule_once(lambda dt, m="सर्वर से संपर्क नहीं हो सका। Colab चेक करें": self._on_pipeline_failure(m), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt, m=str(e): self._on_pipeline_failure(m), 0)

    def _on_pipeline_success(self, path, is_video):
        self.is_loading = False
        self.progress_val = 100
        self.is_error = False

        if is_video:
            self.deepfake_result_vid = path
            self.deepfake_result_thumb = self.get_video_thumbnail(path)
            if self.current_tool == 'DEEPFAKE':
                self.active_display_video = self.deepfake_result_vid
                self.active_display_image = self.deepfake_result_thumb
                self.status_msg = "🎉 10s HD Deepfake तैयार है (Audio Preserved)!"
        else:
            self.faceswap_result_img = path
            if self.current_tool == 'FACESWAP':
                self.active_display_video = ""
                self.active_display_image = self.faceswap_result_img
                self.status_msg = "🎉 4K FaceSwap तैयार है!"

        try:
            sc = self.root.ids.zoom_container.ids.scatter
            sc.scale = 1.0
            sc.center = self.root.ids.zoom_container.center
        except Exception:
            pass

        self.toast("Ready! Tap Download to save.")

    def _on_pipeline_failure(self, err_msg):
        self.is_loading = False
        self.progress_val = 0
        self.is_error = True
        self.status_msg = f"त्रुटि: {err_msg[:60]}"
        self.toast("Failed!")

    def save_final_result(self):
        fpath = ""
        if self.current_tool == 'DEEPFAKE':
            fpath = self.deepfake_result_vid
        elif self.current_tool == 'FACESWAP':
            fpath = self.faceswap_result_img
        else:
            fpath = self.active_display_video if self.active_display_video else self.active_display_image

        if not fpath or not os.path.exists(fpath):
            self.toast("No file to save!")
            return
        try:
            if platform == 'win':
                user = os.environ.get('USERPROFILE', os.path.expanduser('~'))
                dest_dir = os.path.join(user, 'Downloads', 'Kora AI')
            elif platform == 'android':
                dest_dir = "/storage/emulated/0/Download/Kora AI"
            else:
                dest_dir = os.path.join(os.path.expanduser('~'), 'Downloads', 'Kora AI')

            os.makedirs(dest_dir, exist_ok=True)
            ext = ".mp4" if (fpath.lower().endswith('.mp4') or self.current_tool == 'DEEPFAKE') else ".jpg"
            target_name = os.path.join(dest_dir, f"Kora_Output_{int(time.time())}{ext}")
            with open(fpath, "rb") as rf, open(target_name, "wb") as wf:
                wf.write(rf.read())

            if platform == 'android':
                try:
                    from jnius import autoclass
                    autoclass('android.media.MediaScannerConnection').scanFile(
                        autoclass('org.kivy.android.PythonActivity').mActivity,
                        [target_name], None, None
                    )
                except Exception:
                    pass

            self.toast(f"Saved: {os.path.basename(target_name)}", duration=2.5)
        except Exception as e:
            self.toast(f"Save failed: {str(e)[:30]}")

    def toast(self, msg, duration=1.5):
        box = BoxLayout(padding=dp(8))
        box.add_widget(Label(text=f"[b]{msg}[/b]", markup=True, halign='center', font_size='11sp', color=(0.0, 0.88, 1.0, 1)))
        pop = Popup(title="Kora", content=box, size_hint=(0.75, 0.22), auto_dismiss=True, title_color=(0.0, 0.88, 1.0, 1))
        pop.open()
        Clock.schedule_once(lambda dt: pop.dismiss(), duration)

if __name__ == '__main__':
    KoraApp().run()