from marshmallow import Schema, SchemaOpts, fields, post_load
from marshmallow.exceptions import ValidationError
from webargs import validate

from rotkehlchen.assets.asset import Asset
from rotkehlchen.errors import DeserializationError, UnknownAsset
from rotkehlchen.serialization.deserialize import (
    deserialize_asset_amount,
    deserialize_fee,
    deserialize_location,
    deserialize_price,
    deserialize_timestamp,
    deserialize_trade_type,
)
from rotkehlchen.typing import Location, TradeType


class TimestampField(fields.Field):

    @staticmethod
    def _serialize(value, attr, obj, **kwargs):  # pylint: disable=unused-argument
        return value

    def _deserialize(self, value, attr, data, **kwargs):  # pylint: disable=unused-argument
        try:
            timestamp = deserialize_timestamp(value)
        except DeserializationError as e:
            raise ValidationError(str(e))

        return timestamp


class AmountField(fields.Field):

    @staticmethod
    def _serialize(value, attr, obj, **kwargs):  # pylint: disable=unused-argument
        return str(value)

    def _deserialize(self, value, attr, data, **kwargs):  # pylint: disable=unused-argument
        try:
            amount = deserialize_asset_amount(value)
        except DeserializationError as e:
            raise ValidationError(str(e))

        return amount


class PriceField(fields.Field):

    @staticmethod
    def _serialize(value, attr, obj, **kwargs):  # pylint: disable=unused-argument
        return str(value)

    def _deserialize(self, value, attr, data, **kwargs):  # pylint: disable=unused-argument
        try:
            price = deserialize_price(value)
        except DeserializationError as e:
            raise ValidationError(str(e))

        return price


class FeeField(fields.Field):

    @staticmethod
    def _serialize(value, attr, obj, **kwargs):  # pylint: disable=unused-argument
        return str(value)

    def _deserialize(self, value, attr, data, **kwargs):  # pylint: disable=unused-argument
        try:
            fee = deserialize_fee(value)
        except DeserializationError as e:
            raise ValidationError(str(e))

        return fee


class AssetField(fields.Field):

    @staticmethod
    def _serialize(value: Asset, attr, obj, **kwargs) -> str:  # pylint: disable=unused-argument
        return str(value.identifier)

    def _deserialize(  # pylint: disable=unused-argument
            self,
            value: str,
            attr,
            data,
            **kwargs,
    ) -> Asset:
        try:
            asset = Asset(value)
        except (DeserializationError, UnknownAsset) as e:
            raise ValidationError(str(e))

        return asset


class TradeTypeField(fields.Field):

    @staticmethod
    def _serialize(
            value: TradeType,
            attr,  # pylint: disable=unused-argument
            obj,  # pylint: disable=unused-argument
            **kwargs,  # pylint: disable=unused-argument
    ) -> str:
        return str(value)

    def _deserialize(
            self,
            value: str,
            attr,  # pylint: disable=unused-argument
            data,  # pylint: disable=unused-argument
            **kwargs,  # pylint: disable=unused-argument
    ) -> TradeType:
        try:
            trade_type = deserialize_trade_type(value)
        except DeserializationError as e:
            raise ValidationError(str(e))

        return trade_type


class LocationField(fields.Field):

    @staticmethod
    def _serialize(
            value: Location,
            attr,  # pylint: disable=unused-argument
            obj,  # pylint: disable=unused-argument
            **kwargs,  # pylint: disable=unused-argument
    ) -> str:
        return str(value)

    def _deserialize(
            self,
            value: str,
            attr,  # pylint: disable=unused-argument
            data,  # pylint: disable=unused-argument
            **kwargs,  # pylint: disable=unused-argument
    ) -> Location:
        try:
            location = deserialize_location(value)
        except DeserializationError as e:
            raise ValidationError(str(e))

        return location


class BaseOpts(SchemaOpts):
    """
    This allows for having the Object the Schema encodes to inside of the class Meta
    """

    def __init__(self, meta, ordered):
        SchemaOpts.__init__(self, meta, ordered=ordered)
        self.decoding_class = getattr(meta, "decoding_class", None)


class BaseSchema(Schema):
    OPTIONS_CLASS = BaseOpts

    @post_load
    def make_object(self, data, **kwargs):  # pylint: disable=unused-argument
        # this will depend on the Schema used, which has its object class in
        # the class Meta attributes
        decoding_class = self.opts.decoding_class  # pylint: disable=no-member
        return decoding_class(**data)


class TradesQuerySchema(BaseSchema):
    from_timestamp = TimestampField(missing=None)
    to_timestamp = TimestampField(missing=None)
    location = LocationField(missing=None)

    class Meta:
        strict = True
        # decoding to a dict is required by the @use_kwargs decorator from webargs
        decoding_class = dict


class TradeSchema(BaseSchema):
    timestamp = TimestampField(required=True)
    location = LocationField(required=True)
    pair = fields.String(required=True)
    trade_type = TradeTypeField(required=True)
    amount = AmountField(required=True)
    rate = PriceField(required=True)
    fee = FeeField(required=True)
    fee_currency = AssetField(required=True)
    link = fields.String(missing='')
    notes = fields.String(missing='')

    class Meta:
        strict = True
        # decoding to a dict is required by the @use_kwargs decorator from webargs
        decoding_class = dict


class TradePatchSchema(TradeSchema):
    trade_id = fields.String(required=True)


class BaseUserSchema(BaseSchema):
    name = fields.String(required=True)
    password = fields.String(required=True)
    sync_approval = fields.String(
        missing='unknown',
        validate=validate.OneOf(choices=('unknown', 'yes', 'no')),
    )

    class Meta:
        strict = True
        # decoding to a dict is required by the @use_kwargs decorator from webargs
        decoding_class = dict


class UserActionSchema(BaseUserSchema):
    action = fields.String(
        validate=validate.OneOf(choices=('login', 'logout')),
        missing=None,
    )
    premium_api_key = fields.String(missing='')
    premium_api_secret = fields.String(missing='')


class NewUserSchema(BaseUserSchema):
    premium_api_key = fields.String(missing='')
    premium_api_secret = fields.String(missing='')


class ExchangeBalanceQuerySchema(BaseSchema):
    name = fields.String(required=True)
    async_query = fields.Boolean(missing=False)

    class Meta:
        strict = True
        # decoding to a dict is required by the @use_kwargs decorator from webargs
        decoding_class = dict


class BlockchainBalanceQuerySchema(BaseSchema):
    name = fields.String(missing='all')
    async_query = fields.Boolean(missing=False)

    class Meta:
        strict = True
        # decoding to a dict is required by the @use_kwargs decorator from webargs
        decoding_class = dict