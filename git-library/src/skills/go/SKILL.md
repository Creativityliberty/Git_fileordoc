# 🐹 Skill: Go

Ce skill optimise l'analyse des projets écrits en Go.

## 🔍 Signatures de Détection

- `go.mod`
- `go.sum`
- `main.go`

## 🤖 Instructions d'Analyse

1. **Modules** : Analyser les dépendances dans `go.mod`.
2. **Interfaces** : Identifier les contrats clés définis par des interfaces.
3. **Concurrence** : Rechercher l'utilisation massive de `goroutines` et `channels`.
4. **Tooling** : Vérifier si un `Makefile` ou un `docker-compose.yml` est présent.

## 🧪 Stratégie de Test

- Commande `go test ./...`.
- Tests de benchmark avec `go test -bench`.
