import React, { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { CheckCircle, XCircle, Clock, Eye } from 'lucide-react'

const Results = () => {
  const [results, setResults] = useState([])
  const [detailView, setDetailView] = useState(null)
  const [filter, setFilter] = useState('all')
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  useEffect(() => {
    fetchResults()
    const evalId = searchParams.get('eval')
    if (evalId) {
      fetchEvaluationDetails(evalId)
    }
  }, [searchParams])

  const fetchResults = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/results')
      if (response.ok) {
        const data = await response.json()
        setResults(data)
      }
    } catch (error) {
      navigate('/error')
    }
  }

  const fetchEvaluationDetails = async (evalId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/results/${evalId}`)
      if (response.ok) {
        const data = await response.json()
        setDetailView(data)
      }
    } catch (error) {
      navigate('/error')
    }
  }

  const deleteResult = async (resultId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/results/${resultId}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        await fetchResults()
      } else {
        navigate('/error')
      }
    } catch (error) {
      navigate('/error')
    }
  }

  const filteredQuestions = detailView?.questions?.filter(q => {
    if (filter === 'correct') return q.is_correct
    if (filter === 'incorrect') return !q.is_correct
    return true
  }) || []

  if (detailView) {
    return (
      <div>
        <div className="mb-6">
          <button
            onClick={() => setDetailView(null)}
            className="text-blue-600 hover:text-blue-800 mb-4"
          >
            ← Back to Results
          </button>
          <h1 className="text-2xl font-semibold text-gray-900">{detailView.evaluation_name}</h1>
          <p className="text-gray-600">Detailed Results</p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-2xl font-bold text-gray-900">
              {(detailView.accuracy * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Overall Accuracy</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-2xl font-bold text-green-600">{detailView.correct_answers}</div>
            <div className="text-sm text-gray-600">Correct Answers</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-2xl font-bold text-red-600">{detailView.incorrect_answers}</div>
            <div className="text-sm text-gray-600">Incorrect Answers</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-2xl font-bold text-gray-900">{detailView.total_questions}</div>
            <div className="text-sm text-gray-600">Total Questions</div>
          </div>
        </div>

        {/* Filter Controls */}
        <div className="mb-4 flex space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-2 rounded-md text-sm ${
              filter === 'all' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-700'
            }`}
          >
            All Questions
          </button>
          <button
            onClick={() => setFilter('correct')}
            className={`px-3 py-2 rounded-md text-sm ${
              filter === 'correct' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-700'
            }`}
          >
            Correct Only
          </button>
          <button
            onClick={() => setFilter('incorrect')}
            className={`px-3 py-2 rounded-md text-sm ${
              filter === 'incorrect' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-700'
            }`}
          >
            Incorrect Only
          </button>
        </div>

        {/* Questions List */}
        <div className="space-y-4">
          {filteredQuestions.map((question, index) => (
            <div key={index} className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  {question.is_correct ? (
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-500 mr-2" />
                  )}
                  <span className="font-medium">Question {index + 1}</span>
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <Clock className="w-4 h-4 mr-1" />
                  {question.response_time}ms
                </div>
              </div>
              
              <div className="space-y-3">
                <div>
                  <div className="text-sm font-medium text-gray-700">Question:</div>
                  <div className="text-gray-900">{question.question}</div>
                </div>
                
                <div>
                  <div className="text-sm font-medium text-gray-700">Expected Answer:</div>
                  <div className="text-gray-900">{question.expected_answer}</div>
                </div>
                
                <div>
                  <div className="text-sm font-medium text-gray-700">Model Response:</div>
                  <div className={`${question.is_correct ? 'text-green-900' : 'text-red-900'}`}>
                    {question.model_response}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Results</h1>
          <p className="mt-2 text-sm text-gray-700">
            View and analyze your evaluation results.
          </p>
        </div>
      </div>

      {/* Results List */}
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
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Accuracy
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Questions
                    </th>
                    <th className="relative px-6 py-3">
                      <span className="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {results.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-6 py-4 text-center text-sm text-gray-500">
                        No evaluation results yet. Complete an evaluation to see results here.
                      </td>
                    </tr>
                  ) : (
                    results.map((result) => (
                      <tr key={result.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{result.evaluation_name}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {result.model_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(result.completed_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            result.accuracy >= 0.8 
                              ? 'bg-green-100 text-green-800' 
                              : result.accuracy >= 0.6
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {(result.accuracy * 100).toFixed(1)}%
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {result.total_questions}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => fetchEvaluationDetails(result.evaluation_id)}
                            className="text-blue-600 hover:text-blue-900 mr-4"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => deleteResult(result.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Delete
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
    </div>
  )
}

export default Results
