<template>

  <h2>Cài đặt</h2>


  <el-card
    header="Cấu hình hệ thống"
    style="max-width:650px"
  >

    <el-form
      label-width="200px"
    >


      <!-- =============================== -->
      <!-- BROKER -->
      <!-- =============================== -->

      <el-form-item
        label="Địa chỉ Broker"
      >

        <el-input
          v-model="brokerUrl"
        />

      </el-form-item>


      <!-- =============================== -->
      <!-- NGƯỠNG -->
      <!-- =============================== -->

      <el-form-item
        label="Ngưỡng nhiệt độ"
      >

        <el-input-number
          v-model="store.tempThreshold"
          :min="20"
          :max="60"
          :step="1"
        />

        <span
          style="margin-left:8px"
        >
          °C
        </span>

      </el-form-item>


      <!-- =============================== -->
      <!-- CHẾ ĐỘ -->
      <!-- =============================== -->

      <el-form-item
        label="Chế độ thiết bị"
      >

        <!-- AUTO -->
        <el-button
          type="primary"
          @click="setAuto"
        >
          Bật AUTO
        </el-button>


        <!-- MANUAL -->
        <el-button
          @click="setManual"
        >
          MANUAL
        </el-button>

      </el-form-item>


      <!-- =============================== -->
      <!-- CÁC NÚT KHÁC -->
      <!-- =============================== -->

      <el-form-item>

        <el-button
          type="success"
          @click="saveThreshold"
        >
          Lưu ngưỡng
        </el-button>


        <el-button
          type="warning"
          @click="reconnect"
        >
          Kết nối lại Broker
        </el-button>

      </el-form-item>


      <!-- =============================== -->
      <!-- GHI CHÚ -->
      <!-- =============================== -->

      <el-alert
        title="AUTO: nhiệt độ vượt ngưỡng sẽ bật LED và Relay"
        type="info"
        :closable="false"
        show-icon
      />

    </el-form>

  </el-card>

</template>


<script setup>

import {
  ElMessage
} from "element-plus";


import {
  useDeviceStore
} from "../stores/devices";


import {
  sendCommand,
  brokerUrl,
  reconnectMqtt
} from "../composables/useMqtt";


// ========================================
// STORE
// ========================================

const store =
  useDeviceStore();


// ========================================
// GỬI LỆNH CHO TẤT CẢ THIẾT BỊ
// ========================================

function applyToAll(
  payload
) {

  // Không có thiết bị
  if (
    !store.list
    ||
    store.list.length === 0
  ) {

    ElMessage.warning(
      "Chưa tìm thấy thiết bị"
    );

    return false;
  }


  store.list.forEach(
    device => {

      sendCommand(
        device.id,
        payload
      );

    }
  );


  return true;
}


// ========================================
// BẬT AUTO
//
// QUAN TRỌNG:
// gửi MODE + THRESHOLD cùng lúc
// ========================================

function setAuto() {

  const threshold =
    Number(
      store.tempThreshold
    );


  const success =
    applyToAll({

      mode: "AUTO",

      threshold: threshold

    });


  if (success) {

    // Lưu ngưỡng vào localStorage/store
    store.saveThreshold();


    ElMessage.success(
      `Đã bật AUTO - ngưỡng ${threshold}°C`
    );

  }

}


// ========================================
// BẬT MANUAL
// ========================================

function setManual() {

  const success =
    applyToAll({

      mode: "MANUAL"

    });


  if (success) {

    ElMessage.success(
      "Đã chuyển sang MANUAL"
    );

  }

}


// ========================================
// LƯU NGƯỠNG
// ========================================

function saveThreshold() {

  const threshold =
    Number(
      store.tempThreshold
    );


  // Lưu trong Dashboard
  store.saveThreshold();


  // Gửi ngưỡng xuống ESP32
  const success =
    applyToAll({

      threshold: threshold

    });


  if (success) {

    ElMessage.success(
      `Đã gửi ngưỡng ${threshold}°C xuống ESP32`
    );

  }

}


// ========================================
// KẾT NỐI LẠI BROKER
// ========================================

function reconnect() {

  localStorage.setItem(
    "brokerUrl",
    brokerUrl.value
  );


  reconnectMqtt();


  ElMessage.info(
    "Đang kết nối lại MQTT"
  );

}

</script>