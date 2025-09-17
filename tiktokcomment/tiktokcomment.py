import jmespath
from typing import Any, Dict, Iterator, List, Optional
from requests import Session, Response
from loguru import logger
from datetime import datetime
from .typing import Comments, Comment

class TiktokComment:
    BASE_URL: str = 'https://www.tiktok.com'
    API_URL: str = f'{BASE_URL}/api'

    def __init__(self: 'TiktokComment') -> None:
        self.__session: Session = Session()
        self.tiktok: Optional[str] = None

    def __convert_timestamp(self, timestamp: int) -> str:
        try:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except (TypeError, ValueError):
            return str(timestamp)

    def __parse_comment(self: 'TiktokComment', data: Dict[str, Any]) -> Optional[Comment]:
        if not data or 'cid' not in data or 'user' not in data:
            return None
        parsed_data: Dict[str, Any] = jmespath.search(
            """{
                comment_id: cid, username: user.unique_id,
                nickname: user.nickname, comment: text,
                create_time: create_time, avatar: user.avatar_thumb.url_list[0],
                total_reply: reply_comment_total, like_count: digg_count
            }""",
            data
        )
        if not parsed_data or not parsed_data.get('comment_id'): return None
        parsed_data['create_time'] = self.__convert_timestamp(parsed_data.get('create_time'))
        comment: Comment = Comment(
            **parsed_data,
            replies=list(
                self.get_all_replies(parsed_data.get('comment_id'))
            ) if parsed_data.get('total_reply') else []
        )
        logger.info(f"[{comment.create_time}] {comment.username}: {comment.comment} (Likes: {comment.like_count})")
        return comment

    def get_all_replies(self: 'TiktokComment', comment_id: str) -> Iterator[Comment]:
        page: int = 1
        while True:
            replies = self.get_replies(comment_id=comment_id, page=page)
            if not replies: break
            for reply in replies: yield reply
            page += 1

    def get_replies(self: 'TiktokComment', comment_id: str, size: int = 50, page: int = 1) -> List[Comment]:
        try:
            response: Response = self.__session.get(
                f'{self.API_URL}/comment/list/reply/',
                params={
                    'aid': 1988, 'comment_id': comment_id, 'item_id': self.tiktok,
                    'count': size, 'cursor': (page - 1) * size
                }
            )
            response.raise_for_status()
            comments_data = response.json().get('comments', [])
            return [parsed for comment in comments_data if (parsed := self.__parse_comment(comment)) is not None]
        except Exception as e:
            logger.error(f"Gagal mengambil balasan untuk comment_id {comment_id}: {e}")
            return []
    
    def get_all_comments(self: 'TiktokComment', tiktok: str) -> Comments:
        page: int = 1
        all_comments = []
        first_page_data: Optional[Comments] = self.get_comments(tiktok=tiktok, page=page)
        if not first_page_data or not first_page_data.comments:
            return first_page_data or Comments(comments=[], caption='', video_url='', has_more=False)
        all_comments.extend(first_page_data.comments)
        has_more_pages = first_page_data.has_more
        while has_more_pages:
            page += 1
            next_page_data: Optional[Comments] = self.get_comments(tiktok=tiktok, page=page)
            if not next_page_data or not next_page_data.comments: break
            all_comments.extend(next_page_data.comments)
            has_more_pages = next_page_data.has_more
        return Comments(
            comments=all_comments,
            caption=first_page_data.caption,
            video_url=first_page_data.video_url,
            has_more=False
        )

    def get_comments(self: 'TiktokComment', tiktok: str, size: int = 50, page: int = 1) -> Optional[Comments]:
        self.tiktok = tiktok
        try:
            response: Response = self.__session.get(
                f'{self.API_URL}/comment/list/',
                params={'aid': 1988, 'aweme_id': tiktok, 'count': size, 'cursor': (page - 1) * size}
            )
            response.raise_for_status()
            json_response = response.json()
        except Exception as e:
            logger.error(f"Gagal mengambil komentar utama untuk ID {tiktok}: {e}")
            return None
        
        comments_list = json_response.get('comments')
        metadata: Dict[str, Any] = jmespath.search(
            "{caption: comments[0].share_info.title, video_url: comments[0].share_info.url, has_more: has_more}",
            json_response
        ) or {}
        
        if not comments_list:
            logger.warning("Respons API tidak berisi 'comments'. Video mungkin privat atau komentar dinonaktifkan.")
            # REVISI: Ganti baris ini untuk menghindari argumen ganda
            return Comments(
                comments=[],
                caption=metadata.get('caption', 'Unknown Caption'),
                video_url=metadata.get('video_url', ''),
                has_more=False
            )

        return Comments(
            comments=[parsed for comment in comments_list if (parsed := self.__parse_comment(comment)) is not None],
            **metadata
        )
    
    def __call__(self: 'TiktokComment', tiktok: str) -> Comments:
        return self.get_all_comments(tiktok=tiktok)