import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ApiService } from '@/lib/api/services';
import { toast } from 'sonner';

export function useDashboard() {
  return useQuery<any>({
    queryKey: ['dashboard'],
    queryFn: () => ApiService.dashboard.get(),
  });
}

export function useUpload() {
  return useMutation<any, Error, FormData>({
    mutationFn: (formData: FormData) => ApiService.upload.uploadFiles(formData),
    onSuccess: () => {
      toast.success("Files uploaded successfully", {
        description: "Your dataset has been validated and stored.",
      });
    },
    onError: (error) => {
      toast.error("Upload failed", {
        description: error.message || "There was a problem uploading your files.",
      });
    }
  });
}

export function useUploadDemo() {
  const queryClient = useQueryClient();
  return useMutation<any, Error, void>({
    mutationFn: () => ApiService.upload.uploadDemo(),
    onSuccess: (data) => {
      toast.success("Demo dataset generated and uploaded successfully");
      return data;
    },
    onError: (error) => {
      toast.error("Failed to generate demo dataset", {
        description: error.message,
      });
    }
  });
}

export function useReconcile() {
  const queryClient = useQueryClient();
  return useMutation<any, Error, string>({
    mutationFn: (batchId: string) => ApiService.reconcile.run(batchId),
    onSuccess: () => {
      toast.success("Reconciliation complete", {
        description: "The engine has finished processing your datasets.",
      });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['exceptions'] });
      queryClient.invalidateQueries({ queryKey: ['reports'] });
    },
    onError: (error) => {
      toast.error("Reconciliation failed", {
        description: error.message || "An error occurred during reconciliation.",
      });
    }
  });
}

export function useExceptions(params?: Record<string, any>) {
  return useQuery<any>({
    queryKey: ['exceptions', params],
    queryFn: () => ApiService.exceptions.list(params),
  });
}

export function useReports() {
  return useQuery<any>({
    queryKey: ['reports'],
    queryFn: () => ApiService.reports.list(),
  });
}

export function useAIExplain() {
  return useMutation<any, Error, string>({
    mutationFn: (exceptionId: string) => ApiService.ai.explain(exceptionId),
  });
}

export function useSettings() {
  return useQuery<any>({
    queryKey: ['settings'],
    queryFn: () => ApiService.settings.get(),
  });
}

export function useUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation<any, Error, Record<string, any>>({
    mutationFn: (data: Record<string, any>) => ApiService.settings.update(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });
}
