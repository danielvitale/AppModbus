from contextlib import nullcontext

import flet as ft
from modbus_protocol import ModbusProtocol
from actuator_data import actuators_data

import threading
import time

class Actuator(ModbusProtocol):
    def __init__(self, actuator_id: int = 1, default_port: str = "COM5"):
        super().__init__(actuator_id)
        self.default_port = default_port
        self.device_id = 1  # Default device ID

    def open_valve(self, actuator_name: str) -> None:
        """Open the valve completely for the specified actuator."""
        if actuator_name in actuators_data:
            self.sendRequest(
                port=self.default_port,
                device_id=self.device_id,
                function=0x06,
                address=actuators_data[actuator_name]["address"],
                data=actuators_data[actuator_name]["data_open"]
            )

    def close_valve(self, actuator_name: str) -> None:
        """Close the valve completely for the specified actuator."""
        if actuator_name in actuators_data:
            self.sendRequest(
                port=self.default_port,
                device_id=self.device_id,
                function=0x06,
                address=actuators_data[actuator_name]["address"],
                data=actuators_data[actuator_name]["data_close"]
            )

    def send_custom_request(self, device_id: int, function: int, address: int, data: int) -> None:
        """Send a custom request with the provided parameters."""
        self.sendRequest(
            port=self.default_port,
            device_id=device_id,
            function=function,
            address=address,
            data=data
        )


class ModbusApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.actuator = Actuator()
        self.setup_page()
        self.create_ui_components()
        self.assemble_ui()

        self.continuous_read_enabled = False


    def setup_page(self) -> None:
        """Configure basic page properties."""
        self.page.title = "Bongas - Protocolo Modbus"
        self.page.window.center()

    def create_ui_components(self) -> None:
        """Create all UI components."""
        # Create input fields for custom Modbus requests
        self.device_id_field = ft.TextField(label="Device ID", width=200, value="1")
        self.function_field = ft.TextField(label="Function", width=200, value="6")
        self.address_field = ft.TextField(label="Address", width=200)
        self.data_field = ft.TextField(label="Data", width=200)

        # Create response field
        self.response_text = ft.Text(value="00 00 00 00 00 00 00 00")

        # Create send button
        self.send_button = ft.Button(
            text="Enviar Mensagem",
            on_click=self.handle_send_custom_request
        )

        # Create tabs for each actuator type
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Grey-M Smart", content=self.create_actuator_tab("Grey-M Multivoltas")),
                ft.Tab(text="Grey-Q Evolution", content=self.create_actuator_tab("Grey-Q Evolution")),
                ft.Tab(text="White-E Evolution", content=self.create_actuator_tab("White-E Evolution")),
                ft.Tab(text="Módulo TOP-E", content=self.create_actuator_tab("TOP-E Module")),
                ft.Tab(text="Mensagem Modbus", content=self.create_protocol_tab()),
            ],
            expand=2
        )


    def create_actuator_tab(self, actuator_name: str) -> ft.Container:
        """Create a tab for a specific actuator type with improved styling."""
        valve_position_slider = ft.Slider(
            min=0,
            max=100,
            divisions=100,
            label="{value}%",
            value=0,
            width=300,
            on_change=lambda e: self.update_slider_value(e)
        )

        self.position_value_text = ft.Text(
            value="0%",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE
        )

        id_device = ft.TextField(label="ID", width=50, value="1", on_change=lambda e: self.on_device_id_change(e))

        # Fixed: text_align moved to the Text, not for the Container
        status_indicator = ft.Container(
            content=ft.Text("STATUS: Desconectado", color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
            bgcolor=ft.Colors.RED_400,
            border_radius=4,
            padding=8,
            width=200
        )

        # Create controls with improved styling
        return ft.Container(
            content=ft.Column([
                # Header with logo and status
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DEVICE_HUB, size=36, color=ft.Colors.BLUE),
                        ft.Column([
                            ft.Text(f"{actuator_name} Controller", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Controlador para módulo {actuator_name}", size=14, color=ft.Colors.GREY_700)
                        ]),
                        status_indicator
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.BLUE_200),
                ),

                # Divider
                ft.Divider(height=1, color=ft.Colors.BLUE_100),

                # Main controls section
                ft.Container(
                    content=ft.Column([
                        ft.Text("Controle de Posição da Válvula", size=16, weight=ft.FontWeight.W_500),

                        # Position control with slider
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text("Posição Definida:", size=14),
                                    self.position_value_text
                                ], alignment=ft.MainAxisAlignment.CENTER,),
                                ft.Row([
                                    ft.Icon(ft.Icons.CLOSE, color=ft.Colors.RED),
                                    valve_position_slider,
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN)
                                ], alignment=ft.MainAxisAlignment.CENTER,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            ]),
                            padding=15,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            border_radius=8,
                            bgcolor=ft.Colors.WHITE,
                            margin=10
                        ),

                        # Quick action buttons
                        ft.Row([
                            ft.ElevatedButton(
                                text="Fechar Totalmente",
                                icon=ft.Icons.CLOSE,
                                on_click=lambda e: self.handle_close_valve(actuator_name),
                                bgcolor=ft.Colors.RED_400,
                                color=ft.Colors.WHITE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                ),
                            ),
                            ft.ElevatedButton(
                                text="Abrir Percentual",
                                icon=ft.Icons.TUNE,
                                on_click=lambda e: self.set_valve_position(actuator_name, self.position),
                                bgcolor=ft.Colors.AMBER_400,
                                color=ft.Colors.WHITE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                ),
                            ),
                            ft.ElevatedButton(
                                text="Abrir Totalmente",
                                icon=ft.Icons.CHECK_CIRCLE,
                                on_click=lambda e: self.handle_open_valve(actuator_name),
                                bgcolor=ft.Colors.GREEN_400,
                                color=ft.Colors.WHITE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                ),
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                    ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                ),

                # Status and information section
                ft.Container(
                    content=ft.Column([
                        ft.Text("Informações do Dispositivo", weight=ft.FontWeight.BOLD),
                        ft.Row([
                            id_device,
                            ft.Text(value="Totalmente Aberto:"),
                            ft.Icon(name=ft.Icons.CIRCLE, color=ft.Colors.RED, size=40),
                            ft.Text(value="Totalmente Fechado:"),
                            ft.Icon(name=ft.Icons.CIRCLE, color=ft.Colors.RED, size=40),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    bgcolor=ft.Colors.GREY_50,
                )
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor=ft.Colors.WHITE,
        )

    def on_device_id_change(self, e):
        """Handle device ID change event."""
        self.actuator.device_id = int(e.control.value)

    def continuous_read_change(self, e):
        """Handle continuous read checkbox change event."""
        self.continuous_read_enabled = e.control.value

        if self.continuous_read_enabled:
            thread = threading.Thread(target=self.continuous_reading_thread)
            thread.daemon = True
            thread.start()

        self.page.update()

    def continuous_reading_thread(self):
        """Background thread for continuous Modbus reading."""
        while self.continuous_read_enabled:
            # Send Modbus request
            self.actuator.send_custom_request(
                device_id=self.actuator.device_id,
                function=3,
                address=2,
                data=1
            )

            # Update the continuous reading container text
            if hasattr(self.actuator, 'received_data') and self.actuator.received_data:
                raw_data = self.actuator.received_data
                if isinstance(raw_data, bytes) or isinstance(raw_data, list):
                    formatted_data = " ".join([f"{b:02X}" for b in raw_data])
                    self.continuous_response_text.value = f"Dados [HEX]: {formatted_data}"

                    # Add additional processing if needed
                    if len(raw_data) > 3 and (raw_data[1] == 3 or raw_data[1] == 4):
                        # Process read data (function 3 or 4)
                        data_len = raw_data[2]
                        if data_len > 0 and len(raw_data) >= 3 + data_len:
                            # Extract and format response data
                            data_values = raw_data[3:3 + data_len]
                            data_str = " ".join([f"{b:02X}" for b in data_values])
                            self.continuous_response_text.value += f"\n\nValores: {data_str}"

            self.page.update()
            time.sleep(1)

    def update_slider_value(self, e):
        """Update the position value text based on slider movement."""
        self.position = int(e.control.value)
        self.position_value_text.value = f"{self.position}%"
        # Send the corresponding Modbus command if needed
        # This would translate the percentage to the appropriate Modbus data value
        self.page.update()

    def set_valve_position(self, actuator_name, position_percent):
        """Set the valve to a specific position percentage."""
        # Calculate the corresponding Modbus data value based on percentage
        # This is a simplified example - real implementation would depend on the actuator specs
        data_value = actuators_data[actuator_name]["formula"](position_percent)

        # Send the Modbus command to set position
        self.actuator.send_custom_request(
            device_id=self.actuator.device_id,
            function=6,
            address=actuators_data[actuator_name]["address"],
            data=data_value
        )

        # Update the UI to reflect the change
        self.position_value_text.value = f"{position_percent}%"
        self.update_response(f"Válvula TOP-E ajustada para {position_percent}%")
        self.page.update()

    def create_protocol_tab(self) -> ft.Container:
        """Create the tab for custom Modbus protocol messages."""
        # Create independent response texts for each container
        self.write_response_text = ft.Text(value="Aguardando comando...")
        self.continuous_response_text = ft.Text(value="Aguardando leitura contínua...")

        # Container for write commands
        self.write_container = ft.Container(
            content=ft.Column([
                ft.Text("Resposta do Dispositivo (Escrita)", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(height=1),
                self.write_response_text,
            ]),
            padding=10,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            border_radius=8,
            bgcolor=ft.Colors.BLUE_50,
            width=600,
            height=120,
            margin=ft.margin.only(top=20)
        )

        # Container for continuous reading
        self.continuous_read_container = ft.Container(
            content=ft.Column([
                ft.Text("Resposta do Dispositivo (Leitura Contínua)", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(height=1),
                self.continuous_response_text,
            ]),
            padding=10,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            border_radius=8,
            bgcolor=ft.Colors.BLUE_50,
            width=600,
            height=120,
            margin=ft.margin.only(top=20)
        )

        self.continuous_read_checkbox = ft.Checkbox(
            label="Habilitar Leitura Contínua",
            on_change=lambda e: self.continuous_read_change(e)
        )

        # Main container layout
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Configuração Manual de Mensagem Modbus",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Divider(height=2),
                ft.Text(
                    "Configure os parâmetros para envio da mensagem Modbus:",
                    size=14
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            self.device_id_field,
                            self.function_field,
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([
                            self.address_field,
                            self.data_field,
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([
                            self.send_button,
                            self.continuous_read_checkbox
                        ], alignment=ft.MainAxisAlignment.CENTER),
                    ], spacing=10),
                    padding=15,
                    border=ft.border.all(1, ft.Colors.BLUE_100),
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                ),
                self.write_container,
                self.continuous_read_container,
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20
        )

    def assemble_ui(self) -> None:
        """Add all UI components to the page."""
        self.page.add(self.tabs)
        self.page.update()

    # Event handlers
    def handle_open_valve(self, actuator_name: str) -> None:
        """Handle open valve button click."""
        self.actuator.open_valve(actuator_name)
        self.update_response(f"Comando para abrir válvula {actuator_name} enviado")

    def handle_close_valve(self, actuator_name: str) -> None:
        """Handle close valve button click."""
        self.actuator.close_valve(actuator_name)
        self.update_response(f"Comando para fechar válvula {actuator_name} enviado")

    def handle_send_custom_request(self, e) -> None:
        """Handle send custom request button click."""
        try:
            device_id = int(self.device_id_field.value)
            function = int(self.function_field.value)
            address = int(self.address_field.value)
            data = int(self.data_field.value)

            self.actuator.send_custom_request(device_id, function, address, data)
            self.update_response(
                f"Requisição enviada: Device={device_id}, Function={function}, Address={address}, Data={data}")

        except ValueError as error:
            self.update_response(f"Erro: Todos os campos devem ser números inteiros válidos")

    def update_response(self, message: str) -> None:
        """Update the response text for command operations."""
        self.write_response_text.value = message

        if hasattr(self.actuator, 'received_data') and self.actuator.received_data:
            # Format the response data
            raw_data = self.actuator.received_data
            if isinstance(raw_data, bytes) or isinstance(raw_data, list):
                formatted_data = " ".join([f"{b:02X}" for b in raw_data])
                self.write_response_text.value += f"\n\nDados [HEX]: {formatted_data}"

        self.page.update()


def main(page: ft.Page):
    app = ModbusApp(page)


if __name__ == "__main__":
    ft.app(main)