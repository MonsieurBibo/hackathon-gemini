"""
Agent post-1900 — B8

Les actes d'état civil postérieurs à 1900 ne sont pas en ligne sur Arkotheque.
Cet agent :
  1. Détermine l'administration compétente selon l'acte, l'année et le lien de parenté.
  2. Génère un courrier de demande pré-rempli via Gemini 2.5 Pro.

Règles de communicabilité française (loi 2008-696 + CNIL) :
  - Naissance : libre > 75 ans après la clôture du registre, sinon ayants droit uniquement
  - Mariage   : libre > 75 ans après la clôture du registre, sinon ayants droit uniquement
  - Décès     : libre > 25 ans après la date du décès (toujours communicable à tous)
  - Matricule militaire : SHD (hommes nés 1867-1921) ou archives départementales (en ligne Mémoire des Hommes)
  - Nés à l'étranger   : Service central d'état civil (SCEC), Nantes
  - Actes consulaires  : Archives du MEAE (ministère des Affaires étrangères)

Ref tâche : B8 (docs/tasks/backend.md)
"""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel

from services.gemini import answer_admin_question

# Année de référence pour calculer les délais
_ANNEE_REF = 2026

# ---------------------------------------------------------------------------
# Modèles de sortie
# ---------------------------------------------------------------------------

TypeActe = Literal["naissance", "mariage", "deces", "matricule"]
LienFamille = Literal["moi-même", "parent", "grand-parent", "arriere-grand-parent", "autre"]


class Administration(BaseModel):
    nom: str
    adresse: str | None = None
    url: str | None = None
    telephone: str | None = None
    email: str | None = None
    notes: str | None = None


class AdminResult(BaseModel):
    accessible: bool                  # l'acte est-il communicable à cette personne ?
    acces_libre: bool                 # communicable à tout demandeur (délai écoulé)
    administration: Administration
    justificatifs: list[str]          # pièces à fournir
    delai_reponse: str                # délai indicatif
    courrier: str                     # texte du courrier pré-rempli


# ---------------------------------------------------------------------------
# Routing déterministe
# ---------------------------------------------------------------------------

def _est_acces_libre(type_acte: TypeActe, annee_acte: int) -> bool:
    """
    Retourne True si l'acte est communicable à tout demandeur (délai légal écoulé).
    """
    anciennete = _ANNEE_REF - annee_acte
    if type_acte == "deces":
        return anciennete > 25
    elif type_acte in ("naissance", "mariage"):
        return anciennete > 75
    elif type_acte == "matricule":
        # Matricules en ligne sur Mémoire des Hommes : classes 1867–1921
        return annee_acte <= 1921
    return False


def _est_ayant_droit(lien: LienFamille) -> bool:
    return lien in ("moi-même", "parent", "grand-parent", "arriere-grand-parent")


def _choisir_administration(
    type_acte: TypeActe,
    annee_acte: int,
    commune: str | None,
    pays_naissance: str | None = None,
) -> tuple[Administration, list[str], str]:
    """
    Retourne (Administration, justificatifs, délai_réponse).
    """
    acces_libre = _est_acces_libre(type_acte, annee_acte)

    # --- Actes consulaires (nés à l'étranger) ---
    if pays_naissance and pays_naissance.lower() not in ("france", "fr", ""):
        admin = Administration(
            nom="Service central d'état civil (SCEC) — Nantes",
            adresse="11 rue de la Maison Blanche, 44941 Nantes Cedex 09",
            url="https://www.service-public.fr/particuliers/vosdroits/R1407",
            email="scec.nantes@diplomatie.gouv.fr",
            notes=(
                "Compétent pour tous les Français nés, mariés ou décédés hors de France. "
                "Demande possible en ligne via le service Comedec ou par courrier."
            ),
        )
        justificatifs = [
            "Formulaire de demande d'acte d'état civil (cerfa n°11753*04)",
            "Justificatif d'identité (carte nationale d'identité ou passeport)",
            "Justificatif du lien de parenté si acte non encore librement communicable",
        ]
        return admin, justificatifs, "3 à 6 semaines"

    # --- Matricule militaire ---
    if type_acte == "matricule":
        if annee_acte <= 1921:
            admin = Administration(
                nom="Archives départementales du lieu de recensement",
                url="https://www.memoiredeshommes.sga.defense.gouv.fr",
                notes=(
                    "Matricules militaires (classes 1867–1921) numérisés et consultables "
                    "gratuitement sur le portail Mémoire des Hommes et sur les sites des "
                    "archives départementales. Aucune démarche courrier nécessaire."
                ),
            )
            justificatifs = ["Aucun — consultation en ligne gratuite sur Mémoire des Hommes"]
            return admin, justificatifs, "Immédiat (en ligne)"
        else:
            admin = Administration(
                nom="Service Historique de la Défense (SHD)",
                adresse="Château de Vincennes, Avenue de Paris, 94306 Vincennes Cedex",
                url="https://www.servicehistorique.sga.defense.gouv.fr",
                notes=(
                    "Pour les dossiers militaires postérieurs à 1921. "
                    "Délai variable selon l'état du fonds et la période."
                ),
            )
            justificatifs = [
                "Formulaire de demande de communication de dossier individuel",
                "Justificatif d'identité",
                "Justificatif du lien de parenté (actes d'état civil)",
            ]
            return admin, justificatifs, "4 à 12 semaines"

    # --- Actes civils (naissance, mariage, décès) ---
    delai_legal = "75 ans" if type_acte != "deces" else "25 ans"
    if acces_libre:
        # Délai écoulé → mairie ou archives départementales
        admin = Administration(
            nom=f"Mairie de {commune}" if commune else "Mairie du lieu de l'acte",
            notes=(
                f"L'acte de {type_acte} de {annee_acte} est librement communicable "
                f"(délai de {delai_legal} écoulé). "
                "Si la mairie ne détient plus le registre original, les archives "
                "départementales conservent un double."
            ),
        )
        justificatifs = ["Justificatif d'identité (facultatif mais recommandé pour accélérer le traitement)"]
        return admin, justificatifs, "1 à 3 semaines"
    else:
        # Délai non écoulé → mairie uniquement, ayants droit
        admin = Administration(
            nom=f"Mairie de {commune}" if commune else "Mairie du lieu de l'acte",
            notes=(
                f"L'acte de {type_acte} de {annee_acte} n'est pas encore librement communicable "
                f"(délai de {delai_legal} non écoulé). "
                "La demande est réservée aux ayants droit : "
                "ascendants et descendants directs, conjoint, représentant légal."
            ),
        )
        justificatifs = [
            "Justificatif d'identité (original ou copie certifiée conforme)",
            "Justificatif du lien de parenté (acte de naissance, livret de famille...)",
            "Préciser explicitement la qualité d'ayant droit dans la demande",
        ]
        return admin, justificatifs, "2 à 4 semaines"


# ---------------------------------------------------------------------------
# Génération du courrier via Gemini
# ---------------------------------------------------------------------------

async def _generate_courrier(
    type_acte: TypeActe,
    annee_acte: int,
    nom_ancetre: str,
    prenom_ancetre: str | None,
    commune: str | None,
    lien: LienFamille,
    administration: Administration,
    justificatifs: list[str],
) -> str:
    context = f"""
Tu rédiges un courrier administratif français pour une demande de document généalogique.

Expéditeur : [PRÉNOM NOM DU DEMANDEUR], né(e) le [DATE DE NAISSANCE], demeurant [ADRESSE COMPLÈTE], [CODE POSTAL] [VILLE].
Destinataire : {administration.nom}{', ' + administration.adresse if administration.adresse else ''}.

Document recherché :
- Type d'acte : {type_acte}
- Personne concernée : {prenom_ancetre or ''} {nom_ancetre}
- Année approximative : {annee_acte}
- Commune : {commune or 'inconnue'}
- Lien de parenté du demandeur : {lien}

Pièces jointes mentionnées dans le courrier : {', '.join(justificatifs)}.

Le courrier doit :
1. Respecter la forme épistolaire administrative française (lieu et date, objet, formule d'appel, corps, formule de politesse)
2. Indiquer clairement la qualité d'ayant droit si pertinent
3. Demander une copie intégrale de l'acte
4. Utiliser [CROCHETS] pour toutes les parties à compléter par le demandeur
5. Être concis (1 page maximum)
"""
    return await answer_admin_question(
        context=context,
        question=f"Rédige le courrier de demande de copie intégrale de l'acte de {type_acte} de {prenom_ancetre or ''} {nom_ancetre} ({annee_acte}).",
    )


# ---------------------------------------------------------------------------
# Point d'entrée public
# ---------------------------------------------------------------------------

async def handle_post_1900(
    type_acte: TypeActe,
    nom: str,
    prenom: str | None,
    commune: str | None,
    annee: int,
    lien: LienFamille,
    pays_naissance: str | None = None,
) -> AdminResult:
    """
    Détermine l'administration compétente et génère le courrier de demande.

    Paramètres :
        type_acte      : "naissance" | "mariage" | "deces" | "matricule"
        nom            : nom de l'ancêtre recherché
        prenom         : prénom de l'ancêtre (optionnel)
        commune        : commune de l'événement (optionnel)
        annee          : année approximative de l'acte (ex: 1923)
        lien           : lien de parenté du demandeur avec l'ancêtre
        pays_naissance : si né hors de France, préciser le pays
    """
    acces_libre = _est_acces_libre(type_acte, annee)
    accessible = acces_libre or _est_ayant_droit(lien)

    administration, justificatifs, delai = _choisir_administration(
        type_acte, annee, commune, pays_naissance
    )

    courrier = await _generate_courrier(
        type_acte=type_acte,
        annee_acte=annee,
        nom_ancetre=nom,
        prenom_ancetre=prenom,
        commune=commune,
        lien=lien,
        administration=administration,
        justificatifs=justificatifs,
    )

    return AdminResult(
        accessible=accessible,
        acces_libre=acces_libre,
        administration=administration,
        justificatifs=justificatifs,
        delai_reponse=delai,
        courrier=courrier,
    )
