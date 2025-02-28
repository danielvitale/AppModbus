import flet as ft

from modbus_protocol import ModbusProtocol
from actuator_data import actuators_data

class Actuator(ModbusProtocol):
    def __init__(self, atuador = 1):
        super().__init__(atuador)


def main(page: ft.Page):
    page.title = "Bongas - Protocolo Modbus"
    page.window.center()

    actuator = Actuator()

    # SEND OPEN REQUEST

    def callback_send_openRequest(e, input_fields):
        device_id = int(input_fields[0].value)
        function_value = int(input_fields[1].value)
        address_value = int(input_fields[2].value)
        data_value = int(input_fields[3].value)

        actuator.sendRequest(
            port="COM5", device_id=device_id, function=function_value, address=address_value, data=data_value)

    # TOTALLY OPEN VALVE REQUEST
    def callback_openValve(e, actuator_name):
        if actuator_name in actuators_data:
            actuator.sendRequest(
                port="COM5",
                device_id=1,
                function=0x06,
                address=actuators_data[actuator_name]["address"],
                data=actuators_data[actuator_name]["data_open"]
            )

    # TOTALLY CLOSE VALVE REQUEST
    def callback_closeValve(e, actuator_name):
        if actuator_name in actuators_data:
            actuator.sendRequest(
                port="COM5",
                device_id=1,
                function=0x06,
                address=actuators_data[actuator_name]["address"],
                data=actuators_data[actuator_name]["data_close"]
            )

    # BUTTONS
    def elements_actuators(actuator_id):
        return [
            ft.ElevatedButton(text=f"Abrir Totalmente",
                              on_click=lambda e: callback_openValve(e, actuator_id)),
            ft.ElevatedButton(text=f"Fechar Totalmente",
                              on_click=lambda e: callback_closeValve(e, actuator_id))
        ]

    # DATA REQUESTS INPUT FIELDS
    def elements_dataRequest_openProtocol():
        return [
            ft.TextField(label="Device ID", width=200),
            ft.TextField(label="Function", width=200),
            ft.TextField(label="Address", width=200),
            ft.TextField(label="Data", width=200),

            ft.Button(text="Enviar Mensagem",
                      on_click=lambda e: callback_send_openRequest(e, dataRequest_openRequest))
        ]

    # DATA RECEIVE FIELDS
    def elements_dataReceive_openProtocol():
        return [
            ft.Text(value=actuator.received_data)
        ]

    # ROWS CONTENT
    def rows_content():
        return [
            ft.Row([*dataRequest_openRequest], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([*dataReceive_openRequest], alignment=ft.MainAxisAlignment.CENTER)
        ]

    # DATA REQUESTS CAPSULEDS INPUT FIELDS
    dataRequest_openRequest = elements_dataRequest_openProtocol()

    # DATA RECEIVES CAPSULED TEXTS
    dataReceive_openRequest = elements_dataReceive_openProtocol()

    # CAPSULED ROWS CONTENT
    capsuledRows = rows_content()

    # TABS
    tab_Grey_M = ft.Container(
        content=ft.Row([
            *elements_actuators("Grey-M Multivoltas"),
        ], alignment=ft.MainAxisAlignment.CENTER)
    )

    tab_Grey_Q = ft.Container(
        content=ft.Row([
            *elements_actuators("Grey-Q Evolution"),
        ], alignment=ft.MainAxisAlignment.CENTER)
    )

    tab_White_E = ft.Container(
        content=ft.Row([
            *elements_actuators("White-E Evolution"),
        ], alignment=ft.MainAxisAlignment.CENTER)
    )

    tab_TOP_E = ft.Container(
        content=ft.Row([
            *elements_actuators("TOP-E Module"),
        ], alignment=ft.MainAxisAlignment.CENTER)
    )

    tab_openProtocol = ft.Container(
        content=ft.Column(*[capsuledRows])
    )

    # INSTANCE TABS
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Grey-M Smart", content=tab_Grey_M),
            ft.Tab(text="Grey-Q Evolution", content=tab_Grey_Q),
            ft.Tab(text="White-E Evolution", content=tab_White_E),
            ft.Tab(text="Módulo TOP-E", content=tab_TOP_E),
            ft.Tab(text="Mensagem Modbus", content=tab_openProtocol),
        ],
        expand=2
    )

    page.add(tabs)
    page.update()


# Inicializa a aplicação
ft.app(main)