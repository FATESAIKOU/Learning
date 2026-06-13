# 02. Java Weekly Issue 650

**Source**: https://feeds.feedblitz.com/~/957980303/0/baeldung
**Author**: Baeldung (curated weekly digest)
**Date**: 2026-06-13
**Category**: 傳統IT技術

## 1. この技術/政策は何を解決するのか?

Java Weekly Issue 650 が取り上げる二つの主要トピックは、それぞれ異なる課題を解決する。

**JEP 538: PEM Encodings of Cryptographic Objects (3rd Preview)** は、Java プラットフォームにおける暗號鍵管理の相互運用性問題を解決する。従來、Java で PEM 形式（Privacy-Enhanced Mail）の鍵や証明書を扱うには、Bouncy Castle などのサードパーティライブラリが必須だった。JEP 538 は JDK 標準 API として PEM エンコード/デコードを提供し、以下の課題を解消する：

| 課題 | JEP 538 による解決 |
|------|-------------------|
| サードパーティ依存 | `java.security` パッケージ內で完結 |
| フォーマット斷片化 | PEM, PKCS#8, X.509 を統一 API で扱う |
| クラウドネイティブとの乖離 | Kubernetes Secrets, AWS KMS などが出力する PEM 形式を直接読み込み |

**Spring AI エージェントの単一ランタイム戦略**（foojay.io 記事）は、AI エージェント実行に専用のセカンドランタイム（Python や Node.js の別プロセス）を導入することの運用複雜性を解決する。Spring チームは、Spring Boot アプリケーションの JVM プロセス內で AI エージェントを完結させるアーキテクチャを提唱している。

## 2. この問題が発生する背景は?

**PEM エンコード標準化の背景**：

PEM 形式は RFC 7468 で規定されるテキストベースの暗號鍵表現であり、`-----BEGIN CERTIFICATE-----` のようなヘッダ/フッタで囲まれた Base64 エンコードデータである。この形式は以下の理由で Java エコシステムにおける重要性が急増した：

1. **クラウドネイティブ環境でのデファクト標準化**：Kubernetes Secrets、Docker の TLS 設定、クラウドプロバイダのマネージド証明書サービスは、ほぼ全て PEM 形式で鍵を出力する。Java アプリケーションがこれらの鍵を読み込むたびに Bouncy Castle や手製のパーサが必要だった。

2. **マイクロサービス間 TLS の普及**：サービスメッシュ（Istio, Linkerd）や mTLS の普及により、Java マイクロサービスが PEM 形式の証明書をプログラム的に扱う頻度が激増した。

3. **既存 API の制限**：JDK の `KeyStore` API は JKS/PKCS#12 形式を前提としており、PEM ファイルを直接読み込めない。`CertificateFactory` は X.509 証明書の単體読み込みは可能だが、秘密鍵や PKCS#8 形式には対応していなかった。

JEP 538 は JDK 22（2024/03）で初回プレビュー、JDK 24（2025/03）で 2nd プレビューを経て、JDK 27 で 3rd プレビューとして継続されている。これは Preview API のフィードバックサイクルを活用し、API の安定化を慎重に進めていることを示す。

**Spring AI 単一ランタイム戦略の背景**：

AI エージェントを Java アプリケーションに統合する際、多くの開発者は Python エコシステム（LangChain, LlamaIndex）の豊富なツール群に引き寄せられ、Java プロセスとは別の Python サイドカーを立てるアーキテクチャを選択しがちである。しかしこのアプローチには以下の問題がある：

- **プロセス間通信のオーバーヘッド**：REST/gRPC 経由の呼び出しはレイテンシを増加させる
- **デプロイの二重化**：JVM と Python の両方のランタイムをコンテナにパッケージングする必要がある
- **観測可能性の斷片化**：トレーシング、メトリクス、ログが二つの獨立したプロセスに分散する
- **エラーハンドリングの複雜化**：一方のプロセスの障害が他方に伝播する際の処理が複雑になる

Spring AI 2.0.0 GA（2026/06/12 リリース）は、Spring Boot 4.0 / Spring Framework 7.0 をベースラインとし、JSpecify による Null-safety、Jackson 3 による JSON シリアライゼーション改善、および AI モデル統合のための一貫した抽象化レイヤーを提供する。この基盤の上で、AI エージェントを JVM 內で完結させる戦略が現実的になった。

## 3. この技術/政策はどのようにその問題を解決するのか?

**JEP 538 の技術的アプローチ**：

JEP 538 は `java.security` パッケージに以下の新しいクラスとメソッドを追加する（3rd Preview での安定化が見込まれる）：

```
PEMParser       → PEM テキストを解析し、PEMObject のストリームを生成
PEMObject       → ラベル（CERTIFICATE, PRIVATE KEY 等）と Base64 データのペア
PEMEncoder       → 暗號オブジェクトを PEM テキストに変換
KeyFactory       → 既存クラスに PEM 鍵からの生成メソッドを追加
CertificateFactory → 既存クラスに PEM 証明書からの生成メソッドを追加
```

これにより、以下のようなコードが標準 API のみで実現できる：

```java
// PEM ファイルから秘密鍵と証明書を読み込む
Path keyPath = Path.of("/etc/secrets/tls.key");
Path certPath = Path.of("/etc/secrets/tls.crt");

PrivateKey key = KeyFactory.getInstance("RSA")
    .generatePrivate(PEMParser.parse(keyPath));
X509Certificate cert = CertificateFactory.getInstance("X.509")
    .generateCertificate(PEMParser.parse(certPath));
```

この API は Kubernetes の `Secret` マウントやクラウドプロバイダの証明書サービスと直接統合でき、Bouncy Castle 依存を除去する。

**Spring AI 単一ランタイム戦略のアプローチ**：

Spring AI 2.0.0 は以下の設計原則で単一ランタイムを実現する：

1. **統一された ChatClient 抽象**：OpenAI, Anthropic, Google Gemini, AWS Bedrock など複數の AI プロバイダを同一インターフェースで扱う。プロバイダ切り替えは設定変更のみで完結する。

2. **Tool Calling の標準化**：`@Tool` アノテーションで Spring Bean のメソッドを AI エージェントのツールとして公開する。エージェントは JVM 內で直接 Bean を呼び出すため、プロセス間通信が発生しない。

3. **Spring Boot 4 の Null-safety 基盤**：JSpecify アノテーションにより、AI モデルからの不確実な応答（null フィールドを含む JSON）を型安全に処理する。

4. **Jackson 3 による JSON 処理の効率化**：AI モデルとの JSON ベースの通信が Spring AI の中核であるため、Jackson 3 のパフォーマンス改善とカスタマイズ性が直接的な恩恵をもたらす。

## 4. 類似の問題を解決する他の技術/フレームワーク/考え方は存在するか?

**PEM エンコードの代替アプローチ**：

| アプローチ | 具體的手段 | 評価 |
|-----------|-----------|------|
| Bouncy Castle | `PEMParser` / `PEMWriter` クラス | 事実上の標準。機能は豊富だが依存が重い（~4MB） |
| 手製パーサ | Base64 デコード + 正規表現 | メンテナンス負荷が高い。エッジケースに弱い |
| PKCS#12 への事前変換 | `openssl pkcs12 -export` で変換 | 運用フローに追加ステップが発生 |
| 他言語の標準 API | Go `crypto/x509`, Rust `rustls-pemfile` | Go/Rust は標準ライブラリで PEM を扱える。Java が遅れていた分野 |

JEP 538 の意義は、Java を Go や Rust と同等の「標準ライブラリで PEM を扱える言語」に引き上げる點にある。

**AI エージェント統合の代替アプローチ**：

| アプローチ | 代表実裝 | 長所 | 短所 |
|-----------|---------|------|------|
| Python サイドカー | LangChain + FastAPI を別コンテナで実行 | Python AI エコシステムの全ツールを利用可能 | 二重デプロイ、プロセス間通信レイテンシ |
| gRPC ブリッジ | Java ↔ Python gRPC サーバー | 型安全な契約 | プロトコル定義の維持コスト |
| GraalVM Polyglot | GraalVM 上で Python を実行 | 単一プロセス | GraalVM の採用障壁、Python C 拡張の互換性問題 |
| WebAssembly サンドボックス | WASM ランタイムで AI 推論 | ポータブル | パフォーマンスオーバーヘッド |
| Spring AI 単一ランタイム | Spring AI 2.0.0 + Tool Calling | 運用簡單、観測可能性が統一 | Python エコシステムの全ツールは使えない |

Spring AI の単一ランタイム戦略は、特にエンタープライズ Java 組織にとって魅力的である。これらの組織は既に Spring Boot を標準フレームワークとして採用しており、運用チームが JVM の監視・デプロイに習熟している。Python サイドカーを追加することは、運用チームに新しいスキルセットと監視ツールを要求することを意味する。

ただし、この戦略は Python エコシステムの急速なイノベーション（新しい埋め込みモデル、ベクトルストア、エージェントフレームワーク）への追従速度では劣後するリスクがある。Spring AI チームはコミュニティ貢獻とロードマップの透明性によってこのギャップを埋める戦略を取っている。
