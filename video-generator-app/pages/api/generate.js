import { spawn } from 'child_process'
import path from 'path'

export const config = {
  api: { bodyParser: { sizeLimit: '500mb' } },
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const { voice } = req.body || {}
  const pythonScript = path.join(process.cwd(), 'python', 'generate.py')

  res.setHeader('Content-Type', 'text/event-stream')
  res.setHeader('Cache-Control', 'no-cache')
  res.setHeader('Connection', 'keep-alive')
  res.flushHeaders()

  const args = [pythonScript]
  if (voice) args.push(voice)

  const proc = spawn('python', args, {
    cwd: path.join(process.cwd(), 'python'),
    stdio: ['pipe', 'pipe', 'pipe'],
  })

  let outputPath = null

  proc.stdout.on('data', (data) => {
    const lines = data.toString().trim().split('\n')
    for (const line of lines) {
      try {
        const parsed = JSON.parse(line)
        if (parsed.type === 'log') {
          res.write(`data: ${JSON.stringify({ type: 'log', message: parsed.message })}\n\n`)
        } else if (parsed.type === 'done') {
          outputPath = parsed.output
          res.write(`data: ${JSON.stringify({ type: 'done', output: '/api/download?file=final_video.mp4' })}\n\n`)
        } else if (parsed.type === 'error') {
          res.write(`data: ${JSON.stringify({ type: 'error', message: parsed.message })}\n\n`)
        }
      } catch {
        // non-JSON output, just log it
        res.write(`data: ${JSON.stringify({ type: 'log', message: line })}\n\n`)
      }
    }
  })

  proc.stderr.on('data', (data) => {
    res.write(`data: ${JSON.stringify({ type: 'log', message: data.toString() })}\n\n`)
  })

  proc.on('close', (code) => {
    if (code !== 0) {
      res.write(`data: ${JSON.stringify({ type: 'error', message: 'Python process exited with code ' + code })}\n\n`)
    }
    if (!outputPath) {
      res.write(`data: ${JSON.stringify({ type: 'error', message: 'No output file generated' })}\n\n`)
    }
    res.write(`data: ${JSON.stringify({ type: 'close' })}\n\n`)
    res.end()
  })

  req.on('close', () => {
    proc.kill()
  })
}
