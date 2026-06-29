import { API_BASE_URL } from '../constants.js';


export async function addSong(songLink, songTitle) {
  const response = await fetch(`${API_BASE_URL}/songs/add_song`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      song_link: songLink,
      song_title: songTitle,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

export async function getJobStatus(jobId) {
  const response = await fetch(`${API_BASE_URL}/songs/status/${jobId}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}
