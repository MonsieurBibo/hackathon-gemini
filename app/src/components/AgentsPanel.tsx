import { useEffect, useRef } from 'react'
import type { AgentState } from '@/types'

interface Props {
  agents: AgentState[]
  ocrStream: string
}

const BADGE_CLASS: Record<AgentState['status'], string> = {
  thinking: 'badge-thinking',
  searching: 'badge-searching',
  ocr: 'badge-ocr',
  extracting: 'badge-extracting',
  done: 'badge-done',
  error: 'badge-error',
}

const BADGE_LABEL: Record<AgentState['status'], string> = {
  thinking: 'thinking…',
  searching: 'searching',
  ocr: 'OCR',
  extracting: 'extracting',
  done: 'done ✓',
  error: 'error',
}

const PROG_CLASS: Record<AgentState['status'], string> = {
  thinking: 'prog-searching',
  searching: 'prog-searching',
  ocr: 'prog-ocr',
  extracting: 'prog-extracting',
  done: 'prog-done',
  error: 'prog-error',
}

const PROG_WIDTH: Record<AgentState['status'], string> = {
  thinking: '10%',
  searching: '28%',
  ocr: '60%',
  extracting: '85%',
  done: '100%',
  error: '100%',
}

export function AgentsPanel({ agents, ocrStream }: Props) {
  const ocrRef = useRef<HTMLDivElement>(null)
  const activeAgent = agents.find(a => a.status === 'ocr') ?? agents.find(a => a.status !== 'done' && a.status !== 'error')

  useEffect(() => {
    if (ocrRef.current) {
      ocrRef.current.scrollTop = ocrRef.current.scrollHeight
    }
  }, [ocrStream])

  return (
    <div className="panel panel-right">
      <div className="panel-head">
        <span className="panel-head-title">Agents</span>
        <span className="panel-head-count">{agents.length} total</span>
      </div>

      {agents.length === 0 ? (
        <div style={{ padding: '20px 14px', fontFamily: 'JetBrains Mono, monospace', fontSize: '10px', color: 'var(--mid)' }}>
          No agents running yet.
        </div>
      ) : (
        agents.map(agent => (
          <div
            key={agent.agent_id}
            className={`agent-card${agent.status === 'ocr' || agent.status === 'extracting' ? ' active' : ''}`}
          >
            <div className="agent-card-top">
              <span className="agent-name">{agent.individu_nom}</span>
              <span className={`agent-badge ${BADGE_CLASS[agent.status]}`}>
                {BADGE_LABEL[agent.status]}
              </span>
            </div>
            <div className="agent-msg">{agent.last_message}</div>
            <div className="agent-progress">
              <div
                className={`agent-progress-fill ${PROG_CLASS[agent.status]}`}
                style={{ width: agent.progress ? `${agent.progress}%` : PROG_WIDTH[agent.status] }}
              />
            </div>
          </div>
        ))
      )}

      <div className="ocr-zone">
        <div className="ocr-head">
          <span className="ocr-head-label">OCR Stream</span>
          {activeAgent && (
            <span className="ocr-head-sub">{activeAgent.individu_nom} · live</span>
          )}
        </div>
        <div className="ocr-body" ref={ocrRef}>
          {ocrStream
            ? ocrStream
            : <span style={{ color: 'var(--gray)' }}>Waiting for OCR…</span>
          }
          {ocrStream && <span className="ocr-cursor" />}
        </div>
      </div>
    </div>
  )
}
