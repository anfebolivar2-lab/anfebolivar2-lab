"""Genera tres plantillas de Excel en la carpeta de este script."""

from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

CARPETA = Path(__file__).resolve().parent
PESOS = "$#,##0"
FECHA = "dd/mm/yyyy"
ULTIMA_FILA = 301
EJEMPLO = date(2026, 1, 1)


def encabezado(celda):
    celda.fill = PatternFill("solid", fgColor="174C55")
    celda.font = Font(name="Calibri", bold=True, color="FFFFFF")
    celda.alignment = Alignment(vertical="center", wrap_text=True)


def anchos(hoja, valores):
    hoja.sheet_view.showGridLines = False
    for columna, ancho in zip("ABCDEFGHIJK", valores):
        hoja.column_dimensions[columna].width = ancho


def tabla(hoja, nombre, titulos, medidas, *, inicio=1, fin=ULTIMA_FILA):
    anchos(hoja, medidas)
    for columna, titulo in enumerate(titulos, 1):
        encabezado(hoja.cell(inicio, columna, titulo))
    hoja.row_dimensions[inicio].height = 32
    hoja.freeze_panes = f"A{inicio + 1}"
    letra_final = "ABCDEFGHIJK"[len(titulos) - 1]
    objeto = Table(displayName=nombre, ref=f"A{inicio}:{letra_final}{fin}")
    objeto.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2", showRowStripes=True
    )
    hoja.add_table(objeto)


def formato(hoja, formatos, inicio=2, fin=ULTIMA_FILA):
    for letra, tipo in formatos.items():
        for fila in range(inicio, fin + 1):
            hoja[f"{letra}{fila}"].number_format = tipo


def desplegable(hoja, rango, opciones):
    validacion = DataValidation(
        type="list", formula1='"' + ",".join(opciones) + '"',
        allow_blank=True, showErrorMessage=True, errorStyle="stop",
        errorTitle="Opción inválida", error="Selecciona un valor de la lista.",
    )
    hoja.add_data_validation(validacion)
    validacion.add(rango)


def instrucciones(libro, pasos):
    hoja = libro.create_sheet("Instrucciones")
    anchos(hoja, (92,))
    encabezado(hoja.cell(1, 1, "Cómo usar esta plantilla"))
    hoja.row_dimensions[1].height = 28
    for fila, paso in enumerate(pasos, 2):
        celda = hoja.cell(fila, 1, f"{fila - 1}. {paso}")
        celda.alignment = Alignment(wrap_text=True, vertical="center", indent=1)
        hoja.row_dimensions[fila].height = 34


def presupuesto():
    libro = Workbook()
    resumen = libro.active
    resumen.title = "Resumen"
    anchos(resumen, (32, 24))
    resumen.merge_cells("A1:B1")
    encabezado(resumen.cell(1, 1, "Presupuesto mensual"))
    resumen.row_dimensions[1].height = 30
    resumen["A3"], resumen["B3"] = "Mes de referencia", EJEMPLO
    resumen["B3"].number_format = "mmmm yyyy"
    resumen["B3"].fill = PatternFill("solid", fgColor="E2F2EF")

    for fila, concepto, hoja, monto, fecha in (
        (5, "Ingresos totales", "Ingresos", "C", "B"),
        (6, "Gastos totales", "Gastos", "D", "C"),
    ):
        resumen[f"A{fila}"] = concepto
        resumen[f"B{fila}"] = (
            f'=SUMIFS({hoja}!${monto}:${monto},{hoja}!${fecha}:${fecha},'
            f'">="&DATE(YEAR($B$3),MONTH($B$3),1),{hoja}!${fecha}:${fecha},'
            '"<"&DATE(YEAR($B$3),MONTH($B$3)+1,1))'
        )
    resumen["A7"], resumen["B7"] = "Ahorro", "=B5-B6"
    resumen["A8"], resumen["B8"] = "% de ahorro", "=IF(B5=0,0,B7/B5)"
    formato(resumen, {"B": PESOS}, 5, 7)
    resumen["B8"].number_format = "0.0%"
    for fila in (7, 8):
        for columna in (1, 2):
            encabezado(resumen.cell(fila, columna))
        resumen.row_dimensions[fila].height = 23

    ingresos = libro.create_sheet("Ingresos")
    tabla(ingresos, "TablaIngresos", ("Fuente", "Fecha", "Monto"), (36, 18, 19))
    ingresos.append(("Ingreso de ejemplo", EJEMPLO, 1500000))
    formato(ingresos, {"B": FECHA, "C": PESOS})

    gastos = libro.create_sheet("Gastos")
    tabla(gastos, "TablaGastos", ("Categoría", "Descripción", "Fecha", "Monto"),
          (22, 40, 18, 19))
    gastos.append(("Vivienda", "Alquiler de ejemplo", EJEMPLO, 550000))
    gastos.append(("Comida", "Compra de ejemplo", EJEMPLO.replace(day=5), 120000))
    formato(gastos, {"C": FECHA, "D": PESOS})
    desplegable(gastos, f"A2:A{ULTIMA_FILA}", (
        "Vivienda", "Comida", "Transporte", "Servicios", "Salud",
        "Educacion", "Ocio", "Otros",
    ))
    instrucciones(libro, (
        "Borra o reemplaza los registros de ejemplo y anota cada ingreso y gasto con su fecha.",
        "Selecciona la categoría de cada gasto y registra los montos como valores positivos.",
        "En Resumen, ingresa cualquier fecha del mes que quieras consultar en la celda B3.",
        "El porcentaje de ahorro se calcula sobre los ingresos del mes. Si son cero, se muestra 0 %.",
    ))
    return libro


def inventario():
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Inventario"
    titulos = (
        "Código", "Producto", "Categoría", "Stock inicial", "Entradas", "Salidas",
        "Stock actual", "Stock mínimo", "Costo unitario", "Valor en inventario", "Alerta",
    )
    tabla(hoja, "TablaInventario", titulos, (16, 27, 20, 15, 12, 12, 15, 15, 17, 22, 16))
    hoja.append(("EJ-001", "Producto ejemplo 1", "Categoría ejemplo", 10, None, None,
                 None, 5, 12000))
    hoja.append(("EJ-002", "Producto ejemplo 2", "Categoría ejemplo", 20, None, None,
                 None, 8, 8000))
    formato(hoja, {"A": "@", "I": PESOS, "J": PESOS})

    for fila in range(2, ULTIMA_FILA + 1):
        for columna, tipo in (("E", "Entrada"), ("F", "Salida")):
            hoja[f"{columna}{fila}"] = (
                f'=IF(A{fila}="","",SUMIFS(Movimientos!$D:$D,'
                f'Movimientos!$B:$B,A{fila},Movimientos!$C:$C,"{tipo}"))'
            )
        hoja[f"G{fila}"] = f'=IF(A{fila}="","",D{fila}+E{fila}-F{fila})'
        hoja[f"J{fila}"] = f'=IF(OR(A{fila}="",I{fila}=""),"",G{fila}*I{fila})'
        hoja[f"K{fila}"] = (
            f'=IF(AND(A{fila}<>"",H{fila}<>"",G{fila}<=H{fila}),"REPONER","")'
        )
    hoja.conditional_formatting.add(
        f"A2:K{ULTIMA_FILA}",
        FormulaRule(formula=['$K2="REPONER"'],
                    fill=PatternFill("solid", fgColor="FCE1E1")),
    )

    movimientos = libro.create_sheet("Movimientos")
    tabla(movimientos, "TablaMovimientos", ("Fecha", "Código", "Tipo", "Cantidad"),
          (18, 18, 22, 15))
    movimientos.append((EJEMPLO, "EJ-001", "Entrada", 2))
    movimientos.append((EJEMPLO.replace(day=7), "EJ-001", "Salida", 7))
    movimientos.append((EJEMPLO.replace(day=8), "EJ-002", "Entrada", 5))
    formato(movimientos, {"A": FECHA, "B": "@"})
    desplegable(movimientos, f"C2:C{ULTIMA_FILA}", ("Entrada", "Salida"))
    instrucciones(libro, (
        "Reemplaza los datos de ejemplo de ambas hojas por tus propios productos y movimientos.",
        "Asigna un código único a cada producto y completa el stock inicial, el mínimo y el costo.",
        "Registra cada entrada o salida con el mismo código y una cantidad positiva.",
        "El inventario muestra REPONER cuando el stock actual llega al mínimo o queda por debajo.",
    ))
    return libro


def factura():
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Factura"
    hoja.merge_cells("A1:D1")
    encabezado(hoja.cell(1, 1, "Factura"))
    hoja.row_dimensions[1].height = 34

    for columna, titulo in (("A", "Datos del emisor"), ("C", "Datos del cliente")):
        encabezado(hoja[f"{columna}3"])
        hoja.merge_cells(f"{columna}3:{'B' if columna == 'A' else 'D'}3")
    for fila, emisor, cliente in (
        (4, "Emisor ejemplo", "Cliente ejemplo"),
        (5, "Identificación: EJ-EMISOR", "Identificación: EJ-CLIENTE"),
        (6, "Dirección: Calle Ejemplo 100", "Dirección: Calle Ejemplo 200"),
    ):
        hoja.merge_cells(start_row=fila, start_column=1, end_row=fila, end_column=2)
        hoja.merge_cells(start_row=fila, start_column=3, end_row=fila, end_column=4)
        hoja[f"A{fila}"], hoja[f"C{fila}"] = emisor, cliente
        hoja.row_dimensions[fila].height = 20
    hoja["A8"], hoja["B8"] = "Número de factura", "EJ-0001"
    hoja["C8"], hoja["D8"] = "Fecha de factura", EJEMPLO
    hoja["D8"].number_format = FECHA
    for celda in ("A8", "C8"):
        hoja[celda].font = Font(bold=True)

    tabla(hoja, "TablaDetalleFactura", ("Descripción", "Cantidad", "Precio unitario", "Total"),
          (44, 18, 20, 22), inicio=10, fin=25)
    hoja["A11"], hoja["B11"], hoja["C11"] = "Servicio de ejemplo", 2, 40000
    hoja["A12"], hoja["B12"], hoja["C12"] = "Producto de ejemplo", 1, 15000
    for fila in range(11, 26):
        hoja[f"D{fila}"] = f'=IF(OR(B{fila}="",C{fila}=""),"",B{fila}*C{fila})'
        hoja.row_dimensions[fila].height = 19
    formato(hoja, {"C": PESOS, "D": PESOS}, 11, 25)

    hoja["C27"], hoja["D27"] = "Subtotal", "=SUM(D11:D25)"
    hoja["A28"], hoja["B28"] = "Tasa de IVA editable", 0.19
    hoja["B28"].number_format = "0.00%"
    hoja["B28"].fill = PatternFill("solid", fgColor="E2F2EF")
    hoja["C28"], hoja["D28"] = "IVA", "=ROUND(D27*B28,0)"
    hoja["C29"], hoja["D29"] = "Total", "=SUM(D27:D28)"
    formato(hoja, {"D": PESOS}, 27, 29)
    for celda in ("C29", "D29"):
        encabezado(hoja[celda])
    hoja.row_dimensions[29].height = 25

    hoja.print_area = "A1:D29"
    hoja.sheet_properties.pageSetUpPr.fitToPage = True
    hoja.page_setup.orientation = "portrait"
    hoja.page_setup.paperSize = hoja.PAPERSIZE_A4
    hoja.page_setup.fitToWidth = 1
    hoja.page_setup.fitToHeight = 1
    hoja.print_options.horizontalCentered = True

    instrucciones(libro, (
        "Reemplaza los datos ficticios del emisor y del cliente. Ingresa el número y la fecha.",
        "Reemplaza los conceptos de ejemplo e indica la cantidad y el precio unitario de cada ítem.",
        "Escribe la tasa de IVA aplicable en B28 como porcentaje. El 19 % es un ejemplo.",
        "Imprime la hoja Factura desde la vista previa. El formato está preparado para una página A4.",
    ))
    return libro


def main():
    for nombre, crear in (
        ("Presupuesto-mensual.xlsx", presupuesto),
        ("Control-inventario.xlsx", inventario),
        ("Plantilla-facturas.xlsx", factura),
    ):
        crear().save(CARPETA / nombre)


if __name__ == "__main__":
    main()
