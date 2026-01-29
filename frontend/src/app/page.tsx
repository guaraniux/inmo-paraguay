'use client'

import { useState, useRef, useEffect } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faHouse, faRotateRight, faPaperPlane } from '@fortawesome/free-solid-svg-icons'
import { faTelegram } from '@fortawesome/free-brands-svg-icons'
import ChatMessage from '../components/chat/ChatMessage'
import TypingIndicator from '../components/ui/TypingIndicator'
import ThemeToggle from '../components/ui/ThemeToggle'
import { Mensaje, Inmueble } from '../lib/types'
import { cleanResponse, removeDuplicates } from '../lib/utils'

const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' && window.location.hostname.includes('vercel.app') 
  ? 'https://inmo-backend-e6zz.onrender.com' 
  : 'http://localhost:8000')

export default function HomePage() {
  const [mensajes, setMensajes] = useState<Mensaje[]>([])
  const [inputMensaje, setInputMensaje] = useState('')
  const [cargando, setCargando] = useState(false)
  const [sessionId] = useState(() => `session_${Date.now()}`)
  const [apiError, setApiError] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [mensajes, cargando])

  useEffect(() => {
    const iniciarChat = async () => {
      setCargando(true)
      try {
        const response = await fetch(`${API_URL}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            mensaje: 'Hola, presentate brevemente y preguntame que tipo de inmueble estoy buscando', 
            session_id: sessionId 
          })
        })
        if (!response.ok) throw new Error('Error en la API')
        const data = await response.json()
        setMensajes([{ rol: 'assistant', contenido: cleanResponse(data.respuesta) }])
      } catch {
        setApiError(true)
        setMensajes([{ 
          rol: 'assistant', 
          contenido: 'No puedo conectar con el servidor. Por favor, asegurate de que el backend este corriendo.\n\nEjecuta en una terminal:\ncd backend\npython main.py'
        }])
      } finally {
        setCargando(false)
      }
    }
    iniciarChat()
  }, [sessionId])

  const enviarMensaje = async () => {
    if (!inputMensaje.trim() || cargando) return

    const mensaje = inputMensaje.trim()
    setMensajes(prev => [...prev, { rol: 'user', contenido: mensaje }])
    setInputMensaje('')
    setCargando(true)
    setApiError(false)

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mensaje, session_id: sessionId })
      })

      if (!response.ok) throw new Error('Error en la API')

      const data = await response.json()
      
      const inmueblesUnicos = data.propiedades?.length > 0 
        ? removeDuplicates<Inmueble>(data.propiedades) 
        : undefined

      setMensajes(prev => [...prev, { 
        rol: 'assistant', 
        contenido: cleanResponse(data.respuesta),
        inmuebles: inmueblesUnicos
      }])

    } catch {
      setApiError(true)
      setMensajes(prev => [...prev, { 
        rol: 'assistant', 
        contenido: 'Hubo un problema de conexion. Por favor, intenta de nuevo.'
      }])
    } finally {
      setCargando(false)
      inputRef.current?.focus()
    }
  }

  const reiniciarChat = async () => {
    try {
      await fetch(`${API_URL}/sesion/${sessionId}`, { method: 'DELETE' })
    } catch {}
    setMensajes([])
    setApiError(false)
    setCargando(true)
    
    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          mensaje: 'Hola, presentate brevemente y preguntame que tipo de inmueble estoy buscando', 
          session_id: sessionId 
        })
      })
      if (!response.ok) throw new Error('Error')
      const data = await response.json()
      setMensajes([{ rol: 'assistant', contenido: cleanResponse(data.respuesta) }])
    } catch {
      setMensajes([{ rol: 'assistant', contenido: 'Error al reiniciar. Intenta de nuevo.' }])
    } finally {
      setCargando(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      enviarMensaje()
    }
  }

  const currentYear = new Date().getFullYear()

  return (
    <main className="min-h-screen flex flex-col bg-[var(--bg-secondary)] transition-colors duration-300">
      {/* Header */}
      <header className="glass border-b border-[var(--border-color)] sticky top-0 z-40">
        <div className="max-w-2xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25 hover-glow">
                <FontAwesomeIcon icon={faHouse} className="w-4 h-4 text-white" />
              </div>
              {!apiError && (
                <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 rounded-full border-2 border-[var(--bg-primary)]"></span>
              )}
            </div>
            <div>
              <span className="font-bold text-[var(--text-primary)]">INMO</span>
              <p className="text-[10px] text-[var(--text-tertiary)] -mt-0.5">Asistente Inmobiliario</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <button 
              onClick={reiniciarChat}
              className="btn-ghost btn-icon"
              title="Nueva conversacion"
            >
              <FontAwesomeIcon icon={faRotateRight} className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Chat area */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        <div className="max-w-2xl mx-auto px-4 py-6">
          <div className="space-y-5">
            {mensajes.map((msg, idx) => (
              <ChatMessage key={idx} mensaje={msg} />
            ))}
            
            {cargando && (
              <div className="animate-fade-in">
                <TypingIndicator />
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input */}
      <div className="glass border-t border-[var(--border-color)] sticky bottom-0">
        <div className="max-w-2xl mx-auto px-4 py-3">
          <div className="flex gap-2">
            <input
              ref={inputRef}
              type="text"
              value={inputMensaje}
              onChange={(e) => setInputMensaje(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Escribe tu mensaje..."
              className="input-chat flex-1 px-4 py-3 text-sm"
              disabled={cargando}
            />
            <button
              onClick={enviarMensaje}
              disabled={cargando || !inputMensaje.trim()}
              className="btn-primary px-5 py-3"
            >
              <FontAwesomeIcon icon={faPaperPlane} className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        {/* Footer */}
        <div className="border-t border-[var(--border-color)] py-2">
          <div className="max-w-2xl mx-auto px-4 flex items-center justify-center gap-2 text-xs text-[var(--text-tertiary)]">
            <span>© {currentYear}</span>
            <span>·</span>
            <a 
              href="https://t.me/guaraniux" 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 hover:text-[var(--color-primary)] transition-colors"
            >
              <FontAwesomeIcon icon={faTelegram} className="w-3.5 h-3.5" />
              Guaraniux
            </a>
          </div>
        </div>
      </div>
    </main>
  )
}
