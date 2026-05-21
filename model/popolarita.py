from dataclasses import dataclass

from model.artista import Artista


@dataclass
class Popolarita:
    artist: Artista
    pop: int
    ListaClienti:set


    def __hash__(self):
        return hash(self.artist.ArtistId)

    def __eq__(self, other):
        return self.artist.ArtistId == other.artist.ArtistId

    def __str__(self):
        return f"{self.artist.ArtistId}: {self.pop}"
