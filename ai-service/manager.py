from flask import Flask, jsonify, request
from flask_cors import CORS

import subprocess
import sys
import os
import time
import json
import wave
import io

import numpy as np
import paho.mqtt.client as mqtt
import ollama


# ==================================================
# FLASK
# ==================================================

app = Flask(__name__)
CORS(app)


# ==================================================
# THƯ MỤC GỐC
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ==================================================
# MQTT
# ==================================================

MQTT_BROKER = "192.168.100.148"
MQTT_PORT = 1883

DEVICE_ID = "node-01"

TOPIC_CMD = f"devices/{DEVICE_ID}/cmd"
TOPIC_AI_COMMAND = "ai/command"


mqtt_client = mqtt.Client(
    callback_api_version=
        mqtt.CallbackAPIVersion.VERSION2,
    client_id="ai-manager"
)


mqtt_client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    15
)


mqtt_client.loop_start()


# ==================================================
# PROCESS GESTURE / FACE
# ==================================================

processes = {
    "gesture": None,
    "face": None
}


# ==================================================
# VOICE STATE
# ==================================================

voice_active = False


# ==================================================
# KIỂM TRA AI CÓ ĐANG CHẠY
# ==================================================

def is_running(mode):

    global voice_active

    if mode == "voice":
        return voice_active


    process = processes.get(
        mode
    )


    if process is None:
        return False


    return (
        process.poll()
        is None
    )


# ==================================================
# STATUS
# ==================================================

@app.get("/api/ai/status")
def get_status():

    return jsonify({

        "gesture":
            is_running(
                "gesture"
            ),

        "voice":
            voice_active,

        "face":
            is_running(
                "face"
            )

    })


# ==================================================
# START AI
# ==================================================

@app.post("/api/ai/start/<mode>")
def start_ai(mode):

    global voice_active


    # ==============================================
    # VOICE
    # ==============================================

    if mode == "voice":

        voice_active = True


        mqtt_client.publish(
            "ai/status/voice",
            "online",
            qos=1,
            retain=True
        )


        return jsonify({

            "success": True,

            "message":
                "Voice AI da san sang"

        })


    # ==============================================
    # GESTURE / FACE
    # ==============================================

    if mode not in processes:

        return jsonify({

            "success": False,

            "message":
                "Che do AI khong hop le"

        }), 400


    # ==============================================
    # ĐANG CHẠY RỒI
    # ==============================================

    if is_running(mode):

        return jsonify({

            "success": True,

            "message":
                f"AI {mode} dang chay"

        })


    # ==============================================
    # AI SERVICE
    # ==============================================

    ai_service_path = os.path.join(
        BASE_DIR,
        "ai_service.py"
    )


    print()
    print(
        "===================================="
    )

    print(
        f"Dang khoi dong AI: {mode}"
    )

    print(
        "===================================="
    )


    try:

        process = subprocess.Popen(

            [
                sys.executable,
                ai_service_path,
                "--mode",
                mode
            ],

            cwd=
                BASE_DIR,

            stdout=None,
            stderr=None
        )


        processes[mode] = process


        # Chờ kiểm tra lỗi khởi động
        time.sleep(
            1.5
        )


        if (
            process.poll()
            is not None
        ):

            processes[mode] = None


            print(
                f"AI {mode} khoi dong THAT BAI"
            )


            return jsonify({

                "success": False,

                "message":
                    f"AI {mode} khoi dong that bai. "
                    "Hay xem loi trong Terminal."

            }), 500


        print(
            f"AI {mode} da khoi dong"
        )


        return jsonify({

            "success": True,

            "message":
                f"Da khoi dong AI {mode}"

        })


    except Exception as error:

        print(
            "Loi khoi dong AI:",
            error
        )


        processes[mode] = None


        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# ==================================================
# STOP AI
# ==================================================

@app.post("/api/ai/stop/<mode>")
def stop_ai(mode):

    global voice_active


    # ==============================================
    # VOICE
    # ==============================================

    if mode == "voice":

        voice_active = False


        mqtt_client.publish(
            "ai/status/voice",
            "offline",
            qos=1,
            retain=True
        )


        return jsonify({

            "success": True,

            "message":
                "Da dung Voice AI"

        })


    # ==============================================
    # GESTURE / FACE
    # ==============================================

    if mode not in processes:

        return jsonify({

            "success": False,

            "message":
                "Che do AI khong hop le"

        }), 400


    process = processes.get(
        mode
    )


    # ==============================================
    # ĐÃ DỪNG
    # ==============================================

    if (
        process is None
        or
        process.poll() is not None
    ):

        processes[mode] = None


        mqtt_client.publish(
            f"ai/status/{mode}",
            "offline",
            qos=1,
            retain=True
        )


        return jsonify({

            "success": True,

            "message":
                f"AI {mode} da dung"

        })


    # ==============================================
    # DỪNG PROCESS
    # ==============================================

    print(
        f"Dang dung AI {mode}..."
    )


    process.terminate()


    try:

        process.wait(
            timeout=5
        )

    except subprocess.TimeoutExpired:

        process.kill()


    processes[mode] = None


    mqtt_client.publish(
        f"ai/status/{mode}",
        "offline",
        qos=1,
        retain=True
    )


    print(
        f"AI {mode} da dung"
    )


    return jsonify({

        "success": True,

        "message":
            f"Da dung AI {mode}"

    })


# ==================================================
# PHOWHISPER
# ==================================================

asr = None


def get_asr():

    global asr


    if asr is None:

        print()
        print(
            "Dang tai PhoWhisper..."
        )


        from transformers import pipeline


        asr = pipeline(
            "automatic-speech-recognition",
            model=
                "vinai/PhoWhisper-tiny"
        )


        print(
            "PhoWhisper da san sang"
        )


    return asr


# ==================================================
# PROMPT QWEN
# ==================================================

SYSTEM_PROMPT = """
Bạn điều khiển thiết bị IoT bằng giọng nói tiếng Việt.

Chỉ trả về DUY NHẤT một JSON hợp lệ.

Nếu người dùng muốn bật đèn:
{"label":"Bật đèn","command":{"led":"ON"}}

Nếu người dùng muốn tắt đèn:
{"label":"Tắt đèn","command":{"led":"OFF"}}

Nếu câu nói không phải hai lệnh trên:
{"label":"Không xác định","command":{}}
"""


# ==================================================
# VOICE RECOGNITION
# ==================================================

@app.post("/api/voice/recognize")
def recognize_voice():

    global voice_active


    # ==============================================
    # VOICE CHƯA BẬT
    # ==============================================

    if not voice_active:

        return jsonify({

            "success": False,

            "message":
                "Voice AI chua duoc bat"

        }), 400


    # ==============================================
    # KHÔNG CÓ FILE AUDIO
    # ==============================================

    if (
        "audio"
        not in request.files
    ):

        return jsonify({

            "success": False,

            "message":
                "Khong co du lieu am thanh"

        }), 400


    audio_file = (
        request.files[
            "audio"
        ]
    )


    audio_bytes = (
        audio_file.read()
    )


    # ==============================================
    # ĐỌC WAV
    # ==============================================

    try:

        wav = wave.open(
            io.BytesIO(
                audio_bytes
            ),
            "rb"
        )


        sample_rate = (
            wav.getframerate()
        )


        frames = (
            wav.readframes(
                wav.getnframes()
            )
        )


        channels = (
            wav.getnchannels()
        )


        wav.close()


        audio = (
            np.frombuffer(
                frames,
                dtype=np.int16
            )
            .astype(
                np.float32
            )
        )


        audio = (
            audio / 32768.0
        )


        # ==========================================
        # STEREO → MONO
        # ==========================================

        if channels > 1:

            audio = (
                audio.reshape(
                    -1,
                    channels
                )
                .mean(
                    axis=1
                )
            )


    except Exception as error:

        return jsonify({

            "success": False,

            "message":
                f"Loi doc WAV: {error}"

        }), 400


    # ==============================================
    # PHOWHISPER
    # ==============================================

    try:

        recognizer = (
            get_asr()
        )


        result = recognizer({

            "array":
                audio,

            "sampling_rate":
                sample_rate

        })


        text = (
            result[
                "text"
            ]
            .strip()
        )


        print()
        print(
            "PhoWhisper:",
            text
        )


    except Exception as error:

        print(
            "PhoWhisper loi:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                f"PhoWhisper loi: {error}"

        }), 500


    # ==============================================
    # KHÔNG NGHE ĐƯỢC
    # ==============================================

    if not text:

        return jsonify({

            "success": False,

            "message":
                "Khong nghe duoc noi dung"

        })


    # ==============================================
    # QWEN
    # ==============================================

    try:

        response = ollama.chat(

            model=
                "qwen2.5:1.5b-instruct",

            format=
                "json",

            messages=[

                {
                    "role":
                        "system",

                    "content":
                        SYSTEM_PROMPT
                },

                {
                    "role":
                        "user",

                    "content":
                        text
                }

            ]

        )


        data = json.loads(

            response[
                "message"
            ][
                "content"
            ]

        )


    except Exception as error:

        print(
            "Qwen loi:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                f"Qwen loi: {error}"

        }), 500


    # ==============================================
    # LẤY KẾT QUẢ QWEN
    # ==============================================

    label = data.get(
        "label",
        "Không xác định"
    )


    command = data.get(
        "command",
        {}
    )


    # ==================================================
    # QUAN TRỌNG NHẤT:
    # ÉP VOICE SANG MANUAL
    #
    # Bật → giữ sáng
    # Tắt → giữ tắt
    # AUTO KHÔNG GHI ĐÈ SAU 2 GIÂY
    # ==================================================

    if (
        command.get("led")
        ==
        "ON"
    ):

        command = {

            "mode":
                "MANUAL",

            "led":
                "ON"

        }


        label = (
            "Bật đèn"
        )


    elif (
        command.get("led")
        ==
        "OFF"
    ):

        command = {

            "mode":
                "MANUAL",

            "led":
                "OFF"

        }


        label = (
            "Tắt đèn"
        )


    # ==============================================
    # DEBUG
    # ==============================================

    print(
        "Lenh Voice cuoi cung:",
        command
    )


    # ==============================================
    # GỬI MQTT XUỐNG ESP32
    # ==============================================

    if command:

        mqtt_client.publish(

            TOPIC_CMD,

            json.dumps(
                command,
                ensure_ascii=False
            ),

            qos=1

        )


        print(
            "Gui ESP32:",
            command
        )


    # ==============================================
    # GỬI KẾT QUẢ LÊN DASHBOARD
    # ==============================================

    ai_data = {

        "source":
            "voice",

        "label":
            label,

        "text":
            text,

        "command":
            command,

        "confidence":
            1.0

    }


    mqtt_client.publish(

        TOPIC_AI_COMMAND,

        json.dumps(
            ai_data,
            ensure_ascii=False
        ),

        qos=1

    )


    # ==============================================
    # TRẢ VỀ WEB
    # ==============================================

    return jsonify({

        "success":
            True,

        "text":
            text,

        "label":
            label,

        "command":
            command

    })


# ==================================================
# CHẠY SERVER
# ==================================================

if __name__ == "__main__":

    print()
    print(
        "===================================="
    )

    print(
        "AI MANAGER DANG CHAY"
    )

    print(
        "http://localhost:5001"
    )

    print(
        "===================================="
    )

    print()


    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False,
        threaded=True
    )