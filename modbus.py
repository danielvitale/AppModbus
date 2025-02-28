import flet as ft
from modbus_protocol import ModbusProtocol
from actuator_data import actuators_data


class Actuator(ModbusProtocol):
    def __init__(self, atuador_id: int = 1, default_port: str = "COM5"):
        super().__init__(atuador_id)
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
        self.response_text = ft.Text(value="Resposta aparecerá aqui")

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
        # Create a more stylized TOP-E Module tab
        valve_position_slider = ft.Slider(
            min=0,
            max=100,
            divisions=10,
            label="{value}%",
            value=0,
            width=300,
            on_change=lambda e: self.update_slider_value(e.data)
        )

        self.position_value_text = ft.Text(
            value="0%",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE
        )

        # Corrigido: text_align movido para o Text, não para o Container
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
                                    ft.Text("Posição Atual:", size=14),
                                    self.position_value_text
                                ]),
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
                                text="Posição 50%",
                                icon=ft.Icons.TUNE,
                                on_click=lambda e: self.set_valve_position(50),
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
                            ft.Text("ID do Dispositivo: 1", size=14),
                            ft.Text("Endereço: 5", size=14),
                            ft.Text("Status: Operacional", size=14),
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

    def update_slider_value(self, value):
        """Update the position value text based on slider movement."""
        position = int(float(value))
        self.position_value_text.value = f"{position}%"
        # Send the corresponding Modbus command if needed
        # This would translate the percentage to the appropriate Modbus data value
        self.page.update()

    def set_valve_position(self, position_percent):
        """Set the valve to a specific position percentage."""
        # Calculate the corresponding Modbus data value based on percentage
        # This is a simplified example - real implementation would depend on the actuator specs
        data_value = int((position_percent / 100) * 65535)  # Assuming 16-bit register

        # Send the Modbus command to set position
        self.actuator.send_custom_request(
            device_id=1,
            function=6,  # Write Single Register
            address=actuators_data["TOP-E Module"]["address"] if "TOP-E Module" in actuators_data else 5,
            # Use default address if not defined
            data=data_value
        )

        # Update the UI to reflect the change
        self.position_value_text.value = f"{position_percent}%"
        self.update_response(f"Válvula TOP-E ajustada para {position_percent}%")
        self.page.update()

    def create_protocol_tab(self) -> ft.Container:
        """Create the tab for custom Modbus protocol messages."""
        # Create a more detailed response display
        self.response_container = ft.Container(
            content=ft.Column([
                ft.Text("Resposta do Dispositivo", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(height=1),
                self.response_text,
            ]),
            padding=10,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            border_radius=8,
            bgcolor=ft.Colors.BLUE_50,
            width=600,
            height=120,
            margin=ft.margin.only(top=20)
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
                            self.send_button
                        ], alignment=ft.MainAxisAlignment.CENTER),
                    ], spacing=10),
                    padding=15,
                    border=ft.border.all(1, ft.Colors.BLUE_100),
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                ),
                self.response_container,
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
        """Update the response text with formatted information and refresh the UI."""
        self.response_text.value = message

        if hasattr(self.actuator, 'received_data') and self.actuator.received_data:
            # Format received data more clearly
            raw_data = self.actuator.received_data

            if isinstance(raw_data, bytes) or isinstance(raw_data, list):
                # Format bytes or list as hex
                formatted_data = " ".join([f"{b:02X}" for b in raw_data])
                self.response_text.value += f"\n\nDados Recebidos [HEX]: {formatted_data}"

                # If it's a standard Modbus response with function code 3 or 4 (read registers)
                if len(raw_data) > 3 and (raw_data[1] == 3 or raw_data[1] == 4):
                    data_len = raw_data[2]  # Byte count
                    if data_len > 0 and len(raw_data) >= 3 + data_len:
                        data_bytes = raw_data[3:3 + data_len]
                        # Parse registers (2 bytes per register)
                        registers = []
                        for i in range(0, len(data_bytes), 2):
                            if i + 1 < len(data_bytes):
                                reg_val = (data_bytes[i] << 8) + data_bytes[i + 1]
                                registers.append(reg_val)

                        if registers:
                            reg_str = ", ".join([f"{r}" for r in registers])
                            self.response_text.value += f"\nValores: {reg_str}"
            else:
                # For other response types
                self.response_text.value += f"\n\nResposta: {self.actuator.received_data}"

        self.page.update()


def main(page: ft.Page):
    app = ModbusApp(page)


if __name__ == "__main__":
    ft.app(main)