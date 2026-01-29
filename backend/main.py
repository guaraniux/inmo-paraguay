#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
INMO API - BACKEND FASTAPI
=============================================================================
API REST para el sistema inmobiliario INMO. Expone endpoints para:
- Chat con el agente inmobiliario
- Búsqueda de propiedades
- Gestión de sesiones

Autor: Guaraniux
Fecha: 2024
=============================================================================
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
import os
from dotenv import load_dotenv

# Agregar directorio padre al path para importar módulos
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Cargar variables de entorno desde .env en la raíz del proyecto
env_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=env_path)

from agente import AgenteInmoParaguay
from scraper import InfocasasScraper

# =============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# =============================================================================

app = FastAPI(
    title="INMO API",
    description="API para el asistente inmobiliario de Paraguay",
    version="1.0.0"
)

# Configurar CORS para permitir requests del frontend
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Agregar origen de producción si está configurado
vercel_url = os.getenv('VERCEL_URL')
if vercel_url:
    allowed_origins.append(f"https://{vercel_url}")
    allowed_origins.append(vercel_url)

# En producción, permitir todos los orígenes de Vercel usando regex
if os.getenv('PRODUCTION', 'false').lower() == 'true':
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r'^https://.*\.vercel\.app$',
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # En desarrollo, permitir cualquier puerto en localhost y 127.0.0.1
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r'^https?://(localhost|127\.0\.0\.1)(:\d+)?$',
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# =============================================================================
# ALMACENAMIENTO DE SESIONES
# =============================================================================

# Diccionario para mantener agentes por sesión
sesiones: Dict[str, AgenteInmoParaguay] = {}

def obtener_agente(session_id: str) -> AgenteInmoParaguay:
    """
    Obtiene o crea un agente para una sesión específica.
    
    Args:
        session_id: Identificador único de la sesión
        
    Returns:
        Instancia del agente para esa sesión
    """
    if session_id not in sesiones:
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("ERROR: OPENROUTER_API_KEY no está configurada en las variables de entorno")
        sesiones[session_id] = AgenteInmoParaguay(api_key=api_key)
    return sesiones[session_id]

# =============================================================================
# MODELOS DE DATOS (SCHEMAS)
# =============================================================================

class MensajeChat(BaseModel):
    """Modelo para mensajes de chat entrantes."""
    mensaje: str
    session_id: str = "default"

class RespuestaChat(BaseModel):
    """Modelo para respuestas de chat."""
    respuesta: str
    filtros: Dict[str, Any]
    propiedades: List[Dict[str, Any]]
    total_resultados: int

class BusquedaDirecta(BaseModel):
    """Modelo para búsquedas directas (sin chat)."""
    operacion: str = "venta"
    tipo_propiedad: str = "inmuebles"
    ubicacion: str = "asuncion"
    precio_min: Optional[int] = None
    precio_max: Optional[int] = None
    dormitorios: Optional[int] = None
    banos: Optional[int] = None
    pagina: int = 1

# =============================================================================
# ENDPOINTS DE LA API
# =============================================================================

@app.get("/")
async def root():
    """Endpoint raíz - información de la API."""
    return {
        "nombre": "INMO API",
        "version": "1.0.0",
        "descripcion": "API del asistente inmobiliario de Paraguay",
        "endpoints": {
            "/chat": "POST - Enviar mensaje al agente",
            "/buscar": "POST - Búsqueda directa de propiedades",
            "/sesion/{session_id}": "DELETE - Reiniciar sesión",
            "/ubicaciones": "GET - Lista de ubicaciones disponibles"
        }
    }

@app.post("/chat", response_model=RespuestaChat)
async def chat(mensaje: MensajeChat):
    """
    Endpoint principal de chat con el agente.
    
    Recibe un mensaje del usuario y retorna:
    - Respuesta del agente
    - Filtros actuales de búsqueda
    - Propiedades encontradas (si aplica)
    """
    try:
        agente = obtener_agente(mensaje.session_id)
        
        # Procesar mensaje
        respuesta = agente.chat(mensaje.mensaje)
        
        # Obtener datos adicionales
        filtros = agente.get_filtros_actuales()
        busqueda = agente.get_ultima_busqueda()
        
        return RespuestaChat(
            respuesta=respuesta,
            filtros=filtros,
            propiedades=busqueda.get('propiedades', []),
            total_resultados=busqueda.get('total', 0)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando mensaje: {str(e)}")

@app.post("/buscar")
async def buscar_propiedades(busqueda: BusquedaDirecta):
    """
    Endpoint para búsqueda directa de propiedades (sin usar el chat).
    
    Útil para filtros visuales en el frontend.
    """
    try:
        scraper = InfocasasScraper()
        
        propiedades = scraper.search_properties(
            operation=busqueda.operacion,
            prop_type=busqueda.tipo_propiedad,
            location=busqueda.ubicacion,
            min_price=busqueda.precio_min,
            max_price=busqueda.precio_max,
            bedrooms=busqueda.dormitorios,
            bathrooms=busqueda.banos,
            page=busqueda.pagina
        )
        
        # Formatear resultados
        resultados = []
        for idx, prop in enumerate(propiedades[:10], 1):
            monto = prop['precio']['monto']
            precio_str = f"{prop['precio']['moneda']} {monto:,}" if monto else "Consultar"
            
            # Construir ubicación
            partes = []
            if prop['ubicacion']['barrio']:
                partes.append(prop['ubicacion']['barrio'])
            if prop['ubicacion']['ciudad']:
                partes.append(prop['ubicacion']['ciudad'])
            
            resultados.append({
                'numero': idx,
                'id': prop['identificacion']['id'],
                'titulo': prop['informacion_basica']['titulo'][:100],
                'descripcion': prop['informacion_basica'].get('descripcion', '')[:300],
                'precio': precio_str,
                'precio_numerico': monto,
                'moneda': prop['precio']['moneda'],
                'ubicacion': ', '.join(partes) if partes else 'No especificada',
                'dormitorios': prop['caracteristicas']['dormitorios'],
                'banos': prop['caracteristicas']['banos'],
                'm2': prop['caracteristicas']['metros_cuadrados'].get('m2_construidos'),
                'tipo': prop['informacion_basica'].get('tipo_propiedad', 'Inmueble'),
                'imagenes': prop.get('imagenes', []),
                'coordenadas': prop['ubicacion'].get('coordenadas'),
                'url': prop['enlaces'].get('url_propiedad'),
            })
        
        return {
            'total': len(propiedades),
            'pagina': busqueda.pagina,
            'propiedades': resultados
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")

@app.delete("/sesion/{session_id}")
async def reiniciar_sesion(session_id: str):
    """
    Reinicia una sesión de chat (borra historial y filtros).
    """
    if session_id in sesiones:
        sesiones[session_id].reset_conversacion()
        return {"mensaje": "Sesión reiniciada correctamente"}
    return {"mensaje": "Sesión no encontrada, se creará una nueva al chatear"}

@app.get("/ubicaciones")
async def obtener_ubicaciones():
    """
    Retorna las ubicaciones disponibles para búsqueda.
    """
    scraper = InfocasasScraper()
    
    return {
        'departamentos': [
            {'slug': d, 'nombre': d.replace('-', ' ').title()} 
            for d in scraper.CONFIG['departamentos']
        ],
        'ciudades': [
            {'slug': c, 'nombre': c.replace('-', ' ').title(), 'departamento': scraper.CONFIG['parents'].get(c)} 
            for c in scraper.CONFIG['ciudades']
        ]
    }

@app.get("/tipos")
async def obtener_tipos():
    """
    Retorna los tipos de propiedad disponibles.
    """
    return {
        'tipos': [
            {'slug': 'casa', 'nombre': 'Casa'},
            {'slug': 'apartamento', 'nombre': 'Apartamento'},
            {'slug': 'terreno', 'nombre': 'Terreno'},
            {'slug': 'local', 'nombre': 'Local Comercial'},
            {'slug': 'oficina', 'nombre': 'Oficina'},
            {'slug': 'campo', 'nombre': 'Campo'},
        ],
        'operaciones': [
            {'slug': 'venta', 'nombre': 'Venta'},
            {'slug': 'alquiler', 'nombre': 'Alquiler'},
        ]
    }

# =============================================================================
# EJECUTAR SERVIDOR
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
