# Deep Thinking Assistant - Gemini MCP Server

深い思考と分析を提供するGemini APIベースのMCPサーバーです。
AIエディタのモデルと連携して、より深い分析と洞察を提供します。

## 特徴

- 多角的な視点からの問題分析
- 批判的思考と創造的思考の統合
- 実践的で具体的な提案
- 既存の知識の統合と新しい視点の提供
- コンテキストに応じた適切な詳細度の調整
- 提案された解決策の批判的分析と改善提案

## プロジェクト構造

```
dive_deep/
├── logs/                   # ログファイルディレクトリ
├── venv/                   # Python仮想環境
├── .venv/                  # 代替Python仮想環境
├── dive_deep_server.py     # メインサーバーファイル
├── logger_config.py        # ロギング設定
├── prompts.py             # プロンプト定義
├── requirements.txt       # 依存関係
├── .env                   # 環境変数設定
└── README.md             # ドキュメント
```

## セットアップ

1. 依存関係のインストール:
```bash
pip install -r requirements.txt
```

2. 環境変数の設定:
`.env`ファイルを作成し、以下の内容を設定してください：
```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

## 使用方法

サーバーの起動:
```bash
python dive_deep_server.py
```

## 利用可能なツール

### deep_thinking_agent

問題解決のための思考プロセスを深め、着眼点を提示します。このツールは、問題に対する深い理解と多角的な分析を提供し、より良い解決策を導き出すためのガイドラインを提示します。

パラメータ:
- `instructions`: ユーザーからの指示（必須）
- `context`: 思考プロセスのコンテキスト（必須）
- `model`: 使用するモデル名（デフォルト: "gemini-2.0-flash"）

### enhancement_agent

コードの改善点を分析し、具体的な提案を行います。このツールは、コードの品質、パフォーマンス、保守性などの観点から包括的な分析を行い、実践的な改善提案を提供します。

パラメータ:
- `instructions`: レビュー対象のコードに対する指示（必須）
- `code`: コードのリスト（必須）
- `model`: 使用するモデル名（デフォルト: "gemini-2.0-flash"）
- `temperature`: 生成時の温度パラメータ（デフォルト: 0.7）

### final_review_agent

最終的なコードレビューを行い、改善点を提示します。このツールは、提案された変更や改善点を批判的に分析し、潜在的な問題や更なる最適化の機会を特定します。

パラメータ:
- `instructions`: レビュー対象のコードに対する指示（必須）
- `code`: コードのリスト（必須）
- `model`: 使用するモデル名（デフォルト: "gemini-2.0-flash"）
- `temperature`: 生成時の温度パラメータ（デフォルト: 0.7）

## 使用例

1. 思考プロセスの深化:
```python
response = deep_thinking_agent(
    instructions="このアルゴリズムの最適化方法を考えてください",
    context="現在の実装では時間計算量がO(n^2)となっています",
    model="gemini-2.0-flash"
)
```

2. コードの改善提案:
```python
response = enhancement_agent(
    instructions="このコードのパフォーマンスを改善してください",
    code=["def example():\n    # コード内容"],
    model="gemini-2.0-flash"
)
```

3. 最終レビュー:
```python
response = final_review_agent(
    instructions="実装された改善案の最終確認をお願いします",
    code=["def improved_example():\n    # 改善されたコード"],
    model="gemini-2.0-flash"
)
```

## デフォルトのシステムプロンプト

### 思考支援プロンプト

サーバーは以下の原則に基づいて思考を支援します：

1. 問題理解と構造化思考
   - システム思考による全体像の把握
   - MECEによる問題の分解
   - 因果関係の分析（Why-Why分析、特性要因図）
   - ステークホルダー分析と要件整理

2. 解決策の設計と評価
   - デザインパターンとアーキテクチャ原則の適用
   - トレードオフの定量的評価（コストvs.ベネフィット）
   - リスク分析と対策（FMEA手法）
   - 実現可能性の検証（PoC戦略）

3. 技術的卓越性の追求
   - クリーンアーキテクチャの原則
     ・疎結合と高凝集
     ・依存関係の適切な方向性
     ・インターフェースの抽象化
   - コード品質の最適化
     ・可読性と保守性
     ・パフォーマンスとスケーラビリティ
     ・セキュリティと堅牢性
   - テスト戦略の設計
     ・テストピラミッドの考慮
     ・境界値とエッジケース
     ・自動化と継続的検証

4. イノベーションと創造的思考
   - ラテラルシンキングの活用
   - SCAMPERメソッドによるアイデア展開
   - 制約を活かした創造的問題解決
   - 新技術とレガシーシステムの統合

5. 実装とデプロイメントの最適化
   - 段階的な実装戦略
   - 技術的負債の管理と返済計画
   - 変更の影響分析
   - デプロイメントリスクの最小化

6. 継続的改善と学習
   - KPIとメトリクスの設定
   - フィードバックループの確立
   - 知識の体系化と共有
   - PDCAサイクルの実践

7. コミュニケーションとコラボレーション
   - 技術的説明の明確化
   - ドキュメントの構造化
   - チーム間の知識共有
   - レビューとフィードバックの促進

### 回答分析プロンプト

回答の分析は以下の観点から行われます：

1. 論理的整合性と完全性
   - 前提条件と制約の妥当性
   - 論理展開の一貫性
   - 結論の導出プロセス
   - 見落とされた要素の特定
   - 反証可能性の検証

2. 技術的実現可能性と最適性
   - アルゴリズムとデータ構造の適切性
   - システムアーキテクチャの堅牢性
   - パフォーマンスとスケーラビリティ
   - セキュリティと信頼性
   - 保守性と拡張性

3. 実装と運用
   - 開発効率と生産性
   - 運用負荷とコスト
   - 監視と障害対応
   - バージョン管理とデプロイメント
   - チームコラボレーションの有効性

4. リスクと課題
   - 技術的制約と限界
   - セキュリティ脆弱性
   - パフォーマンスのボトルネック
   - 依存関係の複雑さ
   - 潜在的な技術的負債

5. ビジネス価値とインパクト
   - 開発・運用コスト
   - 市場投入までの時間
   - ユーザー体験への影響
   - ビジネス要件との整合性
   - 競争優位性への貢献

分析結果の構成：

1. 提案の強み
   - 技術的優位性
   - 実装の効率性
   - ビジネス価値
   - 革新的要素

2. 改善が必要な領域
   - 技術的課題
   - 実装上のリスク
   - 運用上の懸念
   - スケーラビリティの制限

3. 具体的な改善提案
   - 短期的な改善
   - 中長期的な最適化
   - 代替アプローチ
   - ベストプラクティスの適用

4. 追加の考慮事項
   - エッジケースと例外処理
   - 将来のスケーラビリティ
   - セキュリティ考慮事項
   - パフォーマンス最適化

5. 実装ロードマップ
   - タスクの優先順位付け
   - マイルストーンの設定
   - 成功指標（KPI）の定義
   - リスク軽減戦略 