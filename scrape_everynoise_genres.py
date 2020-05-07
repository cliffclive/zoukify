import azureml.core
from azureml.core import Run, Workspace, Dataset

from src.everynoise_scraper import scrape_everynoise_genre_playlists

# Get the experiment run context
run = Run.get_context()

# Load the workspace from the saved config file
ws = run.experiment.workspace
# Get the default datastore
default_ds = ws.get_default_datastore()

# Scrape all genre playlists from Every Noise At Once
scrape_everynoise_genre_playlists(filepath='everynoise_genre_playlists.json')

# Upload data to Datastore
list_of_files = ['everynoise_genre_playlists.json']
datastore_folder = 'everynoise_data/'

default_ds.upload_files(files=list_of_files, # Upload the diabetes csv files in /data
                        target_path=datastore_folder, # Put it in a folder path in the datastore
                        overwrite=True, # Replace existing files of the same name
                        show_progress=True)

# Create a File Dataset from the path on the datastore (this may take a short while)
file_data_set = Dataset.File.from_files(path=(default_ds, 'everynoise_data/*.json'))

# Register the file dataset
try:
    file_data_set = file_data_set.register(workspace=ws,
                                           name='everynoise file dataset',
                                           description='everynoise genre playlists',
                                           tags = {'format':'JSON'},
                                           create_new_version=True)
except Exception as ex:
    print(ex)

print('EveryNoise Dataset registered')
