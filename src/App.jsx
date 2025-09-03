import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Models from './pages/Models'
import Evaluations from './pages/Evaluations'
import Results from './pages/Results'
import SyntheticMonitoring from './pages/SyntheticMonitoring'
import ErrorPage from './pages/ErrorPage'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/models" element={<Models />} />
          <Route path="/evaluations" element={<Evaluations />} />
          <Route path="/results" element={<Results />} />
          <Route path="/synthetic-monitoring" element={<SyntheticMonitoring />} />
          <Route path="/error" element={<ErrorPage />} />
          <Route path="*" element={<ErrorPage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
