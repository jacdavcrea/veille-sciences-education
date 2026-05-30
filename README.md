# Veille en sciences de l'éducation et de la formation

Dispositif de publication automatisée d'une veille hebdomadaire, dans le cadre d'un travail de Master 2 en ingénierie pédagogique et numérique.

Cette version (v2) intègre explicitement le cadre conceptuel du cours : structuration par les six **types de veille** de la typologie de référence, rubriques réflexives **Concepts du glossaire mobilisés** et **Pistes pour poursuivre**, pages **Méthode** et **À propos** documentant la démarche, et **hooks collaboratifs** via les issues GitHub.

## Principe

```
  Cowork (lundi 8h)  →  veille-courante.md  →  GitHub Action  →  site HTML publié
       (agent IA)       (markdown structuré)     (conversion)      (GitHub Pages)
```

Chaque lundi matin :
1. Cowork produit `content/veille-courante.md` selon la structure attendue,
2. Une GitHub Action convertit, applique la typologie, et publie,
3. Le site est disponible à `https://<pseudo>.github.io/<dépôt>/`.

Le dimanche soir, un second workflow archive automatiquement la veille de la semaine écoulée.

## Structure du dépôt

```
.
├── content/
│   ├── veille-courante.md          ← écrit chaque lundi par Cowork
│   ├── methode.md                  ← page Méthode (statique, éditable)
│   ├── apropos.md                  ← page À propos (statique, éditable)
│   └── archives/                   ← veilles archivées
├── templates/
│   ├── index.html                  ← page d'accueil
│   ├── archive.html                ← page d'archive
│   ├── archives-index.html         ← liste des archives
│   └── page.html                   ← Méthode et À propos
├── static/style.css                ← design éditorial
├── scripts/build.py                ← générateur (typologie, glossaire, RSS)
└── .github/
    ├── workflows/
    │   ├── publish.yml             ← publication hebdomadaire
    │   └── archive.yml             ← archivage hebdomadaire
    └── ISSUE_TEMPLATE/
        └── proposer-une-ressource.yml   ← contribution collaborative
```

## Format markdown attendu

Le fichier `content/veille-courante.md` doit suivre la structure suivante :

```markdown
---
date: 2026-05-25
semaine: 22
titre: Veille du 25 mai 2026
---

Phrase d'introduction éditoriale (facultative, devient l'édito).

## Veille institutionnelle
- [Titre cliquable](https://url) — description

## Veille scientifique et technologique
- ...

## Veille réglementaire, normative, juridique
## Veille image, e-réputation
## Veille commerciale, financière, marketing
## Veille sectorielle, stratégique, environnementale

## Concepts du glossaire mobilisés
- **Concept** — comment il apparaît dans l'actualité

## Pistes pour poursuivre
- Activité, question, sondage, lecture
```

Les types absents une semaine donnée ne sont simplement pas rendus. Le générateur reconnaît les titres de section par correspondance souple (insensible à la casse, aux accents, à la ponctuation) — votre prompt Cowork peut varier les formulations.

## Reconnaissance typologique

Le script `build.py` mappe chaque section H2 vers l'un des six types de la typologie du cours, et produit :

- un **dashboard** de répartition en tête de chaque numéro (« 3 institutionnel · 2 scientifique · 1 réglementaire… »),
- une **mise en forme spécifique** par type (marqueur coloré),
- un **comptage** dans la liste des archives.

Les sections « Concepts du glossaire » et « Pistes pour poursuivre » reçoivent un traitement visuel distinct (encart sur fond crème) qui les identifie comme **rubriques réflexives** plutôt que comme contenu de veille pur.

## Mise en place

1. Créer un dépôt GitHub, y pousser ce contenu.
2. Settings → Pages → Source : *GitHub Actions*.
3. Configurer Cowork pour qu'il écrive vers `content/veille-courante.md` (intégration GitHub native, ou push depuis un Drive surveillé).
4. La première publication se déclenche au prochain push.

## Tester localement

```bash
pip install markdown pyyaml
python scripts/build.py
python -m http.server -d dist 8000
```

Ouvrir http://localhost:8000.

## Personnalisation

- **Sources et critères** : éditer `content/methode.md` (ce contenu apparaît sur la page Méthode publique).
- **Positionnement** : éditer `content/apropos.md`.
- **Palette et typo** : `static/style.css`, variables en début de fichier.
- **Titre du site** : `scripts/build.py`, constantes `SITE_TITLE` / `SITE_SUBTITLE`.
- **Cadence** : `.github/workflows/publish.yml`, expression cron.
- **Typologie** : `scripts/build.py`, liste `TYPOLOGIE` (slug, label, couleur, mots-clés).

## Dimension collaborative

Le lien « Contribuer » dans la navigation ouvre un formulaire d'*issue* GitHub structuré pour proposer une ressource. Les contributions sont publiques, traçables, et peuvent être intégrées à la veille de la semaine suivante.

## Licence

Code : MIT. Contenus : CC BY 4.0.
