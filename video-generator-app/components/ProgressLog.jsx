import { useEffect, useRef } from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'

export default function ProgressLog({ logs }) {
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  return (
    <div className="rounded-lg border border-border bg-card text-card-foreground">
      <div className="px-4 py-2 border-b border-border flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-green-500" />
        <span className="text-xs font-medium">Output</span>
      </div>
      <ScrollArea className="h-64">
        <div className="p-4 font-mono text-xs space-y-1">
          {logs.length === 0 ? (
            <p className="text-muted-foreground">Waiting for generation to start...</p>
          ) : (
            logs.map((log, i) => (
              <div key={i} className={`${
                log.type === 'error' ? 'text-destructive' :
                log.type === 'done' ? 'text-green-400' :
                log.type === 'progress' ? 'text-yellow-400' : 'text-muted-foreground'
              }`}>
                <span className="text-muted-foreground/40 mr-2">&gt;</span>
                {log.message}
              </div>
            ))
          )}
          <div ref={endRef} />
        </div>
      </ScrollArea>
    </div>
  )
}
