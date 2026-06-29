import { API_BASE_URL } from '../constants.js';

export async function fetchSongs() {
  const response = await fetch(`${API_BASE_URL}/songs`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}
