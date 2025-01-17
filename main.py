import os
import sys
import threading
# Add the src dir to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from src.page_scanner import BookPageScanner
import mac_vision_extractor as mac_vision_extractor
from utils.spinner_task import spinner_task
from utils.get_user_input import get_user_input

done = False

def is_done():
    return done

def main(video_path_input):
    global done
    page_scanner = BookPageScanner(video_path_input)
    output_frames_dir = 'output_frames'

    # ----------- Output Frames
    if not os.path.exists(output_frames_dir):
        os.makedirs(output_frames_dir)
    else:
        existing_files = os.listdir(output_frames_dir)
        if existing_files:
            user_response = get_user_input("There are already existing files in the output frames directory. Do you want to delete them and continue? (Y/N): ", 60)
            if user_response == 'y':
                for file in existing_files:
                    file_path = os.path.join(output_frames_dir, file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"Failed to delete {file_path}. Error: {e}")
            else:
                print("Operation aborted.")
                proceed_with_text_extraction = get_user_input("Would you like to proceed with text extraction on the existing frames? (Y/N): ", 60)
                if proceed_with_text_extraction.lower() == 'y':
                    print("Proceeding with text extraction...")
                else:
                    print("Exiting program.")
                    return
        else:
            print('No existing files...')
        
# ----------- Perform actual video processing and frame simulation -----------
    done = False
    spinner_thread = threading.Thread(target=spinner_task, args=('lines', is_done))
    spinner_thread.start()

    try:
        page_scanner.process_video(output_frames_dir)
    except Exception as e:
        print(f'Error scanning video file: {e}')
    finally:
        done = True
        spinner_thread.join()
# ------------------------------------------------------------------------

    # ----------- Output Text
    output_text_dir = 'output_text'
    if not os.path.exists(output_text_dir):
        os.makedirs(output_text_dir)
    else:
        existing_files = os.listdir(output_text_dir)
        if existing_files:
            response = input("There are already existing files in the output text directory. Do you want to delete them and continue? (Y/N): ").strip().lower()
            if response == 'y':
                for file in existing_files:
                    file_path = os.path.join(output_text_dir, file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"Failed to delete {file_path}. Error: {e}")
            else:
                print("Operation aborted.")
                return
        else:
            print('No existing files found in output text, continuing...')

# ----------- Perform actual text extraction from image frames -----------
    done = False
    spinner_thread_dots = threading.Thread(target=spinner_task, args=('dots', is_done))
    spinner_thread_dots.start()
    
    try:
        mac_vision_extractor.text_extractor()
    except Exception as e:
        print(f'Error extracting text from frames: {e}')
    finally:
        done = True
        spinner_thread_dots.join()
# ------------------------------------------------------------------------


# MAIN
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_videos_dir = os.path.join(script_dir, "input_videos")

    if not os.path.exists(input_videos_dir):
        os.makedirs(input_videos_dir)
        print(f"Directory 'input_videos' created at: {input_videos_dir}")
        print(f"Please add video files to the directory and run the program again.")
        sys.exit(1)
    else:
        print(f"Directory 'input_videos' already exists at: {input_videos_dir}")
        print(f"Continuing with video processing...")

        input_videos_dir = "input_videos"
        video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"}

        video_files = [
            f for f in os.listdir(input_videos_dir)
            if os.path.isfile(os.path.join(input_videos_dir, f)) and os.path.splitext(f)[1].lower() in video_extensions
        ]

        if not video_files:
            print(f"No video files found in '{input_videos_dir}'. Exiting program.")
            sys.exit(1)

        for video_file in video_files:
            video_path = os.path.join(input_videos_dir, video_file)
            print(f"Processing video: {video_path}")
            main(video_path)
