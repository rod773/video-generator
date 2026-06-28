import { Settings, Monitor, Hash, Sparkles } from 'lucide-react'
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

export default function ConfigPanel({ voice, setVoice, prompt, setPrompt }) {
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
        <Separator />
        <div>
          <label className="text-xs text-muted-foreground block mb-1.5 flex items-center gap-1">
            <Sparkles className="w-3 h-3" /> Video Prompt
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the video style you want... e.g. cinematic, slow and dramatic, fast-paced montage, vintage film look"
            className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 resize-none"
          />
          <p className="text-xs text-muted-foreground/60 mt-1">
            Influences Ken Burns effects, pacing, and image transitions
          </p>
        </div>
      </div>
    </div>
  )
}
