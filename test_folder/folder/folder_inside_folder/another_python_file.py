# another python script module

def world(emphasis: str = '!',
          reps: int = 2
          ) -> None:
    """
    A very long
    docstring.
    """
    # some comment
    a = "World"  # inline comment
    a += f'{emphasis*reps}'

    # another comment
    print(a)

# end of current module
