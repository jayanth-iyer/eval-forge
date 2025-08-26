import React, { useState, useEffect } from 'react'
import { Plus, Play, Upload, FileText, Loader } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const Evaluations = () => {
  const [evaluations, setEvaluations] = useState([])
  const [models, setModels] = useState([])
  const [showCreateEval, setShowCreateEval] = useState(false)
  const [loading, setLoading] = useState(false)
  const [uploadingDataset, setUploadingDataset] = useState(false)
  const navigate = useNavigate()

  const [newEvaluation, setNewEvaluation] = useState({
    name: '',
    model_id: '',
    dataset_file: null,
    use_sample: false,
    temperature: 0.7,
    max_tokens: 512,
    top_p: 0.9
  })

  useEffect(() => {
    fetchEvaluations()
    fetchModels()
  }, [])

  const fetchEvaluations = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/evaluations')
      if (response.ok) {
        const data = await response.json()
        setEvaluations(data)
      }
    } catch (error) {
      navigate('/error')
    }
  }

  const fetchModels = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/models')
      if (response.ok) {
        const data = await response.json()
        setModels(data.filter(model => model.status === 'connected'))
      }
    } catch (error) {
      navigate('/error')
    }
  }

  const handleCreateEvaluation = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('name', newEvaluation.name)
      formData.append('model_id', newEvaluation.model_id)
      formData.append('use_sample', newEvaluation.use_sample)
      formData.append('temperature', newEvaluation.temperature)
      formData.append('max_tokens', newEvaluation.max_tokens)
      formData.append('top_p', newEvaluation.top_p)
      
      if (newEvaluation.dataset_file) {
        formData.append('dataset_file', newEvaluation.dataset_file)
      }

      const response = await fetch('http://localhost:8000/api/evaluations', {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        await fetchEvaluations()
        setShowCreateEval(false)
        setNewEvaluation({
          name: '',
          model_id: '',
          dataset_file: null,
          use_sample: false,
          temperature: 0.7,
          max_tokens: 512,
          top_p: 0.9
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

  const runEvaluation = async (evaluationId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/evaluations/${evaluationId}/run`, {
        method: 'POST'
      })
      if (response.ok) {
        await fetchEvaluations()
      } else {
        navigate('/error')
      }
    } catch (error) {
      navigate('/error')
    }
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file && file.type === 'text/csv') {
      setNewEvaluation({...newEvaluation, dataset_file: file, use_sample: false})
    } else if (file) {
      alert('Please select a CSV file')
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'running':
        return 'bg-blue-100 text-blue-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Evaluations</h1>
          <p className="mt-2 text-sm text-gray-700">
            Create and manage model evaluations with custom datasets.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            type="button"
            onClick={() => setShowCreateEval(true)}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 sm:w-auto"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Evaluation
          </button>
        </div>
      </div>

      {/* Evaluations List */}
      <div className="mt-8 flex flex-col">
        <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Evaluation
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Model
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Questions
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Accuracy
                    </th>
                    <th className="relative px-6 py-3">
                      <span className="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {evaluations.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-6 py-4 text-center text-sm text-gray-500">
                        No evaluations created yet. Create your first evaluation to get started.
                      </td>
                    </tr>
                  ) : (
                    evaluations.map((evaluation) => (
                      <tr key={evaluation.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{evaluation.name}</div>
                          <div className="text-sm text-gray-500">
                            {new Date(evaluation.created_at).toLocaleDateString()}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {evaluation.model_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(evaluation.status)}`}>
                            {evaluation.status === 'running' && <Loader className="w-3 h-3 mr-1 animate-spin" />}
                            {evaluation.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {evaluation.total_questions || 0}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {evaluation.accuracy ? `${(evaluation.accuracy * 100).toFixed(1)}%` : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          {evaluation.status === 'draft' && (
                            <button
                              onClick={() => runEvaluation(evaluation.id)}
                              className="text-blue-600 hover:text-blue-900 mr-4"
                            >
                              <Play className="w-4 h-4" />
                            </button>
                          )}
                          {evaluation.status === 'completed' && (
                            <button
                              onClick={() => navigate(`/results?eval=${evaluation.id}`)}
                              className="text-green-600 hover:text-green-900"
                            >
                              View Results
                            </button>
                          )}
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

      {/* Create Evaluation Modal */}
      {showCreateEval && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Evaluation</h3>
              <form onSubmit={handleCreateEvaluation}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Evaluation Name</label>
                    <input
                      type="text"
                      required
                      value={newEvaluation.name}
                      onChange={(e) => setNewEvaluation({...newEvaluation, name: e.target.value})}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="e.g., Basic QA Test"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Model</label>
                    <select
                      required
                      value={newEvaluation.model_id}
                      onChange={(e) => setNewEvaluation({...newEvaluation, model_id: e.target.value})}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    >
                      <option value="">Select a model</option>
                      {models.map((model) => (
                        <option key={model.id} value={model.id}>{model.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Dataset Section */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Dataset</label>
                  <div className="space-y-3">
                    <div className="flex items-center">
                      <input
                        type="radio"
                        id="sample"
                        name="dataset"
                        checked={newEvaluation.use_sample}
                        onChange={(e) => setNewEvaluation({...newEvaluation, use_sample: true, dataset_file: null})}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                      />
                      <label htmlFor="sample" className="ml-3 block text-sm font-medium text-gray-700">
                        Use Sample Dataset (10 questions)
                      </label>
                    </div>
                    <div className="flex items-center">
                      <input
                        type="radio"
                        id="upload"
                        name="dataset"
                        checked={!newEvaluation.use_sample}
                        onChange={(e) => setNewEvaluation({...newEvaluation, use_sample: false})}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                      />
                      <label htmlFor="upload" className="ml-3 block text-sm font-medium text-gray-700">
                        Upload CSV Dataset
                      </label>
                    </div>
                    {!newEvaluation.use_sample && (
                      <div className="ml-7">
                        <input
                          type="file"
                          accept=".csv"
                          onChange={handleFileChange}
                          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        />
                        <p className="mt-1 text-xs text-gray-500">
                          CSV format: question,answer (one question per row)
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Parameters */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Temperature</label>
                    <input
                      type="number"
                      min="0"
                      max="2"
                      step="0.1"
                      value={newEvaluation.temperature}
                      onChange={(e) => setNewEvaluation({...newEvaluation, temperature: parseFloat(e.target.value)})}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Max Tokens</label>
                    <input
                      type="number"
                      min="1"
                      max="4096"
                      value={newEvaluation.max_tokens}
                      onChange={(e) => setNewEvaluation({...newEvaluation, max_tokens: parseInt(e.target.value)})}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Top P</label>
                    <input
                      type="number"
                      min="0"
                      max="1"
                      step="0.1"
                      value={newEvaluation.top_p}
                      onChange={(e) => setNewEvaluation({...newEvaluation, top_p: parseFloat(e.target.value)})}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                </div>

                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowCreateEval(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {loading ? 'Creating...' : 'Create Evaluation'}
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

export default Evaluations
