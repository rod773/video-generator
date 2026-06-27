import { Settings, Monitor, Hash } from 'lucide-react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'

const voices = [
  { value: 'en-US-AndrewNeural', label: 'Andrew (US)' },
  { value: 'en-US-AvaNeural', label: 'Ava (US)' },
  { value: 'en-US-GuyNeural', label: 'Guy (US)' },
  { value: 'en-GB-RyanNeural', label: 'Ryan (UK)' },
  { value: 'en-GB-SoniaNeural', label: 'Sonia (UK)' },
  { value: 'en-AU-WilliamNeural', label: 'William (AU)' },
]

export default function ConfigPanel({ voice, setVoice }) {
  return (
    <div className="rounded-lg border border-border bg-card text-card-foreground p-4 space-y-3">
      <h3 className="text-sm font-medium flex items-center gap-2">
        <Settings className="w-4 h-4" /> Configuration
      </h3>
      <Separator />
      <div className="space-y-3">
        <div>
          <label className="text-xs text-muted-foreground block mb-1.5">TTS Voice</label>
          <Select value={voice} onValueChange={setVoice}>
            <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {voices.map(v => (
                <SelectItem key={v.value} value={v.value}>{v.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-muted-foreground block mb-1.5 flex items-center gap-1">
              <Monitor className="w-3 h-3" /> Resolution
            </label>
            <div className="h-10 px-3 rounded-md border border-input bg-background text-sm text-muted-foreground flex items-center">
              1280x720
            </div>
          </div>
          <div>
            <label className="text-xs text-muted-foreground block mb-1.5 flex items-center gap-1">
              <Hash className="w-3 h-3" /> FPS
            </label>
            <div className="h-10 px-3 rounded-md border border-input bg-background text-sm text-muted-foreground flex items-center">
              30
            </div>
          </div>
        </div>
        <div className="text-xs text-muted-foreground/70 space-y-1">
          <p>Image duration: 3-5s per clip</p>
          <p>Ken Burns: random zoom/pan on each image</p>
        </div>
      </div>
    </div>
  )
}
