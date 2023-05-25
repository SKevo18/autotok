import typing as t

import typer
import anyio

from pathlib import Path
from functools import wraps

from autotok.listener import AutoTokClient
from autotok.uploader import upload_to_youtube



def run_async(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        async def coro_wrapper():
            return await func(*args, **kwargs)

        return anyio.run(coro_wrapper)

    return wrapper



CLI = typer.Typer()


@CLI.command()
@run_async
async def listen(username: str, upload: bool=True) -> None:
    return await AutoTokClient(unique_id=username, upload=upload).main()



@CLI.command()
@run_async
async def upload(video_path: Path, title: str, category_id: int=24, tags: list[str]=[], playlist_id: t.Optional[str]=None, description: t.Optional[t.Text]=None) -> None:
    print("Uploading...")

    video_id = upload_to_youtube(
        video_path=video_path,
        title=title,
        description=description if description is not None else '',
        category_id=category_id,
        tags=tags,
        playlist_id=playlist_id
    )

    print(f"Video ID `{video_id}` was uploaded successfuly: https://youtube.com/watch?v={video_id}")



if __name__ == "__main__":
    CLI()
