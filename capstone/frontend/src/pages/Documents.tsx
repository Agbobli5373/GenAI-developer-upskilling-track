import React, { useState } from "react";
import { useQuery } from "react-query";
import {
  DocumentTextIcon,
  PlusIcon,
  CloudArrowUpIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  Cog6ToothIcon,
} from "@heroicons/react/24/outline";
import { documentsAPI } from "@/services/api";
import { Document, DocumentCreate } from "@/types";
import { DocumentViewer } from "@/components/DocumentViewer";
import toast from "react-hot-toast";

export const Documents: React.FC = () => {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadMetadata, setUploadMetadata] = useState<Partial<DocumentCreate>>(
    {
      title: "",
      description: "",
      document_type: "contract",
    }
  );
  const [uploading, setUploading] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(
    null
  );
  const [isViewerOpen, setIsViewerOpen] = useState(false);

  const {
    data: documents,
    isLoading,
    refetch,
  } = useQuery(
    "documents",
    () => documentsAPI.getDocuments().then((res) => res.data),
    {
      refetchInterval: 5000, // Auto-refresh every 5 seconds to check processing status
    }
  );

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      if (!uploadMetadata.title) {
        setUploadMetadata((prev) => ({ ...prev, title: file.name }));
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error("Please select a file");
      return;
    }

    setUploading(true);
    try {
      await documentsAPI.uploadDocument(selectedFile, uploadMetadata);
      toast.success("Document uploaded successfully!");
      setIsUploadModalOpen(false);
      setSelectedFile(null);
      setUploadMetadata({
        title: "",
        description: "",
        document_type: "contract",
      });
      refetch();
    } catch (error: any) {
      const message = error.response?.data?.detail || "Upload failed";
      toast.error(message);
    } finally {
      setUploading(false);
    }
  };

  const handleViewDocument = (document: Document) => {
    setSelectedDocument(document);
    setIsViewerOpen(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "processed":
        return "bg-green-100 text-green-800";
      case "processing":
        return "bg-yellow-100 text-yellow-800";
      case "error":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "processed":
        return "✓";
      case "processing":
        return "⏳";
      case "error":
        return "⚠️";
      default:
        return "📄";
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your legal documents and contracts
          </p>
        </div>
        <button
          onClick={() => setIsUploadModalOpen(true)}
          className="btn-primary"
        >
          <PlusIcon className="w-4 h-4 mr-2" />
          Upload Document
        </button>
      </div>

      {/* Documents List */}
      {documents && documents.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {documents.map((document: Document) => (
            <div
              key={document.id}
              className="card hover:shadow-md transition-shadow"
            >
              <div className="card-body">
                <div className="flex items-start justify-between">
                  <div className="text-gray-400">
                    <DocumentTextIcon className="h-8 w-8" />
                  </div>
                  <div className="flex space-x-1">
                    <button
                      onClick={() => handleViewDocument(document)}
                      className="p-1 text-gray-400 hover:text-gray-600"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </button>
                    <button className="p-1 text-gray-400 hover:text-gray-600">
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button className="p-1 text-gray-400 hover:red-600">
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-900 truncate">
                    {document.title}
                  </h3>
                  {document.description && (
                    <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                      {document.description}
                    </p>
                  )}
                  <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                    <span className="capitalize">{document.document_type}</span>
                    <span>{formatFileSize(document.file_size)}</span>
                  </div>
                  <div className="mt-2 text-xs text-gray-500">
                    Uploaded {formatDate(document.created_at)}
                  </div>
                  <div className="mt-2">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                        document.status
                      )}`}
                    >
                      {getStatusIcon(document.status)} {document.status}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            No documents
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by uploading your first document.
          </p>
          <div className="mt-6">
            <button
              onClick={() => setIsUploadModalOpen(true)}
              className="btn-primary"
            >
              <PlusIcon className="w-4 h-4 mr-2" />
              Upload Document
            </button>
          </div>
        </div>
      )}

      {/* Upload Modal */}
      {isUploadModalOpen && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Upload Document
              </h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    File
                  </label>
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt"
                    onChange={handleFileSelect}
                    className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Supported formats: PDF, DOCX, TXT (max 50MB)
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Title
                  </label>
                  <input
                    type="text"
                    value={uploadMetadata.title}
                    onChange={(e) =>
                      setUploadMetadata((prev) => ({
                        ...prev,
                        title: e.target.value,
                      }))
                    }
                    className="input mt-1"
                    placeholder="Document title"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Description
                  </label>
                  <textarea
                    value={uploadMetadata.description}
                    onChange={(e) =>
                      setUploadMetadata((prev) => ({
                        ...prev,
                        description: e.target.value,
                      }))
                    }
                    className="input mt-1"
                    rows={3}
                    placeholder="Optional description"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Document Type
                  </label>
                  <select
                    value={uploadMetadata.document_type}
                    onChange={(e) =>
                      setUploadMetadata((prev) => ({
                        ...prev,
                        document_type: e.target.value as any,
                      }))
                    }
                    className="input mt-1"
                  >
                    <option value="contract">Contract</option>
                    <option value="agreement">Agreement</option>
                    <option value="policy">Policy</option>
                    <option value="regulation">Regulation</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => {
                    setIsUploadModalOpen(false);
                    setSelectedFile(null);
                    setUploadMetadata({
                      title: "",
                      description: "",
                      document_type: "contract",
                    });
                  }}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpload}
                  disabled={!selectedFile || uploading}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading ? "Uploading..." : "Upload"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Document Viewer */}
      {isViewerOpen && selectedDocument && (
        <DocumentViewer
          document={selectedDocument}
          onClose={() => setIsViewerOpen(false)}
        />
      )}
    </div>
  );
};
