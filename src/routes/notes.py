from fastapi import APIRouter

notes_router = APIRouter(
    prefix='/notes',
    tags=['notes'],
)

@notes_router.get('/')
async def get_all_notes() -> dict:
    """Возвращает список всех заметок."""
    # TODO:

    return {'message': 'Notes API is working'}
