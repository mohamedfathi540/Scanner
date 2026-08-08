import { useState } from "react";
import { useParams } from "react-router-dom";
import { ArrowUpTrayIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { ScanLine, FileSpreadsheet } from "lucide-react";
import { Button } from "../components/ui/Button";
import { Logo } from "../components/ui/Logo";

// Section display info (matches backend section_registry.py)
const SECTION_INFO: Record<string, { name: string; nameAr: string }> = {
  foam: { name: "Foam", nameAr: "الفوم" },
  sewing: { name: "Sewing", nameAr: "الخياطة" },
  packing: { name: "Packing", nameAr: "التعبئة" },
  shoes: { name: "Shoes", nameAr: "الأحذية" },
};

export function ProductionPage() {
  const { section = "foam" } = useParams<{ section: string }>();
  const sectionMeta = SECTION_INFO[section] || SECTION_INFO["foam"];

  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleRemoveFile = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setFile(null);
    setError(null);
    
    // Clear the input value so the same file can be selected again
    const fileInput = document.getElementById("file-upload") as HTMLInputElement;
    if (fileInput) {
      fileInput.value = "";
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'image/png' || droppedFile.type === 'image/jpeg' || droppedFile.type === 'image/jpg') {
        setFile(droppedFile);
        setError(null);
      } else {
        setError('Please upload a valid image file (PNG, JPG, JPEG)');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      // Use relative path by default so requests go through the Vite proxy.
      // This ensures the tunnel URL works from any device.
      const API_URL = import.meta.env.VITE_API_URL || "/api/v1";
      const response = await fetch(`${API_URL}/production/upload/${section}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.message || "Failed to process the report");
      }

      // Download the excel file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `HT_${sectionMeta.name}_Report_${new Date().toISOString().slice(0, 10)}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setFile(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 bg-bg-primary h-full">
      <div className="max-w-2xl w-full flex flex-col items-center space-y-8">
        <div className="text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-6">
            <ScanLine className="w-8 h-8 text-primary-600" />
          </div>
          <div className="flex items-center justify-center gap-3">
            <Logo size={40} className="rounded-lg" />
            <h1 className="text-4xl font-bold tracking-tight text-text-primary">
              Daftar — {sectionMeta.name}
            </h1>
          </div>
          <p className="text-lg text-text-muted">
            Upload an image of a handwritten <strong>{sectionMeta.name}</strong> manufacturing report to automatically extract its contents into a standard Excel format.
          </p>
        </div>

        <div className="w-full max-w-md bg-bg-secondary p-8 rounded-2xl border border-border shadow-sm flex flex-col items-center">
            <>
              <label
                htmlFor="file-upload"
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`relative w-full h-48 border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-colors ${
                  isDragging 
                    ? "border-primary-500 bg-primary-50" 
                    : file 
                      ? "border-primary-500 bg-primary-50/5" 
                      : "border-border hover:border-primary-400 hover:bg-bg-hover"
                }`}
              >
                {file ? (
                  <div className="text-center space-y-2 relative w-full h-full flex flex-col items-center justify-center">
                    {!isUploading && (
                      <button
                        onClick={handleRemoveFile}
                        className="absolute top-2 right-2 p-1.5 bg-bg-primary border border-border rounded-lg text-text-muted hover:text-error hover:border-error/50 hover:bg-error/5 transition-all"
                        title="Remove selected image"
                      >
                        <XMarkIcon className="w-5 h-5" />
                      </button>
                    )}
                    <FileSpreadsheet className="w-10 h-10 text-primary-500 mx-auto" />
                    <p className="font-medium text-text-primary truncate px-12 w-full">{file.name}</p>
                    <p className="text-sm text-text-muted">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                ) : (
                  <div className="text-center space-y-2 pointer-events-none">
                    <ArrowUpTrayIcon className={`w-10 h-10 mx-auto transition-colors ${isDragging ? "text-primary-500" : "text-text-muted"}`} />
                    <p className={`font-medium transition-colors ${isDragging ? "text-primary-600" : "text-text-primary"}`}>
                      {isDragging ? "Drop image here" : "Click or drag image to upload"}
                    </p>
                    <p className="text-sm text-text-muted">PNG, JPG, JPEG up to 10MB</p>
                  </div>
                )}
                <input
                  id="file-upload"
                  type="file"
                  className="hidden"
                  accept="image/png, image/jpeg, image/jpg"
                  onChange={handleFileChange}
                  disabled={isUploading}
                />
              </label>

              {error && (
                <div className="mt-4 p-3 w-full bg-error/10 border border-error/20 rounded-lg text-error text-sm text-center">
                  {error}
                </div>
              )}

              <Button
                onClick={handleUpload}
                isDisabled={!file || isUploading}
                isLoading={isUploading}
                className="w-full mt-6"
                size="lg"
              >
                {isUploading ? "Extracting..." : `Extract to Excel`}
              </Button>
            </>
        </div>
      </div>
    </div>
  );
}
