import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiFetch } from './client'
import type { Problem, Solution, ImpactStats, SubmitResponse } from '../types'

export function useProblems() {
  return useQuery<Problem[]>({
    queryKey: ['problems'],
    queryFn: () => apiFetch('/api/problems'),
  })
}

export function useSolutions() {
  return useQuery<Solution[]>({
    queryKey: ['solutions'],
    queryFn: () => apiFetch('/api/solutions'),
  })
}

export function useStats() {
  return useQuery<ImpactStats>({
    queryKey: ['stats'],
    queryFn: () => apiFetch('/api/stats'),
    refetchInterval: 10_000,
  })
}

export function useSubmitProblem() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: { title: string; description: string; location?: string; submitted_by?: string }) =>
      apiFetch<SubmitResponse>('/api/submit', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      // invalidate after a delay — agents need time
      setTimeout(() => {
        qc.invalidateQueries({ queryKey: ['problems'] })
        qc.invalidateQueries({ queryKey: ['solutions'] })
        qc.invalidateQueries({ queryKey: ['stats'] })
      }, 2000)
    },
  })
}
