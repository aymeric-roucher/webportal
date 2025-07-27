import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { 
  Plus, 
  Search, 
  Download, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  CreditCard,
  Globe,
  Filter,
  MoreHorizontal
} from 'lucide-react'
import { useJobStore } from '@/stores/useJobStore'

export default function DashboardPage() {
  const { jobs } = useJobStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [filter, setFilter] = useState<'all' | 'completed' | 'processing' | 'failed'>('all')
  
  const userCredits = 15
  
  const filteredJobs = jobs.filter(job => {
    const matchesSearch = job.url.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filter === 'all' || job.status === filter
    return matchesSearch && matchesFilter
  })
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'processing':
      case 'queued':
        return <Clock className="h-4 w-4 text-green-500" />
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }
  
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="default">Completed</Badge>
      case 'processing':
        return <Badge variant="secondary">Processing</Badge>
      case 'queued':
        return <Badge variant="secondary">Queued</Badge>
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">Manage your website conversions and account</p>
          </div>
          <Button asChild>
            <Link to="/convert">
              <Plus className="h-4 w-4 mr-2" />
              New Conversion
            </Link>
          </Button>
        </div>
        
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold">{userCredits}</div>
                  <p className="text-sm text-muted-foreground">Credits Remaining</p>
                </div>
                <CreditCard className="h-8 w-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold">{jobs.length}</div>
                  <p className="text-sm text-muted-foreground">Total Conversions</p>
                </div>
                <Globe className="h-8 w-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold">
                    {jobs.filter(j => j.status === 'completed').length}
                  </div>
                  <p className="text-sm text-muted-foreground">Completed</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold">
                    {jobs.filter(j => j.status === 'processing' || j.status === 'queued').length}
                  </div>
                  <p className="text-sm text-muted-foreground">In Progress</p>
                </div>
                <Clock className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>
        </div>
        
        <Tabs defaultValue="conversions" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="conversions">My Conversions</TabsTrigger>
            <TabsTrigger value="cached">Public Cache</TabsTrigger>
            <TabsTrigger value="settings">Account Settings</TabsTrigger>
          </TabsList>
          
          <TabsContent value="conversions" className="space-y-4">
            {/* Search and Filter */}
            <div className="flex items-center space-x-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search conversions..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value as any)}
                  className="px-3 py-2 border rounded-md text-sm"
                >
                  <option value="all">All Status</option>
                  <option value="completed">Completed</option>
                  <option value="processing">Processing</option>
                  <option value="failed">Failed</option>
                </select>
              </div>
            </div>
            
            {/* Conversions List */}
            {filteredJobs.length === 0 ? (
              <Card>
                <CardContent className="p-8 text-center">
                  <Globe className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No conversions found</h3>
                  <p className="text-muted-foreground mb-4">
                    {jobs.length === 0 
                      ? "You haven't converted any websites yet."
                      : "No conversions match your current search and filter criteria."
                    }
                  </p>
                  <Button asChild>
                    <Link to="/convert">Start Your First Conversion</Link>
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-3">
                {filteredJobs.map((job) => (
                  <Card key={job.id}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          {getStatusIcon(job.status)}
                          <div>
                            <p className="font-medium">{new URL(job.url).hostname}</p>
                            <p className="text-sm text-muted-foreground">{job.url}</p>
                            <p className="text-xs text-muted-foreground">
                              {new Date(job.createdAt).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-3">
                          {getStatusBadge(job.status)}
                          
                          {job.status === 'processing' && (
                            <div className="text-right">
                              <div className="text-sm font-medium">{Math.round(job.progress)}%</div>
                              <div className="text-xs text-muted-foreground">
                                {job.currentStep}
                              </div>
                            </div>
                          )}
                          
                          <div className="flex space-x-2">
                            {job.status === 'completed' ? (
                              <Button size="sm" asChild>
                                <Link to={`/results/${job.id}`}>
                                  <Download className="h-4 w-4 mr-2" />
                                  Download
                                </Link>
                              </Button>
                            ) : job.status === 'processing' ? (
                              <Button size="sm" variant="outline" asChild>
                                <Link to={`/processing/${job.id}`}>
                                  View Progress
                                </Link>
                              </Button>
                            ) : (
                              <Button size="sm" variant="outline">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="cached" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Public Cache</CardTitle>
                <CardDescription>
                  Popular websites that have already been processed by other users
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[
                    { domain: 'github.com', title: 'GitHub API', lastUpdated: '2 days ago', downloads: 1234 },
                    { domain: 'reddit.com', title: 'Reddit API', lastUpdated: '1 week ago', downloads: 892 },
                    { domain: 'news.ycombinator.com', title: 'Hacker News API', lastUpdated: '3 days ago', downloads: 567 },
                    { domain: 'stackoverflow.com', title: 'Stack Overflow API', lastUpdated: '5 days ago', downloads: 423 },
                  ].map((site) => (
                    <Card key={site.domain}>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg">{site.title}</CardTitle>
                        <CardDescription>{site.domain}</CardDescription>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <div className="flex items-center justify-between text-sm text-muted-foreground mb-3">
                          <span>Updated {site.lastUpdated}</span>
                          <span>{site.downloads} downloads</span>
                        </div>
                        <Button size="sm" className="w-full">
                          <Download className="h-4 w-4 mr-2" />
                          Download
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="settings" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Account Information</CardTitle>
                  <CardDescription>Manage your account details</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Email</label>
                    <Input value="user@example.com" disabled />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Plan</label>
                    <div className="flex items-center justify-between">
                      <Badge variant="outline">Free Plan</Badge>
                      <Button size="sm" variant="outline">Upgrade</Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Credits & Billing</CardTitle>
                  <CardDescription>Manage your conversion credits</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Current Credits</span>
                    <span className="font-semibold">{userCredits}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Monthly Limit</span>
                    <span className="text-muted-foreground">50 (Free Plan)</span>
                  </div>
                  <Button className="w-full">
                    <CreditCard className="h-4 w-4 mr-2" />
                    Buy More Credits
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}