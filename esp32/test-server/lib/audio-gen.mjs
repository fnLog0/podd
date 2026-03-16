// WAV tone generator for TTS mock responses

export function wavTone({ seconds = 1.5, sampleRate = 16000, frequency = 440, amplitude = 0.3 } = {}) {
  const totalSamples = Math.floor(seconds * sampleRate);
  const channels = 1;
  const bitsPerSample = 16;
  const bytesPerSample = bitsPerSample / 8;
  const dataSize = totalSamples * channels * bytesPerSample;
  const buffer = Buffer.alloc(44 + dataSize);

  buffer.write('RIFF', 0);
  buffer.writeUInt32LE(36 + dataSize, 4);
  buffer.write('WAVE', 8);
  buffer.write('fmt ', 12);
  buffer.writeUInt32LE(16, 16);
  buffer.writeUInt16LE(1, 20);
  buffer.writeUInt16LE(channels, 22);
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(sampleRate * channels * bytesPerSample, 28);
  buffer.writeUInt16LE(channels * bytesPerSample, 32);
  buffer.writeUInt16LE(bitsPerSample, 34);
  buffer.write('data', 36);
  buffer.writeUInt32LE(dataSize, 40);

  for (let i = 0; i < totalSamples; i++) {
    const sample = Math.sin((2 * Math.PI * frequency * i) / sampleRate);
    const value = Math.max(-1, Math.min(1, sample * amplitude));
    buffer.writeInt16LE(Math.round(value * 32767), 44 + i * bytesPerSample);
  }

  return buffer;
}
