from fastapi import APIRouter

products_router = APIRouter(
    prefix='/products',
    tags=['products'],
)


@products_router.get('/')
async def get_all_products():
    """Возвращает список всех товаров."""
    #TODO:

    return {'message': 'Список всех товаров (заглушка)'}


@products_router.post('/')
async def create_product():
    """Создаёт новый товар."""
    #TODO:

    return {'message': 'Товар создан (заглушка)'}


@products_router.get('/category/{category_id}')
async def get_products_by_category(category_id: int):
    """Возвращает список товаров в указанной категории по её ID."""
    #TODO:

    return {'message': f'Товары в категории {category_id} (заглушка)'}


@products_router.get('/{product_id}')
async def get_product(product_id: int):
    """Возвращает детальную информацию о товаре по его ID."""
    #TODO:

    return {'message': f'Детали товара {product_id} (заглушка)'}


@products_router.put('/{product_id}')
async def update_product(product_id: int):
    """Обновляет товар по его ID."""
    #TODO:

    return {'message': f'Товар {product_id} обновлён (заглушка)'}


@products_router.delete('/{product_id}')
async def delete_product(product_id: int):
    """Удаляет товар по его ID."""
    #TODO:

    return {'message': f'Товар {product_id} удалён (заглушка)'}
