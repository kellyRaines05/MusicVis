<template>
  <div class="visualizer-container">
    <audio
      ref="audioPlayer"
      :src="songFileUrl"
      controls
      @play="onPlay"
      class="audio-controls"
    ></audio>

    <canvas ref="canvas" class="fullscreen-canvas" />
  </div>
</template>

<script setup>
  import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
  import { connectSongSocket, disconnectSongSocket } from '@/api/socket.js'

  const props = defineProps({
    song: String
  })

  const canvas = ref(null)
  const audioPlayer = ref(null)
  let ctx = null

  // Computed property to point to your backend audio streaming endpoint
  const songFileUrl = computed(() => {
    if (!props.song) return ''
    return `http://localhost:8000/audio/${encodeURIComponent(props.song)}`
  })

  watch(() => props.song, (song, oldSong) => {
    if (oldSong) {
      disconnectSongSocket()
    }

    if (!song) {
      clearCanvas()
      return
    }

    connectSongSocket(song, {
      getCanvasContext: () => {
        if (!ctx && canvas.value) {
          ctx = canvas.value.getContext('2d')
        }
        return ctx
      },
      getCanvasElement: () => canvas.value,
      getAudioElement: () => audioPlayer.value // Provide audio element to the loop
    })
  }, { immediate: true })

  function clearCanvas() {
    const canvasEl = canvas.value
    if (!canvasEl) return

    const context = canvasEl.getContext('2d')
    if (!context) return

    canvasEl.width = canvasEl.clientWidth
    canvasEl.height = canvasEl.clientHeight

    context.fillStyle = '#000000'
    context.fillRect(0, 0, canvasEl.width, canvasEl.height)
  }

  onMounted(() => {
    clearCanvas()
  })

  onUnmounted(() => {
    disconnectSongSocket()
  })
</script>

<style scoped>
    .visualizer-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1rem;
    }
    .fullscreen-canvas {
      width: 40vw;
      height: 60vh;
      display: block;
      background: #000;
    }
    .audio-controls {
      width: 40vw;
    }
</style>
