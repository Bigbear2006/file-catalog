class RateLimitExceeded(Exception):
    def __init__(self, retry_after: int, blocked: bool = False):
        self.retry_after = retry_after
        self.blocked = blocked
        message = (
            'Клиент временно заблокирован за злоупотребление запросами.'
            if blocked
            else 'Превышена допустимая частота запросов.'
        )
        super().__init__(message)


class FileNotFound(Exception):
    def __init__(self, filename: str):
        self.filename = filename
        super().__init__(f'Файл {filename} отсутствует в каталоге')
