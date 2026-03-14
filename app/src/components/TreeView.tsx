import { useRef, useEffect, useState } from 'react'
import Tree from 'react-d3-tree'
import type { Arbre, Individu } from '@/types'
import type { TreeNode } from '@/hooks/useArbre'

interface Props {
  treeData: TreeNode | null
  arbre: Arbre | null
  onNodeClick: (ind: Individu) => void
}

const STATUT_STROKE: Record<string, string> = {
  complet: '#2a6a2a',
  partiel: '#0a0a0a',
  inconnu: '#c8c4bc',
}

const W = 160
const H = 56

function CustomNode({ nodeDatum, rootId, onNodeClick }: {
  nodeDatum: { name: string; attributes?: Record<string, string>; individu?: Individu }
  rootId: string | null
  onNodeClick: (ind: Individu) => void
}) {
  const ind = nodeDatum.individu
  const statut = ind?.statut ?? 'inconnu'
  const isRoot = !!ind && ind.id === rootId
  const stroke = isRoot ? '#c8f000' : STATUT_STROKE[statut]
  const strokeWidth = isRoot ? 2 : statut === 'inconnu' ? 1 : 2
  const fill = isRoot ? '#0a0a0a' : '#f8f6f0'
  const textColor = isRoot ? '#c8f000' : '#0a0a0a'
  const year = nodeDatum.attributes?.year ?? '?'

  // Split name: last word = surname, rest = given name
  const parts = nodeDatum.name.split(' ')
  const surname = parts.pop() ?? ''
  const givenName = parts.join(' ')

  return (
    <g onClick={() => ind && onNodeClick(ind)} style={{ cursor: 'pointer' }}>
      {/* Lime accent bar on the left edge for non-root known nodes */}
      {!isRoot && statut !== 'inconnu' && (
        <rect x={-(W / 2)} y={-(H / 2)} width={4} height={H} fill="#c8f000" />
      )}
      <rect
        x={-(W / 2)} y={-(H / 2)} width={W} height={H}
        fill={fill}
        stroke={stroke}
        strokeWidth={strokeWidth}
        strokeDasharray={statut === 'inconnu' ? '8 4' : undefined}
      />
      <text y={-8} textAnchor="middle" fontFamily="'Archivo Black', sans-serif" fontSize={11} fill={textColor} stroke="none">
        {givenName}
      </text>
      <text y={7} textAnchor="middle" fontFamily="'Archivo Black', sans-serif" fontSize={11} fill={textColor} stroke="none">
        {surname}
      </text>
      <text y={22} textAnchor="middle" fontFamily="'JetBrains Mono', monospace" fontSize={9} fill={isRoot ? '#9a9890' : '#6a6860'} stroke="none">
        {statut === 'inconnu' ? 'searching…' : `b. ${year}`}
      </text>
    </g>
  )
}

const ZOOM_STEP = 0.15
const ZOOM_DEFAULT = 0.85

export function TreeView({ treeData, arbre, onNodeClick }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [translate, setTranslate] = useState({ x: 150, y: 300 })
  const [zoom, setZoom] = useState(ZOOM_DEFAULT)
  const genNum = arbre?.generation_courante ?? 1

  const fitTree = () => {
    if (!containerRef.current) return
    const { width, height } = containerRef.current.getBoundingClientRect()
    // root on left, ancestors expand to the right
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
              CustomNode({
                nodeDatum: rd3tProps.nodeDatum as never,
                rootId: arbre?.root_id ?? null,
                onNodeClick,
              })
            }
            pathClassFunc={() => 'tree-edge-path'}
            zoom={zoom}
            scaleExtent={{ min: 0.25, max: 2 }}
            enableLegacyTransitions
            transitionDuration={300}
          />
        ) : (
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            height: '100%', flexDirection: 'column', gap: '12px',
          }}>
            <div style={{
              fontFamily: 'Archivo Black, sans-serif', fontSize: '14px',
              color: 'var(--gray)', letterSpacing: '0.1em', textTransform: 'uppercase',
            }}>
              Enter a name to begin
            </div>
            <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '10px', color: 'var(--mid)' }}>
              The tree builds here as the agent discovers ancestors
            </div>
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
