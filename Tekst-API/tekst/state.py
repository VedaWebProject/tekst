from tekst.models.platform import PlatformStateDocument


async def get_state() -> PlatformStateDocument | None:
    state = await PlatformStateDocument.find_one()
    if not state:
        raise RuntimeError("Could not find platform state document")
    return state


async def update_state(**kwargs) -> PlatformStateDocument:
    state = await get_state()
    for k, v in kwargs.items():
        setattr(state, k, v)
    return await state.replace()