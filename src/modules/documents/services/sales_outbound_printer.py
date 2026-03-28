from PyQt6.QtGui import QPen, QFont
from PyQt6.QtCore import Qt, QRectF, QMarginsF
from PyQt6.QtGui import QPageLayout, QPageSize
from PyQt6.QtPrintSupport import QPrinter


class SalesOutboundPrinter:
    @staticmethod
    def create_printer():
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageOrientation(QPageLayout.Orientation.Landscape)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        printer.setPageMargins(QMarginsF(5, 5, 5, 5), QPageLayout.Unit.Millimeter)
        return printer

    @staticmethod
    def mm_to_px(mm, printer):
        return mm * printer.resolution() / 25.4

    @staticmethod
    def draw_cell(painter, rect, text="", align=Qt.AlignmentFlag.AlignCenter):
        old_pen = painter.pen()

        border_pen = QPen(Qt.GlobalColor.black)
        border_pen.setWidth(2)
        border_pen.setCosmetic(False)
        painter.setPen(border_pen)
        painter.drawRect(rect)

        text_pen = QPen(Qt.GlobalColor.black)
        text_pen.setWidth(1)
        text_pen.setCosmetic(False)
        painter.setPen(text_pen)

        padding_x = 14
        padding_y = 2
        text_rect = QRectF(rect.adjusted(padding_x, padding_y, -padding_x, -padding_y))
        painter.drawText(text_rect, align | Qt.AlignmentFlag.AlignVCenter, str(text or ""))

        painter.setPen(old_pen)

    @staticmethod
    def draw_title(painter, content_rect: QRectF, title: str, title_h: float):
        title_font = QFont("Microsoft YaHei", 20)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.drawText(
            QRectF(content_rect.left(), content_rect.top(), content_rect.width(), title_h),
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
            title
        )

    @staticmethod
    def draw_header_section(
        painter,
        data: dict,
        left: float,
        start_y: float,
        width: float,
        row_h: float,
        draw_cell,
        show_phone: bool,
        show_contact: bool,
        show_summary: bool,
    ) -> float:
        header_ratios = [0.12, 0.20, 0.12, 0.22, 0.12, 0.22]
        header_widths = [width * r for r in header_ratios]
        header_widths[-1] = width - sum(header_widths[:-1])

        x = left
        y = start_y
        w = header_widths

        draw_cell(painter, QRectF(x, y, w[0], row_h), "发货仓库")
        draw_cell(painter, QRectF(x + w[0], y, w[1], row_h), data["warehouse"], Qt.AlignmentFlag.AlignLeft)
        draw_cell(painter, QRectF(x + w[0] + w[1], y, w[2], row_h), "单据编号")
        draw_cell(painter, QRectF(x + w[0] + w[1] + w[2], y, w[3], row_h), data["order_no"], Qt.AlignmentFlag.AlignLeft)
        draw_cell(painter, QRectF(x + w[0] + w[1] + w[2] + w[3], y, w[4], row_h), "录单日期")
        draw_cell(
            painter,
            QRectF(x + w[0] + w[1] + w[2] + w[3] + w[4], y, w[5], row_h),
            data["order_date"],
            Qt.AlignmentFlag.AlignLeft
        )

        y += row_h
        draw_cell(painter, QRectF(x, y, w[0], row_h), "购买单位")

        if show_phone:
            draw_cell(
                painter,
                QRectF(x + w[0], y, w[1] + w[2] + w[3], row_h),
                data["customer_name"],
                Qt.AlignmentFlag.AlignLeft
            )
            draw_cell(
                painter,
                QRectF(x + w[0] + w[1] + w[2] + w[3], y, w[4], row_h),
                "单位电话"
            )
            draw_cell(
                painter,
                QRectF(x + w[0] + w[1] + w[2] + w[3] + w[4], y, w[5], row_h),
                data["customer_phone"],
                Qt.AlignmentFlag.AlignLeft
            )
        else:
            draw_cell(
                painter,
                QRectF(x + w[0], y, width - w[0], row_h),
                data["customer_name"],
                Qt.AlignmentFlag.AlignLeft
            )

        y += row_h
        draw_cell(painter, QRectF(x, y, w[0], row_h), "单位地址")

        if show_contact:
            draw_cell(
                painter,
                QRectF(x + w[0], y, w[1] + w[2] + w[3], row_h),
                data["customer_address"],
                Qt.AlignmentFlag.AlignLeft
            )
            draw_cell(
                painter,
                QRectF(x + w[0] + w[1] + w[2] + w[3], y, w[4], row_h),
                "联系人"
            )
            draw_cell(
                painter,
                QRectF(x + w[0] + w[1] + w[2] + w[3] + w[4], y, w[5], row_h),
                data["customer_contact"],
                Qt.AlignmentFlag.AlignLeft
            )
        else:
            draw_cell(
                painter,
                QRectF(x + w[0], y, width - w[0], row_h),
                data["customer_address"],
                Qt.AlignmentFlag.AlignLeft
            )

        if show_summary:
            y += row_h
            draw_cell(painter, QRectF(x, y, w[0], row_h), "备注摘要")
            draw_cell(
                painter,
                QRectF(x + w[0], y, width - w[0], row_h),
                data["summary"],
                Qt.AlignmentFlag.AlignLeft
            )

        return y + row_h

    @staticmethod
    def draw_items_table(
        painter,
        left: float,
        start_y: float,
        width: float,
        row_h: float,
        items: list,
        draw_cell,
    ) -> float:
        table_headers = ["序号", "商品全名", "规格", "颜色", "件数", "数量", "单价", "金额", "备注"]
        table_ratios = [0.07, 0.25, 0.12, 0.10, 0.08, 0.10, 0.10, 0.10, 0.08]
        table_widths = [width * r for r in table_ratios]
        table_widths[-1] = width - sum(table_widths[:-1])

        header_font = QFont("Microsoft YaHei", 11)
        header_font.setBold(True)
        painter.setFont(header_font)

        cx = left
        for i, header in enumerate(table_headers):
            draw_cell(painter, QRectF(cx, start_y, table_widths[i], row_h), header)
            cx += table_widths[i]

        normal_font = QFont("Microsoft YaHei", 11)
        painter.setFont(normal_font)

        display_items = list(items[:7])
        while len(display_items) < 7:
            display_items.append(None)

        for row_index, item in enumerate(display_items):
            row_y = start_y + row_h * (row_index + 1)
            values = [
                str(row_index + 1),
                item.product_name if item else "",
                item.specification if item else "",
                item.color if item else "",
                str(item.pieces) if item and item.pieces is not None else "",
                f"{item.quantity:.2f}" if item and item.quantity is not None else "",
                f"{item.unit_price:.2f}" if item and item.unit_price is not None else "",
                f"{item.amount:.2f}" if item and item.amount is not None else "",
                item.remark if item else "",
            ]

            cx = left
            for i, value in enumerate(values):
                align = Qt.AlignmentFlag.AlignCenter
                if i in (1, 2, 3, 8):
                    align = Qt.AlignmentFlag.AlignLeft
                elif i in (4, 5, 6, 7):
                    align = Qt.AlignmentFlag.AlignRight

                draw_cell(painter, QRectF(cx, row_y, table_widths[i], row_h), value, align)
                cx += table_widths[i]

        return start_y + row_h * 8

    @staticmethod
    def draw_total_section(
        painter,
        left: float,
        start_y: float,
        width: float,
        row_h: float,
        total_amount: str,
        amount_in_words: str,
        draw_cell,
    ) -> float:
        total_left_w = width * 0.22
        total_right_w = width - total_left_w

        draw_cell(
            painter,
            QRectF(left, start_y, total_left_w, row_h),
            f"金额合计：{total_amount}",
            Qt.AlignmentFlag.AlignLeft
        )
        draw_cell(
            painter,
            QRectF(left + total_left_w, start_y, total_right_w, row_h),
            f"大写金额：{amount_in_words}",
            Qt.AlignmentFlag.AlignLeft
        )

        return start_y + row_h

    @staticmethod
    def draw_footer_section(
        painter,
        data: dict,
        left: float,
        start_y: float,
        width: float,
        row_h: float,
        sign_row_h: float,
        draw_cell,
        show_company_phone: bool,
        show_company_contact: bool,
        show_reviewer: bool,
        show_sign_remark: bool,
    ) -> float:
        company_name_w = width * 0.14
        company_value_w = width * 0.44
        company_phone_w = width * 0.14
        company_phone_value_w = width - company_name_w - company_value_w - company_phone_w

        current_y = start_y

        # 第1行：公司名称 / 公司电话
        draw_cell(painter, QRectF(left, current_y, company_name_w, row_h), "公司名称")

        if show_company_phone:
            draw_cell(
                painter,
                QRectF(left + company_name_w, current_y, company_value_w, row_h),
                data["company_name"],
                Qt.AlignmentFlag.AlignLeft
            )
            draw_cell(
                painter,
                QRectF(left + company_name_w + company_value_w, current_y, company_phone_w, row_h),
                "公司电话"
            )
            draw_cell(
                painter,
                QRectF(left + company_name_w + company_value_w + company_phone_w, current_y, company_phone_value_w, row_h),
                data["company_phone"],
                Qt.AlignmentFlag.AlignLeft
            )
        else:
            draw_cell(
                painter,
                QRectF(left + company_name_w, current_y, width - company_name_w, row_h),
                data["company_name"],
                Qt.AlignmentFlag.AlignLeft
            )

        current_y += row_h

        # 第2行：公司地址 / 联系人
        draw_cell(painter, QRectF(left, current_y, company_name_w, row_h), "公司地址")

        if show_company_contact:
            draw_cell(
                painter,
                QRectF(left + company_name_w, current_y, company_value_w, row_h),
                data["company_address"],
                Qt.AlignmentFlag.AlignLeft
            )
            draw_cell(
                painter,
                QRectF(left + company_name_w + company_value_w, current_y, company_phone_w, row_h),
                "联系人"
            )
            draw_cell(
                painter,
                QRectF(left + company_name_w + company_value_w + company_phone_w, current_y, company_phone_value_w, row_h),
                data["company_contact"],
                Qt.AlignmentFlag.AlignLeft
            )
        else:
            draw_cell(
                painter,
                QRectF(left + company_name_w, current_y, width - company_name_w, row_h),
                data["company_address"],
                Qt.AlignmentFlag.AlignLeft
            )

        current_y += row_h

        # 第3行：经手人 / 录单人 / 审核人
        sign_w = width / 3
        rect1 = QRectF(left, current_y, sign_w, sign_row_h)
        rect2 = QRectF(left + sign_w, current_y, sign_w, sign_row_h)
        rect3 = QRectF(left + sign_w * 2, current_y, width - sign_w * 2, sign_row_h)

        draw_cell(painter, rect1, "")
        draw_cell(painter, rect2, "")
        draw_cell(painter, rect3, "")

        padding_x = 14
        painter.drawText(
            QRectF(rect1.adjusted(padding_x, 0, -padding_x, 0)),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            f"经手人：{data['handler']}"
        )
        painter.drawText(
            QRectF(rect2.adjusted(padding_x, 0, -padding_x, 0)),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            f"录单人：{data['recorder']}"
        )

        reviewer_text = f"审核人：{data['reviewer']}" if show_reviewer else ""
        painter.drawText(
            QRectF(rect3.adjusted(padding_x, 0, -padding_x, 0)),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            reviewer_text
        )

        current_y += sign_row_h

        # 第4行：签字备注
        if show_sign_remark:
            remark_rect = QRectF(left, current_y, width, sign_row_h)
            draw_cell(painter, remark_rect, "")

            painter.drawText(
                QRectF(remark_rect.adjusted(padding_x, 0, -padding_x, 0)),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                f"签字备注：{data['sign_remark']}"
            )
            current_y += sign_row_h

        return current_y

    @staticmethod
    def draw_document(
        painter,
        printer,
        data: dict,
        visibility: dict,
        mm_to_px,
        draw_cell,
    ):
        page_rect = QRectF(printer.pageRect(QPrinter.Unit.DevicePixel))

        safe_margin_x = mm_to_px(10, printer)
        safe_margin_y = mm_to_px(3, printer)
        content_rect = page_rect.adjusted(
            safe_margin_x, safe_margin_y,
            -safe_margin_x, -safe_margin_y
        )

        title_h = mm_to_px(11, printer)
        gap = mm_to_px(2.2, printer)
        row_h = mm_to_px(8.2, printer)

        SalesOutboundPrinter.draw_title(
            painter=painter,
            content_rect=content_rect,
            title=data["title"],
            title_h=title_h
        )

        current_y = content_rect.top() + title_h + mm_to_px(6, printer)

        normal_font = QFont("Microsoft YaHei", 11)
        painter.setFont(normal_font)

        left = content_rect.left()
        width = content_rect.width()

        header_bottom_y = SalesOutboundPrinter.draw_header_section(
            painter=painter,
            data=data,
            left=left,
            start_y=current_y,
            width=width,
            row_h=row_h,
            draw_cell=draw_cell,
            show_phone=visibility["show_phone"],
            show_contact=visibility["show_contact"],
            show_summary=visibility["show_summary"],
        )
        current_y = header_bottom_y + gap

        current_y = SalesOutboundPrinter.draw_items_table(
            painter=painter,
            left=left,
            start_y=current_y,
            width=width,
            row_h=row_h,
            items=data["items"],
            draw_cell=draw_cell,
        ) + gap

        current_y = SalesOutboundPrinter.draw_total_section(
            painter=painter,
            left=left,
            start_y=current_y,
            width=width,
            row_h=row_h,
            total_amount=data["total_amount"],
            amount_in_words=data["amount_in_words"],
            draw_cell=draw_cell,
        ) + gap

        sign_row_h = mm_to_px(7.2, printer)

        SalesOutboundPrinter.draw_footer_section(
            painter=painter,
            data=data,
            left=left,
            start_y=current_y,
            width=width,
            row_h=row_h,
            sign_row_h=sign_row_h,
            draw_cell=draw_cell,
            show_company_phone=visibility["show_company_phone"],
            show_company_contact=visibility["show_company_contact"],
            show_reviewer=visibility["show_reviewer"],
            show_sign_remark=visibility["show_sign_remark"],
        )









