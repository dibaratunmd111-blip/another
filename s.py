import flet as ft
import mysql.connector

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


def main(page: ft.Page):

    page.title = "Tracking System"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F5F7FA"
    page.window_width = 900
    page.window_height = 700
    page.scroll = "auto"

    # ==========================
    # INPUT FIELDS
    # ==========================

    item_name = ft.TextField(
        label="Item Name",
        prefix_icon=ft.Icons.INVENTORY_2,
        border_radius=15,
        width=350
    )

    item_status = ft.Dropdown(
        label="Status",
        width=350,
        border_radius=15,
        options=[
            ft.dropdown.Option("Pending"),
            ft.dropdown.Option("In Progress"),
            ft.dropdown.Option("Completed")
        ]
    )

    # ==========================
    # TABLE
    # ==========================

    table = ft.DataTable(
        bgcolor="white",
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=10,
        heading_row_color="#1976D2",
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Item Name")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Action"))
        ],
        rows=[]
    )

    # ==========================
    # STATUS COLOR
    # ==========================

    def get_status_color(status):

        if status == "Completed":
            return ft.Colors.GREEN

        elif status == "In Progress":
            return ft.Colors.ORANGE

        else:
            return ft.Colors.RED

    # ==========================
    # LOAD DATA
    # ==========================

    def load_data():

        table.rows.clear()

        cursor.execute("SELECT * FROM items")
        records = cursor.fetchall()

        for row in records:

            delete_btn = ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color="red",
                tooltip="Delete",
                on_click=lambda e, item_id=row[0]:
                delete_item(item_id)
            )

            status_chip = ft.Container(
                content=ft.Text(
                    row[2],
                    color="white",
                    weight="bold",
                    size=12
                ),
                bgcolor=get_status_color(row[2]),
                padding=8,
                border_radius=20
            )

            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[0]))),
                        ft.DataCell(ft.Text(row[1])),
                        ft.DataCell(status_chip),
                        ft.DataCell(delete_btn)
                    ]
                )
            )

        page.update()

    # ==========================
    # ADD ITEM
    # ==========================

    def add_item(e):

        if not item_name.value or not item_status.value:
            return

        sql = """
        INSERT INTO items(item_name,status)
        VALUES(%s,%s)
        """

        values = (
            item_name.value,
            item_status.value
        )

        cursor.execute(sql, values)
        db.commit()

        item_name.value = ""
        item_status.value = None

        load_data()

        page.snack_bar = ft.SnackBar(
            ft.Text("Item Added Successfully!")
        )
        page.snack_bar.open = True
        page.update()

    # ==========================
    # DELETE ITEM
    # ==========================

    def delete_item(item_id):

        cursor.execute(
            "DELETE FROM items WHERE id=%s",
            (item_id,)
        )

        db.commit()

        load_data()

        page.snack_bar = ft.SnackBar(
            ft.Text("Item Deleted!")
        )
        page.snack_bar.open = True
        page.update()

    # ==========================
    # DASHBOARD COUNTS
    # ==========================

    total_text = ft.Text(
        "0",
        size=28,
        weight="bold"
    )

    def update_stats():

        cursor.execute(
            "SELECT COUNT(*) FROM items"
        )

        total = cursor.fetchone()[0]

        total_text.value = str(total)

        page.update()

    # ==========================
    # REFRESH DATA
    # ==========================

    def refresh():

        load_data()
        update_stats()

    # ==========================
    # BUTTON
    # ==========================

    add_btn = ft.ElevatedButton(
        "Add Item",
        icon=ft.Icons.ADD,
        bgcolor="#1976D2",
        color="white",
        height=50,
        width=200,
        on_click=lambda e: [
            add_item(e),
            update_stats()
        ]
    )

    # ==========================
    # UI
    # ==========================

    page.add(

        ft.Container(

            content=ft.Column([

                ft.Text(
                    "📦 Inventory Tracking System",
                    size=32,
                    weight="bold",
                    color="#1976D2"
                ),

                ft.Text(
                    "Manage and Track Items Easily",
                    size=15,
                    color="grey"
                ),

                ft.Divider(),

                ft.Row([

                    ft.Container(
                        content=ft.Column([
                            ft.Icon(
                                ft.Icons.INVENTORY,
                                size=40,
                                color="white"
                            ),

                            ft.Text(
                                "Total Items",
                                color="white"
                            ),

                            total_text
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER),

                        bgcolor="#1976D2",
                        width=220,
                        height=150,
                        border_radius=20,
                        padding=20
                    )

                ]),

                ft.Divider(),

                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([

                            ft.Text(
                                "Add New Item",
                                size=22,
                                weight="bold"
                            ),

                            item_name,
                            item_status,
                            add_btn

                        ])
                    )
                ),

                ft.Text(
                    "Tracking Records",
                    size=22,
                    weight="bold"
                ),

                table

            ]),

            padding=20
        )
    )

    refresh()


ft.app(target=main)