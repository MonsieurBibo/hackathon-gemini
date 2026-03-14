import { useMemo } from 'react'
import type { Arbre, Individu } from '@/types'

export interface TreeNode {
  name: string
  attributes?: Record<string, string>
  children?: TreeNode[]
  individu: Individu
}

function buildNode(id: string, individus: Record<string, Individu>): TreeNode | null {
  const ind = individus[id]
  if (!ind) return null

  const children: TreeNode[] = []

  if (ind.pere_id) {
    const node = buildNode(ind.pere_id, individus)
    if (node) children.push(node)
  }

  if (ind.mere_id) {
    const node = buildNode(ind.mere_id, individus)
    if (node) children.push(node)
  }

  return {
    name: `${ind.prenom} ${ind.nom}`,
    attributes: {
      year: ind.naissance.date
        ? ind.naissance.date.slice(0, 4)
        : ind.naissance.date_approx
          ? 'ca. ?'
          : '?',
      statut: ind.statut,
    },
    children: children.length > 0 ? children : undefined,
    individu: ind,
  }
}

export function useArbre(arbre: Arbre | null) {
  const treeData = useMemo(() => {
    if (!arbre?.root_id) return null
    return buildNode(arbre.root_id, arbre.individus)
  }, [arbre])

  const individuList = useMemo(() => {
    if (!arbre) return []
    return Object.values(arbre.individus).sort((a, b) => a.generation - b.generation)
  }, [arbre])

  return { treeData, individuList }
}
