"use client";

import * as React from "react";
import { UploadCloud, File, X, CheckCircle, Database, Play } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import { useUpload, useUploadDemo, useReconcile } from "@/hooks/useApi";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";

export default function UploadPage() {
  const [files, setFiles] = React.useState<File[]>([]);
  const { mutate: uploadFiles, isPending: isUploading, isSuccess: isUploadSuccess, data: uploadData } = useUpload();
  const { mutate: uploadDemo, isPending: isUploadingDemo, isSuccess: isDemoSuccess, data: demoData } = useUploadDemo();
  const { mutate: runReconciliation, isPending: isReconciling, isSuccess: isReconcileSuccess } = useReconcile();
  const router = useRouter();

  React.useEffect(() => {
    if (isReconcileSuccess) {
      // Small delay so they can see the success state briefly before redirect
      const timeout = setTimeout(() => {
        router.push("/dashboard");
      }, 1500);
      return () => clearTimeout(timeout);
    }
  }, [isReconcileSuccess, router]);
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };
  
  const handleUpload = () => {
    if (files.length === 0) return;
    
    const formData = new FormData();
    files.forEach(file => {
      const name = file.name.toLowerCase();
      if (name.includes('bank')) formData.append('bank_statement', file);
      else if (name.includes('gateway')) formData.append('payment_gateway', file);
      else if (name.includes('settlement')) formData.append('settlement_report', file);
      else if (name.includes('invoice')) formData.append('invoice', file);
      else formData.append('files', file); // fallback
    });
    
    uploadFiles(formData);
  };
  
  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };
  
  const handleLoadDemo = () => {
    uploadDemo();
  };
  
  const handleRunReconciliation = () => {
    const batchId = uploadData?.batch_id || demoData?.batch_id;
    if (batchId) {
      runReconciliation(batchId);
    }
  };
  
  const isAnyUploadSuccess = isUploadSuccess || isDemoSuccess;
  const isAnyUploading = isUploading || isUploadingDemo;
  
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Upload Datasets</h1>
        <p className="text-text-secondary">Upload your bank statements and gateway exports for reconciliation.</p>
      </div>
      
      <div className="rounded-xl border border-border-default bg-bg-surface overflow-hidden shadow-sm">
        <div className="p-8">
          <div 
            className={cn(
              "border-2 border-dashed rounded-lg p-12 text-center transition-colors",
              files.length > 0 ? "border-brand bg-brand-subtle/30" : "border-border-strong hover:border-brand bg-bg-surface-sunken/50"
            )}
          >
            <div className="flex flex-col items-center justify-center space-y-4">
              <div className="p-4 bg-bg-surface rounded-full shadow-sm">
                <UploadCloud className="h-8 w-8 text-brand" />
              </div>
              <div>
                <p className="text-base font-medium text-text-primary">Drag & drop files here</p>
                <p className="text-sm text-text-secondary mt-1">or click to browse from your computer</p>
              </div>
              <p className="text-xs text-text-disabled max-w-xs">
                Supported formats: CSV, XLSX. Maximum file size 50MB.
              </p>
              
              <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-3">
                <input
                  type="file"
                  id="file-upload"
                  multiple
                  className="hidden"
                  onChange={handleFileChange}
                  accept=".csv,.xlsx"
                />
                <label 
                  htmlFor="file-upload" 
                  className={cn(buttonVariants({ variant: "default" }), "cursor-pointer bg-brand hover:bg-brand-hover text-white w-full sm:w-auto")}
                >
                  Select Files
                </label>
                <Button variant="outline" className="bg-bg-surface w-full sm:w-auto" onClick={handleLoadDemo} disabled={isAnyUploading}>
                  <Database className="h-4 w-4 mr-2" />
                  {isUploadingDemo ? "Generating..." : "Use Demo Dataset"}
                </Button>
              </div>
            </div>
          </div>
          
          {files.length > 0 && (
            <div className="mt-8 space-y-4">
              <h3 className="font-medium text-sm text-text-primary">Selected Files ({files.length})</h3>
              <div className="space-y-2">
                {files.map((file, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-lg border border-border-default bg-bg-surface flex-row">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-brand-subtle rounded text-brand">
                        <File className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-text-primary truncate max-w-[200px] sm:max-w-xs">{file.name}</p>
                        <p className="text-xs text-text-secondary">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                      </div>
                    </div>
                    <button 
                      onClick={() => removeFile(i)}
                      className="p-2 text-text-secondary hover:text-crimson hover:bg-crimson-subtle rounded transition-colors"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
              
              <div className="pt-4 flex justify-end">
                <Button 
                  onClick={handleUpload} 
                  disabled={isUploading || files.length === 0}
                  className="bg-brand hover:bg-brand-hover text-white w-full sm:w-auto"
                >
                  {isUploading ? "Uploading..." : "Upload & Continue"}
                </Button>
              </div>
            </div>
          )}
          
          {isAnyUploadSuccess && !isReconcileSuccess && (
            <div className="mt-6 p-4 bg-teal-subtle border border-teal/20 rounded-lg flex items-start space-x-3">
              <CheckCircle className="h-5 w-5 text-teal shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="text-sm font-medium text-teal">Upload Successful</h4>
                <p className="text-sm text-teal/80 mt-1 mb-3">Your files have been uploaded and validated. You can now proceed to reconciliation.</p>
                <Button 
                  onClick={handleRunReconciliation}
                  disabled={isReconciling}
                  className="bg-teal hover:bg-teal/90 text-white"
                >
                  {isReconciling ? "Running..." : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Run Reconciliation
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}
          
          {isReconcileSuccess && (
            <div className="mt-6 p-4 bg-brand-subtle border border-brand/20 rounded-lg flex items-start space-x-3">
              <CheckCircle className="h-5 w-5 text-brand shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="text-sm font-medium text-brand">Reconciliation Complete</h4>
                <p className="text-sm text-brand/80 mt-1 mb-3">The engine has finished processing your datasets.</p>
                <div className="flex gap-3">
                  <a href="/dashboard" className={buttonVariants({ variant: "default", className: "bg-brand hover:bg-brand-hover text-white" })}>
                    View Dashboard
                  </a>
                  <a href="/exceptions" className={buttonVariants({ variant: "outline", className: "border-brand/20 text-brand hover:bg-brand-subtle" })}>
                    Review Exceptions
                  </a>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
