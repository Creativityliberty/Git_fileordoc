# 🍎 Skill: Swift

Ce skill gère l'analyse des projets Swift (iOS, macOS, Server-side Swift).

## 🔍 Signatures de Détection

- `Package.swift`
- `*.xcodeproj`
- `*.xcworkspace`

## 🤖 Instructions d'Analyse

1. **SwiftPM** : Analyser les packages via `Package.swift`.
2. **Structure** : Identifier l'utilisation de SwiftUI ou UIKit.
3. **Protocols** : Mapper les protocoles et extensions.
4. **Memory Management** : Rechercher d'éventuels cycles de référence (ARC).

## 🧪 Stratégie de Test

- Commande `swift test`.
- Tests d'interface via XCTest.
