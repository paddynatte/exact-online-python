"""Bill of Material Materials API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.bill_of_material_material import BillOfMaterialMaterial


class BillOfMaterialMaterialsAPI(BaseAPI[BillOfMaterialMaterial]):
    """API resource for Bill of Material Materials.

    Supports CRUD operations. No sync endpoint available.

    Usage:
        # List materials
        materials = await client.bill_of_material_materials.list(division=123)

        # Get specific material
        material = await client.bill_of_material_materials.get(division=123, id="guid")

        # Create material (requires existing make Item and BOM version)
        material = await client.bill_of_material_materials.create(
            division=123,
            data={"ItemVersion": "guid", "PartItem": "guid", "Quantity": 1.0}
        )
    """

    ENDPOINT: ClassVar[str] = "/manufacturing/BillOfMaterialMaterials"
    SYNC_ENDPOINT: ClassVar[str | None] = None
    MODEL: ClassVar[type[BillOfMaterialMaterial]] = BillOfMaterialMaterial
    ID_FIELD: ClassVar[str] = "ID"
