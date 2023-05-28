import typing as t
import typer
import asyncio

from pathlib import Path
from functools import wraps

from autotok.listener import AutoTokClient
from autotok.uploader import upload_to_youtube


CLI = typer.Typer()


def run_async(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        async def coro_wrapper():
            return await func(*args, **kwargs)

        return asyncio.run(coro_wrapper())

    return wrapper



@CLI.command()
@run_async
async def listen(usernames: list[str], upload: bool=True) -> None:
    clients = [AutoTokClient(unique_id=username, upload=upload) for username in usernames]

    try:
        await asyncio.gather(*[client.main() for client in clients])

    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        print("`CTRL + C`, quitting...")

        for client in clients:
            client.terminate()
            print(f"`@{client.unique_id}` exitted successfully!")



@CLI.command()
def upload(video_path: Path, title: t.Optional[str]=None, category_id: int=24, tags: list[str]=[], playlist_id: t.Optional[str]=None, description: t.Optional[t.Text]=None) -> None:
    print(f"Uploading `{video_path.name}` to YouTube...")

    video_id = upload_to_youtube(
        video_path=video_path,
        title=title if title is not None else video_path.stem,
        description=description if description is not None else '',
        category_id=category_id,
        tags=tags,
        playlist_id=playlist_id
    )

    print(f"Video ID `{video_id}` was uploaded successfuly: https://youtube.com/watch?v={video_id}")



if __name__ == "__main__":
    CLI()
