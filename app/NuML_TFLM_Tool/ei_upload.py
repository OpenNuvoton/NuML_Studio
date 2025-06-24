import os
from pathlib import Path

from datetime import datetime
import edgeimpulse as ei
import warnings

class EiUploadDir():
    def __init__(self):
        # Edit to your Edge Impulse project API key
        self.EI_API_KEY = None
        with open('API_Key.txt', 'r', encoding='utf-8') as file:
            self.EI_API_KEY = file.readline().strip()
        
        if not self.EI_API_KEY:
            raise ValueError("API key is missing or empty in API_Key.txt")
        
    def upload_dir(self, directory, category="training", label=None):
        """
        Uploads all files in the specified directory to Edge Impulse.
        """
        if not os.path.isdir(directory):
            raise ValueError(f"Provided path '{directory}' is not a valid directory.")
        
        ei.API_KEY = self.EI_API_KEY

        try:
            print(f"Uploading directory...: {directory}")
            #with warnings.catch_warnings():
            #    warnings.simplefilter("ignore")
            response = ei.experimental.data.upload_directory(
                directory=directory,
                category=category,
                label=label, # Will use the prefix before the '.' on each filename for the label
                metadata={
                    "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "source": "pc upload",
                }
            )

            # Check to make sure there were no failures
            #assert len(response.fails) == 0, "Could not upload some files"
            if len(response.fails) > 0:
                print("Could not upload some files")
                print(response.fails)
            else:
                print("Upload finished successfully!")
            
            ## Save the sample IDs, as we will need these to retrieve file information and delete samples
            #ids = []
            #for sample in response.successes:
            #    ids.append(sample.sample_id)
            #
            ## Review the sample IDs and get the associated server-side filename
            ## Note the lack of extension! Multiple samples on the server can have the same filename.
            #for idx in ids:
            #    filename = ei.experimental.data.get_filename_by_id(idx)
            #    print(f"Sample ID: {idx}, filename: {filename}")

        except RuntimeError as e:
            # Handle the error gracefully
            print(f"Error in thread: {e}")