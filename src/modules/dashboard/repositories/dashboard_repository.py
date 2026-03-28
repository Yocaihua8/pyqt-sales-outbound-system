from src.DataAccessObjects import db_facade as db_op


class DashboardRepository:
    @staticmethod
    def get_dashboard_summary():
        return db_op.get_dashboard_summary()
