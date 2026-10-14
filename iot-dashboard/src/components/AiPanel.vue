<template>

  <el-card
    style="margin-top:16px"
  >

    <template #header>

      Điều khiển bằng AI

      <el-tag

        :type="
          store.aiOnline
            ? 'success'
            : 'info'
        "

        style="
          margin-left:8px
        "
      >

        {{
          store.aiOnline
            ? "AI service đang chạy"
            : "AI service đã dừng"
        }}

      </el-tag>

    </template>


    <el-empty

      v-if="
        !store.aiCommands.length
      "

      description="
        Chưa có lệnh AI
      "

    />


    <el-timeline
      v-else
    >

      <el-timeline-item

        v-for="
          (command,index)
          in
          store.aiCommands.slice(
            0,
            8
          )
        "

        :key="
          index
        "

        :timestamp="
          command.time
        "
      >


        <b>

          {{
            command.label
          }}

        </b>


        <el-tag
          size="small"
          style="
            margin-left:8px
          "
        >

          {{
            command.source
          }}

        </el-tag>


        <div
          style="
            margin-top:5px;
            color:#888
          "
        >

          {{
            JSON.stringify(
              command.command
            )
          }}

          — độ tin cậy

          {{
            command.confidence
          }}

        </div>


      </el-timeline-item>

    </el-timeline>

  </el-card>

</template>


<script setup>

import {
  useDeviceStore
} from "../stores/devices";

const store =
  useDeviceStore();

</script>