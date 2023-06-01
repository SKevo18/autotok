#!/usr/bin/env python3
import asyncio
import traceback

from pathlib import Path

from TikTokLive import TikTokLiveClient
from TikTokLive.types.objects import VideoQuality
from TikTokLive.types.errors import LiveNotFound

from autotok import LOGGER, DOWNLOADS_ROOT, now
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
            "title": f"{self.unique_id} ({self.datetime_str.split('_')[0].replace('-', '/')})",
            "description": f'https://tiktok.com/@{self.unique_id}\n\nAutomatický záznam z {self.datetime_str}',
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
        LOGGER.info("Stopping...")
        self.stop()

        if self.upload and self.download_path.exists():
            LOGGER.info(f"`@{self.unique_id}` - Uploading to YouTube...")

            video_id = upload_to_youtube(
                video_path=self.download_path,
                **self.youtube_kwargs
            )

            LOGGER.info(f"`@{self.unique_id}` - Video ID `{video_id}` was uploaded successfuly: https://youtube.com/watch?v={video_id}")


    async def on_connect(self, _) -> None:
        LOGGER.info(f"Connected to room '{self.room_id}' (https://tiktok.com/@{self.unique_id}/live)")

        self.download_path.parent.mkdir(parents=True, exist_ok=True)

        self.download(path=self.download_path, quality=VideoQuality.UHD) # type: ignore


    async def on_error(self, error: Exception) -> None:
        LOGGER.error(error, exc_info=True)


    async def on_disconnect(self, _) -> None:
        LOGGER.warning(f"`@{self.unique_id}` - Disconnected. Saving current video and attempting to reconnect...")
        self.terminate()

        return await self.main()



    async def main(self):
        while not self.connected or not self.connecting:
            try:
                await self.start()

            except LiveNotFound:
                LOGGER.debug(f"User `@{self.unique_id}` seems to be offline, checking again in 1 minute...")

                await asyncio.sleep(60)

            except Exception as e:
                print(traceback.print_exc())
                LOGGER.error(f"`@{self.unique_id}` - Failed to do something: `", e, "`. Retrying after 10 seconds...", exc_info=True)

                await asyncio.sleep(10)

        LOGGER.info(f"`@{self.unique_id}` - Finally, at last, connected!")
