/* ========================================================================== */
/* SUGERENCIAS.JS - MOTOR DE AUTOCOMPLETADO Y LISTAS DESPLEGABLES             */
/* ========================================================================== */

async function fetchYMostrarSugerencias(idUl, url, filtro = "") {
    try {
        const res = await fetch(url);
        const lista = await res.json();
        mostrarSugerencias(idUl, lista, filtro);
    } catch (error) {
        console.error("Error al obtener datos para sugerencias:", error);
    }
}

function mostrarSugerencias(ulElement, lista, filtro) {
    if (typeof ulElement === "string") {
        ulElement = document.getElementById(ulElement);
    }
    if (!ulElement) return;

    // Forzamos el cierre de otras sugerencias y del menú flotante para evitar solapamientos
    document.querySelectorAll("ul.sugerencias").forEach(otraUl => {
        if (otraUl !== ulElement) {
            otraUl.innerHTML = "";
            otraUl.style.display = "none";
        }
    });
    const menuAgregar = document.getElementById("menuAgregarItems");
    if (menuAgregar) menuAgregar.classList.add("oculto");

    ulElement.innerHTML = "";

    const input = ulElement.previousElementSibling?.querySelector("input[type='text']") 
                || ulElement.parentElement.querySelector("input[type='text']");
    
    if (input) {
        ulElement.style.width = `${input.offsetWidth}px`;
    }

    let filtradas = lista.filter(item => item.toLowerCase().includes(filtro.toLowerCase()));

    if (input?.readOnly && !filtradas.includes("")) {
        filtradas.unshift(""); 
    }

    if (filtradas.length === 0) {
        ulElement.style.display = "none";
        return;
    }

    ulElement.style.display = "block";

    filtradas.forEach(item => {
        const li = document.createElement("li");
        
        if (item === "") {
            li.textContent = "(Sin opción)";
            li.style.fontStyle = "italic";
            li.style.color = "#666";
            li.style.fontSize = "0.9em";
        } else {
            let tipoCampo = null;
            if (input) {
                if (input.classList.contains("tipo_menu") || input.name === "tipo_menu") tipoCampo = "tipo_menu";
                else if (input.classList.contains("menu") || input.name === "menu") tipoCampo = "menu";
                else if (input.classList.contains("guarnicion") || input.name === "guarnicion") tipoCampo = "guarnicion";
                else if (input.name === "cadete" || input.id === "cadete" || input.id === "edit_cadete") tipoCampo = "cadete";
                else if (input.classList.contains("forma_pago") || input.name === "forma_pago" || input.id === "edit_forma_pago") tipoCampo = "forma_pago";
            }

            if (tipoCampo) {
                li.style.display = "flex";
                li.style.justifyContent = "space-between";
                li.style.alignItems = "center";
                li.style.paddingRight = "5px"; 

                const spanTexto = document.createElement("span");
                spanTexto.textContent = item;
                li.appendChild(spanTexto);

                const spanCruz = document.createElement("span");
                spanCruz.innerHTML = "&times;"; 
                spanCruz.style.color = "#3d0215";
                spanCruz.style.fontWeight = "bold";
                spanCruz.style.fontSize = "15px";
                spanCruz.style.cursor = "pointer";
                spanCruz.style.padding = "0 5px";
                spanCruz.title = "Eliminar permanentemente";
                
                spanCruz.style.opacity = "0"; 
                spanCruz.style.transition = "opacity 0.2s ease-in-out"; 

                li.addEventListener("mouseenter", () => spanCruz.style.opacity = "1");
                li.addEventListener("mouseleave", () => spanCruz.style.opacity = "0");

                spanCruz.addEventListener("click", async (e) => {
                    e.stopPropagation(); 
                    if (confirm(`¿Estás seguro de eliminar "${item}" permanentemente?`)) {
                        let tipoBackend = "";
                        if (tipoCampo === "tipo_menu") tipoBackend = "tipo_menu";
                        else if (tipoCampo === "menu") tipoBackend = "menus";
                        else if (tipoCampo === "guarnicion") tipoBackend = "guarniciones";
                        else if (tipoCampo === "cadete") tipoBackend = "cadetes"; 
                        else if (tipoCampo === "forma_pago") tipoBackend = "forma_pago"; 

                        try {
                            const res = await fetch("/api/eliminar_item_config", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({ tipo: tipoBackend, id_item: item })
                            });
                            
                                if (res.ok) {
                                // 1. Ocultamos y vaciamos la lista de sugerencias de golpe
                                ulElement.innerHTML = "";
                                ulElement.style.display = "none";
                                
                                // 2. Si el input tenía escrito el ítem que borramos, lo limpiamos
                                if (input && input.value === item) {
                                    input.value = "";
                                    // Le avisamos al sistema que el input cambió
                                    input.dispatchEvent(new Event('input', { bubbles: true }));
                                }
                            } else {
                                alert("❌ Error al intentar eliminar.");
                            }
                        } catch(err) { 
                            console.error(err); 
                            alert("❌ Error de conexión.");
                        }
                    }
                });
                li.appendChild(spanCruz);
            } else {
                li.textContent = item;
            }
        }

        li.setAttribute("tabindex", "0");
        
        li.addEventListener("click", () => {
            let valorFinal = item;
            
            if (input.id.includes("direccion")) {
                const prefix = input.id.startsWith("edit_") ? "edit_" : "";
                let piso = "", depto = "", timbre = "";

                const matchPiso = valorFinal.match(/Piso[:]?\s+"([^"]+)"/i);
                if (matchPiso) { piso = matchPiso[1]; valorFinal = valorFinal.replace(matchPiso[0], ""); }

                const matchDepto = valorFinal.match(/Dpto[:]?\s+"([^"]+)"/i);
                if (matchDepto) { depto = matchDepto[1]; valorFinal = valorFinal.replace(matchDepto[0], ""); }

                const matchTimbre = valorFinal.match(/(?:Tbre|Timb|Timbre)[:]?\s+"([^"]+)"/i);
                if (matchTimbre) { timbre = matchTimbre[1]; valorFinal = valorFinal.replace(matchTimbre[0], ""); }

                valorFinal = valorFinal.trim().replace(/,$/, "").trim();

                const inPiso = document.getElementById(prefix + "piso");
                const inDepto = document.getElementById(prefix + "depto");
                const inTimbre = document.getElementById(prefix + "timbre");

                if (inPiso) inPiso.value = piso;
                if (inDepto) inDepto.value = depto;
                if (inTimbre) inTimbre.value = timbre;
            }

            input.value = valorFinal;
            ulElement.innerHTML = "";
            ulElement.style.display = "none";

            const idOname = input.id || input.name; 
            const tipoLimpio = idOname.replace("edit_", "");
            
            if (tipoLimpio === "direccion" || tipoLimpio === "empresa") {
                const esEdicion = input.id.startsWith("edit_");
                // Asegurate de que cargarCadeteFrecuente siga existiendo en tu main.js
                if (typeof cargarCadeteFrecuente === 'function') {
                    cargarCadeteFrecuente(tipoLimpio, item, esEdicion);
                }
            }

            if (input.classList.contains("tipo_menu")) {
                if (input.id === "edit_tipo_menu") {
                    const editMenu = document.getElementById("edit_menu");
                    if (editMenu) {
                        editMenu.value = ""; 
                        setTimeout(() => editMenu.focus(), 100); 
                    }
                } else {
                    const fila = input.closest(".fila-pedido");
                    if (fila) {
                        const menuInput = fila.querySelector(".menu");
                        if (menuInput) menuInput.value = "";
                    }
                }
            }
        });

        li.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                li.click(); 
            } else if (e.key === "Tab") {
                const siguiente = li.nextElementSibling;
                if (!siguiente) {
                    ulElement.innerHTML = "";
                    ulElement.style.display = "none";
                }
            }
        });

        ulElement.appendChild(li);
    });
}

function limpiarSugerencias(id) {
    const ul = document.getElementById(id);
    if (ul) {
        ul.innerHTML = "";
        ul.style.display = "none";
    }
}

async function mostrarTodo(elemento) {
    let campo, input, ul;

    if (elemento.tagName === "INPUT") {
        input = elemento;
        campo = input.closest(".campo");
    } else {
        campo = elemento.closest(".campo");
        if (campo) input = campo.querySelector("input[type='text']");
    }

    // 👇 EL ESCUDO: Si no encontró la clase ".campo", cancelamos silenciosamente
    if (!campo) return;

    ul = campo.querySelector("ul.sugerencias");
    if (!input || !ul) return;

    document.querySelectorAll("ul.sugerencias").forEach(otraUl => {
        if (otraUl !== ul) {
            otraUl.innerHTML = "";
            otraUl.style.display = "none";
        }
    });

    // Cerramos el menú de agregar ítems
    const menuAgregar = document.getElementById("menuAgregarItems");
    if (menuAgregar) menuAgregar.classList.add("oculto");

    if (ul.style.display === "block") {
        ul.innerHTML = "";
        ul.style.display = "none";
        return;
    }

    const campoNombre = input.name || input.className;
    let url = "";

    if (campoNombre === "menu") {
        const fila = input.closest(".fila-dos");
        const inputTipoMenu = fila.querySelector("input[name='tipo_menu']");
        const tipo = inputTipoMenu?.value;
        
        if (!tipo) {
            let errorMsj = campo.querySelector(".msj-error-menu");
            if (!errorMsj) {
                errorMsj = document.createElement("span");
                errorMsj.className = "msj-error-menu";
                errorMsj.textContent = "Seleccioná un tipo primero";
                errorMsj.style.color = "#d32f2f";
                errorMsj.style.fontSize = "9px";
                errorMsj.style.fontWeight = "bold";
                errorMsj.style.position = "absolute";
                errorMsj.style.top = "100%"; 
                errorMsj.style.left = "0";
                errorMsj.style.marginTop = "2px";
                campo.appendChild(errorMsj);
                setTimeout(() => {
                    if (errorMsj.parentNode) errorMsj.remove();
                }, 3000);
            }
            return; 
        }
        url = `/menus_por_tipo/${encodeURIComponent(tipo)}`;
    } else {
        const rutas = {
            direccion: "/direcciones",
            empresa: "/empresas",
            nombre: "/nombres",
            cadete: "/cadetes",
            tipo_menu: "/tipo_menu",
            guarnicion: "/guarniciones",
            descripcion: "/descripciones",
            forma_pago: "/forma_pago",
            estado: "/estados"
        };
        url = rutas[campoNombre];
        if (!url) return;
    }

    try {
        const res = await fetch(url);
        const lista = await res.json();
        mostrarSugerencias(ul, lista, "");
        ul.style.display = "block";
    } catch (error) {
        console.error("Error al mostrar lista completa:", error);
    }
}
window.mostrarTodo = mostrarTodo;

async function actualizarSugerenciasMenuPorTipo() {
    const tipoSeleccionado = document.getElementById("modal_tipo_menu").value;
    if (!tipoSeleccionado) return; 
    
    try {
        const res = await fetch(`/api/sugerencias_menus_por_tipo/${encodeURIComponent(tipoSeleccionado)}`);
        if (!res.ok) return;
        const data = await res.json();

        const input = document.getElementById('modal_nombre_menu');
        let datalistId = `datalist_modal_nombre_menu`;
        let datalist = document.getElementById(datalistId);
        
        if (!datalist) {
            datalist = document.createElement('datalist');
            datalist.id = datalistId;
            document.body.appendChild(datalist);
            input.setAttribute('list', datalistId);
        }

        datalist.innerHTML = ""; 
        data.forEach(item => {
            const option = document.createElement('option');
            option.value = item;
            datalist.appendChild(option);
        });
    } catch (e) {
        console.error("Error cargando sugerencias filtradas:", e);
    }
}
window.actualizarSugerenciasMenuPorTipo = actualizarSugerenciasMenuPorTipo;