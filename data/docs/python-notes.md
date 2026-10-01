# Python Notes

## Variables and Types

Python is dynamically typed, so variables do not need explicit type declarations. Common built-in types include `int`, `float`, `str`, `bool`, `list`, `tuple`, `dict`, and `set`. Use `type()` to inspect a value's type at runtime. Type hints like `def greet(name: str) -> str` are optional but improve readability and help tools catch bugs early.

## Control Flow

The `if` / `elif` / `else` statements control branching. Loops come in two flavors: `for` iterates over sequences, and `while` repeats until a condition is false. Use `break` to exit a loop early and `continue` to skip to the next iteration. List comprehensions such as `[x * 2 for x in range(10)]` are the idiomatic way to transform collections.

## Functions

Define functions with the `def` keyword. Functions can take default arguments, keyword arguments, and a variable number of positional arguments with `*args`. Use `**kwargs` to accept arbitrary keyword arguments. Docstrings in triple quotes describe what a function does and are accessible via `help()`.

## Virtual Environments

Always isolate project dependencies with a virtual environment. Create one with `python -m venv .venv` and activate it with `source .venv/bin/activate` on macOS and Linux, or `.venv\\Scripts\\activate` on Windows. Install packages with `pip install` and freeze the exact versions into `requirements.txt` using `pip freeze > requirements.txt`.

## Testing

The standard library ships with `unittest`, and `pytest` is the popular third-party runner. Write small, focused test functions that assert expected behavior. Run the suite often, ideally before every commit. A test that fails for an unknown reason is more dangerous than no test at all, because it teaches you to ignore failures.

## Common Gotchas

Mutable default arguments like `def f(items=[])` are shared across calls; use `None` and create a new list inside instead. Remember that integer division with `//` rounds down, while `/` always returns a float. Finally, never use `==` to compare with `None`; use `is None`.
