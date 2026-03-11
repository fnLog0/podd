import { spawn } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { Cli, z } from 'incur'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const repoRoot = path.resolve(__dirname, '..')

const projectPaths = {
  repoRoot,
  esp32: path.join(repoRoot, 'esp32'),
  espConfig: path.join(repoRoot, 'esp32', 'src', 'core', 'Config.h'),
  testServer: path.join(repoRoot, 'test-server'),
  testServerEntry: path.join(repoRoot, 'test-server', 'server.mjs'),
}

function runCommand(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      stdio: 'inherit',
      shell: false,
      ...options,
    })

    child.on('error', reject)
    child.on('close', (code) => {
      if (code === 0) {
        resolve()
        return
      }

      reject(new Error(`${command} exited with code ${code}`))
    })
  })
}

const cli = Cli.create('podd', {
  description: 'Development CLI for the Podd workspace',
})

cli.command('paths', {
  description: 'Show important workspace paths',
  run() {
    return projectPaths
  },
})

cli.command('config-show', {
  description: 'Show where the ESP32 firmware config lives',
  run() {
    return {
      espConfig: projectPaths.espConfig,
      note: 'Edit WiFi and backend URLs in this file.',
    }
  },
})

cli.command('server-start', {
  description: 'Start the local ESP32 test server',
  options: z.object({
    host: z.string().default('0.0.0.0').describe('Host to bind'),
    port: z.coerce.number().default(3000).describe('Port to bind'),
  }),
  async run(c) {
    await runCommand('node', [projectPaths.testServerEntry], {
      cwd: projectPaths.testServer,
      env: {
        ...process.env,
        HOST: String(c.options.host),
        PORT: String(c.options.port),
      },
    })

    return {
      status: 'stopped',
    }
  },
})

cli.command('esp-build', {
  description: 'Compile the ESP32 firmware with Arduino CLI',
  options: z.object({
    sim: z.boolean().default(false).describe('Build with SIMULATION_MODE enabled'),
    fqbn: z.string().default('esp32:esp32:esp32').describe('Arduino fully-qualified board name'),
  }),
  async run(c) {
    const buildPath = c.options.sim
      ? '/tmp/podd-esp32-cli-sim-build'
      : '/tmp/podd-esp32-cli-build'

    const args = [
      'compile',
      '--fqbn',
      c.options.fqbn,
      '--build-path',
      buildPath,
    ]

    if (c.options.sim) {
      args.push(
        '--build-property',
        'compiler.cpp.extra_flags=-DSIMULATION_MODE=1',
        '--build-property',
        'compiler.c.extra_flags=-DSIMULATION_MODE=1',
      )
    }

    args.push(projectPaths.esp32)

    await runCommand('arduino-cli', args, {
      cwd: projectPaths.esp32,
      env: process.env,
    })

    return {
      firmware: projectPaths.esp32,
      mode: c.options.sim ? 'simulation' : 'hardware',
      buildPath,
      fqbn: c.options.fqbn,
    }
  },
})

cli.serve()
