#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
AGENTE INMOBILIARIO INMO - VERSIÓN PARAGUAY
=============================================================================
Asistente conversacional inteligente para búsqueda de propiedades 
inmobiliarias en Paraguay. Utiliza el scraper de InfoCasas y la API
de OpenRouter para generar respuestas naturales.

Autor: Guaraniux
Fecha: 2024
=============================================================================
"""

import requests
from scraper import InfocasasScraper
import json
import re
import time
import os


class AgenteInmoParaguay:
    """
    Asistente INMO: Asesor inmobiliario virtual con personalidad paraguaya.
    
    Características:
    - Conversación natural con voseo paraguayo
    - Extracción automática de filtros de búsqueda
    - Integración con scraper de InfoCasas
    - Memoria de conversación y búsquedas anteriores
    """
    
    def __init__(self, api_key: str = None):
        """
        Inicializa el agente inmobiliario.
        
        Args:
            api_key: Clave API de OpenRouter (opcional, usa variable de entorno si no se provee)
        """
        # Configuración de API (prioriza variable de entorno por seguridad)
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.model = "x-ai/grok-4.1-fast"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Historial de conversación
        self.history = []
        
        # ======================================================================
        # PERSONALIDAD DEL AGENTE
        # ======================================================================
        self.personalidad = """Tu eres Inmo, un asesor inmobiliario en Paraguay. Tu trabajo es ayudar a encontrar propiedades reales.

PERSONALIDAD:
- Hablás con voseo paraguayo natural (vos buscás, vos querés)
- Sos profesional pero cercano
- Respondés de forma concisa y directa
- NO usés la palabra "che"
- NO usés listas con viñetas, asteriscos ni guiones
- Integrá la información de forma fluida en la conversación

REGLAS CRÍTICAS:
1. NUNCA inventes propiedades, precios o detalles
2. SOLO mencioná propiedades si recibís datos en [RESULTADOS] o [RESULTADOS ANTERIORES]
3. Si no hay resultados, decilo honestamente y sugerí alternativas
4. NO compartas enlaces, teléfonos ni información de contacto
5. Si los resultados son de otra zona, dejalo claro
6. Mantené las respuestas cortas (máximo 5-6 oraciones)
7. Cuando el usuario pregunte por "la primera", "la segunda", "la última", "la de X precio", usá el campo 'numero' y los detalles completos

FORMATO DE RESPUESTA:
Cuando describás propiedades INICIALMENTE:
"Encontré X opciones interesantes. Por ejemplo, hay un apartamento de 2 dormitorios en [barrio] por USD X, también vi una casa en [barrio] con 3 dormitorios por USD Y..."

Cuando el usuario pida MÁS INFO sobre una específica:
"Esa casa tiene [dormitorios] dormitorios y [baños] baños, cuenta con [m2] de construcción. [Detalles de descripción]. El precio es [precio]."

NUNCA así:
- Propiedad 1: ...
- Propiedad 2: ...
* Casa en..."""

        # Inicializar scraper
        self.scraper = InfocasasScraper()
        
        # ======================================================================
        # FILTROS DE BÚSQUEDA ACUMULATIVOS
        # ======================================================================
        self.filtros = {
            'operacion': None,           # 'venta' o 'alquiler'
            'tipo_propiedad': None,      # 'casa', 'apartamento', 'terreno', etc.
            'ubicacion': None,           # slug de ubicación
            'ubicacion_solicitada': None, # nombre legible de la ubicación
            'presupuesto_max': None,     # precio máximo en USD
            'dormitorios': None          # cantidad de dormitorios
        }
        
        # Última búsqueda realizada (para referencias posteriores)
        self.ultima_busqueda = None
    
    # ==========================================================================
    # LIMPIEZA DE DATOS SENSIBLES
    # ==========================================================================
    
    def _limpiar_texto_sensible(self, texto: str) -> str:
        """
        Elimina información sensible de los textos (URLs, teléfonos).
        
        Args:
            texto: Texto a limpiar
            
        Returns:
            Texto sin información sensible
        """
        if not texto:
            return ""
        
        # Eliminar URLs
        texto = re.sub(r'https?://\S+|www\.\S+', '', texto)
        # Eliminar números de teléfono
        texto = re.sub(r'\+?\d{2,4}[\s-]?\d{3,4}[\s-]?\d{3,4}', '', texto)
        
        return texto.strip()

    # ==========================================================================
    # EXTRACCIÓN DE FILTROS DEL MENSAJE
    # ==========================================================================
    
    def extraer_filtros(self, mensaje: str):
        """
        Extrae parámetros de búsqueda del mensaje del usuario.
        
        Analiza el texto para identificar:
        - Operación (venta/alquiler)
        - Tipo de propiedad
        - Ubicación
        - Presupuesto
        - Cantidad de dormitorios
        
        Args:
            mensaje: Mensaje del usuario
        """
        mensaje_lower = mensaje.lower()
        
        # ----------------------------------------------------------------------
        # 1. DETECTAR OPERACIÓN
        # ----------------------------------------------------------------------
        palabras_alquiler = ['alquiler', 'alquilar', 'rentar', 'arrendar']
        palabras_venta = ['venta', 'comprar', 'compra', 'vendo', 'invertir', 'inversion', 'inversión']
        
        if any(x in mensaje_lower for x in palabras_alquiler):
            self.filtros['operacion'] = 'alquiler'
        elif any(x in mensaje_lower for x in palabras_venta):
            self.filtros['operacion'] = 'venta'
        
        # ----------------------------------------------------------------------
        # 2. DETECTAR TIPO DE PROPIEDAD
        # ----------------------------------------------------------------------
        if any(x in mensaje_lower for x in ['apartamento', 'depto', 'departamento', 'apto']):
            self.filtros['tipo_propiedad'] = 'apartamento'
        elif 'casa' in mensaje_lower:
            self.filtros['tipo_propiedad'] = 'casa'
        elif any(x in mensaje_lower for x in ['terreno', 'lote', 'fraccionamiento']):
            self.filtros['tipo_propiedad'] = 'terreno'
        
        # ----------------------------------------------------------------------
        # 3. DETECTAR UBICACIÓN
        # ----------------------------------------------------------------------
        ubicacion_detectada = self.scraper._detectar_ubicacion(mensaje_lower)
        if ubicacion_detectada:
            self.filtros['ubicacion'] = ubicacion_detectada
            
            # Guardar nombre legible para mostrar al usuario
            nombres_bonitos = {
                'coronel oviedo': 'Coronel Oviedo',
                'asuncion': 'Asunción',
                'asunción': 'Asunción',
                'ciudad del este': 'Ciudad del Este',
            }
            
            for key, value in nombres_bonitos.items():
                if key in mensaje_lower:
                    self.filtros['ubicacion_solicitada'] = value
                    break
            else:
                self.filtros['ubicacion_solicitada'] = ubicacion_detectada.replace('-', ' ').title()
        
        # ----------------------------------------------------------------------
        # 4. DETECTAR PRESUPUESTO
        # ----------------------------------------------------------------------
        # Casos especiales en texto
        if 'millon y medio' in mensaje_lower or 'un millon medio' in mensaje_lower:
            self.filtros['presupuesto_max'] = 1500000
        elif 'dos millones' in mensaje_lower or '2 millones' in mensaje_lower:
            self.filtros['presupuesto_max'] = 2000000
        elif 'tres millones' in mensaje_lower or '3 millones' in mensaje_lower:
            self.filtros['presupuesto_max'] = 3000000
        elif 'un millon' in mensaje_lower or '1 millon' in mensaje_lower:
            self.filtros['presupuesto_max'] = 1000000
        else:
            # Patrón general para precios
            patron_precio = r'(?:hasta|max|maximo|presupuesto de|alrededor de)\s*(?:u\$s|usd|gs|guaranies)?\s*(\d+(?:\.\d+)?)\s*(mil|millones?|k)?'
            precio_match = re.search(patron_precio, mensaje_lower)
            
            if precio_match:
                numero = float(precio_match.group(1).replace('.', ''))
                multiplicador = precio_match.group(2) or ''
                
                if 'millon' in multiplicador:
                    numero *= 1000000
                elif 'mil' in multiplicador or 'k' in multiplicador:
                    numero *= 1000
                    
                self.filtros['presupuesto_max'] = int(numero)

        # ----------------------------------------------------------------------
        # 5. DETECTAR DORMITORIOS
        # ----------------------------------------------------------------------
        patron_dorm = r'(\d+)\s*(?:dorm|hab|cuarto|pieza|habitacion)'
        dorm = re.search(patron_dorm, mensaje_lower)
        if dorm:
            self.filtros['dormitorios'] = int(dorm.group(1))

    def _tiene_filtros_completos(self) -> bool:
        """
        Verifica si tenemos los filtros mínimos para realizar una búsqueda.
        
        Returns:
            True si tenemos operación, tipo y ubicación definidos
        """
        return (
            self.filtros['operacion'] is not None and 
            self.filtros['tipo_propiedad'] is not None and 
            self.filtros['ubicacion'] is not None
        )

    # ==========================================================================
    # BÚSQUEDA DE PROPIEDADES
    # ==========================================================================
    
    def buscar_propiedades(self) -> dict:
        """
        Ejecuta la búsqueda usando los filtros acumulados.
        
        Returns:
            Diccionario con total de resultados y lista de propiedades
        """
        # Ejecutar búsqueda con el scraper
        propiedades = self.scraper.search_properties(
            operation=self.filtros['operacion'],
            prop_type=self.filtros['tipo_propiedad'],
            location=self.filtros['ubicacion'],
            max_price=self.filtros['presupuesto_max'],
            bedrooms=self.filtros['dormitorios']
        )
        
        # Filtrar manualmente por precio si es necesario
        if self.filtros['presupuesto_max']:
            propiedades = [
                p for p in propiedades 
                if p['precio']['monto'] and 
                   p['precio']['monto'] <= self.filtros['presupuesto_max']
            ]

        # Construir resultado estructurado
        resultado = {
            'total': len(propiedades),
            'ubicacion_buscada': self.filtros['ubicacion_solicitada'] or self.filtros['ubicacion'],
            'propiedades': []
        }
        
        # Procesar todos los inmuebles encontrados
        for idx, prop in enumerate(propiedades, 1):
            monto = prop['precio']['monto']
            precio_str = f"{prop['precio']['moneda']} {monto:,}" if monto else "Precio a consultar"
            
            # Construir ubicación completa
            partes_ubicacion = []
            if prop['ubicacion']['barrio']:
                partes_ubicacion.append(prop['ubicacion']['barrio'])
            if prop['ubicacion']['ciudad']:
                partes_ubicacion.append(prop['ubicacion']['ciudad'])
            elif prop['ubicacion']['departamento']:
                partes_ubicacion.append(prop['ubicacion']['departamento'])
            
            ubicacion_completa = ', '.join(partes_ubicacion) if partes_ubicacion else 'Ubicación no especificada'
            
            # Obtener metros cuadrados
            m2_construidos = prop['caracteristicas']['metros_cuadrados'].get('m2_construidos')
            m2_str = f"{m2_construidos} m²" if m2_construidos else "No especificado"
            
            # Agregar inmueble al resultado
            resultado['propiedades'].append({
                'numero': idx,
                'id': prop['identificacion']['id'],
                'titulo': self._limpiar_texto_sensible(prop['informacion_basica']['titulo']),
                'precio': precio_str,
                'precio_numerico': monto,
                'moneda': prop['precio']['moneda'],
                'ubicacion': ubicacion_completa,
                'dormitorios': prop['caracteristicas']['dormitorios'] or '?',
                'banos': prop['caracteristicas']['banos'] or '?',
                'm2': m2_str,
                'tipo': prop['informacion_basica'].get('tipo_propiedad', 'Casa'),
                'operacion': self.filtros['operacion'] or 'venta',
                'destacado': prop.get('destacado', False),
                'imagenes': prop.get('imagenes', []),
                'coordenadas': prop['ubicacion'].get('coordenadas'),
            })
        
        return resultado

    # ==========================================================================
    # CHAT PRINCIPAL
    # ==========================================================================
    
    def chat(self, mensaje: str) -> str:
        """
        Procesa el mensaje del usuario y genera una respuesta.
        
        Args:
            mensaje: Mensaje del usuario
            
        Returns:
            Respuesta del agente
        """
        # Extraer filtros del mensaje actual
        self.extraer_filtros(mensaje)
        
        # Determinar si debemos buscar propiedades
        debe_buscar = self._tiene_filtros_completos()
        resultados_json = None
        
        if debe_buscar:
            try:
                resultados = self.buscar_propiedades()
                self.ultima_busqueda = resultados
                resultados_json = resultados
            except Exception as e:
                print(f"[DEBUG] Error en búsqueda: {e}")
        
        # Construir el contexto dinámico
        system_prompt = self._construir_system_prompt(resultados_json)
        
        # Crear el mensaje completo con contexto
        mensaje_completo = f"CONTEXTO DE BÚSQUEDA:\n{system_prompt}\n\nMensaje del usuario: {mensaje}"
        
        # Construir historial para la API
        messages = [{"role": "system", "content": self.personalidad}]
        
        # Añadir historial previo (últimos 4 mensajes para contexto)
        for m in self.history[-4:]:
            messages.append(m)
            
        messages.append({"role": "user", "content": mensaje_completo})
        
        # Configurar headers para OpenRouter
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "InmoAgent"
        }
        
        # Configurar payload
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": 2048
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    respuesta_texto = result['choices'][0]['message']['content']
                    
                    # Guardar en historial
                    self.history.append({"role": "user", "content": mensaje})
                    self.history.append({"role": "assistant", "content": respuesta_texto})
                    
                    return respuesta_texto
                else:
                    return "No recibí respuesta del modelo."
            else:
                # Reintentar en caso de error temporal (429, 502, 503)
                if response.status_code in [429, 503, 502]:
                    time.sleep(2)
                    response = requests.post(self.api_url, headers=headers, json=data, timeout=45)
                    if response.status_code == 200:
                        result = response.json()
                        respuesta_texto = result['choices'][0]['message']['content']
                        self.history.append({"role": "user", "content": mensaje})
                        self.history.append({"role": "assistant", "content": respuesta_texto})
                        return respuesta_texto

                print(f"[DEBUG] Error API OpenRouter: {response.status_code} - {response.text}")
                return "Disculpá, tuve un problemita técnico con la conexión. ¿Podemos intentar de nuevo?"
            
        except Exception as e:
            print(f"[DEBUG] Excepción: {str(e)}")
            return "Disculpá, se cortó nuestra conexión. ¿Me repetís lo último?"

    def _construir_system_prompt(self, resultados_json=None) -> str:
        """
        Construye el contexto dinámico con filtros y resultados.
        
        Args:
            resultados_json: Resultados de búsqueda (opcional)
            
        Returns:
            String con el contexto para el modelo
        """
        prompt = ""

        # Agregar información de filtros actuales
        filtros_info = "\n\nFILTROS ACTUALES RECONOCIDOS:\n"
        missing_info = []
        
        if self.filtros['operacion']:
            filtros_info += f"- Operación: {self.filtros['operacion']}\n"
        else:
            missing_info.append("OPERACIÓN (Venta/Alquiler)")
            
        if self.filtros['tipo_propiedad']:
            filtros_info += f"- Tipo: {self.filtros['tipo_propiedad']}\n"
        else:
            missing_info.append("TIPO DE PROPIEDAD")
            
        if self.filtros['ubicacion_solicitada']:
            filtros_info += f"- Zona: {self.filtros['ubicacion_solicitada']}\n"
        elif self.filtros['ubicacion']:
            filtros_info += f"- Zona: {self.filtros['ubicacion']}\n"
        else:
            missing_info.append("UBICACIÓN/ZONA")

        if self.filtros['presupuesto_max']:
            filtros_info += f"- Presupuesto máximo: USD {self.filtros['presupuesto_max']:,}\n"
        if self.filtros['dormitorios']:
            filtros_info += f"- Dormitorios: {self.filtros['dormitorios']}\n"
        
        prompt += filtros_info
        
        # Indicar información faltante
        if missing_info:
            prompt += f"\n[FALTA INFORMACIÓN]: No se puede realizar la búsqueda aún. "
            prompt += f"Por favor preguntale al usuario por: {', '.join(missing_info)}.\n"
        
        # Agregar resultados de búsqueda
        if resultados_json:
            if resultados_json['total'] > 0:
                prompt += f"\n\n[RESULTADOS DE BÚSQUEDA - USA SOLO ESTOS DATOS]\n"
                prompt += json.dumps(resultados_json, ensure_ascii=False, indent=2)
                prompt += "\n\nINSTRUCCIÓN: Cada propiedad tiene 'numero' (1,2,3...). "
                prompt += "Si el usuario dice 'la primera', 'la de X dólares', usá ese número."
            else:
                zona = resultados_json.get('ubicacion_buscada', 'esa zona')
                prompt += f"\n\n[SIN RESULTADOS]: No hay propiedades disponibles en {zona}.\n"
                prompt += "INSTRUCCIÓN: Decile al cliente que no encontraste nada y sugerí alternativas."
        elif self.ultima_busqueda and self.ultima_busqueda['total'] > 0:
            # Usar búsqueda previa si no hay nuevos resultados
            prompt += f"\n\n[RESULTADOS ANTERIORES DISPONIBLES]\n"
            prompt += json.dumps(self.ultima_busqueda, ensure_ascii=False, indent=2)
            prompt += "\n\nINSTRUCCIÓN: El usuario puede estar preguntando por estas propiedades."
        
        return prompt

    # ==========================================================================
    # API PARA FRONTEND
    # ==========================================================================
    
    def get_ultima_busqueda(self) -> dict:
        """
        Retorna la última búsqueda realizada (para el frontend).
        
        Returns:
            Diccionario con los resultados de la última búsqueda
        """
        return self.ultima_busqueda or {'total': 0, 'propiedades': []}
    
    def get_filtros_actuales(self) -> dict:
        """
        Retorna los filtros actuales (para el frontend).
        
        Returns:
            Diccionario con los filtros activos
        """
        return self.filtros.copy()
    
    def reset_conversacion(self):
        """Reinicia la conversación y los filtros."""
        self.history = []
        self.ultima_busqueda = None
        self.filtros = {
            'operacion': None,
            'tipo_propiedad': None,
            'ubicacion': None,
            'ubicacion_solicitada': None,
            'presupuesto_max': None,
            'dormitorios': None
        }


# =============================================================================
# FUNCIÓN PRINCIPAL (CLI)
# =============================================================================

def main():
    """Ejecuta el agente en modo consola interactiva."""
    
    # Obtener API key de variable de entorno
    API_KEY = os.getenv('OPENROUTER_API_KEY')
    if not API_KEY:
        raise ValueError("ERROR: OPENROUTER_API_KEY no está configurada en las variables de entorno")
    agente = AgenteInmoParaguay(api_key=API_KEY)
    
    print("=" * 60)
    print("INMO - ASESOR INMOBILIARIO")
    print("Powered by Guaraniux")
    print("=" * 60)
    print("Escribí 'salir' para terminar la conversación\n")
    
    # Primera interacción automática
    print("Inmo:")
    respuesta_inicial = agente.chat("Saludá al cliente y preguntale qué está buscando")
    print(respuesta_inicial)
    
    # Bucle principal de conversación
    while True:
        try:
            mensaje = input("\nVos: ").strip()
            
            if not mensaje:
                continue
                
            if mensaje.lower() in ['salir', 'chau', 'adiós', 'nos vemos', 'exit']:
                print("\nInmo: ¡Que tengas un excelente día! Cualquier cosa, acá estoy.")
                break
            
            print("\nInmo:")
            respuesta = agente.chat(mensaje)
            print(respuesta)
            
        except KeyboardInterrupt:
            print("\n\nInmo: ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\nError inesperado: {e}")


if __name__ == "__main__":
    main()
