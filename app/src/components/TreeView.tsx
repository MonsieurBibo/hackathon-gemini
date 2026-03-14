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

function CustomNode({ nodeDatum, onNodeClick }: {
  nodeDatum: { name: string; attributes?: Record<string, string>; individu?: Individu }
  onNodeClick: (ind: Individu) => void
}) {
  const ind = nodeDatum.individu
  const statut = ind?.statut ?? 'inconnu'
  const isRoot = ind?.pere_id === undefined && ind?.mere_id === undefined
  const stroke = STATUT_STROKE[statut]
  const fill = isRoot ? '#0a0a0a' : '#f8f6f0'
  const textColor = isRoot ? '#c8f000' : '#0a0a0a'
  const year = nodeDatum.attributes?.year ?? '?'

  const handleClick = () => { if (ind) onNodeClick(ind) }

  return (
    <g onClick={handleClick} style={{ cursor: 'pointer' }}>
      {/* Lime accent bar */}
      {!isRoot && statut !== 'inconnu' && (
        <rect x={-72} y={-24} width={4} height={48} fill="#c8f000" />
      )}
      {/* Node box */}
      <rect
        x={-68}
        y={-24}
        width={136}
        height={48}
        fill={fill}
        stroke={stroke}
        strokeWidth={statut === 'inconnu' ? 1 : 2}
        strokeDasharray={statut === 'inconnu' ? '8 4' : undefined}
      />
      {/* Name */}
      <text
        y={-4}
        textAnchor="middle"
        fontFamily="'Archivo Black', sans-serif"
        fontSize={12}
        fill={textColor}
      >
        {nodeDatum.name.split(' ').slice(0, -1).join(' ')}
      </text>
      <text
        y={12}
        textAnchor="middle"
        fontFamily="'Archivo Black', sans-serif"
        fontSize={12}
        fill={textColor}
      >
        {nodeDatum.name.split(' ').pop()}
      </text>
      {/* Year */}
      <text
        y={26}
        textAnchor="middle"
        fontFamily="'JetBrains Mono', monospace"
        fontSize={9}
        fill={isRoot ? '#5a5a5a' : 'var(--mid)'}
      >
        {statut === 'inconnu' ? 'searching…' : `b. ${year}`}
      </text>
    </g>
  )
}

export function TreeView({ treeData, arbre, onNodeClick }: Props) {
  const genNum = arbre?.generation_courante ?? 1

  return (
    <div className="center-panel">
      <div className="gen-watermark">G{genNum}</div>

      <div className="tree-canvas">
        {treeData ? (
          <Tree
            data={treeData as never}
            orientation="horizontal"
            pathFunc="step"
            translate={{ x: window.innerWidth * 0.55, y: window.innerHeight * 0.4 }}
            nodeSize={{ x: 180, y: 80 }}
            separation={{ siblings: 1.2, nonSiblings: 1.4 }}
            renderCustomNodeElement={rd3tProps =>
              CustomNode({
                nodeDatum: rd3tProps.nodeDatum as never,
                onNodeClick,
              })
            }
            pathClassFunc={() => 'tree-edge-path'}
            zoom={0.85}
            scaleExtent={{ min: 0.3, max: 2 }}
          />
        ) : (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            flexDirection: 'column',
            gap: '12px',
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '11px',
            color: 'var(--mid)',
          }}>
            <div style={{
              fontFamily: 'Archivo Black, sans-serif',
              fontSize: '14px',
              color: 'var(--gray)',
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
            }}>
              Enter a name to begin
            </div>
            <div style={{ fontSize: '10px' }}>
              The tree will appear here as the agent discovers ancestors
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
