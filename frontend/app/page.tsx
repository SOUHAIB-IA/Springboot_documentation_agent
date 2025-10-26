"use client";

import { useState, useEffect } from "react";
import { useAgentSocket } from "@/hooks/use-agent-socket";
import { open } from '@tauri-apps/plugin-dialog';
import HeroHeader from "@/components/hero-header";
import MissionLaunchPanel from "@/components/mission-launch-panel";
import StatusIndicator from "@/components/status-indicator";
import AgentFeedPanel from "@/components/agent-feed-panel";
import DocumentationPanel from "@/components/documentation-panel";

export default function Home() {
  const [projectPath, setProjectPath] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  
  // The hook now manages logs and the final document
  const { logs, finalDoc, isConnected, startMission } = useAgentSocket("http://localhost:8000");

  const handleBrowse = async () => {
    try {
      const selected = await open({ directory: true, multiple: false, title: 'Select Project Folder' });
      if (typeof selected === 'string') {
        setProjectPath(selected);
      }
    } catch (error) {
      console.error("Failed to open dialog", error);
    }
  };

  const handleLaunchMission = () => {
    if (!projectPath) {
      alert("Please browse for a project folder first.");
      return;
    }
    if (!isConnected) {
      alert("Connecting to agent server... Please try again in a moment.");
      return;
    }
    setIsProcessing(true);
    // The hook handles the rest
    startMission(projectPath);
  };
  
  // When the final doc is received, or if the socket disconnects, stop processing
  useEffect(() => {
    if (finalDoc || !isConnected) {
      setIsProcessing(false);
    }
  }, [finalDoc, isConnected]);

  // A simple progress simulation based on log length
  const progress = finalDoc ? 100 : (logs.length > 0 ? (logs.length % 99) + 1 : 0);

  return (
    <div className="min-h-screen bg-background text-foreground dark">
      <HeroHeader />

      <main className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="space-y-6">
          <MissionLaunchPanel
            onLaunch={handleLaunchMission}
            onBrowse={handleBrowse}
            isProcessing={isProcessing}
            selectedPath={projectPath}
          />

          <StatusIndicator isProcessing={isProcessing} progress={progress} fileCount={{ current: 0, total: 0 }} />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AgentFeedPanel logs={logs} isProcessing={isProcessing} />
            <DocumentationPanel documentation={finalDoc} isProcessing={isProcessing} />
          </div>
        </div>
      </main>
    </div>
  );
}