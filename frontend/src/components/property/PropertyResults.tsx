'use client'

import { useState, useCallback, useMemo } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faMap, faGrip } from '@fortawesome/free-solid-svg-icons'
import PropertyMiniCard from './PropertyMiniCard'
import PropertyModal from './PropertyModal'
import PropertyMap from './PropertyMap'
import { Inmueble } from '../../lib/types'

interface PropertyResultsProps {
  inmuebles: Inmueble[]
}

export default function PropertyResults({ inmuebles }: PropertyResultsProps) {
  const [selectedInmueble, setSelectedInmueble] = useState<Inmueble | null>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'map'>('grid')
  
  // Memoizar el callback para evitar re-renders del mapa
  const handleInmuebleClick = useCallback((inmueble: Inmueble) => {
    setSelectedInmueble(inmueble)
  }, [])

  const handleCloseModal = useCallback(() => {
    setSelectedInmueble(null)
  }, [])

  // Memoizar la lista de inmuebles con coordenadas
  const inmueblesConCoords = useMemo(() => 
    inmuebles.filter(i => i.coordenadas), 
    [inmuebles]
  )
  
  if (!inmuebles || inmuebles.length === 0) return null

  const hasCoordinates = inmueblesConCoords.length > 0

  return (
    <>
      {/* Toggle de vista */}
      {hasCoordinates && (
        <div className="flex items-center gap-1 mb-3 p-1 bg-[var(--bg-tertiary)] rounded-xl w-fit">
          <button
            onClick={() => setViewMode('grid')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              viewMode === 'grid' 
                ? 'bg-[var(--bg-primary)] text-[var(--text-primary)] shadow-sm' 
                : 'text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]'
            }`}
          >
            <FontAwesomeIcon icon={faGrip} className="w-3 h-3" />
            Grid
          </button>
          <button
            onClick={() => setViewMode('map')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              viewMode === 'map' 
                ? 'bg-[var(--bg-primary)] text-[var(--text-primary)] shadow-sm' 
                : 'text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]'
            }`}
          >
            <FontAwesomeIcon icon={faMap} className="w-3 h-3" />
            Mapa
          </button>
        </div>
      )}

      {/* Vista Grid */}
      {viewMode === 'grid' && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 animate-fade-in">
          {inmuebles.map((inmueble, index) => (
            <div 
              key={inmueble.id} 
              className="animate-fade-in"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <PropertyMiniCard
                inmueble={inmueble}
                onClick={() => setSelectedInmueble(inmueble)}
              />
            </div>
          ))}
        </div>
      )}

      {/* Vista Mapa */}
      {viewMode === 'map' && hasCoordinates && (
        <div className="h-[400px] animate-fade-in">
          <PropertyMap
            inmuebles={inmuebles}
            onInmuebleClick={handleInmuebleClick}
          />
        </div>
      )}
      
      <PropertyModal
        inmueble={selectedInmueble}
        isOpen={!!selectedInmueble}
        onClose={handleCloseModal}
      />
    </>
  )
}
