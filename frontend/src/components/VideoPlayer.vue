<template>
  <div class="q-pa-md">
    <div class="video-wrapper">
      <q-media-player
        v-if="hasSong"
        class="video-player"
        type="video"
        :sources="sources"
        dense
        dark
      />

      <div v-else class="no-song-placeholder" role="button">
        No song selected
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { QMediaPlayer } from '@quasar/quasar-ui-qmediaplayer'
import '@quasar/quasar-ui-qmediaplayer/dist/index.css'

const props = defineProps({
  song: String
})

const hasSong = computed(() => Boolean(props.song))

const sources = computed(() => {
  if (!hasSong.value) return []

  return [
    {
      src: `http://localhost:8000/video/${encodeURIComponent(props.song)}`,
      type: 'video/mp4'
    }
  ]
})
</script>

<style scoped>
  .video-player,
  .no-song-placeholder {
    min-width: 1028px;
    min-height: 768px;
    border-radius: 16px;
    overflow: hidden;
  }

  .video-player :deep(.q-media--big-button) {
    width: 4rem;
    height: 4rem;
  }

  .video-player {
    --big-play-button-color: var(--q-accent);
    --big-play-button-background: var(--q-primary);
    --big-play-button-border: var(--q-secondary);
    --big-play-button-hover-background: var(--q-primary) ;
    --big-play-button-border: var(--q-secondary) 2px solid;
    --big-play-button-border-hover: var(--q-secondary) 2px solid;
  }

  .no-song-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #000;
    color: #fff;
    font-size: 1rem;
    font-weight: 700;
  }
</style>
