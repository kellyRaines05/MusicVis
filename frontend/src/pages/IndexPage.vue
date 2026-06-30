<template>
  <q-page class="column items-center justify-start">
    <div class="row items-center justify-center q-pa-md">
      <h2 class="text-primary q-mb-none">MusicVis: Interactive Demo</h2>
    </div>

    <div class="row full-width justify-center q-pa-md q-col-gutter-xl">
      <!-- Existing Song -->
      <div class="col-12 col-md-5">
        <q-card class="q-pa-md full-height">
          <q-card-section>
            <h5 class="text-primary text-center q-mt-none">View a Song</h5>
            <div class="text-center text-subtitle1 q-mb-md">Select a prepared song from the list below to view its visualization.</div>
            <q-select
              v-model="selectedSong"
              :options="songs"
              label="Select a song"
              outlined
              dense
              class="q-mb-lg"
            />
            <q-btn
              @click="viewSong"
              label="View Song"
              color="secondary"
              class="full-width"
            />
          </q-card-section>
        </q-card>
      </div>

      <!-- New Song -->
      <div class="col-12 col-md-5">
        <q-card class="q-pa-md full-height">
          <q-card-section>
            <h5 class="text-primary text-center q-mt-none">Visualize a New Song</h5>
            <q-input
              v-model="songName"
              class="q-mb-sm"
              label="Song Name"
              outlined
              dense
              :rules="[val => val && val.length > 0 || 'This field is required']"
            />
            <q-input
              v-model="youtubeLink"
              class="q-mb-sm"
              label="YouTube Link"
              outlined
              dense
              :rules="[val => val && val.length > 0 || 'This field is required']"
            />
            <p class="q-pl-sm text-grey-9">make sure to copy the link from Youtube from "Share" not the web address</p>
            <q-btn
              @click="addSongHandler"
              :label="isAddingSong ? 'Adding...' : 'Add Song'"
              :disable="isAddingSong"
              color="secondary"
              class="full-width"
            />

            <div v-if="jobId" class="q-mt-md">
              <div class="text-caption text-grey-7">Job ID: {{ jobId }}</div>
              <q-linear-progress :value="jobProgress / 100" rounded color="secondary" class="q-mt-sm" />
              <div class="text-caption q-mt-xs">{{ jobStatus }} ({{ jobProgress }}%)</div>
              <div v-if="jobMessage" class="text-caption text-grey-7 q-mt-xs">{{ jobMessage }}</div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <div class="row full-width items-center justify-center q-gutter-lg">
      <h5 class="text-primary text-center q-mb-md">Song Visualization</h5>
    </div>
   <div class="row full-width items-center justify-center">
      <VideoPlayer :song="activeSong" />
    </div>
  </q-page>
</template>

<script setup>
  import { ref, onMounted, onUnmounted } from 'vue'
  import { useQuasar } from 'quasar'
  import { fetchSongs } from '@/api/loadOptions.js'
  import { addSong, getJobStatus } from '@/api/addSong.js'
  import { SONG_TITLE_MAPPING } from '@/constants.js'
  import VideoPlayer from '@/components/VideoPlayer.vue'

  const songs = ref([])
  const selectedSong = ref(null)
  const activeSong = ref(null)
  const songName = ref('')
  const youtubeLink = ref('')
  const jobId = ref(null)
  const jobStatus = ref('')
  const jobProgress = ref(0)
  const jobMessage = ref('')
  const isAddingSong = ref(false)

  const $q = useQuasar()
  let interval;

  const viewSong = () => {
    if (!selectedSong.value) {
      $q.notify({
        type: 'negative',
        message: 'Please select a song to view.',
        position: 'top',
      })
      return
    }

    activeSong.value = selectedSong.value.value
  }

  const loadSongs = async () => {
    songs.value = await fetchSongs()

    songs.value = songs.value.map((song) => ({
      label: SONG_TITLE_MAPPING[song] || song,
      value: song,
    }))
  }

  const addSongHandler = async () => {
    if (!songName.value.trim() || !youtubeLink.value.trim()) {
      $q.notify({
        type: 'negative',
        message: 'Please enter both a song name and YouTube link.',
        position: 'top',
      })
      return
    }

    isAddingSong.value = true
    jobId.value = null
    jobStatus.value = 'Queued'
    jobProgress.value = 0
    jobMessage.value = 'Starting the upload pipeline'

    try {
      const response = await addSong(youtubeLink.value.trim(), songName.value.trim())

      if (!response || !response.job_id) {
        throw new Error('Missing job id from server response')
      }

      jobId.value = response.job_id
      jobStatus.value = response.status || 'Queued'
      jobProgress.value = response.progress || 0
      jobMessage.value = 'Job created. Waiting for processing to begin.'

      if (interval) clearInterval(interval)

      interval = setInterval(async () => {
        try {
          const data = await getJobStatus(jobId.value)
          jobStatus.value = data.status
          jobProgress.value = data.progress || 0
          jobMessage.value = data.message || ''

          if (data.status === 'Done' || data.status?.startsWith('Error')) {
            clearInterval(interval)
            interval = null
            isAddingSong.value = false

            if (data.status === 'Done') {
              await loadSongs()
              $q.notify({
                type: 'positive',
                message: 'Song added successfully.',
                position: 'top',
              })
            } else {
              $q.notify({
                type: 'negative',
                message: data.message || 'Failed to add song.',
                position: 'top',
              })
            }
          }
        } catch (err) {
          clearInterval(interval)
          interval = null
          isAddingSong.value = false
          jobStatus.value = 'Failed to fetch status'
          jobMessage.value = 'Lost connection to the processing job.'

          $q.notify({
            type: 'negative',
            message: 'Lost connection to job status.',
            position: 'top',
          })
        }
      }, 1000)
    } catch (err) {
      console.error(err)
      isAddingSong.value = false
      jobStatus.value = 'Failed to start upload'
      jobMessage.value = 'The server could not start processing this song.'

      $q.notify({
        type: 'negative',
        message: 'Server error while starting job.',
        position: 'top',
      })
    }
  }

  onMounted(() => {
    loadSongs()
  })

  onUnmounted(() => {
    if (interval) clearInterval(interval);
  })

</script>

<style scoped>
  h2 {
    color: var(--primary);
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 1rem;
  }

  .q-page {
    padding: 1rem;
  }

  .q-card {
    background-color: var(--q-accent);
  }
</style>
