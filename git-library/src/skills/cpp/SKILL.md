# ⚙️ Skill: C++

Ce skill permet d'analyser les projets hautes performances en C++.

## 🔍 Signatures de Détection

- `CMakeLists.txt`
- `Makefile`
- `conanfile.txt` / `vcpkg.json`

## 🤖 Instructions d'Analyse

1. **Build System** : Analyser les cibles de build dans `CMakeLists.txt`.
2. **Standard** : Vérifier la version du standard utilisée (C++11/14/17/20/23).
3. **Pointers** : Surveiller l'usage des pointeurs intelligents vs pointeurs bruts.
4. **Header Files** : Mapper les inclusions et dépendances.

## 🧪 Stratégie de Test

- Tests avec GoogleTest (gtest) ou Catch2.
- Analyse statique via `clang-tidy`.
