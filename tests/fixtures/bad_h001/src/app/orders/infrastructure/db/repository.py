from sqlalchemy.orm import sessionmaker


class SqlOrderRepository:
    def __init__(self, sessions: sessionmaker) -> None:
        self._sessions = sessions
