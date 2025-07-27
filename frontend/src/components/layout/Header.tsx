import { Link, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Globe, User, Menu } from 'lucide-react'

export default function Header() {
  const location = useLocation()
  
  return (
    <header className="border-b bg-background">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-2">
          <Globe className="h-6 w-6 text-primary" />
          <span className="font-bold text-xl">Webportal</span>
        </Link>
        
        <nav className="hidden md:flex items-center space-x-6">
          <Link 
            to="/convert" 
            className={`text-sm font-medium transition-colors hover:text-primary ${
              location.pathname === '/convert' ? 'text-primary' : 'text-muted-foreground'
            }`}
          >
            Convert Site
          </Link>
          <Link 
            to="/dashboard" 
            className={`text-sm font-medium transition-colors hover:text-primary ${
              location.pathname === '/dashboard' ? 'text-primary' : 'text-muted-foreground'
            }`}
          >
            Dashboard
          </Link>
        </nav>
        
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm" className="hidden md:flex">
            <User className="h-4 w-4 mr-2" />
            Sign In
          </Button>
          <Button size="sm" className="hidden md:flex">
            Get Started
          </Button>
          <Button variant="ghost" size="icon" className="md:hidden">
            <Menu className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  )
}