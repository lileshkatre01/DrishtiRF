import { useState, useEffect, useRef, useCallback } from 'react'

export function useWebSocket(jobId) {
  const [messages, setMessages] = useState([])
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)

  const connect = useCallback(() => {
    if (!jobId) return
    const ws = new WebSocket(`ws://127.0.0.1:8000/api/ws/jobs/${jobId}`)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
    }
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setMessages(prev => [...prev, data])
      } catch (_) {}
    }
    ws.onclose = () => {
      setConnected(false)
    }
    ws.onerror = () => {
      setConnected(false)
    }

    return () => ws.close()
  }, [jobId])

  useEffect(() => {
    const cleanup = connect()
    return cleanup
  }, [connect])

  const sendPing = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'ping' }))
    }
  }, [])

  return { messages, connected, sendPing }
}
