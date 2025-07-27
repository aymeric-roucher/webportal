import { useQuery } from 'react-query'
import { supabase } from '@/utils/supabase'
import { CachedSite } from '@/types'

export function useCachedSites() {
  return useQuery<CachedSite[]>(
    'cached-sites',
    async () => {
      const { data, error } = await supabase
        .from('cached_sites')
        .select('*')
        .order('download_count', { ascending: false })
      
      if (error) throw error
      
      return data.map(site => ({
        domain: site.domain,
        filePath: site.file_path,
        lastUpdated: site.last_updated,
        title: site.title,
        description: site.description
      }))
    }
  )
}

export function useCheckCache(domain: string) {
  return useQuery<CachedSite | null>(
    ['cached-site', domain],
    async () => {
      if (!domain) return null
      
      const { data, error } = await supabase
        .from('cached_sites')
        .select('*')
        .eq('domain', domain)
        .single()
      
      if (error) {
        if (error.code === 'PGRST116') {
          return null
        }
        throw error
      }
      
      return {
        domain: data.domain,
        filePath: data.file_path,
        lastUpdated: data.last_updated,
        title: data.title,
        description: data.description
      }
    },
    {
      enabled: !!domain
    }
  )
}