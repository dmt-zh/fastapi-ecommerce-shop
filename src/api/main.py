from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import get_settings
from src.routes import categories, products, reviews, users
from src.services.database.factory import make_database
from src.utils.misc import setup_logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Управляет жизненным циклом приложения FastAPI.

    Выполняет инициализацию ресурсов перед запуском приложения и их
    корректное освобождение при завершении работы.
    """
    app.state.settings = settings

    logger = setup_logger(debug=settings.api_debug)
    logger.info('Starting API...')

    database = await make_database(settings=settings, logger=logger)
    app.state.database = database
    logger.info('Database connected')
    logger.info('API ready!')
    yield

    await database.teardown()
    logger.info('API shutdown complete')


app = FastAPI(
    title=settings.api_service_name,
    version=settings.api_version,
    debug=settings.api_debug,
    lifespan=lifespan,
)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(reviews.router)
app.include_router(users.router)


@app.get('/')
async def root() -> dict[str, str]:
    """Корневой маршрут, подтверждающий, что API работает."""
    return {'message': 'Добро пожаловать в API интернет-магазина!'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        'src.api.main:app',
        port=8000,
        host='0.0.0.0',
        reload=True,
    )
