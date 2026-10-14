<template>
  <div class="ai-page">

    <!-- ================================================= -->
    <!-- TIÊU ĐỀ -->
    <!-- ================================================= -->

    <div class="title-row">
      <div>
        <h2>Trung tâm AI nhận dạng</h2>

        <p>
          Theo dõi cử chỉ tay, giọng nói và khuôn mặt theo thời gian thực
        </p>
      </div>

      <el-tag
        :type="anyAiOnline ? 'success' : 'info'"
        size="large"
      >
        {{
          anyAiOnline
            ? "AI đang hoạt động"
            : "AI chưa hoạt động"
        }}
      </el-tag>
    </div>


    <!-- ================================================= -->
    <!-- 3 AI -->
    <!-- ================================================= -->

    <el-row :gutter="18">

      <!-- ================================================= -->
      <!-- AI 1 - CỬ CHỈ -->
      <!-- ================================================= -->

      <el-col :span="8">
        <el-card class="ai-card">

          <div class="ai-icon">
            ✋
          </div>

          <h3>
            Nhận dạng cử chỉ tay
          </h3>


          <el-tag
            :type="
              store.aiStatus.gesture
                ? 'success'
                : 'danger'
            "
          >
            {{
              store.aiStatus.gesture
                ? "ONLINE"
                : "OFFLINE"
            }}
          </el-tag>


          <div class="buttons">

            <el-button
              type="success"
              :disabled="store.aiStatus.gesture"
              @click="startMode('gesture')"
            >
              ▶ Chạy
            </el-button>


            <el-button
              type="danger"
              :disabled="!store.aiStatus.gesture"
              @click="stopMode('gesture')"
            >
              ■ Dừng
            </el-button>

          </div>


          <el-divider />


          <div class="result-label">
            Nhận dạng gần nhất
          </div>


          <div class="result-value">
            {{
              lastGesture?.label
                || "Chưa có dữ liệu"
            }}
          </div>


          <div
            v-if="lastGesture"
            class="command"
          >
            Lệnh:

            {{
              formatCommand(
                lastGesture.command
              )
            }}
          </div>


          <el-progress
            v-if="lastGesture"
            :percentage="
              confidencePercent(
                lastGesture.confidence
              )
            "
          />

        </el-card>
      </el-col>


      <!-- ================================================= -->
      <!-- AI 2 - GIỌNG NÓI -->
      <!-- ================================================= -->

      <el-col :span="8">
        <el-card class="ai-card">

          <div class="ai-icon">
            🎤
          </div>

          <h3>
            Nhận dạng giọng nói
          </h3>


          <el-tag
            :type="
              store.aiStatus.voice
                ? 'success'
                : 'danger'
            "
          >
            {{
              store.aiStatus.voice
                ? "ONLINE"
                : "OFFLINE"
            }}
          </el-tag>


          <!-- GIỐNG 2 AI CÒN LẠI -->
          <div class="buttons">

            <el-button
              type="success"
              :disabled="store.aiStatus.voice"
              @click="openVoice"
            >
              ▶ Chạy
            </el-button>


            <el-button
              type="danger"
              :disabled="!store.aiStatus.voice"
              @click="stopVoice"
            >
              ■ Dừng
            </el-button>

          </div>


          <el-divider />


          <div class="result-label">
            Nội dung nhận dạng
          </div>


          <div class="result-value">
            {{
              lastVoice?.text
                ||
              lastVoice?.label
                ||
              "Chưa có dữ liệu"
            }}
          </div>


          <div
            v-if="lastVoice"
            class="command"
          >
            Lệnh:

            {{
              formatCommand(
                lastVoice.command
              )
            }}
          </div>


          <el-progress
            v-if="lastVoice"
            :percentage="
              confidencePercent(
                lastVoice.confidence
              )
            "
          />

        </el-card>
      </el-col>


      <!-- ================================================= -->
      <!-- AI 3 - KHUÔN MẶT -->
      <!-- ================================================= -->

      <el-col :span="8">
        <el-card class="ai-card">

          <div class="ai-icon">
            👤
          </div>

          <h3>
            Nhận dạng khuôn mặt
          </h3>


          <el-tag
            :type="
              store.aiStatus.face
                ? 'success'
                : 'danger'
            "
          >
            {{
              store.aiStatus.face
                ? "ONLINE"
                : "OFFLINE"
            }}
          </el-tag>


          <div class="buttons">

            <el-button
              type="success"
              :disabled="store.aiStatus.face"
              @click="startMode('face')"
            >
              ▶ Chạy
            </el-button>


            <el-button
              type="danger"
              :disabled="!store.aiStatus.face"
              @click="stopMode('face')"
            >
              ■ Dừng
            </el-button>

          </div>


          <el-divider />


          <div class="result-label">
            Người được nhận dạng
          </div>


          <div class="result-value">
            {{
              lastFace?.label
                || "Chưa có dữ liệu"
            }}
          </div>


          <div
            v-if="lastFace"
            class="command"
          >
            Lệnh:

            {{
              formatCommand(
                lastFace.command
              )
            }}
          </div>


          <el-progress
            v-if="lastFace"
            :percentage="
              confidencePercent(
                lastFace.confidence
              )
            "
          />

        </el-card>
      </el-col>

    </el-row>


    <!-- ================================================= -->
    <!-- LỊCH SỬ AI -->
    <!-- ================================================= -->

    <el-card
      class="history-card"
      header="Lịch sử nhận dạng AI"
    >

      <el-table
        :data="store.aiCommands"
        height="430"
      >

        <el-table-column
          prop="time"
          label="Thời gian"
          width="120"
        />


        <el-table-column
          label="AI"
          width="140"
        >

          <template #default="{ row }">

            <el-tag
              v-if="row.source === 'gesture'"
            >
              ✋ Cử chỉ
            </el-tag>


            <el-tag
              v-else-if="row.source === 'voice'"
              type="warning"
            >
              🎤 Giọng nói
            </el-tag>


            <el-tag
              v-else-if="row.source === 'face'"
              type="success"
            >
              👤 Khuôn mặt
            </el-tag>

          </template>

        </el-table-column>


        <el-table-column
          prop="label"
          label="Kết quả nhận dạng"
          min-width="180"
        />


        <el-table-column
          label="Nội dung nghe được"
          min-width="190"
        >

          <template #default="{ row }">
            {{
              row.text || "--"
            }}
          </template>

        </el-table-column>


        <el-table-column
          label="Lệnh thiết bị"
          min-width="170"
        >

          <template #default="{ row }">

            {{
              formatCommand(
                row.command
              )
            }}

          </template>

        </el-table-column>


        <el-table-column
          label="Độ tin cậy"
          width="130"
        >

          <template #default="{ row }">

            {{
              confidencePercent(
                row.confidence
              )
            }}%

          </template>

        </el-table-column>

      </el-table>

    </el-card>


    <!-- ================================================= -->
    <!-- CỬA SỔ VOICE -->
    <!-- ================================================= -->

    <el-dialog
      v-model="voiceDialog"
      title="🎤 Nhận dạng giọng nói"
      width="540px"
      :close-on-click-modal="false"
    >

      <div class="voice-window">


        <div
          class="microphone"
          :class="{
            listening: voiceListening
          }"
        >
          🎤
        </div>


        <!-- ĐANG NGHE -->

        <h3
          v-if="voiceListening"
          class="listening-text"
        >
          Đang nghe...
        </h3>


        <!-- ĐANG XỬ LÝ -->

        <h3
          v-else-if="voiceProcessing"
        >
          AI đang nhận dạng...
        </h3>


        <!-- SẴN SÀNG -->

        <h3
          v-else
        >
          Sẵn sàng nhận giọng nói
        </h3>


        <p class="voice-help">
          Hãy nói một trong các lệnh:
        </p>


        <div class="examples">

          <el-tag>
            Bật đèn
          </el-tag>

          <el-tag>
            Tắt đèn
          </el-tag>

         

        </div>


        <el-divider />


        <!-- KẾT QUẢ -->

        <div class="voice-result">

          <div class="result-label">
            Nội dung nghe được
          </div>


          <div class="voice-text">
            {{
              voiceText
                || "Chưa có dữ liệu"
            }}
          </div>


          <div
            v-if="voiceCommand"
            class="voice-command"
          >
            Lệnh thực hiện:

            <strong>
              {{ voiceCommand }}
            </strong>

          </div>

        </div>


        <!-- NÚT -->

        <div class="voice-actions">

          <el-button
            type="primary"
            size="large"
            :loading="
              voiceListening
              ||
              voiceProcessing
            "
            :disabled="
              voiceListening
              ||
              voiceProcessing
            "
            @click="listenVoice"
          >
            {{
              voiceListening
                ? "Đang nghe..."
                : voiceProcessing
                  ? "Đang xử lý..."
                  : "🎤 Bắt đầu nghe"
            }}
          </el-button>


          <el-button
            type="danger"
            size="large"
            @click="closeVoice"
          >
            Đóng
          </el-button>

        </div>

      </div>

    </el-dialog>

  </div>
</template>


<script setup>

import {
  computed,
  ref
} from "vue";


import {
  ElMessage
} from "element-plus";


import {
  useDeviceStore
} from "../stores/devices";


import {
  startAi,
  stopAi,
  recognizeVoice
} from "../services/aiApi";


import {
  recordVoice
} from "../utils/voiceRecorder.js";


// =================================================
// STORE
// =================================================

const store =
  useDeviceStore();


// =================================================
// VOICE STATE
// =================================================

const voiceDialog =
  ref(false);


const voiceListening =
  ref(false);


const voiceProcessing =
  ref(false);


const voiceText =
  ref("");


const voiceCommand =
  ref("");


// =================================================
// LẤY AI COMMAND GẦN NHẤT
// =================================================

const lastGesture =
computed(() =>

  store.aiCommands.find(
    item =>
      item.source === "gesture"
  )

);


const lastVoice =
computed(() =>

  store.aiCommands.find(
    item =>
      item.source === "voice"
  )

);


const lastFace =
computed(() =>

  store.aiCommands.find(
    item =>
      item.source === "face"
  )

);


// =================================================
// KIỂM TRA AI ONLINE
// =================================================

const anyAiOnline =
computed(() =>

  store.aiStatus.gesture
  ||
  store.aiStatus.voice
  ||
  store.aiStatus.face

);


// =================================================
// CHẠY GESTURE / FACE
// =================================================

async function startMode(mode) {

  try {

    const result =
      await startAi(mode);


    if (result.success) {

      // cập nhật trước để giao diện phản hồi ngay
      if (
        mode === "gesture"
        ||
        mode === "face"
      ) {

        store.aiStatus[mode] =
          true;

      }


      ElMessage.success(
        `Đã khởi động AI ${mode}`
      );

    } else {

      ElMessage.error(
        result.message
      );

    }

  } catch (error) {

    console.error(
      error
    );


    ElMessage.error(
      "Không kết nối được AI Manager"
    );

  }

}


// =================================================
// DỪNG GESTURE / FACE
// =================================================

async function stopMode(mode) {

  try {

    const result =
      await stopAi(mode);


    if (result.success) {

      if (
        mode === "gesture"
        ||
        mode === "face"
      ) {

        store.aiStatus[mode] =
          false;

      }


      ElMessage.success(
        `Đã dừng AI ${mode}`
      );

    } else {

      ElMessage.error(
        result.message
      );

    }

  } catch (error) {

    console.error(
      error
    );


    ElMessage.error(
      "Không kết nối được AI Manager"
    );

  }

}


// =================================================
// MỞ VOICE AI
// Đây là hàm em lỡ xóa
// =================================================

async function openVoice() {

  try {

    const result =
      await startAi(
        "voice"
      );


    if (!result.success) {

      ElMessage.error(
        result.message
      );

      return;

    }


    // cập nhật ONLINE ngay
    store.aiStatus.voice =
      true;


    // mở cửa sổ
    voiceDialog.value =
      true;


    // reset kết quả cũ
    voiceText.value =
      "Voice AI đã sẵn sàng";


    voiceCommand.value =
      "";


    ElMessage.success(
      "Đã bật AI giọng nói"
    );

  } catch (error) {

    console.error(
      error
    );


    ElMessage.error(
      "Không kết nối được AI Manager"
    );

  }

}


// =================================================
// DỪNG VOICE AI
// =================================================

async function stopVoice() {

  try {

    const result =
      await stopAi(
        "voice"
      );


    if (result.success) {

      store.aiStatus.voice =
        false;


      voiceDialog.value =
        false;


      voiceListening.value =
        false;


      voiceProcessing.value =
        false;


      ElMessage.success(
        "Đã dừng AI giọng nói"
      );

    } else {

      ElMessage.error(
        result.message
      );

    }

  } catch (error) {

    console.error(
      error
    );


    ElMessage.error(
      "Không kết nối được AI Manager"
    );

  }

}


// =================================================
// ĐÓNG CỬA SỔ
// Không tắt AI
// =================================================

function closeVoice() {

  voiceDialog.value =
    false;

}


// =================================================
// NGHE GIỌNG NÓI
// =================================================

async function listenVoice() {

  // AI chưa chạy
  if (
    !store.aiStatus.voice
  ) {

    ElMessage.warning(
      "Voice AI chưa được bật"
    );

    return;

  }


  // đang chạy thì không bấm lần nữa
  if (
    voiceListening.value
    ||
    voiceProcessing.value
  ) {

    return;

  }


  try {

    // =========================================
    // 1. THU ÂM
    // =========================================

    voiceListening.value =
      true;


    voiceProcessing.value =
      false;


    voiceText.value =
      "Đang nghe trong 4 giây...";


    voiceCommand.value =
      "";


    const audioBlob =
      await recordVoice(4);


    // =========================================
    // 2. XỬ LÝ
    // =========================================

    voiceListening.value =
      false;


    voiceProcessing.value =
      true;


    voiceText.value =
      "Đang nhận dạng giọng nói...";


    // gửi WAV → Flask
    const result =
      await recognizeVoice(
        audioBlob
      );


    voiceProcessing.value =
      false;


    // =========================================
    // 3. BACKEND BÁO LỖI
    // =========================================

    if (!result.success) {

      voiceText.value =
        result.message
        ||
        "Không nhận dạng được";


      voiceCommand.value =
        "";


      ElMessage.warning(
        voiceText.value
      );


      return;

    }


    // =========================================
    // 4. KẾT QUẢ PHOWHISPER
    // =========================================

    voiceText.value =
      result.text
      ||
      "Không nghe được nội dung";


    // =========================================
    // 5. LỆNH QWEN
    // =========================================

    voiceCommand.value =
      formatCommand(
        result.command
      );


    ElMessage.success(
      "Nhận dạng giọng nói thành công"
    );

  } catch (error) {

    console.error(
      "Voice error:",
      error
    );


    voiceListening.value =
      false;


    voiceProcessing.value =
      false;


    voiceText.value =
      "Không thể nhận dạng giọng nói";


    voiceCommand.value =
      "";


    ElMessage.error(
      "Có lỗi khi thu hoặc nhận dạng giọng nói"
    );

  }

}


// =================================================
// CONFIDENCE
// =================================================

function confidencePercent(value) {

  if (
    value === undefined
    ||
    value === null
  ) {

    return 0;

  }


  const number =
    Number(value);


  if (
    Number.isNaN(number)
  ) {

    return 0;

  }


  if (
    number > 1
  ) {

    return Math.round(
      number
    );

  }


  return Math.round(
    number * 100
  );

}


// =================================================
// HIỂN THỊ LỆNH
// =================================================

function formatCommand(command) {

  if (
    !command
    ||
    Object.keys(command).length === 0
  ) {

    return "--";

  }


  if (command.relay) {

    return command.relay === "ON"
      ? "Bật Relay"
      : "Tắt Relay";

  }


  if (command.led) {

    return command.led === "ON"
      ? "Bật đèn LED"
      : "Tắt đèn LED";

  }


  if (command.mode) {

    return command.mode === "AUTO"
      ? "Bật chế độ AUTO"
      : "Bật chế độ MANUAL";

  }


  return JSON.stringify(
    command
  );

}

</script>


<style scoped>

/* ================================================= */
/* TRANG */
/* ================================================= */

.ai-page {
  padding: 4px;
}


/* ================================================= */
/* HEADER */
/* ================================================= */

.title-row {

  display: flex;

  justify-content:
    space-between;

  align-items: center;

  margin-bottom:
    22px;

}


.title-row h2 {
  margin: 0;
}


.title-row p {

  margin-top:
    6px;

  margin-bottom:
    0;

  color:
    #777;

}


/* ================================================= */
/* CARD */
/* ================================================= */

.ai-card {

  text-align:
    center;

  min-height:
    400px;

}


.ai-icon {

  font-size:
    50px;

  margin-bottom:
    8px;

}


.ai-card h3 {

  margin-top:
    5px;

}


/* ================================================= */
/* BUTTON */
/* ================================================= */

.buttons {

  margin-top:
    18px;

  display:
    flex;

  justify-content:
    center;

  gap:
    8px;

}


/* ================================================= */
/* RESULT */
/* ================================================= */

.result-label {

  color:
    #888;

  font-size:
    14px;

  margin-bottom:
    7px;

}


.result-value {

  font-size:
    20px;

  font-weight:
    bold;

  min-height:
    55px;

  display:
    flex;

  justify-content:
    center;

  align-items:
    center;

  word-break:
    break-word;

  padding:
    0 10px;

}


.command {

  margin:
    12px 0;

  font-weight:
    bold;

}


/* ================================================= */
/* HISTORY */
/* ================================================= */

.history-card {

  margin-top:
    20px;

}


/* ================================================= */
/* VOICE DIALOG */
/* ================================================= */

.voice-window {

  text-align:
    center;

  padding:
    5px 15px 20px 15px;

}


.microphone {

  font-size:
    85px;

  margin:
    10px 0 15px 0;

  transition:
    transform 0.3s;

}


.microphone.listening {

  animation:
    pulse 0.7s infinite alternate;

}


@keyframes pulse {

  from {

    transform:
      scale(1);

  }

  to {

    transform:
      scale(1.2);

  }

}


.listening-text {

  color:
    #409eff;

}


.voice-help {

  color:
    #777;

  margin-top:
    12px;

}


.examples {

  margin-top:
    12px;

  display:
    flex;

  flex-wrap:
    wrap;

  justify-content:
    center;

  gap:
    8px;

}


.voice-result {

  padding:
    8px 15px;

}


.voice-text {

  font-size:
    22px;

  font-weight:
    bold;

  margin-top:
    10px;

  min-height:
    35px;

  word-break:
    break-word;

}


.voice-command {

  margin-top:
    18px;

  font-size:
    18px;

}


.voice-actions {

  margin-top:
    25px;

  display:
    flex;

  justify-content:
    center;

  gap:
    10px;

}

</style>