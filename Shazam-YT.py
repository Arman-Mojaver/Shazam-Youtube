import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager
from pytube import YouTube
import moviepy.editor
import json


class Song:
    def __init__(self, index, name, artist, filename=None, url=None):
        self.index = index
        self.name = name
        self.artist = artist

        if filename is None:
            self.filename = self.name + ' - ' + self.artist
        else:
            self.filename = filename

        if url is None:
            self.url = None
        else:
            self.url = url

    # Gets the URL of the 1st video of Youtube when the song is searched.
    def get_url(self):

        try:
            # String to be searched in Youtube
            search_string = self.name + self.artist

            # Saving the search video URL in the variable 'search_video_url'.
            search_video_url = "https://www.youtube.com/results?search_query=" + str(search_string) + ' audio'

            # Navigate to search_video_url with video being appended to search_query
            driver.get(search_video_url)

            # Search the video list and get the url of the first match where the video title contains
            # self.name or self.artist (this is to avoid the advert).
            wait.until(visible((By.ID, "video-title")))
            all_videos = driver.find_elements_by_id("video-title")
            for video in all_videos:
                if self.name in video.text or self.artist in video.text:
                    self.url = video.get_attribute("href")
                    break
        except:
            print('the following song did not provide any search results in youtube: ', self.name + self.artist)
            self.url = None

    def __repr__(self):
        return 'index: {}\t name: {} artist: {}'.format(self.index, self.name.ljust(80), self.artist)

    
# Opening the file in read mode, saving every line, and removing the end of line '\n'
def get_data(file):
    with open(file, 'rt', encoding="utf8") as my_file:
        lines = [line.rstrip('\n') for line in my_file]
    return lines


# Removes the beginning and the end of the file that are not songs.
def remove_garbage_string(lines):
    # Getting the index of where the songs start.
    start = lines.index('1')

    # Removing whatever text is before the songs.
    lines2 = lines[start:]

    # Getting the index of where the songs end.
    # The variable 'end' is initialized to avoid warning from IDE.
    end = None
    for i in range(0, len(lines2), 3):
        if str(int((i / 3) + 1)) == lines2[i]:
            pass
        else:
            end = i
            break

    # Removing whatever text is after the songs.
    lines3 = lines2[0:end]

    return lines3


# Checking whether there are old songs and taking them out of the list of songs to be downloaded.
def get_list_of_songs_to_be_downloaded(old_songs_file, new_songs_ol):
    # Checking if there is an Old_songs.json file, and removing the songs that already have been downloaded.
    try:
        # Loading the songs that has been already downloaded from the last run.
        list_of_songs_from_json = [Song(**d) for d in load_json(old_songs_file)]

        # Getting the last downloaded song from the last run.
        last_song = list_of_songs_from_json[-1]

        # Getting the index of the last song from the last run in the new song list.
        index_last_song_in_new_list = get_index_last_song_in_new_list(new_songs_ol, last_song)

        # Filtering out the songs that already have been downloaded.
        list_of_songs_to_be_downloaded_without_old_songs = [o for o in new_songs_ol
                                                            if int(o.index) < int(index_last_song_in_new_list)]

        # Printing some information.
        print('Old_songs.json file found, removing downloaded songs from new list')
        print('Amount of songs to download: ' + str(len(list_of_songs_to_be_downloaded_without_old_songs))
              + ' songs')
        return list_of_songs_to_be_downloaded_without_old_songs

    except FileNotFoundError:
        # Printing some information.
        print('file not found, downloading the whole list of songs')
        print('Amount of songs to download: ' + str(len(new_songs_ol)) + ' songs')

        # Downloading the whole list of songs, because there is no Old_songs.json file.
        return new_songs_ol


# Getting the index of the last downloaded song from a previous run in the new song list.
def get_index_last_song_in_new_list(object_list, the_last_song):
    index = None
    for song in object_list:
        if the_last_song.filename == song.filename:
            index = int(song.index)
    return index


# Given a URL and a download folder, the function downloads the video to the folder.
def download_youtube_video(obj, dw_folder):
    yt = YouTube(obj.url)
    stream = yt.streams.first()
    stream.download(dw_folder, filename=obj.filename)


# Getting the audio from the video file.
def mp4_to_mp3(video_file, folder):
    clip = moviepy.editor.VideoFileClip(folder+'\\'+video_file)
    clip.audio.write_audiofile(folder+'\\'+video_file.split('.')[0] + '.mp3')
    clip.close()


# Saving an object to a json file
def save_json(obj, json_file):
    with open(json_file, 'w') as fp:
        json.dump(obj, fp, indent=4)


# Loading an object from a json file
def load_json(json_file):
    with open(json_file, 'r') as fp:
        loaded_data = json.load(fp)
    return loaded_data


# ---------------------------------- Getting song information ----------------------------------------


# name and folder of the .txt file that contains the songs copied from Shazam's website.
working_folder = 'C:/Users/arman/PycharmProjects/Pytest'
txt_file = 'Shazam.txt'
old_songs = 'Old_songs.json'
download_folder = 'C:\\Users\\arman\\Downloads\\Musica'

# Changing the working directory
os.chdir(working_folder)

# Saving the complete data from the .txt file in variable 'my_lines'.
my_lines = get_data(txt_file)

# Removing the garbage from the file.
my_lines_without_garbage = remove_garbage_string(my_lines)

# Creating a list of objects of the class 'Song'.
songs_OL = list(reversed([Song(*my_lines_without_garbage[i:i + 3]) for i in
                          range(0, len(my_lines_without_garbage), 3)]))
[print(i) for i in songs_OL]

list_of_songs_to_be_downloaded = get_list_of_songs_to_be_downloaded(old_songs, songs_OL)
[print(i) for i in list_of_songs_to_be_downloaded]


# ---------------------------------- Getting song URL information ------------------------------------


# Initializing Selenium
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.maximize_window()
wait = WebDriverWait(driver, 3)
presence = ec.presence_of_element_located
visible = ec.visibility_of_element_located


# Getting the urls
[o.get_url() for o in list_of_songs_to_be_downloaded]


# Closing the browser
driver.close()


# ------------------------------ Filtering out the objects without URL--------------------------------


list_of_songs_to_be_downloaded_with_url = [o for o in list_of_songs_to_be_downloaded if o.url is not None]
list_of_songs_to_be_downloaded_without_url = [o for o in list_of_songs_to_be_downloaded if o.url is None]

list_of_songs_to_be_downloaded_without_url_dicts = [o.__dict__ for o in list_of_songs_to_be_downloaded_without_url]
save_json(list_of_songs_to_be_downloaded_without_url_dicts, 'no_url_songs.json')


# --------------------------------------- Downloading song -------------------------------------------


for i, o in enumerate(list_of_songs_to_be_downloaded_with_url):
    download_youtube_video(o, download_folder)
    print('Downloaded ' + str(i+1) + ' of ' + str(len(list_of_songs_to_be_downloaded_with_url)) + ' songs.')


# ------------------------------------ Converting mp4 to mp3 -----------------------------------------


os.chdir(download_folder)

video_files_list = os.listdir()
[print(v) for v in video_files_list]

[mp4_to_mp3(video, download_folder) for video in video_files_list]


# ------------------------------------ Removing .mp4 files--- -----------------------------------------


video_files = [file for file in os.listdir() if file.split('.')[1] == 'mp4']
[os.remove(video) for video in video_files]


# ------------------------------------ Updating the json file -----------------------------------------


# saving the new downloaded songs into the json file
songs_OL_dicts = [o.__dict__ for o in songs_OL]
save_json(songs_OL_dicts, 'Old_songs.json')
