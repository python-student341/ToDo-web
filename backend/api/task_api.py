from fastapi import Cookie, APIRouter
from sqlalchemy import select, delete

from backend.schemas.schemas import ToDoSchema
from backend.models.models import ToDoModel
from backend.database.database import session_dep
from backend.database.hash import security

router = APIRouter()

#Add new task
@router.post('/add_task', tags=['ToDo'], summary='Add new task')
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
@router.get('/get_tasks', tags=['ToDo'], summary='Get all tasks for current user')
async def get_tasks(session: session_dep, token: str = Cookie(None)):
    if not token:
        return {'success': False, 'message': 'No token'}

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = select(ToDoModel).where(ToDoModel.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

#Delete task
@router.delete('/delete_task/{id}', tags=['ToDo'], summary='Delete current task')
async def delete_task(session: session_dep, id: int, token: str = Cookie(None)):
    if not token:
        return {'success': False, 'message': 'No token'}

    payload = security._decode_token(token)
    user_id = int(payload.sub)
    task = await session.get(ToDoModel, id)

    if not task:
        return {'success': False, 'message': 'Task not found'}

    if task.user_id != user_id:
        return {'success': False, 'message': 'You can only change your own tasks'}

    deleted_task = delete(ToDoModel).where(ToDoModel.id == id)

    await session.execute(deleted_task)
    await session.commit()

    return {'success': True, 'message': 'Task was deleted'}

@router.put('/change_task/{id}', tags=['ToDo'], summary='Change/Update current task')
async def change_task(id: int, data: ToDoSchema, session: session_dep, token: str = Cookie(None)):

    if not token:
        return {'success': False, 'message': 'No token'}

    naive_date = data.date.replace(tzinfo=None)

    payload = security._decode_token(token)
    user_id = int(payload.sub)
    task = await session.get(ToDoModel, id)

    if not task:
        return {'success': False, 'message': 'Task not found'}

    if task.user_id != user_id:
        return {'success': False, 'message': 'You can only change your own tasks'}

    query = select(ToDoModel).where(ToDoModel.id == id)
    result = await session.execute(query)
    db_task = result.scalar_one_or_none()

    db_task.task = data.task
    db_task.date = naive_date

    await session.commit()
    await session.refresh(db_task)

    return {'success': True, 'message': 'Task was changed/updated'}