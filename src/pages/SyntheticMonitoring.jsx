import React, { useState, useEffect } from 'react'
import { Plus, Play, Trash2, Edit, Clock, CheckCircle, XCircle, AlertTriangle, BarChart3 } from 'lucide-react'

const SyntheticMonitoring = () => {
  const [activeFeature, setActiveFeature] = useState('user-journey')
  const [tests, setTests] = useState([])
  const [executions, setExecutions] = useState([])
  const [metrics, setMetrics] = useState({ uptime: {}, api: {}, browser: {} })
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const features = [
    { id: 'user-journey', name: 'User Journey Simulation', icon: Play },
    { id: 'monitoring-types', name: 'Monitoring Types', icon: CheckCircle },
    { id: 'test-results', name: 'Test Results', icon: BarChart3 },
  ]

  // Fetch tests, executions, and metrics
  useEffect(() => {
    fetchTests()
    fetchExecutions()
    fetchMetrics()
  }, [])

  const fetchTests = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/synthetic-tests')
      if (!response.ok) throw new Error('Failed to fetch tests')
      const data = await response.json()
      setTests(data)
      setError(null)
    } catch (error) {
      console.error('Error fetching tests:', error)
      setError('Something went wrong while fetching tests')
    }
  }

  const fetchExecutions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/synthetic-executions')
      if (!response.ok) throw new Error('Failed to fetch executions')
      const data = await response.json()
      setExecutions(data)
      setError(null)
    } catch (error) {
      console.error('Error fetching executions:', error)
      setError('Something went wrong while fetching executions')
    }
  }

  const fetchMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/synthetic-monitoring/metrics')
      if (!response.ok) throw new Error('Failed to fetch metrics')
      const data = await response.json()
      setMetrics(data)
      setError(null)
    } catch (error) {
      console.error('Error fetching metrics:', error)
      setError('Something went wrong while fetching metrics')
    }
  }

  const executeTest = async (testId) => {
    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/api/synthetic-tests/${testId}/execute`, {
        method: 'POST'
      })
      if (!response.ok) throw new Error('Failed to execute test')
      await fetchExecutions()
      await fetchMetrics()
      setError(null)
    } catch (error) {
      console.error('Error executing test:', error)
      setError('Something went wrong while executing test')
    }
    setLoading(false)
  }

  const deleteTest = async (testId) => {
    if (!confirm('Are you sure you want to delete this test?')) return
    
    try {
      const response = await fetch(`http://localhost:8000/api/synthetic-tests/${testId}`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('Failed to delete test')
      await fetchTests()
      await fetchExecutions()
      await fetchMetrics()
      setError(null)
    } catch (error) {
      console.error('Error deleting test:', error)
      setError('Something went wrong while deleting test')
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'failure':
        return <XCircle className="w-4 h-4 text-red-500" />
      case 'timeout':
        return <Clock className="w-4 h-4 text-yellow-500" />
      case 'error':
        return <AlertTriangle className="w-4 h-4 text-red-500" />
      default:
        return <Clock className="w-4 h-4 text-gray-500" />
    }
  }

  const renderUserJourneySimulation = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">User Journey Simulation</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Create Test
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tests.map((test) => (
          <div key={test.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{test.name}</h3>
                <p className="text-sm text-gray-500 capitalize">{test.test_type} Test</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => executeTest(test.id)}
                  disabled={loading}
                  className="text-blue-600 hover:text-blue-800 disabled:opacity-50"
                >
                  <Play className="w-4 h-4" />
                </button>
                <button
                  onClick={() => deleteTest(test.id)}
                  className="text-red-600 hover:text-red-800"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <div className="space-y-2">
              <p className="text-sm text-gray-600">
                <span className="font-medium">URL:</span> {test.url}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Method:</span> {test.method}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Interval:</span> {test.interval}s
              </p>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-600">Status:</span>
                <span className={`px-2 py-1 rounded-full text-xs ${
                  test.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {test.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  const renderMonitoringTypes = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Monitoring Types</h2>
      
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Uptime Monitoring</h3>
          <p className="text-gray-600 mb-4">Basic availability checks for your endpoints</p>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Active Tests:</span>
              <span className="text-sm font-medium">{tests.filter(t => t.test_type === 'uptime').length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Success Rate:</span>
              <span className="text-sm font-medium text-green-600">
                {metrics.uptime.success_rate ? `${metrics.uptime.success_rate}%` : '0%'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Total Tests (24h):</span>
              <span className="text-sm font-medium">{metrics.uptime.total_tests || 0}</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">API Monitoring</h3>
          <p className="text-gray-600 mb-4">Test REST/GraphQL endpoints with validation</p>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Active Tests:</span>
              <span className="text-sm font-medium">{tests.filter(t => t.test_type === 'api').length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Avg Response:</span>
              <span className="text-sm font-medium text-blue-600">
                {metrics.api.avg_response_time ? `${Math.round(metrics.api.avg_response_time)}ms` : '0ms'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Success Rate:</span>
              <span className="text-sm font-medium text-green-600">
                {metrics.api.success_rate ? `${metrics.api.success_rate}%` : '0%'}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Browser Automation</h3>
          <p className="text-gray-600 mb-4">End-to-end user journey testing</p>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Active Tests:</span>
              <span className="text-sm font-medium">{tests.filter(t => t.test_type === 'browser').length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Success Rate:</span>
              <span className="text-sm font-medium text-green-600">
                {metrics.browser.success_rate ? `${metrics.browser.success_rate}%` : '0%'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Status:</span>
              <span className="text-sm font-medium text-yellow-600">Coming Soon</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderTestResults = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Test Results</h2>
      
      <div className="bg-white rounded-lg shadow-md">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Recent Executions</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Test
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Response Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Executed At
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Error
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {executions.slice(0, 10).map((execution) => {
                const test = tests.find(t => t.id === execution.test_id)
                return (
                  <tr key={execution.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {test?.name || 'Unknown Test'}
                      </div>
                      <div className="text-sm text-gray-500">{test?.url}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(execution.status)}
                        <span className="text-sm text-gray-900 capitalize">
                          {execution.status}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {Math.round(execution.response_time)}ms
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(execution.executed_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                      {execution.error_message || '-'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )

  const renderContent = () => {
    switch (activeFeature) {
      case 'user-journey':
        return renderUserJourneySimulation()
      case 'monitoring-types':
        return renderMonitoringTypes()
      case 'test-results':
        return renderTestResults()
      default:
        return renderUserJourneySimulation()
    }
  }

  return (
    <div className="flex h-full">
      {/* Left Sidebar */}
      <div className="w-64 bg-white shadow-sm border-r border-gray-200">
        <div className="p-6">
          <h1 className="text-xl font-bold text-gray-900">Synthetic Monitoring</h1>
        </div>
        <nav className="px-4 space-y-2">
          {features.map((feature) => {
            const Icon = feature.icon
            return (
              <button
                key={feature.id}
                onClick={() => setActiveFeature(feature.id)}
                className={`w-full flex items-center gap-3 px-4 py-2 text-left rounded-md transition-colors ${
                  activeFeature === feature.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-5 h-5" />
                {feature.name}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-8">
        {renderContent()}
      </div>

      {/* Create Test Modal */}
      {showCreateModal && (
        <CreateTestModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            fetchTests()
          }}
        />
      )}
    </div>
  )
}

// Create Test Modal Component
const CreateTestModal = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    service_name: '',
    test_type: 'api',
    url: '',
    method: 'GET',
    expected_status: 200,
    expected_response_contains: '',
    timeout: 30,
    interval: 300,
    is_active: true,
    auth_type: 'none',
    auth_credentials: '',
    ssl_check_enabled: false
  })
  const [externalApps, setExternalApps] = useState([])
  const [selectedApp, setSelectedApp] = useState('')
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchExternalApps()
  }, [])

  const fetchExternalApps = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/external-apps')
      if (response.ok) {
        const data = await response.json()
        setExternalApps(data.filter(app => app.is_active))
      }
    } catch (error) {
      console.error('Error fetching external apps:', error)
    }
  }

  const handleAppSelection = (appId) => {
    const app = externalApps.find(a => a.id === parseInt(appId))
    if (app) {
      setFormData({
        ...formData,
        service_name: app.service_name,
        url: app.base_url + app.health_endpoint,
        auth_type: app.auth_type,
        auth_credentials: app.auth_type !== 'none' ? '***' : '',
        timeout: app.timeout,
        ssl_check_enabled: app.ssl_check_enabled
      })
    } else {
      // Reset to manual configuration
      setFormData({
        ...formData,
        service_name: '',
        url: '',
        auth_type: 'none',
        auth_credentials: '',
        timeout: 30,
        ssl_check_enabled: false
      })
    }
    setSelectedApp(appId)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      // Prepare auth credentials as JSON if provided
      let processedData = { ...formData }
      if (formData.auth_type !== 'none' && formData.auth_credentials) {
        if (formData.auth_type === 'api_key') {
          processedData.auth_credentials = JSON.stringify({
            header_name: 'X-API-Key',
            key: formData.auth_credentials
          })
        } else if (formData.auth_type === 'bearer_token') {
          processedData.auth_credentials = JSON.stringify({
            token: formData.auth_credentials
          })
        }
      } else {
        processedData.auth_credentials = null
      }
      
      const response = await fetch('http://localhost:8000/api/synthetic-tests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(processedData),
      })
      
      if (response.ok) {
        onSuccess()
        setError(null)
      } else {
        throw new Error('Failed to create test')
      }
    } catch (error) {
      console.error('Error creating test:', error)
      setError('Something went wrong while creating test')
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Create Synthetic Test</h2>
        
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Test Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Configure From External App
            </label>
            <select
              value={selectedApp}
              onChange={(e) => handleAppSelection(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Manual Configuration</option>
              {externalApps.map((app) => (
                <option key={app.id} value={app.id}>
                  {app.name} ({app.service_name})
                </option>
              ))}
            </select>
            {externalApps.length === 0 && (
              <p className="text-sm text-gray-500 mt-1">
                No external apps configured. <a href="/external-apps" className="text-blue-600 hover:underline">Add one here</a>.
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              External Service Name
            </label>
            <input
              type="text"
              value={formData.service_name}
              onChange={(e) => setFormData({ ...formData, service_name: e.target.value })}
              placeholder="e.g., My E-commerce API"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              disabled={selectedApp !== ''}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Test Type
            </label>
            <select
              value={formData.test_type}
              onChange={(e) => setFormData({ ...formData, test_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="api">API Test</option>
              <option value="uptime">Uptime Test</option>
              <option value="browser">Browser Test</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              URL
            </label>
            <input
              type="url"
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              placeholder="https://api.example.com/health"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              disabled={selectedApp !== ''}
            />
            {selectedApp !== '' && (
              <p className="text-sm text-gray-500 mt-1">
                URL configured from selected external app
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Expected Response Contains (Optional)
            </label>
            <input
              type="text"
              value={formData.expected_response_contains}
              onChange={(e) => setFormData({ ...formData, expected_response_contains: e.target.value })}
              placeholder="success, OK, healthy"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Method
              </label>
              <select
                value={formData.method}
                onChange={(e) => setFormData({ ...formData, method: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="GET">GET</option>
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="DELETE">DELETE</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Expected Status
              </label>
              <input
                type="number"
                value={formData.expected_status}
                onChange={(e) => setFormData({ ...formData, expected_status: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Timeout (seconds)
              </label>
              <input
                type="number"
                value={formData.timeout}
                onChange={(e) => setFormData({ ...formData, timeout: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Interval (seconds)
              </label>
              <input
                type="number"
                value={formData.interval}
                onChange={(e) => setFormData({ ...formData, interval: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Authentication
            </label>
            <select
              value={formData.auth_type}
              onChange={(e) => setFormData({ ...formData, auth_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="none">No Authentication</option>
              <option value="api_key">API Key</option>
              <option value="bearer_token">Bearer Token</option>
            </select>
          </div>

          {formData.auth_type !== 'none' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {formData.auth_type === 'api_key' ? 'API Key' : 'Bearer Token'}
              </label>
              <input
                type="password"
                value={formData.auth_credentials}
                onChange={(e) => setFormData({ ...formData, auth_credentials: e.target.value })}
                placeholder={formData.auth_type === 'api_key' ? 'your-api-key' : 'your-bearer-token'}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="is_active" className="text-sm text-gray-700">
                Active
              </label>
            </div>
            
            {formData.test_type === 'uptime' && formData.url.startsWith('https://') && (
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="ssl_check"
                  checked={formData.ssl_check_enabled}
                  onChange={(e) => setFormData({ ...formData, ssl_check_enabled: e.target.checked })}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="ssl_check" className="text-sm text-gray-700">
                  SSL Check
                </label>
              </div>
            )}
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Create Test
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default SyntheticMonitoring
