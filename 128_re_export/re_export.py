import os
import subprocess

def get_bitrate(file_path):
    """Retrieve the bitrate of an MP3 file using ffmpeg."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 
             'stream=bit_rate', '-of', 'csv=p=0', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        bitrate = result.stdout.strip()
        return int(bitrate) // 1000  # Convert to kbps
    except Exception as e:
        print(f"Error getting bitrate for {file_path}: {e}")
        return None
    



def re_export_audio(input_folder):
    """Re-export MP3 files in the folder to 128 kbps if their bitrate is not 128."""
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.mp3'):
                file_path = os.path.join(root, file)
                bitrate = get_bitrate(file_path)
                print(f'File {file_path} has bitrate {bitrate} kbps')

                if bitrate and bitrate != 128:
                
                    output_file = os.path.join(root, f"{os.path.splitext(file)[0]}_128kbps.mp3")
                    try:
                        print(f"Re-exporting {file} to 128 kbps...")
                        subprocess.run(
                            ['ffmpeg', '-i', file_path, '-b:a', '128k', '-y', output_file],
                            check=True
                        )
                        print(f"Re-exported {file} to {output_file}")
                    except subprocess.CalledProcessError as e:
                        print(f"Error processing {file_path}: {e}")


if __name__ == "__main__":
    input_folder = input("Enter the folder path containing MP3 files: ").strip()
    if os.path.isdir(input_folder):
        re_export_audio(input_folder)
    else:
        print("Invalid folder path!")
