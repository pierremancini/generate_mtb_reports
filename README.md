# Generate MTB report

Module contenant les outils pour générer des reports MTB et pre-MTB.

## Blueprint "get_report"

Cette blueprint sert à générer sont forme de pdf via un template Latex un rapport pre-MTB
à partir d'un patient_id (complet) donné.

Le patient_id est transmit dans l'url via GET à la blueprint.

### Exemple d'utilisation de la blueprint "get_report":  

`<nom du site web>/get_report/?patient_id=T02-0002-DX-001O`

### Mise en production (indépendante de GVX):  

- Télécharger le module redcap_utils versionné dans https://bitbucket.org/bergomultipli/redcap_utils.

- Dans le fichier config.yml changer la valeur de "path_to_utils" pour pointer vers le module redcap_utils.  `report.py` utilise la fonction `get_clinical_data` de redcap_utils.

- Créer le fichier secret_config.yml au même niveau que report.py et ajouter la ligne : `redcap_key: <api_key>`.  Avec `<api_key>` étant la clé api de l'instance de redcap d'où les données cliniques seront extraites.

- Installer les paquets python: pip3 install -r requirements.txt

- Installer latex: sudo apt install texlive-latex-extra

- Dans config.yml db_dir pointe vers le dossier contenant la base de données SQLite.

- Lancer la commande `python3 master.py` (application remplaçant GVX)

- Aller sur l'url https://ib101a:5000.  Si "Hello, master!" est affiché l'application flask est correctement lancée, la blueprint peut être utilisée comme dans l'exemple.


## report.py

Script générant le rapport pre-MTB. Remplit le template Latex avec les données de la base SQLite
liées à un patient_id.


## MTB_to_CRF.py

Transmet sous forme de fichier texte des informations d'un rapport MTB au CRF. 


### Dépendances:

- Une partie de report.py.
- Module update_redcap_record.py . cf. dépot bitbucket cron_to_redcap
- Utilitaire ftp.py . cf. dépot bitbucket eCRF