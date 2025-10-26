"use client"

export default function HeroHeader() {
  return (
    <header className="relative overflow-hidden border-b border-border bg-gradient-to-b from-card to-background">
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 bg-[linear-gradient(0deg,transparent_24%,rgba(0,217,255,.05)_25%,rgba(0,217,255,.05)_26%,transparent_27%,transparent_74%,rgba(0,217,255,.05)_75%,rgba(0,217,255,.05)_76%,transparent_77%,transparent),linear-gradient(90deg,transparent_24%,rgba(0,217,255,.05)_25%,rgba(0,217,255,.05)_26%,transparent_27%,transparent_74%,rgba(0,217,255,.05)_75%,rgba(0,217,255,.05)_76%,transparent_77%,transparent)] bg-[length:50px_50px] animate-grid-fade" />
      </div>

      <div className="relative z-10 px-4 py-16 sm:py-24 text-center">
        <div className="space-y-4">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight">
            <span className="bg-gradient-to-r from-primary via-secondary to-primary bg-clip-text text-transparent animate-pulse-glow">
              Mission Control
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto">
            Command your AI agents with precision. Monitor, analyze, and generate documentation in real-time.
          </p>

          <div className="flex justify-center gap-2 pt-4">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse-glow" />
            <div className="w-2 h-2 rounded-full bg-secondary animate-pulse-glow" style={{ animationDelay: "0.3s" }} />
            <div className="w-2 h-2 rounded-full bg-accent animate-pulse-glow" style={{ animationDelay: "0.6s" }} />
          </div>
        </div>
      </div>
    </header>
  )
}
