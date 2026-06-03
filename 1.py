import flet as ft
import mysql.connector
from datetime import date

# ==========================
# MYSQL CONNECTION
# ==========================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shariefd2002",
    database="tracking_db"
)

cursor = db.cursor()

# ==========================
# MAIN APP
# ==========================

def main(page: ft.Page):

    page.title = "Inventory Tracking System"
    page.window_width = 1100
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#f4f6f9"
    page.scroll = "auto"

    # ==========================
    # INPUTS
    # ==========================

    item_name = ft.TextField(
        label="Item Name",
        width=250,
        border_radius=15
    )

    quantity = ft.TextField(
        label="Quantity",
        width=150,
        border_radius=15
    )

    search_box = ft.TextField(
        label="Search Item",
        prefix_icon=ft.Icons.SEARCH,
        width=300
    )

    category_dropdown = ft.Dropdown(
        label="Category",
        width=200
    )

    status_dropdown = ft.Dropdown(
        label="Status",
        width=200,
        options=[
            ft.dropdown.Option("Available"),
            ft.dropdown.Option("Pending"),
            ft.dropdown.Option("Out of Stock")
        ]
    )

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Item")),
            ft.DataColumn(ft.Text("Category")),
            ft.DataColumn(ft.Text("Qty")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Date Added")),
            ft.DataColumn(ft.Text("Actions"))
        ],
        rows=[]
    )

    total_items = ft.Text("0", size=25, weight="bold")

    selected_id = {"id": None}

    # ==========================
    # LOAD CATEGORIES
    # ==========================

    def load_categories():

        category_dropdown.options.clear()

        cursor.execute(
            "SELECT category_id, category_name FROM categories"
        )

        for cat in cursor.fetchall():
            category_dropdown.options.append(
                ft.dropdown.Option(
                    key=str(cat[0]),
                    text=cat[1]
                )
            )

        page.update()

    # ==========================
    # DASHBOARD
    # ==========================

    def update_dashboard():

        cursor.execute(
            "SELECT COUNT(*) FROM items"
        )

        total = cursor.fetchone()[0]

        total_items.value = str(total)

        page.update()

    # ==========================
    # STATUS COLOR
    # ==========================

    def status_color(status):

        if status == "Available":
            return ft.Colors.GREEN

        elif status == "Pending":
            return ft.Colors.ORANGE

        return ft.Colors.RED

    # ==========================
    # LOAD DATA
    # ==========================

    def load_data(search=""):

        table.rows.clear()

        sql = """
        SELECT i.id,
               i.item_name,
               c.category_name,
               i.quantity,
               i.status,
               i.date_added

        FROM items i
        JOIN categories c
        ON i.category_id=c.category_id
        """

        values = ()

        if search:
            sql += " WHERE i.item_name LIKE %s"
            values = (f"%{search}%",)

        cursor.execute(sql, values)

        records = cursor.fetchall()

        for row in records:

            item_id = row[0]

            edit_btn = ft.IconButton(
                icon=ft.Icons.EDIT,
                icon_color="blue",
                on_click=lambda e,
                r=row: edit_record(r)
            )

            delete_btn = ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color="red",
                on_click=lambda e,
                id=item_id: delete_item(id)
            )

            badge = ft.Container(
                content=ft.Text(
                    row[4],
                    color="white"
                ),
                bgcolor=status_color(row[4]),
                border_radius=20,
                padding=5
            )

            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[0]))),
                        ft.DataCell(ft.Text(row[1])),
                        ft.DataCell(ft.Text(row[2])),
                        ft.DataCell(ft.Text(str(row[3]))),
                        ft.DataCell(badge),
                        ft.DataCell(ft.Text(str(row[5]))),
                        ft.DataCell(
                            ft.Row([
                                edit_btn,
                                delete_btn
                            ])
                        )
                    ]
                )
            )

        update_dashboard()
        page.update()

    # ==========================
    # ADD ITEM
    # ==========================

    def add_item(e):

        sql = """
        INSERT INTO items
        (
            item_name,
            quantity,
            status,
            date_added,
            category_id
        )
        VALUES
        (%s,%s,%s,%s,%s)
        """

        values = (
            item_name.value,
            quantity.value,
            status_dropdown.value,
            date.today(),
            category_dropdown.value
        )

        cursor.execute(sql, values)
        db.commit()

        clear_fields()

        load_data()

    # ==========================
    # EDIT
    # ==========================

    def edit_record(row):

        selected_id["id"] = row[0]

        item_name.value = row[1]
        quantity.value = str(row[3])
        status_dropdown.value = row[4]

        page.update()

    # ==========================
    # UPDATE
    # ==========================

    def update_item(e):

        if selected_id["id"] is None:
            return

        sql = """
        UPDATE items
        SET item_name=%s,
            quantity=%s,
            status=%s
        WHERE id=%s
        """

        values = (
            item_name.value,
            quantity.value,
            status_dropdown.value,
            selected_id["id"]
        )

        cursor.execute(sql, values)
        db.commit()

        clear_fields()

        load_data()

    # ==========================
    # DELETE
    # ==========================

    def delete_item(item_id):

        cursor.execute(
            "DELETE FROM items WHERE id=%s",
            (item_id,)
        )

        db.commit()

        load_data()

    # ==========================
    # CLEAR
    # ==========================

    def clear_fields():

        item_name.value = ""
        quantity.value = ""
        status_dropdown.value = None
        category_dropdown.value = None
        selected_id["id"] = None

        page.update()

    # ==========================
    # SEARCH
    # ==========================

    def search_item(e):
        load_data(search_box.value)

    # ==========================
    # BUTTONS
    # ==========================

    add_btn = ft.ElevatedButton(
        "Add",
        icon=ft.Icons.ADD,
        bgcolor="green",
        color="white",
        on_click=add_item
    )

    update_btn = ft.ElevatedButton(
        "Update",
        icon=ft.Icons.SAVE,
        bgcolor="blue",
        color="white",
        on_click=update_item
    )

    search_btn = ft.ElevatedButton(
        "Search",
        on_click=search_item
    )

    # ==========================
    # UI
    # ==========================

    page.add(

        ft.Column([

            ft.Text(
                "📦 INVENTORY TRACKING SYSTEM",
                size=30,
                weight="bold"
            ),

            ft.Row([

                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Total Items"
                        ),
                        total_items
                    ]),
                    bgcolor="#1976D2",
                    padding=20,
                    border_radius=15,
                    width=200
                )

            ]),

            ft.Divider(),

            ft.Text(
                "Add / Update Item",
                size=20,
                weight="bold"
            ),

            ft.Row([
                item_name,
                quantity
            ]),

            ft.Row([
                category_dropdown,
                status_dropdown
            ]),

            ft.Row([
                add_btn,
                update_btn
            ]),

            ft.Divider(),

            ft.Row([
                search_box,
                search_btn
            ]),

            table

        ], spacing=20)

    )

    load_categories()
    load_data()

ft.app(target=main)