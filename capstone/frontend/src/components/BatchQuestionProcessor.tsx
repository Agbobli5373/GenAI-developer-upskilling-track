import React, { useState, useCallback } from "react";
import {
  QueueListIcon,
  PlayIcon,
  PauseIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  PlusIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import { apiService } from "../services/api";
import {
  BatchQuestionRequest,
  BatchQuestionResponse,
  EnhancedRAGResponse,
} from "../types";

interface BatchQuestionProcessorProps {
  onResults?: (results: BatchQuestionResponse) => void;
}

export const BatchQuestionProcessor: React.FC<BatchQuestionProcessorProps> = ({
  onResults,
}) => {
  const [questions, setQuestions] = useState<string[]>([""]);
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [batchSettings, setBatchSettings] = useState({
    max_parallel: 3,
    timeout_per_question: 30,
    include_cross_references: true,
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<BatchQuestionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentProgress, setCurrentProgress] = useState(0);

  const addQuestion = () => {
    setQuestions([...questions, ""]);
  };

  const removeQuestion = (index: number) => {
    if (questions.length > 1) {
      const newQuestions = questions.filter((_, i) => i !== index);
      setQuestions(newQuestions);
    }
  };

  const updateQuestion = (index: number, value: string) => {
    const newQuestions = [...questions];
    newQuestions[index] = value;
    setQuestions(newQuestions);
  };

  const handleBatchProcess = async () => {
    const validQuestions = questions.filter((q) => q.trim().length > 0);

    if (validQuestions.length === 0) {
      setError("Please enter at least one question");
      return;
    }

    setIsProcessing(true);
    setError(null);
    setCurrentProgress(0);

    try {
      const request: BatchQuestionRequest = {
        questions: validQuestions,
        document_ids:
          selectedDocuments.length > 0 ? selectedDocuments : undefined,
        batch_settings: batchSettings,
      };

      // Start polling for progress updates
      const progressInterval = setInterval(() => {
        setCurrentProgress((prev) => Math.min(prev + 10, 90));
      }, 1000);

      const response = await apiService.batchQuestionProcessing(request);

      clearInterval(progressInterval);
      setCurrentProgress(100);
      setResults(response.data);

      if (onResults) {
        onResults(response.data);
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Batch processing failed. Please try again."
      );
      console.error("Batch processing error:", err);
    } finally {
      setIsProcessing(false);
    }
  };

  const getStatusIcon = (success: boolean) => {
    return success ? (
      <CheckCircleIcon className="h-5 w-5 text-green-500" />
    ) : (
      <XCircleIcon className="h-5 w-5 text-red-500" />
    );
  };

  const formatTime = (seconds: number) => {
    return `${seconds.toFixed(2)}s`;
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center justify-center gap-2">
          <QueueListIcon className="h-6 w-6 text-purple-600" />
          Batch Question Processor
        </h2>
        <p className="text-gray-600">
          Process multiple legal questions efficiently with AI-powered analysis
        </p>
      </div>

      {/* Question Input Section */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Questions</h3>

        <div className="space-y-3">
          {questions.map((question, index) => (
            <div key={index} className="flex items-start gap-3">
              <div className="flex-1">
                <textarea
                  value={question}
                  onChange={(e) => updateQuestion(index, e.target.value)}
                  placeholder={`Enter question ${index + 1}...`}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                  rows={2}
                />
              </div>
              <div className="flex flex-col gap-2">
                <span className="text-sm text-gray-500 font-medium">
                  #{index + 1}
                </span>
                {questions.length > 1 && (
                  <button
                    onClick={() => removeQuestion(index)}
                    className="p-1 text-red-500 hover:text-red-700"
                    title="Remove question"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={addQuestion}
          className="mt-3 flex items-center gap-2 px-3 py-2 text-purple-600 hover:text-purple-800 hover:bg-purple-50 rounded-md transition-colors"
        >
          <PlusIcon className="h-4 w-4" />
          Add Question
        </button>
      </div>

      {/* Batch Settings */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Batch Settings
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Parallel Processing
            </label>
            <input
              type="number"
              min="1"
              max="10"
              value={batchSettings.max_parallel}
              onChange={(e) =>
                setBatchSettings((prev) => ({
                  ...prev,
                  max_parallel: parseInt(e.target.value) || 1,
                }))
              }
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Timeout per Question (seconds)
            </label>
            <input
              type="number"
              min="10"
              max="300"
              value={batchSettings.timeout_per_question}
              onChange={(e) =>
                setBatchSettings((prev) => ({
                  ...prev,
                  timeout_per_question: parseInt(e.target.value) || 30,
                }))
              }
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          <div className="flex items-center space-x-2 pt-6">
            <input
              type="checkbox"
              id="cross-references"
              checked={batchSettings.include_cross_references}
              onChange={(e) =>
                setBatchSettings((prev) => ({
                  ...prev,
                  include_cross_references: e.target.checked,
                }))
              }
              className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
            />
            <label htmlFor="cross-references" className="text-sm text-gray-700">
              Include Cross References
            </label>
          </div>
        </div>
      </div>

      {/* Process Button */}
      <div className="flex justify-center">
        <button
          onClick={handleBatchProcess}
          disabled={isProcessing || questions.every((q) => !q.trim())}
          className="px-8 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
        >
          {isProcessing ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              Processing... ({currentProgress}%)
            </>
          ) : (
            <>
              <PlayIcon className="h-5 w-5" />
              Process Questions
            </>
          )}
        </button>
      </div>

      {/* Progress Bar */}
      {isProcessing && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Processing Progress
            </span>
            <span className="text-sm text-gray-500">{currentProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-purple-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${currentProgress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-2">
          <ExclamationTriangleIcon className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div className="text-red-700">{error}</div>
        </div>
      )}

      {/* Results Display */}
      {results && (
        <div className="space-y-6">
          {/* Batch Summary */}
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <ChartBarIcon className="h-5 w-5 text-purple-600" />
              Batch Summary
            </h3>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-900">
                  {results.total_questions}
                </div>
                <div className="text-sm text-purple-600">Total Questions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-900">
                  {results.completed}
                </div>
                <div className="text-sm text-green-600">Completed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-900">
                  {Math.round(results.batch_summary.success_rate * 100)}%
                </div>
                <div className="text-sm text-blue-600">Success Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-900">
                  {formatTime(results.batch_summary.total_processing_time)}
                </div>
                <div className="text-sm text-indigo-600">Total Time</div>
              </div>
            </div>

            {/* Common Themes */}
            {results.batch_summary.common_themes.length > 0 && (
              <div className="mt-4">
                <h4 className="font-medium text-gray-800 mb-2">
                  Common Themes:
                </h4>
                <div className="flex flex-wrap gap-2">
                  {results.batch_summary.common_themes.map((theme, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-purple-200 text-purple-800 rounded-full text-sm"
                    >
                      {theme}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Individual Results */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Individual Results
            </h3>

            {results.results.map((result, index) => (
              <div
                key={index}
                className={`border rounded-lg p-6 ${
                  result.success
                    ? "border-green-200 bg-green-50"
                    : "border-red-200 bg-red-50"
                }`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(result.success)}
                    <h4 className="font-medium text-gray-900">
                      Question {index + 1}
                    </h4>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <ClockIcon className="h-4 w-4" />
                      {formatTime(result.processing_time)}
                    </span>
                  </div>
                </div>

                <div className="mb-3">
                  <div className="text-sm text-gray-600 mb-2">Question:</div>
                  <div className="bg-white border border-gray-200 rounded p-3 text-gray-800">
                    {result.question}
                  </div>
                </div>

                {result.success && result.answer ? (
                  <div>
                    <div className="text-sm text-gray-600 mb-2">Answer:</div>
                    <div className="bg-white border border-gray-200 rounded p-4 text-gray-800">
                      <div className="whitespace-pre-wrap">
                        {result.answer.answer}
                      </div>

                      {result.answer.confidence_score !== undefined && (
                        <div className="mt-3 text-sm text-gray-600">
                          Confidence:{" "}
                          {Math.round(result.answer.confidence_score * 100)}%
                        </div>
                      )}

                      {result.answer.sources &&
                        result.answer.sources.length > 0 && (
                          <div className="mt-3">
                            <div className="text-sm text-gray-600 mb-1">
                              Sources ({result.answer.sources.length}):
                            </div>
                            <div className="space-y-1">
                              {result.answer.sources
                                .slice(0, 3)
                                .map((source, sourceIndex) => (
                                  <div
                                    key={sourceIndex}
                                    className="text-xs text-gray-500 bg-gray-50 p-2 rounded"
                                  >
                                    <div className="font-medium">
                                      {source.title}
                                    </div>
                                    <div className="truncate">
                                      {source.content}
                                    </div>
                                  </div>
                                ))}
                            </div>
                          </div>
                        )}
                    </div>
                  </div>
                ) : (
                  result.error && (
                    <div>
                      <div className="text-sm text-red-600 mb-2">Error:</div>
                      <div className="bg-red-100 border border-red-200 rounded p-3 text-red-800">
                        {result.error}
                      </div>
                    </div>
                  )
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default BatchQuestionProcessor;
