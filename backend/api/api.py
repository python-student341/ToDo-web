from sqlalchemy import select, delete
from fastapi import Response, APIRouter, Cookie, HTTPException
from datetime import datetime

from backend.schemas.schemas import UserShema, UserLoginSchema, ToDoSchema
from backend.models.models import UserModel, ToDoModel
from backend.database.database import session_dep
from backend.database.hash import pwd_context, security, config, hashing_password

router = APIRouter()

#Login
@router.post('/login', tags=['Work with users'], summary='Login')
async def login(user: UserLoginSchema, session: session_dep, response: Response):
    query = select(UserModel).where(UserModel.email == user.email)
    result = await session.execute(query)
    db_user = result.scalar_one_or_none()

    if not db_user:
        return {'success': False, 'msg': 'User not found'}

    if not pwd_context.verify(user.password, db_user.password):
        return {'success': False, 'msg': 'Incorrect password'}

    token = security.create_access_token(uid=str(db_user.id))
    response.set_cookie(key=config.JWT_ACCESS_COOKIE_NAME, value=token, httponly=True, samesite='Lax', max_age=60*60)

    return {'success': True, 'message': 'Login successful', 'token': token}

#Add new user
@router.post('/users', tags=['Work with users'], summary='Add new user')
async def add_new_user(data: UserShema, session: session_dep):

    if data.password != data.repeat_password:
        raise HTTPException(status_code=400, detail="The passwords don't match")

    exiting_user = await session.execute(select(UserModel).where(UserModel.email == data.email))

    if exiting_user.scalar_one_or_none():
        raise HTTPException(status_code=409, detail='This email already exists in database')

    new_user = UserModel(
        email = data.email,
        name = data.name,
        password=hashing_password(data.password),
        age = data.age
    )

    session.add(new_user)
    await session.commit()
    return {'success': True, 'msg': 'New user was added', 'info': new_user}

#Get all users
@router.get('/users', tags=['Work with users'], summary='Get all users')
async def get_users(session: session_dep):
    query = select(UserModel)
    result = await session.execute(query)
    return result.scalars().all()

#Add new task
@router.post('/add_task')
async def add_task(data: ToDoSchema, session: session_dep, token: str = Cookie(None)):

    if not token:
        return {'success': False, 'msg': 'No token'}

    naive_date = data.date.replace(tzinfo=None)
    
    payload = security._decode_token(token)
    user_id = int(payload.sub)

    new_task = ToDoModel(
        user_id=user_id,
        task=data.task,
        date=naive_date
    )
    session.add(new_task)
    await session.commit()
    return {'success': True, 'message': 'New task was added', 'info': new_task}

#Get all tasks
@router.get('/get_tasks')
async def get_tasks(session: session_dep, token: str = Cookie(None)):
    if not token:
        return {'success': False, 'message': 'No token'}

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = select(ToDoModel).where(ToDoModel.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

@router.delete('/delet_task/{id}')
async def delete_task(session: session_dep, id: int, token: str = Cookie(None)):
    if not token:
        return {'success': False, 'message': 'No token'}

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    if not await session.get(ToDoModel, id):
        return {'success': False, 'message': 'Task not found'}

    deleted_task = delete(ToDoModel).where(ToDoModel.id == id)

    await session.execute(deleted_task)
    await session.commit()

    return {'success': True, 'message': 'Task was deleted'}

@router.put('/change_task/{id}')
async def change_task(id: int, data: ToDoSchema, session: session_dep, token: str = Cookie(None)):

    if not token:
        return {'success': False, 'message': 'No token'}

    naive_date = data.date.replace(tzinfo=None)

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    if not await session.get(ToDoModel, id):
        return {'success': False, 'message': 'Task not found'}

    query = select(ToDoModel).where(ToDoModel.id == id)
    result = await session.execute(query)
    db_task = result.scalar_one_or_none()

    db_task.task = data.task
    db_task.date = naive_date

    await session.commit()
    await session.refresh(db_task)

    return {'success': True, 'message': 'Task was changed/updated'}