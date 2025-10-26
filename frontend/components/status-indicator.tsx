"use client"

interface StatusIndicatorProps {
  isProcessing: boolean
  progress: number
  fileCount: { current: number; total: number }
}

export default function StatusIndicator({ isProcessing, progress, fileCount }: StatusIndicatorProps) {
  const getStatusColor = () => {
    if (!isProcessing && progress === 0) return "bg-muted"
    if (isProcessing) return "bg-primary animate-pulse-glow"
    return "bg-accent"
  }

  const getStatusText = () => {
    if (!isProcessing && progress === 0) return "Idle"
    if (isProcessing) return "Processing"
    return "Complete"
  }

  return (
    <div className="rounded-lg border border-border bg-card p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-foreground">Status</h3>
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${getStatusColor()}`} />
            <span className="text-sm font-medium text-muted-foreground">{getStatusText()}</span>
          </div>
        </div>

        {fileCount.total > 0 && (
          <div className="text-right">
            <p className="text-2xl font-bold text-primary">{fileCount.current}</p>
            <p className="text-xs text-muted-foreground">of {fileCount.total} files</p>
          </div>
        )}
      </div>

      {fileCount.total > 0 && (
        <div className="space-y-2">
          <div className="w-full h-2 rounded-full bg-muted overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary via-secondary to-accent transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-muted-foreground text-right">{Math.round(progress)}% complete</p>
        </div>
      )}
    </div>
  )
}
