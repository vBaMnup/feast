from fastapi import HTTPException, status


def create_db_error(operation: str, error_message: str) -> HTTPException:
    """
    Создает объект исключения для ошибок базы данных

    Args:
        operation: Описание операции, при которой произошла ошибка
        error_message: Сообщение об ошибке

    Returns:
        Объект HTTPException с соответствующим сообщением
    """
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Ошибка при {operation} столика: {error_message}",
    )
