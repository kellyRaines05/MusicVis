"""
Creates database of songs with preprocessed feature extraction. Creates SQLAlchemy classes/tables.

Classes:
    - Base: base class
    - Song: songs table has a title and filepath to refer to. Parent to Stem.
    - Stem: stems table has a type based on the htdemucs_6s stemmer (bass, drum, guitar, piano, other, vocals). Parent to Features, Child to Song.
    - Features: features table has a timestamp associated with the features json which make-up the MusicFeatures

Functions:
    - add_stems_to_db: fills the database given the stemmed files in separated/htdemucs6s/ directory
    - get_song_features: selects the features from a particular song in the order of timestamp with each associated stem within that list
"""

from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy import String, Float
from sqlalchemy import ForeignKey, select
from typing import List
import os

from algorithmic_art_characteristics import *
from music_feature_extraction import *

class Base(DeclarativeBase):
    pass

class Song(Base):
    __tablename__ = 'songs'
    id: Mapped[int] = mapped_column(primary_key=True)
    song_title: Mapped[str] = mapped_column(String(30))
    file_name: Mapped[str] = mapped_column(String(100))
    stems: Mapped[List["Stem"]] = relationship(back_populates="songs", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Song(id={self.id!r}, song_title={self.song_title!r}, file_name={self.file_name!r})"


class Stem(Base):
    __tablename__ = 'stems'
    id: Mapped[int] = mapped_column(primary_key=True)
    stem_type: Mapped[str] = mapped_column(String(10))
    file_name: Mapped[str] = mapped_column(String(100))
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"))
    songs: Mapped["Song"] = relationship(back_populates="stems")
    features: Mapped[List["Features"]] = relationship(back_populates="stems", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Stem(id={self.id!r}, sstem_type={self.stem_type!r}, file_name={self.file_name!r})"

class Features(Base):
    __tablename__ = 'features'
    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[float] = mapped_column(Float)
    features_json: Mapped[JSON] = mapped_column(JSON)
    stem_id: Mapped[int] = mapped_column(ForeignKey("stems.id"))
    stems: Mapped["Stem"] = relationship(back_populates="features")

    def __repr__(self) -> str:
        return f"Feature(id={self.id!r}, timestamp={self.timestamp!r}, features_json={self.features_json!r})"
    
def add_stems_to_db(engine):
    with Session(engine) as session:
        stem_dir = "separated/htdemucs_6s/"
        for directory in os.listdir(stem_dir):
            song_stem_dir = os.path.join(stem_dir, directory)
            song = Song(song_title=directory, file_name=song_stem_dir)
            session.add(song)
            session.commit()
            song_id = song.id
            
            for file_path in os.listdir(song_stem_dir):
                if file_path.endswith(".wav"):
                    stem_path = os.path.join(song_stem_dir, file_path)
                    stem = Stem(song_id=song_id, stem_type=file_path.split('.')[0], file_name=stem_path)
                    session.add(stem)
                    session.commit()
                    stem_id = stem.id
                    
                    features = get_features(stem_path, time_chunk=4)
                    for feature in features:
                        if feature is not None:
                            feature = Features(stem_id=stem_id, timestamp=feature.time, features_json=feature.to_dict())
                            session.add(feature)
                            session.commit()

def update_song_location(file_dir: str, engine):
    with Session(engine) as session:
        for file_name in os.listdir(file_dir):
            if not file_name.endswith(".wav"):
                continue

            song_path = os.path.join(file_dir, file_name)
            title, _ = os.path.splitext(file_name)

            song = session.scalar(
                select(Song).where(Song.song_title == title)
            )

            if song is None:
                continue
            song.file_name = song_path
        session.commit()

def get_song_features(song_title: str, engine) -> list[list[MusicFeatures]]:
    with Session(engine) as session:
        song = session.scalar(
            select(Song).where(Song.song_title == song_title)
        )
        if song is None:
            return []

        features_dict: dict[float, list[MusicFeatures | None]] = {}
        timeline = set()
        for stem_index, stem in enumerate(song.stems):
            rows = session.execute(
                select(Features.timestamp, Features.features_json)
                .where(Features.stem_id == stem.id)
                .order_by(Features.timestamp.asc())
            ).all()

            for ts, feat_json in rows:
                timeline.add(ts)
                if ts not in features_dict:
                    features_dict[ts] = {}
                features_dict[ts][stem_index] = MusicFeatures.from_dict(feat_json)

        sorted_ts = sorted(features_dict.keys())
        result = []

        for ts in sorted_ts:
            inner = features_dict[ts]
            result.append([inner[k] for k in inner])

        return result, sorted(list(timeline))
    
def get_song_file_location(song_title: str, engine) -> str:
    with Session(engine) as session:
        song = session.scalar(
            select(Song).where(Song.song_title == song_title)
        )
        if song is None:
            return None
        else:
            return song.file_name