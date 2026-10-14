import cv2
import numpy as np

from insightface.app import FaceAnalysis


# ==========================================
# NHẬP TÊN
# ==========================================

NAME = input(
    "Nhap ten nguoi can dang ky: "
).strip()


if not NAME:

    print(
        "Ten khong duoc de trong"
    )

    exit()


# ==========================================
# KHỞI TẠO INSIGHTFACE
# ==========================================

print(
    "Dang tai InsightFace..."
)


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


print(
    "InsightFace da san sang"
)


# ==========================================
# CAMERA
# ==========================================

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print(
        "Khong mo duoc camera"
    )

    exit()


embeddings = []


print()
print(
    "======================================"
)
print(
    "DANG KY KHUON MAT"
)
print(
    "======================================"
)

print(
    "Nhan SPACE de luu mau"
)

print(
    "Can 20 mau"
)

print(
    "Nhan Q de thoat"
)

print()


# ==========================================
# VÒNG LẶP CAMERA
# ==========================================

while True:

    ok, frame = cap.read()


    if not ok:

        print(
            "Khong doc duoc camera"
        )

        break


    faces = app.get(frame)


    # ======================================
    # NẾU CÓ MẶT
    # ======================================

    if faces:

        face = faces[0]


        x1, y1, x2, y2 = (
            face.bbox.astype(int)
        )


        cv2.rectangle(

            frame,

            (x1, y1),

            (x2, y2),

            (0, 255, 0),

            2

        )


        cv2.putText(

            frame,

            "Da phat hien khuon mat",

            (
                x1,
                max(
                    y1 - 10,
                    30
                )
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0, 255, 0),

            2

        )


    else:

        cv2.putText(

            frame,

            "Khong tim thay khuon mat",

            (10, 70),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0, 0, 255),

            2

        )


    # ======================================
    # HIỂN THỊ SỐ MẪU
    # ======================================

    cv2.putText(

        frame,

        f"So mau: {len(embeddings)}/20",

        (10, 35),

        cv2.FONT_HERSHEY_SIMPLEX,

        1,

        (255, 255, 255),

        2

    )


    cv2.imshow(

        "Dang ky khuon mat",

        frame

    )


    key = (
        cv2.waitKey(1)
        &
        0xFF
    )


    # ======================================
    # SPACE = LƯU MẪU
    # ======================================

    if (
        key == 32
        and
        faces
    ):

        embedding = (
            faces[0]
            .normed_embedding
        )


        embeddings.append(
            embedding
        )


        print(
            f"Da luu mau "
            f"{len(embeddings)}/20"
        )


    # ======================================
    # Q = THOÁT
    # ======================================

    if key == ord("q"):

        break


    # ĐỦ 20 MẪU
    if len(embeddings) >= 20:

        break


# ==========================================
# ĐÓNG CAMERA
# ==========================================

cap.release()

cv2.destroyAllWindows()


# ==========================================
# KIỂM TRA
# ==========================================

if len(embeddings) == 0:

    print(
        "Khong co du lieu khuon mat"
    )

    exit()


# ==========================================
# LẤY EMBEDDING TRUNG BÌNH
# ==========================================

new_embedding = np.mean(

    embeddings,

    axis=0

)


# Chuẩn hóa
new_embedding = (

    new_embedding

    /

    np.linalg.norm(
        new_embedding
    )

)


# ==========================================
# ĐỌC DB CŨ
# ==========================================

try:

    old_data = dict(

        np.load(
            "faces_db.npz"
        )

    )


except Exception:

    old_data = {}


# ==========================================
# LƯU NGƯỜI MỚI
# ==========================================

old_data[NAME] = (
    new_embedding
)


np.savez(

    "faces_db.npz",

    **old_data

)


print()
print(
    "======================================"
)
print(
    "DANG KY THANH CONG"
)
print(
    "======================================"
)

print(
    "Ten:",
    NAME
)

print(
    "So mau:",
    len(embeddings)
)

print(
    "Da luu vao faces_db.npz"
)