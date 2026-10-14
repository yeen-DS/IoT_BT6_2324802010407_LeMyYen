export async function recordVoice(
  seconds = 4
) {

  const stream =
    await navigator.mediaDevices
      .getUserMedia({
        audio: true
      });


  const context =
    new AudioContext();


  const source =
    context.createMediaStreamSource(
      stream
    );


  const processor =
    context.createScriptProcessor(
      4096,
      1,
      1
    );


  const samples = [];


  processor.onaudioprocess =
    event => {

      const input =
        event.inputBuffer
          .getChannelData(0);

      samples.push(
        new Float32Array(input)
      );

    };


  source.connect(
    processor
  );


  processor.connect(
    context.destination
  );


  await new Promise(
    resolve =>
      setTimeout(
        resolve,
        seconds * 1000
      )
  );


  processor.disconnect();

  source.disconnect();


  stream
    .getTracks()
    .forEach(
      track =>
        track.stop()
    );


  const length =
    samples.reduce(
      (total, item) =>
        total + item.length,
      0
    );


  const merged =
    new Float32Array(
      length
    );


  let offset = 0;


  for (
    const sample
    of samples
  ) {

    merged.set(
      sample,
      offset
    );

    offset +=
      sample.length;

  }


  const blob =
    encodeWav(
      merged,
      context.sampleRate
    );


  await context.close();


  return blob;
}


// ==========================================
// FLOAT32 → WAV PCM 16 BIT
// ==========================================

function encodeWav(
  samples,
  sampleRate
) {

  const buffer =
    new ArrayBuffer(
      44 +
      samples.length * 2
    );


  const view =
    new DataView(
      buffer
    );


  writeString(
    view,
    0,
    "RIFF"
  );


  view.setUint32(
    4,
    36 +
    samples.length * 2,
    true
  );


  writeString(
    view,
    8,
    "WAVE"
  );


  writeString(
    view,
    12,
    "fmt "
  );


  view.setUint32(
    16,
    16,
    true
  );


  view.setUint16(
    20,
    1,
    true
  );


  view.setUint16(
    22,
    1,
    true
  );


  view.setUint32(
    24,
    sampleRate,
    true
  );


  view.setUint32(
    28,
    sampleRate * 2,
    true
  );


  view.setUint16(
    32,
    2,
    true
  );


  view.setUint16(
    34,
    16,
    true
  );


  writeString(
    view,
    36,
    "data"
  );


  view.setUint32(
    40,
    samples.length * 2,
    true
  );


  let position = 44;


  for (
    let i = 0;
    i < samples.length;
    i++
  ) {

    let sample =
      Math.max(
        -1,
        Math.min(
          1,
          samples[i]
        )
      );


    sample =
      sample < 0
        ? sample * 32768
        : sample * 32767;


    view.setInt16(
      position,
      sample,
      true
    );


    position += 2;

  }


  return new Blob(
    [view],
    {
      type: "audio/wav"
    }
  );

}


function writeString(
  view,
  offset,
  string
) {

  for (
    let i = 0;
    i < string.length;
    i++
  ) {

    view.setUint8(
      offset + i,
      string.charCodeAt(i)
    );

  }

}