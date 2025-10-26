"use client"

import { Download, Copy } from "lucide-react"
import { Button } from "@/components/ui/button"

interface DocumentationPanelProps {
  documentation: string
  isProcessing: boolean
}

export default function DocumentationPanel({ documentation, isProcessing }: DocumentationPanelProps) {
  const handleCopy = () => {
    navigator.clipboard.writeText(documentation)
  }

  const handleDownload = () => {
    const element = document.createElement("a")
    const file = new Blob([documentation], { type: "text/markdown" })
    element.href = URL.createObjectURL(file)
    element.download = "documentation.md"
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  return (
    <div className="rounded-lg border border-border bg-card p-6 space-y-4 flex flex-col h-[500px]">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-foreground">Documentation Preview</h3>
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCopy}
            disabled={!documentation}
            className="text-muted-foreground hover:text-foreground disabled:opacity-50"
            title="Copy to clipboard"
          >
            <Copy className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDownload}
            disabled={!documentation}
            className="text-muted-foreground hover:text-foreground disabled:opacity-50"
            title="Download as markdown"
          >
            <Download className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto bg-input rounded-lg p-4 border border-border">
        {documentation ? (
          <div className="prose prose-invert max-w-none text-sm space-y-3">
            {documentation.split("\n").map((line, idx) => {
              if (line.startsWith("# ")) {
                return (
                  <h1 key={idx} className="text-xl font-bold text-primary mt-4 mb-2">
                    {line.replace("# ", "")}
                  </h1>
                )
              }
              if (line.startsWith("## ")) {
                return (
                  <h2 key={idx} className="text-lg font-semibold text-secondary mt-3 mb-2">
                    {line.replace("## ", "")}
                  </h2>
                )
              }
              if (line.startsWith("- ")) {
                return (
                  <li key={idx} className="text-foreground ml-4">
                    {line.replace("- ", "")}
                  </li>
                )
              }
              if (line.trim()) {
                return (
                  <p key={idx} className="text-muted-foreground leading-relaxed">
                    {line}
                  </p>
                )
              }
              return null
            })}
          </div>
        ) : (
          <div className="text-muted-foreground text-center py-8">
            <p>{isProcessing ? "Generating documentation..." : "Documentation will appear here"}</p>
          </div>
        )}
      </div>
    </div>
  )
}
