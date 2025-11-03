from sqlalchemy import select, delete
from fastapi import Response, APIRouter, Cookie, HTTPException
from datetime import datetime

from schemas.schemas import UserSchema, UserLoginSchema, PasswordSchema, UserDeleteSchema, UserNameSchema
from models.models import UserModel, ToDoModel, SubToDoModel
from database.database import session_dep
from database.hash import pwd_context, security, config, hashing_password


router = APIRouter()


#Add new user
@router.post('/users/add_new_user', tags=['Users'], summary='Add new user')
async def add_new_user(data: UserSchema, session: session_dep):

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


#Login
@router.post('/users/login', tags=['Users'], summary='Login')
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


#Get all users
@router.get('/users/get_all_users', tags=['Users'], summary='Get all users')
async def get_users(session: session_dep, password: str):
    if password != 'super_password':
        return {'success': False, 'message': 'Not enough rights'}

    query = select(UserModel)
    result = await session.execute(query)

    return result.scalars().all()


#Change password
@router.put('/users/change_password/{id}', tags=['Users'])
async def change_password(id: int, data: PasswordSchema, session: session_dep, token: str = Cookie(None)):

    if not token:
        return {'success': False, 'message': 'No token'}

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    if user_id != id:
        return {'success': False, 'message': 'You can only change your own data'}

    query = select(UserModel).where(UserModel.id == id)
    result = await session.execute(query)
    db_old_password = result.scalar_one_or_none()

    if not pwd_context.verify(data.old_password, db_old_password.password):
        return {'success': False, 'msg': 'Incorrect password'}

    if data.new_password != data.repeat_new_password:
        return {'success': False, 'message': "The passwords don't match"}

    db_old_password.password = hashing_password(data.new_password)

    await session.commit()
    await session.refresh(db_old_password)
        
    return {'success': True, 'message': 'Password was changed'}


#Change name
@router.put('/users/change_name/{id}', tags=['Users'])
async def change_name(data: UserNameSchema, id: int, session: session_dep, token: str = Cookie(None)):
    
    if not token:
        return {'success': False, 'message': 'No token'}

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = select(UserModel).where(UserModel.id == id)
    result = await session.execute(query)
    db_user = result.scalar_one_or_none()

    if not pwd_context.verify(data.password, db_user.password):
        return {'success': False, 'message': 'Incorrect password'}

    db_user.name = data.name

    await session.commit()
    await session.refresh(db_user)

    return {'success': True, 'message': 'Name was changed'}


#Delete user
@router.delete('/users/delete_user/{id}', tags=['Users'])
async def delete_user(data: UserDeleteSchema, id: int, session: session_dep, token: str = Cookie(None)):

    if not token:
        return {'success': False, 'message': 'No token'}

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    if not await session.get(UserModel, id):
        return {'success': False, 'message': 'User not found'}

    if user_id != id:
        return {'success': False, 'message': 'You can only change your own data'}

    delete_all_subtasks = delete(SubToDoModel).where(SubToDoModel.todo_id.in_(select(ToDoModel.id).where(ToDoModel.user_id == id)))
    await session.execute(delete_all_subtasks)
    await session.commit()

    delete_all_tasks = delete(ToDoModel).where(ToDoModel.user_id == id)
    await session.execute(delete_all_tasks)
    await session.commit()

    query = select(UserModel).where(UserModel.id == id)
    result = await session.execute(query)
    db_password = result.scalar_one_or_none()

    if not pwd_context.verify(data.password, db_password.password):
        return {'success': False, 'message': 'Incorrect password'}

    deleted_user = delete(UserModel).where(UserModel.id == id)

    await session.execute(deleted_user)
    await session.commit()

    return{'success': True, 'message': 'User was deleted'}