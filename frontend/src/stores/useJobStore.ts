import { create } from 'zustand'
import { ProcessingJob } from '@/types'

interface JobStore {
  currentJob: ProcessingJob | null
  jobs: ProcessingJob[]
  setCurrentJob: (job: ProcessingJob | null) => void
  addJob: (job: ProcessingJob) => void
  updateJob: (id: string, updates: Partial<ProcessingJob>) => void
  getJob: (id: string) => ProcessingJob | undefined
}

export const useJobStore = create<JobStore>((set, get) => ({
  currentJob: null,
  jobs: [],
  setCurrentJob: (job) => set({ currentJob: job }),
  addJob: (job) => set((state) => ({ 
    jobs: [...state.jobs, job],
    currentJob: job 
  })),
  updateJob: (id, updates) => set((state) => {
    const updatedJobs = state.jobs.map(job => 
      job.id === id ? { ...job, ...updates } : job
    )
    const updatedCurrentJob = state.currentJob?.id === id 
      ? { ...state.currentJob, ...updates }
      : state.currentJob
    
    return {
      jobs: updatedJobs,
      currentJob: updatedCurrentJob
    }
  }),
  getJob: (id) => get().jobs.find(job => job.id === id)
}))