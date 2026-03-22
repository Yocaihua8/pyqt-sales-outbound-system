# 进销存管理系统 / Inventory Management System

一个基于 **Python + PyQt6 + SQLite** 开发的桌面端进销存管理系统，面向中小型业务场景下的登录认证、仪表盘、基础资料维护、销售出库、采购入库、库存管理、商品管理、仓库管理、用户管理等业务流程。

An inventory management desktop application built with **Python + PyQt6 + SQLite**, designed for small business scenarios including authentication, dashboard, master data maintenance, sales outbound, purchase inbound, stock management, product management, warehouse management, and user management.

---

## 项目简介 / Project Overview

本项目是我独立开发的桌面应用项目，目标是实现一个可运行、可维护、可逐步扩展的进销存管理系统。

当前版本已覆盖登录、首页仪表盘、公司与客户资料管理、销售出库、采购入库、库存管理、商品管理、仓库管理、用户管理等核心模块，并持续推进代码分层重构，将原本集中在 UI 层的业务逻辑逐步拆分到 `services` 与 `repositories` 层，以提升系统的可维护性、复用性与后续扩展能力。

This is an independently developed desktop application project aimed at building a practical, maintainable, and extensible inventory management system.

The current version already includes core modules such as login, dashboard, company/customer data management, sales outbound, purchase inbound, stock management, product management, warehouse management, and user management. The project is also under continuous layered refactoring to move business logic out of the UI layer into `services` and `repositories` for better maintainability, reusability, and scalability.

---

## 技术栈 / Tech Stack

- **Python**
- **PyQt6**
- **SQLite**

---

## 核心功能 / Main Features

### 中文
- 用户登录与认证
- 首页仪表盘数据展示
- 公司资料与客户资料维护
- 销售出库单录入、保存、查询、详情查看、重新打印
- 采购入库业务页与入库管理
- 库存查询与库存相关服务拆分
- 商品管理
- 仓库管理
- 用户管理
- 基础资料管理
- 打印与打印预览支持
- `services / repositories / ui` 分层重构

### English
- User login and authentication
- Dashboard data display
- Company and customer master data maintenance
- Sales outbound entry, saving, querying, detail viewing, and reprint support
- Purchase inbound workflow and inbound management
- Stock query and stock-related service refactoring
- Product management
- Warehouse management
- User management
- Basic information management
- Printing and print preview support
- Layered refactoring across `services / repositories / ui`

---

## 项目结构 / Project Structure

```text
pyqt-sales-outbound-system
├─ config/                           # 外部配置文件
│  └─ company_profile.json
├─ src/
│  ├─ DataAccessObjects/             # 数据库连接与底层 DAO 操作
│  ├─ config/                        # 页面字段与内部配置
│  ├─ controllers/                   # 控制器层
│  ├─ core/                          # 核心常量、模型、单位等
│  ├─ repositories/                  # 数据访问抽象层
│  │  ├─ auth_repository.py
│  │  ├─ dashboard_repository.py
│  │  ├─ inbound_repository.py
│  │  ├─ outbound_repository.py
│  │  ├─ product_repository.py
│  │  ├─ sales_order_repository.py
│  │  ├─ sales_outbound_repository.py
│  │  ├─ stock_repository.py
│  │  ├─ user_repository.py
│  │  └─ warehouse_repository.py
│  ├─ services/                      # 业务服务层
│  │  ├─ auth_service.py
│  │  ├─ basic_info_service.py
│  │  ├─ company_archive_service.py
│  │  ├─ company_profile_service.py
│  │  ├─ customer_archive_service.py
│  │  ├─ dashboard_service.py
│  │  ├─ document_form_service.py
│  │  ├─ document_page_state_service.py
│  │  ├─ document_table_service.py
│  │  ├─ inbound_page_service.py
│  │  ├─ inbound_service.py
│  │  ├─ main_window_navigation_service.py
│  │  ├─ outbound_page_service.py
│  │  ├─ outbound_service.py
│  │  ├─ product_service.py
│  │  ├─ sales_order_list_service.py
│  │  ├─ sales_outbound_printer.py
│  │  ├─ sales_outbound_service.py
│  │  ├─ stock_service.py
│  │  ├─ user_service.py
│  │  └─ warehouse_service.py
│  └─ ui/                            # UI 界面层
│     ├─ base_document_page.py
│     ├─ basic_info_page.py
│     ├─ company_info_page.py
│     ├─ customer_info_page.py
│     ├─ dashboard_page.py
│     ├─ inbound_manager.py
│     ├─ login.py
│     ├─ main_window.py
│     ├─ outbound_manager.py
│     ├─ product_manager.py
│     ├─ sales_order_list_page.py
│     ├─ sales_outbound_page.py
│     ├─ sales_outbound_query_page.py
│     ├─ stock_manager.py
│     ├─ user_manager.py
│     └─ warehouse_manager.py
├─ main.py                           # 程序入口
└─ requirements.txt                  # 项目依赖
```

---

## 当前开发与重构进展 / Development & Refactoring Progress

目前项目已经从“单一销售出库页实现”逐步扩展为一个包含多业务页面的进销存系统原型，并持续进行分层重构。

当前已推进的方向包括：

- 将认证、仪表盘、出入库、库存、商品、仓库、用户等模块拆分到独立的 `service` 与 `repository`
- 抽离公司信息相关逻辑到 `company_profile_service`
- 抽离销售出库业务逻辑到 `sales_outbound_service`
- 新增入库页、库存页、基础资料页等配套业务服务
- 引入 `base_document_page` 与文档页相关服务，提升页面复用性
- 独立打印逻辑到 `sales_outbound_printer`
- 为后续继续扩展入库单、单据骨架复用、多资料档案管理做准备

The project has evolved from a single sales-outbound implementation into a broader inventory management system prototype, while continuing its layered refactoring.

Current progress includes:

- Splitting authentication, dashboard, inbound/outbound, stock, product, warehouse, and user modules into dedicated `service` and `repository` layers
- Extracting company profile logic into `company_profile_service`
- Extracting sales outbound logic into `sales_outbound_service`
- Adding supporting services for inbound pages, stock pages, and master-data pages
- Introducing `base_document_page` and document-related services for better page reuse
- Isolating printing logic into `sales_outbound_printer`
- Preparing for further expansion of inbound documents, reusable document-page skeletons, and multi-archive data management

---

## 运行方式 / How to Run

### 1. 安装依赖 / Install dependencies
```bash
pip install -r requirements.txt
```

### 2. 启动项目 / Run the application
```bash
python main.py
```

---

## 说明 / Notes

### 中文
- 仓库中不包含运行生成的数据库文件时，首次运行可能需要根据数据库逻辑自动建表
- 本地 IDE 配置、缓存文件、日志文件已通过 `.gitignore` 排除
- 若后续继续扩展模块，建议保持 `ui -> service -> repository -> dao` 的分层模式
- 当前项目重点在于桌面端业务流程实现与结构重构，而不是前后端分离架构

### English
- If runtime database files are excluded, tables may need to be created automatically on first run
- Local IDE files, cache files, and logs are ignored through `.gitignore`
- Future modules should continue following the `ui -> service -> repository -> dao` layering pattern
- The current focus of the project is desktop business workflow implementation and structural refactoring rather than frontend-backend separation

---

## 个人贡献 / My Contribution

### 中文
这是我的独立开发项目，我负责了从需求梳理、功能设计到代码实现与结构重构的完整流程，包括：

- 系统功能设计与模块划分
- PyQt6 界面开发
- SQLite 数据集成
- 销售出库、采购入库、库存管理等业务页开发
- 公司/客户资料管理功能实现
- 打印与打印预览流程实现
- `services / repositories / ui` 分层重构
- 页面复用骨架与单据页通用能力整理

### English
This is an independently developed project. I was responsible for the full lifecycle from requirement breakdown and feature design to implementation and refactoring, including:

- System feature design and module planning
- PyQt6 UI development
- SQLite integration
- Development of sales outbound, purchase inbound, and stock management pages
- Company/customer data management features
- Printing and print-preview workflow
- Layered refactoring across `services / repositories / ui`
- Extracting reusable page skeletons and shared document-page capabilities

---

## GitHub

- GitHub Profile: [Yocaihua8](https://github.com/Yocaihua8)
- Repository: [pyqt-sales-outbound-system](https://github.com/Yocaihua8/pyqt-sales-outbound-system)