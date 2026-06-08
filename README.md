# Note de frais

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

### Dossier Drive pour les images

Pour enregistrer les justificatifs dans la colonne **Image** du Google Sheet :

1. Créez un dossier dans Google Drive (ex. `Justificatifs notes de frais`)
2. Partagez-le avec l'email du compte de service (`client_email` dans `credentials.json`) en tant qu'**Éditeur**
3. Copiez l'ID du dossier depuis l'URL (`https://drive.google.com/drive/folders/ID_ICI`)
4. Ajoutez-le dans `.env` :

```
GOOGLE_DRIVE_FOLDER_ID="votre_id_de_dossier"
```
