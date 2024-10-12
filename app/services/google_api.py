import copy
from datetime import datetime

from aiogoogle import Aiogoogle
from aiogoogle.excs import AiogoogleError

from app.core.config import settings
from app.models import CharityProject


FORMAT = '%Y/%m/%d %H:%M:%S'
ROW_COUNT = 100
COL_COUNT = 11
SHEET_ID = 0
PROPERTIES_TITLE = f'QRKot_отчёт_на_{datetime.now().strftime(FORMAT)}'
SHEETS_TITLE = 'Лист1'
TABLE_HEAD = [
    ['Отчёт от', str(datetime.now().strftime(FORMAT))]
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
SPREADSHEET_UPDATE_ERROR = (
    'Ошибка при заполнении таблицы данными: {error}'
)


async def spreadsheets_create(
        wrapper_services: Aiogoogle,
        spreadsheet_body: dict = SPREADSHEET_BODY
) -> tuple[str, str]:
    spreadsheet_body = copy.deepcopy(spreadsheet_body)
    service = await wrapper_services.discover('sheets', 'v4')
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    return response['spreadsheetId'], response['spreadsheetUrl']


async def set_user_permissions(
        spreadsheet_id: str,
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
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        projects: list[CharityProject],
        wrapper_services: Aiogoogle,
        table_head: list[list] = TABLE_HEAD
) -> None:
    table_head = copy.deepcopy(table_head)
    service = await wrapper_services.discover('sheets', 'v4')
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
    current_col_count = max([
        len(item) for item in update_body['values']
    ])
    current_row_count = len(update_body['values'])
    try:
        await wrapper_services.as_service_account(
            service.spreadsheets.values.update(
                spreadsheetId=spreadsheet_id,
                range=f'R1C1:R{current_row_count}C{current_col_count}',
                valueInputOption='USER_ENTERED',
                json=update_body
            )
        )
    except AiogoogleError as error:
        raise ValueError(
            SPREADSHEET_UPDATE_ERROR.format(error=error)
        )
