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
              class="q-mb-sm"
              label="Song Name"
              outlined
              dense
              :rules="[val => val && val.length > 0 || 'This field is required']"
            />
            <q-input
              class="q-mb-sm"
              label="YouTube Link"
              outlined
              dense
              :rules="[val => val && val.length > 0 || 'This field is required']"
            />
            <q-btn
              @click="addSongHandler"
              label="Add Song"
              color="secondary"
              class="full-width"
            />

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
  import { ref, computed, onMounted, onUnmounted } from 'vue'
  import { useQuasar } from 'quasar'
  import { fetchSongs } from '@/api/loadOptions.js'
  import { SONG_TITLE_MAPPING } from '@/constants.js'
  import VideoPlayer from '@/components/VideoPlayer.vue'

  const songs = ref([])
  const selectedSong = ref(null)
  const activeSong = ref(null)

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
    // try {
    //   const response = await apiAddSong(
    //     youtubeLink.value,
    //     songName.value
    //   );

    //   if (!response || !response.job_id) {
    //     console.error("Failed to add song:", response);

    //     $q.notify({
    //       type: "negative",
    //       message: "Failed to add song.",
    //       position: "top",
    //     });

    //     return;
    //   }

    //   const jobId = response.job_id;
    //   jobStatus.value = "Starting";

    //   // prevent multiple intervals
    //   if (interval) clearInterval(interval);

    //   interval = setInterval(async () => {
    //     try {
    //       const data = await getJobStatus(jobId);

    //       jobStatus.value = data.status;

    //       if (data.status === "Done" || data.status?.startsWith("Error")) {
    //         clearInterval(interval);
    //         interval = null;
    //       }
    //     } catch (err) {
    //       clearInterval(interval);
    //       interval = null;

    //       jobStatus.value = "Failed to fetch status";

    //       $q.notify({
    //         type: "negative",
    //         message: "Lost connection to job status.",
    //         position: "top",
    //       });
    //     }
    //   }, 500);
    // } catch (err) {
    //   console.error(err);

    //   $q.notify({
    //     type: "negative",
    //     message: "Server error while starting job.",
    //     position: "top",
    //   });
    // }
  };

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
