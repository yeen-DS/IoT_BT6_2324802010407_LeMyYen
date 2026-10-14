import time
import cv2
import mediapipe as mp


# ==================================================
# CẤU HÌNH
# ==================================================

STABLE_FRAMES = 8
COOLDOWN = 3

# Đầu ngón tay:
# 8  = trỏ
# 12 = giữa
# 16 = áp út
# 20 = út
TIPS = [8, 12, 16, 20]


# ==================================================
# CỬ CHỈ → LỆNH
# ==================================================

GESTURES = {

    # 1 ngón → bật relay
    1: (
        "Bat relay",
        {
            "mode": "MANUAL",
            "relay": "ON"
        }
    ),

    # 2 ngón → tắt relay
    2: (
        "Tat relay",
        {
            "mode": "MANUAL",
            "relay": "OFF"
        }
    ),

    # 3 ngón → bật LED
    3: (
        "Bat den LED",
        {
            "mode": "MANUAL",
            "led": "ON"
        }
    ),

    # 4 ngón → tắt LED
    4: (
        "Tat den LED",
        {
            "mode": "MANUAL",
            "led": "OFF"
        }
    ),

    # 5 ngón → AUTO
    5: (
        "Bat che do AUTO",
        {
            "mode": "AUTO"
        }
    )

}


# ==================================================
# ĐẾM NGÓN TAY
# ==================================================

def count_fingers(
    landmarks,
    hand_label
):

    count = 0


    # ==================================================
    # 4 NGÓN:
    # TRỎ - GIỮA - ÁP ÚT - ÚT
    # ==================================================

    for tip in TIPS:

        if (
            landmarks[tip].y
            <
            landmarks[tip - 2].y
        ):

            count += 1


    # ==================================================
    # NGÓN CÁI
    # ==================================================

    if hand_label == "Right":

        if (
            landmarks[4].x
            <
            landmarks[3].x
        ):

            count += 1

    else:

        if (
            landmarks[4].x
            >
            landmarks[3].x
        ):

            count += 1


    return count


# ==================================================
# CHẠY AI CỬ CHỈ TAY
# ==================================================

def run(
    send_command
):

    # ==================================================
    # MEDIAPIPE HANDS
    # ==================================================

    mp_hands = (
        mp.solutions.hands
    )


    hands = mp_hands.Hands(

        static_image_mode=False,

        max_num_hands=1,

        min_detection_confidence=0.7,

        min_tracking_confidence=0.6

    )


    draw = (
        mp.solutions.drawing_utils
    )


    # ==================================================
    # CAMERA
    # ==================================================

    cap = cv2.VideoCapture(
        0
    )


    if not cap.isOpened():

        print(
            "Khong mo duoc camera"
        )

        return


    # ==================================================
    # BIẾN
    # ==================================================

    history = []

    last_command_time = 0

    last_label = ""


    print()
    print(
        "======================================"
    )

    print(
        "AI CU CHI TAY DANG CHAY"
    )

    print(
        "======================================"
    )

    print(
        "1 ngon -> Bat relay"
    )

    print(
        "2 ngon -> Tat relay"
    )

    print(
        "3 ngon -> Bat LED"
    )

    print(
        "4 ngon -> Tat LED"
    )

    print(
        "5 ngon -> AUTO"
    )

    print(
        "Nhan Q de thoat"
    )

    print(
        "======================================"
    )


    # ==================================================
    # VÒNG LẶP CAMERA
    # ==================================================

    while True:

        ok, frame = (
            cap.read()
        )


        if not ok:

            print(
                "Khong doc duoc camera"
            )

            break


        # ==================================================
        # LẬT CAMERA GIỐNG GƯƠNG
        # ==================================================

        frame = cv2.flip(
            frame,
            1
        )


        # ==================================================
        # BGR → RGB
        # ==================================================

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        # ==================================================
        # MEDIAPIPE NHẬN DIỆN
        # ==================================================

        result = hands.process(
            rgb
        )


        fingers = 0

        hand_detected = False


        # ==================================================
        # NẾU CÓ BÀN TAY
        # ==================================================

        if (
            result.multi_hand_landmarks
            and
            result.multi_handedness
        ):

            hand_detected = True


            hand = (
                result
                .multi_hand_landmarks[0]
            )


            hand_label = (

                result
                .multi_handedness[0]
                .classification[0]
                .label

            )


            # ==================================================
            # ĐẾM NGÓN
            # ==================================================

            fingers = count_fingers(

                hand.landmark,

                hand_label

            )


            # ==================================================
            # VẼ KHUNG XƯƠNG BÀN TAY
            # ==================================================

            draw.draw_landmarks(

                frame,

                hand,

                mp_hands.HAND_CONNECTIONS

            )


            # ==================================================
            # CHỈ HIỆN SỐ NGÓN KHI CÓ TAY
            # ==================================================

            cv2.putText(

                frame,

                f"So ngon tay: {fingers}",

                (10, 40),

                cv2.FONT_HERSHEY_SIMPLEX,

                1,

                (0, 255, 0),

                2

            )


            # ==================================================
            # LƯU FRAME
            # ==================================================

            history = (

                history
                +
                [fingers]

            )[-STABLE_FRAMES:]


        # ==================================================
        # KHÔNG CÓ TAY
        # KHÔNG HIỆN CHỮ GÌ
        # ==================================================

        else:

            history.clear()


        # ==================================================
        # KIỂM TRA 8 FRAME ỔN ĐỊNH
        # ==================================================

        if (

            hand_detected

            and

            len(history)
            ==
            STABLE_FRAMES

            and

            len(
                set(history)
            )
            ==
            1

            and

            fingers
            in
            GESTURES

            and

            time.time()
            -
            last_command_time
            >
            COOLDOWN

        ):

            label, command = (
                GESTURES[
                    fingers
                ]
            )


            # ==================================================
            # GỬI LỆNH
            # ==================================================

            send_command(

                "gesture",

                label,

                command,

                1.0

            )


            print()

            print(
                "Nhan dien:",
                fingers,
                "ngon"
            )

            print(
                "Lenh:",
                label
            )

            print(
                "Command:",
                command
            )


            last_command_time = (
                time.time()
            )


            last_label = (
                label
            )


            # Xóa history để không gửi liên tục
            history.clear()


        # ==================================================
        # HIỆN LỆNH GẦN NHẤT
        # ==================================================

        if last_label != "":

            cv2.putText(

                frame,

                f"Lenh: {last_label}",

                (10, 80),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (255, 255, 0),

                2

            )


        # ==================================================
        # CAMERA
        # ==================================================

        cv2.imshow(

            "AI cu chi tay",

            frame

        )


        # ==================================================
        # Q → THOÁT
        # ==================================================

        if (

            cv2.waitKey(1)
            &
            0xFF

            ==

            ord("q")

        ):

            break


    # ==================================================
    # DỌN CAMERA
    # ==================================================

    cap.release()

    hands.close()

    cv2.destroyAllWindows()


    print(
        "Da dung AI cu chi tay"
    )