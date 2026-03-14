import axios from 'axios'
import type { Individu, SearchFormData } from '@/types'

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export const api = axios.create({ baseURL: BASE })

export const startSearch = async (data: SearchFormData): Promise<string> => {
  const res = await api.post<{ session_id: string }>('/search', data)
  return res.data.session_id
}

export const answerQuestion = async (
  sessionId: string,
  agentId: string,
  individuId: string,
  choix: number | string,
): Promise<void> => {
  await api.post(`/answer/${sessionId}`, { agent_id: agentId, individu_id: individuId, choix })
}

export const getStreamUrl = (sessionId: string) => `${BASE}/stream/${sessionId}`

export async function semanticSearch(sessionId: string, query: string): Promise<Individu[]> {
  const resp = await api.get<Individu[]>('/similar', { params: { session_id: sessionId, q: query } })
  return resp.data
}
