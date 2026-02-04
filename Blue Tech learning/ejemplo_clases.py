class Proyecto:
    def __init__(self, nombre_obra, presupuesto):
        self.nombre_obra = nombre_obra
        self.presupuesto = presupuesto
        self.gastos = 0

    def registrar_gasto(self, monto, descripcion):
        if self.gastos + monto <= self.presupuesto:
            self.gastos += monto
            print(f"✅ Gasto registrado: {descripcion} por {monto} Bs.")
        else:
            print(
                f"❌ ALERTA: El gasto de {monto} Bs excede el presupuesto de la obra {self.nombre_obra}!"
            )

    def estado_financiero(self):
        saldo = self.presupuesto - self.gastos
        print(f"\n📊 --- REPORTE: {self.nombre_obra} ---")
        print(f"💰 Presupuesto Total: {self.presupuesto} Bs")
        print(f"💸 Gastos Acumulados: {self.gastos} Bs")
        print(f"💵 Saldo Disponible: {saldo} Bs\n")


# --- USO DEL SISTEMA ---
obra_santa_cruz = Proyecto("Condominio Las Palmeras", 500000)

obra_santa_cruz.registrar_gasto(120000, "Compra de Cemento Viacha")
obra_santa_cruz.registrar_gasto(
    400000, "Pago de Planilla Mes 1"
)  # Esto debería dar alerta

obra_santa_cruz.estado_financiero()
