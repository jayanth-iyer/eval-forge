import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Brain, Play, BarChart3, Plus } from 'lucide-react'

const Dashboard = () => {
  const [stats, setStats] = useState({
    modelCount: 0,
    evaluationCount: 0,
    avgAccuracy: null,
    avgBleuScore: null,
    avgRouge1Score: null,
    avgRouge2Score: null,
    avgRougeLScore: null,
    avgSemanticSimilarity: null
  })
  const navigate = useNavigate()

  useEffect(() => {
    fetchDashboardStats()
  }, [])

  const fetchDashboardStats = async () => {
    try {
      // Fetch models
      const modelsResponse = await fetch('http://localhost:8000/api/models')
      const models = modelsResponse.ok ? await modelsResponse.json() : []

      // Fetch evaluations
      const evaluationsResponse = await fetch('http://localhost:8000/api/evaluations')
      const evaluations = evaluationsResponse.ok ? await evaluationsResponse.json() : []

      // Calculate average metrics from completed evaluations
      const completedEvaluations = evaluations.filter(evaluation => evaluation.status === 'completed' && evaluation.accuracy !== null)
      
      const avgAccuracy = completedEvaluations.length > 0 
        ? (completedEvaluations.reduce((sum, evaluation) => sum + evaluation.accuracy, 0) / completedEvaluations.length * 100).toFixed(1)
        : null

      // Calculate average BLEU score
      const evaluationsWithBleu = completedEvaluations.filter(evaluation => evaluation.avg_bleu_score !== null)
      const avgBleuScore = evaluationsWithBleu.length > 0
        ? (evaluationsWithBleu.reduce((sum, evaluation) => sum + evaluation.avg_bleu_score, 0) / evaluationsWithBleu.length).toFixed(3)
        : null

      // Calculate average ROUGE scores
      const evaluationsWithRouge1 = completedEvaluations.filter(evaluation => evaluation.avg_rouge_1_score !== null)
      const avgRouge1Score = evaluationsWithRouge1.length > 0
        ? (evaluationsWithRouge1.reduce((sum, evaluation) => sum + evaluation.avg_rouge_1_score, 0) / evaluationsWithRouge1.length).toFixed(3)
        : null

      const evaluationsWithRouge2 = completedEvaluations.filter(evaluation => evaluation.avg_rouge_2_score !== null)
      const avgRouge2Score = evaluationsWithRouge2.length > 0
        ? (evaluationsWithRouge2.reduce((sum, evaluation) => sum + evaluation.avg_rouge_2_score, 0) / evaluationsWithRouge2.length).toFixed(3)
        : null

      const evaluationsWithRougeL = completedEvaluations.filter(evaluation => evaluation.avg_rouge_l_score !== null)
      const avgRougeLScore = evaluationsWithRougeL.length > 0
        ? (evaluationsWithRougeL.reduce((sum, evaluation) => sum + evaluation.avg_rouge_l_score, 0) / evaluationsWithRougeL.length).toFixed(3)
        : null

      // Calculate average semantic similarity
      const evaluationsWithSemantic = completedEvaluations.filter(evaluation => evaluation.avg_semantic_similarity !== null)
      const avgSemanticSimilarity = evaluationsWithSemantic.length > 0
        ? (evaluationsWithSemantic.reduce((sum, evaluation) => sum + evaluation.avg_semantic_similarity, 0) / evaluationsWithSemantic.length).toFixed(3)
        : null

      setStats({
        modelCount: models.length,
        evaluationCount: evaluations.length,
        avgAccuracy,
        avgBleuScore,
        avgRouge1Score,
        avgRouge2Score,
        avgRougeLScore,
        avgSemanticSimilarity
      })
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error)
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Welcome to Eval Forge - LLM Evaluation Platform</p>
      </div>

      {/* Basic Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200">
          <div className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Brain className="h-8 w-8 text-indigo-500" />
              </div>
              <div className="ml-4 w-0 flex-1">
                <dl>
                  <dt className="text-base font-medium text-gray-600 mb-1">
                    Configured Models
                  </dt>
                  <dd className="text-3xl font-bold text-gray-900">{stats.modelCount}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200">
          <div className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Play className="h-8 w-8 text-green-500" />
              </div>
              <div className="ml-4 w-0 flex-1">
                <dl>
                  <dt className="text-base font-medium text-gray-600 mb-1">
                    Total Evaluations
                  </dt>
                  <dd className="text-3xl font-bold text-gray-900">{stats.evaluationCount}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200">
          <div className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BarChart3 className="h-8 w-8 text-blue-500" />
              </div>
              <div className="ml-4 w-0 flex-1">
                <dl>
                  <dt className="text-base font-medium text-gray-600 mb-1">
                    Average Accuracy
                  </dt>
                  <dd className="text-3xl font-bold text-gray-900">
                    {stats.avgAccuracy ? `${stats.avgAccuracy}%` : '-'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Advanced Metrics */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Advanced Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          <div className="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200">
            <div className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BarChart3 className="h-8 w-8 text-blue-500" />
                </div>
                <div className="ml-4 w-0 flex-1">
                  <dl>
                    <dt className="text-base font-medium text-gray-600 mb-1">
                      BLEU Score
                    </dt>
                    <dd className="text-2xl font-bold text-gray-900">
                      {stats.avgBleuScore || '-'}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200">
            <div className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BarChart3 className="h-8 w-8 text-purple-500" />
                </div>
                <div className="ml-4 w-0 flex-1">
                  <dl>
                    <dt className="text-base font-medium text-gray-600 mb-1">
                      ROUGE-1
                    </dt>
                    <dd className="text-2xl font-bold text-gray-900">
                      {stats.avgRouge1Score || '-'}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200">
            <div className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BarChart3 className="h-8 w-8 text-orange-500" />
                </div>
                <div className="ml-4 w-0 flex-1">
                  <dl>
                    <dt className="text-base font-medium text-gray-600 mb-1">
                      ROUGE-2
                    </dt>
                    <dd className="text-2xl font-bold text-gray-900">
                      {stats.avgRouge2Score || '-'}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200">
            <div className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BarChart3 className="h-8 w-8 text-red-500" />
                </div>
                <div className="ml-4 w-0 flex-1">
                  <dl>
                    <dt className="text-base font-medium text-gray-600 mb-1">
                      ROUGE-L
                    </dt>
                    <dd className="text-2xl font-bold text-gray-900">
                      {stats.avgRougeLScore || '-'}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200">
            <div className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BarChart3 className="h-8 w-8 text-green-500" />
                </div>
                <div className="ml-4 w-0 flex-1">
                  <dl>
                    <dt className="text-base font-medium text-gray-600 mb-1">
                      Semantic Similarity
                    </dt>
                    <dd className="text-2xl font-bold text-gray-900">
                      {stats.avgSemanticSimilarity || '-'}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Link
              to="/models"
              className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <div>
                <span className="rounded-lg inline-flex p-3 bg-blue-50 text-blue-600 ring-4 ring-white">
                  <Plus className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-4">
                <h3 className="text-lg font-medium">
                  <span className="absolute inset-0" aria-hidden="true" />
                  Add Your First Model
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  Connect to your local Ollama instance or configure API models
                </p>
              </div>
            </Link>

            <Link
              to="/evaluations"
              className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <div>
                <span className="rounded-lg inline-flex p-3 bg-green-50 text-green-600 ring-4 ring-white">
                  <Play className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-4">
                <h3 className="text-lg font-medium">
                  <span className="absolute inset-0" aria-hidden="true" />
                  Create Evaluation
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  Set up a new evaluation with custom datasets
                </p>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
