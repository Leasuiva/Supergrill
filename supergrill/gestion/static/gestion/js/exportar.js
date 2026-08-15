/* ========================================================================== */
/* EXPORTAR.JS - LÓGICA PARA EXPORTAR DATOS A EXCEL REAL (.XLSX)              */
/* ========================================================================== */

async function exportarExcel() {
    // Verificamos que la librería se haya cargado correctamente en el HTML
    if (typeof XLSX === "undefined") {
        alert("❌ Error: No se pudo cargar la librería de Excel. Revisá tu conexión a internet.");
        return;
    }

    try {
        // 1. Traemos los datos frescos de la base de datos
        const res = await fetch("/api/pedidos_cargados_data");
        let data = await res.json();
        
        // Filtramos para dejar afuera los eliminados
        data = data.filter(row => String(row[11] || "").toLowerCase().trim() !== "eliminado");
        
        if (!data || data.length === 0) {
            alert("⚠️ No hay pedidos cargados válidos para exportar.");
            return;
        }

        // 2. Preparamos la matriz de datos para Excel (La primera fila son las cabeceras)
        const datosExcel = [
            ["ID", "Dirección", "Empresa", "Nombre Cliente", "Menú", "Guarnición", "Descripción", "Cantidad", "Cadete", "Forma de Pago", "Estado"]
        ];

        // 3. Llenamos las filas limpiando los ceros
        data.forEach(row => {
            let direccion = row[1];
            let empresa = row[2];
            
            // Si no tiene dirección ni empresa, le ponemos "Retira" para que quede prolijo
            if ((!direccion || direccion === "0") && (!empresa || empresa === "0")) {
                direccion = "Retira en el local";
            }

            const fila = [
                row[0],                               // ID
                direccion,                            // Dirección
                empresa === "0" ? "" : empresa,       // Empresa
                row[3] === "0" ? "" : row[3],         // Nombre
                row[4] === "0" ? "" : row[4],         // Menú
                row[5] === "0" ? "" : row[5],         // Guarnición
                row[6] === "0" ? "" : row[6],         // Descripción
                row[7],                               // Cantidad
                row[8] === "0" ? "" : row[8],         // Cadete
                row[9] === "0" ? "" : row[9],         // Forma Pago
                row[10] === "0" ? "" : row[10]        // Estado
            ];
            
            datosExcel.push(fila);
        });

        // 4. Creamos el Libro de Trabajo y la Hoja
        const hoja = XLSX.utils.aoa_to_sheet(datosExcel);
        const libro = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(libro, hoja, "Pedidos del Día");

        // 5. Ajustamos el ancho de las columnas para que quede prolijo al abrirlo
        hoja['!cols'] = [
            { wch: 5 },   // ID
            { wch: 30 },  // Dirección (Ancha)
            { wch: 15 },  // Empresa
            { wch: 20 },  // Nombre
            { wch: 25 },  // Menú
            { wch: 15 },  // Guarnición
            { wch: 35 },  // Descripción (Muy Ancha)
            { wch: 10 },  // Cantidad
            { wch: 15 },  // Cadete
            { wch: 15 },  // Forma Pago
            { wch: 15 }   // Estado
        ];

        // 6. Generamos el archivo físico .xlsx y forzamos la descarga
        const fecha = new Date().toLocaleDateString('es-AR').replace(/\//g, '-');
        XLSX.writeFile(libro, `Supergrill_Pedidos_${fecha}.xlsx`);
        
    } catch (e) {
        console.error("Error exportando a Excel:", e);
        alert("❌ Hubo un error al generar el archivo Excel.");
    }
}
window.exportarExcel = exportarExcel;

// Funcion para exportar los datos en la parte de archivados.
async function exportarExcelArchivados() {
    // Verificamos que la librería se haya cargado correctamente en el HTML[cite: 1]
    if (typeof XLSX === "undefined") {
        alert("❌ Error: No se pudo cargar la librería de Excel. Revisá tu conexión a internet.");
        return;
    }

    try {
        // 1. Tomamos los datos de la variable global de archivados.js[cite: 3]
        let data = resultadosArchivadosActuales; 
        
        if (!data || data.length === 0) {
            alert("⚠️ No hay pedidos archivados válidos para exportar.");
            return;
        }

        // 2. Filtramos para dejar afuera los eliminados (usando el índice 10 como en archivados.js)[cite: 3]
        data = data.filter(row => String(row[10] || "").toLowerCase().trim() !== "eliminado");

        // 3. Preparamos la matriz de datos sumando la columna "Fecha" al final[cite: 1]
        const datosExcel = [
            ["ID", "Dirección", "Empresa", "Nombre Cliente", "Menú", "Guarnición", "Descripción", "Cantidad", "Cadete", "Forma de Pago", "Estado", "Fecha"]
        ];

        // 4. Llenamos las filas limpiando los ceros[cite: 1]
        data.forEach(row => {
            let direccion = row[1];
            let empresa = row[2];
            
            if ((!direccion || direccion === "0") && (!empresa || empresa === "0")) {
                direccion = "Retira en el local";
            }

            const fila = [
                row[0],                               // ID
                direccion,                            // Dirección
                empresa === "0" ? "" : empresa,       // Empresa
                row[3] === "0" ? "" : row[3],         // Nombre
                row[4] === "0" ? "" : row[4],         // Menú
                row[5] === "0" ? "" : row[5],         // Guarnición
                row[6] === "0" ? "" : row[6],         // Descripción
                row[7],                               // Cantidad
                row[8] === "0" ? "" : row[8],         // Cadete
                row[9] === "0" ? "" : row[9],         // Forma Pago
                row[10] === "0" ? "" : row[10],       // Estado
                row[11]                               // Fecha[cite: 3]
            ];
            
            datosExcel.push(fila);
        });

        // 5. Creamos el Libro de Trabajo y la Hoja[cite: 1]
        const hoja = XLSX.utils.aoa_to_sheet(datosExcel);
        const libro = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(libro, hoja, "Archivados");

        // 6. Ajustamos el ancho de las columnas (sumamos la columna fecha)[cite: 1]
        hoja['!cols'] = [
            { wch: 5 },   // ID
            { wch: 30 },  // Dirección
            { wch: 15 },  // Empresa
            { wch: 20 },  // Nombre
            { wch: 25 },  // Menú
            { wch: 15 },  // Guarnición
            { wch: 35 },  // Descripción
            { wch: 10 },  // Cantidad
            { wch: 15 },  // Cadete
            { wch: 15 },  // Forma Pago
            { wch: 15 },  // Estado
            { wch: 15 }   // Fecha
        ];

        // 7. Generamos el archivo físico con las fechas en el nombre[cite: 1]
        const desde = document.getElementById('fechaDesde')?.value || "Inicio";
        const hasta = document.getElementById('fechaHasta')?.value || "Fin";
        XLSX.writeFile(libro, `Supergrill_Archivados_${desde}_al_${hasta}.xlsx`);
        
    } catch (e) {
        console.error("Error exportando a Excel:", e);
        alert("❌ Hubo un error al generar el archivo Excel.");
    }
}
window.exportarExcelArchivados = exportarExcelArchivados;