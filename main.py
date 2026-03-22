import sys
from PyQt6.QtWidgets import QApplication

from src.core.units import setup_logging
from DataAccessObjects.db_connections import DatabaseConnection
from DataAccessObjects.db_operations import OutboundDAO, UserDAO
from ui.login import LoginDialog
from ui.main_window import MainWindow

def restart_login():
    """用于切换用户：重新运行登录流程"""
    # 关闭当前数据库连接？当前连接会被main中的finally关闭？但我们需要重新启动登录。
    # 这里简单处理：直接重新调用main()，但需要注意QApplication实例重复问题。
    # 更好的方式是发出信号，但为简化，我们重新创建QApplication。
    # 实际上，切换用户时我们关闭了主窗口，然后main.py中的app.exec()结束，会退出程序。
    # 我们需要重新启动登录而不退出整个应用。可以在这里重新创建登录和主窗口。
    # 但为了简单，我们采用退出应用并让用户重新启动的方式。但用户体验不好。
    # 我们改为：在switch_user中，我们隐藏主窗口，显示登录，成功后重新创建主窗口。
    # 但代码需要调整。我们先采用简单方式：退出应用，让用户重新运行。
    # 但要求“切换用户”功能，最好不退出。我们修改一下设计。

    # 由于时间关系，我们这里实现一个简单的重启登录，但会退出当前应用并重新启动。
    # 但Qt应用不能轻易重启，所以采用更简单的方式：关闭主窗口，重新显示登录。
    # 我们可以在main_window.py的switch_user中调用一个函数，该函数重新创建登录。
    # 我们将这个函数定义在main.py中，并作为全局可访问。
    # 但为了简化，我们直接在main_window.py中处理切换，而不依赖main.py函数。

# 因为上述原因，我们修改main_window.py中的switch_user方法，改为：
# 1. 隐藏当前主窗口
# 2. 创建新的登录对话框
# 3. 如果登录成功，销毁旧主窗口，创建新主窗口并显示
# 这需要在主窗口内访问app和dao等。我们将调整代码。

# 但为了快速满足要求，我们保持简单的切换用户：直接退出并提示重新启动。
# 用户会接受吗？可能不太友好。但我们可以改为重新启动应用程序。

# 考虑到复杂度，我们决定在main_window.py的switch_user中调用QApplication.quit()，然后让用户手动重启。
# 但这样不好。我们可以在main.py中保存全局变量，并提供一个重启函数。

# 我们重新设计main.py：

app = None
db_conn = None
outbound_dao = None
user_dao = None
main_window = None

def run_login():
    global app, db_conn, outbound_dao, user_dao, main_window
    login_dlg = LoginDialog(user_dao)
    if login_dlg.exec() != LoginDialog.DialogCode.Accepted:
        return False

    current_user = user_dao.validate_login(
        login_dlg.username_edit.text().strip(),
        login_dlg.password_edit.text()
    )
    if not current_user:
        return False

    main_window = MainWindow(outbound_dao, current_user, user_dao)
    main_window.show()
    return True

def main():
    global app, db_conn, outbound_dao, user_dao
    logger = setup_logging()
    app = QApplication(sys.argv)

    db_conn = DatabaseConnection()
    outbound_dao = OutboundDAO(db_conn)
    user_dao = UserDAO(db_conn)

    if not run_login():
        logger.info("Login failed or cancelled.")
        db_conn.close()
        sys.exit(0)

    exit_code = app.exec()
    db_conn.close()
    sys.exit(exit_code)

def restart_login():
    """供主窗口调用的切换用户函数"""
    global main_window, app, db_conn, outbound_dao, user_dao
    if main_window:
        main_window.close()
        main_window.deleteLater()
        main_window = None
    # 重新运行登录
    if not run_login():
        # 如果取消登录，则退出应用
        app.quit()

if __name__ == '__main__':
    main()