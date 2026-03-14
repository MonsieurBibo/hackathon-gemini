import { useEffect, useRef, useState, useCallback } from 'react'
import type { Arbre, AgentState, SSEEvent } from '@/types'
import { getStreamUrl } from '@/api/client'

interface SSEState {
  arbre: Arbre | null
  agents: AgentState[]
  ocrStream: string
  question: Extract<SSEEvent, { type: 'question' }> | null
  isRunning: boolean
  error: string | null
}

const AGENT_PROGRESS: Record<AgentState['status'], number> = {
  thinking: 10,
  searching: 25,
  ocr: 60,
  extracting: 85,
  done: 100,
  error: 100,
}

export function useSSE(sessionId: string | null): SSEState {
  const [state, setState] = useState<SSEState>({
    arbre: null,
    agents: [],
    ocrStream: '',
    question: null,
    isRunning: false,
    error: null,
  })

  const esRef = useRef<EventSource | null>(null)

  const updateAgent = useCallback((agentId: string, individuId: string, patch: Partial<AgentState>) => {
    setState(prev => {
      const idx = prev.agents.findIndex(a => a.agent_id === agentId)
      if (idx === -1) {
        return {
          ...prev,
          agents: [...prev.agents, {
            agent_id: agentId,
            individu_id: individuId,
            individu_nom: patch.individu_nom ?? individuId,
            status: patch.status ?? 'thinking',
            last_message: patch.last_message ?? '',
            progress: patch.progress ?? 10,
            ...patch,
          }],
        }
      }
      const updated = [...prev.agents]
      updated[idx] = { ...updated[idx], ...patch }
      return { ...prev, agents: updated }
    })
  }, [])

  useEffect(() => {
    if (!sessionId) return

    esRef.current?.close()

    const es = new EventSource(getStreamUrl(sessionId))
    esRef.current = es

    setState(prev => ({ ...prev, isRunning: true, error: null, ocrStream: '' }))

    const handle = (eventType: string, raw: string) => {
      try {
        const data = JSON.parse(raw) as SSEEvent & { type: string }

        switch (eventType) {
          case 'thinking': {
            const e = data as Extract<SSEEvent, { type: 'thinking' }>
            updateAgent(e.agent_id, e.individu_id, {
              status: 'thinking',
              last_message: e.message,
              progress: AGENT_PROGRESS.thinking,
            })
            break
          }

          case 'step': {
            const e = data as Extract<SSEEvent, { type: 'step' }>
            updateAgent(e.agent_id, e.individu_id, {
              status: 'searching',
              last_message: e.message,
              progress: AGENT_PROGRESS.searching,
            })
            break
          }

          case 'ocr_chunk': {
            const e = data as Extract<SSEEvent, { type: 'ocr_chunk' }>
            updateAgent(e.agent_id, e.individu_id, {
              status: 'ocr',
              last_message: 'Reading document…',
              progress: AGENT_PROGRESS.ocr,
            })
            const chunk = e.chunk
            setState(prev => ({ ...prev, ocrStream: prev.ocrStream + chunk }))
            break
          }

          case 'individual': {
            const individu = (data as Extract<SSEEvent, { type: 'individual' }>).individu
            setState(prev => ({
              ...prev,
              arbre: prev.arbre
                ? { ...prev.arbre, individus: { ...prev.arbre.individus, [individu.id]: individu } }
                : null,
            }))
            break
          }

          case 'individual_update': {
            const { individu_id, patch } = data as Extract<SSEEvent, { type: 'individual_update' }>
            setState(prev => {
              if (!prev.arbre) return prev
              const existing = prev.arbre.individus[individu_id]
              if (!existing) return prev
              return {
                ...prev,
                arbre: {
                  ...prev.arbre,
                  individus: { ...prev.arbre.individus, [individu_id]: { ...existing, ...patch } },
                },
              }
            })
            break
          }

          case 'fallback': {
            const f = data as Extract<SSEEvent, { type: 'fallback' }>
            updateAgent(f.agent_id, f.individu_id, {
              status: 'searching',
              last_message: `Fallback #${f.tentative}: ${f.action}`,
              tentative: f.tentative,
            })
            break
          }

          case 'question':
            setState(prev => ({ ...prev, question: data as Extract<SSEEvent, { type: 'question' }> }))
            break

          case 'error': {
            const e = data as Extract<SSEEvent, { type: 'error' }>
            updateAgent(e.agent_id, e.individu_id, {
              status: 'error',
              last_message: e.message,
              progress: 100,
            })
            break
          }

          case 'done': {
            const arbre = (data as Extract<SSEEvent, { type: 'done' }>).arbre
            setState(prev => ({ ...prev, arbre, isRunning: false }))
            es.close()
            break
          }
        }
      } catch {
        // malformed JSON — ignore
      }
    }

    // react-to named SSE events
    const events = ['thinking', 'step', 'ocr_chunk', 'individual', 'individual_update', 'fallback', 'question', 'error', 'done']
    events.forEach(evt => {
      es.addEventListener(evt, (e: MessageEvent) => handle(evt, e.data))
    })

    es.onerror = () => {
      setState(prev => ({ ...prev, isRunning: false, error: 'Connection lost' }))
      es.close()
    }

    return () => { es.close() }
  }, [sessionId, updateAgent])

  return state
}
