#!/usr/bin/env python3
"""
Script de creation des donnees pour les Archives departementales des Bouches-du-Rhone (AD13)
Basé sur l'exploration du site https://www.archives13.fr/

Auteur: Barbara Proenca
Note: Les metrages sont estimatifs et doivent etre ajustes avec les donnees reelles.
"""

import pandas as pd
from pathlib import Path

# Donnees des Fonctions (grandes categories de fonds)
fonctions_data = [
    {
        "fonction": "ARCHIVES ANCIENNES",
        "Description": "Les archives anciennes sont les archives des institutions d'Ancien Regime supprimees par la Revolution francaise. Elles couvrent une periode de pres de 1000 ans - le document le plus ancien datant de 814 - et forment les series A a H du cadre de classement. L'on distingue deux grands ensembles : les archives administratives de l'ancienne Provence (series A a E) et les archives religieuses (series G et H).",
        "date_extreme_min": 814,
        "date_extreme_max": 1789,
        "date_extreme_fonction": "814/1789",
        "Métrage réel": 2500.0,
        "Nombre d'entrée": 45,
        "Thematique": "Fonds anciens"
    },
    {
        "fonction": "ARCHIVES REVOLUTIONNAIRES",
        "Description": "Les archives revolutionnaires concernent la periode de 1789 a 1800, epoque de profonds bouleversements politiques et administratifs. Elles documentent la transformation des institutions et la naissance de l'administration moderne.",
        "date_extreme_min": 1789,
        "date_extreme_max": 1800,
        "date_extreme_fonction": "1789/1800",
        "Métrage réel": 800.0,
        "Nombre d'entrée": 25,
        "Thematique": "Fonds revolutionnaires"
    },
    {
        "fonction": "ARCHIVES MODERNES ET CONTEMPORAINES",
        "Description": "Les archives modernes et contemporaines sont les fonds produits par les administrations publiques du departement de 1800 a nos jours : les services de l'Etat et ceux du Conseil general puis departemental. Cette periode commence par le coup d'Etat de Napoleon Bonaparte du 18 brumaire an VIII.",
        "date_extreme_min": 1800,
        "date_extreme_max": 2024,
        "date_extreme_fonction": "1800/2024",
        "Métrage réel": 35000.0,
        "Nombre d'entrée": 1500,
        "Thematique": "Fonds publics modernes"
    },
    {
        "fonction": "ARCHIVES HOSPITALIERES",
        "Description": "Les archives hospitalieres regroupent les fonds des etablissements hospitaliers du departement, temoignant de l'histoire de la sante publique et de l'assistance dans les Bouches-du-Rhone.",
        "date_extreme_min": 1500,
        "date_extreme_max": 2020,
        "date_extreme_fonction": "1500/2020",
        "Métrage réel": 3000.0,
        "Nombre d'entrée": 120,
        "Thematique": "Sante et assistance"
    },
    {
        "fonction": "ARCHIVES COMMUNALES ET INTERCOMMUNALES DEPOSEES",
        "Description": "Les archives communales et intercommunales deposees proviennent des communes du departement qui ont confie leurs archives anciennes aux Archives departementales pour assurer leur conservation et leur mise en valeur.",
        "date_extreme_min": 1200,
        "date_extreme_max": 1940,
        "date_extreme_fonction": "1200/1940",
        "Métrage réel": 5000.0,
        "Nombre d'entrée": 200,
        "Thematique": "Fonds communaux"
    },
    {
        "fonction": "ARCHIVES PRIVEES",
        "Description": "Les archives privees rassemblent les fonds d'origine privee entres par don, legs, depot ou achat. Elles proviennent de familles, d'entreprises, d'associations ou de personnalites, enrichissant ainsi la memoire collective du territoire.",
        "date_extreme_min": 1100,
        "date_extreme_max": 2023,
        "date_extreme_fonction": "1100/2023",
        "Métrage réel": 4000.0,
        "Nombre d'entrée": 350,
        "Thematique": "Fonds prives"
    },
    {
        "fonction": "FONDS ICONOGRAPHIQUES ET AUDIOVISUELS",
        "Description": "Les fonds iconographiques et audiovisuels comprennent les photographies, cartes postales, affiches, plans, films et enregistrements sonores qui documentent visuellement et auditivement l'histoire du departement.",
        "date_extreme_min": 1850,
        "date_extreme_max": 2024,
        "date_extreme_fonction": "1850/2024",
        "Métrage réel": 2000.0,
        "Nombre d'entrée": 180,
        "Thematique": "Images et sons"
    },
    {
        "fonction": "BIBLIOTHEQUE",
        "Description": "La bibliotheque des Archives departementales conserve des ouvrages de reference, des periodiques et des publications utiles a la recherche historique sur la Provence et les Bouches-du-Rhone.",
        "date_extreme_min": 1600,
        "date_extreme_max": 2024,
        "date_extreme_fonction": "1600/2024",
        "Métrage réel": 1500.0,
        "Nombre d'entrée": 90,
        "Thematique": "Documentation"
    },
    {
        "fonction": "ETAT CIVIL",
        "Description": "L'etat civil comprend les registres paroissiaux et d'etat civil des communes du departement, source fondamentale pour la genealogie et l'etude demographique du territoire.",
        "date_extreme_min": 1530,
        "date_extreme_max": 2023,
        "date_extreme_fonction": "1530/2023",
        "Métrage réel": 6000.0,
        "Nombre d'entrée": 400,
        "Thematique": "Genealogie"
    },
    {
        "fonction": "ARCHIVES NOTARIALES",
        "Description": "Les archives notariales regroupent les minutes et repertoires des notaires du departement, constituant une source essentielle pour l'histoire economique, sociale et familiale de la region.",
        "date_extreme_min": 1300,
        "date_extreme_max": 1950,
        "date_extreme_fonction": "1300/1950",
        "Métrage réel": 8000.0,
        "Nombre d'entrée": 500,
        "Thematique": "Actes notaries"
    }
]

# Donnees des Thematiques (sous-categories)
thematiques_data = [
    # Archives anciennes - Series
    {
        "thematique": "Serie A - Actes du pouvoir souverain et domaine public",
        "Description": "Actes des rois de France, edits, ordonnances et administration du domaine royal en Provence.",
        "date_extreme_min": 814,
        "date_extreme_max": 1789,
        "date_extreme_thematique": "814/1789",
        "Métrage réel": 150.0,
        "Nombre d'entrée": 5,
        "Fonction": "ARCHIVES ANCIENNES"
    },
    {
        "thematique": "Serie B - Cours et juridictions",
        "Description": "Cour des Comptes, parlement de Provence, senechaussees, amirautes et tribunaux de commerce.",
        "date_extreme_min": 1200,
        "date_extreme_max": 1789,
        "date_extreme_thematique": "1200/1789",
        "Métrage réel": 800.0,
        "Nombre d'entrée": 12,
        "Fonction": "ARCHIVES ANCIENNES"
    },
    {
        "thematique": "Serie C - Administrations provinciales",
        "Description": "Etats de Provence, intendance de Provence, assemblees provinciales.",
        "date_extreme_min": 1400,
        "date_extreme_max": 1789,
        "date_extreme_thematique": "1400/1789",
        "Métrage réel": 600.0,
        "Nombre d'entrée": 10,
        "Fonction": "ARCHIVES ANCIENNES"
    },
    {
        "thematique": "Serie D - Instruction publique, sciences et arts",
        "Description": "Universites, colleges, academies et institutions d'enseignement sous l'Ancien Regime.",
        "date_extreme_min": 1500,
        "date_extreme_max": 1789,
        "date_extreme_thematique": "1500/1789",
        "Métrage réel": 100.0,
        "Nombre d'entrée": 3,
        "Fonction": "ARCHIVES ANCIENNES"
    },
    {
        "thematique": "Serie E - Intendance des galeres, intendance sanitaire, communautes de metiers",
        "Description": "Intendance des galeres de Marseille, intendance sanitaire, corporations et communautes de metiers.",
        "date_extreme_min": 1600,
        "date_extreme_max": 1789,
        "date_extreme_thematique": "1600/1789",
        "Métrage réel": 400.0,
        "Nombre d'entrée": 8,
        "Fonction": "ARCHIVES ANCIENNES"
    },
    {
        "thematique": "Serie G - Clerge seculier",
        "Description": "Dioceses, chapitres cathedraux, seminaires et paroisses de Provence.",
        "date_extreme_min": 900,
        "date_extreme_max": 1789,
        "date_extreme_thematique": "900/1789",
        "Métrage réel": 250.0,
        "Nombre d'entrée": 5,
        "Fonction": "ARCHIVES ANCIENNES"
    },
    {
        "thematique": "Serie H - Clerge regulier",
        "Description": "Abbayes, prieures et ordres religieux masculins et feminins de Provence.",
        "date_extreme_min": 1000,
        "date_extreme_max": 1789,
        "date_extreme_thematique": "1000/1789",
        "Métrage réel": 200.0,
        "Nombre d'entrée": 2,
        "Fonction": "ARCHIVES ANCIENNES"
    },
    # Archives modernes - Thematiques
    {
        "thematique": "Administration generale",
        "Description": "Prefecture, sous-prefectures, conseil general puis departemental, services administratifs.",
        "date_extreme_min": 1800,
        "date_extreme_max": 2024,
        "date_extreme_thematique": "1800/2024",
        "Métrage réel": 8000.0,
        "Nombre d'entrée": 400,
        "Fonction": "ARCHIVES MODERNES ET CONTEMPORAINES"
    },
    {
        "thematique": "Economie, industrie, agriculture et forets",
        "Description": "Chambres de commerce, agriculture, industrie, statistiques economiques, eaux et forets.",
        "date_extreme_min": 1800,
        "date_extreme_max": 2020,
        "date_extreme_thematique": "1800/2020",
        "Métrage réel": 4000.0,
        "Nombre d'entrée": 200,
        "Fonction": "ARCHIVES MODERNES ET CONTEMPORAINES"
    },
    {
        "thematique": "Opinion et presse",
        "Description": "Surveillance de l'opinion, presse, associations, syndicats, partis politiques.",
        "date_extreme_min": 1800,
        "date_extreme_max": 2000,
        "date_extreme_thematique": "1800/2000",
        "Métrage réel": 1500.0,
        "Nombre d'entrée": 80,
        "Fonction": "ARCHIVES MODERNES ET CONTEMPORAINES"
    },
    {
        "thematique": "Affaires militaires",
        "Description": "Conscription, recrutement, anciens combattants, guerres mondiales, defense nationale.",
        "date_extreme_min": 1800,
        "date_extreme_max": 1960,
        "date_extreme_thematique": "1800/1960",
        "Métrage réel": 3000.0,
        "Nombre d'entrée": 150,
        "Fonction": "ARCHIVES MODERNES ET CONTEMPORAINES"
    },
    {
        "thematique": "Education et enseignement",
        "Description": "Instruction publique, ecoles primaires, colleges, lycees, universite, bourses.",
        "date_extreme_min": 1800,
        "date_extreme_max": 2020,
        "date_extreme_thematique": "1800/2020",
        "Métrage réel": 2500.0,
        "Nombre d'entrée": 120,
        "Fonction": "ARCHIVES MODERNES ET CONTEMPORAINES"
    },
    {
        "thematique": "Finances publiques et fiscalite",
        "Description": "Contributions directes et indirectes, cadastre, enregistrement, domaines, tresor public.",
        "date_extreme_min": 1800,
        "date_extreme_max": 2000,
        "date_extreme_thematique": "1800/2000",
        "Métrage réel": 5000.0,
        "Nombre d'entrée": 250,
        "Fonction": "ARCHIVES MODERNES ET CONTEMPORAINES"
    },
    {
        "thematique": "Archives judiciaires",
        "Description": "Cours d'appel, tribunaux, justices de paix, etablissements penitentiaires.",
        "date_extreme_min": 1800,
        "date_extreme_max": 2010,
        "date_extreme_thematique": "1800/2010",
        "Métrage réel": 6000.0,
        "Nombre d'entrée": 180,
        "Fonction": "ARCHIVES MODERNES ET CONTEMPORAINES"
    },
    {
        "thematique": "Services de police",
        "Description": "Police generale, etrangers, surete, commissariats, renseignements generaux.",
        "date_extreme_min": 1800,
        "date_extreme_max": 2000,
        "date_extreme_thematique": "1800/2000",
        "Métrage réel": 2000.0,
        "Nombre d'entrée": 60,
        "Fonction": "ARCHIVES MODERNES ET CONTEMPORAINES"
    },
    {
        "thematique": "Transports, amenagement, environnement",
        "Description": "Ponts et chaussees, routes, chemins de fer, port de Marseille, urbanisme, environnement.",
        "date_extreme_min": 1800,
        "date_extreme_max": 2024,
        "date_extreme_thematique": "1800/2024",
        "Métrage réel": 3000.0,
        "Nombre d'entrée": 60,
        "Fonction": "ARCHIVES MODERNES ET CONTEMPORAINES"
    },
    # Autres fonds
    {
        "thematique": "Hopitaux de Marseille",
        "Description": "Archives de l'Assistance publique - Hopitaux de Marseille et etablissements associes.",
        "date_extreme_min": 1600,
        "date_extreme_max": 2000,
        "date_extreme_thematique": "1600/2000",
        "Métrage réel": 2000.0,
        "Nombre d'entrée": 80,
        "Fonction": "ARCHIVES HOSPITALIERES"
    },
    {
        "thematique": "Autres etablissements hospitaliers",
        "Description": "Hopitaux locaux, hospices et etablissements de sante du departement.",
        "date_extreme_min": 1700,
        "date_extreme_max": 2020,
        "date_extreme_thematique": "1700/2020",
        "Métrage réel": 1000.0,
        "Nombre d'entrée": 40,
        "Fonction": "ARCHIVES HOSPITALIERES"
    },
    {
        "thematique": "Fonds familiaux et personnels",
        "Description": "Archives de familles nobles et bourgeoises, papiers de personnalites locales.",
        "date_extreme_min": 1200,
        "date_extreme_max": 2020,
        "date_extreme_thematique": "1200/2020",
        "Métrage réel": 1500.0,
        "Nombre d'entrée": 150,
        "Fonction": "ARCHIVES PRIVEES"
    },
    {
        "thematique": "Fonds d'entreprises",
        "Description": "Archives d'entreprises industrielles, commerciales et artisanales du departement.",
        "date_extreme_min": 1800,
        "date_extreme_max": 2023,
        "date_extreme_thematique": "1800/2023",
        "Métrage réel": 1800.0,
        "Nombre d'entrée": 120,
        "Fonction": "ARCHIVES PRIVEES"
    },
    {
        "thematique": "Fonds associatifs et syndicaux",
        "Description": "Archives d'associations, syndicats, mouvements sociaux et organisations professionnelles.",
        "date_extreme_min": 1850,
        "date_extreme_max": 2020,
        "date_extreme_thematique": "1850/2020",
        "Métrage réel": 700.0,
        "Nombre d'entrée": 80,
        "Fonction": "ARCHIVES PRIVEES"
    },
    {
        "thematique": "Photographies et cartes postales",
        "Description": "Collections de photographies et cartes postales anciennes illustrant le departement.",
        "date_extreme_min": 1860,
        "date_extreme_max": 2024,
        "date_extreme_thematique": "1860/2024",
        "Métrage réel": 800.0,
        "Nombre d'entrée": 80,
        "Fonction": "FONDS ICONOGRAPHIQUES ET AUDIOVISUELS"
    },
    {
        "thematique": "Affiches et plans",
        "Description": "Collections d'affiches, plans et documents cartographiques.",
        "date_extreme_min": 1700,
        "date_extreme_max": 2020,
        "date_extreme_thematique": "1700/2020",
        "Métrage réel": 600.0,
        "Nombre d'entrée": 50,
        "Fonction": "FONDS ICONOGRAPHIQUES ET AUDIOVISUELS"
    },
    {
        "thematique": "Films et enregistrements sonores",
        "Description": "Archives audiovisuelles, films documentaires et enregistrements sonores.",
        "date_extreme_min": 1920,
        "date_extreme_max": 2024,
        "date_extreme_thematique": "1920/2024",
        "Métrage réel": 600.0,
        "Nombre d'entrée": 50,
        "Fonction": "FONDS ICONOGRAPHIQUES ET AUDIOVISUELS"
    },
    {
        "thematique": "Registres paroissiaux",
        "Description": "Registres de baptemes, mariages et sepultures anterieurs a 1792.",
        "date_extreme_min": 1530,
        "date_extreme_max": 1792,
        "date_extreme_thematique": "1530/1792",
        "Métrage réel": 2000.0,
        "Nombre d'entrée": 130,
        "Fonction": "ETAT CIVIL"
    },
    {
        "thematique": "Etat civil republicain",
        "Description": "Registres de naissances, mariages et deces depuis 1792.",
        "date_extreme_min": 1792,
        "date_extreme_max": 2023,
        "date_extreme_thematique": "1792/2023",
        "Métrage réel": 4000.0,
        "Nombre d'entrée": 270,
        "Fonction": "ETAT CIVIL"
    }
]

# Donnees des Producteurs
producteurs_data = [
    # Producteurs des archives anciennes
    {
        "producteur": "Parlement de Provence",
        "Description": "Cour souveraine de justice pour la Provence, creee en 1501.",
        "date_extreme_min": 1501,
        "date_extreme_max": 1789,
        "date_extreme_producteur": "1501/1789",
        "Métrage réel": 300.0,
        "Nombre d'entrée": 3,
        "Thematique": "Serie B - Cours et juridictions"
    },
    {
        "producteur": "Cour des Comptes de Provence",
        "Description": "Institution financiere de controle des comptes publics en Provence.",
        "date_extreme_min": 1350,
        "date_extreme_max": 1789,
        "date_extreme_producteur": "1350/1789",
        "Métrage réel": 250.0,
        "Nombre d'entrée": 2,
        "Thematique": "Serie B - Cours et juridictions"
    },
    {
        "producteur": "Senechaussee de Marseille",
        "Description": "Tribunal de premiere instance et d'appel pour la ville de Marseille.",
        "date_extreme_min": 1200,
        "date_extreme_max": 1789,
        "date_extreme_producteur": "1200/1789",
        "Métrage réel": 150.0,
        "Nombre d'entrée": 2,
        "Thematique": "Serie B - Cours et juridictions"
    },
    {
        "producteur": "Etats de Provence",
        "Description": "Assemblee representative des trois ordres de la province de Provence.",
        "date_extreme_min": 1400,
        "date_extreme_max": 1789,
        "date_extreme_producteur": "1400/1789",
        "Métrage réel": 200.0,
        "Nombre d'entrée": 2,
        "Thematique": "Serie C - Administrations provinciales"
    },
    {
        "producteur": "Intendance de Provence",
        "Description": "Administration royale chargee de la gestion de la province au nom du roi.",
        "date_extreme_min": 1630,
        "date_extreme_max": 1789,
        "date_extreme_producteur": "1630/1789",
        "Métrage réel": 300.0,
        "Nombre d'entrée": 3,
        "Thematique": "Serie C - Administrations provinciales"
    },
    {
        "producteur": "Intendance des galeres",
        "Description": "Administration des galeres royales basees a Marseille.",
        "date_extreme_min": 1650,
        "date_extreme_max": 1748,
        "date_extreme_producteur": "1650/1748",
        "Métrage réel": 100.0,
        "Nombre d'entrée": 2,
        "Thematique": "Serie E - Intendance des galeres, intendance sanitaire, communautes de metiers"
    },
    {
        "producteur": "Intendance sanitaire de Marseille",
        "Description": "Service charge de la lutte contre les epidemies et du controle sanitaire du port.",
        "date_extreme_min": 1600,
        "date_extreme_max": 1789,
        "date_extreme_producteur": "1600/1789",
        "Métrage réel": 200.0,
        "Nombre d'entrée": 2,
        "Thematique": "Serie E - Intendance des galeres, intendance sanitaire, communautes de metiers"
    },
    {
        "producteur": "Archeveche d'Aix",
        "Description": "Diocese d'Aix-en-Provence, siege de l'archevêque metropolitain.",
        "date_extreme_min": 900,
        "date_extreme_max": 1789,
        "date_extreme_producteur": "900/1789",
        "Métrage réel": 100.0,
        "Nombre d'entrée": 1,
        "Thematique": "Serie G - Clerge seculier"
    },
    {
        "producteur": "Eveche de Marseille",
        "Description": "Diocese de Marseille, administrant les paroisses de la ville et des environs.",
        "date_extreme_min": 1000,
        "date_extreme_max": 1789,
        "date_extreme_producteur": "1000/1789",
        "Métrage réel": 80.0,
        "Nombre d'entrée": 1,
        "Thematique": "Serie G - Clerge seculier"
    },
    {
        "producteur": "Abbaye de Saint-Victor de Marseille",
        "Description": "Grande abbaye benedictine, l'une des plus anciennes de Provence.",
        "date_extreme_min": 1020,
        "date_extreme_max": 1789,
        "date_extreme_producteur": "1020/1789",
        "Métrage réel": 100.0,
        "Nombre d'entrée": 1,
        "Thematique": "Serie H - Clerge regulier"
    },
    # Producteurs modernes
    {
        "producteur": "Prefecture des Bouches-du-Rhone",
        "Description": "Administration centrale de l'Etat dans le departement, dirigee par le prefet.",
        "date_extreme_min": 1800,
        "date_extreme_max": 2024,
        "date_extreme_producteur": "1800/2024",
        "Métrage réel": 5000.0,
        "Nombre d'entrée": 200,
        "Thematique": "Administration generale"
    },
    {
        "producteur": "Sous-prefecture d'Aix-en-Provence",
        "Description": "Administration de l'arrondissement d'Aix-en-Provence.",
        "date_extreme_min": 1800,
        "date_extreme_max": 2000,
        "date_extreme_producteur": "1800/2000",
        "Métrage réel": 500.0,
        "Nombre d'entrée": 30,
        "Thematique": "Administration generale"
    },
    {
        "producteur": "Sous-prefecture d'Arles",
        "Description": "Administration de l'arrondissement d'Arles.",
        "date_extreme_min": 1800,
        "date_extreme_max": 2000,
        "date_extreme_producteur": "1800/2000",
        "Métrage réel": 400.0,
        "Nombre d'entrée": 25,
        "Thematique": "Administration generale"
    },
    {
        "producteur": "Conseil general des Bouches-du-Rhone",
        "Description": "Assemblee deliberante du departement, devenue Conseil departemental en 2015.",
        "date_extreme_min": 1800,
        "date_extreme_max": 2024,
        "date_extreme_producteur": "1800/2024",
        "Métrage réel": 3000.0,
        "Nombre d'entrée": 150,
        "Thematique": "Administration generale"
    },
    {
        "producteur": "Chambre de commerce de Marseille",
        "Description": "Institution consulaire representant les entreprises commerciales.",
        "date_extreme_min": 1599,
        "date_extreme_max": 2000,
        "date_extreme_producteur": "1599/2000",
        "Métrage réel": 800.0,
        "Nombre d'entrée": 40,
        "Thematique": "Economie, industrie, agriculture et forets"
    },
    {
        "producteur": "Direction des services agricoles",
        "Description": "Services departementaux de l'agriculture et de la foret.",
        "date_extreme_min": 1880,
        "date_extreme_max": 1990,
        "date_extreme_producteur": "1880/1990",
        "Métrage réel": 600.0,
        "Nombre d'entrée": 30,
        "Thematique": "Economie, industrie, agriculture et forets"
    },
    {
        "producteur": "Tribunal de grande instance de Marseille",
        "Description": "Juridiction judiciaire de droit commun pour Marseille.",
        "date_extreme_min": 1800,
        "date_extreme_max": 2000,
        "date_extreme_producteur": "1800/2000",
        "Métrage réel": 2000.0,
        "Nombre d'entrée": 60,
        "Thematique": "Archives judiciaires"
    },
    {
        "producteur": "Cour d'appel d'Aix-en-Provence",
        "Description": "Juridiction d'appel pour le ressort comprenant plusieurs departements.",
        "date_extreme_min": 1800,
        "date_extreme_max": 1950,
        "date_extreme_producteur": "1800/1950",
        "Métrage réel": 1500.0,
        "Nombre d'entrée": 40,
        "Thematique": "Archives judiciaires"
    },
    {
        "producteur": "Rectorat d'Aix-Marseille",
        "Description": "Administration de l'Education nationale pour l'academie.",
        "date_extreme_min": 1850,
        "date_extreme_max": 2000,
        "date_extreme_producteur": "1850/2000",
        "Métrage réel": 1000.0,
        "Nombre d'entrée": 50,
        "Thematique": "Education et enseignement"
    },
    {
        "producteur": "Direction departementale de l'equipement",
        "Description": "Services de l'Etat charges des routes, de l'urbanisme et de l'habitat.",
        "date_extreme_min": 1800,
        "date_extreme_max": 2010,
        "date_extreme_producteur": "1800/2010",
        "Métrage réel": 2000.0,
        "Nombre d'entrée": 40,
        "Thematique": "Transports, amenagement, environnement"
    },
    {
        "producteur": "Assistance publique - Hopitaux de Marseille",
        "Description": "Etablissement public hospitalier gerant les hopitaux de Marseille.",
        "date_extreme_min": 1600,
        "date_extreme_max": 2000,
        "date_extreme_producteur": "1600/2000",
        "Métrage réel": 2000.0,
        "Nombre d'entrée": 80,
        "Thematique": "Hopitaux de Marseille"
    },
    {
        "producteur": "Compagnie generale transatlantique",
        "Description": "Compagnie maritime assurant les liaisons vers l'Afrique du Nord et les colonies.",
        "date_extreme_min": 1855,
        "date_extreme_max": 1974,
        "date_extreme_producteur": "1855/1974",
        "Métrage réel": 300.0,
        "Nombre d'entrée": 15,
        "Thematique": "Fonds d'entreprises"
    },
    {
        "producteur": "Societe generale de raffinage",
        "Description": "Entreprise de raffinage petrolier implantee a Marseille.",
        "date_extreme_min": 1900,
        "date_extreme_max": 1980,
        "date_extreme_producteur": "1900/1980",
        "Métrage réel": 200.0,
        "Nombre d'entrée": 10,
        "Thematique": "Fonds d'entreprises"
    },
    {
        "producteur": "Famille de Villeneuve-Trans",
        "Description": "Grande famille noble de Provence, seigneurs de Trans et autres fiefs.",
        "date_extreme_min": 1200,
        "date_extreme_max": 1900,
        "date_extreme_producteur": "1200/1900",
        "Métrage réel": 50.0,
        "Nombre d'entrée": 5,
        "Thematique": "Fonds familiaux et personnels"
    },
    {
        "producteur": "Famille Borelly",
        "Description": "Famille de negociants marseillais, proprietaires du chateau Borrely.",
        "date_extreme_min": 1600,
        "date_extreme_max": 1850,
        "date_extreme_producteur": "1600/1850",
        "Métrage réel": 30.0,
        "Nombre d'entrée": 3,
        "Thematique": "Fonds familiaux et personnels"
    }
]


def main():
    """Cree le fichier Excel avec les donnees des AD13."""
    project_root = Path(__file__).parent.parent
    output_path = project_root / "data" / "archives.xlsx"
    
    # Creer les DataFrames
    df_fonctions = pd.DataFrame(fonctions_data)
    df_thematiques = pd.DataFrame(thematiques_data)
    df_producteurs = pd.DataFrame(producteurs_data)
    
    # Renommer les colonnes pour correspondre au format attendu
    df_thematiques = df_thematiques.rename(columns={
        "thematique": "Thématique",
        "date_extreme_thematique": "date_extreme_thematique"
    })
    
    # Ecrire le fichier Excel avec plusieurs feuilles
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_fonctions.to_excel(writer, sheet_name='Fonction', index=False)
        df_thematiques.to_excel(writer, sheet_name='Thématique', index=False)
        df_producteurs.to_excel(writer, sheet_name='Producteur', index=False)
    
    print(f"Fichier Excel cree: {output_path}")
    print(f"  - Fonctions: {len(df_fonctions)}")
    print(f"  - Thematiques: {len(df_thematiques)}")
    print(f"  - Producteurs: {len(df_producteurs)}")
    
    # Calculer les totaux
    total_metrage_fonctions = df_fonctions['Métrage réel'].sum()
    print(f"\nTotal metrage (Fonctions): {total_metrage_fonctions:,.0f} ml")


if __name__ == "__main__":
    main()

