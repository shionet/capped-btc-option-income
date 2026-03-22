class AppError(Exception):
    pass


class UnsupportedExchangeError(AppError):
    pass


class LiveModeDisabledError(AppError):
    pass
