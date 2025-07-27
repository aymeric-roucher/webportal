import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import Layout from '@/components/layout/Layout'
import LandingPage from '@/pages/LandingPage'
import ConvertPage from '@/pages/ConvertPage'
import ProcessingPage from '@/pages/ProcessingPage'
import ResultsPage from '@/pages/ResultsPage'
import DashboardPage from '@/pages/DashboardPage'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/convert" element={<ConvertPage />} />
            <Route path="/processing/:jobId" element={<ProcessingPage />} />
            <Route path="/results/:jobId" element={<ResultsPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  )
}

export default App