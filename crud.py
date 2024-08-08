from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, text

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
from models import DBPost, DBComment
import schemas
from profanity_chacker import check_for_profanity


async def create_post(db: AsyncSession, post: schemas.PostCreate, user_id: int):
    db_post = DBPost(**post.dict(), owner_id=user_id)
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post


async def get_posts(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(DBPost).offset(skip).limit(limit))
    return result.scalars().all()


async def create_comment(db: AsyncSession, comment: schemas.CommentCreate, user_id: int, is_blocked: bool):

    db_comment = models.DBComment(**comment.dict(), owner_id=user_id, is_blocked=is_blocked)
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment


async def get_comments(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(DBComment).offset(skip).limit(limit))
    return result.scalars().all()


async def delete_comment(db: AsyncSession, comment_id: int, user_id: int):
    result = await db.execute(select(models.DBComment).where(models.DBComment.id == comment_id))
    comment = result.scalars().first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    await db.delete(comment)
    await db.commit()
    return {"detail": "Comment deleted"}


async def get_comments_daily_breakdown(db: AsyncSession, date_from: datetime, date_to: datetime):
    # result = await db.execute(
    #     select(
    #         func.date(DBComment.created_at).label("date"),
    #         func.count(DBComment.id).label("total_comments"),
    #         func.sum(func.case([(DBComment.is_blocked == True, 1)], else_=0)).label("blocked_comments"),
    #     )
    #     .where(DBComment.created_at >= date_from, DBComment.created_at <= date_to)
    #     .group_by(func.date(DBComment.created_at))
    #     .order_by(func.date(DBComment.created_at))
    # )
    # return result.fetchall()
    query = text("""
            SELECT 
                date(comments.created_at) AS date, 
                count(comments.id) AS total_comments, 
                sum(case when comments.is_blocked = 1 then 1 else 0 end) AS blocked_comments
            FROM comments
            WHERE comments.created_at >= :date_from AND comments.created_at <= :date_to 
            GROUP BY date(comments.created_at) 
            ORDER BY date(comments.created_at)
        """)

    result = await db.execute(query, {'date_from': date_from, 'date_to': date_to})
    return result.fetchall()
