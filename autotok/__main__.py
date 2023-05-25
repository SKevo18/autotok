import typer
import anyio

from autotok.listener import AutoTokClient
from functools import wraps



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



if __name__ == "__main__":
    CLI()
