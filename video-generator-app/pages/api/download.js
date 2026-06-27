import fs from 'fs'
import path from 'path'

export default function handler(req, res) {
  const { file } = req.query
  const filePath = path.join(process.cwd(), 'python', 'output', file)

  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ error: 'File not found' })
  }

  const stat = fs.statSync(filePath)
  res.setHeader('Content-Length', stat.size)
  res.setHeader('Content-Type', 'video/mp4')
  res.setHeader('Content-Disposition', `attachment; filename="${file}"`)

  const stream = fs.createReadStream(filePath)
  stream.pipe(res)
}
