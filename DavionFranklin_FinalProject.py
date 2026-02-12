# Davion Franklin

# Python Music Player
"""This program serves as a music library application where users can organize and listen to music. Users have the
options to either add albums that contain songs, or singles. Users can add/delete songs to albums, or add/delete albums
and singles to the library."""

"""~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Instructions~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:
Ensure that pygame is installed on your IDE.
Choose an action first, THEN the menu will prompt you to choose a song, single, or album.
Song features are within the albums menu.
I have provided royalty free songs 4 under a single album for example use. As well as a single that will be attached.
Ensure they share a folder with the script."""

# Note: I realized as I was working that alot of things in my PseudoCode could be simplified.
# I also added/removed some planned features for simplicity purposes.
# Enjoy!

import pygame # Used for playing audio files.
import json # Used to load database.

pygame.mixer.init() # Initializes pygame.

# Parent class of all objects music related.
class MusicItem:
    def __init__(self, name, artist, release_date, is_playing = False):
        self.name = name
        self.artist = artist
        self.release_date = release_date
        self.is_playing = is_playing

    # Formats as string.
    def __str__(self):
        formatted_line = f'{self.name}: {self.artist} ({self.release_date})'
        return formatted_line

    # Retrieves data from .json file.
    @classmethod
    def from_json(cls, data):
        return cls(
            name = data.get('name'),
            artist = data.get('artist'),
            release_date = data.get('release_date')
        )

    # Writes data to .json file.
    def to_json(self):
        return{
            'name': self.name,
            'artist': self.artist,
            'release_date': self.release_date,
            'music_item_type': self.__class__.__name__
        }

# Stored as a dictionary inside an album.
class Song(MusicItem):
    def __init__(self, name, artist, release_date, album, file_name, is_playing = False):
        super().__init__(name, artist, release_date, is_playing = False)
        self.album = album
        self.file_name = file_name

    # Retrieves song data from .json file.
    @classmethod
    def from_json(cls, data):
        return cls(
            name = data.get('name'),
            artist = data.get('artist'),
            release_date = data.get('release_date'),
            album = data.get('album'),
            file_name = data.get('file_name')
        )

    # Writes song data to .json file.
    def to_json(self):
        data = super().to_json()
        data.update({
            'album': self.album,
            'file_name': self.file_name
        })
        return data

# Stored within the music library.
class Single(Song):
    def __init__(self, name, artist, release_date, file_name):
        super().__init__(name, artist, release_date, album = 'Single', file_name = file_name)

# Stored within music library, contains songs.
class Album(MusicItem):
    def __init__(self, name, artist, release_date, is_playing = False):
        super().__init__(name, artist, release_date, is_playing = False)
        self.songs = {}

    def __str__(self):
        formatted_line = f'{self.name}: {self.artist} ({self.release_date})'
        return formatted_line


    # Retrieves and stores album data from .json file.
    @classmethod
    def from_json(cls, data):
        songs = {}
        for index, song_data in data.get('songs', {}).items():
            music_type = song_data.get('music_item_type','Song')
            if music_type == 'Single':
                songs[int(index)] = Single.from_json(song_data)
            else:
                songs[int(index)] = Song.from_json(song_data)

        album = cls(
            name = data.get('name'),
            artist = data.get('artist'),
            release_date = data.get('release_date')
        )

        album.songs = songs
        return album

    # Writes album data to .json file.
    def to_json(self):
        data = super().to_json()
        data.update({
            'songs': {index: song.to_json() for index, song in self.songs.items()}
        })
        return data

# Holds and manipulates all music items.
class Library:
    def __init__(self):
        self.albums = {}
        self.singles = {}
        self.current_album = None
        self.current_song_index = None
        self.current_song_keys = []

    # Chooses a dictionary based on music item type.
    def map_music_item(self, music_item_type, album_index):
        if music_item_type == 'song':
            if album_index is None or album_index not in self.albums:
                raise ValueError('Invalid album index.')
            return self.albums[album_index].songs
        mapped = {
                'album': self.albums,
                'singles': self.singles
        }

        return mapped.get(music_item_type, self.singles) # Returns corresponding dictionary.

    # Updates dictionary with new index for elements, used to update indexes when a song is removed from an album.
    def reindex(self, music_item_type, album_index = None):
        music_dict = self.map_music_item(music_item_type, album_index)
        new_dict = {index + 1: music_item for index, music_item in enumerate(music_dict.values())}
        if music_item_type == 'song':
            self.albums[album_index].songs = new_dict
        elif music_item_type == 'album':
            self.albums = new_dict
        else:
            self.singles = new_dict

    # Adds music item to relevant dictionary.
    def add_music_item(self,music_item_type, music_item, album_index):

        music_dict = self.map_music_item(music_item_type, album_index)

        if music_item in music_dict.values():
            return None

        integer_key = max(music_dict.keys(), default=0) + 1 # Takes max integer key in dict and adds 1 for the new addition.
        music_dict[integer_key] = music_item

    # Deletes music item from relevant dictionary.
    def delete_music_item(self, music_item_type, index, album_index):
        music_dict = self.map_music_item(music_item_type, album_index)

        if index in music_dict:
            del music_dict[index]
            self.reindex(music_item_type, album_index)

    # Displays corresponding music item.
    def view_music_item(self, music_item_type, album_index):
        music_dict = self.map_music_item(music_item_type, album_index)

        for integer, music_item in music_dict.items():
            print(f'{integer}: {music_item}')

    # Plays songs.
    @staticmethod
    def play_song(song):
        if not song.file_name: # If song was not given a path.
            print('\nRequested song could not be found in folder.')
            return

        # Stops playback if desired song is currently playing.
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        # Plays song.
        try:
            pygame.mixer.music.load(song.file_name) # Loads file.
            pygame.mixer.music.play() # Plays file.
            song.is_playing = False # Sets condition of music item to state that it is currently playing.
            print(f'\nNow playing {song.name} by {song.artist}...')
        except pygame.error as error:
            print(f'\nError playing {song.file_name}: {error}')

    # Stops music.
    def stop_music(self):
        if pygame.mixer.music.get_busy(): # Checks if pygame is working.
            pygame.mixer.music.stop() # Stops music.
            print('\nMusic stopped...')

        for album in self.albums.values(): # Updates all albums, is playing value to False.
            album.is_playing = False

            for song in album.songs.values(): # Updates all songs, is playing value to False.
                song.is_playing = False

        for single in self.singles.values(): # Updates all singles, is playing value to False.
            single.is_playing = False
        self.current_album = None
        self.current_song_index = None
        self.current_song_keys = [] # List that gathers active song's key and updates it when finished playing for sequencing albums.

    # Iterates through each song in an album and plays it.
    def play_album(self, album_index):
        if album_index not in self.albums: # If the input index is invalid.
            print(f'\nAlbum with index {album_index} is invalid.')
            return

        # Prints error if the album is empty.
        album = self.albums[album_index]
        if not album.songs:
            print(f'\nThe album {album} is currently empty.')
            return

        self.stop_music()

        self.current_album = album
        self.current_song_keys = sorted(album.songs.keys())
        self.current_song_index = 0
        self.play_current_song()

    # Plays song that is currently active in an album.
    def play_current_song(self):
        if self.current_album is None or self.current_song_index is None:
            return

        song_key = self.current_song_keys[self.current_song_index]
        song = self.current_album.songs[song_key]

        if not song.file_name:
            print(f'\nSong {song.name} is missing a file, skipping.') # If song has no path.
            return


        # Plays songs in album.
        try:
            pygame.mixer.music.load(song.file_name)
            pygame.mixer.music.play()
            song.is_playing = True
            print()
            print(f'\tNow playing {song.name} by {song.artist}...')

        # Handles errors.
        except pygame.error as error:
            print(f'\nError playing {song.file_name}: {error}')

    # Skips current song in album.
    def next_song(self):
        if self.current_album is None:
            return

        index = self.current_song_keys[self.current_song_index]
        self.current_album.songs[index].is_playing = False

        # Selects next song in album to be played.
        self.current_song_index += 1
        if self.current_song_index >= len(self.current_song_keys):

            print(f'\nAlbum {self.current_album.namme} has finished playing.')
            self.stop_music()
        else:
            self.play_current_song()

music_library = Library() # Creates library for program use.

# Loads data from .json file.
def load_data():
    try:
        with open('music_database.json', 'r') as reader:
            data = json.load(reader)

            # Gathers data and creates albums from .json file.
            for album_index, album_data in data.get('albums', {}).items():
                album = Album(
                    album_data['name'],
                    album_data['artist'],
                    album_data['release_date'],
                    is_playing=False
                )
                music_library.add_music_item('album', album, None)

                album_index = max(music_library.albums.keys()) # Indexes albums.

                # Gathers data and creates songs from .json file.
                for song_index, song_data in album_data.get('songs', {}).items():
                    song = Song(
                        song_data['name'],
                        song_data['artist'],
                        song_data['release_date'],
                        album.name,
                        song_data['file_name'],
                    )
                    music_library.add_music_item('song', song, album_index)

            # Gathers data and creates singles from .json file.
            for single_index, single_data in data.get('singles', {}).items():
                single = Single(
                    single_data['name'],
                    single_data['artist'],
                    single_data['release_date'],
                    single_data['file_name']
                )
                music_library.add_music_item('single', single, None)

    # Displays error if the file could not be located.
    except FileNotFoundError:
        print('\nUnable to find music database, please ensure it is in the same folder as your script.')

# Saves data from program and writes it to .json file.
def save_data():
    data = {
        'albums':{index: album.to_json() for index, album in music_library.albums.items()},
        'singles': {index: single.to_json() for index, single in music_library.singles.items()}
    }

    try:
        with open('music_database.json', 'w') as writer:
            json.dump(data, writer, indent = 4)
        print('\nLibrary saved.')
    except Exception as error:
        print(f'\nError saving library: {error}')

# Validates that index is a proper positive integer.
def validate_index(music_item_type, music_item_dict):
    while True:
        index = input(f'\nChoose {music_item_type} (enter index): ')
        if music_item_dict: # If dict is not empty.
            try:
                index = abs(int(index))
                if index in music_item_dict:
                    return index
                else:
                    print(f'\nInvalid input "{index}", please enter a valid {music_item_type} index.')
            except ValueError:
                print(f'\nInvalid input "{index}", please enter a valid {music_item_type} index.')
        else:
            print(f'\nYou currently have no {music_item_type}s. In this location.') # Empty dict error.
            return None

# Collects inputs for adding music item.
def collect_song_inputs(music_item_type, album_index):
    name = input('\nEnter name: ')
    artist = input('Enter artist: ')
    release_date = input('Enter release date (MM-DD-YYYY):  ')

    # Depending on music item type, collects exclusive inputs.
    if music_item_type == 'song':
        file_name = input('Enter file (name.ext) name ensure it is in the same folder as the script. or leave blank if N/A :')
        album = music_library.albums[album_index]
        new_song = Song(name, artist, release_date, album, file_name, is_playing = False)
        music_library.add_music_item('song', new_song, album_index) # Adds created song.
    elif music_item_type == 'single':
        file_name = input('Enter file (name.ext) name ensure it is in the same folder as the script. or leave blank if N/A :')
        new_single = Single(name, artist, release_date, file_name)
        music_library.add_music_item('single', new_single, None) # Adds created single.
    else:
        new_album = Album(name, artist, release_date, is_playing=False, )
        music_library.add_music_item('album',new_album, album_index = None) # Adds created album.

# Menu containing options relating to music item type.
def main_menu():
    print('\nWelcome to Python Music Player!')

    while True:
        choice = input('\nA. Albums'
                       '\nB. Singles'
                       '\nC. Exit'
                       '\nEnter your choice: ').upper()

        match choice:
            case 'A':
                albums_menu() # Opens albums submenu.
            case 'B':
                singles_menu() # Opens singles submenu.
            case 'C':
                # Goodbye message, and closes program.
                print('\nSee you next time!')
                break
            case _:
                print(f'\nInvalid input "{choice}", please try again.') # For invalid choice.

# Submenu that handles album functions and methods.
def albums_menu():
    while True:
        choice = input('\nA. Add Album'
                       '\nB. Delete Album'
                       '\nC. View Song Options'
                       '\nD. Play Album'
                       '\nE. Stop Album'
                       '\nF. Skip Song'
                       '\nG. Back'
                       '\nEnter your choice: ').upper()

        # Displays albums with their index.
        print('\nAlbums:')
        for index, album in music_library.albums.items():
            print(f'\t{index}: {album}')

        match choice:
            case 'A':
                collect_song_inputs('album', None) # Adds album.
                save_data()
            case 'B':
                album_index = validate_index('album',music_library.albums)
                if album_index is not None:
                    music_library.delete_music_item('album', album_index, None) # Deletes album.
                    save_data()
            case 'C':
                album_index = validate_index('album', music_library.albums)
                if album_index is not None:
                    songs_menu(album_index) # Displays album.

            case 'D':
                album_index = validate_index('album', music_library.albums)
                music_library.play_album(album_index) # Plays album.

            case 'E':
                music_library.stop_music() # Stops album.

            case 'F':
                music_library.next_song() # Skips song.
            case 'G':
                music_library.stop_music() # Stops music and goes back to previous menu.
                break
            case _:
                print(f'\nInvalid input "{choice}", please try again.') # For invalid inputs.


# Submenu that handles song functions and methods.
def songs_menu(album_index):
    album = music_library.albums[album_index]
    current_song = None

    while True:

        choice = input('\nA. Add Song'
                       '\nB. Delete Song'
                       '\nC. Play Song'
                       '\nD. Stop Song'
                       '\nE. Back'
                       '\nEnter your choice: ').upper()

        print(f'\n{album}')
        if album.songs:
            for index, song in album.songs.items():
                print(f'\t\t{index}: {song}')
        else:
            print(f'\nThe album {album} is currently empty.') # If album is empty.


        match choice:
            case 'A':
                collect_song_inputs('song', album_index) # Collects inputs and adds song to album.
                save_data()

            case 'B':
                if music_library.albums[album_index].songs:
                    song_index = validate_index('song', music_library.albums[album_index].songs)
                    music_library.delete_music_item('song', song_index, album_index) # Deletes song.
                    save_data()
                else:
                    print('\nThere are no songs available, please add some or choose another option.')

            case 'C':
                song_index = validate_index('song', music_library.albums[album_index].songs)
                current_song = music_library.albums[album_index].songs[song_index]
                music_library.play_song(current_song)

            case 'D':
                if current_song and pygame.mixer.music.get_busy():
                    music_library.stop_music() # Stops song.
                    print(f'\n{current_song.name} by {current_song.artist} stopped...')
                else:
                    print('\nNo song is currently playing.')

            case 'E':
                music_library.stop_music() # Stops song and goes back to main menu.
                break

            case _:
                print(f'\nInvalid input "{choice}", please try again.') # For invalid input.

# Submenu that handles functions and methods for singles.
def singles_menu():
    current_single = None

    if not music_library.singles: # If there are no singles.
        print('\nThere are no singles in your library.')
    while True:
        choice = input('\nA. Add Single'
                       '\nB. Delete Single'
                       '\nC. Play Single'
                       '\nD. Stop Single'
                       '\nE. Back'
                       '\nEnter your choice: ').upper()

        for index, singles in music_library.singles.items():
            print(f'{index}: {singles}')

        match choice:
            case 'A':
                collect_song_inputs('single', None) # Collects inputs and adds single to library.
                save_data()

            case 'B':
                if music_library.singles:
                    single_index = validate_index('single', music_library.singles)
                    music_library.delete_music_item('single', single_index, None) # Deletes single.
                    save_data()
                else:
                    print('\nThere are no singles available, please add some or choose another option.')

            case 'C':
                single_index = validate_index('single', music_library.singles)
                current_single = music_library.singles[single_index]
                music_library.play_song(current_single) # Plays single.

            case 'D':
                if current_single and pygame.mixer.music.get_busy():
                    music_library.stop_music() # Stops single.
                    print(f'\n{current_single.name} by {current_single.artist} stopped...')
                else:
                    print('\nNo song is currently playing.')
            case 'E':
                music_library.stop_music() # Stops single and returns to main menu.
                break

            case _:
                print(f'\nInvalid input "{choice}", please try again.')

load_data()
main_menu()
