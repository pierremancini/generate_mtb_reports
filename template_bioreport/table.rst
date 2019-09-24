###############################################
RAPPORT BIOLOGIQUE MULTIPLI (MULTISARC/ACOMPLI)
###############################################

Code patient : {{code_patient}}

Sex patient : {{sex_patient}}

Date d’édition du rapport : {{report_date}}

Mode de fixation : {{fixation}}

Organe : {{organe}}

Type histologique : {{hist_type}}

Cellularité tumorale : {{cellularity}}%



ETUDE SOMATIQUE
===============

ADN TUMORAL : PANEL DE 616 GENES RAPPORTES PAR LE CANCER GENE CENSUS

ARN TUMORAL: ETUDE DU  TRANSCRIPTOME


ETUDE DE LA CHARGE MUTATIONNELLE
--------------------------------

{{charge_mut}} Mutations / Mb codantes

ETUDE DES VARIATIONS PONCTUELLES ET INSERTIONS-DELETIONS
--------------------------------------------------------

VARIATIONS PATHOGENES
.....................

.. raw:: pdf

   PageBreak


.. csv-table:: VARIATIONS PATHOGENES
   :header: Gene,"HGVSg","HGVSc","HGVSp",NM,LOH,"Freq",Actionability
   :widths: 10, 16, 14, 14, 12, 14, 6, 14

   {{var_pathogenes}}


VARIATIONS PROBABLEMENT PATHOGENES
..................................

.. csv-table:: VARIATIONS PROBABLEMENT PATHOGENES
   :header: Gene, HGVSg, HGVSc, HGVSp, NM,LOH, Freq ,Actionability
   :widths: 10, 16, 14, 14, 12, 14, 8, 14
  {% for var in var_probablement_pathogenes %}{{var|join(', ')}}{% endfor %}


VARIATIONS DE SIGNIFICATION CLINIQUE INDETERMINEE
.................................................


ETUDE DES COPY NUMBER VARIANT : AMPLIFICATIONS ET DELETIONS
-----------------------------------------------------------

ETUDE DES TRANSCRITS DE FUSION :

.. csv-table:: FUSION
    :header:  Fusion, 5'\, NM, 5'\, Exon impliqué, 3'\, NM, 3'\, Exon impliqué, Pathogénicté, Actionnabilité

    testfusion, NM446123, impl65516, NM3', implEZFzfe, oui, non


II/ ETUDE CONSTITUTIONNELLE : 59 GENES DE PREDISPOSITION HEREDITAIRES RECOMMANDES PAR L’ACMG


ETUDE DES VARIATIONS PONCTUELLES ET INSERTIONS-DELETIONS :



ETUDE DES COPY NUMBER VARIANT : AMPLIFICATIONS ET DELETIONS


**Liste des gènes étudiés**
  ACTA2, ACTC1, APC, APOB, ATP7B, BMPR1A, BRCA1, BRCA2, CACNA1S, COL3A1, DSC2, DSG2, DSP, FBN1, GLA., KCNH2, KCNQ1, LDLR, LMNA, MEN1, MLH1, MSH2, MSH6, MUTYH, MYBPC3, MYH11, MYH7, MYL2, MYL3, NF2, OTC, PCSK9, PKP2, PMS2, PRKAG2, PTEN, RB1, RET, RYR1, RYR2, SCN5A, SDHAF2, SDHB, SDHC, SDHD, SMAD3, SMAD4, STK11, TGFBR1, TGFBR2, TMEM43, TNNI3, TNNT2, TP53, TPM1, TSC1, TSC2, VHL, WT1.




ETUDE CONSTITUTIONNELLE : ETUDES DES POLYMORPHISMES LIES A UNE TOXICITE (Niveau d’évidence 1A et 1B d’après PharmacoGKB)


CONCLUSION
==========


Quoi mettre en conclusion vu que c’est un rapport valable quelque soit le contexte (MULTIPLI ou hors MULTIPLI).

*Interprétation du statut germinal de prédisposition aux maladies héréditaires

Conclusion quantitative ?
Nombre de variants actionnables ?
Charge mutationnelle ?
Statut MSI ?



METHODS
=======

**Genome build**
  {{hg19}}

**Liste des gènes étudiés en somatique (618)**
  ACTA2, ACTC1, APC, APOB, ATP7B, BMPR1A, BRCA1, BRCA2, CACNA1S, COL3A1, DSC2, DSG2, DSP, FBN1, GLA., KCNH2, KCNQ1, LDLR, LMNA, MEN1, MLH1, MSH2, MSH6, MUTYH, MYBPC3, MYH11, MYH7, MYL2, MYL3, NF2, OTC, PCSK9, PKP2, PMS2, PRKAG2, PTEN, RB1, RET, RYR1, RYR2, SCN5A, SDHAF2, SDHB, SDHC, SDHD, SMAD3, SMAD4, STK11, TGFBR1, TGFBR2, TMEM43, TNNI3, TNNT2, TP53, TPM1, TSC1, TSC2, VHL, WT1.

**Liste des gènes étudiés en constit**
  ACTA2, ACTC1, APC, APOB, ATP7B, BMPR1A, BRCA1, BRCA2, CACNA1S, COL3A1, DSC2, DSG2, DSP, FBN1, GLA., KCNH2, KCNQ1, LDLR, LMNA, MEN1, MLH1, MSH2, MSH6, MUTYH, MYBPC3, MYH11, MYH7, MYL2, MYL3, NF2, OTC, PCSK9, PKP2, PMS2, PRKAG2, PTEN, RB1, RET, RYR1, RYR2, SCN5A, SDHAF2, SDHB, SDHC, SDHD, SMAD3, SMAD4, STK11, TGFBR1, TGFBR2, TMEM43, TNNI3, TNNT2, TP53, TPM1, TSC1, TSC2, VHL, WT1.

**Liste des NM de reference**
  WT1: NM_35435453.3, TP53: NM_35454.4
