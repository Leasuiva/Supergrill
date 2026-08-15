/* ========================================================================== */
/* ARCHIVADOS.JS - LÓGICA EXCLUSIVA PARA LA PÁGINA DE ARCHIVOS HISTÓRICOS     */
/* ========================================================================== */

let almacenGruposArchivados = {}; 
let resultadosArchivadosActuales = [];

document.addEventListener("DOMContentLoaded", function () {
    // Escucha el buscador de texto en tiempo real
    const inputFiltro = document.getElementById('filtroTextoArchivados');
    if (inputFiltro) {
        inputFiltro.addEventListener('input', function() {
            const termino = this.value.toLowerCase().trim();
            
            if (!termino) {
                renderizarTablaArchivados(resultadosArchivadosActuales);
                return;
            }

            const filtrados = resultadosArchivadosActuales.filter(p => {
                const contenidoFila = [
                    p[1], // Dirección
                    p[2], // Empresa
                    p[3], // Nombre Cliente
                    p[4], // Menú
                    p[8]  // Cadete
                ].join(" ").toLowerCase();
                
                return contenidoFila.includes(termino);
            });
            
            renderizarTablaArchivados(filtrados);
        });
    }
});

// --- OBTENER DATOS DE LA API POR RANGO DE FECHAS ---
async function buscarPorRango() {
    const desde = document.getElementById('fechaDesde')?.value;
    const hasta = document.getElementById('fechaHasta')?.value;

    if (!desde || !hasta) return alert("⚠️ Selecciona ambas fechas.");

    try {
        const pedidos = await apiFetch(`/api/ver_archivados_rango?desde=${encodeURIComponent(desde)}&hasta=${encodeURIComponent(hasta)}`);
        
        resultadosArchivadosActuales = pedidos;
        almacenGruposArchivados = {}; 

        renderizarTablaArchivados(pedidos);

        const btnExportar = document.getElementById('btnExportarArchivados');
        if (btnExportar) {
            if (pedidos && pedidos.length > 0) {
                // Si hay pedidos, mostramos el botón
                btnExportar.style.display = 'inline-block';
            } else {
                // Si no hay pedidos, lo mantenemos oculto
                btnExportar.style.display = 'none';
            }
        }

    } catch (error) {
        alert(`❌ Error al cargar los datos del archivo: ${error.message}`);
    }
}
window.buscarPorRango = buscarPorRango;

// --- DIBUJAR LA TABLA HISTÓRICA ---
function renderizarTablaArchivados(pedidos) {
    const tbody = document.getElementById('cuerpoArchivados');
    if (!tbody) return;
    tbody.innerHTML = '';

    const template = document.getElementById("tpl-fila-archivados");
    if (!template) return console.error("Falta el template id='tpl-fila-archivados' en el HTML.");

    let totalMenus = 0;

    if (!pedidos || pedidos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:30px; color:#666;">No se encontraron pedidos.</td></tr>';
        actualizarCartelTotal(0); 
        return;
    }

    const gruposDireccion = {};
    pedidos.forEach(p => {
        const estado = String(p[10] || "").toLowerCase();
        if (estado !== 'eliminado') totalMenus += (parseInt(p[7]) || 1); 

        let dir = (p[1] && p[1] !== "0") ? p[1] : (p[2] && p[2] !== "0" ? p[2] : "🏠 RETIRA EN LOCAL");
        if (!gruposDireccion[dir]) gruposDireccion[dir] = [];
        gruposDireccion[dir].push(p);
    });

    actualizarCartelTotal(totalMenus);

    let contadorGruposVisual = 0;

    for (const direccion in gruposDireccion) {
        const pedidosDelGrupo = gruposDireccion[direccion];
        const filasTotales = pedidosDelGrupo.length;
        const esGrupoGris = (contadorGruposVisual % 2 !== 0);

        pedidosDelGrupo.forEach((p, index) => {
            const clone = template.content.cloneNode(true);
            const tr = clone.querySelector("tr");
            
            if (esGrupoGris) tr.classList.add('grupo-fondo-gris');
            
            const estado = String(p[10] || "").toLowerCase();
            if (estado === 'eliminado') tr.classList.add('fila-eliminada');

            const tdDireccion = tr.querySelector(".celda-direccion");
            const tdPedido = tr.querySelector(".celda-pedido");
            const tdCadete = tr.querySelector(".celda-cadete");
            const tdPago = tr.querySelector(".celda-pago");
            const tdEstado = tr.querySelector(".celda-estado");
            const tdFecha = tr.querySelector(".celda-fecha");

            const claseBorde = (index === filasTotales - 1) ? "borde-grupo" : "borde-interno";

            if (index === 0) {
                const direccionVisual = typeof formatearDireccionHtml === "function" ? formatearDireccionHtml(direccion) : direccion;
                const idClave = p[0]; 
                
                almacenGruposArchivados[idClave] = { pedidos: pedidosDelGrupo, direccionFull: direccionVisual };

                tdDireccion.setAttribute("rowspan", filasTotales);
                tdDireccion.querySelector(".titulo-direccion").innerHTML = direccionVisual;
                tdDireccion.querySelector(".btn-ver-cantidades-min").setAttribute("onclick", `abrirModalCantidadesDireccion(${idClave})`);
                
                tdCadete.setAttribute("rowspan", filasTotales);
                tdCadete.classList.add("borde-grupo");
                tdCadete.innerHTML = p[8] || '---';
            } else {
                tdDireccion.remove();
                tdCadete.remove();
            }

            let textoPedido = "";
            
            // Si el menú no es "0", armamos el texto con cantidad, guarnición y descripción
            if (p[4] && p[4] !== "0") {
                const guarnicion = p[5] && p[5] !== "0" ? ` con ${p[5]}` : "";
                const descripcion = p[6] && p[6] !== "0" ? ` <span style="font-size:0.9em; color:#555;">[${p[6]}]</span>` : "";
                textoPedido = `(${p[7]}) ${p[4]}${guarnicion}${descripcion}`;
            }

            // Agregamos el nombre del cliente si existe, asegurando que quede prolijo
            if (p[3] && p[3] !== "0" && p[3].trim() !== "") { 
                textoPedido += textoPedido === "" ? p[3] : ` - ${p[3]}`; 
            }

            tdPedido.className = `celda-pedido ${claseBorde}`;
            tdPedido.innerHTML = textoPedido;

            tdPago.className = `texto-centro celda-pago ${claseBorde}`;
            tdPago.innerHTML = p[9] || '---';

            tdEstado.className = `texto-centro borde-izquierdo-estado celda-estado ${claseBorde}`;
            tdEstado.innerHTML = p[10] || '---';

            tdFecha.classList.add(claseBorde);
            tdFecha.innerHTML = p[11];

            tbody.appendChild(tr);
        });
        contadorGruposVisual++;
    }
}

// --- CARTEL DE TOTALES DE LA BÚSQUEDA ---
function actualizarCartelTotal(total) {
    let divTotal = document.getElementById("cartelTotalArchivados");
    
    if (!divTotal) {
        const tabla = document.getElementById("cuerpoArchivados").closest("table");
        divTotal = document.createElement("div");
        divTotal.id = "cartelTotalArchivados";
        divTotal.style.cssText = "background-color: #042505; color: white; padding: 15px; text-align: center; font-size: 18px; font-weight: bold; border-radius: 5px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);";
        tabla.parentNode.insertBefore(divTotal, tabla);
    }
    
    const desde = document.getElementById('fechaDesde')?.value || "";
    const hasta = document.getElementById('fechaHasta')?.value || "";
    
    const formatear = (fecha) => {
        if (!fecha) return "";
        const partes = fecha.split("-");
        return partes.length === 3 ? `${partes[2]}/${partes[1]}/${partes[0]}` : fecha;
    };

    let textoRango = (desde && hasta) ? ` del ${formatear(desde)} al ${formatear(hasta)}` : "";
    divTotal.innerHTML = `📊 Total de menús vendidos${textoRango}: <span style="color: #9af1ae; font-size: 1.3em; margin-left: 10px;">${total}</span>`;
}

// --- MODAL DE CANTIDADES (Exclusivo de esta vista) ---
function abrirModalCantidadesDireccion(idClave) {
    const data = almacenGruposArchivados[idClave];
    if (!data) return;

    const modal = document.getElementById("modalCantidades");
    const contenedor = document.getElementById("contenedorTotalesUnificados");
    if (!modal || !contenedor) return;

    const conteoMenus = {};
    let totalComida = 0;

    data.pedidos.forEach(p => {
        const menu = p[4] || "Sin especificar";
        const cantidad = parseInt(p[7]) || 0;
        conteoMenus[menu] = (conteoMenus[menu] || 0) + cantidad;
        totalComida += cantidad;
    });

    modal.style.display = "block";
    
    contenedor.innerHTML = `
        <div class="modal-resumen-header">
            <h4 style="margin:0; color:#042505;">📍 ${data.direccionFull}</h4>
        </div>
        <div class="modal-resumen-body">
            <div class="bloque-tipo-menu" style="width: 100%; border:none; box-shadow:none;">
                <h5 style="background-color: #042505; color: white; border-radius: 4px 4px 0 0;">RESUMEN DEL PEDIDO</h5>
                <ul class="lista-totales">
                    ${Object.keys(conteoMenus).map(nombre => `
                        <li>
                            <span class="nombre-item" style="font-weight: bold;">${nombre}</span>
                            <span class="badge-conteo" style="background-color: #28a745;">${conteoMenus[nombre]}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
            <div class="modal-resumen-footer">
                TOTAL UNIDADES: <span style="color: #9af1ae; margin-left: 10px; font-size: 1.2em;">${totalComida}</span>
            </div>
        </div>
    `;
}
window.abrirModalCantidadesDireccion = abrirModalCantidadesDireccion;