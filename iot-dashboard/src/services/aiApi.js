const API =
  "http://localhost:5001/api";


// ==========================================
// START AI
// ==========================================

export async function startAi(mode) {

  const response =
    await fetch(
      `${API}/ai/start/${mode}`,
      {
        method: "POST"
      }
    );

  return await response.json();
}


// ==========================================
// STOP AI
// ==========================================

export async function stopAi(mode) {

  const response =
    await fetch(
      `${API}/ai/stop/${mode}`,
      {
        method: "POST"
      }
    );

  return await response.json();
}


// ==========================================
// GỬI FILE GIỌNG NÓI
// ==========================================

export async function recognizeVoice(
  audioBlob
) {

  const formData =
    new FormData();


  formData.append(
    "audio",
    audioBlob,
    "voice.wav"
  );


  const response =
    await fetch(
      `${API}/voice/recognize`,
      {
        method: "POST",
        body: formData
      }
    );


  return await response.json();
}