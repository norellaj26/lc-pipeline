frozen=True — this makes every instance immutable. Once you create an error, nobody can change it

value: Any — not str. Because the bad value might be None (missing LEI), a number (-1000), or a string ('INVALID').

-> 'ValidationError' : "Don't look this up right now. It's a string hint — resolve it later when the class exists."
This is called a forward reference. You're referencing something that will exist, just not yet.

Immutability (frozen=True)

A factory method (@classmethod)

Two representations (__str__ + __repr__)

Serialization (to_dict)
