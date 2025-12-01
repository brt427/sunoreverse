"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Upload, Loader2 } from "lucide-react"
import { AnalysisResults } from "@/components/analysis-results"
import { analyzeAudio, type MusicAnalysis } from "@/lib/api"
import { validateAudioFile, sanitizeFilename } from "@/lib/file-validation"

export function AnalysisForm() {
  const [file, setFile] = useState<File | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysis, setAnalysis] = useState<MusicAnalysis | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null) // Clear previous errors

    if (e.target.files?.[0]) {
      const selectedFile = e.target.files[0]

      // Validate file
      const validation = validateAudioFile(selectedFile)
      if (!validation.valid) {
        setError(validation.error || 'Invalid file')
        setFile(null)
        // Reset the input
        e.target.value = ''
        return
      }

      setFile(selectedFile)
    }
  }

  const handleAnalyze = async () => {
    if (!file) return

    setIsAnalyzing(true)
    setError(null)

    try {
      const result = await analyzeAudio(file)
      setAnalysis(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze audio')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleReset = () => {
    setFile(null)
    setAnalysis(null)
    setError(null)
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
                <span className="mt-2 rounded-full bg-muted px-3 py-1 text-sm text-foreground">
                  {sanitizeFilename(file.name)}
                </span>
              )}
              {!file && <span className="mt-2 text-sm text-muted-foreground">or click to browse files</span>}
            </label>
          </div>

          {error && (
            <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-sm text-destructive">
              {error}
            </div>
          )}

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
              "analyze song"
            )}
          </Button>
        </div>
      </Card>

      <p className="text-center text-sm text-muted-foreground">
        transform any song into a creative prompt
      </p>
    </div>
  )
}
