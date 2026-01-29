'use client'

import { useEffect, useRef, useState, memo } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faMapLocationDot } from '@fortawesome/free-solid-svg-icons'
import { Inmueble } from '../../lib/types'
import { formatPrice } from '../../lib/utils'

interface PropertyMapProps {
  inmuebles: Inmueble[]
  onInmuebleClick: (inmueble: Inmueble) => void
}

function PropertyMapComponent({ inmuebles, onInmuebleClick }: PropertyMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const markersRef = useRef<any[]>([])
  const [isLoaded, setIsLoaded] = useState(false)

  const inmueblesConCoords = inmuebles.filter(i => i.coordenadas)

  useEffect(() => {
    if (typeof window === 'undefined' || inmueblesConCoords.length === 0) return

    const loadLeaflet = async () => {
      if (!document.querySelector('link[href*="leaflet"]')) {
        const link = document.createElement('link')
        link.rel = 'stylesheet'
        link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
        document.head.appendChild(link)
      }

      if (!(window as any).L) {
        await new Promise<void>((resolve) => {
          const script = document.createElement('script')
          script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
          script.onload = () => resolve()
          document.head.appendChild(script)
        })
      }

      setIsLoaded(true)
    }

    loadLeaflet()

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [inmueblesConCoords.length])

  useEffect(() => {
    if (!isLoaded || !mapRef.current || inmueblesConCoords.length === 0) return

    const L = (window as any).L
    if (!L) return

    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove()
    }

    const avgLat = inmueblesConCoords.reduce((sum, i) => sum + i.coordenadas!.latitud, 0) / inmueblesConCoords.length
    const avgLng = inmueblesConCoords.reduce((sum, i) => sum + i.coordenadas!.longitud, 0) / inmueblesConCoords.length

    const map = L.map(mapRef.current, {
      zoomControl: false,
      attributionControl: false
    }).setView([avgLat, avgLng], 13)

    mapInstanceRef.current = map

    L.control.zoom({ position: 'bottomright' }).addTo(map)

    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      maxZoom: 19
    }).addTo(map)

    const bounds: [number, number][] = []
    markersRef.current = []

    inmueblesConCoords.forEach((inmueble) => {
      const lat = inmueble.coordenadas!.latitud
      const lng = inmueble.coordenadas!.longitud
      bounds.push([lat, lng])

      const imagen = inmueble.imagenes?.[0]?.thumbnail || inmueble.imagenes?.[0]?.url
      const precio = formatPrice(inmueble.precio_numerico, inmueble.moneda)
      
      const opBadge = inmueble.operacion === 'alquiler' 
        ? '<span style="background:#f59e0b;color:white;padding:3px 8px;border-radius:6px;font-size:10px;font-weight:700;text-transform:uppercase;">Alquiler</span>'
        : '<span style="background:#10b981;color:white;padding:3px 8px;border-radius:6px;font-size:10px;font-weight:700;text-transform:uppercase;">Venta</span>'
      
      const destacadoBadge = inmueble.destacado 
        ? '<span style="background:linear-gradient(135deg,#fbbf24,#f59e0b);color:white;padding:3px 8px;border-radius:6px;font-size:10px;font-weight:700;margin-left:4px;">★</span>'
        : ''

      const iconHtml = `
        <div class="property-marker" style="
          position: relative;
          cursor: pointer;
          transition: transform 0.2s ease;
        ">
          <div style="
            width: 130px;
            height: 95px;
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 6px 25px rgba(0,0,0,0.35);
            border: 3px solid white;
            background: #f1f5f9;
            position: relative;
          ">
            ${imagen ? `<img src="${imagen}" style="width:100%;height:100%;object-fit:cover;" onerror="this.style.display='none'" />` : '<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;color:#94a3b8;font-size:12px;">Sin imagen</div>'}
            <div style="
              position: absolute;
              top: 6px;
              left: 6px;
              display: flex;
              align-items: center;
            ">${opBadge}${destacadoBadge}</div>
            <div style="
              position: absolute;
              bottom: 0;
              left: 0;
              right: 0;
              background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);
              padding: 12px 8px 6px;
            ">
              <span style="
                color: white;
                font-size: 13px;
                font-weight: 700;
                text-shadow: 0 1px 3px rgba(0,0,0,0.5);
                white-space: nowrap;
              ">${precio}</span>
            </div>
          </div>
          <div style="
            width: 0;
            height: 0;
            border-left: 12px solid transparent;
            border-right: 12px solid transparent;
            border-top: 12px solid white;
            margin: -1px auto 0;
            filter: drop-shadow(0 3px 3px rgba(0,0,0,0.2));
          "></div>
        </div>
      `

      const icon = L.divIcon({
        className: 'custom-property-marker',
        html: iconHtml,
        iconSize: [130, 115],
        iconAnchor: [65, 115]
      })

      const marker = L.marker([lat, lng], { icon })
        .addTo(map)
        .on('click', () => onInmuebleClick(inmueble))

      marker.on('mouseover', function() {
        const el = marker.getElement()
        if (el) {
          el.style.zIndex = '1000'
          const pm = el.querySelector('.property-marker') as HTMLElement
          if (pm) pm.style.transform = 'scale(1.08)'
        }
      })
      marker.on('mouseout', function() {
        const el = marker.getElement()
        if (el) {
          el.style.zIndex = ''
          const pm = el.querySelector('.property-marker') as HTMLElement
          if (pm) pm.style.transform = ''
        }
      })

      markersRef.current.push(marker)
    })

    if (bounds.length > 1) {
      map.fitBounds(bounds, { padding: [60, 60] })
    }
  }, [isLoaded, inmueblesConCoords, onInmuebleClick])

  if (inmueblesConCoords.length === 0) {
    return (
      <div className="h-full bg-[var(--bg-tertiary)] rounded-2xl flex items-center justify-center">
        <div className="text-center text-[var(--text-tertiary)]">
          <FontAwesomeIcon icon={faMapLocationDot} className="w-10 h-10 mb-2 opacity-50" />
          <p className="text-sm">Sin ubicaciones disponibles</p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative h-full rounded-2xl overflow-hidden">
      <div ref={mapRef} className="w-full h-full" style={{ minHeight: '350px' }} />
      <div className="absolute top-3 left-3 px-3 py-1.5 bg-[var(--bg-primary)]/90 backdrop-blur-sm rounded-full shadow-lg">
        <span className="text-xs font-medium text-[var(--text-primary)]">
          {inmueblesConCoords.length} inmuebles
        </span>
      </div>
    </div>
  )
}

// Memoizar el componente para evitar re-renders innecesarios
const PropertyMap = memo(PropertyMapComponent, (prevProps, nextProps) => {
  // Solo re-renderizar si cambian los inmuebles
  if (prevProps.inmuebles.length !== nextProps.inmuebles.length) return false
  
  // Comparar IDs de inmuebles
  const prevIds = prevProps.inmuebles.map(i => i.id).join(',')
  const nextIds = nextProps.inmuebles.map(i => i.id).join(',')
  
  return prevIds === nextIds
})

export default PropertyMap
