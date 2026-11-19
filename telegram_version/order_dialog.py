from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from tovar import Tovar


class OrderDialog(QDialog):
    def __init__(self, order_model, parent=None):
        super().__init__(parent)
        self.order_model = order_model
        self.setWindowTitle("Подтверждение заказа")
        self.resize(720, 340)

        self.table = QTableWidget(0, 5, self)
        self.table.setHorizontalHeaderLabels(
            ["Товар", "Размер", "Количество", "Цена за пару", "Сумма"]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().hide()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        self.total_label = QLabel(self)
        buttons = QDialogButtonBox(self)
        self.confirm_button = buttons.addButton(
            "Подтвердить заказ", QDialogButtonBox.ButtonRole.AcceptRole
        )
        self.remove_button = buttons.addButton(
            "Удалить позицию", QDialogButtonBox.ButtonRole.ActionRole
        )
        buttons.addButton("Вернуться в каталог", QDialogButtonBox.ButtonRole.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.remove_button.clicked.connect(self.remove_selected)
        self.table.itemSelectionChanged.connect(self.update_remove_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addWidget(self.total_label, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(buttons)
        self.refresh()

    def refresh(self):
        row_count = self.order_model.rowCount()
        self.table.setRowCount(row_count)
        total = 0
        for row in range(row_count):
            line = self.order_model.item(row).data(Qt.ItemDataRole.UserRole)
            total += line.total
            columns = (
                line.product_name,
                line.size_title,
                str(line.quantity),
                f"{Tovar.format_price(line.unit_price)} ₽",
                f"{Tovar.format_price(line.total)} ₽",
            )
            for column, value in enumerate(columns):
                self.table.setItem(row, column, QTableWidgetItem(value))

        self.total_label.setText(f"Итого: {Tovar.format_price(total)} ₽")
        self.confirm_button.setEnabled(row_count > 0)
        self.table.clearSelection()
        self.update_remove_button()

    def update_remove_button(self):
        self.remove_button.setEnabled(self.table.selectionModel().hasSelection())

    def remove_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if rows:
            self.order_model.removeRow(rows[0].row())
            self.refresh()
