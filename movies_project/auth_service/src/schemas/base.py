from fastapi import Query
from fastapi_pagination import Page


Page = Page.with_custom_options(
    page=Query(1, description='Номер страницы', ge=1),
    size=Query(50, description='Количество элементов', ge=1)
)
