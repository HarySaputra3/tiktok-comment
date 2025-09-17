import re
import os
import click
import csv
import json
from loguru import logger
from tiktokcomment.tiktokcomment import TiktokComment
from tiktokcomment.typing import Comments

__title__ = 'TikTok Comment Scrapper'
__version__ = '3.0.1 (Final, No Image)'

@click.command(help=__title__)
@click.version_option(version=__version__, prog_name=__title__)
@click.option(
    "--tiktok",
    help='ID video dari URL TikTok',
    required=True,
    callback=lambda _, __, value: match.group(0) if value and (match := re.match(r"^\d+$", value)) else None
)
@click.option(
    "--output",
    default='data/',
    help='Direktori untuk menyimpan hasil'
)
def main(tiktok: str, output: str):
    if not tiktok:
        raise ValueError('ID video tidak valid. Contoh: --tiktok 7550636537705237767')      
    
    logger.info(f"Memulai scrape komentar untuk TikTok ID: {tiktok}")

    comments: Comments = TiktokComment()(tiktok=tiktok)

    if not comments or not comments.comments:
        logger.warning(f"Tidak ada komentar yang ditemukan untuk TikTok ID: {tiktok}. Proses selesai.")
        return

    if not os.path.exists(output):
        os.makedirs(output)

    # Menulis file CSV
    csv_path = f"{output}{tiktok}.csv"
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Menghapus 'comment_image_url' dari header
            fieldnames = [
                'comment_id', 'parent_comment_id', 'username', 'nickname', 
                'comment_text', 'create_time', 'total_replies', 'like_count'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for comment in comments.comments:
                writer.writerow({
                    'comment_id': comment.comment_id, 'parent_comment_id': '',
                    'username': comment.username, 'nickname': comment.nickname,
                    'comment_text': comment.comment, 'create_time': comment.create_time,
                    'total_replies': comment.total_reply, 'like_count': comment.like_count
                })
                for reply in comment.replies:
                    writer.writerow({
                        'comment_id': reply.comment_id, 'parent_comment_id': comment.comment_id,
                        'username': reply.username, 'nickname': reply.nickname,
                        'comment_text': reply.comment, 'create_time': reply.create_time,
                        'total_replies': reply.total_reply, 'like_count': reply.like_count
                    })
        logger.info(f"Berhasil menyimpan CSV: {csv_path}")
    except Exception as e:
        logger.error(f"Gagal menulis file CSV: {e}")

    # Menulis file JSON
    json_path = f"{output}{tiktok}.json"
    try:
        with open(json_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(comments.dict, jsonfile, ensure_ascii=False, indent=4)
        logger.info(f"Berhasil menyimpan JSON: {json_path}")
    except Exception as e:
        logger.error(f"Gagal menulis file JSON: {e}")

if __name__ == '__main__':
    main()