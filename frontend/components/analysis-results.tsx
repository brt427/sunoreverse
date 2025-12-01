"use client"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ArrowLeft, Copy, Check } from "lucide-react"
import { useState } from "react"

interface MusicAnalysis {
  tempo: number
  key: string
  mode: string
  energy: number
  analysis: {
    genre: string
    mood: string
    instrumentation: string
    production: string
    tempo_descriptor: string
    vocal_style: string
    prompt: string
  }
}

interface AnalysisResultsProps {
  analysis: MusicAnalysis
  onReset: () => void
}

export function AnalysisResults({ analysis, onReset }: AnalysisResultsProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(analysis.analysis.prompt.toLowerCase())
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-6">
      <Button variant="ghost" onClick={onReset} className="mb-2 gap-2 text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" />
        new analysis
      </Button>

      <div className="mb-4 text-center">
        <h2 className="text-xs font-medium uppercase tracking-widest text-muted-foreground">audio features</h2>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Card className="border border-border bg-card p-6 shadow-none">
          <div className="mb-2 text-xs font-medium uppercase tracking-widest text-muted-foreground">tempo</div>
          <div className="text-3xl font-normal text-foreground">
            {analysis.tempo} <span className="text-lg text-muted-foreground">bpm</span>
          </div>
        </Card>

        <Card className="border border-border bg-card p-6 shadow-none">
          <div className="mb-2 text-xs font-medium uppercase tracking-widest text-muted-foreground">key</div>
          <div className="text-3xl font-normal text-foreground">
            {analysis.key} {analysis.mode}
          </div>
        </Card>

        <Card className="border border-border bg-card p-6 shadow-none">
          <div className="mb-2 text-xs font-medium uppercase tracking-widest text-muted-foreground">energy</div>
          <div className="text-3xl font-normal text-foreground">{analysis.energy}</div>
        </Card>

        <Card className="border border-border bg-card p-6 shadow-none">
          <div className="mb-2 text-xs font-medium uppercase tracking-widest text-muted-foreground">mood</div>
          <div className="text-3xl font-normal capitalize leading-tight text-foreground">{analysis.analysis.mood}</div>
        </Card>
      </div>

      {/* Generated Prompt */}
      <Card className="mt-8 border border-border bg-card p-8 shadow-none">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-medium uppercase tracking-widest text-muted-foreground">generated prompt</h2>
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopy}
            className="gap-2 border-border bg-transparent hover:bg-muted"
          >
            {copied ? (
              <>
                <Check className="h-4 w-4" />
                copied
              </>
            ) : (
              <>
                <Copy className="h-4 w-4" />
                copy
              </>
            )}
          </Button>
        </div>
        <div className="rounded-lg bg-muted/50 p-5">
          <p className="text-sm leading-relaxed text-foreground">{analysis.analysis.prompt.toLowerCase()}</p>
        </div>
        <p className="mt-4 text-center text-xs text-muted-foreground">
          use this prompt with suno, udio, or other ai music tools
        </p>
      </Card>
    </div>
  )
}
