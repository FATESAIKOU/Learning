# 03. scikit-learn: scikit-learn release 1.9: better numerics new core functionality

**Source**: https://blog.scikit-learn.org/updates/release-1-9/
**Author**: Gael Varoquaux
**Date**: 2026-06-13
**Category**: 傳統IT技術

## 1. この技術/政策は何を解決するのか?

scikit-learn 1.9 は、機械學習ワークフローにおける三つの構造的課題を解決する。

| 課題 | 解決手段 |
|------|---------|
| モデル訓練のブラックボックス化 | Callback 機構による訓練過程の可視化と介入 |
| 推定器の內部狀態の不可視性 | HTML 表示の強化（fitted attributes の公開） |
| 數値計算の不安定性と遅さ | アルゴリズムの數値的改善と GPU サポート |

scikit-learn は Python 機械學習の基盤ライブラリであり、2026 年時點で月間 1 億回以上のダウンロードを持つ。しかし、fit() を呼び出してから完了するまでの間、ユーザーは「モデルが収束しているのか」「あとどれくらい時間がかかるのか」「中間スコアはどう推移しているのか」を全く知ることができなかった。これは特に大規模データセットやハイパーパラメータ探索において深刻な UX 問題だった。

## 2. この問題が発生する背景は?

**Callback 不在の歴史的背景**：

scikit-learn の設計哲學は「シンプルで一貫した API」を最優先してきた。`fit()`, `predict()`, `transform()` という統一インターフェースは、ライブラリの成功の核心である。しかし、このシンプルさの代償として、fit() の內部で何が起きているかを外部から観測する仕組みが存在しなかった。

具體的には以下のような狀況が日常的に発生していた：

- **GridSearchCV で 1000 通りのパラメータ組み合わせを試行**している際、全體の進捗がわからない。プログレスバーを表示するには `verbose` パラメータに頼るしかなく、カスタマイズは不可能だった。
- **LogisticRegression の LBFGS ソルバーが収束しない**場合、ユーザーは最終的な `n_iter_` 屬性を見るまでその事実に気づけない。早期停止の條件をカスタマイズする手段もなかった。
- **並列計算（n_jobs > 1）での進捗追跡**はさらに困難で、各ワーカープロセスの狀態を親プロセスから観測する標準的な方法がなかった。

**數値計算の課題背景**：

scikit-learn の多くの推定器は、內部で LAPACK/BLAS に依存する NumPy/SciPy の線形代數ルーチンを使用している。これらのルーチンは：

1. **大規模データでの數値的不安定性**：共分散行列の條件數が大きい場合、逆行列計算が精度を失う
2. **欠損値への非対応**：多くの推定器が欠損値を含むデータを受け付けず、前處理が必須だった
3. **CPU のみの実行**：GPU アクセラレーションが一部の推定器でのみ實驗的にサポートされていた

## 3. この技術/政策はどのようにその問題を解決するのか?

**Callback 機構の設計と実裝**：

scikit-learn 1.9 の callback 機構は、以下の設計原則に基づいている：

```
Callback のライフサイクル：
  on_fit_begin(estimator)         → 訓練開始時に呼ばれる
  on_fit_iter_end(estimator, ...)  → 各イテレーション終了時に呼ばれる
  on_fit_end(estimator)            → 訓練完了時に呼ばれる
```

この設計の核心的利點は **ネストされた追跡** である。Pipeline 內の各ステップ、GridSearchCV 內の各フォールドと各パラメータ組み合わせ、さらに並列ワーカー內の各イテレーションまで、階層的にコールバックが伝播する。

1.9 で callback が実裝された推定器：

| 推定器 | 用途 | callback の効果 |
|--------|------|----------------|
| LogisticRegression (LBFGS) | 分類 | イテレーション毎の損失と勾配ノルムを監視、早期停止 |
| GridSearchCV / RandomizedSearchCV | ハイパーパラメータ探索 | パラメータ組み合わせ毎のスコアと進捗を追跡 |
| Pipeline | ワークフロー | 各ステップの訓練進捗を階層的に監視 |
| StandardScaler | 前處理 | 統計量計算の進捗 |

ユーザーは以下のようにカスタムコールバックを定義できる：

```python
from sklearn.callbacks import Callback

class ProgressBarCallback(Callback):
    def on_fit_begin(self, estimator):
        self.bar = tqdm(total=estimator.max_iter)
    def on_fit_iter_end(self, estimator, **kwargs):
        self.bar.update(1)
        self.bar.set_postfix(loss=kwargs.get('loss', 'N/A'))
```

**數値計算の改善**：

1.9 では多くの推定器で內部アルゴリズムが改善された：

- **ソルバーの數値的安定性向上**：共分散行列の計算に正則化を追加し、悪條件問題での精度を改善
- **欠損値のネイティブ處理**：HistGradientBoosting 系の推定器で欠損値を特別なビンとして扱う機能が他の推定器にも拡張
- **GPU サポートの拡大**：一部の推定器で cuML や Array API 経由の GPU 実行が實驗的にサポート

**HTML 表示の強化**：

Jupyter Notebook での推定器表示が強化され、`fitted attributes`（學習済み係數、切片、クラスラベルなど）がクリック展開で閲覧可能になった。ColumnTransformer の表示も改善され、各カラムがどの変換器にルーティングされるかが視覚的に確認できる。

## 4. 類似の問題を解決する他の技術/フレームワーク/考え方は存在するか?

**Callback/訓練監視の代替アプローチ**：

| フレームワーク | 訓練監視の仕組み | scikit-learn との比較 |
|--------------|----------------|---------------------|
| Keras / TensorFlow | `tf.keras.callbacks.Callback` クラス | 最も成熟した callback システム。EarlyStopping, ModelCheckpoint, TensorBoard など豊富な組み込みコールバックを持つ。scikit-learn の設計はこれを參照している |
| PyTorch Lightning | `Callback` フック（on_train_start, on_train_batch_end 等） | より細粒度のフックを持つが、フレームワーク全體の採用が必要 |
| XGBoost / LightGBM | `evals_result` 辭書 + `verbose_eval` + カスタム目的関數 | callback より簡素だが、eval_set による學習曲線追跡が標準搭載 |
| MLflow / Weights & Biases | 外部ロギングツールによるメトリクス追跡 | ライブラリ非依存だが、fit() 內部の細粒度イベントには対応できない |

scikit-learn の callback 設計の獨自性は、**推定器非依存の統一インターフェース** と **ネストされた追跡の自動伝播** にある。Keras の callback は Keras モデル専用であり、PyTorch Lightning の callback は LightningModule 専用である。scikit-learn の callback は Pipeline, GridSearchCV, 任意の推定器の組み合わせで一貫して動作する。

**數値計算改善の代替アプローチ**：

| アプローチ | 代表ライブラリ | トレードオフ |
|-----------|-------------|------------|
| GPU 特化ライブラリ | cuML (RAPIDS), PyTorch | scikit-learn 互換 API を持つが、NVIDIA GPU 必須 |
| JIT コンパイル | JAX, Numba | パフォーマンスは高いが、scikit-learn の全推定器をカバーしない |
| 分散計算 | Dask-ML, Spark MLlib | 大規模データ向けだが、小中規模ではオーバーヘッドが大きい |
| Array API 標準 | PyTorch, CuPy, JAX の Array API 準拠 | scikit-learn 1.9 が實驗的にサポート。ハードウェア非依存の GPU 実行を可能にする |

scikit-learn の戦略は、CPU での數値的安定性を改善しつつ、Array API 経由で GPU サポートを段階的に導入するという二段構えである。これは、scikit-learn のユーザーベースの大多數が CPU 環境で動作しているという現実を反映している。
