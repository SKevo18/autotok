#!/usr/bin/env python3
from time import sleep
from pathlib import Path
from warnings import warn

from TikTokLive import TikTokLiveClient
from TikTokLive.types.errors import LiveNotFound
from TikTokLive.types.objects import VideoQuality

from autotok import DOWNLOADS_ROOT, now
from autotok.uploader import upload_to_youtube



class AutoTokClient(TikTokLiveClient):
    def __init__(self, unique_id: str, upload: bool=True, *args, **kwargs) -> None:
        super().__init__(unique_id=unique_id, *args, **kwargs)

        self.add_listener("connect", self.on_connect)
        self.add_listener("disconnect", self.on_disconnect)
        self.add_listener("error", self.on_error)

        self.datetime_str = now()
        self.update_filename()

        self.upload = upload
        self.youtube_kwargs = {
            "title": f"{self.unique_id} - auto-playback {self.datetime_str.split('_')[0].replace('-', '/')}",
            "description": f'https://tiktok.com/@{self.unique_id}',
            "category_id": 24,
            "tags": [self.unique_id, 'auto'],
        }



    @property
    def download_path(self) -> Path:
        return DOWNLOADS_ROOT / self.unique_id / self.filename


    def update_filename(self) -> str:
        self.filename = f"{self.datetime_str}_UTC.avi"

        return self.filename


    def terminate(self) -> None:
        print("Stopping...")

        try:
            self.stop_download()
        except Exception as e:
            warn(f"Error during `stop_download`: {e}")

        self.stop()

        if self.upload:
            print("Uploading to YouTube...")

            video_id = upload_to_youtube(
                video_path=self.download_path,
                **self.youtube_kwargs
            )

            print(f"Video ID `{video_id}` was uploaded successfuly: https://youtube.com/watch?v={video_id}")


    async def on_connect(self, _) -> None:
        print(f"Connected to room '{self.room_id}' (https://tiktok.com/@{self.unique_id}/live)")

        self.download_path.parent.mkdir(parents=True, exist_ok=True)

        self.download(path=self.download_path, quality=VideoQuality.UHD) # type: ignore


    async def on_error(self, error: Exception) -> None:
        warn(str(error))


    async def on_disconnect(self, _) -> None:
        print("Disconnected. Saving & uploading current video and attempting to reconnect...")
        self.terminate()

        return await self.start()



    def main(self):
        while not self.connected:
            try:
                self.run()

            except LiveNotFound:
                print(f"User `@{self.unique_id}` seems to be offline, retrying after 1 minute...")

                sleep(60)
            
            except KeyboardInterrupt:
                print("`CTRL + C`, quitting...")
                self.terminate()

                print("Exitted successfuly!")
                break
