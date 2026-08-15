import json
import os
import sys
import logging

# 1. CONFIGURACIÓN PROFESIONAL DE LOGGING
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class Extractor:
    """Módulo E (Extract) del sistema ETL"""
    def __init__(self, ruta_archivo):
        self.ruta_archivo = ruta_archivo

    def extraer_datos(self):
        logging.info(f"Iniciando extracción desde: {self.ruta_archivo}")
        if not os.path.exists(self.ruta_archivo):
            logging.error(f"El archivo '{self.ruta_archivo}' no fue encontrado.")
            return None
        try:
            with open(self.ruta_archivo, 'r', encoding='utf-8') as archivo:
                return json.load(archivo)
        except Exception as e:
            logging.error(f"Error durante la extracción: {e}")
            return None

class Transformador:
    """Módulo T (Transform) del sistema ETL"""
    def __init__(self, datos_crudos):
        self.datos_crudos = datos_crudos
        self.datos_limpios = {}
        self.registros_rechazados = {} 

    def ejecutar_transformacion(self):
        logging.info("Iniciando fase de Transformación (T)...")
        
        if 'cadetes' in self.datos_crudos:
            self._transformar_cadetes(self.datos_crudos['cadetes'])
            
        # Ejemplo: si tuvieras más tablas, las agregarías aquí
        # if 'pedidos' in self.datos_crudos:
        #     self._transformar_pedidos(self.datos_crudos['pedidos'])
            
        logging.info("Transformación finalizada.")
        return self.datos_limpios, self.registros_rechazados

    def _transformar_cadetes(self, cadetes_crudos):
        limpios = []
        rechazados = []

        for c in cadetes_crudos:
            try:
                id_raw = c.get('id_cadete')
                if not id_raw or int(id_raw) == 0:
                    raise ValueError("ID de cadete inválido o inexistente")
                
                nombre_raw = c.get('cadete')
                if nombre_raw is None or str(nombre_raw).strip() == "":
                    nombre_limpio = 'Sin Nombre'
                else:
                    nombre_limpio = str(nombre_raw).strip().title()
                
                activo_raw = c.get('activo', False)
                esta_activo = True if str(activo_raw).lower() in ['1', 'true'] else False

                deuda_raw = c.get('deuda', 0)
                try:
                    deuda_limpia = int(deuda_raw) if deuda_raw != "" else 0
                except (ValueError, TypeError):
                    deuda_limpia = 0

                cadete_transformado = {
                    'id': int(id_raw),
                    'nombre': nombre_limpio,
                    'activo': esta_activo,
                    'deuda': deuda_limpia
                }
                limpios.append(cadete_transformado)

            except Exception as e:
                c['motivo_rechazo'] = str(e)
                rechazados.append(c)
        
        self.datos_limpios['cadetes'] = limpios
        if rechazados:
            self.registros_rechazados['cadetes'] = rechazados
            
        logging.info(f"Cadetes -> OK: {len(limpios)} | Rechazados: {len(rechazados)}")

class Cargador:
    """Módulo L (Load) del sistema ETL"""
    def __init__(self, datos_limpios):
        self.datos_limpios = datos_limpios

    def cargar_tabla(self, nombre_tabla):
        logging.info(f"Iniciando fase de Carga (L) para la tabla: {nombre_tabla}")
        
        if nombre_tabla not in self.datos_limpios:
            logging.error(f"La tabla '{nombre_tabla}' no existe en los datos transformados.")
            return False
            
        registros = self.datos_limpios[nombre_tabla]
        
        try:
            # Aquí es donde conectarías con el ORM de Django.
            # Por ejemplo, importarías tus modelos de Django al principio del archivo:
            # from supergrill.models import Cadete
            
            # Simulamos el guardado en base de datos:
            for registro in registros:
                # Lógica real de Django sería algo así:
                # Cadete.objects.update_or_create(
                #     id=registro['id'], 
                #     defaults={
                #         'nombre': registro['nombre'],
                #         'activo': registro['activo'],
                #         'deuda': registro['deuda']
                #     }
                # )
                pass # Eliminamos esto cuando conectes Django
                
            logging.info(f"✅ ¡Se cargaron {len(registros)} registros exitosamente en la tabla '{nombre_tabla}'!")
            return True
            
        except Exception as e:
            logging.error(f"Error crítico al guardar en la base de datos: {e}")
            return False

def menu_principal():
    ruta_archivo = r'C:\Proyectos\Supergrill_DJANGO\supergrill\backup_flask.json' 
    extractor = Extractor(ruta_archivo)
    
    # Variables de estado para el ETL
    datos_crudos = None 
    datos_limpios = None
    registros_rechazados = None

    while True:
        print("\n" + "=" * 50)
        print(" 🚀 SISTEMA ETL - SUPERGRILL (PRO VERSION) ")
        print("=" * 50)
        print("1. Ejecutar Extracción (E)")
        print("2. Ver tablas extraídas (Crudos)")
        print("3. Ver registros de una tabla (Crudos)")
        print("4. Ejecutar Transformación (T) ⚙️")
        print("5. Cargar tabla a la Base de Datos (L) 💾")
        print("6. Salir")
        print("=" * 50)
        
        opcion = input("Elige una opción (1-6): ")
        
        if opcion == '1':
            datos_crudos = extractor.extraer_datos()
            if datos_crudos:
                print("\n✅ Extracción exitosa.")
        
        elif opcion == '2':
            if not datos_crudos:
                print("\n⚠️ Primero debes extraer (Opción 1).")
                continue
            for tabla, registros in datos_crudos.items():
                cantidad = len(registros) if isinstance(registros, list) else 'N/A'
                print(f"  • {tabla}: {cantidad} registros")
                
        elif opcion == '3':
            if not datos_crudos:
                print("\n⚠️ Primero debes extraer (Opción 1).")
                continue
            
            nombre_tabla = input("\nEscribe el nombre de la tabla: ").strip()
            if nombre_tabla in datos_crudos and isinstance(datos_crudos[nombre_tabla], list):
                print(json.dumps(datos_crudos[nombre_tabla][:10], indent=4, ensure_ascii=False))
            else:
                print("❌ Tabla no encontrada o no es una lista.")
                
        elif opcion == '4':
            if not datos_crudos:
                print("\n⚠️ Primero debes extraer los datos crudos (Opción 1) antes de transformarlos.")
                continue
            
            transformador = Transformador(datos_crudos)
            datos_limpios, registros_rechazados = transformador.ejecutar_transformacion()
            print("\n✅ Transformación completada. Revisa los logs arriba.")
            
        elif opcion == '5':
            if not datos_limpios:
                print("\n⚠️ Primero debes transformar los datos (Opción 4) antes de cargarlos.")
                continue
            
            print("\nTablas disponibles y listas para cargar:")
            for tabla in datos_limpios.keys():
                print(f"  • {tabla} ({len(datos_limpios[tabla])} registros)")
                
            tabla_elegida = input("\nEscribe el nombre de la tabla que deseas cargar (o 'cancelar'): ").strip().lower()
            
            if tabla_elegida != 'cancelar':
                cargador = Cargador(datos_limpios)
                cargador.cargar_tabla(tabla_elegida)
                
        elif opcion == '6':
            sys.exit()
        else:
            print("\n❌ Opción no válida.")

if __name__ == "__main__":
    menu_principal()