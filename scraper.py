#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
INFOCASAS SCRAPER - VERSIÓN PARAGUAY
=============================================================================
Scraper optimizado para extraer datos de propiedades inmobiliarias de 
InfoCasas Paraguay. Incluye soporte para proxies residenciales rotativos,
extracción de imágenes, coordenadas y detección de propiedades destacadas.

Autor: Guaraniux
Fecha: 2024
=============================================================================
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import re
import random
import os


class InfocasasScraper:
    """
    Scraper para extraer datos de propiedades de InfoCasas Paraguay.
    
    Características:
    - Soporte para proxies residenciales rotativos (ProxyScrape)
    - Extracción de imágenes de propiedades
    - Extracción de coordenadas para mapas
    - Detección automática de propiedades destacadas
    - Búsqueda por múltiples filtros (operación, tipo, ubicación, precio, etc.)
    """
    
    # ==========================================================================
    # CONFIGURACIÓN GENERAL DEL SCRAPER
    # ==========================================================================
    
    CONFIG = {
        'url': 'https://www.infocasas.com.py',
        'nombre': 'Paraguay',
        'moneda': 'USD',
        # Lista completa de departamentos de Paraguay
        'departamentos': [
            'asuncion', 'central', 'alto-parana', 'itapua', 'caaguazu', 
            'caazapa', 'concepcion', 'cordillera', 'guaira', 'paraguari', 
            'misiones', 'neembucu', 'amambay', 'canindeyu', 'presidente-hayes', 
            'boqueron', 'alto-paraguay', 'san-pedro'
        ],
        # Lista ampliada de ciudades principales de Paraguay
        'ciudades': [
            # Central
            'asuncion', 'san-lorenzo', 'luque', 'capiata', 'lambare', 
            'fernando-de-la-mora', 'limpio', 'nemby', 'villa-elisa', 
            'mariano-roque-alonso', 'san-antonio', 'ita', 'aregua', 
            'ypane', 'guarambare', 'villeta', 'ypacarai', 'nueva-italia',
            'san-juan-bautista-de-nemby', 'j-augusto-saldivar',
            # Alto Paraná
            'ciudad-del-este', 'presidente-franco', 'minga-guazu',
            'hernandarias', 'santa-rita', 'san-alberto',
            # Itapúa
            'encarnacion', 'hohenau', 'obligado', 'bella-vista', 
            'capitan-miranda', 'cambyreta', 'nueva-alborada',
            # Caaguazú
            'coronel-oviedo', 'caaguazu', 'jose-domingo-ocampos',
            # Amambay
            'pedro-juan-caballero', 'bella-vista-norte',
            # Guairá
            'villarrica', 'colonia-independencia',
            # Concepción
            'concepcion',
            # Ñeembucú
            'pilar',
            # Cordillera
            'caacupe', 'san-bernardino', 'altos', 'tobati', 'atyra',
            # Paraguarí
            'paraguari', 'ybycui', 'pirayú', 'sapucai',
            # San Pedro
            'san-pedro', 'san-estanislao',
            # Misiones
            'san-ignacio', 'ayolas', 'san-juan-bautista',
            # Presidente Hayes
            'villa-hayes', 'benjamin-aceval',
            # Boquerón
            'filadelfia', 'loma-plata', 'neuland',
        ],
        # Mapeo completo de ciudades a sus departamentos
        'parents': {
            # Central
            'san-lorenzo': 'central',
            'luque': 'central',
            'capiata': 'central',
            'lambare': 'central',
            'fernando-de-la-mora': 'central',
            'limpio': 'central',
            'nemby': 'central',
            'villa-elisa': 'central',
            'mariano-roque-alonso': 'central',
            'san-antonio': 'central',
            'ita': 'central',
            'aregua': 'central',
            'ypane': 'central',
            'guarambare': 'central',
            'villeta': 'central',
            'ypacarai': 'central',
            'nueva-italia': 'central',
            'san-juan-bautista-de-nemby': 'central',
            'j-augusto-saldivar': 'central',
            # Alto Paraná
            'ciudad-del-este': 'alto-parana',
            'presidente-franco': 'alto-parana',
            'minga-guazu': 'alto-parana',
            'hernandarias': 'alto-parana',
            'santa-rita': 'alto-parana',
            'san-alberto': 'alto-parana',
            # Itapúa
            'encarnacion': 'itapua',
            'hohenau': 'itapua',
            'obligado': 'itapua',
            'bella-vista': 'itapua',
            'capitan-miranda': 'itapua',
            'cambyreta': 'itapua',
            'nueva-alborada': 'itapua',
            # Caaguazú
            'coronel-oviedo': 'caaguazu',
            'caaguazu': 'caaguazu',
            'jose-domingo-ocampos': 'caaguazu',
            # Amambay
            'pedro-juan-caballero': 'amambay',
            'bella-vista-norte': 'amambay',
            # Guairá
            'villarrica': 'guaira',
            'colonia-independencia': 'guaira',
            # Concepción
            'concepcion': 'concepcion',
            # Ñeembucú
            'pilar': 'neembucu',
            # Cordillera
            'caacupe': 'cordillera',
            'san-bernardino': 'cordillera',
            'altos': 'cordillera',
            'tobati': 'cordillera',
            'atyra': 'cordillera',
            # Paraguarí
            'paraguari': 'paraguari',
            'ybycui': 'paraguari',
            'pirayú': 'paraguari',
            'sapucai': 'paraguari',
            # San Pedro
            'san-pedro': 'san-pedro',
            'san-estanislao': 'san-pedro',
            # Misiones
            'san-ignacio': 'misiones',
            'ayolas': 'misiones',
            'san-juan-bautista': 'misiones',
            # Presidente Hayes
            'villa-hayes': 'presidente-hayes',
            'benjamin-aceval': 'presidente-hayes',
            # Boquerón
            'filadelfia': 'boqueron',
            'loma-plata': 'boqueron',
            'neuland': 'boqueron',
        },
        # Variaciones de nombres para detección flexible
        'variaciones': {
            'asuncion': ['asuncion', 'asunción', 'asu', 'capital'],
            'ciudad-del-este': ['ciudad del este', 'cde', 'este'],
            'encarnacion': ['encarnacion', 'encarnación'],
            'coronel-oviedo': ['coronel oviedo', 'cnel oviedo', 'oviedo'],
            'san-lorenzo': ['san lorenzo'],
            'fernando-de-la-mora': ['fernando de la mora', 'fernando'],
            'mariano-roque-alonso': ['mariano roque alonso', 'mra', 'mariano'],
            'pedro-juan-caballero': ['pedro juan caballero', 'pjc', 'pedro juan'],
            'villa-elisa': ['villa elisa'],
            'san-bernardino': ['san bernardino', 'sanberna', 'san ber'],
            'caacupe': ['caacupe', 'caacupé'],
            'villarrica': ['villarrica', 'villa rica'],
            'presidente-franco': ['presidente franco'],
            'minga-guazu': ['minga guazu', 'minga guazú'],
            'central': ['central', 'gran asuncion', 'gran asunción', 'area metropolitana'],
            'alto-parana': ['alto parana', 'alto paraná'],
            'itapua': ['itapua', 'itapúa'],
        },
        # Barrios populares de Asunción
        'barrios_asuncion': [
            'villa-morra', 'carmelitas', 'manora', 'recoleta', 'las-carmelitas',
            'sajonia', 'mburucuya', 'seminario', 'los-laureles', 'herrera',
            'madame-lynch', 'santa-maria', 'ciudad-nueva', 'jara', 'barrio-obrero',
            'san-vicente', 'hipodromo', 'botanico', 'san-pablo', 'pinoza',
            'republicano', 'tacumbu', 'las-mercedes', 'vista-alegre', 'zeballos-cue',
            'san-roque', 'catedral', 'san-antonio', 'roberto-l-pettit'
        ]
    }
    
    # Mapeo de tipos de propiedad a slugs de URL
    TIPOS_PROPIEDAD_URL = {
        'apartamento': 'departamentos',
        'departamento': 'departamentos',
        'casa': 'casas',
        'terreno': 'terrenos',
        'lote': 'terrenos',
        'local': 'locales',
        'local-comercial': 'locales',
        'oficina': 'oficinas',
        'garage': 'cocheras',
        'cochera': 'cocheras',
        'campo': 'campos',
        'estancia': 'campos',
        'duplex': 'duplex',
        'penthouse': 'penthouse',
        'inmuebles': 'inmuebles',
        'casas-y-departamentos': 'casas-y-departamentos',
    }
    
    # ==========================================================================
    # CONFIGURACIÓN DE PROXYSCRAPE
    # ==========================================================================
    
    PROXY_CONFIG = {
        'api_key': os.getenv('PROXYSCRAPE_API_KEY', ''),
        'proxy_url': 'http://api.proxyscrape.com/v3/accounts/freebies/scraperapi/request',
        'enabled': bool(os.getenv('PROXYSCRAPE_API_KEY')),
    }
    
    def __init__(self):
        """Inicializa el scraper con la configuración base."""
        self.base_url = self.CONFIG['url']
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-PY,es;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        }
    
    # ==========================================================================
    # MÉTODOS DE CONEXIÓN Y REQUESTS
    # ==========================================================================
    
    def _hacer_request(self, url: str, timeout: int = 20) -> Optional[requests.Response]:
        """
        Realiza una petición HTTP usando proxies rotativos o conexión directa.
        """
        if self.PROXY_CONFIG['enabled']:
            return self._request_con_proxy(url, timeout)
        else:
            return self._request_directo(url, timeout)
    
    def _request_con_proxy(self, url: str, timeout: int = 20) -> Optional[requests.Response]:
        """Realiza petición usando ProxyScrape."""
        try:
            proxy_url = (
                f"{self.PROXY_CONFIG['proxy_url']}"
                f"?apikey={self.PROXY_CONFIG['api_key']}"
                f"&url={requests.utils.quote(url)}"
            )
            
            response = requests.get(proxy_url, headers=self.headers, timeout=timeout)
            
            if response.status_code == 200:
                return response
            else:
                print(f"[PROXY] Error {response.status_code}, intentando directo...")
                return self._request_directo(url, timeout)
                
        except Exception as e:
            print(f"[PROXY] Excepción: {e}, intentando directo...")
            return self._request_directo(url, timeout)
    
    def _request_directo(self, url: str, timeout: int = 15) -> Optional[requests.Response]:
        """Realiza petición directa sin proxy."""
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            if response.status_code == 200:
                return response
            return None
        except Exception:
            return None
    
    # ==========================================================================
    # MÉTODOS DE BÚSQUEDA
    # ==========================================================================
    
    def search_properties(self, 
                          operation: str = "venta", 
                          prop_type: str = "inmuebles", 
                          location: str = "asuncion",
                          min_price: Optional[int] = None,
                          max_price: Optional[int] = None,
                          bedrooms: Optional[int] = None,
                          bathrooms: Optional[int] = None,
                          page: int = 1) -> List[Dict[str, Any]]:
        """
        Busca propiedades según los filtros especificados.
        """
        # Normalizar ubicación
        location = self._normalizar_ubicacion(location)
        
        # Intentar primero con el tipo específico
        properties = self._fetch_properties(
            operation, prop_type, location, 
            min_price, max_price, bedrooms, bathrooms, page
        )
        
        # Si no hay resultados y buscamos casas o apartamentos, probar categoría combinada
        if len(properties) == 0 and prop_type in ['casa', 'apartamento', 'departamento']:
            properties = self._fetch_properties(
                operation, 'casas-y-departamentos', location,
                min_price, max_price, bedrooms, bathrooms, page
            )
            
            # Filtrar por tipo específico
            if prop_type == 'casa':
                properties = [
                    p for p in properties 
                    if 'casa' in p['informacion_basica']['tipo_propiedad'].lower()
                ]
            elif prop_type in ['apartamento', 'departamento']:
                properties = [
                    p for p in properties 
                    if any(x in p['informacion_basica']['tipo_propiedad'].lower() 
                           for x in ['apartamento', 'departamento', 'depto'])
                ]
        
        # Si sigue sin resultados, intentar búsqueda general "inmuebles"
        if len(properties) == 0 and prop_type not in ['inmuebles', 'casas-y-departamentos']:
            properties = self._fetch_properties(
                operation, 'inmuebles', location,
                min_price, max_price, bedrooms, bathrooms, page
            )
        
        return properties
    
    def _normalizar_ubicacion(self, location: str) -> str:
        """
        Normaliza el nombre de ubicación para la URL.
        """
        if not location:
            return 'asuncion'
        
        # Convertir a minúsculas y reemplazar espacios
        location = location.lower().strip()
        location = location.replace(' ', '-')
        
        # Quitar acentos
        reemplazos = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ñ': 'n', 'ü': 'u'
        }
        for acento, sin_acento in reemplazos.items():
            location = location.replace(acento, sin_acento)
        
        return location
    
    def _construir_url(self, operation: str, prop_type_slug: str, location: str) -> str:
        """
        Construye la URL correcta según la estructura de InfoCasas.
        
        InfoCasas usa diferentes estructuras:
        - /venta/casas/asuncion (departamento capital)
        - /venta/casas/central/san-lorenzo (ciudad dentro de departamento)
        - /venta/casas/central (departamento completo)
        """
        # Caso especial: Asunción es departamento y ciudad a la vez
        if location == 'asuncion':
            return f"{self.base_url}/{operation}/{prop_type_slug}/asuncion"
        
        # Si es un departamento, usar directamente
        if location in self.CONFIG['departamentos']:
            return f"{self.base_url}/{operation}/{prop_type_slug}/{location}"
        
        # Si es una ciudad, buscar su departamento padre
        parent_dept = self.CONFIG['parents'].get(location)
        if parent_dept:
            return f"{self.base_url}/{operation}/{prop_type_slug}/{parent_dept}/{location}"
        
        # Si es un barrio de Asunción
        if location in self.CONFIG['barrios_asuncion']:
            return f"{self.base_url}/{operation}/{prop_type_slug}/asuncion/{location}"
        
        # Intentar como ubicación directa
        return f"{self.base_url}/{operation}/{prop_type_slug}/{location}"

    def _fetch_properties(self,
                         operation: str,
                         prop_type: str,
                         location: str,
                         min_price: Optional[int] = None,
                         max_price: Optional[int] = None,
                         bedrooms: Optional[int] = None,
                         bathrooms: Optional[int] = None,
                         page: int = 1) -> List[Dict[str, Any]]:
        """
        Método interno que ejecuta la búsqueda real y parsea los resultados.
        """
        # Convertir tipo de propiedad a slug de URL
        prop_type_slug = self.TIPOS_PROPIEDAD_URL.get(prop_type, prop_type + 's')
        
        # Construir URL usando el nuevo método
        url = self._construir_url(operation, prop_type_slug, location)
        
        # Agregar parámetros de filtro a la URL
        params = {}
        if page > 1: 
            params['pagina'] = page
        if min_price: 
            params['precio_desde'] = min_price
        if max_price: 
            params['precio_hasta'] = max_price
        if bedrooms: 
            params['dormitorios'] = bedrooms
        if bathrooms: 
            params['banos'] = bathrooms
        
        if params:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url += f"?{query_string}"
        
        print(f"[SCRAPER] Buscando en: {url}")
        
        try:
            response = self._hacer_request(url)
            if not response:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            script = soup.find('script', id='__NEXT_DATA__', type='application/json')
            if not script:
                return []
            
            data = json.loads(script.string)
            props_data = data.get('props', {}).get('pageProps', {})
            
            properties = []
            
            # Estructura 1: Propiedad individual con duplicados
            if 'fetchResult' in props_data and 'property' in props_data['fetchResult']:
                prop = props_data['fetchResult']['property']
                properties.append(self._extract_property_data(prop))
                if 'duplicated' in prop and prop['duplicated']:
                    for dup in prop['duplicated']:
                        properties.append(self._extract_property_data(dup))
            
            # Estructura 2: Lista de propiedades directa
            if 'properties' in props_data:
                for prop in props_data['properties']:
                    properties.append(self._extract_property_data(prop))
            
            # Estructura 3: Resultados de búsqueda rápida
            if 'fetchResult' in props_data and 'searchFast' in props_data['fetchResult']:
                search_data = props_data['fetchResult']['searchFast'].get('data', [])
                for prop in search_data:
                    properties.append(self._extract_property_data(prop))
            
            return properties
            
        except Exception as e:
            print(f"[ERROR] Error al buscar propiedades: {e}")
            return []
    
    # ==========================================================================
    # EXTRACCIÓN DE DATOS
    # ==========================================================================
    
    def _extract_property_data(self, prop: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae y estructura todos los datos de una propiedad.
        Incluye detección automática de propiedades destacadas.
        """
        # Extraer objetos anidados
        price_info = prop.get('price') or {}
        locations = prop.get('locations') or {}
        prop_type = prop.get('property_type') or {}
        currency = price_info.get('currency') or {}
        
        # Extraer ubicación
        barrio_list = locations.get('neighbourhood', [])
        barrio = barrio_list[0].get('name') if isinstance(barrio_list, list) and len(barrio_list) > 0 else None
        
        depto_list = locations.get('state', [])
        depto = depto_list[0].get('name') if isinstance(depto_list, list) and len(depto_list) > 0 else None
        
        ciudad_list = locations.get('city', [])
        ciudad = ciudad_list[0].get('name') if isinstance(ciudad_list, list) and len(ciudad_list) > 0 else None

        # ======================================================================
        # DETECCIÓN DE PROPIEDAD DESTACADA
        # ======================================================================
        destacado = False
        
        # Método 1: Campo 'featured' directo
        if prop.get('featured'):
            destacado = True
        
        # Método 2: Campo 'is_featured'
        if prop.get('is_featured'):
            destacado = True
        
        # Método 3: Campo 'highlight' o 'highlighted'
        if prop.get('highlight') or prop.get('highlighted'):
            destacado = True
        
        # Método 4: Campo 'premium'
        if prop.get('premium'):
            destacado = True
        
        # Método 5: Campo 'promoted' o 'is_promoted'
        if prop.get('promoted') or prop.get('is_promoted'):
            destacado = True
        
        # Método 6: Campo 'super' o 'super_destacado'
        if prop.get('super') or prop.get('super_destacado'):
            destacado = True
        
        # Método 7: Campo en 'tags' o 'labels'
        tags = prop.get('tags', []) or prop.get('labels', [])
        if isinstance(tags, list):
            for tag in tags:
                if isinstance(tag, str):
                    tag_lower = tag.lower()
                    if any(x in tag_lower for x in ['destacad', 'premium', 'super', 'featured']):
                        destacado = True
                        break
                elif isinstance(tag, dict):
                    tag_name = tag.get('name', '').lower()
                    if any(x in tag_name for x in ['destacad', 'premium', 'super', 'featured']):
                        destacado = True
                        break
        
        # Método 8: Campo 'plan' o 'subscription' (planes premium)
        plan = prop.get('plan') or prop.get('subscription') or {}
        if isinstance(plan, dict):
            plan_name = plan.get('name', '').lower()
            if any(x in plan_name for x in ['premium', 'super', 'destacad', 'gold', 'platinum']):
                destacado = True
        elif isinstance(plan, str) and any(x in plan.lower() for x in ['premium', 'super', 'destacad']):
            destacado = True

        # ======================================================================
        # EXTRACCIÓN DE IMÁGENES
        # ======================================================================
        imagenes = []
        
        if 'images' in prop and prop['images']:
            for img in prop['images']:
                if isinstance(img, dict):
                    url = img.get('image') or img.get('url') or img.get('original')
                    if url:
                        imagenes.append({
                            'url': url,
                            'thumbnail': img.get('thumbnail') or img.get('small') or url,
                            'alt': img.get('alt', 'Imagen de propiedad')
                        })
                elif isinstance(img, str):
                    imagenes.append({
                        'url': img,
                        'thumbnail': img,
                        'alt': 'Imagen de propiedad'
                    })
        
        if 'main_image' in prop and prop['main_image']:
            main_img = prop['main_image']
            if isinstance(main_img, dict):
                url = main_img.get('image') or main_img.get('url')
                if url and not any(i['url'] == url for i in imagenes):
                    imagenes.insert(0, {
                        'url': url,
                        'thumbnail': main_img.get('thumbnail') or url,
                        'alt': 'Imagen principal'
                    })
            elif isinstance(main_img, str) and not any(i['url'] == main_img for i in imagenes):
                imagenes.insert(0, {
                    'url': main_img,
                    'thumbnail': main_img,
                    'alt': 'Imagen principal'
                })
        
        if 'photos' in prop and prop['photos']:
            for foto in prop['photos']:
                if isinstance(foto, dict):
                    url = foto.get('url') or foto.get('image')
                    if url and not any(i['url'] == url for i in imagenes):
                        imagenes.append({
                            'url': url,
                            'thumbnail': foto.get('thumbnail') or url,
                            'alt': 'Foto de propiedad'
                        })
        
        # ======================================================================
        # EXTRACCIÓN DE COORDENADAS
        # ======================================================================
        latitud = None
        longitud = None
        
        if 'lat' in prop and 'lng' in prop:
            latitud = prop.get('lat')
            longitud = prop.get('lng')
        elif 'latitude' in prop and 'longitude' in prop:
            latitud = prop.get('latitude')
            longitud = prop.get('longitude')
        elif 'location' in prop and isinstance(prop['location'], dict):
            loc = prop['location']
            latitud = loc.get('lat') or loc.get('latitude')
            longitud = loc.get('lng') or loc.get('longitude')
        elif 'geo' in prop and isinstance(prop['geo'], dict):
            geo = prop['geo']
            latitud = geo.get('lat') or geo.get('latitude')
            longitud = geo.get('lng') or geo.get('longitude')
        
        if not latitud and locations:
            if 'lat' in locations:
                latitud = locations.get('lat')
                longitud = locations.get('lng')
        
        # ======================================================================
        # CONSTRUIR OBJETO DE RESPUESTA
        # ======================================================================
        return {
            'identificacion': {
                'id': prop.get('id')
            },
            'informacion_basica': {
                'titulo': str(prop.get('title', '')).strip(),
                'descripcion': str(prop.get('description', '')).strip(),
                'tipo_propiedad': prop_type.get('name', 'Inmueble'),
            },
            'precio': {
                'monto': price_info.get('amount'),
                'moneda': currency.get('name') or 'Gs.',
            },
            'ubicacion': {
                'ciudad': ciudad,
                'barrio': barrio,
                'departamento': depto,
                'direccion': prop.get('address') or prop.get('street'),
                'coordenadas': {
                    'latitud': latitud,
                    'longitud': longitud
                } if latitud and longitud else None
            },
            'caracteristicas': {
                'dormitorios': prop.get('bedrooms'),
                'banos': prop.get('bathrooms'),
                'metros_cuadrados': {
                    'm2_construidos': prop.get('m2Built') or prop.get('m2'),
                    'm2_terreno': prop.get('m2') if prop.get('m2Built') else None
                },
                'antiguedad': prop.get('age'),
                'garages': prop.get('garages'),
            },
            'imagenes': imagenes,
            'destacado': destacado,  # Campo destacado a nivel raíz
            'propietario': {
                'nombre': prop.get('owner', {}).get('name'),
                'whatsapp': prop.get('owner', {}).get('whatsapp_phone'),
            },
            'enlaces': {
                'url_propiedad': f"{self.base_url}{prop.get('link')}" if prop.get('link') else None,
            },
            'metadata': {
                'fecha_publicacion': prop.get('published_at') or prop.get('created_at'),
                'destacada': destacado,  # También en metadata por compatibilidad
            }
        }

    # ==========================================================================
    # DETECCIÓN DE UBICACIÓN
    # ==========================================================================
    
    def _detectar_ubicacion(self, query: str) -> Optional[str]:
        """
        Detecta la ubicación mencionada en un texto de búsqueda.
        """
        # Normalizar texto
        query_norm = query.lower()
        reemplazos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n'}
        for acento, sin_acento in reemplazos.items():
            query_norm = query_norm.replace(acento, sin_acento)
        
        # Paso 1: Buscar en variaciones (más específicas)
        for slug, vars_list in self.CONFIG['variaciones'].items():
            for var in vars_list:
                pattern = rf'\b{re.escape(var)}\b'
                if re.search(pattern, query_norm):
                    return slug
        
        # Paso 2: Buscar en barrios de Asunción
        for barrio in self.CONFIG['barrios_asuncion']:
            barrio_clean = barrio.replace('-', ' ')
            pattern = rf'\b{re.escape(barrio_clean)}\b'
            if re.search(pattern, query_norm):
                return barrio
        
        # Paso 3: Buscar en lista de ciudades
        for ciudad in self.CONFIG['ciudades']:
            ciudad_clean = ciudad.replace('-', ' ')
            pattern = rf'\b{re.escape(ciudad_clean)}\b'
            if re.search(pattern, query_norm):
                return ciudad
        
        # Paso 4: Buscar en lista de departamentos
        for depto in self.CONFIG['departamentos']:
            depto_clean = depto.replace('-', ' ')
            pattern = rf'\b{re.escape(depto_clean)}\b'
            if re.search(pattern, query_norm):
                return depto
            
        return None


# =============================================================================
# EJEMPLO DE USO
# =============================================================================
if __name__ == "__main__":
    scraper = InfocasasScraper()
    
    print("Buscando casas en venta en Asunción...")
    resultados = scraper.search_properties(
        operation="venta",
        prop_type="casa",
        location="asuncion",
        max_price=200000
    )
    
    print(f"\nSe encontraron {len(resultados)} propiedades:")
    for i, prop in enumerate(resultados[:3], 1):
        print(f"\n--- Propiedad {i} ---")
        print(f"Título: {prop['informacion_basica']['titulo'][:50]}...")
        print(f"Precio: {prop['precio']['moneda']} {prop['precio']['monto']}")
        print(f"Destacado: {'Sí' if prop['destacado'] else 'No'}")
        print(f"Ubicación: {prop['ubicacion']['barrio']}, {prop['ubicacion']['ciudad']}")
        print(f"Imágenes: {len(prop['imagenes'])} fotos")
