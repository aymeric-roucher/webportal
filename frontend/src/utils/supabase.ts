import { createClient } from '@supabase/supabase-js'
import { ProcessingJob, User } from '@/types'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export interface Database {
  public: {
    Tables: {
      processing_jobs: {
        Row: ProcessingJob
        Insert: Omit<ProcessingJob, 'id' | 'createdAt'>
        Update: Partial<Omit<ProcessingJob, 'id'>>
      }
      users: {
        Row: User
        Insert: Omit<User, 'id'>
        Update: Partial<Omit<User, 'id'>>
      }
      cached_sites: {
        Row: {
          id: string
          domain: string
          file_path: string
          last_updated: string
          title: string
          description?: string
          download_count: number
        }
        Insert: Omit<{
          id: string
          domain: string
          file_path: string
          last_updated: string
          title: string
          description?: string
          download_count: number
        }, 'id' | 'download_count'>
        Update: Partial<Omit<{
          id: string
          domain: string
          file_path: string
          last_updated: string
          title: string
          description?: string
          download_count: number
        }, 'id'>>
      }
    }
  }
}

export type TypedSupabaseClient = typeof supabase