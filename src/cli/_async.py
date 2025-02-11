import asyncio
import inspect
from functools import wraps
from typing import override

import typer


class UTyper(typer.Typer):
    """A Typer subclass to support async functions as commands."""

    # https://github.com/tiangolo/typer/issues/88
    @override
    def command(self, *args, **kwargs):  # noqa: ANN202
        decorator = super().command(*args, **kwargs)

        def add_runner(f):  # noqa: ANN202
            if inspect.iscoroutinefunction(f):

                @wraps(f)
                def runner(*args, **kwargs):  # noqa: ANN202
                    return asyncio.run(f(*args, **kwargs))

                decorator(runner)
            else:
                decorator(f)
            return f

        return add_runner
