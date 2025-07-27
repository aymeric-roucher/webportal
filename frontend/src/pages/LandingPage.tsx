import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowRight, Zap, Download, Shield, Clock } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <div className="text-center space-y-6 max-w-4xl mx-auto">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
            Convert any website into 
            <span className="text-primary"> API docs</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Stop web scraping. Start using APIs. Webportal reverse-engineers websites 
            to generate clean API documentation by automating browser interactions 
            and capturing underlying network requests.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" className="text-lg px-8">
              <Link to="/convert">
                Start Converting <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button variant="outline" size="lg" className="text-lg px-8">
              View Examples
            </Button>
          </div>
          <p className="text-sm text-muted-foreground">
            3 free conversions • No credit card required
          </p>
        </div>
      </section>

      {/* Demo Section */}
      <section className="bg-muted/50 py-16">
        <div className="container mx-auto px-4">
          <div className="text-center space-y-4 mb-12">
            <h2 className="text-3xl font-bold">See it in action</h2>
            <p className="text-muted-foreground">
              Watch as Webportal automatically navigates GitHub and extracts API calls
            </p>
          </div>
          <div className="max-w-4xl mx-auto">
            <Card>
              <CardContent className="p-0">
                <div className="aspect-video bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-blue-950 dark:to-indigo-900 flex items-center justify-center">
                  <div className="text-center space-y-4">
                    <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto">
                      <Zap className="h-8 w-8 text-primary" />
                    </div>
                    <p className="text-lg font-semibold">Demo Video Coming Soon</p>
                    <p className="text-muted-foreground">Live browser automation in action</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center space-y-4 mb-12">
          <h2 className="text-3xl font-bold">Why choose Webportal?</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Built for developers who need reliable API access without the complexity of web scraping
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader>
              <Zap className="h-10 w-10 text-primary mb-2" />
              <CardTitle className="text-lg">Live Processing</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Watch real-time screenshots as our AI agent navigates websites and captures API calls
              </CardDescription>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <Download className="h-10 w-10 text-primary mb-2" />
              <CardTitle className="text-lg">Instant Results</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Get structured markdown documentation with examples ready to use in your projects
              </CardDescription>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <Shield className="h-10 w-10 text-primary mb-2" />
              <CardTitle className="text-lg">Smart Caching</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Popular sites are pre-processed. Get instant downloads for GitHub, Reddit, and more
              </CardDescription>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <Clock className="h-10 w-10 text-primary mb-2" />
              <CardTitle className="text-lg">Always Updated</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Unlike static scraping, our docs stay current with website changes and new features
              </CardDescription>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Examples Section */}
      <section className="bg-muted/50 py-16">
        <div className="container mx-auto px-4">
          <div className="text-center space-y-4 mb-12">
            <h2 className="text-3xl font-bold">Popular sites already converted</h2>
            <p className="text-muted-foreground">
              Download API docs instantly for these sites
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {[
              { name: 'GitHub', desc: 'Repository management, issues, pull requests', status: 'Ready' },
              { name: 'Reddit', desc: 'Posts, comments, user data', status: 'Ready' },
              { name: 'Hacker News', desc: 'Stories, comments, user profiles', status: 'Processing' },
            ].map((site) => (
              <Card key={site.name}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{site.name}</CardTitle>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      site.status === 'Ready' 
                        ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                        : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300'
                    }`}>
                      {site.status}
                    </span>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="mb-4">{site.desc}</CardDescription>
                  <Button variant="outline" size="sm" className="w-full">
                    {site.status === 'Ready' ? 'Download Docs' : 'Get Notified'}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center space-y-6 max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold">Ready to get started?</h2>
          <p className="text-muted-foreground">
            Convert your first website to API docs in under 5 minutes
          </p>
          <Button asChild size="lg" className="text-lg px-8">
            <Link to="/convert">
              Start Your First Conversion <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </Button>
        </div>
      </section>
    </div>
  )
}