import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Globe, Loader2, Download, CheckCircle } from 'lucide-react'
import { useJobStore } from '@/stores/useJobStore'

const formSchema = z.object({
  url: z.string().url('Please enter a valid URL'),
  instructions: z.string().optional()
})

type FormData = z.infer<typeof formSchema>

export default function ConvertPage() {
  const navigate = useNavigate()
  const { addJob } = useJobStore()
  const [isChecking, setIsChecking] = useState(false)
  const [cachedResult, setCachedResult] = useState<string | null>(null)
  
  const { register, handleSubmit, formState: { errors, isSubmitting }, watch } = useForm<FormData>({
    resolver: zodResolver(formSchema)
  })
  
  const url = watch('url')
  
  const checkCache = async (url: string) => {
    if (!url) return
    
    setIsChecking(true)
    try {
      const domain = new URL(url).hostname
      const response = await fetch(`/api/check-cache/${domain}`)
      const data = await response.json()
      
      if (data.cached) {
        setCachedResult(data.file_path)
      } else {
        setCachedResult(null)
      }
    } catch (error) {
      setCachedResult(null)
    } finally {
      setIsChecking(false)
    }
  }
  
  const onSubmit = async (data: FormData) => {
    if (cachedResult) {
      window.open(`/api/download/${cachedResult}`, '_blank')
      return
    }
    
    try {
      const response = await fetch('/api/process-website', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      
      const result = await response.json()
      
      const job = {
        id: result.job_id,
        url: data.url,
        status: 'queued' as const,
        progress: 0,
        currentStep: 'Initializing...',
        screenshots: [],
        createdAt: new Date().toISOString()
      }
      
      addJob(job)
      navigate(`/processing/${result.job_id}`)
    } catch (error) {
      console.error('Failed to start conversion:', error)
    }
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-3xl font-bold">Convert Website to API Docs</h1>
          <p className="text-muted-foreground">
            Enter any website URL and let our AI agent navigate it to extract API calls
          </p>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Globe className="h-5 w-5 mr-2" />
              Website Conversion
            </CardTitle>
            <CardDescription>
              Provide a URL and optional interaction instructions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="space-y-2">
                <label htmlFor="url" className="text-sm font-medium">
                  Website URL
                </label>
                <Input
                  id="url"
                  placeholder="https://example.com"
                  {...register('url')}
                  onBlur={() => url && checkCache(url)}
                  className={errors.url ? 'border-destructive' : ''}
                />
                {errors.url && (
                  <p className="text-sm text-destructive">{errors.url.message}</p>
                )}
              </div>
              
              {isChecking && (
                <Alert>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <AlertDescription>
                    Checking if this site has already been processed...
                  </AlertDescription>
                </Alert>
              )}
              
              {cachedResult && (
                <Alert className="border-green-200 bg-green-50 dark:bg-green-950">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800 dark:text-green-200">
                    Great news! This site has already been processed. Click "Download Docs" to get instant results.
                  </AlertDescription>
                </Alert>
              )}
              
              <div className="space-y-2">
                <label htmlFor="instructions" className="text-sm font-medium">
                  Interaction Instructions (Optional)
                </label>
                <Textarea
                  id="instructions"
                  placeholder="e.g., Click the login button, then search for Python repositories"
                  {...register('instructions')}
                  rows={3}
                />
                <p className="text-xs text-muted-foreground">
                  Describe specific actions you want the AI agent to perform on the website
                </p>
              </div>
              
              <Button 
                type="submit" 
                className="w-full" 
                size="lg"
                disabled={isSubmitting || isChecking}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Starting Conversion...
                  </>
                ) : cachedResult ? (
                  <>
                    <Download className="mr-2 h-4 w-4" />
                    Download Docs (Instant)
                  </>
                ) : (
                  <>
                    <Globe className="mr-2 h-4 w-4" />
                    Start Conversion
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
        
        <div className="text-center space-y-4">
          <h3 className="text-lg font-semibold">Popular Sites</h3>
          <div className="flex flex-wrap gap-2 justify-center">
            {[
              'github.com',
              'reddit.com', 
              'news.ycombinator.com',
              'stackoverflow.com'
            ].map((site) => (
              <Button
                key={site}
                variant="outline"
                size="sm"
                onClick={() => {
                  const form = document.getElementById('url') as HTMLInputElement
                  if (form) {
                    form.value = `https://${site}`
                    checkCache(`https://${site}`)
                  }
                }}
              >
                {site}
              </Button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}