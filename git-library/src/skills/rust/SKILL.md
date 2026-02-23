# 🦀 Skill: Rust

Ce skill gère les systèmes performants écrits en Rust.

### 🔍 Signatures de Détection

- `Cargo.toml`
- `Cargo.lock`
- `src/main.rs` ou `src/lib.rs`

### 🤖 Instructions d'Analyse

1. **Crates** : Analyser les dépendances dans `Cargo.toml`.
2. **Traits** : Identifier les abstractions clés.
3. **Safety** : Rechercher les blocs `unsafe`.
4. **Features** : Vérifier les flags de compilation.

### 🧪 Stratégie de Test

- Commande `cargo test`.
- Tests d'intégration dans le dossier `tests/`.
- Benchmarks avec `criterion`.
