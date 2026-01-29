'use client'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faExpand, faStar } from '@fortawesome/free-solid-svg-icons'
import LazyImage from '../ui/LazyImage'
import { Inmueble } from '../../lib/types'
import { formatPrice } from '../../lib/utils'

interface PropertyMiniCardProps {
  inmueble: Inmueble
  onClick: () => void
}

export default function PropertyMiniCard({ inmueble, onClick }: PropertyMiniCardProps) {
  const imagen = inmueble.imagenes?.[0]?.thumbnail || inmueble.imagenes?.[0]?.url
  
  return (
    <div className="property-mini group" onClick={onClick}>
      <div className="aspect-[4/3] bg-gray-200 dark:bg-gray-700 relative">
        {imagen ? (
          <LazyImage
            src={imagen}
            alt={inmueble.titulo}
            className="w-full h-full"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800">
            <span className="text-gray-400 dark:text-gray-500 text-xs">Sin imagen</span>
          </div>
        )}
        
        {/* Badge destacado */}
        {inmueble.destacado && (
          <div className="absolute top-2 left-2">
            <span className="px-2 py-1 bg-gradient-to-r from-yellow-400 to-amber-500 text-white rounded-md text-[10px] font-bold flex items-center gap-1 shadow-md">
              <FontAwesomeIcon icon={faStar} className="w-2.5 h-2.5" />
              Destacado
            </span>
          </div>
        )}
        
        {/* Badge operacion - texto completo */}
        <div className="absolute top-2 right-2">
          <span className={`px-2 py-1 rounded-md text-[10px] font-bold shadow-md uppercase ${
            inmueble.operacion === 'alquiler' 
              ? 'bg-amber-500 text-white' 
              : 'bg-emerald-500 text-white'
          }`}>
            {inmueble.operacion === 'alquiler' ? 'Alquiler' : 'Venta'}
          </span>
        </div>
      </div>
      
      <div className="property-mini-overlay">
        <p className="text-white font-semibold text-sm drop-shadow-lg">
          {formatPrice(inmueble.precio_numerico, inmueble.moneda)}
        </p>
        <p className="text-white/70 text-[10px] mt-0.5 font-mono">ID: {inmueble.id}</p>
      </div>
      
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-all duration-200">
        <div className="w-10 h-10 bg-white/95 rounded-full flex items-center justify-center shadow-lg">
          <FontAwesomeIcon icon={faExpand} className="w-4 h-4 text-gray-700" />
        </div>
      </div>
    </div>
  )
}
