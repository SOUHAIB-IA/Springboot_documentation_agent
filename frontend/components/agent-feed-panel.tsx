"use client"

import { useEffect, useRef } from "react"
import { Pause, Play } from "lucide-react"
import { Button } from "@/components/ui/button"

interface Log {
  id: string
  level: string
  message: string
  timestamp: string
}

interface AgentFeedPanelProps {
  logs: Log[]
  isProcessing: boolean
}

export default function AgentFeedPanel({ logs, isProcessing }: AgentFeedPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs])

  const getLevelColor = (level: string) => {
    switch (level) {
      case "INFO":
        return "text-primary"
      case "WARNING":
        return "text-yellow-400"
      case "ERROR":
        return "text-red-400"
      case "SUCCESS":
        return "text-accent"
      default:
        return "text-muted-foreground"
    }
  }

  return (
    <div className="rounded-lg border border-border bg-card p-6 space-y-4 flex flex-col h-[500px]">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-foreground">Agent Feed</h3>
        <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
          {isProcessing ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
        </Button>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto space-y-2 font-mono text-sm bg-input rounded-lg p-4 border border-border"
      >
        {logs.length === 0 ? (
          <div className="text-muted-foreground text-center py-8">
            <p>Awaiting mission launch...</p>
          </div>
        ) : (
          logs.map((log) => (
            <div key={log.id} className="animate-float-up">
              <span className="text-muted-foreground">[{log.timestamp}]</span>{" "}
              <span className={`font-semibold ${getLevelColor(log.level)}`}>{log.level}</span>{" "}
              <span className="text-foreground">{log.message}</span>
            </div>
          ))
        )}
      </div>

      <p className="text-xs text-muted-foreground">
        {logs.length} {logs.length === 1 ? "entry" : "entries"}
      </p>
    </div>
  )
}
