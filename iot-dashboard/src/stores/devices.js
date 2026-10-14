import {
  defineStore
} from "pinia";


// Nếu quá 8 giây
// không có telemetry
// => OFFLINE
const OFFLINE_TIMEOUT = 8000;


export const useDeviceStore =
  defineStore(
    "devices",
    {

      // ========================
      // STATE
      // ========================
      state: () => ({

        devices: {},

        alerts: [],

        aiCommands: [],

        aiOnline: false,

aiStatus: {

  gesture: false,

  voice: false,

  face: false

},

        tempThreshold:
          Number(
            localStorage.getItem(
              "tempThreshold"
            ) || 37
          )

      }),


      // ========================
      // GETTER
      // ========================
      getters: {

        // Danh sách thiết bị
        list: (state) => {

          return Object.values(
            state.devices
          );

        },


        // Số thiết bị online
        onlineCount: (state) => {

          return Object.values(
            state.devices
          )
          .filter(
            device =>
              device.online
          )
          .length;

        },


        // Nhiệt độ trung bình
        avgTemp: (state) => {

          const onlineDevices =
            Object.values(
              state.devices
            )
            .filter(
              device =>
                device.online &&
                device.temp != null
            );


          if (
            onlineDevices.length === 0
          ) {

            return "--";

          }


          const total =
            onlineDevices.reduce(
              (sum, device) => {

                return (
                  sum +
                  Number(
                    device.temp
                  )
                );

              },
              0
            );


          return (
            total /
            onlineDevices.length
          ).toFixed(1);

        }

      },


      // ========================
      // ACTIONS
      // ========================
      actions: {

        // ----------------------
        // TẠO DEVICE NẾU CHƯA CÓ
        // ----------------------
        ensure(id) {

          if (
            !this.devices[id]
          ) {

            this.devices[id] = {

              id: id,

              name: id,

              fw: "--",

              ip: "--",

              online: false,

              temp: null,

              hum: null,

              relay: "OFF",

              led: "OFF",

              mode: "MANUAL",

              rssi: null,

              uptime: 0,

              lastSeen: 0,

              history: []

            };

          }

          return this.devices[id];

        },


        // ----------------------
        // TELEMETRY
        // ----------------------
        updateTelemetry(
          id,
          data
        ) {

          const device =
            this.ensure(id);


          Object.assign(
            device,
            data,
            {

              online: true,

              lastSeen:
                Date.now()

            }
          );


          // Lưu lịch sử biểu đồ
          device.history.push({

            t: Date.now(),

            temp:
              Number(
                data.temp
              ),

            hum:
              Number(
                data.hum
              )

          });


          // Chỉ giữ 120 điểm
          if (
            device.history.length
            > 120
          ) {

            device.history.shift();

          }


          // -------------------
          // CẢNH BÁO NHIỆT ĐỘ
          // -------------------
          if (
            Number(
              data.temp
            )
            >=
            this.tempThreshold
          ) {

            const message =
              `Nhiet do ${data.temp} do C vuot nguong ${this.tempThreshold} do C`;


            const last =
              this.alerts[0];


            // tránh spam cảnh báo
            if (
              !last ||
              last.deviceId !== id ||
              last.message !== message ||
              Date.now() -
                last.timestamp
              > 10000
            ) {

              this.addAlert(
                "warning",
                id,
                message
              );

            }

          }

        },


        // ----------------------
        // STATUS
        // ----------------------
        updateStatus(
          id,
          status
        ) {

          const device =
            this.ensure(id);


          const online =
            status === "online";


          if (
            device.online &&
            !online
          ) {

            this.addAlert(
              "error",
              id,
              "Thiet bi mat ket noi"
            );

          }


          device.online =
            online;


          if (online) {

            device.lastSeen =
              Date.now();

          }

        },


        // ----------------------
        // DEVICE INFO
        // ----------------------
        updateInfo(
          id,
          info
        ) {

          Object.assign(
            this.ensure(id),
            info
          );

        },


        // ----------------------
        // THÊM CẢNH BÁO
        // ----------------------
        addAlert(
          level,
          deviceId,
          message
        ) {

          const timestamp =
            Date.now();


          this.alerts.unshift({

            level:

              level,

            deviceId:
              deviceId,

            message:
              message,

            timestamp:
              timestamp,

            time:
              new Date(
                timestamp
              )
              .toLocaleString()

          });


          // Giữ tối đa 200
          if (
            this.alerts.length
            > 200
          ) {

            this.alerts.pop();

          }

        },


        // ----------------------
        // AI COMMAND
        // ----------------------
        pushAiCommand(
          command
        ) {

          this.aiCommands.unshift({

            ...command,

            time:
              new Date()
              .toLocaleTimeString()

          });


          if (
            this.aiCommands.length
            > 50
          ) {

            this.aiCommands.pop();

          }

        },


        // ----------------------
        // WATCHDOG
        // ----------------------
        checkTimeouts() {

          const now =
            Date.now();


          for (
            const device
            of Object.values(
              this.devices
            )
          ) {

            if (
              device.online &&
              device.lastSeen &&
              now -
                device.lastSeen
              >
              OFFLINE_TIMEOUT
            ) {

              device.online =
                false;


              this.addAlert(
                "error",
                device.id,
                "Mat ket noi - qua 8 giay khong co du lieu"
              );

            }

          }

        },


        // ----------------------
        // LƯU NGƯỠNG
        // ----------------------
        saveThreshold() {

          localStorage.setItem(
            "tempThreshold",
            this.tempThreshold
          );

        }

      }

    }
  );