import { useState } from 'react'
import { useSSE } from '@/hooks/useSSE'
import { useArbre } from '@/hooks/useArbre'
import { SearchPanel } from '@/components/SearchPanel'
import { AgentsPanel } from '@/components/AgentsPanel'
import { TreeView } from '@/components/TreeView'
import { IndividuCard } from '@/components/IndividuCard'
import { Chatbox } from '@/components/Chatbox'
import type { Individu } from '@/types'
import { MOCK_ARBRE, MOCK_AGENTS, MOCK_OCR } from '@/mocks/data'

const USE_MOCK = import.meta.env.DEV && import.meta.env.VITE_MOCK === 'true'

export default function App() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [selectedIndividu, setSelectedIndividu] = useState<Individu | null>(null)

  const sse = useSSE(USE_MOCK ? null : sessionId)
  const arbre = USE_MOCK ? MOCK_ARBRE : sse.arbre
  const agents = USE_MOCK ? MOCK_AGENTS : sse.agents
  const ocrStream = USE_MOCK ? MOCK_OCR : sse.ocrStream
  const question = USE_MOCK ? null : sse.question
  const isRunning = USE_MOCK ? false : sse.isRunning
  const error = USE_MOCK ? null : sse.error

  const { treeData, individuList } = useArbre(arbre)

  const genLabel = arbre ? `GEN ${arbre.generation_courante}/${arbre.generation_max}` : '—'
  const deptLabel = arbre ? (Object.values(arbre.individus)[0]?.naissance.dept ?? '—') : '—'
  const activeCount = agents.filter(a => a.status !== 'done' && a.status !== 'error').length

  return (
    <div className="app-layout">
      <header className="header">
        <div className="header-logo">
          <div className="header-logo-title">Genealogy<br />AI</div>
        </div>
        <div className="header-info">
          <div className="header-cell">
            <span className="header-cell-label">Department</span>
            <span className="header-cell-value">{deptLabel}</span>
          </div>
          <div className="header-cell">
            <span className="header-cell-label">Session</span>
            <span className="header-cell-value">{sessionId?.slice(0, 8) ?? '—'}</span>
          </div>
          <div className="header-cell">
            <span className="header-cell-label">Generation</span>
            <span className="header-cell-value">{genLabel}</span>
          </div>
          <div className="header-cell">
            <span className="header-cell-label">Agents</span>
            <span className="header-cell-value">{activeCount} active</span>
          </div>
        </div>
        {isRunning && (
          <div className="header-live">
            <div className="live-dot" />
            <span className="live-label">LIVE</span>
          </div>
        )}
        {error && (
          <div className="header-live">
            <span className="live-label" style={{ color: '#c83030' }}>ERROR</span>
          </div>
        )}
      </header>

      <div className="app-body">
        <SearchPanel
          individuList={individuList}
          selectedId={selectedIndividu?.id ?? null}
          onSelect={setSelectedIndividu}
          onSearch={setSessionId}
          isRunning={isRunning}
        />

        <TreeView
          treeData={treeData}
          arbre={arbre}
          onNodeClick={setSelectedIndividu}
        />

        <AgentsPanel agents={agents} ocrStream={ocrStream} />
      </div>

      {selectedIndividu && (
        <IndividuCard
          individu={selectedIndividu}
          arbre={arbre}
          onClose={() => setSelectedIndividu(null)}
          onNavigate={setSelectedIndividu}
        />
      )}

      {question && sessionId && (
        <Chatbox question={question} sessionId={sessionId} />
      )}
    </div>
  )
}
