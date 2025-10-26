"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { FolderSearch, Zap } from "lucide-react"

interface MissionLaunchPanelProps {
  onLaunch: () => void;
  onBrowse:()=> void;
  isProcessing: boolean;
  selectedPath: string | null;
}


export default function MissionLaunchPanel({onLaunch,onBrowse,isProcessing,selectedPath}: MissionLaunchPanelProps) {
  const [prompt, setPrompt] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (selectedPath && !isProcessing) {
      onLaunch()
    }
  }

  return (
    <div className="rounded-lg border border-border bg-card p-6 space-y-4">
      <div className="space-y-2">
        <h2 className="text-xl font-semibold text-foreground">Launch Mission</h2>
        <p className="text-sm text-muted-foreground">Select a Spring Boot project directory to begin processing.</p></div>

      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <Button
          variant="outline"
          onClick={onBrowse}
          disabled={isProcessing}
          className="flex items-center gap-2 text-muted-foreground hover:text-foreground"
          >
            <FolderSearch className="w-4 h-4" />
            Browse for Project...
          </Button>
          <div className="flex-grow p-3 rounded-lg bg-input border border-border text-sm text-muted-foreground truncate">
            {selectedPath ? selectedPath : "No project selected."}
          </div>
        </div>

         <Button
          onClick={handleSubmit}
          disabled={!selectedPath || isProcessing}
          className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-3 rounded-lg transition-all duration-300 hover:shadow-lg hover:shadow-primary/50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <Zap className="w-4 h-4" />
          {isProcessing ? "Mission in Progress..." : "Launch Agent"}
        </Button>
      </div>
    </div>
  )
}
