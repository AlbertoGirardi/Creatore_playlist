import os
import time
from pydub import AudioSegment
from datetime import timedelta

volume_change = -15
bitrate = 128

def normalize_audio(audio_segment):
    # Normalize audio volume to -20 dBFS
    normalized_audio = audio_segment.normalize(headroom=0.1)
    return normalized_audio

def convert_to_mp3(audio_segment):
    # Convert audio segment to mp3 format
    mp3_audio = audio_segment.export(format="mp3")
    return AudioSegment.from_mp3(mp3_audio)

def generate_output_filename(output_folder, output_file):
    # Check if the output filename already exists in the output directory
    filename, ext = os.path.splitext(output_file)
    base_filename = os.path.basename(filename)
    index = 1
    while True:
        new_filename = f"{base_filename}_{index}{ext}"
        if not os.path.exists(os.path.join(output_folder, new_filename)):
            return new_filename
        index += 1

def create_log_file(output_folder, output_file, filenames,timestamps, total_length, T0, folders):
    # Generate log file path
    log_filename = os.path.splitext(output_file)[0] + ".txt"
    log_file_path = os.path.join(output_folder, log_filename)

    # Write filenames and additional information to the log file
    with open(log_file_path, 'w') as log_file:
        log_file.write("Files added to the final track:\n")
        last_section_length = 0
        last_section_lengthp = 0
        log_file.write(f"origin folder:")
        n = 0
        timestamps.insert(0, 0)
        for filename in filenames:
            try:
                for folder, num in folders:
                    if num == n:
                        log_file.write(f"\nSection total time: {str(timedelta(seconds=(last_section_lengthp-last_section_length)))} \n\n\n\n{os.path.basename(folder.upper())}:\n\n")
                        last_section_length = last_section_lengthp
                log_file.write(f"{n+1} -\t {str(timedelta(seconds=round(timestamps[n])))}\t|  {filename}\n")
                last_section_lengthp = round(timestamps[n])
                n+=1
            except UnicodeEncodeError:
                log_file.write("file name could not be written\n")

        log_file.write(f"\nSection total time: {str(timedelta(seconds=(last_section_lengthp-last_section_length)))}")
        log_file.write(f"\n\n------------------------------------------------------------------\n")
        log_file.write(f"\n\n\nTotal Length of the Track: {str(timedelta(seconds=round(total_length)))}\n")
        log_file.write(f"Number of tracks: {len(timestamps)-1}\n\n")
        log_file.write(f"Total Size of Track: {round(os.path.getsize(os.path.join(output_folder, output_file)) / (1024 * 1024), 2)} MB\n")
        log_file.write(f"Avarage track lenght: {str(timedelta(seconds=round(total_length/(len(timestamps)))))}\n")
        log_file.write(f"\nVolume Change: {volume_change}\n")
        log_file.write(f"Bitrate: {bitrate} kbps\n\n")
        log_file.write(f"Date of Generation: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Time taken for mixing: {round(time.time()-T0,2)} seconds\n")


    #logging to the list of all tracks made
        
    with open(os.path.join(output_folder, 'MASTER_OUTPUT_LOG.txt'), 'a' ) as logg_file:
        logg_file.write(f"{output_file}\t{time.strftime('%Y-%m-%d %H:%M')}\t{str(timedelta(seconds=round(total_length)))}\t\t{len(timestamps)-1} tracks\n")

def stitch_audio_in_folders(root_folder, output_folder, output_file):
    t0 = time.time()
    # Initialize an empty list to store audio segments


    final_audio = AudioSegment.empty()
    # Initialize an empty list to store filenames for logging
    filenames = []
    folders = []        #list of folders and the track they start at

    # Initialize variable to store total length of track
    total_length = 0
    n_file = 0
    timestamps_l = []
    # Iterate through all subfolders in the root folder
    for foldername, _, filenames_list in os.walk(root_folder):
        # Exclude the output folder from the stitching process
        if foldername == output_folder:
            continue
        
        concatenated_audio = AudioSegment.empty()
        folders.append([foldername, n_file])
        # Initialize an empty list to store audio files in the same folder
        folder_audio = []

        # Iterate through all files in the folder
        for filename in filenames_list:
            print(f"adding: '{filename}' ")
            n_file += 1
            if filename.endswith('.mp3'):
                # Load and normalize .mp3 files
                audio_path = os.path.join(foldername, filename)
                audio_segment = AudioSegment.from_mp3(audio_path)
                normalized_audio = normalize_audio(audio_segment)
                # folder_audio.append(normalized_audio)
                filenames.append(filename)
                total_length += audio_segment.duration_seconds
                concatenated_audio += normalized_audio
            elif filename.endswith('.m4a'):
                # Load .m4a files, convert to .mp3, and normalize
                audio_path = os.path.join(foldername, filename)
                audio_segment = AudioSegment.from_file(audio_path, format="m4a")
                mp3_audio = convert_to_mp3(audio_segment)
                normalized_audio = normalize_audio(mp3_audio)
            #    // folder_audio.append(normalized_audio)
                filenames.append(filename)
                total_length += audio_segment.duration_seconds
                concatenated_audio += normalized_audio


            timestamps_l.append(total_length)
            # print(total_length)

        # Concatenate all audio files in the same folder
        
            # concatenated_audio = sum(folder_audio)

            # Append the concatenated audio to the audio_segments list
        final_audio += concatenated_audio
    del folder_audio
    print("\n\nJOINING FILES...")
    # Concatenate all audio segments from different folders
    

    # Lower the volume of the final audio track (if needed)
    final_audio = final_audio + volume_change  # Adjust the volume level as needed

    # Generate a unique output filename
    unique_output_file = generate_output_filename(output_folder, output_file)
    print("\n\nEXPORTING...")

    # Export the final audio to the unique output filename in the output folder
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, unique_output_file)
    final_audio.export(output_path, format="mp3", bitrate=f'{bitrate}k')  # Adjust bitrate as needed
    print('logging')
    # Create a log file with the filenames of the files added to the final track
    folders.pop(0)
    create_log_file(output_folder, unique_output_file, filenames, timestamps_l,total_length, t0, folders)
    # print(timestamps_l)
    # print(filenames)
    print(f"\n\nTime:{round(time.time()-t0,2)}\n")

# Example usage
root_folder = "C:\\Users\\alber\\Music\\MEGAMIX"
output_folder = root_folder + "\\#OUTPUT"
output_file = "MegaMIX_Alberto_Girardi.mp3"
stitch_audio_in_folders(root_folder, output_folder, output_file)
print("FINISHED!!!")
    