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

function CustomNode({ nodeDatum, rootId, onNodeClick }: {
  nodeDatum: { name: string; attributes?: Record<string, string>; individu?: Individu }
  rootId: string | null
  onNodeClick: (ind: Individu) => void
}) {
  const ind = nodeDatum.individu
  const statut = ind?.statut ?? 'inconnu'
  const isRoot = !!ind && ind.id === rootId
  const stroke = STATUT_STROKE[statut]
  const fill = isRoot ? '#0a0a0a' : '#f8f6f0'
  const textColor = isRoot ? '#c8f000' : '#0a0a0a'
  const year = nodeDatum.attributes?.year ?? '?'

  return (
    <g onClick={() => ind && onNodeClick(ind)} style={{ cursor: 'pointer' }}>
      {!isRoot && statut !== 'inconnu' && (
        <rect x={-72} y={-26} width={4} height={52} fill="#c8f000" />
      )}
      <rect
        x={-68} y={-26} width={136} height={52}
        fill={fill}
        stroke={stroke}
        strokeWidth={statut === 'inconnu' ? 1 : 2}
        strokeDasharray={statut === 'inconnu' ? '8 4' : undefined}
      />
      <text y={-6} textAnchor="middle" fontFamily="'Archivo Black', sans-serif" fontSize={12} fill={textColor}>
        {nodeDatum.name.split(' ').slice(0, -1).join(' ')}
      </text>
      <text y={10} textAnchor="middle" fontFamily="'Archivo Black', sans-serif" fontSize={12} fill={textColor}>
        {nodeDatum.name.split(' ').pop()}
      </text>
      <text y={26} textAnchor="middle" fontFamily="'JetBrains Mono', monospace" fontSize={9} fill={isRoot ? '#5a5a5a' : '#6a6860'}>
        {statut === 'inconnu' ? 'searching…' : `b. ${year}`}
      </text>
    </g>
  )
}

export function TreeView({ treeData, arbre, onNodeClick }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [translate, setTranslate] = useState({ x: 600, y: 300 })
  const genNum = arbre?.generation_courante ?? 1

  useEffect(() => {
    if (!containerRef.current) return
    const { width, height } = containerRef.current.getBoundingClientRect()
    // root on right side, ancestors expand to the left
    setTranslate({ x: width * 0.72, y: height * 0.5 })
  }, [treeData])

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
            nodeSize={{ x: 200, y: 90 }}
            separation={{ siblings: 1.2, nonSiblings: 1.5 }}
            renderCustomNodeElement={rd3tProps =>
              CustomNode({
                nodeDatum: rd3tProps.nodeDatum as never,
                rootId: arbre?.root_id ?? null,
                onNodeClick,
              })
            }
            pathClassFunc={() => 'tree-edge-path'}
            zoom={0.85}
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
        <button className="zoom-btn">+</button>
        <button className="zoom-btn">−</button>
        <button className="zoom-btn" style={{ fontSize: '14px' }}>⤢</button>
      </div>
    </div>
  )
}
