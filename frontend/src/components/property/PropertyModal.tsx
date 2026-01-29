'use client'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { 
  faBed, 
  faBath, 
  faRulerCombined, 
  faLocationDot,
  faStar,
  faTag,
  faKey
} from '@fortawesome/free-solid-svg-icons'
import Modal from '../ui/Modal'
import ImageCarousel from '../ui/ImageCarousel'
import { Inmueble } from '../../lib/types'
import { formatPrice } from '../../lib/utils'

interface PropertyModalProps {
  inmueble: Inmueble | null
  isOpen: boolean
  onClose: () => void
}

// Funcion para pluralizar correctamente
function pluralize(count: number | string, singular: string, plural: string): string {
  const num = typeof count === 'string' ? parseInt(count) : count
  return num === 1 ? singular : plural
}

export default function PropertyModal({ inmueble, isOpen, onClose }: PropertyModalProps) {
  if (!inmueble) return null

  const images = inmueble.imagenes || []
  
  // Obtener valores numericos para pluralizacion
  const numDormitorios = typeof inmueble.dormitorios === 'string' 
    ? parseInt(inmueble.dormitorios) || 0 
    : inmueble.dormitorios || 0
  const numBanos = typeof inmueble.banos === 'string' 
    ? parseInt(inmueble.banos) || 0 
    : inmueble.banos || 0

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="bg-[var(--bg-primary)] rounded-2xl overflow-hidden max-w-lg w-full max-h-[90vh] overflow-y-auto animate-slide-up shadow-2xl">
        {/* Carrusel de imagenes con badges */}
        <div className="relative">
          <ImageCarousel images={images} />
          
          {/* Badges sobre la imagen - solo izquierda */}
          <div className="absolute top-3 left-3 flex flex-wrap gap-2">
            {/* Badge de operacion */}
            <span className={`px-3 py-1.5 rounded-lg text-xs font-bold shadow-lg flex items-center gap-1.5 ${
              inmueble.operacion === 'alquiler' 
                ? 'bg-amber-500 text-white' 
                : 'bg-emerald-500 text-white'
            }`}>
              <FontAwesomeIcon icon={inmueble.operacion === 'alquiler' ? faKey : faTag} className="w-3 h-3" />
              {inmueble.operacion === 'alquiler' ? 'ALQUILER' : 'VENTA'}
            </span>
            
            {/* Badge destacado */}
            {inmueble.destacado && (
              <span className="px-3 py-1.5 bg-gradient-to-r from-yellow-400 to-amber-500 text-white rounded-lg text-xs font-bold shadow-lg flex items-center gap-1.5">
                <FontAwesomeIcon icon={faStar} className="w-3 h-3" />
                DESTACADO
              </span>
            )}
          </div>
        </div>
        
        {/* Contenido */}
        <div className="p-5">
          {/* Precio y ID */}
          <div className="flex items-center justify-between mb-4">
            <span className="text-3xl font-bold gradient-text">
              {formatPrice(inmueble.precio_numerico, inmueble.moneda)}
            </span>
            <span className="px-3 py-1.5 bg-[var(--bg-tertiary)] text-[var(--text-secondary)] rounded-lg text-xs font-mono">
              ID: {inmueble.id}
            </span>
          </div>
          
          {/* Ubicacion */}
          <div className="flex items-start gap-2 text-[var(--text-secondary)] mb-5">
            <FontAwesomeIcon icon={faLocationDot} className="w-4 h-4 mt-0.5 text-[var(--color-primary)]" />
            <span className="text-sm leading-tight">{inmueble.ubicacion}</span>
          </div>
          
          {/* Caracteristicas */}
          <div className="grid grid-cols-3 gap-3">
            {inmueble.dormitorios && inmueble.dormitorios !== '?' && (
              <div className="bg-[var(--bg-tertiary)] rounded-xl p-3 text-center hover-glow transition-all">
                <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center mx-auto mb-2">
                  <FontAwesomeIcon icon={faBed} className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <p className="text-lg font-bold text-[var(--text-primary)]">{inmueble.dormitorios}</p>
                <p className="text-xs text-[var(--text-tertiary)] uppercase tracking-wide">
                  {pluralize(numDormitorios, 'Dormitorio', 'Dormitorios')}
                </p>
              </div>
            )}
            
            {inmueble.banos && inmueble.banos !== '?' && (
              <div className="bg-[var(--bg-tertiary)] rounded-xl p-3 text-center hover-glow transition-all">
                <div className="w-10 h-10 bg-emerald-100 dark:bg-emerald-900/30 rounded-xl flex items-center justify-center mx-auto mb-2">
                  <FontAwesomeIcon icon={faBath} className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                </div>
                <p className="text-lg font-bold text-[var(--text-primary)]">{inmueble.banos}</p>
                <p className="text-xs text-[var(--text-tertiary)] uppercase tracking-wide">
                  {pluralize(numBanos, 'Baño', 'Baños')}
                </p>
              </div>
            )}
            
            {inmueble.m2 && inmueble.m2 !== 'No especificado' && (
              <div className="bg-[var(--bg-tertiary)] rounded-xl p-3 text-center hover-glow transition-all">
                <div className="w-10 h-10 bg-violet-100 dark:bg-violet-900/30 rounded-xl flex items-center justify-center mx-auto mb-2">
                  <FontAwesomeIcon icon={faRulerCombined} className="w-5 h-5 text-violet-600 dark:text-violet-400" />
                </div>
                <p className="text-lg font-bold text-[var(--text-primary)]">{inmueble.m2}</p>
                <p className="text-xs text-[var(--text-tertiary)] uppercase tracking-wide">Superficie</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Modal>
  )
}
