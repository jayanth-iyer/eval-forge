import React, { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, Globe, Shield, Clock, CheckCircle, XCircle, Settings, List } from 'lucide-react'

const ExternalApps = () => {
  const [apps, setApps] = useState([])
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingApp, setEditingApp] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [appEndpoints, setAppEndpoints] = useState({})

  useEffect(() => {
    fetchApps()
  }, [])

  const fetchApps = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/external-apps')
      if (response.ok) {
        const data = await response.json()
        setApps(data)
        // Fetch endpoints for each app
        const endpointsData = {}
        for (const app of data) {
          try {
            const endpointsResponse = await fetch(`http://localhost:8000/api/external-apps/${app.id}/endpoints`)
            if (endpointsResponse.ok) {
              endpointsData[app.id] = await endpointsResponse.json()
            }
          } catch (err) {
            console.warn(`Failed to fetch endpoints for app ${app.id}:`, err)
          }
        }
        setAppEndpoints(endpointsData)
      } else {
        throw new Error('Failed to fetch apps')
      }
    } catch (error) {
      console.error('Error fetching apps:', error)
      setError('Something went wrong while loading apps')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (appId) => {
    if (!confirm('Are you sure you want to delete this app configuration?')) {
      return
    }

    try {
      const response = await fetch(`http://localhost:8000/api/external-apps/${appId}`, {
        method: 'DELETE',
      })
      
      if (response.ok) {
        fetchApps()
      } else {
        throw new Error('Failed to delete app')
      }
    } catch (error) {
      console.error('Error deleting app:', error)
      setError('Something went wrong while deleting app')
    }
  }

  const handleEdit = (app) => {
    setEditingApp(app)
    setShowCreateModal(true)
  }

  const handleModalClose = () => {
    setShowCreateModal(false)
    setEditingApp(null)
  }

  const handleModalSuccess = () => {
    setShowCreateModal(false)
    setEditingApp(null)
    fetchApps()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading external apps...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">External Apps</h1>
          <p className="text-gray-600 mt-1">
            Configure external applications and APIs for monitoring
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add App
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Apps Grid */}
      {apps.length === 0 ? (
        <div className="text-center py-12">
          <Globe className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No external apps configured</h3>
          <p className="text-gray-500 mb-4">
            Add your first external app to start monitoring its health and performance.
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Add Your First App
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {apps.map((app) => (
            <AppCard
              key={app.id}
              app={app}
              endpoints={appEndpoints[app.id] || []}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      {showCreateModal && (
        <CreateAppModal
          app={editingApp}
          endpoints={editingApp ? appEndpoints[editingApp.id] || [] : []}
          onClose={handleModalClose}
          onSuccess={handleModalSuccess}
        />
      )}
    </div>
  )
}

// App Card Component
const AppCard = ({ app, endpoints, onEdit, onDelete }) => {
  const getAuthIcon = (authType) => {
    if (authType === 'none') return null
    return <Shield className="w-4 h-4 text-green-500" />
  }

  const getStatusIcon = (isActive) => {
    return isActive ? 
      <CheckCircle className="w-4 h-4 text-green-500" /> : 
      <XCircle className="w-4 h-4 text-gray-400" />
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-2">
          <Globe className="w-5 h-5 text-blue-500" />
          <h3 className="font-semibold text-gray-900">{app.name}</h3>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => onEdit(app)}
            className="p-1 text-gray-400 hover:text-blue-600"
          >
            <Edit className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(app.id)}
            className="p-1 text-gray-400 hover:text-red-600"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-sm text-gray-500">Service Name</p>
          <p className="text-sm font-medium text-gray-900">{app.service_name}</p>
        </div>

        <div>
          <p className="text-sm text-gray-500">Base URL</p>
          <p className="text-sm font-medium text-gray-900 truncate">{app.base_url}</p>
        </div>

        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <p className="text-sm text-gray-500">Authentication</p>
            {getAuthIcon(app.auth_type)}
          </div>
          <div className="flex items-center gap-2">
            <p className="text-sm text-gray-500">Status</p>
            {getStatusIcon(app.is_active)}
          </div>
        </div>

        {app.description && (
          <div>
            <p className="text-sm text-gray-500">Description</p>
            <p className="text-sm text-gray-700">{app.description}</p>
          </div>
        )}
        
        <div>
          <p className="text-sm text-gray-500">API Endpoints</p>
          <div className="flex items-center gap-2">
            <List className="w-4 h-4 text-blue-500" />
            <p className="text-sm font-medium text-gray-900">
              {endpoints.length} endpoint{endpoints.length !== 1 ? 's' : ''} configured
            </p>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100">
        <button
          onClick={() => onEdit(app)}
          className="w-full bg-gray-50 text-gray-700 px-3 py-2 rounded-md hover:bg-gray-100 text-sm font-medium flex items-center justify-center gap-2"
        >
          <Settings className="w-4 h-4" />
          Configure App & Endpoints
        </button>
      </div>
    </div>
  )
}

// Create/Edit App Modal Component
const CreateAppModal = ({ app, endpoints, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: app?.name || '',
    service_name: app?.service_name || '',
    base_url: app?.base_url || '',
    description: app?.description || '',
    auth_type: app?.auth_type || 'none',
    auth_credentials: '',
    is_active: app?.is_active ?? true,
    timeout: app?.timeout || 30,
    ssl_check_enabled: app?.ssl_check_enabled ?? false
  })
  const [appEndpoints, setAppEndpoints] = useState(endpoints || [])
  const [showEndpointForm, setShowEndpointForm] = useState(false)
  const [editingEndpoint, setEditingEndpoint] = useState(null)
  const [error, setError] = useState(null)

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

      const url = app ? 
        `http://localhost:8000/api/external-apps/${app.id}` : 
        'http://localhost:8000/api/external-apps'
      
      const method = app ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(processedData),
      })
      
      if (response.ok) {
        const savedApp = await response.json()
        
        // If this is a new app and we have endpoints configured, create them
        if (!app && appEndpoints.length > 0) {
          for (const endpoint of appEndpoints) {
            try {
              const endpointPayload = {
                ...endpoint,
                external_app_id: savedApp.id
              }
              // Remove temporary ID
              delete endpointPayload.id
              
              await fetch(`http://localhost:8000/api/external-apps/${savedApp.id}/endpoints`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify(endpointPayload),
              })
            } catch (endpointError) {
              console.warn('Failed to create endpoint:', endpointError)
              // Continue with other endpoints even if one fails
            }
          }
        }
        
        onSuccess()
        setError(null)
      } else {
        throw new Error(`Failed to ${app ? 'update' : 'create'} app`)
      }
    } catch (error) {
      console.error(`Error ${app ? 'updating' : 'creating'} app:`, error)
      setError('Something went wrong while saving app')
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          {app ? 'Edit External App - Multiple Endpoints' : 'Add External App - Multiple Endpoints'}
        </h2>
        
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              App Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="My E-commerce App"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Service Name *
            </label>
            <input
              type="text"
              value={formData.service_name}
              onChange={(e) => setFormData({ ...formData, service_name: e.target.value })}
              placeholder="E-commerce API Service"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Base URL *
            </label>
            <input
              type="url"
              value={formData.base_url}
              onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
              placeholder="https://api.example.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>


          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Brief description of this application..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
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

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Timeout (seconds)
            </label>
            <input
              type="number"
              value={formData.timeout}
              onChange={(e) => setFormData({ ...formData, timeout: parseInt(e.target.value) })}
              min="1"
              max="300"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

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
            
            {formData.base_url.startsWith('https://') && (
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

          {/* API Endpoints Section */}
          <div className="border-t border-gray-200 pt-4">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-medium text-gray-900">API Endpoints</h3>
              <button
                type="button"
                onClick={() => setShowEndpointForm(true)}
                className="bg-green-600 text-white px-3 py-1 rounded-md hover:bg-green-700 text-sm flex items-center gap-1"
              >
                <Plus className="w-3 h-3" />
                Add Endpoint
              </button>
            </div>
            
            {appEndpoints.length === 0 ? (
              <div className="text-center py-6 bg-gray-50 rounded-md">
                <List className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-500">No endpoints configured</p>
                <p className="text-xs text-gray-400">Add your first API endpoint to start monitoring</p>
              </div>
            ) : (
              <div className="space-y-2">
                {appEndpoints.map((endpoint) => (
                  <EndpointCard
                    key={endpoint.id || `new-${endpoint.name}`}
                    endpoint={endpoint}
                    onEdit={(ep) => {
                      setEditingEndpoint(ep)
                      setShowEndpointForm(true)
                    }}
                    onDelete={(epId) => handleDeleteEndpoint(epId)}
                  />
                ))}
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
              {app ? 'Update App' : 'Add App'}
            </button>
          </div>
        </form>
        
        {/* Endpoint Form Modal */}
        {showEndpointForm && (
          <EndpointFormModal
            appId={app?.id}
            endpoint={editingEndpoint}
            isNewApp={!app}
            onClose={() => {
              setShowEndpointForm(false)
              setEditingEndpoint(null)
            }}
            onSuccess={(newEndpoint) => {
              if (editingEndpoint) {
                setAppEndpoints(prev => prev.map(ep => ep.id === editingEndpoint.id ? newEndpoint : ep))
              } else {
                setAppEndpoints(prev => [...prev, newEndpoint])
              }
              setShowEndpointForm(false)
              setEditingEndpoint(null)
            }}
          />
        )}
      </div>
    </div>
  )
  
  async function handleDeleteEndpoint(endpointId) {
    if (!confirm('Are you sure you want to delete this endpoint?')) {
      return
    }
    
    try {
      const response = await fetch(`http://localhost:8000/api/external-app-endpoints/${endpointId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        setAppEndpoints(prev => prev.filter(ep => ep.id !== endpointId))
      } else {
        throw new Error('Failed to delete endpoint')
      }
    } catch (error) {
      console.error('Error deleting endpoint:', error)
      setError('Something went wrong while deleting endpoint')
    }
  }
}

// Endpoint Card Component
const EndpointCard = ({ endpoint, onEdit, onDelete }) => {
  const getMethodColor = (method) => {
    const colors = {
      GET: 'bg-green-100 text-green-800',
      POST: 'bg-blue-100 text-blue-800',
      PUT: 'bg-yellow-100 text-yellow-800',
      DELETE: 'bg-red-100 text-red-800',
      PATCH: 'bg-purple-100 text-purple-800'
    }
    return colors[method] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="border border-gray-200 rounded-md p-3 bg-white">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className={`px-2 py-1 rounded text-xs font-medium ${getMethodColor(endpoint.method)}`}>
              {endpoint.method}
            </span>
            <span className="font-medium text-gray-900">{endpoint.name}</span>
          </div>
          <p className="text-sm text-gray-600 font-mono">{endpoint.endpoint_path}</p>
          {endpoint.description && (
            <p className="text-xs text-gray-500 mt-1">{endpoint.description}</p>
          )}
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => onEdit(endpoint)}
            className="p-1 text-gray-400 hover:text-blue-600"
          >
            <Edit className="w-3 h-3" />
          </button>
          <button
            onClick={() => onDelete(endpoint.id)}
            className="p-1 text-gray-400 hover:text-red-600"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>
  )
}

// Endpoint Form Modal Component
const EndpointFormModal = ({ appId, endpoint, isNewApp, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: endpoint?.name || '',
    endpoint_path: endpoint?.endpoint_path || '',
    method: endpoint?.method || 'GET',
    description: endpoint?.description || '',
    headers: endpoint?.headers || '',
    body: endpoint?.body || '',
    expected_status: endpoint?.expected_status || 200,
    expected_response_contains: endpoint?.expected_response_contains || '',
    timeout: endpoint?.timeout || null,
    is_active: endpoint?.is_active ?? true
  })
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      // For new apps, just store the endpoint locally without making API calls
      if (isNewApp) {
        const newEndpoint = {
          ...formData,
          id: `temp-${Date.now()}`, // Temporary ID for local storage
          external_app_id: null // Will be set when app is created
        }
        onSuccess(newEndpoint)
        return
      }

      // For existing apps, make API calls as before
      const url = endpoint ? 
        `http://localhost:8000/api/external-app-endpoints/${endpoint.id}` : 
        `http://localhost:8000/api/external-apps/${appId}/endpoints`
      
      const method = endpoint ? 'PUT' : 'POST'
      const payload = { ...formData }
      if (!endpoint) {
        payload.external_app_id = appId
      }
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })
      
      if (response.ok) {
        const result = await response.json()
        onSuccess(result)
      } else {
        throw new Error(`Failed to ${endpoint ? 'update' : 'create'} endpoint`)
      }
    } catch (error) {
      console.error(`Error ${endpoint ? 'updating' : 'creating'} endpoint:`, error)
      setError('Something went wrong while saving endpoint')
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60">
      <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <h3 className="text-lg font-bold text-gray-900 mb-4">
          {endpoint ? 'Edit Endpoint' : 'Add Endpoint'}
        </h3>
        
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Endpoint Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Health Check"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Endpoint Path *
            </label>
            <input
              type="text"
              value={formData.endpoint_path}
              onChange={(e) => setFormData({ ...formData, endpoint_path: e.target.value })}
              placeholder="/health"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              HTTP Method
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
              <option value="PATCH">PATCH</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Optional description"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Expected Status Code
            </label>
            <input
              type="number"
              value={formData.expected_status}
              onChange={(e) => setFormData({ ...formData, expected_status: parseInt(e.target.value) })}
              min="100"
              max="599"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="endpoint_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="endpoint_active" className="text-sm text-gray-700">
              Active
            </label>
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
              {endpoint ? 'Update' : 'Add'} Endpoint
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ExternalApps
