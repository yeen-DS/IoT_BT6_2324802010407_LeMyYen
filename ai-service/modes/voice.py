import json
import sounddevice as sd
import ollama

from transformers import pipeline


# ==========================================
# CẤU HÌNH
# ==========================================

SAMPLE_RATE = 16000
DURATION = 4

LLM_MODEL = "qwen2.5:1.5b-instruct"


# ==========================================
# PROMPT CHO LLM
# ==========================================

SYSTEM_PROMPT = """
Bạn điều khiển thiết bị IoT bằng giọng nói tiếng Việt.

Chỉ trả về DUY NHẤT JSON, không giải thích thêm.

Các lệnh hợp lệ:

{"label":"Bật relay","command":{"relay":"ON"}}

{"label":"Tắt relay","command":{"relay":"OFF"}}

{"label":"Bật đèn","command":{"led":"ON"}}

{"label":"Tắt đèn","command":{"led":"OFF"}}

{"label":"Bật AUTO","command":{"mode":"AUTO"}}

{"label":"Bật MANUAL","command":{"mode":"MANUAL"}}

Nếu người dùng nói câu tự nhiên như:
- "bật đèn lên"
- "mở đèn"
- "bật giúp tôi cái đèn"

thì vẫn phải trả về:

{"label":"Bật đèn","command":{"led":"ON"}}

Nếu câu nói không thuộc các lệnh trên, trả về:

{"label":"Không xác định","command":{}}
"""


# ==========================================
# HÀM CHẠY AI GIỌNG NÓI
# ==========================================

def run(send_command):

    print("===================================")
    print("DANG TAI PHOWHISPER...")
    print("===================================")

    asr = pipeline(
        "automatic-speech-recognition",
        model="vinai/PhoWhisper-tiny"
    )


    print()
    print("AI GIONG NOI DA SAN SANG")
    print("Nhan Enter roi noi trong 4 giay")
    print("Nhan Ctrl+C de thoat")
    print()


    while True:

        # ==================================
        # CHỜ NGƯỜI DÙNG
        # ==================================

        input(
            "\nNhan Enter de bat dau noi..."
        )


        # ==================================
        # GHI ÂM
        # ==================================

        print(
            "Dang nghe..."
        )


        audio = sd.rec(

            int(
                DURATION
                *
                SAMPLE_RATE
            ),

            samplerate=
                SAMPLE_RATE,

            channels=
                1,

            dtype=
                "float32"

        )


        sd.wait()


        print(
            "Da ghi am xong"
        )


        # ==================================
        # PHOWHISPER NHẬN DẠNG GIỌNG NÓI
        # ==================================

        print(
            "Dang nhan dang giong noi..."
        )


        result = asr({

            "array":
                audio.flatten(),

            "sampling_rate":
                SAMPLE_RATE

        })


        text = (
            result["text"]
            .strip()
        )


        print()
        print(
            "Nghe duoc:",
            text
        )


        # Nếu không nghe được gì
        if not text:

            print(
                "Khong nghe duoc noi dung."
            )

            continue


        # ==================================
        # QWEN HIỂU CÂU LỆNH
        # ==================================

        print(
            "Dang phan tich lenh..."
        )


        response = ollama.chat(

            model=
                LLM_MODEL,

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


        # ==================================
        # LẤY JSON TỪ LLM
        # ==================================

        try:

            data = json.loads(

                response[
                    "message"
                ][
                    "content"
                ]

            )

        except Exception as error:

            print(
                "LLM tra ve JSON loi:",
                error
            )

            continue


        print(
            "LLM:",
            data
        )


        # ==================================
        # KIỂM TRA COMMAND
        # ==================================

        command = data.get(
            "command",
            {}
        )


        label = data.get(
            "label",
            text
        )


        # Không nhận ra lệnh
        if not command:

            print(
                "Khong xac dinh duoc lenh hop le."
            )

            continue


        # ==================================
        # GỬI MQTT
        #
        # tham số cuối "text"
        # giúp Dashboard hiển thị
        # câu mà PhoWhisper nghe được
        # ==================================

        send_command(

            "voice",

            label,

            command,

            1.0,

            text

        )


        print()
        print(
            "Da gui lenh MQTT"
        )
        print(
            "Noi dung:",
            text
        )
        print(
            "Lenh:",
            command
        )