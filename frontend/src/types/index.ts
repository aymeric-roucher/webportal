export interface ProcessingJob {
  id: string
  url: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress: number
  currentStep: string
  estimatedTimeRemaining?: number
  screenshots: string[]
  errorMessage?: string
  createdAt: string
  completedAt?: string
  resultPath?: string
}

export interface CachedSite {
  domain: string
  filePath: string
  lastUpdated: string
  title: string
  description?: string
}

export interface User {
  id: string
  email: string
  credits: number
  plan: 'free' | 'paid'
}

export interface ConversionRequest {
  url: string
  instructions?: string
}