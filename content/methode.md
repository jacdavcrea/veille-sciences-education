---
titre: Méthode
kicker: Note méthodologique
---

Cette page documente la méthode mise en œuvre pour produire la veille hebdomadaire publiée sur ce site. Elle vise une transparence méthodologique conforme aux exigences académiques en sciences de l'éducation et de la formation, et rend le dispositif transférable à d'autres contextes disciplinaires.

## Cadre conceptuel

La veille est entendue ici dans son acception large, telle que présentée dans le cours de M2 : une **activité itérative** de surveillance d'un environnement informationnel structuré, finalisée par une intention (anticiper, surveiller son environnement, suivre des thématiques, surveiller sa réputation, ne pas s'endormir, respecter la réglementation), et qui concerne **tous les métiers de l'éducation**.

Le présent dispositif s'inscrit principalement dans une veille **scientifique et institutionnelle**, avec une attention secondaire aux dimensions sectorielle et réglementaire. La typologie utilisée pour structurer chaque numéro reprend explicitement les six types présentés en cours :

- veille institutionnelle,
- veille scientifique et technologique,
- veille réglementaire, normative, juridique,
- veille image, e-réputation,
- veille commerciale, financière, marketing,
- veille sectorielle, stratégique, environnementale.

Cette structuration n'est pas un classement *a posteriori* : elle oriente la collecte elle-même. Chaque semaine, l'agent de veille est sollicité pour explorer ces six axes, ce qui assure une certaine systématicité et limite les angles morts.

## Sources surveillées

La veille mobilise quatre catégories de sources, en cohérence avec une exigence de sourcing pluriel :

**Sources institutionnelles.** Sites du ministère de l'Éducation nationale, du ministère de l'Enseignement supérieur, des académies, de France Compétences, du CNED, de la DEPP, du Conseil d'État, du Conseil supérieur des programmes.

**Sources scientifiques.** Revues francophones à comité de lecture (*Revue française de pédagogie*, *Distances et Médiations des Savoirs*, *Recherche et formation*, *Éducation et didactique*, *Spirale*) ; revues internationales (*Computers & Education*, *British Journal of Educational Technology*, *Review of Educational Research*) ; archives ouvertes HAL-SHS ; thèses sur theses.fr ; carnets Hypothèses pertinents.

**Sources réglementaires.** Journal officiel, Légifrance, circulaires du Bulletin officiel de l'Éducation nationale, référentiels Qualiopi et France Compétences.

**Sources médiatiques et sectorielles.** *Le Monde Éducation*, *Café pédagogique*, *AEF*, *The Conversation France*, presse spécialisée (*EducPros*, *News Tank Education*), rapports d'organismes (OCDE, Conseil de l'Europe, IFÉ, IGÉSR).

## Critères de sélection

Les ressources retenues chaque semaine répondent à au moins l'un de ces critères :

1. **Pertinence disciplinaire** — appartenance au champ des sciences de l'éducation et de la formation ou intersection démontrée.
2. **Actualité** — publication ou diffusion récente (moins de quinze jours sauf reprise justifiée).
3. **Robustesse de la source** — institution reconnue, revue à comité de lecture, auteur identifié et compétent dans le champ.
4. **Intérêt pour la communauté du M2 IPN** — apport pour la compréhension de l'ingénierie pédagogique et numérique, en lien avec les contenus du parcours.

Les sources contributoires ou non identifiées (forums, blogs personnels sans légitimité scientifique, réseaux sociaux) ne sont pas exclues *a priori* mais ne sont mobilisées que pour la veille e-réputation, en explicitant leur statut.

## Outillage

Le dispositif s'appuie sur une chaîne logicielle entièrement automatisée :

1. **Cowork** (agent IA personnalisé) interroge chaque lundi matin les sources identifiées, applique les critères de sélection et produit un rapport au format markdown.
2. Le rapport est déposé dans un dépôt **GitHub** versionné, ce qui constitue une trace auditable de l'évolution de la veille.
3. Une **GitHub Action** détecte le dépôt du nouveau fichier, convertit le markdown en HTML stylisé selon les templates de ce site, et publie la mise à jour.
4. **GitHub Pages** héberge le site à une URL stable et gratuite.
5. Un second workflow archive automatiquement la veille de la semaine écoulée le dimanche soir, avant l'arrivée de la nouvelle.

Le code source du dispositif est ouvert et réutilisable.

## Positionnement réflexif

Trois limites méthodologiques sont à expliciter :

**La médiation par l'IA.** L'usage d'un agent comme Cowork pour la collecte introduit une médiation qui n'est pas neutre : choix des sources accessibles, biais d'entraînement, profondeur de lecture variable. Un contrôle humain hebdomadaire reste indispensable pour valider la sélection et la justesse des résumés. Cette veille n'est pas substituable à une lecture approfondie des sources primaires.

**L'exhaustivité illusoire.** Comme le rappelle le support de cours, une veille ne vise pas l'exhaustivité mais une couverture représentative. Les choix opérés sont assumés ; ce que la veille ne capte pas (presse régionale, littérature grise non indexée, échanges informels en colloque) reste hors champ.

**La temporalité de l'actualité.** La cadence hebdomadaire impose un découpage artificiel. Certains phénomènes (controverses, débats) se déploient sur plusieurs semaines et ne se laissent pas saisir en un seul numéro. Les pages d'archive permettent de reconstituer ces continuités.

## Transférabilité

L'ensemble du dispositif est conçu pour être réapproprié. Le dépôt GitHub peut être *forké* en quelques minutes, les critères de sélection et les sources adaptés à un autre champ disciplinaire, le titre et la palette modifiés en deux fichiers. La méthode décrite ici peut servir de canevas pour toute veille thématique récurrente.
