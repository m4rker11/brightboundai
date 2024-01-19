import time
import subprocess
import psutil  # Import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class OnMyWatch:
    # Set the directory on watch
    watchDirectory = "."

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive=True)
        self.observer.start()
        # Automatically start Streamlit when the script starts
        Handler.start_streamlit()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()

class Handler(FileSystemEventHandler):

    @staticmethod
    def kill_streamlit():
        """Kill all processes containing 'streamlit' in their command line."""
        for proc in psutil.process_iter(['name', 'cmdline']):
            # Ensure cmdline is a list and not None
            if proc.info['cmdline'] and 'streamlit' in ' '.join(proc.info['cmdline']):
                try:
                    proc.kill()
                    print(f"Killed process {proc.pid} running Streamlit")
                except psutil.NoSuchProcess:
                    pass
                except psutil.AccessDenied:
                    print(f"Access denied when trying to kill process {proc.pid}. You might need administrative privileges.")

    @staticmethod
    def start_streamlit():
        # Kill any previous instance of Streamlit
        Handler.kill_streamlit()
        # Run the command in the background
        print("Starting Streamlit app...")
        subprocess.Popen(["streamlit", "run", "GUI.py"])

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'modified' or event.event_type == 'created' or event.event_type == 'deleted':
            # Event is modified, you can process it now
            print(f"Watchdog received modified event - {event.src_path}.")
            # Restart Streamlit when a file change is detected
            Handler.start_streamlit()

if __name__ == '__main__':
    watch = OnMyWatch()
    watch.run()
