import React, { useState, useEffect } from "react";
import { Document, DocumentChunk, DocumentStructure } from "@/types";
import { documentsAPI } from "@/services/api";

interface DocumentViewerProps {
  document: Document;
  onError?: (error: string) => void;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  document,
  onError,
}) => {
  const [chunks, setChunks] = useState<DocumentChunk[]>([]);
  const [structure, setStructure] = useState<DocumentStructure | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeChunkType, setActiveChunkType] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<DocumentChunk[]>([]);

  useEffect(() => {
    loadDocumentData();
  }, [document.id]);

  const loadDocumentData = async () => {
    try {
      setLoading(true);

      // Load chunks and structure in parallel
      const [chunksResponse, structureResponse] = await Promise.all([
        documentsAPI.getDocumentChunks(document.id),
        documentsAPI.getDocumentStructure(document.id),
      ]);

      setChunks(chunksResponse.data);
      setStructure(structureResponse.data);
    } catch (error) {
      console.error("Error loading document data:", error);
      onError?.("Failed to load document data");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      const response = await documentsAPI.searchDocumentChunks(
        document.id,
        searchQuery,
        20
      );
      setSearchResults(response.data.chunks);
    } catch (error) {
      console.error("Search error:", error);
      onError?.("Search failed");
    }
  };

  const getFilteredChunks = () => {
    if (searchResults.length > 0) {
      return searchResults;
    }

    if (activeChunkType === "all") {
      return chunks;
    }

    return chunks.filter((chunk) => chunk.chunk_type === activeChunkType);
  };

  const getChunkTypeColor = (type: string) => {
    const colors = {
      heading: "bg-blue-100 text-blue-800",
      clause: "bg-green-100 text-green-800",
      definition: "bg-purple-100 text-purple-800",
      paragraph: "bg-gray-100 text-gray-800",
      list_item: "bg-yellow-100 text-yellow-800",
    };
    return colors[type as keyof typeof colors] || "bg-gray-100 text-gray-800";
  };

  const handleReprocess = async () => {
    try {
      await documentsAPI.reprocessDocument(document.id);
      // Reload data after reprocessing starts
      setTimeout(() => {
        loadDocumentData();
      }, 2000);
    } catch (error) {
      console.error("Reprocess error:", error);
      onError?.("Failed to start reprocessing");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading document...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Document Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {document.title}
            </h2>
            <p className="text-gray-600 mt-1">{document.filename}</p>
          </div>
          <div className="flex items-center space-x-2">
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                document.status === "processed"
                  ? "bg-green-100 text-green-800"
                  : document.status === "processing"
                  ? "bg-yellow-100 text-yellow-800"
                  : document.status === "error"
                  ? "bg-red-100 text-red-800"
                  : "bg-gray-100 text-gray-800"
              }`}
            >
              {document.status}
            </span>
            {document.status === "processed" && (
              <button
                onClick={handleReprocess}
                className="px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded-full hover:bg-blue-200"
              >
                Reprocess
              </button>
            )}
          </div>
        </div>

        {document.description && (
          <p className="text-gray-700 mt-2">{document.description}</p>
        )}
      </div>

      {/* Document Stats */}
      {structure && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-700">Total Chunks</h3>
            <p className="text-2xl font-bold text-gray-900">
              {structure.total_chunks}
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-700">Pages</h3>
            <p className="text-2xl font-bold text-gray-900">
              {Object.keys(structure.page_distribution).length}
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-700">File Size</h3>
            <p className="text-2xl font-bold text-gray-900">
              {(document.file_size / 1024).toFixed(1)} KB
            </p>
          </div>
        </div>
      )}

      {/* Search Bar */}
      <div className="mb-6">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            placeholder="Search within document..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSearch()}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <button
            onClick={handleSearch}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Search
          </button>
          {searchResults.length > 0 && (
            <button
              onClick={() => {
                setSearchQuery("");
                setSearchResults([]);
              }}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Chunk Type Filter */}
      {structure && (
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-700 mb-2">
            Filter by Type
          </h3>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setActiveChunkType("all")}
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                activeChunkType === "all"
                  ? "bg-blue-100 text-blue-800"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              All ({structure.total_chunks})
            </button>
            {Object.entries(structure.chunk_types).map(([type, count]) => (
              <button
                key={type}
                onClick={() => setActiveChunkType(type)}
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  activeChunkType === type
                    ? "bg-blue-100 text-blue-800"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {type} ({count})
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Document Chunks */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Document Content
          {searchResults.length > 0 && (
            <span className="text-sm font-normal text-gray-600 ml-2">
              ({searchResults.length} search results)
            </span>
          )}
        </h3>

        {getFilteredChunks().map((chunk, index) => (
          <div
            key={chunk.id}
            className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${getChunkTypeColor(
                    chunk.chunk_type
                  )}`}
                >
                  {chunk.chunk_type}
                </span>
                <span className="text-xs text-gray-500">
                  Page {chunk.page_number} • Para {chunk.paragraph_index}
                </span>
                <span className="text-xs text-gray-500">
                  Chars {chunk.char_start}-{chunk.char_end}
                </span>
              </div>
              <span className="text-xs text-gray-400">
                #{chunk.chunk_index}
              </span>
            </div>

            <p className="text-gray-800 leading-relaxed">
              {searchQuery && searchResults.length > 0
                ? chunk.content.replace(
                    new RegExp(searchQuery, "gi"),
                    (match) => `<mark class="bg-yellow-200">${match}</mark>`
                  )
                : chunk.content}
            </p>

            {chunk.metadata && Object.keys(chunk.metadata).length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-100">
                <div className="text-xs text-gray-500">
                  Words: {chunk.metadata.word_count || "N/A"} • Characters:{" "}
                  {chunk.metadata.char_count || "N/A"}
                </div>
              </div>
            )}
          </div>
        ))}

        {getFilteredChunks().length === 0 && (
          <div className="text-center py-8 text-gray-500">
            {searchQuery ? "No search results found" : "No chunks available"}
          </div>
        )}
      </div>
    </div>
  );
};
