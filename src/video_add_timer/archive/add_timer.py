import sys
import subprocess
import json
import datetime
from pathlib import Path

# --- 1. メタデータ取得関数 ---
def get_video_start_time(video_path):
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_entries', 'format_tags=creation_time', video_path
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
        
        # ここでは純粋なUTCのタイムスタンプ（数値）を返す
        return dt_utc.timestamp()

    except Exception as e:
        print(f"メタデータエラー: {e}")
        return None

# --- 2. タイムスタンプ焼き付け関数 ---
def add_timestamp_overlay(input_file, output_file, start_timestamp, font_path):
    
    # 日時を.と-で区切る。:はエラーが出やすい。
    time_fmt = "%Y.%m.%d %H-%M-%S"
    
    # JST対策
    # FFmpegのgmtimeはUTCを表示してしまうため、
    # 表示用に無理やり9時間(32400秒)を足した数値を渡す
    JST_OFFSET = 9 * 60 * 60  # 32400秒
    display_timestamp = int(start_timestamp + JST_OFFSET)
    
    # pts:gmtime:オフセット:フォーマット
    text_expr = f"%{{pts\\:gmtime\\:{display_timestamp}\\:{time_fmt}}}"
    
    filter_str = (
        f"drawtext=fontfile='{font_path}':"
        f"text='{text_expr}':"
        "fontsize=60:fontcolor=white:"
        "box=1:boxcolor=black@0.6:boxborderw=5:"
        "x=w-tw-50:y=h-th-50"
    )

    cmd = [
        'ffmpeg',
        '-y',
        '-i', input_file,
        '-t', '5',              # テスト用: 5秒のみ
        '-vf', filter_str,
        '-c:a', 'copy',
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        output_file
    ]

    print(f"変換中...")
    # 確認のため、コンソールには計算上のJST開始時間を表示
    dt_jst_check = datetime.datetime.fromtimestamp(start_timestamp + JST_OFFSET, datetime.timezone.utc)
    print(f"画面上の開始時間(JST): {dt_jst_check.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"完了: {output_file}")
    except subprocess.CalledProcessError:
        print("FFmpegエラー")

# --- メイン処理 ---
if __name__ == "__main__":
    video_dir = Path("../video_20251209")
    INPUT_VIDEO = video_dir / "GX010052.MP4"
    OUTPUT_VIDEO = Path("output_dot_jst.mp4")
    
    # フォントパス（Jetson用）
    FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    if not INPUT_VIDEO.exists():
        print(f"ファイルなし: {INPUT_VIDEO}")
        sys.exit(1)

    # UTCのタイムスタンプを取得
    start_ts = get_video_start_time(str(INPUT_VIDEO))

    if start_ts is not None:
        add_timestamp_overlay(str(INPUT_VIDEO), str(OUTPUT_VIDEO), start_ts, FONT_PATH)
    else:
        print("開始時刻が取得できませんでした")