from fastapi import HTTPException, status


def create_db_error(operation: str, error_message: str) -> HTTPException:
    """
    Create a custom HTTPException for database errors.

    Args:
        operation: The operation that caused the error.
        error_message: The error message.

    Returns:
        A custom HTTPException.
    """

    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Ошибка при {operation} столика: {error_message}",
    )
