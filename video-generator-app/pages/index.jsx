import { useState } from 'react'
import { Play, Loader2 } from 'lucide-react'
import Layout from '@/components/Layout'
import UploadZone from '@/components/UploadZone'
import ConfigPanel from '@/components/ConfigPanel'
import ProgressLog from '@/components/ProgressLog'
import VideoPlayer from '@/components/VideoPlayer'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export default function Home() {
  const [images, setImages] = useState([])
  const [scriptText, setScriptText] = useState('')
  const [voice, setVoice] = useState('en-US-AndrewNeural')
  const [prompt, setPrompt] = useState('')
  const [logs, setLogs] = useState([])
  const [generating, setGenerating] = useState(false)
  const [videoSrc, setVideoSrc] = useState(null)

  const addLog = (type, message) => {
    setLogs(prev => [...prev, { type, message, time: Date.now() }])
  }

  const handleGenerate = async () => {
    if (!images.length) { addLog('error', 'Please upload at least one image.'); return }
    if (!scriptText.trim()) { addLog('error', 'Please enter a script.'); return }

    setGenerating(true)
    setVideoSrc(null)
    setLogs([])
    addLog('progress', 'Uploading files...')

    const formData = new FormData()
    images.forEach(img => formData.append('images', img))
    const scriptBlob = new Blob([scriptText], { type: 'text/plain' })
    formData.append('script', scriptBlob, 'script.txt')
    if (prompt.trim()) {
      const promptBlob = new Blob([prompt], { type: 'text/plain' })
      formData.append('prompt', promptBlob, 'prompt.txt')
    }

    try {
      const uploadRes = await fetch('/api/upload', { method: 'POST', body: formData })
      const uploadData = await uploadRes.json()
      if (!uploadData.success) {
        addLog('error', 'Upload failed: ' + (uploadData.error || 'unknown'))
        setGenerating(false)
        return
      }
      const imageCount = uploadData.files.filter(f => f.type?.startsWith('image/')).length
      addLog('progress', `Uploaded ${imageCount} image(s)`)
      addLog('progress', 'Starting video generation...')

      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voice }),
      })

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop()

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.type === 'log' || data.type === 'progress') addLog(data.type, data.message)
              else if (data.type === 'done') { addLog('done', 'Video generated successfully!'); setVideoSrc(data.output) }
              else if (data.type === 'error') addLog('error', data.message)
            } catch {}
          }
        }
      }
    } catch (err) {
      addLog('error', 'Connection error: ' + err.message)
    }

    setGenerating(false)
  }

  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <UploadZone images={images} setImages={setImages} scriptText={scriptText} setScriptText={setScriptText} />
          <ConfigPanel voice={voice} setVoice={setVoice} prompt={prompt} setPrompt={setPrompt} />
        </div>

        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center gap-3 flex-wrap">
            <Button onClick={handleGenerate} disabled={generating} size="lg" className="gap-2">
              {generating ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</>
              ) : (
                <><Play className="w-4 h-4" /> Generate Video</>
              )}
            </Button>
            {images.length > 0 && <Badge variant="secondary">{images.length} image{images.length > 1 ? 's' : ''}</Badge>}
            {scriptText.trim() && <Badge variant="outline">Script ready</Badge>}
          </div>

          <ProgressLog logs={logs} />
          {videoSrc && <VideoPlayer src={videoSrc} />}
        </div>
      </div>
    </Layout>
  )
}
