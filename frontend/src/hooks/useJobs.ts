import { useQuery, useMutation, useQueryClient } from 'react-query'
import { supabase } from '@/utils/supabase'
import { ProcessingJob, ConversionRequest } from '@/types'

export function useJobs() {
  const queryClient = useQueryClient()
  
  const { data: jobs = [], isLoading } = useQuery<ProcessingJob[]>(
    'jobs',
    async () => {
      const { data, error } = await supabase
        .from('processing_jobs')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (error) throw error
      return data
    }
  )
  
  const createJobMutation = useMutation(
    async (request: ConversionRequest) => {
      const response = await fetch('/api/process-website', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      })
      
      if (!response.ok) {
        throw new Error('Failed to create job')
      }
      
      return response.json()
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('jobs')
      }
    }
  )
  
  const updateJobMutation = useMutation(
    async ({ id, updates }: { id: string; updates: Partial<ProcessingJob> }) => {
      const { data, error } = await supabase
        .from('processing_jobs')
        .update(updates)
        .eq('id', id)
        .select()
        .single()
      
      if (error) throw error
      return data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('jobs')
      }
    }
  )
  
  return {
    jobs,
    isLoading,
    createJob: createJobMutation.mutate,
    updateJob: updateJobMutation.mutate,
    isCreating: createJobMutation.isLoading,
    isUpdating: updateJobMutation.isLoading
  }
}

export function useJob(jobId: string) {
  return useQuery<ProcessingJob>(
    ['job', jobId],
    async () => {
      const { data, error } = await supabase
        .from('processing_jobs')
        .select('*')
        .eq('id', jobId)
        .single()
      
      if (error) throw error
      return data
    },
    {
      enabled: !!jobId,
      refetchInterval: (data) => {
        return data?.status === 'processing' || data?.status === 'queued' ? 2000 : false
      }
    }
  )
}

export function useRealtimeJobs() {
  const queryClient = useQueryClient()
  
  useQuery(
    'realtime-jobs',
    () => null,
    {
      enabled: false,
      onSuccess: () => {
        const subscription = supabase
          .channel('processing_jobs')
          .on(
            'postgres_changes',
            {
              event: '*',
              schema: 'public',
              table: 'processing_jobs'
            },
            (payload) => {
              queryClient.invalidateQueries('jobs')
              if (payload.new && typeof payload.new === 'object') {
                queryClient.setQueryData(
                  ['job', (payload.new as ProcessingJob).id],
                  payload.new
                )
              }
            }
          )
          .subscribe()
        
        return () => {
          subscription.unsubscribe()
        }
      }
    }
  )
}