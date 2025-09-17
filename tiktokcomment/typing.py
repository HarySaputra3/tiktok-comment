import json
from typing import Optional, List, Dict, Any

class Comment:
    def __init__(
        self: 'Comment',
        comment_id: str,
        username: str,
        nickname: str,
        comment: str,
        create_time: str,
        avatar: str,
        total_reply: int,
        like_count: int = 0,
        replies: Optional[List['Comment']] = None
    ) -> None:
        self._comment_id: str = comment_id
        self._username: str = username
        self._nickname: str = nickname
        self._comment: str = comment
        self._create_time: str = create_time
        self._avatar: str = avatar
        self._total_reply: int = total_reply
        self._like_count: int = like_count
        self._replies: List['Comment'] = replies if replies is not None else []

    @property
    def comment_id(self: 'Comment') -> str: return self._comment_id
    
    @property
    def username(self: 'Comment') -> str: return self._username
    
    @property
    def nickname(self: 'Comment') -> str: return self._nickname
    
    @property
    def comment(self: 'Comment') -> str: return self._comment
    
    @property
    def create_time(self: 'Comment') -> str: return self._create_time
    
    @property
    def avatar(self: 'Comment') -> str: return self._avatar
    
    @property
    def total_reply(self: 'Comment') -> int: return self._total_reply

    @property
    def like_count(self: 'Comment') -> int: return self._like_count
    
    @property
    def replies(self: 'Comment') -> List['Comment']: return self._replies
    
    @property
    def dict(self: 'Comment') -> Dict[str, Any]:
        return {
            'comment_id': self._comment_id,
            'username': self._username,
            'nickname': self._nickname,
            'comment': self._comment,
            'create_time': self._create_time,
            'avatar': self._avatar,
            'total_reply': self._total_reply,
            'like_count': self._like_count,
            'replies': [reply.dict for reply in self._replies]
        }
    
    @property
    def json(self: 'Comment') -> str:
        return json.dumps(self.dict, ensure_ascii=False)
    
    def __str__(self: 'Comment') -> str:
        return self.json

class Comments:
    def __init__(
        self: 'Comments',
        caption: str,
        video_url: str,
        comments: List[Comment],
        has_more: bool
    ) -> None:
        self._caption: str = caption
        self._video_url: str = video_url
        self._comments: List[Comment] = comments
        self._has_more: bool = has_more

    @property
    def caption(self: 'Comments') -> str: return self._caption
    
    @property
    def video_url(self: 'Comments') -> str: return self._video_url
    
    @property
    def comments(self: 'Comments') -> List[Comment]: return self._comments
    
    @property
    def has_more(self: 'Comments') -> bool: return self._has_more
    
    @property
    def dict(self: 'Comments') -> Dict[str, Any]:
        return {
            'caption': self._caption,
            'video_url': self._video_url,
            'comments': [comment.dict for comment in self._comments],
            'has_more': self._has_more  
        }
    
    @property
    def json(self: 'Comments') -> str:
        return json.dumps(self.dict, ensure_ascii=False)
    
    def __str__(self: 'Comments') -> str:
        return self.json