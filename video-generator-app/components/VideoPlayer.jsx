import { Download } from 'lucide-react'

export default function VideoPlayer({ src }) {
  if (!src) return null

  return (
    <div className="rounded-lg border border-border bg-card text-card-foreground overflow-hidden">
      <div className="px-4 py-2 border-b border-border flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-green-500" />
        <span className="text-sm">Generated Video</span>
      </div>
      <video controls className="w-full max-h-96 bg-black" src={src}>
        Your browser does not support the video tag.
      </video>
      <div className="px-4 py-2 border-t border-border">
        <a href={src} download
          className="inline-flex items-center gap-2 text-sm text-primary hover:text-primary/80 transition-colors">
          <Download className="w-4 h-4" />
          Download MP4
        </a>
      </div>
    </div>
  )
}
