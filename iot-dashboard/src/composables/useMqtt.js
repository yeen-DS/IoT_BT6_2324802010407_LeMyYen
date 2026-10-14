import mqtt from "mqtt";
import { ref } from "vue";
import { useDeviceStore } from "../stores/devices";

export const brokerUrl = ref(
  localStorage.getItem("brokerUrl") ||
  "ws://192.168.100.148:8083/mqtt"
);

export const connected = ref(false);

let client = null;


// ======================================
// KẾT NỐI MQTT
// ======================================
export function connectMqtt(force = false) {

  const store = useDeviceStore();

  // Nếu yêu cầu kết nối lại
  if (force && client) {

    try {
      client.end(true);
    } catch (error) {
      console.log(error);
    }

    client = null;
    connected.value = false;
  }

  // Nếu đã có client thì không tạo lại
  if (client) {
    return client;
  }

  // Lưu broker vào trình duyệt
  localStorage.setItem(
    "brokerUrl",
    brokerUrl.value
  );


  // ======================================
  // TẠO MQTT CLIENT
  // ======================================
  client = mqtt.connect(
    brokerUrl.value,
    {

      clientId:
        "dashboard-" +
        Math.random()
          .toString(16)
          .slice(2, 8),

      keepalive: 15,

      reconnectPeriod: 2000,

      connectTimeout: 10000,

      clean: true
    }
  );


  // ======================================
  // KẾT NỐI THÀNH CÔNG
  // ======================================
  client.on(
    "connect",
    () => {

      console.log(
        "Dashboard da ket noi MQTT"
      );

      connected.value = true;


      // Subscribe các topic
      client.subscribe([
        "devices/+/telemetry",
        "devices/+/status",
        "devices/+/info",

        "ai/command",

        // trạng thái AI chung
        "ai/status",

        // trạng thái từng AI
        "ai/status/+"
      ]);

    }
  );


  // ======================================
  // MẤT KẾT NỐI
  // ======================================
  client.on(
    "close",
    () => {

      connected.value = false;

    }
  );


  client.on(
    "offline",
    () => {

      connected.value = false;

    }
  );


  // ======================================
  // ĐANG KẾT NỐI LẠI
  // ======================================
  client.on(
    "reconnect",
    () => {

      connected.value = false;

      console.log(
        "Dang ket noi lai MQTT..."
      );

    }
  );


  // ======================================
  // LỖI MQTT
  // ======================================
  client.on(
    "error",
    (error) => {

      console.error(
        "MQTT Error:",
        error.message
      );

    }
  );


  // ======================================
  // NHẬN MESSAGE MQTT
  // ======================================
  client.on(
    "message",
    (topic, payload) => {

      const message =
        payload.toString();


      console.log(
        "MQTT:",
        topic,
        message
      );


      const parts =
        topic.split("/");


      try {

        // ==================================
        // MESSAGE TỪ ESP32
        // ==================================
        if (
          parts[0] === "devices"
        ) {

          const id =
            parts[1];

          const kind =
            parts[2];


          // -------------------------------
          // TELEMETRY
          // -------------------------------
          if (
            kind === "telemetry"
          ) {

            const data =
              JSON.parse(message);

            store.updateTelemetry(
              id,
              data
            );

          }


          // -------------------------------
          // STATUS
          // -------------------------------
          if (
            kind === "status"
          ) {

            store.updateStatus(
              id,
              message
            );

          }


          // -------------------------------
          // INFO
          // -------------------------------
          if (
            kind === "info"
          ) {

            const data =
              JSON.parse(message);

            store.updateInfo(
              id,
              data
            );

          }

        }


        // ==================================
        // AI COMMAND
        // ==================================
        if (
          topic === "ai/command"
        ) {

          const data =
            JSON.parse(message);

          store.pushAiCommand(
            data
          );

        }


        // ==================================
        // AI STATUS CHUNG
        // ==================================
        if (
          topic === "ai/status"
        ) {

          store.aiOnline =
            message === "online";

        }


        // ==================================
        // AI STATUS RIÊNG
        // ai/status/gesture
        // ai/status/voice
        // ai/status/face
        // ==================================
        if (
          topic.startsWith(
            "ai/status/"
          )
        ) {

          const mode =
            parts[2];


          if (
            [
              "gesture",
              "voice",
              "face"
            ].includes(mode)
          ) {

            store.aiStatus[mode] =
              message === "online";

          }

        }


      } catch (error) {

        console.error(
          "Payload MQTT loi:",
          error
        );

      }

    }
  );


  return client;
}


// ======================================
// KẾT NỐI LẠI BROKER
// ======================================
export function reconnectMqtt() {

  connectMqtt(true);

}


// ======================================
// GỬI LỆNH XUỐNG ESP32
// ======================================
export function sendCommand(
  deviceId,
  payload
) {

  if (
    !client ||
    !connected.value
  ) {

    console.log(
      "MQTT chua ket noi"
    );

    return false;
  }


  const topic =
    `devices/${deviceId}/cmd`;


  client.publish(
    topic,
    JSON.stringify(payload),
    {
      qos: 1
    }
  );


  console.log(
    "Gui lenh:",
    topic,
    payload
  );


  return true;
}