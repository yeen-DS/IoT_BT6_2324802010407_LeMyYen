<template>

  <h2>Cảnh báo</h2>

  <el-card
    header="Lịch sử cảnh báo"
  >

    <el-table
      :data="store.alerts"
      height="520"
    >

      <el-table-column
        prop="time"
        label="Thời gian"
        width="200"
      />


      <el-table-column
        prop="deviceId"
        label="Thiết bị"
        width="140"
      />


      <el-table-column
        label="Mức độ"
        width="130"
      >

        <template #default="{ row }">

          <el-tag
            :type="
              row.level === 'error'
                ? 'danger'
                : 'warning'
            "
          >

            {{
              row.level === "error"
                ? "Nghiêm trọng"
                : "Cảnh báo"
            }}

          </el-tag>

        </template>

      </el-table-column>


      <el-table-column
        prop="message"
        label="Nội dung"
      />

    </el-table>

  </el-card>

</template>


<script setup>

import {
  useDeviceStore
} from "../stores/devices";

const store =
  useDeviceStore();

</script>