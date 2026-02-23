# ⚛️ Skill: React & NodeJS

Ce skill permet d'analyser les projets basés sur React, Vue, Svelte ou NodeJS pur.

### 🔍 Signatures de Détection

- `package.json`
- `node_modules/`
- `tsconfig.json`

### 🤖 Instructions d'Analyse

1. **Structure** : Identifier les composants dans `src/components`.
2. **État** : Vérifier l'utilisation de Redux, Context API ou Zustand.
3. **Build** : Rechercher les scripts `build`, `start`, `dev` dans `package.json`.
4. **Hooks** : Analyser les hooks personnalisés.

### 🧪 Stratégie de Test

- Priorité aux tests unitaires avec Vitest ou Jest.
- Tests E2E avec Playwright si un dossier `tests/e2e` est présent.
