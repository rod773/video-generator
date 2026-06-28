import multer from 'multer'
import path from 'path'
import fs from 'fs'

const uploadDir = path.join(process.cwd(), 'public', 'uploads')
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true })
}

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadDir),
  filename: (req, file, cb) => {
    if (file.fieldname === 'script') {
      cb(null, 'script.txt')
    } else if (file.fieldname === 'prompt') {
      cb(null, 'prompt.txt')
    } else {
      const ext = path.extname(file.originalname)
      cb(null, `image_${Date.now()}_${Math.random().toString(36).slice(2)}${ext}`)
    }
  },
})

const upload = multer({
  storage,
  fileFilter: (req, file, cb) => {
    if (file.fieldname === 'script' || file.fieldname === 'prompt') {
      cb(null, true)
    } else if (file.mimetype.startsWith('image/')) {
      cb(null, true)
    } else {
      cb(new Error('Only image files allowed'))
    }
  },
})

export const config = {
  api: { bodyParser: false },
}

export default function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  // Clean up old files before new upload
  if (fs.existsSync(uploadDir)) {
    for (const f of fs.readdirSync(uploadDir)) {
      try { fs.unlinkSync(path.join(uploadDir, f)) } catch {}
    }
  }

  upload.fields([
    { name: 'images', maxCount: 200 },
    { name: 'script', maxCount: 1 },
    { name: 'prompt', maxCount: 1 },
  ])(req, res, (err) => {
    if (err) {
      return res.status(400).json({ error: err.message })
    }
    const imageFiles = req.files?.images || []
    const scriptFiles = req.files?.script || []
    const promptFiles = req.files?.prompt || []
    const files = [...imageFiles, ...scriptFiles, ...promptFiles]
    const uploaded = files.map(f => ({
      name: f.filename,
      size: f.size,
      type: f.mimetype,
    }))
    res.json({ success: true, files: uploaded })
  })
}
