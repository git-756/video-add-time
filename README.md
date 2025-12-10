# Video Date Timer (動画撮影日時焼き込みツール)

動画ファイルのメタデータ（作成日時）を読み取り、その日時を動画の右下に字幕として焼き込むPythonスクリプトです。GoProなどのアクションカメラで撮影した動画を、撮影日時順に整理したり確認したりするのに役立ちます。

動画の開始時刻（UTC）を取得し、日本時間（JST）に変換してから、1秒ごとにカウントアップする現在時刻を画面にオーバーレイします。

---

## ✨ 主な機能

- **メタデータ自動取得**: `ffprobe` を使用して動画の `creation_time` タグを読み取ります。
- **正確な日時表示**: 動画のPTS（プレゼンテーションタイムスタンプ）を利用して、フレームごとに正確な日時を表示します。
- **一括バッチ処理**: 指定フォルダ内のすべての `.MP4` / `.mp4` ファイルを連続して処理します。
- **ファイル名自動変更**: 出力ファイル名を `YYYY.mm.dd_HH-MM-SS.mp4` の形式（日本時間）に自動変更し、ファイル管理を容易にします。

---

## ⚙️ 動作要件

- **Python 3.8 以上**
- **FFmpeg**: `ffmpeg` および `ffprobe` コマンドがシステムにインストールされ、パスが通っている必要があります。
    - Mac (Homebrew): `brew install ffmpeg`
    - Ubuntu/Debian: `sudo apt install ffmpeg`
- **フォント**: デフォルトでは `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf` を使用します。環境に合わせてスクリプト内のパスを変更してください。

---

## 🚀 使い方

1.  **リポジトリのクローン**
    ```bash
    git clone [リポジトリのURL]
    cd video-add-timer
    ```

2.  **ディレクトリの準備**
    - `original_videos` フォルダを作成し、処理したい動画ファイルを入れます。
    - `processed_videos` フォルダは自動的に作成されます。

3.  **スクリプトの設定（任意）**
    - `batch_add_timer.py` を開き、必要に応じて設定を変更します。
    ```python
    TEST_MODE = False  # Trueにすると最初の5秒だけ処理します（テスト用）
    FONT_PATH = "..."  # お使いの環境のフォントパスに合わせてください
    ```

4.  **スクリプトの実行**
    ```bash
    python batch_add_timer.py
    ```

5.  **結果の確認**
    - `processed_videos` フォルダに、日時が焼き込まれ、ファイル名が撮影日時に変更された動画が出力されます。

---

## 📜 ライセンス

このプロジェクトは **MIT License** のもとで公開されています。ライセンスの全文については、[LICENSE](LICENSE) ファイルをご覧ください。

## 作成者
[Samurai-Human-Go](https://samurai-human-go.com/%e9%81%8b%e5%96%b6%e8%80%85%e6%83%85%e5%a0%b1/)
- [ブログ記事: ](https://samurai-human-go.com)