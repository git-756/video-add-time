import sys
import subprocess
import json
import datetime
from pathlib import Path

# --- 設定エリア ---
# ★本番処理を行うときはここを False にしてください★
TEST_MODE = False  

# 入力・出力ディレクトリの設定
INPUT_DIR_NAME = "original_videos"
OUTPUT_DIR_NAME = "processed_videos"

# Jetson用フォントパス
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
# ----------------

def get_video_start_time_utc(video_path):
    """ 動画からCreation Time(UTC)のタイムスタンプを取得 """
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_entries', 'format_tags=creation_time', str(video_path)
    ]
    try:
        result = subprocess.check_output(cmd)
        data = json.loads(result)
        tags = data.get('format', {}).get('tags', {})
        creation_time_str = tags.get('creation_time')

        if not creation_time_str:
            return None

        # 文字列からUTC時間を生成
        dt_utc = datetime.datetime.fromisoformat(creation_time_str.replace('Z', '+00:00'))
        return dt_utc.timestamp()

    except Exception as e:
        print(f"[{video_path.name}] メタデータ取得エラー: {e}")
        return None

def process_video(input_path, output_dir, font_path, is_test_mode):
    """ 1つの動画を処理して日時を焼き込み、日時ファイル名で保存する """
    
    # 1. 開始時間の取得
    start_ts_utc = get_video_start_time_utc(input_path)
    if start_ts_utc is None:
        print(f"スキップ: 日時が取得できませんでした -> {input_path.name}")
        return

    # 2. JST時間の計算 (UTC + 9時間)
    JST_OFFSET = 9 * 60 * 60
    start_ts_jst = start_ts_utc + JST_OFFSET
    
    # 日時オブジェクト(JST)を作成
    dt_jst = datetime.datetime.fromtimestamp(start_ts_jst, datetime.timezone.utc)

    # 3. 保存ファイル名の決定 (例: 2025-12-09_13-30-00.mp4)
    # ファイル名にはコロン(:)は使わないのが安全(Windows等との互換性のため)
    new_filename = dt_jst.strftime("%Y.%m.%d_%H-%M-%S.mp4")
    output_path = output_dir / new_filename

    # 重複回避: もし同名のファイルがあったら _1, _2 をつける
    counter = 1
    while output_path.exists():
        new_filename = dt_jst.strftime(f"%Y-%m-%d_%H-%M-%S_{counter}.mp4")
        output_path = output_dir / new_filename
        counter += 1

    # 4. FFmpegコマンド生成
    # 画面内表示フォーマット (ドット区切り: 13.30.00)
    display_fmt = "%Y-%m-%d %H.%M.%S"
    display_timestamp = int(start_ts_jst)
    
    # テキスト描写フィルタ
    text_expr = f"%{{pts\\:gmtime\\:{display_timestamp}\\:{display_fmt}}}"
    filter_str = (
        f"drawtext=fontfile='{font_path}':"
        f"text='{text_expr}':"
        "fontsize=60:fontcolor=white:"
        "box=1:boxcolor=black@0.6:boxborderw=5:"
        "x=w-tw-50:y=h-th-50"
    )

    cmd = [
        'ffmpeg',
        '-y',                  # 上書き許可
        '-i', str(input_path), # 入力
    ]

    # テストモードなら5秒で切る
    if is_test_mode:
        cmd.extend(['-t', '5'])

    cmd.extend([
        '-vf', filter_str,
        '-c:a', 'copy',        # 音声コピー
        '-c:v', 'libx264',     # 映像エンコード
        '-preset', 'ultrafast',# 高速設定
        str(output_path)       # 出力
    ])

    print(f"処理開始: {input_path.name} -> {output_path.name}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"完了しました。\n")
    except subprocess.CalledProcessError:
        print(f"エラー: {input_path.name} の変換に失敗しました。\n")

def main():
    # 実行場所(CWD)の取得
    base_dir = Path.cwd()
    
    # フォルダパスの設定 (スクリプト実行場所と同じ階層にある想定)
    # 必要に応じて ../original_videos などパスを調整してください
    input_dir = base_dir / INPUT_DIR_NAME
    output_dir = base_dir / OUTPUT_DIR_NAME

    # 入力フォルダチェック
    if not input_dir.exists():
        print(f"エラー: 入力フォルダが見つかりません: {input_dir}")
        print(f"作成して動画を入れてください: mkdir {INPUT_DIR_NAME}")
        return

    # 出力フォルダ自動作成
    if not output_dir.exists():
        output_dir.mkdir()
        print(f"出力フォルダを作成しました: {output_dir}")

    # フォントチェック
    if not Path(FONT_PATH).exists():
        print(f"警告: フォントが見つかりません ({FONT_PATH})。デフォルトフォントが使われます。")

    # 対象ファイルを取得 (.MP4 と .mp4 両対応)
    video_files = list(input_dir.glob("*.MP4")) + list(input_dir.glob("*.mp4"))
    
    if not video_files:
        print("処理対象の動画ファイル(.MP4)が見つかりませんでした。")
        return

    print(f"--- バッチ処理開始 ---")
    print(f"対象ファイル数: {len(video_files)}")
    print(f"保存先: {output_dir}")
    print(f"モード: {'【テスト(各5秒)】' if TEST_MODE else '【本番(全編)】'}")
    print("-" * 30)

    for video in video_files:
        process_video(video, output_dir, FONT_PATH, TEST_MODE)

    print("全ての処理が終了しました。")

if __name__ == "__main__":
    main()