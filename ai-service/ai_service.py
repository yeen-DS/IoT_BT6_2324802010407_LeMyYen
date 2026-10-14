import argparse
import json
import paho.mqtt.client as mqtt


# ==========================================
# 1. CẤU HÌNH MQTT
# ==========================================

MQTT_BROKER = "192.168.100.148"
MQTT_PORT = 1883

DEVICE_ID = "node-01"

TOPIC_CMD = f"devices/{DEVICE_ID}/cmd"

# Nhật ký kết quả AI gửi lên Web
TOPIC_AI_COMMAND = "ai/command"


# ==========================================
# 2. CHỌN AI
# ==========================================

parser = argparse.ArgumentParser()

parser.add_argument(
    "--mode",
    choices=[
        "gesture",
        "voice",
        "face"
    ],
    default="gesture"
)

args = parser.parse_args()

mode = args.mode


# ==========================================
# 3. TOPIC STATUS RIÊNG CHO TỪNG AI
# ==========================================

TOPIC_AI_STATUS = f"ai/status/{mode}"

# Ví dụ:
#
# ai/status/gesture
# ai/status/voice
# ai/status/face


# ==========================================
# 4. KẾT NỐI MQTT
# ==========================================

client = mqtt.Client(
    callback_api_version=
        mqtt.CallbackAPIVersion.VERSION2,

    client_id=
        f"ai-{mode}"
)


# ==========================================
# LWT
# Nếu AI chết bất thường
# Broker tự gửi OFFLINE
# ==========================================

client.will_set(
    TOPIC_AI_STATUS,
    "offline",
    qos=1,
    retain=True
)


print(
    f"Dang ket noi MQTT "
    f"{MQTT_BROKER}:{MQTT_PORT}..."
)


client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    keepalive=15
)


client.loop_start()


# ==========================================
# 5. BÁO AI ONLINE
# ==========================================

client.publish(
    TOPIC_AI_STATUS,
    "online",
    qos=1,
    retain=True
)


print(
    f"AI {mode} ONLINE"
)


# ==========================================
# 6. HÀM GỬI LỆNH
# ==========================================

def send_command(
    source,
    label,
    command,
    confidence=1.0,
    text=None
):

    # --------------------------------------
    # Gửi lệnh xuống ESP32
    # --------------------------------------

    client.publish(
        TOPIC_CMD,
        json.dumps(
            command,
            ensure_ascii=False
        ),
        qos=1
    )


    # --------------------------------------
    # Tạo dữ liệu gửi lên Dashboard
    # --------------------------------------

    data = {

        "source":
            source,

        "label":
            label,

        "command":
            command,

        "confidence":
            round(
                float(confidence),
                2
            )
    }


    # Nếu là AI giọng nói
    # thêm câu PhoWhisper nghe được
    if text is not None:

        data["text"] = text


    # --------------------------------------
    # Gửi kết quả AI lên Web
    # --------------------------------------

    client.publish(
        TOPIC_AI_COMMAND,

        json.dumps(
            data,
            ensure_ascii=False
        )
    )


    print(
        f"[{source}] "
        f"{label} "
        f"-> {command}"
    )


    if text:

        print(
            f"Nghe duoc: {text}"
        )


# ==========================================
# 7. CHẠY AI
# ==========================================

try:

    # ------------------------------
    # CỬ CHỈ TAY
    # ------------------------------

    if mode == "gesture":

        print(
            "Khoi dong AI cu chi tay..."
        )

        from modes.gesture import run


    # ------------------------------
    # GIỌNG NÓI
    # ------------------------------

    elif mode == "voice":

        print(
            "Khoi dong AI giong noi..."
        )

        from modes.voice import run


    # ------------------------------
    # KHUÔN MẶT
    # ------------------------------

    elif mode == "face":

        print(
            "Khoi dong AI khuon mat..."
        )

        from modes.face import run


    # Chạy module AI
    run(
        send_command
    )


# ==========================================
# 8. KHI TẮT AI
# ==========================================

except KeyboardInterrupt:

    print(
        "\nDang dung AI..."
    )


finally:

    # Báo AI này OFFLINE
    client.publish(
        TOPIC_AI_STATUS,
        "offline",
        qos=1,
        retain=True
    )


    print(
        f"AI {mode} OFFLINE"
    )


    client.loop_stop()

    client.disconnect()