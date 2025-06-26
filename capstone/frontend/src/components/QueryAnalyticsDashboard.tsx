import React, { useState } from "react";
import {
  ChartBarIcon,
  MagnifyingGlassIcon,
  LightBulbIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  BeakerIcon,
  DocumentMagnifyingGlassIcon,
} from "@heroicons/react/24/outline";
import { apiService } from "../services/api";
import {
  QueryPerformanceAnalysis,
  QueryOptimizationResponse,
  QuerySuggestion,
} from "../types";

interface QueryAnalyticsDashboardProps {
  onOptimizeQuery?: (optimizedQuery: string) => void;
}

export const QueryAnalyticsDashboard: React.FC<
  QueryAnalyticsDashboardProps
> = ({ onOptimizeQuery }) => {
  const [query, setQuery] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [performance, setPerformance] =
    useState<QueryPerformanceAnalysis | null>(null);
  const [optimization, setOptimization] =
    useState<QueryOptimizationResponse | null>(null);
  const [suggestions, setSuggestions] = useState<QuerySuggestion[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<
    "performance" | "optimization" | "suggestions"
  >("performance");

  const analyzeQuery = async () => {
    if (!query.trim()) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      // Run all analyses in parallel
      const [performanceResponse, optimizationResponse, suggestionsResponse] =
        await Promise.all([
          apiService.analyzeQueryPerformance({ query }),
          apiService.optimizeQuery({
            query,
            context: "legal document search",
            optimization_type: "comprehensive",
          }),
          apiService.getQuerySuggestions(query),
        ]);

      setPerformance(performanceResponse.data);
      setOptimization(optimizationResponse.data);
      setSuggestions(suggestionsResponse.data.suggestions || []);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Analysis failed. Please try again."
      );
      console.error("Query analysis error:", err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleOptimizeClick = () => {
    if (optimization?.optimized_query && onOptimizeQuery) {
      onOptimizeQuery(optimization.optimized_query);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return "text-green-600";
    if (score >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 0.8) return "bg-green-100";
    if (score >= 0.6) return "bg-yellow-100";
    return "bg-red-100";
  };

  const formatScore = (score: number) => Math.round(score * 100);

  return (
    <div className="w-full max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center justify-center gap-2">
          <ChartBarIcon className="h-6 w-6 text-emerald-600" />
          Query Analytics Dashboard
        </h2>
        <p className="text-gray-600">
          Analyze and optimize your legal search queries for better results
        </p>
      </div>

      {/* Query Input */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Query Analysis
        </h3>

        <div className="space-y-4">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your legal search query for analysis..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none"
              rows={3}
            />
          </div>

          <div className="flex justify-center">
            <button
              onClick={analyzeQuery}
              disabled={isAnalyzing || !query.trim()}
              className="px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
            >
              {isAnalyzing ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <BeakerIcon className="h-5 w-5" />
                  Analyze Query
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-2">
          <ExclamationTriangleIcon className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div className="text-red-700">{error}</div>
        </div>
      )}

      {/* Results */}
      {(performance || optimization || suggestions.length > 0) && (
        <div className="space-y-6">
          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab("performance")}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === "performance"
                    ? "border-emerald-500 text-emerald-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <ChartBarIcon className="inline h-4 w-4 mr-1" />
                Performance Analysis
              </button>
              {optimization && (
                <button
                  onClick={() => setActiveTab("optimization")}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === "optimization"
                      ? "border-emerald-500 text-emerald-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
                >
                  <DocumentMagnifyingGlassIcon className="inline h-4 w-4 mr-1" />
                  Query Optimization
                </button>
              )}
              {suggestions.length > 0 && (
                <button
                  onClick={() => setActiveTab("suggestions")}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === "suggestions"
                      ? "border-emerald-500 text-emerald-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
                >
                  <LightBulbIcon className="inline h-4 w-4 mr-1" />
                  Suggestions ({suggestions.length})
                </button>
              )}
            </nav>
          </div>

          {/* Tab Content */}
          {activeTab === "performance" && performance && (
            <div className="space-y-6">
              {/* Performance Metrics */}
              <div className="bg-gradient-to-r from-emerald-50 to-blue-50 border border-emerald-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Query Performance Metrics
                </h3>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div
                    className={`text-center p-4 rounded-lg ${getScoreBgColor(
                      performance.complexity_score
                    )}`}
                  >
                    <div
                      className={`text-2xl font-bold ${getScoreColor(
                        performance.complexity_score
                      )}`}
                    >
                      {formatScore(performance.complexity_score)}%
                    </div>
                    <div className="text-sm text-gray-600">Complexity</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {performance.complexity_score >= 0.7
                        ? "High"
                        : performance.complexity_score >= 0.4
                        ? "Medium"
                        : "Low"}
                    </div>
                  </div>

                  <div
                    className={`text-center p-4 rounded-lg ${getScoreBgColor(
                      performance.clarity_score
                    )}`}
                  >
                    <div
                      className={`text-2xl font-bold ${getScoreColor(
                        performance.clarity_score
                      )}`}
                    >
                      {formatScore(performance.clarity_score)}%
                    </div>
                    <div className="text-sm text-gray-600">Clarity</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {performance.clarity_score >= 0.7
                        ? "Clear"
                        : performance.clarity_score >= 0.4
                        ? "Moderate"
                        : "Unclear"}
                    </div>
                  </div>

                  <div
                    className={`text-center p-4 rounded-lg ${getScoreBgColor(
                      performance.specificity_score
                    )}`}
                  >
                    <div
                      className={`text-2xl font-bold ${getScoreColor(
                        performance.specificity_score
                      )}`}
                    >
                      {formatScore(performance.specificity_score)}%
                    </div>
                    <div className="text-sm text-gray-600">Specificity</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {performance.specificity_score >= 0.7
                        ? "Specific"
                        : performance.specificity_score >= 0.4
                        ? "Moderate"
                        : "Vague"}
                    </div>
                  </div>

                  <div
                    className={`text-center p-4 rounded-lg ${getScoreBgColor(
                      performance.overall_score
                    )}`}
                  >
                    <div
                      className={`text-2xl font-bold ${getScoreColor(
                        performance.overall_score
                      )}`}
                    >
                      {formatScore(performance.overall_score)}%
                    </div>
                    <div className="text-sm text-gray-600">Overall Score</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {performance.overall_score >= 0.7
                        ? "Excellent"
                        : performance.overall_score >= 0.4
                        ? "Good"
                        : "Needs Work"}
                    </div>
                  </div>
                </div>
              </div>

              {/* Identified Issues */}
              {performance.identified_issues &&
                performance.identified_issues.length > 0 && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                    <h4 className="font-semibold text-red-900 mb-3 flex items-center gap-2">
                      <ExclamationTriangleIcon className="h-5 w-5" />
                      Identified Issues
                    </h4>
                    <ul className="space-y-2">
                      {performance.identified_issues.map((issue, index) => (
                        <li
                          key={index}
                          className="flex items-start gap-2 text-red-800"
                        >
                          <span className="text-red-500 mt-1">•</span>
                          <span>{issue}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

              {/* Improvement Suggestions */}
              {performance.improvement_suggestions &&
                performance.improvement_suggestions.length > 0 && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
                      <LightBulbIcon className="h-5 w-5" />
                      Improvement Suggestions
                    </h4>
                    <ul className="space-y-2">
                      {performance.improvement_suggestions.map(
                        (suggestion, index) => (
                          <li
                            key={index}
                            className="flex items-start gap-2 text-blue-800"
                          >
                            <CheckCircleIcon className="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" />
                            <span>{suggestion}</span>
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                )}
            </div>
          )}

          {activeTab === "optimization" && optimization && (
            <div className="space-y-6">
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-purple-900 mb-4">
                  Query Optimization Results
                </h3>

                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-purple-800 mb-2">
                      Original Query:
                    </h4>
                    <div className="bg-gray-100 border border-gray-300 rounded p-3 text-gray-800 font-mono">
                      {query}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-purple-800 mb-2">
                      Optimized Query:
                    </h4>
                    <div className="bg-white border border-purple-300 rounded p-3 text-purple-900 font-mono">
                      {optimization.optimized_query}
                    </div>
                    <button
                      onClick={handleOptimizeClick}
                      className="mt-2 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 text-sm"
                    >
                      Use Optimized Query
                    </button>
                  </div>

                  {optimization.explanation && (
                    <div>
                      <h4 className="font-medium text-purple-800 mb-2">
                        Optimization Explanation:
                      </h4>
                      <div className="bg-purple-100 border border-purple-200 rounded p-3 text-purple-800">
                        {optimization.explanation}
                      </div>
                    </div>
                  )}

                  {optimization.suggested_refinements &&
                    optimization.suggested_refinements.length > 0 && (
                      <div>
                        <h4 className="font-medium text-purple-800 mb-2">
                          Additional Refinements:
                        </h4>
                        <ul className="space-y-1">
                          {optimization.suggested_refinements.map(
                            (refinement, index) => (
                              <li
                                key={index}
                                className="flex items-start gap-2 text-purple-700"
                              >
                                <span className="text-purple-500 mt-1">•</span>
                                <span>{refinement}</span>
                              </li>
                            )
                          )}
                        </ul>
                      </div>
                    )}
                </div>
              </div>
            </div>
          )}

          {activeTab === "suggestions" && suggestions.length > 0 && (
            <div className="space-y-4">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-yellow-900 mb-4">
                  Query Suggestions
                </h3>
                <p className="text-yellow-700 mb-4">
                  These alternative queries might help you find better results:
                </p>

                <div className="space-y-3">
                  {suggestions.map((suggestion, index) => (
                    <div
                      key={index}
                      className="bg-white border border-yellow-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => setQuery(suggestion.query)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="font-medium text-gray-900 mb-1">
                            {suggestion.query}
                          </div>
                          {suggestion.explanation && (
                            <div className="text-sm text-gray-600 mb-2">
                              {suggestion.explanation}
                            </div>
                          )}
                          <div className="flex items-center gap-4 text-xs text-gray-500">
                            <span className="flex items-center gap-1">
                              <ClockIcon className="h-3 w-3" />
                              Confidence:{" "}
                              {Math.round(suggestion.confidence * 100)}%
                            </span>
                          </div>
                        </div>
                        <LightBulbIcon className="h-5 w-5 text-yellow-500 flex-shrink-0" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default QueryAnalyticsDashboard;
