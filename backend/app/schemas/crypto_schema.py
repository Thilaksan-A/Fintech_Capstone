from app.models.crypto import CryptoAsset, CryptoTechnicalIndicator
from app.extensions import ma


class CryptoAssetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CryptoAsset
        load_instance = True
        include_relationships = False


class CryptoTechnicalIndicatorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CryptoTechnicalIndicator
        load_instance = True
        include_fk = True
