# git-fileordoc

`git-fileordoc` est un outil en ligne de commande permettant de télécharger uniquement ce dont vous avez besoin depuis un dépôt GitHub.

## Fonctionnalités

* **Fichier unique** : Téléchargement instantané via `curl`.
* **Dossier spécifique** : Clone uniquement le contenu d'un dossier sans le reste du repo.
* **Nom personnalisé** : Possibilité de renommer le fichier ou le dossier à la volée en ajoutant un deuxième argument.

## Usage

```bash
# Téléchargement vers le dossier courant
./git-fileordoc.sh https://github.com/user/repo/tree/main/folder

# Téléchargement vers un dossier spécifique (choix du nom/chemin)
./git-fileordoc.sh https://github.com/user/repo/tree/main/folder nouveau-nom-dossier
```

## Installation & Permission

Pour installer l'outil globalement :

```bash
sudo curl -o /usr/local/bin/git-fileordoc https://raw.githubusercontent.com/Creativityliberty/Git_fileordoc/main/git-fileordoc.sh
sudo chmod +x /usr/local/bin/git-fileordoc
```

## Exemples d'utilisation

| Tâche | Commande |
| --- | --- |
| **Télécharger un fichier** | `git-fileordoc https://github.com/user/repo/blob/main/file.js` |
| **Dossier avec nouveau nom** | `git-fileordoc https://github.com/user/repo/tree/main/src/utils mes_outils` |
| **Mettre à jour l'outil** | `git-fileordoc ---update` |

## Pourquoi c'est une "Upgrade" ?

1. **Dossier Temporaire Dynamique** : Utilisation de `mktemp -d` pour éviter les conflits si tu lances plusieurs instances.
2. **Renommage Natif** : L'ajout du deuxième argument `[TARGET_NAME]` évite de devoir faire un `mv` manuellement après le téléchargement.
3. **Optimisation Git** : Utilisation forcée de `--filter=blob:none` pour garantir que Git ne télécharge aucun contenu avant que le chemin cible ne soit défini.
