import { Link } from 'react-router-dom'
import { Globe } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="border-t bg-muted/50">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-3">
            <Link to="/" className="flex items-center space-x-2">
              <Globe className="h-5 w-5 text-primary" />
              <span className="font-bold">Webportal</span>
            </Link>
            <p className="text-sm text-muted-foreground">
              Convert any website into clean API documentation automatically.
            </p>
          </div>
          
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">Product</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link to="/convert" className="hover:text-foreground">Convert Site</Link></li>
              <li><Link to="/dashboard" className="hover:text-foreground">Dashboard</Link></li>
              <li><Link to="/pricing" className="hover:text-foreground">Pricing</Link></li>
            </ul>
          </div>
          
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">Support</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link to="/docs" className="hover:text-foreground">Documentation</Link></li>
              <li><Link to="/help" className="hover:text-foreground">Help Center</Link></li>
              <li><Link to="/contact" className="hover:text-foreground">Contact</Link></li>
            </ul>
          </div>
          
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">Legal</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link to="/privacy" className="hover:text-foreground">Privacy Policy</Link></li>
              <li><Link to="/terms" className="hover:text-foreground">Terms of Service</Link></li>
            </ul>
          </div>
        </div>
        
        <div className="mt-8 pt-8 border-t text-center text-sm text-muted-foreground">
          © 2024 Webportal. All rights reserved.
        </div>
      </div>
    </footer>
  )
}