# MusicVis: Leveraging Cross-Modal Correspondences for Fine-Grained Visual Representations of Music

## Quick Start
``musicVis.py`` is the main entry module. Using the local sqlite DB, there are sample wav files labeled as s001 to s100. Simply call musicVis(song_title) to render the images corresponding to the music.

### Adding music
In order to add music, the wav file should be stemmed. In ``stem_music.py``, call Demucs (default model: htdemucs_6s) to separate it into 6 stemmed files. Add these files to the SQlite database by calling add_stems_to_db(). Be sure to modify the folder location to match the stemmed file! It should automatically extract the related features necessary for mapping to visuals.

## MusicVis Example Visualizations (seizure warning)
[MusicVis](https://github.com/user-attachments/assets/24622145-2f2c-4083-ab1f-5d44ecb7f686)
