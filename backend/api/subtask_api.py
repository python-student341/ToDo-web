from fastapi import Cookie, APIRouter
from sqlalchemy import select, delete

from schemas.schemas import SubToDoSchema
from models.models import SubToDoModel, ToDoModel
from database.database import session_dep
from database.hash import security

router = APIRouter()

#Add subtask
@router.post('/add_task/add_subtask/{id}', tags=['SubToDo'])
async def add_subtask(id: int, data: SubToDoSchema, session: session_dep, token: str = Cookie(None)):
    
    if not token:
        return {'success': False, 'message': 'No token'}

    payload = security._decode_token(token)
    user_id = int(payload.sub)
    todo_id = id

    todo = await session.get(ToDoModel, todo_id)
    if not todo or todo.user_id != user_id:
        return {'success': False, 'message': 'You can only change your own tasks'}

    new_subtask = SubToDoModel(
        todo_id=todo_id,
        task = data.task
    )

    session.add(new_subtask)
    await session.commit()

    return {'success': True, 'message': 'Subtask was added'}

#Get subtasks
@router.get('/get_subtasks', tags=['SubToDo'])
async def get_subtasks(id: int, session: session_dep, token: str = Cookie(None)):
    
    if not token:
        return {'success': False, 'message': 'No token'}

    payload = security._decode_token(token)
    user_id = int(payload.sub)
    todo_id = id

    subtask = await session.get(SubToDoModel, id)    
    if not subtask:
        return {'success': False, 'message': 'Task not found'}

    todo = await session.get(ToDoModel, subtask.todo_id)
    if not todo or todo.user_id != user_id:
        return {'success': False, 'message': 'You can only change your own tasks'}

    query = select(SubToDoModel).where(SubToDoModel.todo_id == todo_id)
    result = await session.execute(query)

    return result.scalars().all()

#Delete subtask
@router.delete('/delete_subtask/{id}', tags=['SubToDo'])
async def delete_subtask(id: int, session: session_dep, token: str = Cookie(None)):

    if not token:
        return {'success': False, 'message': 'No token'}

    payload = security._decode_token(token)
    user_id = int(payload.sub)
    todo_id = id

    subtask = await session.get(SubToDoModel, id)
    if not subtask:
        return {'success': False, 'message': 'Task not found'}

    todo = await session.get(ToDoModel, subtask.todo_id)
    if not todo or todo.user_id != user_id:
        return {'success': False, 'message': 'You can only change your own tasks'}

    deleted_subtask = delete(SubToDoModel).where(SubToDoModel.id == subtask.id)

    await session.execute(deleted_subtask)
    await session.commit()

    return {'success': True, 'message': 'Subtask was deleted'}

#Change/Update subtask
@router.put('/change_subtask/{id}', tags=['SubToDo'])
async def change_subtask(id: int, data: SubToDoSchema, session: session_dep, token: str = Cookie(None)):

    if not token:
        return {'success': False, 'message': 'No token'}

    payload = security._decode_token(token)
    user_id = int(payload.sub)
    todo_id = id

    subtask = await session.get(SubToDoModel, id)
    if not subtask:
        return {'success': False, 'message': 'Task not found'}

    todo = await session.get(ToDoModel, subtask.todo_id)
    if not todo or todo.user_id != user_id:
        return {'success': False, 'message': 'You can only change your own tasks'}

    query = select(SubToDoModel).where(SubToDoModel.id == id)
    result = await session.execute(query)
    db_subtask = result.scalar_one_or_none()

    db_subtask.task = data.task

    await session.commit()
    await session.refresh(db_subtask)

    return {'success': True, 'message': 'Task was changed/updated'}