import copy
from datetime import datetime
from http import HTTPStatus

from aiogoogle import Aiogoogle
from fastapi import HTTPException

from app.core.config import settings
from app.models import CharityProject


FORMAT = '%Y/%m/%d %H:%M:%S'
ROW_COUNT = 100
COL_COUNT = 11
SHEET_ID = 0
PROPERTIES_TITLE = 'QRKot_отчёт_на_{now_date_time}'
SHEETS_TITLE = 'Лист1'
TABLE_HEAD = [
    ['Отчёт от', 'now_date_time']
]
TABLE_DESCRIPTION = [
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]

SPREADSHEET_BODY = {
    'properties': {
        'title': PROPERTIES_TITLE,
        'locale': 'ru_RU'
    },
    'sheets': [{
        'properties': {
            'sheetType': 'GRID',
            'sheetId': SHEET_ID,
            'title': 'Лист1',
            'gridProperties': {
                'rowCount': ROW_COUNT,
                'columnCount': COL_COUNT
            }
        }
    }]
}
ROW_COUNT_ERROR = (
    'В таблице не хватает строк, чтобы записать все данные.'
)


async def spreadsheets_create(
        wrapper_services: Aiogoogle,
        spreadsheet_body: dict = copy.deepcopy(SPREADSHEET_BODY)
) -> tuple[str, str]:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body['properties']['title'] = PROPERTIES_TITLE.format(
        now_date_time=now_date_time
    )
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    url = 'https://docs.google.com/spreadsheets/d/' + spreadsheet_id
    return spreadsheet_id, url


async def set_user_permissions(
        spreadsheetid: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email
    }
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetid,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        projects: list[CharityProject],
        wrapper_services: Aiogoogle,
        table_head: list[list] = copy.deepcopy(TABLE_HEAD)
) -> None:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    table_head[0][1] = str(now_date_time)
    update_body = {
        'majorDimension': 'ROWS',
        'values': [
            *table_head,
            *TABLE_DESCRIPTION,
            *[list(map(str, [
                project.name,
                project.close_date - project.create_date,
                project.description
            ])) for project in projects]
        ]
    }
    if len(update_body['values']) > ROW_COUNT:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ROW_COUNT_ERROR,
        )
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{ROW_COUNT}C{COL_COUNT}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
