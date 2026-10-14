import time
import cv2
import numpy as np

from insightface.app import FaceAnalysis


# ==========================================
# CẤU HÌNH
# ==========================================

SIM_THRESHOLD = 0.45

STABLE_FRAMES = 5

COOLDOWN = 8


# ==========================================
# HÀM CHẠY FACE AI
# ==========================================

def run(send_command):

    print(
        "Dang tai AI khuon mat..."
    )


    # ======================================
    # KHỞI TẠO INSIGHTFACE
    # ======================================

    app = FaceAnalysis(

        name="buffalo_sc",

        providers=[
            "CPUExecutionProvider"
        ]

    )


    app.prepare(

        ctx_id=-1,

        det_size=(320, 320)

    )


    # ======================================
    # ĐỌC DATABASE KHUÔN MẶT
    # ======================================

    try:

        db = dict(

            np.load(
                "faces_db.npz"
            )

        )

    except Exception as error:

        print(
            "Khong tim thay faces_db.npz"
        )

        print(
            "Hay chay enroll_faces.py truoc"
        )

        print(
            "Loi:",
            error
        )

        return


    # ======================================
    # KIỂM TRA DATABASE
    # ======================================

    if len(db) == 0:

        print(
            "Database khuon mat rong"
        )

        return


    # ======================================
    # DANH SÁCH TÊN
    # ======================================

    names = list(
        db.keys()
    )


    # ======================================
    # MA TRẬN EMBEDDING
    # ======================================

    matrix = np.stack(

        [
            db[name]
            for name in names
        ]

    )


    print(
        "Da tai khuon mat:",
        names
    )


    # ======================================
    # CAMERA
    # ======================================

    cap = cv2.VideoCapture(
        0
    )


    if not cap.isOpened():

        print(
            "Khong mo duoc camera"
        )

        return


    print()

    print(
        "======================================"
    )

    print(
        "AI KHUON MAT DANG CHAY"
    )

    print(
        "======================================"
    )

    print(
        "Nguoi quen -> Bat LED"
    )

    print(
        "Nguoi la -> Tat LED"
    )

    print(
        "Nhan Q de thoat"
    )

    print(
        "======================================"
    )


    # ======================================
    # BIẾN
    # ======================================

    last_name = None

    stable_count = 0

    last_command_time = 0


    # ======================================
    # VÒNG LẶP CAMERA
    # ======================================

    while True:

        ok, frame = (
            cap.read()
        )


        if not ok:

            print(
                "Khong doc duoc camera"
            )

            break


        # ==================================
        # NHẬN DIỆN KHUÔN MẶT
        # ==================================

        faces = app.get(
            frame
        )


        current_name = None

        current_score = 0.0


        # ==================================
        # NẾU CÓ KHUÔN MẶT
        # ==================================

        if faces:

            face = faces[0]


            # ==================================
            # SO SÁNH EMBEDDING
            # ==================================

            similarities = (

                matrix

                @

                face.normed_embedding

            )


            best_index = int(

                np.argmax(
                    similarities
                )

            )


            score = float(

                similarities[
                    best_index
                ]

            )


            current_score = score


            # ==================================
            # NGƯỜI QUEN / NGƯỜI LẠ
            # ==================================

            if (
                score
                >=
                SIM_THRESHOLD
            ):

                current_name = (

                    names[
                        best_index
                    ]

                )

            else:

                current_name = (
                    "Nguoi la"
                )


            # ==================================
            # LẤY VỊ TRÍ KHUÔN MẶT
            # ==================================

            x1, y1, x2, y2 = (

                face.bbox.astype(int)

            )


            # ==================================
            # MÀU KHUNG
            # ==================================

            if (
                current_name
                !=
                "Nguoi la"
            ):

                # Người quen: xanh
                color = (
                    0,
                    255,
                    0
                )

            else:

                # Người lạ: đỏ
                color = (
                    0,
                    0,
                    255
                )


            # ==================================
            # VẼ KHUNG
            # ==================================

            cv2.rectangle(

                frame,

                (x1, y1),

                (x2, y2),

                color,

                2

            )


            # ==================================
            # HIỂN THỊ TÊN + SCORE
            # ==================================

            label_text = (

                f"{current_name} "
                f"{score:.2f}"

            )


            cv2.putText(

                frame,

                label_text,

                (
                    x1,

                    max(
                        y1 - 10,
                        30
                    )

                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.8,

                color,

                2

            )


        # ==================================
        # KIỂM TRA ỔN ĐỊNH NHIỀU FRAME
        # ==================================

        if current_name:

            if (
                current_name
                ==
                last_name
            ):

                stable_count += 1

            else:

                stable_count = 1

                last_name = (
                    current_name
                )


        else:

            stable_count = 0

            last_name = None


        # ==================================
        # GỬI LỆNH
        # ==================================

        if (

            current_name

            and

            stable_count
            >=
            STABLE_FRAMES

            and

            time.time()
            -
            last_command_time
            >
            COOLDOWN

        ):

            # ==================================
            # NGƯỜI QUEN
            # ==================================

            if (
                current_name
                !=
                "Nguoi la"
            ):

                command = {

                    "mode":
                        "MANUAL",

                    "led":
                        "ON"

                }


                send_command(

                    "face",

                    f"Nhan dien {current_name}",

                    command,

                    current_score

                )


                print()

                print(
                    "Nguoi quen:",
                    current_name
                )

                print(
                    "Do tuong dong:",
                    current_score
                )

                print(
                    "Lenh:",
                    command
                )


            # ==================================
            # NGƯỜI LẠ
            # ==================================

            else:

                command = {

                    "mode":
                        "MANUAL",

                    "led":
                        "OFF"

                }


                send_command(

                    "face",

                    "Phat hien nguoi la",

                    command,

                    current_score

                )


                print()

                print(
                    "Nguoi la"
                )

                print(
                    "Do tuong dong:",
                    current_score
                )

                print(
                    "Lenh:",
                    command
                )


            # ==================================
            # GHI THỜI GIAN GỬI LỆNH
            # ==================================

            last_command_time = (
                time.time()
            )


        # ==================================
        # HIỂN THỊ CAMERA
        # ==================================

        cv2.imshow(

            "AI nhan dien khuon mat - Q de thoat",

            frame

        )


        # ==================================
        # NHẤN Q ĐỂ THOÁT
        # ==================================

        if (

            cv2.waitKey(1)
            &
            0xFF

            ==

            ord("q")

        ):

            break


    # ======================================
    # ĐÓNG CAMERA
    # ======================================

    cap.release()

    cv2.destroyAllWindows()


    print(
        "Da dung AI khuon mat"
    )