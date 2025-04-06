# Deep Thinking Assistant - OpenAI MCP Server

深い思考と分析を提供するOpenAI APIベースのMCPサーバーです。
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
├── dive_deep_server.py     # メインサーバーファイル
├── logger_config.py        # ロギング設定
├── prompts.py             # プロンプト定義
├── requirements.txt       # 依存関係
├── .env                   # 環境変数設定
├── .gitignore            # Gitの除外設定
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
OPENAI_API_KEY=your_api_key_here
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
- `model`: 使用するモデル名（デフォルト: "o3-mini"）
- `reasoning_effort`: 推論の努力レベル（デフォルト: "medium"）

### enhancement_agent

コードの改善点を分析し、具体的な提案を行います。このツールは、コードの品質、パフォーマンス、保守性などの観点から包括的な分析を行い、実践的な改善提案を提供します。

パラメータ:
- `instructions`: レビュー対象のコードに対する指示（必須）
- `code`: コードのリスト（必須）
- `model`: 使用するモデル名（デフォルト: "gpt-4"）
- `temperature`: 生成時の温度パラメータ（デフォルト: 0.7）

### final_review_agent

最終的なコードレビューを行い、改善点を提示します。このツールは、提案された変更や改善点を批判的に分析し、潜在的な問題や更なる最適化の機会を特定します。

パラメータ:
- `instructions`: レビュー対象のコードに対する指示（必須）
- `code`: コードのリスト（必須）
- `model`: 使用するモデル名（デフォルト: "gpt-4"）
- `temperature`: 生成時の温度パラメータ（デフォルト: 0.7）

## 使用例

1. 思考プロセスの深化:
```python
response = deep_thinking_agent(
    instructions="このアルゴリズムの最適化方法を考えてください",
    context="現在の実装では時間計算量がO(n^2)となっています",
    model="o3-mini"
)
```

2. コードの改善提案:
```python
response = enhancement_agent(
    instructions="このコードのパフォーマンスを改善してください",
    code=["def example():\n    # コード内容"],
    model="gpt-4"
)
```

3. 最終レビュー:
```python
response = final_review_agent(
    instructions="実装された改善案の最終確認をお願いします",
    code=["def improved_example():\n    # 改善されたコード"],
    model="gpt-4"
)
```

## デフォルトのシステムプロンプト

### 思考支援プロンプト

サーバーは以下の原則に基づいて思考を支援します：

1. 思考プロセス
   - 問題を複数の視点から分析
   - 前提条件と制約の明確化
   - 潜在的な課題やリスクの特定
   - 解決策の長所・短所の比較検討

2. 知識の統合
   - 関連する概念や理論の結びつけ
   - 実践的な経験との関連付け
   - 異なる分野からの知見の活用

3. 批判的思考
   - 仮定の妥当性の検証
   - 論理的一貫性のチェック
   - 反証可能性の考慮
   - バイアスの認識と排除

4. 創造的思考
   - 新しい視点や解決策の提案
   - 既存の概念の組み合わせ
   - 制約を活かした発想

5. 実用性重視
   - 具体的で実行可能な提案
   - コンテキストに応じた適切な詳細度
   - フィードバックループの組み込み

### 回答分析プロンプト

回答の分析は以下の観点から行われます：

1. 論理的整合性
   - 前提条件との整合性
   - 論理の飛躍や欠落
   - 結論の妥当性

2. 実装上の課題
   - 技術的な実現可能性
   - パフォーマンスへの影響
   - スケーラビリティの課題
   - セキュリティリスク

3. ビジネス的な影響
   - コストと効果のバランス
   - 保守性と運用負荷
   - ステークホルダーへの影響

4. 代替案の可能性
   - より効率的なアプローチ
   - トレードオフの検討
   - 新しい視点からの解決策

5. 見落とされた視点
   - エッジケースの考慮
   - 長期的な影響
   - 副作用や波及効果 