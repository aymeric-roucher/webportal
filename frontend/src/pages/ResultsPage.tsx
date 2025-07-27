import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Download, 
  Share2, 
  Copy, 
  CheckCircle, 
  Globe, 
  FileText,
  ExternalLink,
  RefreshCw
} from 'lucide-react'
import { useJobStore } from '@/stores/useJobStore'
import ReactMarkdown from 'react-markdown'

export default function ResultsPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const { getJob } = useJobStore()
  const [job, setJob] = useState(getJob(jobId!))
  const [markdownContent, setMarkdownContent] = useState<string>('')
  const [copiedToClipboard, setCopiedToClipboard] = useState(false)
  
  useEffect(() => {
    if (!jobId) return
    
    const fetchResults = async () => {
      try {
        const response = await fetch(`/api/jobs/${jobId}/results`)
        const content = await response.text()
        setMarkdownContent(content)
      } catch (error) {
        console.error('Failed to fetch results:', error)
      }
    }
    
    fetchResults()
  }, [jobId])
  
  const downloadMarkdown = () => {
    if (!markdownContent || !job) return
    
    const blob = new Blob([markdownContent], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${new URL(job.url).hostname}-api-docs.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }
  
  const copyToClipboard = async () => {
    if (!markdownContent) return
    
    try {
      await navigator.clipboard.writeText(markdownContent)
      setCopiedToClipboard(true)
      setTimeout(() => setCopiedToClipboard(false), 2000)
    } catch (error) {
      console.error('Failed to copy to clipboard:', error)
    }
  }
  
  const shareResults = async () => {
    if (navigator.share && job) {
      try {
        await navigator.share({
          title: `API Documentation for ${new URL(job.url).hostname}`,
          text: 'Check out these auto-generated API docs!',
          url: window.location.href,
        })
      } catch (error) {
        console.error('Failed to share:', error)
      }
    }
  }
  
  if (!job) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto text-center">
          <h1 className="text-2xl font-bold mb-4">Job not found</h1>
          <Link to="/convert">
            <Button>Start New Conversion</Button>
          </Link>
        </div>
      </div>
    )
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <Badge variant="default">
                <CheckCircle className="h-3 w-3 mr-1" />
                Completed
              </Badge>
              <span className="text-sm text-muted-foreground">
                Processed {new Date(job.completedAt!).toLocaleString()}
              </span>
            </div>
            <h1 className="text-2xl font-bold">API Documentation Ready</h1>
            <p className="text-muted-foreground flex items-center mt-1">
              <Globe className="h-4 w-4 mr-2" />
              {job.url}
            </p>
          </div>
          <div className="flex space-x-3">
            <Button variant="outline" onClick={shareResults}>
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
            <Button variant="outline" onClick={copyToClipboard}>
              {copiedToClipboard ? (
                <CheckCircle className="h-4 w-4 mr-2" />
              ) : (
                <Copy className="h-4 w-4 mr-2" />
              )}
              {copiedToClipboard ? 'Copied!' : 'Copy'}
            </Button>
            <Button onClick={downloadMarkdown}>
              <Download className="h-4 w-4 mr-2" />
              Download .md
            </Button>
          </div>
        </div>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">12</div>
              <p className="text-sm text-muted-foreground">API Endpoints</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">4</div>
              <p className="text-sm text-muted-foreground">Data Models</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">8</div>
              <p className="text-sm text-muted-foreground">Screenshots</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">2.3s</div>
              <p className="text-sm text-muted-foreground">Avg Response</p>
            </CardContent>
          </Card>
        </div>
        
        {/* Main Content */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                Generated Documentation
              </span>
              <Button variant="outline" size="sm" asChild>
                <Link to="/convert">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Process Another Site
                </Link>
              </Button>
            </CardTitle>
            <CardDescription>
              Complete API documentation with examples and data models
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="preview" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="preview">Preview</TabsTrigger>
                <TabsTrigger value="raw">Raw Markdown</TabsTrigger>
              </TabsList>
              
              <TabsContent value="preview" className="mt-6">
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <ReactMarkdown>{markdownContent}</ReactMarkdown>
                </div>
              </TabsContent>
              
              <TabsContent value="raw" className="mt-6">
                <pre className="bg-muted p-4 rounded-lg overflow-auto text-sm">
                  <code>{markdownContent}</code>
                </pre>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
        
        {/* Export Options */}
        <Card>
          <CardHeader>
            <CardTitle>Export Options</CardTitle>
            <CardDescription>
              Download in different formats for your development workflow
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button variant="outline" className="justify-start h-auto p-4">
                <div className="text-left">
                  <div className="font-medium">Postman Collection</div>
                  <div className="text-sm text-muted-foreground">Import into Postman</div>
                </div>
                <ExternalLink className="h-4 w-4 ml-auto" />
              </Button>
              
              <Button variant="outline" className="justify-start h-auto p-4">
                <div className="text-left">
                  <div className="font-medium">OpenAPI Spec</div>
                  <div className="text-sm text-muted-foreground">Swagger/OpenAPI format</div>
                </div>
                <ExternalLink className="h-4 w-4 ml-auto" />
              </Button>
              
              <Button variant="outline" className="justify-start h-auto p-4">
                <div className="text-left">
                  <div className="font-medium">cURL Commands</div>
                  <div className="text-sm text-muted-foreground">Copy-paste ready</div>
                </div>
                <ExternalLink className="h-4 w-4 ml-auto" />
              </Button>
            </div>
          </CardContent>
        </Card>
        
        {/* Next Steps */}
        <Card>
          <CardHeader>
            <CardTitle>What's Next?</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-medium text-primary">1</span>
                </div>
                <div>
                  <p className="font-medium">Test the API endpoints</p>
                  <p className="text-sm text-muted-foreground">Use the provided examples to verify the API calls work as expected</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-medium text-primary">2</span>
                </div>
                <div>
                  <p className="font-medium">Integrate into your application</p>
                  <p className="text-sm text-muted-foreground">Replace web scraping with direct API calls in your code</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-medium text-primary">3</span>
                </div>
                <div>
                  <p className="font-medium">Monitor for changes</p>
                  <p className="text-sm text-muted-foreground">Re-process the site periodically to catch API updates</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}