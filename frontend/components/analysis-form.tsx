"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Upload, Loader2 } from "lucide-react"
import { AnalysisResults } from "@/components/analysis-results"

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

export function AnalysisForm() {
  const [file, setFile] = useState<File | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysis, setAnalysis] = useState<MusicAnalysis | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleAnalyze = async () => {
    setIsAnalyzing(true)

    // Simulate analysis (replace with actual API call)
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // Demo analysis result
    setAnalysis({
      tempo: 160,
      key: "F",
      mode: "minor",
      energy: 0.87,
      analysis: {
        genre: "2010s Feel-Good Pop",
        mood: "uplifting and joyful",
        instrumentation: "acoustic guitar, bright keyboard, simple percussion",
        production: "polished, clean mix",
        tempo_descriptor: "upbeat",
        vocal_style: "clean male vocals",
        prompt:
          "2010s Feel-Good Pop, uplifting and joyful, upbeat, featuring acoustic guitar, bright keyboard, simple percussion, polished, clean mix, clean male vocals",
      },
    })

    setIsAnalyzing(false)
  }

  const handleReset = () => {
    setFile(null)
    setAnalysis(null)
  }

  if (analysis) {
    return <AnalysisResults analysis={analysis} onReset={handleReset} />
  }

  return (
    <div className="space-y-6">
      <Card className="border border-border bg-card p-8 shadow-none md:p-12">
        <div className="space-y-6">
          <div className="relative">
            <input
              type="file"
              accept="audio/*"
              onChange={handleFileChange}
              className="hidden"
              id="file-upload"
              disabled={isAnalyzing}
            />
            <label
              htmlFor="file-upload"
              className="flex h-48 cursor-pointer flex-col items-center justify-center rounded-xl border border-border bg-background/50 transition-all hover:bg-background"
            >
              <Upload className="mb-4 h-12 w-12 text-muted-foreground" />
              <span className="text-base text-foreground">{file ? "song selected" : "drop your audio file"}</span>
              {file && (
                <span className="mt-2 rounded-full bg-muted px-3 py-1 text-sm text-foreground">{file.name}</span>
              )}
              {!file && <span className="mt-2 text-sm text-muted-foreground">or click to browse files</span>}
            </label>
          </div>

          <Button
            onClick={handleAnalyze}
            disabled={!file || isAnalyzing}
            className="h-14 w-full rounded-xl bg-primary text-base font-normal text-primary-foreground hover:bg-primary/90"
            size="lg"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                analyzing song
              </>
            ) : (
              <>
                <span className="mr-2">✨</span>
                analyze song
              </>
            )}
          </Button>
        </div>
      </Card>

      <p className="text-center text-sm text-muted-foreground">
        transform your songs into emotional insights and creative prompts
      </p>
    </div>
  )
}
