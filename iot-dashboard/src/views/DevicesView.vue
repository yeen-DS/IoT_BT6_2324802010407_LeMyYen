<template>

  <h2>Thiết bị</h2>

  <el-card header="Danh sách thiết bị">

    <el-table
      :data="store.list"
      style="width:100%"
    >

      <el-table-column
        prop="id"
        label="Mã thiết bị"
        width="120"
      />


      <el-table-column
        prop="name"
        label="Tên thiết bị"
        width="200"
      />


      <el-table-column
        label="Trạng thái"
        width="130"
      >

        <template #default="{ row }">

          <el-tag
            :type="
              row.online
                ? 'success'
                : 'danger'
            "
          >

            {{
              row.online
                ? "Đang kết nối"
                : "Mất kết nối"
            }}

          </el-tag>

        </template>

      </el-table-column>


      <el-table-column
        label="Nhiệt độ"
        width="100"
      >

        <template #default="{ row }">

          {{ row.temp ?? "--" }} °C

        </template>

      </el-table-column>


      <el-table-column
        label="Độ ẩm"
        width="100"
      >

        <template #default="{ row }">

          {{ row.hum ?? "--" }} %

        </template>

      </el-table-column>


      <el-table-column
        label="Relay"
        width="100"
      >

        <template #default="{ row }">

          <el-switch

            :model-value="
              row.relay === 'ON'
            "

            :disabled="
              !row.online
            "

            @change="
              value =>
                sendCommand(
                  row.id,
                  {
                    relay:
                      value
                        ? 'ON'
                        : 'OFF'
                  }
                )
            "
          />

        </template>

      </el-table-column>


      <el-table-column
        label="LED"
        width="100"
      >

        <template #default="{ row }">

          <el-switch

            :model-value="
              row.led === 'ON'
            "

            :disabled="
              !row.online
            "

            @change="
              value =>
                sendCommand(
                  row.id,
                  {
                    led:
                      value
                        ? 'ON'
                        : 'OFF'
                  }
                )
            "
          />

        </template>

      </el-table-column>


      <el-table-column
        prop="mode"
        label="Chế độ"
        width="100"
      />


      <el-table-column
        label="RSSI"
        width="100"
      >

        <template #default="{ row }">

          {{ row.rssi ?? "--" }}
          dBm

        </template>

      </el-table-column>


      <el-table-column
        label="Uptime"
        width="110"
      >

        <template #default="{ row }">

          {{ row.uptime ?? 0 }} s

        </template>

      </el-table-column>


      <el-table-column
        label="Cập nhật cuối"
      >

        <template #default="{ row }">

          {{
            row.lastSeen
              ?
              new Date(
                row.lastSeen
              )
              .toLocaleTimeString()
              :
              "--"
          }}

        </template>

      </el-table-column>

    </el-table>

  </el-card>

</template>


<script setup>

import {
  useDeviceStore
} from "../stores/devices";

import {
  sendCommand
} from "../composables/useMqtt";


const store =
  useDeviceStore();

</script>