# Note de frais

**Application en ligne :** [https://notedefrais-production.up.railway.app/](https://notedefrais-production.up.railway.app/)

Application web de gestion de notes de frais : analyse de justificatifs par IA (Groq), formulaire éditable (HTMX), enregistrement dans Google Sheets, tableau de bord mensuel et export PDF.

---

## Sommaire

- [Présentation](#présentation)
- [Installation](#installation)
- [Configuration](#configuration)
- [Lancement](#lancement)
- [Structure du projet](#structure-du-projet)
- [Routes API](#routes-api)
- [Déploiement Railway](#déploiement-railway)
- [API Google Drive](#api-google-drive)
- [Conseils et pièges à éviter](#conseils-et-pièges-à-éviter)
- [Pour aller plus loin (optionnel)](#pour-aller-plus-loin-optionnel)

---

## Présentation

Flux principal :

1. **Upload / photo** d'un justificatif
2. **Analyse IA** (extraction des champs : type, fournisseur, date, montant, TVA, etc.)
3. **Formulaire éditable** avec champ employé
4. **Envoi** vers Google Sheets
5. **Tableau de bord** : dépenses mensuelles, TVA, répartition par employé
6. **Export PDF** du récapitulatif mensuel

---

## Installation

```bash
git clone https://github.com/RomainR99/Note_de_frais.git
cd Note_de_frais
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Configuration

Copiez `.env.example` vers `.env` et renseignez :

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Clé API Groq pour l'analyse d'images |
| `GOOGLE_SHEET_ID` | ID du Google Spreadsheet |
| `GOOGLE_SHEET_NAME` | Nom de l'onglet (ex. `Justificatifs notes de frais`) |
| `GOOGLE_CREDENTIALS_FILE` | Fichier credentials en local (`credentials.json`) |
| `GOOGLE_CREDENTIALS` | JSON du compte de service (Railway uniquement) |
| `APP_BASE_URL` | URL publique de l'app (`http://127.0.0.1:8000` en local) |

En local, placez `credentials.json` à la racine (fichier ignoré par git).  
Partagez le Google Sheet avec l'email du compte de service (`client_email` dans le JSON) en **Éditeur**.

---

## Lancement

```bash
source venv/bin/activate
uvicorn app:app --reload
```

Ouvrez [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Structure du projet

| Fichier / dossier | Rôle |
|-------------------|------|
| `app.py` | Routes FastAPI, rendu HTMX |
| `backend.py` | Agent IA Groq (extraction depuis image) |
| `sheets.py` | Client Google Sheets (lecture / écriture) |
| `dashboard.py` | Calculs mensuels (TTC, TVA, par employé) |
| `pdf_export.py` | Génération du récapitulatif PDF |
| `google_credentials.py` | Chargement des credentials (fichier ou variable d'env) |
| `image_utils.py` | Sauvegarde locale des images uploadées |
| `static/` | HTML, CSS, JS (HTMX + prévisualisation) |
| `uploads/` | Images servies par l'application |

---

## Routes API

| Route | Méthode | Description |
|-------|---------|-------------|
| `/` | GET | Page principale |
| `/api/analyze` | POST | Analyse d'une image, retourne le formulaire pré-rempli |
| `/api/submit` | POST | Envoie la note vers Google Sheets |
| `/api/expenses` | GET | Liste HTML des notes enregistrées |
| `/api/dashboard` | GET | Tableau de bord mensuel (paramètre `?month=YYYY-MM`) |
| `/api/export/pdf` | GET | Export PDF mensuel (paramètre `?month=YYYY-MM`) |
| `/uploads/{fichier}` | GET | Accès HTTP aux images stockées localement |

---

## Déploiement Railway

1. Connectez le dépôt GitHub à [Railway](https://railway.app/)
2. Ajoutez les variables d'environnement (sans commiter de secrets) :
   - `GOOGLE_CREDENTIALS` → contenu JSON du compte de service
   - `GROQ_API_KEY`, `GOOGLE_SHEET_ID`, `GOOGLE_SHEET_NAME`
   - `APP_BASE_URL` → `https://notedefrais-production.up.railway.app`
3. Commande de démarrage : `uvicorn app:app --host 0.0.0.0 --port $PORT`

> Les images dans `uploads/` sont éphémères sur Railway (disque non persistant). Les liens d'images dans le Sheet ne fonctionnent que tant que le fichier existe sur le serveur.

---

## API Google Drive

Lors de la configuration OAuth dans la [Google Cloud Console](https://console.cloud.google.com/), activer les scopes suivants :

| Scope | Description |
|-------|-------------|
| `.../auth/userinfo.email` | Accès à l'adresse e-mail de l'utilisateur |
| `.../auth/userinfo.profile` | Accès au profil de base de l'utilisateur (nom, photo) |
| `.../auth/drive.file` | Accès aux fichiers créés ou ouverts par l'application dans Google Drive |

Scopes complets :

```
https://www.googleapis.com/auth/userinfo.email
https://www.googleapis.com/auth/userinfo.profile
https://www.googleapis.com/auth/drive.file
```

### Dossier Drive pour les images (optionnel)

Pour enregistrer les justificatifs dans un dossier Drive plutôt qu'en local :

1. Créez un dossier dans Google Drive (ex. `Justificatifs notes de frais`)
2. Partagez-le avec l'email du compte de service en tant qu'**Éditeur**
3. Copiez l'ID du dossier depuis l'URL (`https://drive.google.com/drive/folders/ID_ICI`)
4. Ajoutez-le dans `.env` :

```
GOOGLE_DRIVE_FOLDER_ID="votre_id_de_dossier"
```

---

## Conseils et pièges à éviter

### Sur le modèle IA

Le modèle peut parfois retourner des champs avec des valeurs approximatives ou mal formatées. Votre backend doit être défensif : ne jamais supposer qu'un champ est présent ou correctement typé. Utilisez `.get("champ", None)` systématiquement.

### Sur HTMX

Rappel du TP précédent : HTMX ne swape pas le contenu sur les réponses 4xx/5xx par défaut. Il faut écouter l'événement `htmx:responseError` en JS et injecter manuellement le fragment d'erreur.

### Sur Google Sheets

La bibliothèque gspread peut lever des exceptions en cas de quota dépassé ou de permission manquante. Wrappez vos appels dans des `try/except` et retournez des messages d'erreur clairs à l'utilisateur.

### Sur les credentials

Ne commitez jamais votre fichier JSON de compte de service ni votre `.env`. Vérifiez votre `.gitignore` avant chaque commit. En cas de doute, révoquez et régénérez vos credentials depuis [Google Cloud Console](https://console.cloud.google.com/).

### Sur l'image en base64 dans le formulaire

Une image de 3 Mo encodée en base64 représente environ 4 Mo de données texte dans le formulaire. C'est acceptable pour ce TP, mais gardez en tête que c'est une contrainte à résoudre différemment en production (upload séparé, presigned URL, etc.).

---

## Pour aller plus loin (optionnel)

| Fonctionnalité | Statut |
|----------------|--------|
| **Déploiement Railway** | Implémenté — [notedefrais-production.up.railway.app](https://notedefrais-production.up.railway.app/) |
| **Export PDF** mensuel depuis le Sheet | Implémenté — `/api/export/pdf?month=YYYY-MM` |
| **Tableau de bord** mensuel (TTC, TVA, par employé) | Implémenté |
| **Catégorisation automatique** : colonne centre de coût / projet sélectionnable avant soumission | À faire |
| **Historique local** : afficher les 5 dernières soumissions via `/api/history` | À faire (liste complète disponible via `/api/expenses`) |
