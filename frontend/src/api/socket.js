let socket = null
let animationFrameId = null

export function connectSongSocket(song, {
  onFrame,
  getCanvasContext,
  getCanvasElement,
  getAudioElement // Pass the HTML5 audio element here
}) {
  disconnectSongSocket()

  const wsUrl = `ws://localhost:8000/ws/${encodeURIComponent(song)}`
  socket = new WebSocket(wsUrl)
  socket.binaryType = 'arraybuffer'

  socket.onopen = () => {
    function sendFrameRequest() {
      const audio = getAudioElement()

      // Only request frames if the socket is open and audio is actively playing
      if (socket?.readyState === 1 && audio && !audio.paused) {
        // Convert audio.currentTime (seconds) to milliseconds for your backend
        const timeMs = Math.floor(audio.currentTime * 1000)

        socket.send(JSON.stringify({ time: timeMs }))
      }

      // Continue the loop
      animationFrameId = requestAnimationFrame(sendFrameRequest)
    }

    // Start the animation loop
    animationFrameId = requestAnimationFrame(sendFrameRequest)
  }

  socket.onmessage = async (event) => {
    const blob = new Blob([event.data], { type: 'image/webp' })
    const bitmap = await createImageBitmap(blob)

    const ctx = getCanvasContext()
    const canvas = getCanvasElement()

    if (!ctx || !canvas) return

    // Dynamic resize handler
    if (canvas.width !== canvas.clientWidth || canvas.height !== canvas.clientHeight) {
      canvas.width = canvas.clientWidth
      canvas.height = canvas.clientHeight
    }

    ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height)
    if (onFrame) onFrame()
  }

  socket.onerror = (err) => {
    console.error('WebSocket error:', err)
  }
}

export function disconnectSongSocket() {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }

  if (socket) {
    socket.close()
    socket = null
  }
}
