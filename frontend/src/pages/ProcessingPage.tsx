import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { 
  Globe, 
  Clock, 
  Eye, 
  X, 
  AlertCircle, 
  CheckCircle,
  Loader2,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { useJobStore } from '@/stores/useJobStore'
import { ProcessingJob } from '@/types'

export default function ProcessingPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()
  const { updateJob, getJob } = useJobStore()
  const [job, setJob] = useState<ProcessingJob | null>(null)
  const [currentScreenshot, setCurrentScreenshot] = useState(0)
  
  useEffect(() => {
    if (!jobId) return
    
    const foundJob = getJob(jobId)
    if (foundJob) {
      setJob(foundJob)
    }
    
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/jobs/${jobId}/status`)
        const data = await response.json()
        
        updateJob(jobId, data)
        setJob(data)
        
        if (data.status === 'completed') {
          navigate(`/results/${jobId}`)
        }
      } catch (error) {
        console.error('Failed to poll job status:', error)
      }
    }, 2000)
    
    return () => clearInterval(pollInterval)
  }, [jobId, getJob, updateJob, navigate])
  
  const cancelJob = async () => {
    if (!jobId) return
    
    try {
      await fetch(`/api/jobs/${jobId}/cancel`, { method: 'POST' })
      navigate('/convert')
    } catch (error) {
      console.error('Failed to cancel job:', error)
    }
  }
  
  const formatTimeRemaining = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }
  
  if (!job) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardContent className="p-8 text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
              <p>Loading job details...</p>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Processing Website</h1>
            <p className="text-muted-foreground flex items-center mt-1">
              <Globe className="h-4 w-4 mr-2" />
              {job.url}
            </p>
          </div>
          <Button variant="outline" onClick={cancelJob}>
            <X className="h-4 w-4 mr-2" />
            Cancel
          </Button>
        </div>
        
        {/* Status Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center">
                  <Badge variant={
                    job.status === 'completed' ? 'default' : 
                    job.status === 'failed' ? 'destructive' : 
                    'secondary'
                  }>
                    {job.status}
                  </Badge>
                  <span className="ml-3">{job.currentStep}</span>
                </CardTitle>
                <CardDescription className="flex items-center mt-2">
                  <Clock className="h-4 w-4 mr-2" />
                  {job.estimatedTimeRemaining ? (
                    `Estimated time remaining: ${formatTimeRemaining(job.estimatedTimeRemaining)}`
                  ) : (
                    'Calculating time remaining...'
                  )}
                </CardDescription>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold">{Math.round(job.progress)}%</div>
                <div className="text-sm text-muted-foreground">Complete</div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Progress value={job.progress} className="w-full" />
          </CardContent>
        </Card>
        
        {/* Error Alert */}
        {job.status === 'failed' && job.errorMessage && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>Processing failed:</strong> {job.errorMessage}
            </AlertDescription>
          </Alert>
        )}
        
        {/* Live Screenshots */}
        {job.screenshots.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Eye className="h-5 w-5 mr-2" />
                Live Browser View
              </CardTitle>
              <CardDescription>
                Watch our AI agent navigate the website in real-time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="relative">
                  <img
                    src={`/api/screenshots/${job.screenshots[currentScreenshot]}`}
                    alt={`Screenshot ${currentScreenshot + 1}`}
                    className="w-full rounded-lg border shadow-sm"
                  />
                  
                  {job.screenshots.length > 1 && (
                    <>
                      <Button
                        variant="outline"
                        size="icon"
                        className="absolute left-2 top-1/2 -translate-y-1/2"
                        onClick={() => setCurrentScreenshot(Math.max(0, currentScreenshot - 1))}
                        disabled={currentScreenshot === 0}
                      >
                        <ChevronLeft className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="icon"
                        className="absolute right-2 top-1/2 -translate-y-1/2"
                        onClick={() => setCurrentScreenshot(Math.min(job.screenshots.length - 1, currentScreenshot + 1))}
                        disabled={currentScreenshot === job.screenshots.length - 1}
                      >
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </>
                  )}
                </div>
                
                {job.screenshots.length > 1 && (
                  <div className="flex items-center justify-center space-x-2">
                    <span className="text-sm text-muted-foreground">
                      {currentScreenshot + 1} of {job.screenshots.length}
                    </span>
                    <div className="flex space-x-1">
                      {job.screenshots.map((_, index) => (
                        <button
                          key={index}
                          className={`w-2 h-2 rounded-full ${
                            index === currentScreenshot ? 'bg-primary' : 'bg-muted'
                          }`}
                          onClick={() => setCurrentScreenshot(index)}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}
        
        {/* Processing Steps */}
        <Card>
          <CardHeader>
            <CardTitle>Processing Steps</CardTitle>
            <CardDescription>
              Track the progress of website analysis and API extraction
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { step: 'Initialize browser', status: 'completed' },
                { step: 'Navigate to website', status: 'completed' },
                { step: 'Analyze page structure', status: 'completed' },
                { step: 'Perform interactions', status: job.progress > 25 ? 'completed' : 'current' },
                { step: 'Capture network requests', status: job.progress > 50 ? 'completed' : job.progress > 25 ? 'current' : 'pending' },
                { step: 'Generate API documentation', status: job.progress > 75 ? 'completed' : job.progress > 50 ? 'current' : 'pending' },
                { step: 'Finalize results', status: job.progress === 100 ? 'completed' : job.progress > 75 ? 'current' : 'pending' }
              ].map((item, index) => (
                <div key={index} className="flex items-center space-x-3">
                  {item.status === 'completed' ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : item.status === 'current' ? (
                    <Loader2 className="h-5 w-5 animate-spin text-primary" />
                  ) : (
                    <div className="h-5 w-5 rounded-full border-2 border-muted" />
                  )}
                  <span className={`${
                    item.status === 'completed' ? 'text-foreground' :
                    item.status === 'current' ? 'text-primary font-medium' :
                    'text-muted-foreground'
                  }`}>
                    {item.step}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}