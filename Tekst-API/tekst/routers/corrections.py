from typing import Annotated

from beanie import PydanticObjectId
from fastapi import APIRouter, Path, status

from tekst import errors
from tekst.auth import UserDep
from tekst.models.correction import CorrectionCreate, CorrectionDocument, CorrectionRead
from tekst.models.location import LocationDocument
from tekst.models.notifications import TemplateIdentifier
from tekst.models.resource import ResourceBaseDocument
from tekst.models.text import TextDocument
from tekst.models.user import UserDocument
from tekst.notifications import broadcast_admin_notification, send_notification
from tekst.utils import pick_translation


# initialize corrections router
router = APIRouter(
    prefix="/corrections",
    tags=["corrections"],
)


@router.post(
    "",
    response_model=CorrectionRead,
    status_code=status.HTTP_201_CREATED,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_404_CONTENT_NOT_FOUND,
        ]
    ),
)
async def create_correction(
    correction: CorrectionCreate,
    user: UserDep,
) -> CorrectionDocument:
    """Creates a correction note referring to a specific content"""
    # check if the resource this content belongs to is readable by user
    resource_doc = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == correction.resource_id,
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    )
    if not resource_doc:
        raise errors.E_404_RESOURCE_NOT_FOUND
    # check if the given position is valid
    if not await LocationDocument.find_one(
        LocationDocument.text_id == resource_doc.text_id,
        LocationDocument.level == resource_doc.level,
        LocationDocument.position == correction.position,
    ).exists():
        raise errors.E_404_CONTENT_NOT_FOUND
    # force user ID of correction to match reqesting user
    correction.user_id = user.id
    # notify the resource's owner (or admins if it's public) of the new correction
    msg_specific_attrs = {
        "from_user_name": user.name if "name" in user.public_fields else user.username,
        "correction_note": correction.note,
        "text_slug": (await TextDocument.get(resource_doc.text_id)).slug,
        "resource_id": resource_doc.id,
        "resource_title": pick_translation(resource_doc.title),
    }
    if not resource_doc.public and resource_doc.owner_id:
        to_user: UserDocument = await UserDocument.get(resource_doc.owner_id)
        if (
            to_user
            and to_user.id != user.id
            and TemplateIdentifier.EMAIL_NEW_CORRECTION.value
            in to_user.user_notification_triggers
        ):
            await send_notification(
                to_user,
                TemplateIdentifier.EMAIL_NEW_CORRECTION,
                **msg_specific_attrs,
            )
    else:
        await broadcast_admin_notification(
            TemplateIdentifier.EMAIL_NEW_CORRECTION,
            **msg_specific_attrs,
        )
    # create correction note
    return await CorrectionDocument.model_from(correction).create()


@router.get(
    "/{resourceId}",
    response_model=list[CorrectionRead],
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
        ]
    ),
)
async def get_corrections(
    resource_id: Annotated[PydanticObjectId, Path(alias="resourceId")],
    user: UserDep,
) -> list[CorrectionDocument]:
    """Returns a list of all corrections for a specific resource"""
    # check if the requested resource is owned by this user
    resource_doc = await ResourceBaseDocument.get(
        resource_id,
        with_children=True,
    )
    if not resource_doc or (user.id != resource_doc.owner_id and not user.is_superuser):
        raise errors.E_404_RESOURCE_NOT_FOUND
    # return all corrections for the resource
    return await CorrectionDocument.find(
        CorrectionDocument.resource_id == resource_id,
    ).to_list()


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errors.responses([errors.E_404_NOT_FOUND, errors.E_403_FORBIDDEN]),
)
async def delete_correction(
    correction_id: Annotated[PydanticObjectId, Path(alias="id")],
    user: UserDep,
) -> None:
    """Deletes a specific correction note"""
    # get correction
    correction_doc = await CorrectionDocument.get(correction_id)
    if not correction_doc:
        raise errors.E_404_NOT_FOUND
    # check if the requested resource is owned by this user
    resource_doc = await ResourceBaseDocument.get(
        correction_doc.resource_id,
        with_children=True,
    )
    if not resource_doc or (user.id != resource_doc.owner_id and not user.is_superuser):
        raise errors.E_403_FORBIDDEN
    # delete correction
    await correction_doc.delete()
