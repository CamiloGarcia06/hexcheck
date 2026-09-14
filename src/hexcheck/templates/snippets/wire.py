app.state.__FEATURE__ = __Entity__UseCases(
    create=Create__Entity__(deps.__entity___repository),
    list_all=List__Feature__(deps.__entity___repository),
)
app.include_router(__FEATURE___router)
