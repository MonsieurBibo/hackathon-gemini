"""
Smoke test : remonte 1 génération depuis Prudence Aimée PINÇON (Cher, 1843).

Résultat attendu (POC vérifié manuellement) :
  - Père : Jean PINÇON, Neuilly-en-Sancerre
  - Mère : Jeanne Aimée DALLOY

Usage : .venv/bin/python smoke_test_prudence.py
"""
import asyncio
import sys

from agents.ocr_agent import PersonHint
from agents.recursive_agent import build_arbre
from models.events import (
    DoneEvent, ErrorEvent, IndividualEvent, IndividualUpdateEvent,
    OcrChunkEvent, StepEvent, ThinkingEvent,
)


def event_cb(event):
    match event.event:
        case "thinking":
            print(f"  💭 {event.message}")
        case "step":
            print(f"  → {event.message}")
        case "ocr_chunk":
            print(event.chunk, end="", flush=True)
        case "individual":
            ind = event.individu
            print(f"\n[INDIVIDU] {ind.prenom} {ind.nom} | gen={ind.generation} | {ind.naissance.commune} ~{ind.naissance.date}")
        case "individual_update":
            print(f"  ✅ update individu {str(event.individu_id)[:8]}… patch={event.patch}")
        case "error":
            print(f"  ❌ ERREUR : {event.message}", file=sys.stderr)
        case "done":
            arbre = event.arbre
            print(f"\n{'='*60}")
            print(f"ARBRE TERMINÉ — {len(arbre.individus)} individus")
            for ind in arbre.individus.values():
                parent_info = ""
                if ind.pere_id:
                    pere = arbre.individus.get(str(ind.pere_id))
                    if pere:
                        parent_info += f" | père={pere.prenom} {pere.nom}"
                if ind.mere_id:
                    mere = arbre.individus.get(str(ind.mere_id))
                    if mere:
                        parent_info += f" | mère={mere.prenom} {mere.nom}"
                print(f"  gen{ind.generation} {ind.prenom} {ind.nom} [{ind.statut}]{parent_info}")


async def main():
    hint = PersonHint(
        nom="PINÇON",
        prenom="Prudence Aimée",
        annee_naissance=1843,
        commune="Neuilly-en-Sancerre",
    )
    print(f"Smoke test : {hint.prenom} {hint.nom}, ~{hint.annee_naissance}, {hint.commune}")
    print("="*60)

    arbre = await build_arbre(hint, generation_max=1, event_cb=event_cb)

    # Vérifications
    root = arbre.individus[str(arbre.root_id)]
    ok = True
    if root.statut not in ("complet", "partiel"):
        print("FAIL: statut racine inattendu")
        ok = False
    if root.pere_id is None:
        print("FAIL: père non trouvé")
        ok = False
    else:
        pere = arbre.individus[str(root.pere_id)]
        if "PINÇON" not in pere.nom.upper():
            print(f"FAIL: nom père inattendu : {pere.nom}")
            ok = False
    if root.mere_id is None:
        print("FAIL: mère non trouvée")
        ok = False
    else:
        mere = arbre.individus[str(root.mere_id)]
        if "DALLOY" not in mere.nom.upper():
            print(f"FAIL: nom mère inattendu : {mere.nom}")
            ok = False

    print("\n" + ("✅ SMOKE TEST PASSED" if ok else "❌ SMOKE TEST FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
