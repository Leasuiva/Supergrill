/* ========================================================================== */
/* COCINA.JS - LÓGICA EXCLUSIVA PARA EL MONITOR DEL TELEVISOR                 */
/* ========================================================================== */

let versionActual = 0;

// 1. RELOJ EN TIEMPO REAL
setInterval(() => {
    const reloj = document.getElementById('reloj');
    if (reloj) reloj.innerText = new Date().toLocaleTimeString();
}, 1000);

// 2. AJUSTE DINÁMICO DE PANTALLA (Zoom automático)
function ajustarLetra() {
    if (window.innerWidth <= 700) return; 
    const contenedor = document.getElementById("contenedor");
    if (!contenedor) return;

    const alturaDisponible = window.innerHeight - contenedor.getBoundingClientRect().top - 15; 
    contenedor.style.maxHeight = alturaDisponible + "px";
    contenedor.style.overflow = "hidden"; 

    let size = 28;
    document.documentElement.style.fontSize = size + "px";
    void contenedor.offsetHeight; 

    let loop = 0;
    while ((contenedor.scrollHeight > contenedor.clientHeight || contenedor.scrollWidth > contenedor.clientWidth) && size > 8 && loop < 15) {
        size = size * 0.9; 
        document.documentElement.style.fontSize = size + "px";
        void contenedor.offsetHeight; 
        loop++;
    }
}

// 3. FESTEJO DE 300 PLATOS
function verificarMeta300(totalPlatos) {
    const fechaHoy = new Date().toLocaleDateString('es-AR');
    const yaFestejamos = localStorage.getItem("festejo_300_" + fechaHoy);

    if (totalPlatos >= 300 && !yaFestejamos) {
        localStorage.setItem("festejo_300_" + fechaHoy, "true");
        dispararVideoCelebracion();
    }
}

/* function dispararVideoCelebracion() {
    if (document.getElementById("overlayFestejo")) return;

    const overlay = document.createElement("div");
    overlay.id = "overlayFestejo";
    overlay.style.cssText = "position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.85); z-index: 9999; display: flex; justify-content: center; align-items: center;";

    const video = document.createElement("video");
    video.src = "/static/festejo300.mp4";
    video.style.cssText = "max-width: 95%; max-height: 95%; mix-blend-mode: screen; pointer-events: none;";
    video.controls = false;
    video.muted = false; 

    video.onended = () => overlay.remove();
    overlay.appendChild(video);
    document.body.appendChild(overlay);

    let promesaReproduccion = video.play();
    if (promesaReproduccion !== undefined) {
        promesaReproduccion.catch(() => {
            console.warn("Audio bloqueado por el navegador. Reproduciendo animación en silencio.");
            video.muted = true;
            video.play();
        });
    }
} */

// 4. OBTENER DATOS Y DIBUJAR TARJETAS
async function cargarDatos() {
    try {
        const dataP = await apiFetch(`/pedidos?t=${Date.now()}`);
        const dataC = await apiFetch(`/api/pedidos_cargados_data?t=${Date.now()}`);
        
        const todos = [...dataP, ...dataC.filter(p => (p[11] || "").toLowerCase() !== 'eliminado')];
        
        const conteoTipos = {};
        const conteoGuarnicion = {};
        let totalPlatosDelDia = 0; 
        let totalPedidosYa = 0; // NUEVA VARIABLE PARA EL RESUMEN

        todos.forEach(p => {
            const direccion = p[1]?.trim() || "";
            const cadete = p[8]?.trim() || "";
            const menu = p[4]?.trim();
            const guarnicion = p[5]?.trim();
            const cantidad = parseInt(p[7]) || 1;
            let tipo = p[13]?.trim() || "OTROS";

            const esPedidosYa = (direccion.toUpperCase() === "PEDIDOSYA" || cadete.toUpperCase() === "PEDIDOSYA");

            if (menu && menu !== "-" && menu !== "0") {
                totalPlatosDelDia += cantidad; 
                if (esPedidosYa) totalPedidosYa += cantidad; // SUMAMOS PEDIDOS YA

                if (!conteoTipos[tipo]) conteoTipos[tipo] = {};
                conteoTipos[tipo][menu] = (conteoTipos[tipo][menu] || 0) + cantidad;
            }
            if (guarnicion && guarnicion !== "-" && guarnicion !== "0") {
                conteoGuarnicion[guarnicion] = (conteoGuarnicion[guarnicion] || 0) + cantidad;
            }
        });
        
        dibujar(conteoTipos, conteoGuarnicion);
        
        // 👇 NUEVA LÓGICA: INYECTAR TOTALES SI ESTAMOS EN CELULAR 👇
        const divTotalesCelu = document.getElementById("totales-celular");
        if (divTotalesCelu) {
            let htmlTotales = `<div style="display:flex; align-items:center;">TOTAL: <span class="badge-total-celu">${totalPlatosDelDia}</span></div>`;
            
            // Si hay PedidosYa, le agregamos el cartelito rojo abajo
            if (totalPedidosYa > 0) {
                htmlTotales += `<div class="pedidos-ya-celu">🛵 Incluye ${totalPedidosYa} de PedidosYa</div>`;
            }
            
            divTotalesCelu.innerHTML = htmlTotales;
        }
        // 👆 FIN NUEVA LÓGICA 👆

        verificarMeta300(totalPlatosDelDia);
    } catch (e) { console.error("Error al cargar datos del monitor:", e); }
}

function dibujar(tipos, guarniciones) {
    const contenedor = document.getElementById("contenedor");
    if (!contenedor) return; 

    // DETECTAMOS SI ES CELULAR
    const esCelular = window.innerWidth <= 768;

    // GUARDAMOS EL ESTADO DE LOS MENÚS ABIERTOS (Para no frustrar al usuario si se actualiza la pantalla)
    const estadoAcordeones = {};
    if (esCelular) {
        document.querySelectorAll('.bloque').forEach(b => {
            const titulo = b.querySelector('.bloque-header span:first-child')?.innerText.trim();
            const lista = b.querySelector('.lista');
            if (titulo && lista && !lista.classList.contains('lista-oculta')) {
                estadoAcordeones[titulo] = true;
            }
        });
    }

    contenedor.innerHTML = "";
    const tarjetas = [];
    let totalLineas = 0;

    const crearBloqueElemento = (titulo, datos, esG) => {
        const div = document.createElement("div");
        div.className = "bloque";
        
        // Se agrega un span para el título y otro para el icono de la flecha
        let html = `<div class="bloque-header ${esG ? 'guarnicion' : ''}">
                        <span>${titulo}</span>
                        <span class="icono-desplegable">▼</span>
                    </div>
                    <ul class="lista">`;
                    
        const nombres = Object.keys(datos).sort();
        nombres.forEach(n => { html += `<li><span>${n}</span><span class="badge">${datos[n]}</span></li>`; });
        div.innerHTML = html + "</ul>";

        // LÓGICA DE MENÚ DESPLEGABLE (ACORDEÓN) SOLO PARA CELULARES
        if (esCelular) {
            const header = div.querySelector('.bloque-header');
            const lista = div.querySelector('.lista');
            const icono = div.querySelector('.icono-desplegable');

            // Si no estaba abierto previamente, lo ocultamos por defecto
            if (!estadoAcordeones[titulo]) {
                lista.classList.add('lista-oculta');
            } else {
                icono.classList.add('rotado');
            }

            header.addEventListener('click', () => {
                lista.classList.toggle('lista-oculta');
                icono.classList.toggle('rotado');
            });
        }

        const lineas = nombres.length + 2;
        totalLineas += lineas;
        return { elemento: div, cantidadItems: lineas };
    };

    // ORDEN PARA CELULAR: Guarniciones primero
    if (esCelular && Object.keys(guarniciones).length > 0) {
        tarjetas.push(crearBloqueElemento("GUARNICIONES", guarniciones, true));
    }

    // Luego el resto de los platos
    Object.keys(tipos).sort().forEach(t => tarjetas.push(crearBloqueElemento(t, tipos[t], false)));

    // ORDEN PARA TV/PC: Guarniciones al final (como estaba antes)
    if (!esCelular && Object.keys(guarniciones).length > 0) {
        tarjetas.push(crearBloqueElemento("GUARNICIONES", guarniciones, true));
    }

    // --- EL RESTO QUEDA IGUAL ---
    const maxColumnasPermitidas = Math.max(1, Math.floor(window.innerWidth / 300));
    const MAX_FILAS_COLUMNA = Math.max(12, Math.ceil(totalLineas / maxColumnasPermitidas));

    const columnasFinales = [];
    let columnaActual = [];
    let filasEnColumnaActual = 0;

    tarjetas.forEach(tarjeta => {
        if (columnaActual.length > 0 && (filasEnColumnaActual + tarjeta.cantidadItems > MAX_FILAS_COLUMNA)) {
            columnasFinales.push(columnaActual);
            columnaActual = [tarjeta];
            filasEnColumnaActual = tarjeta.cantidadItems;
        } else {
            columnaActual.push(tarjeta);
            filasEnColumnaActual += tarjeta.cantidadItems;
        }
    });

    if (columnaActual.length > 0) columnasFinales.push(columnaActual);

    contenedor.style.display = "flex";
    contenedor.style.flexWrap = "nowrap"; 
    contenedor.style.justifyContent = "center";
    contenedor.style.gap = "10px";
    contenedor.style.width = "100vw"; 
    contenedor.style.boxSizing = "border-box";
    contenedor.style.overflow = "hidden"; 

    const porcentajeAncho = (100 / columnasFinales.length) - 1; 

    columnasFinales.forEach(grupo => {
        const colDiv = document.createElement("div");
        colDiv.className = "columna";
        colDiv.style.flex = "1 1 0"; 
        colDiv.style.minWidth = "0"; 
        colDiv.style.maxWidth = `${porcentajeAncho}%`; 
        
        grupo.forEach(tarjeta => { colDiv.appendChild(tarjeta.elemento); });
        contenedor.appendChild(colDiv);
    });

    ajustarLetra();
}

// 5. ESCUCHA DE CAMBIOS DESDE EL SERVIDOR (Polling)
async function vigilarCambios() {
    try {
        const data = await apiFetch('/api/estado_monitor');
        if (data.version !== versionActual) {
            versionActual = data.version;
            cargarDatos(); 
        }
    } catch (e) { console.error("Error vigilando servidor:", e); }
}

// Inicializamos el monitor solo si estamos en la pantalla correcta
if (document.getElementById("contenedor")) {
    setInterval(vigilarCambios, 2000);
    vigilarCambios(); 
}

// --- BOTÓN REFRESCAR CELULAR (ILUMINA SOLO LOS CAMBIOS) ---
const botonRefrescar = document.getElementById('boton-refrescar');

if (botonRefrescar) {
    botonRefrescar.addEventListener('click', async function() {
        // 1. Sacamos una "foto" de las cantidades actuales
        const valoresViejos = obtenerCantidadesActuales();
        
        // 2. Traemos los datos nuevos (esto redibuja la pantalla)
        await cargarDatos(); 
        
        // 3. Comparamos lo nuevo con lo viejo y resaltamos las diferencias
        resaltarCambios(valoresViejos);
    });
}

// Función que lee la pantalla y guarda cuántos platos hay de cada cosa
function obtenerCantidadesActuales() {
    const estado = {};
    
    // Leemos cada plato individual
    document.querySelectorAll('.lista li').forEach(li => {
        // Agarramos el nombre de la categoría y del plato para que sea único (Ej: "HAMBURGUESAS-Completa")
        const categoria = li.closest('.bloque').querySelector('.bloque-header').innerText.trim();
        const nombrePlato = li.querySelector('span:first-child').innerText.trim();
        const cantidad = parseInt(li.querySelector('.badge').innerText.trim());
        
        estado[`${categoria}-${nombrePlato}`] = cantidad;
    });

    // Leemos el total del celular
    const badgeTotal = document.querySelector('.badge-total-celu');
    if (badgeTotal) {
        estado['TOTAL'] = parseInt(badgeTotal.innerText.trim());
    }
    
    return estado;
}

// Función que busca las diferencias y aplica el efecto
function resaltarCambios(valoresViejos) {
    // Revisamos cada plato nuevo redibujado
    document.querySelectorAll('.lista li').forEach(li => {
        const categoria = li.closest('.bloque').querySelector('.bloque-header').innerText.trim();
        const nombrePlato = li.querySelector('span:first-child').innerText.trim();
        const badge = li.querySelector('.badge');
        const cantidadNueva = parseInt(badge.innerText.trim());
        
        const clave = `${categoria}-${nombrePlato}`;

        // Si la cantidad cambió, o si es un plato que antes no estaba (undefined)
        if (valoresViejos[clave] !== cantidadNueva) {
            aplicarDestello(badge);
        }
    });

    // Revisamos si el total del celular también cambió
    const badgeTotal = document.querySelector('.badge-total-celu');
    if (badgeTotal) {
        const totalNuevo = parseInt(badgeTotal.innerText.trim());
        if (valoresViejos['TOTAL'] !== totalNuevo) {
            aplicarDestello(badgeTotal);
        }
    }
}

// Función cortita para poner y sacar la clase CSS
function aplicarDestello(elemento) {
    elemento.classList.add('badge-actualizado');
    // Le sacamos el brillo después de 1.5 segundos para que te dé tiempo a verlo
    setTimeout(() => {
        elemento.classList.remove('badge-actualizado');
    }, 1500); 
}