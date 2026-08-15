/* ========================================================================== */
/* TOTALES.JS - CÁLCULOS Y MODAL DE RESUMEN DE CANTIDADES                     */
/* ========================================================================== */

let ultimoEstadoCantidades = {}; 
let primeraCargaHecha = false; 

async function abrirModalCantidades() {
    const modal = document.getElementById("modalCantidades");
    const contenedor = document.getElementById("contenedorTotalesUnificados");

    if (contenedor && !primeraCargaHecha) contenedor.innerHTML = "<p style='width:100%; text-align:center; padding:20px; color:#666;'>⏳ Calculando...</p>";
    if (modal) { modal.style.display = "block"; document.body.classList.add("modal-open"); }

    try {
        const datosPendientes = await apiFetch(`/pedidos?t=${Date.now()}`); 
        const datosCargados = await apiFetch(`/api/pedidos_cargados_data?t=${Date.now()}`); 

        const cargadosValidos = datosCargados.filter(p => (p[11] || "").toLowerCase() !== 'eliminado');
        const todos = [...datosPendientes, ...cargadosValidos];

        const conteoTipos = {}; 
        const conteoGuarnicion = {};
        const conteoPedidosYa = {}; 
        let totalGeneralMenues = 0;
        const estadoActual = {}; 

        todos.forEach(p => {
            const direccion = p[1] ? p[1].trim() : ""; 
            const cadete = p[8] ? p[8].trim() : "";
            const menu = p[4] ? p[4].trim() : "";
            const guarnicion = p[5] ? p[5].trim() : "";
            const cantidad = parseInt(p[7]) || 1;
            let tipoMenu = p[13] ? p[13].trim() : "OTROS"; 
            if(tipoMenu === "") tipoMenu = "OTROS";

            const esPedidosYa = (direccion.toUpperCase() === "PEDIDOSYA" || cadete.toUpperCase() === "PEDIDOSYA");
            
            if (esPedidosYa && menu && menu !== "-" && menu !== "0") {
                let nombreCombinado = menu;
                if (guarnicion && guarnicion !== "-" && guarnicion !== "0") nombreCombinado += " con " + guarnicion; 
                conteoPedidosYa[nombreCombinado] = (conteoPedidosYa[nombreCombinado] || 0) + cantidad;
                estadoActual[`PY_${nombreCombinado}`] = conteoPedidosYa[nombreCombinado];
            }

            if (menu && menu !== "-" && menu !== "0") {
                if (!conteoTipos[tipoMenu]) conteoTipos[tipoMenu] = {};
                conteoTipos[tipoMenu][menu] = (conteoTipos[tipoMenu][menu] || 0) + cantidad;
                if (!esPedidosYa) totalGeneralMenues += cantidad;
                estadoActual[`MENU_${tipoMenu}_${menu}`] = (conteoTipos[tipoMenu][menu]);
            }

            if (guarnicion && guarnicion !== "-" && guarnicion !== "0") {
                conteoGuarnicion[guarnicion] = (conteoGuarnicion[guarnicion] || 0) + cantidad;
                estadoActual[`GUARN_${guarnicion}`] = (conteoGuarnicion[guarnicion]);
            }
        });

        if (contenedor) {
            contenedor.innerHTML = ""; 
            const tiposOrdenados = Object.keys(conteoTipos).sort();
            const hayGuarniciones = Object.keys(conteoGuarnicion).length > 0;
            const hayPedidosYa = Object.keys(conteoPedidosYa).length > 0; 

            if (tiposOrdenados.length === 0 && !hayGuarniciones && !hayPedidosYa) {
                 contenedor.innerHTML = "<div style='padding:20px; text-align:center; color:rgba(70, 235, 55, 0.6); grid-column: 1 / -1;'>Sin datos hoy.</div>";
            } else {
                const crearBloque = (titulo, datos, tipoBloque = "normal") => {
                    const div = document.createElement("div");
                    div.className = "bloque-tipo-menu"; 
                    div.style.display = "flex";
                    div.style.flexDirection = "column";

                    let estiloExtra = "text-align: left !important; padding-left: 10px;"; 
                    let claseHeader = "";
                    if (tipoBloque === "guarnicion") claseHeader = "header-oscuro";
                    else if (tipoBloque === "pedidosya") estiloExtra += " background-color: #ec0808; color: white; border-radius: 4px 4px 0 0;";

                    div.innerHTML = `<h5 class="${claseHeader}" style="${estiloExtra}">${titulo}</h5>`;
                    const ul = document.createElement("ul");
                    ul.className = "lista-totales"; 

                    let totalBloque = 0; 
                    Object.keys(datos).sort().forEach(nombre => {
                        const cantidad = datos[nombre];
                        totalBloque += cantidad; 
                        
                        const li = document.createElement("li");
                        let claveUnica = "";
                        if (tipoBloque === "guarnicion") claveUnica = `GUARN_${nombre}`;
                        else if (tipoBloque === "pedidosya") claveUnica = `PY_${nombre}`;
                        else claveUnica = `MENU_${titulo}_${nombre}`;

                        const cantidadAnterior = ultimoEstadoCantidades[claveUnica] || 0;
                        if (primeraCargaHecha && cantidad !== cantidadAnterior) li.className = "item-actualizado"; 
                        li.innerHTML = `<span class="nombre-item">${nombre}</span><span class="badge-conteo">${cantidad}</span>`;
                        ul.appendChild(li);
                    });
                    
                    div.appendChild(ul);
                    if (tipoBloque === "pedidosya") {
                        const barraGruesa = document.createElement("div");
                        barraGruesa.style.cssText = "background-color: #000000; color: white; text-align: center; font-size: 12px; font-weight: bold; padding: 4px; margin-top: auto; border-radius: 0 0 4px 4px; box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);";
                        barraGruesa.innerHTML = `TOTAL: ${totalBloque}`;
                        div.appendChild(barraGruesa);
                    }
                    contenedor.appendChild(div);
                };

                tiposOrdenados.forEach(tipo => crearBloque(tipo, conteoTipos[tipo], "normal"));
                if (hayGuarniciones) crearBloque("GUARNICIONES", conteoGuarnicion, "guarnicion");
                if (hayPedidosYa) crearBloque("🛵 PEDIDOS YA", conteoPedidosYa, "pedidosya");
            }
            
            const footer = document.querySelector(".modal-footer-custom");
            const viejoTotalGeneral = document.getElementById("barraTotalGeneral");
            if (viejoTotalGeneral) viejoTotalGeneral.remove();
            
            if (totalGeneralMenues > 0 && footer) {
                const divTotal = document.createElement("div");
                divTotal.id = "barraTotalGeneral";
                divTotal.className = "barra-total-negra";
                divTotal.innerHTML = `TOTAL: ${totalGeneralMenues}`;
                footer.prepend(divTotal);
            }
        }
        
        const modalDOM = document.getElementById("modalCantidades");
        if (modalDOM) {
            const cantidadPlatos = Object.keys(estadoActual).length;
            if (cantidadPlatos > 14) modalDOM.classList.add("modo-compacto");
            else modalDOM.classList.remove("modo-compacto");
        }

        ultimoEstadoCantidades = estadoActual;
        primeraCargaHecha = true; 
    } catch (err) { console.error(err); }
}

function cerrarModalCantidades() {
    const modal = document.getElementById("modalCantidades");
    if (modal) {
        modal.style.display = "none";
        document.body.classList.remove("modal-open");
    }
}

window.abrirModalCantidades = abrirModalCantidades;
window.cerrarModalCantidades = cerrarModalCantidades;