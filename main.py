from datetime import datetime
from typing import List
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Depends, HTTPException, status, Response, Query
from fastapi_users import FastAPIUsers, router
from auth import auth_backend
from manager import get_user_manager, UserManager
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
import models
import schemas
from db import get_async_session, create_db_and_tables, engine
from models import Base
import crud
from profanity_chacker import check_for_profanity

app = FastAPI()


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(models.User, session)


fastapi_users = FastAPIUsers[models.User, int](
    get_user_manager,
    [auth_backend],
)


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(schemas.UserRead, schemas.UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(schemas.UserRead, schemas.UserCreate),
    prefix="/users",
    tags=["users"],
)


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/authenticated-route")
async def authenticated_route(user: models.User = Depends(fastapi_users.current_user(verified=True))):
    return {"message": f"Hello {user.email}"}


@app.get("/users/me/", response_model=schemas.UserRead)
async def read_users_me(current_user: schemas.UserRead = Depends(fastapi_users.current_user())):
    return current_user


@app.get("/posts/", response_model=List[schemas.PostRead])
async def read_posts(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_async_session)):
    posts = await crud.get_posts(db, skip=skip, limit=limit)
    return posts


@app.post("/posts/", response_model=schemas.PostRead)
async def create_post(post: schemas.PostCreate,
                      user: models.User = Depends(fastapi_users.current_user()),
                      db: AsyncSession = Depends(get_async_session)):
    db_post = await crud.create_post(db=db, post=post, user_id=user.id)
    return db_post


@app.get("/comments/", response_model=List[schemas.CommentRead])
async def read_comments(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_async_session)):
    comments = await crud.get_comments(db, skip=skip, limit=limit)
    return comments


@app.post("/comments/", response_model=schemas.CommentRead)
async def create_comment(comment: schemas.CommentCreate,
                         user: models.User = Depends(fastapi_users.current_user()),
                         db: AsyncSession = Depends(get_async_session)):
    is_blocked = await check_for_profanity(comment.content)
    db_comment = await crud.create_comment(db=db, comment=comment, user_id=user.id, is_blocked=is_blocked)
    if is_blocked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment contains profanity.")
    return db_comment


@app.delete("/comments/{comment_id}", response_model=dict)
async def delete_comment(comment_id: int,
                         user: models.User = Depends(fastapi_users.current_user()),
                         db: AsyncSession = Depends(get_async_session)):
    return await crud.delete_comment(db=db, comment_id=comment_id, user_id=user.id)


@app.get("/comments-daily-breakdown/")
async def comments_daily_breakdown(
    date_from: datetime = Query(...),
    date_to: datetime = Query(...),
    db: AsyncSession = Depends(get_async_session)
):

    return await crud.get_comments_daily_breakdown(db, date_from, date_to)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
