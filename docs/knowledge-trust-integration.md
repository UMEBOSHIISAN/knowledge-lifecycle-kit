# Knowledge Trust Integration Contract

> Version: Gen2 (2026-08-23)
> Scope: Knowledge Lifecycle Gate (KLG) & Memory Trust Substrate Consolidation
> Invariant: Knowledge Trust owns knowledge state transitions and immutable history. It never grants Action Authority.

---

## 1. 責務統合 (Consolidated Architecture)

Knowledge Trust は以下の2つの能力を統合したナレッジ正本管理ドメインです。

1. **Lifecycle State Transition (`knowledge-lifecycle-gate`)**:
   - `NEW` ➔ `CANDIDATE` ➔ `CONFIRMED` ➔ `STALE` ➔ `RETIRED` の状態機械。
   - Markdown ドキュメント内のメタデータ検証と不正遷移の遮断。
2. **Immutable Versioning & Audit (`memory_trust`)**:
   - `store/` — 現行の確定正本。
   - `versions/` — 改ざん不能なタイムスタンプ・アクター・SHA-256 付き不変履歴。
   - `audit/audit.jsonl` — 全ミューテーション（追記・更新）の不可逆な監査元帳。
   - `redact/redact.jsonl` — 機密情報除去の明示的記録。

---

## 2. 境界不変条件 (Boundary Invariants)

- **No Action Authority**: Knowledge Trust はナレッジの信頼度と履歴のみを管理し、システムの実行権限（Action Authority）は発行しない。
- **No Direct Mutation**: `store/` への直接編集を禁止し、必ず `versions/` への世代保存と `audit.jsonl` へのハッシュ記録を伴う。
- **Rebuildability**: 派生インデックス（`context-reuse.db` 等）は Knowledge Trust の正本から 100% 再構築可能でなければならない。
