# Generate MTB report

Module contenant les outils pour générer des reports MTB et pre-MTB.

## Blueprint "get_report"

Cette blueprint sert à générer sont forme de pdf via un template Latex un rapport pre-MTB
à partir d'un patient_id (complet) donné.

Le patient_id est transmit dans l'url via GET à la blueprint.

- Exemple d'utilisation de la blueprint "get_report":  

<nom du site web>/get_report/?patient_id=T02-0002-DX-001O


## report.py

Script générant le rapport pre-MTB. Remplit le template Latex avec les données de la base SQLite
liées à un patient_id.


## MTB_to_CRF

Transmet sous forme de fichier texte des informations d'un rapport MTB au CRF. Ce script utilise
un partie de report.py.
