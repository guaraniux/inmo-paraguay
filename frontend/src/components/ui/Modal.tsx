'use client'

import { useEffect, useCallback, ReactNode, useState } from 'react'
import { createPortal } from 'react-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faXmark } from '@fortawesome/free-solid-svg-icons'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  children: ReactNode
}

export default function Modal({ isOpen, onClose, children }: ModalProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') onClose()
  }, [onClose])

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'hidden'
    }
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, handleKeyDown])

  if (!isOpen || !mounted) return null

  const modalContent = (
    <div 
      className="fixed inset-0 z-[9999] flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.92)' }}
      onClick={onClose}
    >
      {/* Boton cerrar - posicion fija en la pantalla */}
      <button
        onClick={onClose}
        className="fixed top-4 right-4 w-11 h-11 flex items-center justify-center text-white/80 hover:text-white bg-white/10 hover:bg-white/20 rounded-full transition-all duration-200 z-[10000]"
        aria-label="Cerrar"
      >
        <FontAwesomeIcon icon={faXmark} className="w-5 h-5" />
      </button>
      
      <div 
        className="animate-fade-in-scale relative"
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  )

  return createPortal(modalContent, document.body)
}
