'use client'

import { useState, useEffect, useCallback } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faChevronLeft, faChevronRight } from '@fortawesome/free-solid-svg-icons'
import LazyImage from './LazyImage'

interface ImageCarouselProps {
  images: Array<{ url: string; thumbnail?: string; alt?: string }>
  autoPlay?: boolean
  interval?: number
}

export default function ImageCarousel({ images, autoPlay = false, interval = 4000 }: ImageCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isHovered, setIsHovered] = useState(false)

  const nextSlide = useCallback(() => {
    setCurrentIndex(prev => (prev + 1) % images.length)
  }, [images.length])

  const prevSlide = useCallback(() => {
    setCurrentIndex(prev => (prev - 1 + images.length) % images.length)
  }, [images.length])

  const goToSlide = (index: number) => {
    setCurrentIndex(index)
  }

  useEffect(() => {
    if (!autoPlay || isHovered || images.length <= 1) return

    const timer = setInterval(nextSlide, interval)
    return () => clearInterval(timer)
  }, [autoPlay, isHovered, interval, nextSlide, images.length])

  if (!images || images.length === 0) {
    return (
      <div className="aspect-[4/3] bg-gray-200 dark:bg-gray-700 flex items-center justify-center rounded-xl">
        <span className="text-gray-400 dark:text-gray-500 text-sm">Sin imagenes</span>
      </div>
    )
  }

  return (
    <div 
      className="carousel-container relative rounded-xl overflow-hidden group"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Track */}
      <div 
        className="carousel-track"
        style={{ transform: `translateX(-${currentIndex * 100}%)` }}
      >
        {images.map((img, idx) => (
          <div key={idx} className="carousel-slide aspect-[4/3]">
            <LazyImage
              src={img.url || img.thumbnail || ''}
              alt={img.alt || ''}
              className="w-full h-full"
            />
          </div>
        ))}
      </div>

      {/* Navigation arrows */}
      {images.length > 1 && (
        <>
          <button
            onClick={prevSlide}
            className="absolute left-3 top-1/2 -translate-y-1/2 w-10 h-10 bg-black/40 hover:bg-black/60 backdrop-blur-sm rounded-full flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-all duration-300 transform -translate-x-2 group-hover:translate-x-0"
          >
            <FontAwesomeIcon icon={faChevronLeft} className="w-4 h-4" />
          </button>
          <button
            onClick={nextSlide}
            className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 bg-black/40 hover:bg-black/60 backdrop-blur-sm rounded-full flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-x-2 group-hover:translate-x-0"
          >
            <FontAwesomeIcon icon={faChevronRight} className="w-4 h-4" />
          </button>
        </>
      )}

      {/* Dots indicator */}
      {images.length > 1 && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-1.5">
          {images.map((_, idx) => (
            <button
              key={idx}
              onClick={() => goToSlide(idx)}
              className={`carousel-dot ${idx === currentIndex ? 'active' : ''}`}
            />
          ))}
        </div>
      )}

      {/* Counter */}
      <div className="absolute top-3 right-3 px-2.5 py-1 bg-black/50 backdrop-blur-sm rounded-full">
        <span className="text-white text-xs font-medium">
          {currentIndex + 1} / {images.length}
        </span>
      </div>
    </div>
  )
}
