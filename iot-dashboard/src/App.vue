<template>

  <el-container style="height: 100vh">

    <!-- SIDEBAR -->
    <el-aside
      width="220px"
      style="background: #1f2d3d"
    >

      <h3
        style="
          color: white;
          text-align: center;
          padding: 20px 0;
        "
      >
        IoT Manager
      </h3>

      <el-menu
        :default-active="$route.path"
        router
        background-color="#1f2d3d"
        text-color="#ccc"
        active-text-color="#fff"
      >

        <el-menu-item index="/">
          Tổng quan
        </el-menu-item>

        <el-menu-item index="/devices">
          Thiết bị
        </el-menu-item>
        <el-menu-item index="/ai">
  AI Nhận dạng
</el-menu-item>

        <el-menu-item index="/alerts">
          Cảnh báo
        </el-menu-item>

        <el-menu-item index="/settings">
          Cài đặt
        </el-menu-item>

      </el-menu>

    </el-aside>


    <!-- PHẦN BÊN PHẢI -->
    <el-container>

      <!-- HEADER -->
      <el-header
        style="
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-bottom: 1px solid #ddd;
        "
      >

        <span>
          Hệ thống giám sát IoT
          - DHT11 / Relay / LED
        </span>

        <el-tag
          :type="
            connected
              ? 'success'
              : 'danger'
          "
        >

          {{
            connected
              ? "Đã kết nối broker"
              : "Mất kết nối broker"
          }}

        </el-tag>

      </el-header>


      <!-- NỘI DUNG -->
      <el-main
        style="background: #f5f7fa"
      >

        <router-view />

      </el-main>

    </el-container>

  </el-container>

</template>


<script setup>

import {
  onMounted,
  onUnmounted,
  watch
} from "vue";

import {
  ElNotification
} from "element-plus";

import {
  connectMqtt,
  connected
} from "./composables/useMqtt";

import {
  useDeviceStore
} from "./stores/devices";


const store = useDeviceStore();

let timer = null;


// Khi mở web
onMounted(() => {

  connectMqtt();

  // watchdog mỗi 1 giây
  timer = setInterval(() => {

    store.checkTimeouts();

  }, 1000);

});


// Khi đóng component
onUnmounted(() => {

  clearInterval(timer);

});


// Hiện thông báo khi có cảnh báo mới
watch(
  () => store.alerts.length,

  (moi, cu) => {

    if (moi > cu) {

      const a =
        store.alerts[0];

      ElNotification({

        title:
          a.deviceId,

        message:
          a.message,

        type:
          a.level === "error"
            ? "error"
            : "warning",

        duration: 4000

      });

    }

  }
);

</script>