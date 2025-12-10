import sys
import subprocess
import json
import datetime
from pathlib import Path

def check_metadata(video_path):
    video_path = str(video_path)
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_entries', 'format_tags=creation_time', video_path
    ]
    try:
        output = subprocess.check_output(cmd)
        data = json.loads(output)
        tags = data.get('format', {}).get('tags', {})
        creation_time = tags.get('creation_time')
        
        print(f"--- ファイル: {video_path} ---")
        if creation_time:
            print(f"メタデータ(UTC): {creation_time}")
            dt_utc = datetime.datetime.fromisoformat(creation_time.replace('Z', '+00:00'))
            dt_jst = dt_utc.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
            print(f"日本時間(JST): {dt_jst}")
            print(f"タイムスタンプ値: {dt_jst.timestamp()}")
            return True
        else:
            print("× creation_time が見つかりませんでした。")
            return False
    except Exception as e:
        print(f"エラー発生: {e}")
        return False

if __name__ == "__main__":
    # ここに対象の動画パスを指定
    target_video = Path("../video_20251209/GX010052.MP4")
    
    if target_video.exists():
        check_metadata(target_video)
    else:
        print("ファイルが見つかりません")