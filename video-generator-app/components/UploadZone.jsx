import { useRef, useState } from 'react'
import { Image, Upload, X } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function UploadZone({ images, setImages, scriptText, setScriptText }) {
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef(null)
  const scriptInputRef = useRef(null)

  const handleImageDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'))
    if (files.length) setImages(prev => [...prev, ...files])
  }

  const handleImageSelect = (e) => {
    const files = Array.from(e.target.files).filter(f => f.type.startsWith('image/'))
    if (files.length) setImages(prev => [...prev, ...files])
  }

  const handleScriptFile = (e) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (ev) => setScriptText(ev.target.result)
      reader.readAsText(file)
    }
  }

  const removeImage = (index) => setImages(prev => prev.filter((_, i) => i !== index))

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-sm font-medium mb-2 flex items-center gap-2">
          <Image className="w-4 h-4" /> Images
        </h3>
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleImageDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
            dragOver ? 'border-primary bg-primary/10' : 'border-border hover:border-muted-foreground/50'
          }`}
        >
          <input ref={fileInputRef} type="file" multiple accept="image/*" onChange={handleImageSelect} className="hidden" />
          <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">Drop images here or click to browse</p>
          <p className="text-xs text-muted-foreground/60 mt-1">JPG, PNG, WebP, BMP</p>
        </div>
        {images.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {images.map((img, i) => (
              <div key={i} className="relative group">
                <img src={URL.createObjectURL(img)} alt="" className="w-16 h-16 object-cover rounded-lg border border-border" />
                <button onClick={() => removeImage(i)}
                  className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-destructive text-destructive-foreground rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <h3 className="text-sm font-medium mb-2 flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
          Script
        </h3>
        <textarea
          value={scriptText}
          onChange={(e) => setScriptText(e.target.value)}
          placeholder="Enter your narration text. Separate paragraphs with blank lines..."
          className="flex min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 resize-none"
        />
        <div className="mt-1">
          <input ref={scriptInputRef} type="file" accept=".txt" onChange={handleScriptFile} className="hidden" />
          <Button variant="link" size="sm" className="h-auto p-0 text-xs" onClick={() => scriptInputRef.current?.click()} type="button">
            Import from .txt file
          </Button>
        </div>
      </div>
    </div>
  )
}
