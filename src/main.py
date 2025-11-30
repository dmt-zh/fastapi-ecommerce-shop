from fastapi import FastAPI

from src.routers import categories_router, products_router

app = FastAPI(
    title='FastAPI Интернет-магазин',
    version='0.1.0',
    debug=True,  # FIXME: delete after development
)

app.include_router(categories_router)
app.include_router(products_router)


@app.get("/")
async def root():
    """Корневой маршрут, подтверждающий, что API работает."""

    return {"message": "Добро пожаловать в API интернет-магазина!"}
