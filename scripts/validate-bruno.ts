#!/usr/bin/env node
/**
 * Validate Bruno collection structure and files
 */

import * as fs from "fs";
import * as path from "path";

const BRU_NO_DIR = path.join(process.cwd(), "bru-no");

function validateBrunoCollection() {
  console.log("🔍 Validating Bruno collection...\n");

  // Check required files
  const requiredFiles = ["bruno.json", ".bru"];
  const testFiles = [
    "health-check.bru",
    "upload-audio-silent.bru",
    "upload-audio-file.bru",
    "download-audio.bru",
  ];

  let allValid = true;

  // Check collection directory exists
  if (!fs.existsSync(BRU_NO_DIR)) {
    console.error("❌ bru-no directory not found");
    process.exit(1);
  }

  console.log("✅ Collection directory exists\n");

  // Check required files
  console.log("📋 Required files:");
  requiredFiles.forEach((file) => {
    const filePath = path.join(BRU_NO_DIR, file);
    if (fs.existsSync(filePath)) {
      console.log(`  ✅ ${file}`);
      if (file === "bruno.json") {
        try {
          const content = JSON.parse(fs.readFileSync(filePath, "utf8"));
          console.log(`     - Name: ${content.name}`);
          console.log(`     - Version: ${content.version}`);
          console.log(`     - Type: ${content.type}`);
        } catch (e) {
          console.log(`     ❌ Invalid JSON: ${e.message}`);
          allValid = false;
        }
      }
    } else {
      console.log(`  ❌ ${file} - MISSING`);
      allValid = false;
    }
  });

  console.log("\n📝 Test files:");
  testFiles.forEach((file) => {
    const filePath = path.join(BRU_NO_DIR, file);
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, "utf8");
      const hasEnvVar = content.includes("{{baseUrl}}");
      console.log(`  ✅ ${file}`);
      if (hasEnvVar) {
        console.log(`     - Uses environment variables`);
      }
    } else {
      console.log(`  ❌ ${file} - MISSING`);
      allValid = false;
    }
  });

  // Check test files directory
  const testFilesDir = path.join(process.cwd(), "test-files");
  if (fs.existsSync(testFilesDir)) {
    const audioFile = path.join(testFilesDir, "test-audio.wav");
    if (fs.existsSync(audioFile)) {
      const stats = fs.statSync(audioFile);
      console.log(`\n🎵 Test audio file: ${formatBytes(stats.size)}`);
    } else {
      console.log(`\n⚠️  Test audio file not found (run: npm run generate-audio)`);
    }
  }

  // Check other directories
  const dirs = ["tts-output", "temp"];
  console.log(`\n📁 Additional directories:`);
  dirs.forEach((dir) => {
    const dirPath = path.join(process.cwd(), dir);
    if (fs.existsSync(dirPath)) {
      console.log(`  ✅ ${dir}/`);
    } else {
      console.log(`  ⚠️  ${dir}/ - not created (will be created when needed)`);
    }
  });

  // Final summary
  console.log(`\n${allValid ? "✅" : "❌"} Collection is ${allValid ? "valid" : "INVALID"}`);

  if (allValid) {
    console.log(`\n📚 Ready to import in Bruno:`);
    console.log(`   1. Open Bruno application`);
    console.log(`   2. Click "Import Collection"`);
    console.log(`   3. Select the bru-no/ folder`);
    console.log(`   4. Set baseUrl environment variable`);
    console.log(`   5. Run health-check.bru to verify server`);
  }

  process.exit(allValid ? 0 : 1);
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return bytes + " bytes";
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / 1048576).toFixed(1) + " MB";
}

validateBrunoCollection();
