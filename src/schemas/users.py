
from pydantic import BaseModel, ConfigDict, EmailStr, Field

##############################################################################################

class User(BaseModel):
    """Модель для ответа с данными пользователя. Используется в GET-запросах."""

    id: int
    email: EmailStr
    is_active: bool
    role: str
    model_config = ConfigDict(from_attributes=True)

##############################################################################################

class UserCreate(BaseModel):
    """Модель для создания и обновления пользователя. Используется в POST и PUT запросах."""

    email: EmailStr = Field(description='Email пользователя')
    password: str = Field(min_length=5, description='Пароль (минимум 8 символов)')
    role: str = Field(default='buyer', pattern='^(buyer|seller|admin)$', description='Роль: "admin", "buyer" или "seller"')

##############################################################################################
