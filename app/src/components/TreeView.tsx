import React, { useRef, useEffect, useState } from 'react'
import Tree from 'react-d3-tree'
import type { Arbre, Individu, SSEEvent } from '@/types'
import type { TreeNode } from '@/hooks/useArbre'

interface Props {
  treeData: TreeNode | null
  arbre: Arbre | null
  onNodeClick: (ind: Individu) => void
  onSearchParents: (ind: Individu) => void
  questionedIndividuId: string | null
  question: Extract<SSEEvent, { type: 'question' }> | null
  onAnswer: (agentId: string, individuId: string, choix: number) => void
}

const STATUT_STROKE: Record<string, string> = {
  complet: '#2a6a2a',
  partiel: '#0a0a0a',
  inconnu: '#c8c4bc',
  post_1900: '#1a4a8a',
}

const W = 160
const H = 56
const BTN_H = 20
const BTN_Y_OFFSET = H / 2 + 4

function CustomNode({ nodeDatum, rootId, onNodeClick, onSearchParents, questionedIndividuId, question, onAnswer, arbre }: {
  nodeDatum: { name: string; attributes?: Record<string, string>; individu?: Individu }
  rootId: string | null
  onNodeClick: (ind: Individu) => void
  onSearchParents: (ind: Individu) => void
  questionedIndividuId: string | null
  question: Extract<SSEEvent, { type: 'question' }> | null
  onAnswer: (agentId: string, individuId: string, choix: number) => void
  arbre: Arbre | null
}) {
  const [minimized, setMinimized] = useState(false)

  const ind = nodeDatum.individu
  const statut = ind?.statut ?? 'inconnu'
  const isPost1900 = statut === 'post_1900' ||
    (!!ind?.naissance.date && parseInt(ind.naissance.date.slice(0, 4)) > 1900)
  const isRoot = !!ind && ind.id === rootId
  const isQuestioned = !!ind && ind.id === questionedIndividuId
  const stroke = isRoot ? '#c8f000' : (STATUT_STROKE[statut] ?? '#c8c4bc')
  const strokeWidth = isRoot ? 2 : statut === 'inconnu' ? 1 : 2
  const fill = isRoot ? '#0a0a0a' : isPost1900 ? '#1a4a8a' : '#f8f6f0'
  const textColor = isRoot ? '#c8f000' : isPost1900 ? '#ffffff' : '#0a0a0a'
  const year = nodeDatum.attributes?.year ?? '?'

  const parts = nodeDatum.name.split(' ')
  const surname = parts.pop() ?? ''
  const givenName = parts.join(' ')

  const showSearchBtn = !!ind && ind.pere_id === null && ind.mere_id === null && statut !== 'complet'

  const handleSearchClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (ind) onSearchParents(ind)
  }

  const individu = question ? (arbre?.individus[question.individu_id] ?? null) : null
  const foreignY = showSearchBtn ? H / 2 + BTN_H + 16 : H / 2 + 12

  return (
    <g onClick={() => ind && onNodeClick(ind)} style={{ cursor: 'pointer' }}>
      {!isRoot && statut !== 'inconnu' && (
        <rect x={-(W / 2)} y={-(H / 2)} width={4} height={H} fill="#c8f000" />
      )}
      <rect
        x={-(W / 2)} y={-(H / 2)} width={W} height={H}
        fill={fill} stroke={stroke} strokeWidth={strokeWidth}
        strokeDasharray={statut === 'inconnu' ? '8 4' : undefined}
      />
      <text y={-8} textAnchor="middle" fontFamily="'Archivo Black', sans-serif" fontSize={11} fill={textColor} stroke="none">
        {givenName}
      </text>
      <text y={7} textAnchor="middle" fontFamily="'Archivo Black', sans-serif" fontSize={11} fill={textColor} stroke="none">
        {surname}
      </text>
      <text y={22} textAnchor="middle" fontFamily="'JetBrains Mono', monospace" fontSize={9} fill={isRoot ? '#9a9890' : isPost1900 ? '#a0b8d8' : '#6a6860'} stroke="none">
        {statut === 'inconnu' ? 'searching…' : isPost1900 ? `b. ${year} ·restricted` : `b. ${year}`}
      </text>

      {showSearchBtn && (
        <g onClick={handleSearchClick} style={{ cursor: 'pointer' }}>
          <rect x={-(W / 2)} y={BTN_Y_OFFSET} width={W} height={BTN_H} fill="#0a0a0a" stroke="#c8f000" strokeWidth={1.5} />
          <text y={BTN_Y_OFFSET + BTN_H / 2 + 4} textAnchor="middle" fontFamily="'Archivo Black', sans-serif" fontSize={9} fill="#c8f000" stroke="none" letterSpacing="0.15em">
            + SEARCH PARENTS
          </text>
        </g>
      )}

      {isQuestioned && (
        <rect x={-(W / 2) - 4} y={-(H / 2) - 4} width={W + 8} height={H + 8} fill="none" stroke="#c8f000" strokeWidth={2} className="node-questioned" />
      )}

      {isQuestioned && question !== null && (
        <foreignObject x={-190} y={foreignY} width={380} height={minimized ? 44 : 200}>
          <div xmlns="http://www.w3.org/1999/xhtml" style={{ background: '#0a0a0a', border: '2px solid #c8f000', fontFamily: 'Archivo, sans-serif', fontSize: '11px', color: '#f8f6f0', boxShadow: '4px 4px 0 rgba(0,0,0,0.5)' }}>
            <div style={{ display: 'flex', alignItems: 'center', padding: '8px 12px', borderBottom: minimized ? 'none' : '1px solid #2a2a2a', gap: '8px' }}>
              <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '9px', color: '#888', letterSpacing: '0.1em' }}>{question.agent_id.toUpperCase()}</span>
              <span style={{ color: '#555' }}>→</span>
              <span style={{ fontFamily: '"Archivo Black", sans-serif', fontSize: '11px', color: '#c8f000', textTransform: 'uppercase', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {individu ? `${individu.prenom} ${individu.nom}` : question.individu_id}
              </span>
              <div style={{ width: '6px', height: '6px', background: '#c8f000', borderRadius: '50%' }} />
              <button onClick={(e) => { e.stopPropagation(); setMinimized(m => !m) }} style={{ background: 'none', border: '1px solid #444', color: '#aaa', fontFamily: 'monospace', fontSize: '12px', width: '20px', height: '20px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                {minimized ? '□' : '−'}
              </button>
            </div>
            {!minimized && (
              <div style={{ padding: '10px 12px', overflow: 'hidden' }}>
                <div style={{ marginBottom: '8px', lineHeight: '1.5', fontSize: '10px' }}>{question.question}</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {question.options.map((opt, i) => (
                    <button key={i} onClick={(e) => { e.stopPropagation(); onAnswer(question.agent_id, question.individu_id, i) }}
                      style={{ background: 'transparent', border: '1px solid #3a3a3a', color: '#f8f6f0', fontFamily: 'JetBrains Mono, monospace', fontSize: '9px', padding: '5px 10px', textAlign: 'left', cursor: 'pointer' }}
                      onMouseEnter={e => { (e.target as HTMLButtonElement).style.background = '#c8f000'; (e.target as HTMLButtonElement).style.color = '#0a0a0a' }}
                      onMouseLeave={e => { (e.target as HTMLButtonElement).style.background = 'transparent'; (e.target as HTMLButtonElement).style.color = '#f8f6f0' }}
                    >
                      [{i + 1}] {opt}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </foreignObject>
      )}
    </g>
  )
}

const ZOOM_STEP = 0.15
const ZOOM_DEFAULT = 0.85

export function TreeView({ treeData, arbre, onNodeClick, onSearchParents, questionedIndividuId, question, onAnswer }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [translate, setTranslate] = useState({ x: 150, y: 300 })
  const [zoom, setZoom] = useState(ZOOM_DEFAULT)
  const genNum = arbre?.generation_courante ?? 1

  const fitTree = () => {
    if (!containerRef.current) return
    const { width, height } = containerRef.current.getBoundingClientRect()
    setTranslate({ x: width * 0.18, y: height * 0.5 })
    setZoom(ZOOM_DEFAULT)
  }

  useEffect(() => { fitTree() }, [treeData])

  return (
    <div className="center-panel">
      <div className="gen-watermark">G{genNum}</div>
      <div className="tree-canvas" ref={containerRef}>
        {treeData ? (
          <Tree
            data={treeData as never}
            orientation="horizontal"
            pathFunc="step"
            translate={translate}
            nodeSize={{ x: 220, y: 90 }}
            separation={{ siblings: 1.2, nonSiblings: 1.5 }}
            renderCustomNodeElement={rd3tProps =>
              <CustomNode
                nodeDatum={rd3tProps.nodeDatum as never}
                rootId={arbre?.root_id ?? null}
                onNodeClick={onNodeClick}
                onSearchParents={onSearchParents}
                questionedIndividuId={questionedIndividuId}
                question={question}
                onAnswer={onAnswer}
                arbre={arbre}
              />
            }
            pathClassFunc={() => 'tree-edge-path'}
            zoom={zoom}
            scaleExtent={{ min: 0.25, max: 2 }}
            enableLegacyTransitions
            transitionDuration={300}
          />
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', flexDirection: 'column', gap: '12px' }}>
            <div style={{ fontFamily: 'Archivo Black, sans-serif', fontSize: '14px', color: 'var(--gray)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>Enter a name to begin</div>
            <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '10px', color: 'var(--mid)' }}>The tree builds here as the agent discovers ancestors</div>
          </div>
        )}
      </div>
      <div className="zoom-controls">
        <button className="zoom-btn" onClick={() => setZoom(z => Math.min(2, z + ZOOM_STEP))}>+</button>
        <button className="zoom-btn" onClick={() => setZoom(z => Math.max(0.25, z - ZOOM_STEP))}>−</button>
        <button className="zoom-btn" style={{ fontSize: '14px' }} onClick={fitTree}>⤢</button>
      </div>
    </div>
  )
}
