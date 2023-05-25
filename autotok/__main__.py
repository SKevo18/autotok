import typing as t
import typer

from pathlib import Path

from autotok.listener import AutoTokClient
from autotok.uploader import upload_to_youtube


CLI = typer.Typer()



@CLI.command()
def listen(username: str, upload: bool=True) -> None:
    client = AutoTokClient(unique_id=username, upload=upload)

    return client.main()


@CLI.command()
def upload(video_path: Path, title: t.Optional[str]=None, category_id: int=24, tags: list[str]=[], playlist_id: t.Optional[str]=None, description: t.Optional[t.Text]=None) -> None:
    print("Uploading...")

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
