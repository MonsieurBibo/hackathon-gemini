import { useState } from 'react'
import { useSSE } from '@/hooks/useSSE'
import { useArbre } from '@/hooks/useArbre'
import { SearchPanel } from '@/components/SearchPanel'
import { AgentsPanel } from '@/components/AgentsPanel'
import { TreeView } from '@/components/TreeView'
import { IndividuCard } from '@/components/IndividuCard'
import { Chatbox } from '@/components/Chatbox'
import { StartScreen } from '@/components/StartScreen'
import type { Individu } from '@/types'

export default function App() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [selectedIndividu, setSelectedIndividu] = useState<Individu | null>(null)

  const sse = useSSE(sessionId)
  const arbre = sse.arbre
  const agents = sse.agents
  const ocrStream = sse.ocrStream
  const question = sse.question
  const isRunning = sse.isRunning
  const error = sse.error

  const { treeData, individuList } = useArbre(arbre)

  const genLabel = arbre ? `GEN ${arbre.generation_courante}/${arbre.generation_max}` : '—'
  const deptLabel = arbre ? (Object.values(arbre.individus)[0]?.naissance.dept ?? '—') : '—'
  const activeCount = agents.filter(a => a.status !== 'done' && a.status !== 'error').length

  const handleReset = () => {
    setSessionId(null)
    setSelectedIndividu(null)
  }

  return (
    <div className="app-layout">
      <header className="header">
        <div
          className="header-logo"
          onClick={handleReset}
          style={{ cursor: 'pointer' }}
          title="Back to start"
        >
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

      {!sessionId ? (
        <StartScreen onSearch={setSessionId} />
      ) : (
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
      )}

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
