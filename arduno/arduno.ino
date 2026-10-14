#include <WiFiManager.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// ===========================
// 1. KHAI BÁO CHÂN
// ===========================
#define DHT_PIN 4
#define RELAY_PIN 5
#define LED_PIN 6
#define DHT_TYPE DHT11

// ===========================
// 2. THÔNG TIN THIẾT BỊ
// ===========================
const char* DEVICE_ID = "node-01";

// SỬA IP NÀY THÀNH IP LAPTOP CHẠY EMQX
const char* mqtt_server = "192.168.100.148";

const int mqtt_port = 1883;

// ===========================
// 3. TOPIC MQTT
// ===========================
char topicTelemetry[64];
char topicStatus[64];
char topicCmd[64];
char topicInfo[64];

// ===========================
// 4. ĐỐI TƯỢNG
// ===========================
DHT dht(DHT_PIN, DHT_TYPE);

WiFiClient espClient;
PubSubClient client(espClient);

// ===========================
// 5. TRẠNG THÁI
// ===========================
bool relayState = false;
bool ledState = false;
bool autoMode = false;

float tempThreshold = 37.0;

unsigned long lastSend = 0;

// ===========================
// 6. ĐIỀU KHIỂN RELAY + LED
// ===========================
void applyOutputs() {

  digitalWrite(
    RELAY_PIN,
    relayState ? HIGH : LOW
  );

  digitalWrite(
    LED_PIN,
    ledState ? HIGH : LOW
  );
}

// ===========================
// 7. NHẬN LỆNH MQTT
// ===========================
void callback(
  char* topic,
  byte* payload,
  unsigned int length
) {

  StaticJsonDocument<192> doc;

  DeserializationError error =
      deserializeJson(doc, payload, length);

  if (error) {

    Serial.println("JSON loi");

    return;
  }

  // ------------------------
  // RELAY
  // ------------------------
  if (doc.containsKey("relay")) {

    String value =
      doc["relay"].as<String>();

    relayState =
      (value == "ON");
  }

  // ------------------------
  // LED
  // ------------------------
  if (doc.containsKey("led")) {

    String value =
      doc["led"].as<String>();

    ledState =
      (value == "ON");
  }

  // ------------------------
  // MODE
  // ------------------------
  if (doc.containsKey("mode")) {

    String value =
      doc["mode"].as<String>();

    autoMode =
      (value == "AUTO");
  }

  // ------------------------
  // NGƯỠNG NHIỆT ĐỘ
  // ------------------------
  if (doc.containsKey("threshold")) {

    tempThreshold =
      doc["threshold"].as<float>();
  }

  applyOutputs();

  Serial.println("Nhan lenh MQTT");

  Serial.print("Relay: ");
  Serial.println(relayState);

  Serial.print("LED: ");
  Serial.println(ledState);

  Serial.print("AUTO: ");
  Serial.println(autoMode);

  Serial.print("Nguong: ");
  Serial.println(tempThreshold);
}

// ===========================
// 8. GỬI THÔNG TIN THIẾT BỊ
// ===========================
void publishInfo() {

  StaticJsonDocument<192> info;

  info["name"] =
    "Node cam bien phong thuc hanh";

  info["fw"] =
    "1.0.0";

  info["ip"] =
    WiFi.localIP().toString();

  char buffer[192];

  serializeJson(
    info,
    buffer
  );

  // Retained
  client.publish(
    topicInfo,
    buffer,
    true
  );
}

// ===========================
// 9. KẾT NỐI MQTT
// ===========================
void reconnectMQTT() {

  while (!client.connected()) {

    Serial.print(
      "Dang ket noi MQTT..."
    );

    // LWT:
    // nếu ESP32 mất kết nối bất thường
    // Broker tự gửi "offline"
    if (
      client.connect(
        DEVICE_ID,
        topicStatus,
        1,
        true,
        "offline"
      )
    ) {

      Serial.println("OK");

      // Gửi online
      client.publish(
        topicStatus,
        "online",
        true
      );

      // Gửi thông tin thiết bị
      publishInfo();

      // Subscribe lệnh
      client.subscribe(
        topicCmd,
        1
      );

    } else {

      Serial.print("Loi rc = ");

      Serial.println(
        client.state()
      );

      delay(2000);
    }
  }
}

// ===========================
// 10. SETUP
// ===========================
void setup() {

  Serial.begin(115200);

  // ------------------------
  // OUTPUT
  // ------------------------
  pinMode(
    RELAY_PIN,
    OUTPUT
  );

  pinMode(
    LED_PIN,
    OUTPUT
  );

  relayState = false;
  ledState = false;

  applyOutputs();

  // ------------------------
  // DHT11
  // ------------------------
  dht.begin();

  // ------------------------
  // TẠO TOPIC
  // ------------------------
  sprintf(
    topicTelemetry,
    "devices/%s/telemetry",
    DEVICE_ID
  );

  sprintf(
    topicStatus,
    "devices/%s/status",
    DEVICE_ID
  );

  sprintf(
    topicCmd,
    "devices/%s/cmd",
    DEVICE_ID
  );

  sprintf(
    topicInfo,
    "devices/%s/info",
    DEVICE_ID
  );

  // ------------------------
  // WIFI MANAGER
  // ------------------------
  WiFiManager wm;

  wm.autoConnect(
    "ESP32-IoT-Setup"
  );

  Serial.println(
    "WiFi da ket noi"
  );

  Serial.print(
    "IP ESP32: "
  );

  Serial.println(
    WiFi.localIP()
  );

  // ------------------------
  // MQTT
  // ------------------------
  client.setServer(
    mqtt_server,
    mqtt_port
  );

  client.setCallback(
    callback
  );

  // Keep Alive 10 giây
  client.setKeepAlive(10);

  client.setBufferSize(512);
}

// ===========================
// 11. LOOP
// ===========================
void loop() {

  // ------------------------
  // KẾT NỐI MQTT
  // ------------------------
  if (!client.connected()) {

    reconnectMQTT();
  }

  client.loop();

  // ------------------------
  // GỬI TELEMETRY
  // MỖI 2 GIÂY
  // ------------------------
  if (
    millis() - lastSend
    >= 2000
  ) {

    lastSend = millis();

    // ----------------------
    // ĐỌC DHT11
    // ----------------------
    float temperature =
      dht.readTemperature();

    float humidity =
      dht.readHumidity();

    if (
      isnan(temperature)
      ||
      isnan(humidity)
    ) {

      Serial.println(
        "Loi doc DHT11"
      );

      return;
    }

    // ======================
    // AUTO MODE
    // ======================
    if (autoMode) {

      if (
        temperature
        >= tempThreshold
      ) {

        relayState = true;
        ledState = true;

      } else {

        relayState = false;
        ledState = false;
      }

      applyOutputs();
    }

    // ======================
    // TẠO JSON
    // ======================
    StaticJsonDocument<256> doc;

    doc["temp"] =
      temperature;

    doc["hum"] =
      humidity;

    doc["relay"] =
      relayState
      ? "ON"
      : "OFF";

    doc["led"] =
      ledState
      ? "ON"
      : "OFF";

    doc["mode"] =
      autoMode
      ? "AUTO"
      : "MANUAL";

    doc["rssi"] =
      WiFi.RSSI();

    doc["uptime"] =
      millis() / 1000;

    char buffer[256];

    serializeJson(
      doc,
      buffer
    );

    // ======================
    // PUBLISH
    // ======================
    client.publish(
      topicTelemetry,
      buffer
    );

    Serial.print(
      "Telemetry: "
    );

    Serial.println(
      buffer
    );
  }
}