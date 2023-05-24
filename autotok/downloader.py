#!/usr/bin/env python3
from time import sleep
from pathlib import Path
from warnings import warn

from TikTokLive import TikTokLiveClient
from TikTokLive.types.errors import LiveNotFound

from autotok import DOWNLOADS_ROOT, now
from autotok.uploader import upload_to_youtube



class TikTokDownloadClient(TikTokLiveClient):
    def __init__(self, unique_id: str, *args, **kwargs) -> None:
        super().__init__(unique_id=unique_id, *args, **kwargs)

        self.add_listener("connect", self.on_connect)
        self.add_listener("disconnect", self.on_disconnect)
        self.add_listener("error", self.on_error)

        self.update_filename()



    @property
    def download_path(self) -> Path:
        return DOWNLOADS_ROOT / self.unique_id / self.filename



    def update_filename(self) -> str:
        self.filename = f"{now()}_UTC.avi"

        return self.filename



    def terminate(self) -> None:
        try:
            self.stop_download()
        except Exception as e:
            warn(f"Error during `stop_download`: {e}")

        self.stop()

        # TODO:
        upload_to_youtube(self.download_path)



    async def on_connect(self, _) -> None:
        print(f"Connected to room '{self.room_id}' (https://tiktok.com/@{self.unique_id}/live)")

        self.download_path.parent.mkdir(parents=True, exist_ok=True)

        self.download(path=self.download_path) # type: ignore


    async def on_error(self, error: Exception) -> None:
        warn(str(error))


    async def on_disconnect(self, _) -> None:
        print("Disconnected. Saving & uploading current video and attempting to reconnect...")
        self.terminate()

        return self.main()



    def main(self) -> None:
        try:
            return self.run()

        except LiveNotFound:
            warn(f"User `@{self.unique_id}` seems to be offline, retrying in 1 minute...")
            self.stop()

            sleep(60)

            return self.main()

        except KeyboardInterrupt:
            warn("`CTRL + C` detected, terminating...")
            self.terminate()
            print("ok!")



if __name__ == '__main__':
    TikTokDownloadClient('username').main()
