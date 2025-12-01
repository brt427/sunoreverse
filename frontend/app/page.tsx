import { AnalysisForm } from "@/components/analysis-form"

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto max-w-5xl px-4 py-12 md:py-20">
        <div className="mb-12 text-center">
          <h1 className="mb-3 text-3xl font-bold tracking-tight text-foreground md:text-4xl">sunoreverse</h1>
          <p className="text-pretty text-sm text-muted-foreground md:text-base">song → prompt</p>
        </div>

        <AnalysisForm />
      </div>
    </main>
  )
}
