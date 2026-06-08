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
