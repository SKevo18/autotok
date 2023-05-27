#!/usr/bin/env python3
import asyncio
import traceback

from pathlib import Path
from warnings import warn

from TikTokLive import TikTokLiveClient
from TikTokLive.types.objects import VideoQuality
from TikTokLive.types.errors import LiveNotFound, AlreadyConnecting

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

        if self.upload and self.download_path.exists():
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
        print("Disconnected. Saving current video and attempting to reconnect...")
        self.terminate()

        return await self.main()



    async def main(self):
        while not self.connected or not self.connecting:
            try:
                await self.start()

            except LiveNotFound:
                print(f"User `@{self.unique_id}` seems to be offline, checking again in 1 minute...")

                await asyncio.sleep(60)

            except AlreadyConnecting as e:
                print("shitte, we wait:", e)

                self.stop()
                await asyncio.sleep(10)

            except Exception as e:
                print(traceback.print_exc())
                print(f"Failed to do something: {e}, retrying after 10 seconds...")

                await asyncio.sleep(10)

        print("Finally, at last, connected!")
