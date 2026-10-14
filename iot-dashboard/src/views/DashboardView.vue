<template>
  <h2>Tổng quan</h2>

  <el-row :gutter="16">

    <el-col :span="6">
      <el-card>
        <div>Thiết bị online</div>

        <div style="font-size:28px;font-weight:bold;margin-top:8px">
          {{ store.onlineCount }}/{{ store.list.length }}
        </div>
      </el-card>
    </el-col>

    <el-col :span="6">
      <el-card>
        <div>Nhiệt độ trung bình</div>

        <div style="font-size:28px;font-weight:bold;margin-top:8px">
          {{ store.avgTemp }} °C
        </div>
      </el-card>
    </el-col>

    <el-col :span="6">
      <el-card>
        <div>Số cảnh báo</div>

        <div style="font-size:28px;font-weight:bold;margin-top:8px">
          {{ store.alerts.length }}
        </div>
      </el-card>
    </el-col>

    <el-col :span="6">
      <el-card>
        <div>AI Service</div>

        <div style="font-size:28px;font-weight:bold;margin-top:8px">
          {{ store.aiStatus.gesture ||
store.aiStatus.voice ||
store.aiStatus.face ? "Đang chạy" : "Đã dừng" }}
        </div>
      </el-card>
    </el-col>

  </el-row>


  <el-card
    header="Nhiệt độ / Độ ẩm theo thời gian thực"
    style="margin-top:16px"
  >

    <v-chart
      style="height:320px"
      :option="chartOption"
      autoresize
    />

  </el-card>


  <AiPanel />

</template>


<script setup>

import { computed } from "vue";

import VChart from "vue-echarts";

import { use } from "echarts/core";

import {
  LineChart
} from "echarts/charts";

import {
  GridComponent,
  TooltipComponent,
  LegendComponent
} from "echarts/components";

import {
  CanvasRenderer
} from "echarts/renderers";

import {
  useDeviceStore
} from "../stores/devices";

import AiPanel
  from "../components/AiPanel.vue";


use([
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  CanvasRenderer
]);


const store =
  useDeviceStore();


const chartOption =
computed(() => {

  const history =
    store.list[0]?.history ?? [];

  return {

    tooltip: {
      trigger: "axis"
    },

    legend: {
      data: [
        "Nhiệt độ",
        "Độ ẩm"
      ]
    },

    xAxis: {
      type: "category",

      data:
        history.map(
          item =>
            new Date(
              item.t
            )
            .toLocaleTimeString()
        )
    },

    yAxis: [

      {
        type: "value",
        name: "°C"
      },

      {
        type: "value",
        name: "%"
      }

    ],

    series: [

      {
        name:
          "Nhiệt độ",

        type:
          "line",

        smooth:
          true,

        data:
          history.map(
            item =>
              item.temp
          )
      },

      {
        name:
          "Độ ẩm",

        type:
          "line",

        smooth:
          true,

        yAxisIndex:
          1,

        data:
          history.map(
            item =>
              item.hum
          )
      }

    ]

  };

});

</script>