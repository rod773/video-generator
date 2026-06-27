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
    } else {
      const ext = path.extname(file.originalname)
      cb(null, `image_${Date.now()}_${Math.random().toString(36).slice(2)}${ext}`)
    }
  },
})

const upload = multer({
  storage,
  fileFilter: (req, file, cb) => {
    if (file.fieldname === 'script') {
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

  upload.array('images', 200)(req, res, (err) => {
    if (err) {
      return res.status(400).json({ error: err.message })
    }
    const files = req.files || []
    const uploaded = files.map(f => ({
      name: f.filename,
      size: f.size,
      type: f.mimetype,
    }))
    res.json({ success: true, files: uploaded })
  })
}
