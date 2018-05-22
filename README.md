# Generate MTB report

Module contenant les outils pour générer des reports MTB et pre-MTB.

## Generate pre-MTB | Blueprint "get_report"

Cette blueprint sert à générer sont forme de pdf via un template Latex un rapport pre-MTB
à partir d'un patient_id (complet) donné.

Le patient_id est transmit dans l'url via GET à la blueprint.


### Installation

- Télécharger le module redcap_utils versionné dans https://bitbucket.org/bergomultipli/redcap_utils.

- pip3 install -r requirements.txt

- sudo apt install texlive-latex-extra

- Lancer la commande `python3 master.py` (application remplaçant GVX)

- Aller sur l'url http://ib101a:5000.  Si "Hello, master!" est affiché l'application flask est correctement lancée, la blueprint peut être utilisée comme dans la partie Usage.


### Configurations

- Dans le fichier config.yml changer la valeur de "path_to_utils" pour pointer vers le module redcap_utils.  `report.py` utilise la fonction `get_clinical_data` de redcap_utils.

- Créer le fichier secret_config.yml au même niveau que report.py et ajouter la ligne : `redcap_key: <api_key>`.  Avec `<api_key>` étant la clé api de l'instance de redcap d'où les données cliniques seront extraites.

- Dans config.yml db_dir pointe vers le dossier contenant la base de données SQLite.

### Usage

- Aller sur l'url: `<nom du site web>/get_report/?patient_id=T02-0002-DX-001O`

___

## report.py

Script générant le rapport pre-MTB. Remplit le template Latex avec les données de la base SQLite liées à un patient_id.

___

## Generate and transfer MTB | MTB_to_CRF.py

Transmet sous forme de fichier texte des informations d'un rapport MTB au CRF. 

### Installation

- Récupération des sources de [generate_mtb_reports](https://bitbucket.org/bergomultipli/generate_mtb_reports/src/default/):

 `hg clone ssh://hg@bitbucket.org/bergomultipli/generate_mtb_reports`

- Installation des dépendances:

    - pip3 install -r requirements.txt

    - Récupération des sources de [cron_to_redcap](https://bitbucket.org/bergomultipli/cron_to_redcap/src/default/):

    `hg clone ssh://hg@bitbucket.org/bergomultipli/cron_to_redcap`

    - Récupération des sources de [eCRF](https://bitbucket.org/bergomultipli/ecrf/src/default/):

    `hg clone ssh://hg@bitbucket.org/bergomultipli/ecrf`


- Créer le fichier secret_config.yml et compléter les champs redcap_key, login_crf et password_crf.

### Configurations

La configuration du script MTB_to_CRF.py se fait dans les fichiers secret_config.yml et config.yml.

- Dépendance:

path_to_utils: chemin vers les dépendances [cron_to_redcap](https://bitbucket.org/bergomultipli/cron_to_redcap/src/default/) et [eCRF](https://bitbucket.org/bergomultipli/ecrf/src/default/):
 
- Bases de données GVX:

db_dir: dossier contenant les fichiers de la base de données
protocol: exemple, MULTIPLI
catalog: nom du fichier de base de données catalog de GVX

- Champs relatifs au server FTP du eCRF:
 
crf_host: Adresse du server FTP
login_crf
password_crf

- Champs relatifs l'API redcap:

redcap_api_url: Adresse de l'instance RedCap
redcap_key: token de l'API

- Logging:

path_to_log: Chemin vers le fichier de log

### Usage

python3 MTB_to_CRF.py [-c path_to_config] [-s path_to_secret_config]