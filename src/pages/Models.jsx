import React, { useState, useEffect } from 'react'
import { Plus, Settings, Trash2, CheckCircle, XCircle, Loader } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const Models = () => {
  const [models, setModels] = useState([])
  const [showAddModel, setShowAddModel] = useState(false)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const [newModel, setNewModel] = useState({
    name: '',
    type: 'ollama',
    endpoint: 'http://localhost:11434',
    model_name: ''
  })

  useEffect(() => {
    fetchModels()
  }, [])

  const fetchModels = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/models')
      if (response.ok) {
        const data = await response.json()
        setModels(data)
      }
    } catch (error) {
      navigate('/error')
    }
  }

  const handleAddModel = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await fetch('http://localhost:8000/api/models', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newModel),
      })

      if (response.ok) {
        await fetchModels()
        setShowAddModel(false)
        setNewModel({
          name: '',
          type: 'ollama',
          endpoint: 'http://localhost:11434',
          model_name: ''
        })
      } else {
        navigate('/error')
      }
    } catch (error) {
      navigate('/error')
    } finally {
      setLoading(false)
    }
  }

  const testConnection = async (modelId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/models/${modelId}/test`)
      if (!response.ok) {
        navigate('/error')
      }
      await fetchModels()
    } catch (error) {
      navigate('/error')
    }
  }

  const deleteModel = async (modelId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/models/${modelId}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        await fetchModels()
      } else {
        navigate('/error')
      }
    } catch (error) {
      navigate('/error')
    }
  }

  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Models</h1>
          <p className="mt-2 text-sm text-gray-700">
            Configure and manage your LLM models for evaluation.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            type="button"
            onClick={() => setShowAddModel(true)}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 sm:w-auto"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Model
          </button>
        </div>
      </div>

      {/* Models List */}
      <div className="mt-8 flex flex-col">
        <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Model
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="relative px-6 py-3">
                      <span className="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {models.length === 0 ? (
                    <tr>
                      <td colSpan="4" className="px-6 py-4 text-center text-sm text-gray-500">
                        No models configured. Add your first model to get started.
                      </td>
                    </tr>
                  ) : (
                    models.map((model) => (
                      <tr key={model.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{model.name}</div>
                            <div className="text-sm text-gray-500">{model.model_name}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {model.type}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            model.status === 'connected' 
                              ? 'bg-green-100 text-green-800' 
                              : model.status === 'error'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {model.status === 'connected' && <CheckCircle className="w-3 h-3 mr-1" />}
                            {model.status === 'error' && <XCircle className="w-3 h-3 mr-1" />}
                            {model.status === 'testing' && <Loader className="w-3 h-3 mr-1 animate-spin" />}
                            {model.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => testConnection(model.id)}
                            className="text-blue-600 hover:text-blue-900 mr-4"
                          >
                            Test
                          </button>
                          <button
                            onClick={() => deleteModel(model.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Add Model Modal */}
      {showAddModel && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Model</h3>
              <form onSubmit={handleAddModel}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Display Name</label>
                  <input
                    type="text"
                    required
                    value={newModel.name}
                    onChange={(e) => setNewModel({...newModel, name: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="e.g., Llama 3.2 Local"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Type</label>
                  <select
                    value={newModel.type}
                    onChange={(e) => setNewModel({...newModel, type: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  >
                    <option value="ollama">Ollama</option>
                  </select>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Endpoint</label>
                  <input
                    type="url"
                    required
                    value={newModel.endpoint}
                    onChange={(e) => setNewModel({...newModel, endpoint: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="http://localhost:11434"
                  />
                </div>
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700">Model Name</label>
                  <input
                    type="text"
                    required
                    value={newModel.model_name}
                    onChange={(e) => setNewModel({...newModel, model_name: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="llama3.2"
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowAddModel(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {loading ? 'Adding...' : 'Add Model'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Models
