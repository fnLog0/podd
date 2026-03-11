import * as fs from "fs";
import * as path from "path";

async function main(): Promise<void> {
  const wavFile = path.join(process.cwd(), "test-files", "test-audio.wav");

  // Check if test audio exists, generate if not
  if (!fs.existsSync(wavFile)) {
    console.log("🎵 Test audio not found, generating...");
    await import("./generate-test-audio");
  }

  console.log(`✅ Bruno collection ready!`);
  console.log(`\n📁 Collection location: bru-no/`);
  console.log(`   - bruno.json (collection metadata)`);
  console.log(`   - .bru (environment variables)`);
  console.log(`   - health-check.bru (GET /)`);
  console.log(`   - upload-audio-silent.bru (POST /upload with silent audio)`);
  console.log(`   - upload-audio-file.bru (POST /upload with test file)`);
  console.log(`   - download-audio.bru (GET /audio/:filename)`);
  console.log(`\n💡 Next steps:`);
  console.log(`   1. Start server: npm run server`);
  console.log(`   2. Open Bruno and import the bru-no/ folder`);
  console.log(`   3. Set baseUrl environment variable`);
  console.log(`   4. Run health-check.bru to verify connection`);
  console.log(`   5. Run upload-audio-file.bru to test audio upload`);
}

main().catch(console.error);
