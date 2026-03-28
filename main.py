import sys
from PyQt6.QtWidgets import QApplication

from src.core.units import setup_logging
from src.DataAccessObjects.db_connections import DatabaseConnection
from src.DataAccessObjects.db_dao import OutboundDAO, UserDAO
from src.modules.auth.ui.login import LoginDialog
from src.modules.app.ui.main_window import MainWindow


class AppCoordinator:
    def __init__(self):
        self.logger = setup_logging()
        self.app = QApplication(sys.argv)

        self.db_conn = DatabaseConnection()
        self.outbound_dao = OutboundDAO(self.db_conn)
        self.user_dao = UserDAO(self.db_conn)

        self.main_window = None

    def run_login(self) -> bool:
        login_dlg = LoginDialog(self.user_dao)
        if login_dlg.exec() != LoginDialog.DialogCode.Accepted:
            return False

        current_user = login_dlg.current_user
        if not current_user:
            return False

        self.main_window = MainWindow(
            current_user=current_user,
            user_dao=self.user_dao,
            restart_login_callback=self.restart_login
        )
        self.main_window.show()
        return True

    def restart_login(self):
        if self.main_window:
            self.main_window.close()
            self.main_window.deleteLater()
            self.main_window = None

        if not self.run_login():
            self.app.quit()

    def run(self):
        if not self.run_login():
            self.logger.info("Login failed or cancelled.")
            self.db_conn.close()
            sys.exit(0)

        exit_code = self.app.exec()
        self.db_conn.close()
        sys.exit(exit_code)


def main():
    coordinator = AppCoordinator()
    coordinator.run()


if __name__ == '__main__':
    main()

