def procesar_pdf(pdf):
    texto = leer_pdf(pdf)

    st.text_area("Texto detectado en el PDF", texto, height=300)

    # ✅ CORTAR TEXTO DESDE EL DETALLE
    if "Código Producto / Servicio" in texto:
        texto = texto.split("Código Producto / Servicio")[1]

    # ✅ DATOS BASE
    punto_venta = buscar(r"Punto de Venta:\s*(\d+)", texto)
    numero = buscar(r"Comp\.?\s*Nro:\s*\d+\s*(\d+)", texto)

    datos_base = {
        "Receptor": "SALUD METROPOLITANA SA",
        "CUIT Receptor": "30715602012",
        "Emisor": "PAPUS SRL",
        "CUIT Emisor": "30714997234",
        "Fecha": buscar(r"(\d{2}/\d{2}/\d{4})", texto),
        "Tipo": "FACTURA A",
        "Punto de Venta": punto_venta,
        "Número": numero,
    }

    filas = []
    buffer_descripcion = []

    lineas = [l.strip() for l in texto.split("\n") if l.strip()]

    for linea in lineas:

        # ✅ ESTA ES LA LÍNEA CLAVE (detalle)
        if "unidades" in linea and "%" in linea:

            # Cantidad correcta
            m_cant = re.search(r"X\s*(\d+),", linea)
            cantidad = int(m_cant.group(1)) if m_cant else 0

            # Importes
            nums = re.findall(r"\d+,\d+", linea)

            if len(nums) >= 4:
                precio = float(nums[1].replace(",", "."))
                subtotal = float(nums[3].replace(",", "."))
                total = float(nums[-1].replace(",", "."))
            else:
                precio = subtotal = total = 0

            filas.append({
                **datos_base,
                "Producto": " ".join(buffer_descripcion),
                "Cantidad": cantidad,
                "Unidad": "unidades",
                "Precio Unitario": precio,
                "Subtotal": subtotal,
                "IVA %": 21,
                "Total c/ IVA": total,
            })

            buffer_descripcion = []

        else:
            buffer_descripcion.append(linea)

    return filas
