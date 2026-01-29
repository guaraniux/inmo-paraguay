'use client'

import { useState, useEffect, useRef } from 'react'

interface LazyImageProps {
  src: string
  alt: string
  className?: string
  onClick?: () => void
}

export default function LazyImage({ src, alt, className = '', onClick }: LazyImageProps) {
  const [isLoaded, setIsLoaded] = useState(false)
  const [isInView, setIsInView] = useState(false)
  const [error, setError] = useState(false)
  const imgRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true)
          observer.disconnect()
        }
      },
      { rootMargin: '100px' }
    )

    if (imgRef.current) {
      observer.observe(imgRef.current)
    }

    return () => observer.disconnect()
  }, [])

  const handleLoad = () => setIsLoaded(true)
  const handleError = () => setError(true)

  const placeholderSvg = `data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"><rect fill="%23e2e8f0" width="400" height="300"/><text fill="%2394a3b8" font-size="14" x="50%" y="50%" text-anchor="middle" dy=".3em">Sin imagen</text></svg>`

  return (
    <div 
      ref={imgRef}
      className={`lazy-image ${isLoaded ? 'loaded' : ''} ${className}`}
      onClick={onClick}
    >
      {isInView && (
        <img
          src={error ? placeholderSvg : src}
          alt={alt}
          className={`w-full h-full object-cover transition-opacity duration-300 ${isLoaded ? 'opacity-100' : 'opacity-0'}`}
          onLoad={handleLoad}
          onError={handleError}
          loading="lazy"
        />
      )}
    </div>
  )
}
