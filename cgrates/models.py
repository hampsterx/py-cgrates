from schematics.models import Model as DefaultModel
from schematics.types import (
    StringType as DefaultStringType, DateTimeType,
    FloatType, IntType, ListType, BooleanType
)

class Model(DefaultModel):

    def to_dict(self):
        return self.to_primitive()


class SecondsType(IntType):

    def convert(self, value, context=None):

        value = value.replace("s", "") if value else None

        if not value:
            return None

        return self.to_native(value, context)

    def to_primitive(self, value, context=None):
        value = super(SecondsType, self).to_primitive(value,context=context)
        return "{}s".format(value)


class StringType(DefaultStringType):
    def convert(self, value, context=None):

        if not value:
            return None

        return self.to_native(value, context)


class CDR(Model):
    origin_id = StringType(serialized_name="OriginID")
    category = StringType(serialized_name="Category")
    request_type = StringType(serialized_name="RequestType")
    direction = StringType(serialized_name="Direction")
    destination = StringType(serialized_name="Destination")
    setup_time = DateTimeType(serialized_name="SetupTime", serialized_format="%Y-%m-%dT%H:%M:%S%z")
    answer_time = DateTimeType(serialized_name="AnswerTime", serialized_format="%Y-%m-%dT%H:%M:%S%z")
    usage = StringType(serialized_name="Usage")
    tenant = StringType(serialized_name="Tenant")
    type_of_record = StringType(serialized_name="ToR")

    def __repr__(self):
        return '<CDR(origin_id={self.origin_id},...)>'.format(self=self)

class VoiceCDR(CDR):
    type_of_record = StringType(default="*voice", serialized_name="ToR")

class DataCDR(CDR):
    type_of_record = StringType(default="*data", serialized_name="ToR")

class SMSCDR(CDR):
    type_of_record = StringType(default="*sms", serialized_name="ToR")


class Rate(Model):
    connect_fee = FloatType(default=0, serialized_name="ConnectFee")
    rate = FloatType(serialized_name="Rate")
    rate_unit = SecondsType(serialized_name="RateUnit")
    rate_increment = SecondsType(serialized_name="RateIncrement")
    group_interval_start = SecondsType(serialized_name="GroupIntervalStart", required=False)

    def __repr__(self):
        return '<Rate(rate={self.rate}, rate_unit={self.rate_unit},...)>'.format(self=self)

class Destination(Model):
    destination_id = StringType(serialized_name="Id", required=True)
    prefixes = ListType(StringType(), serialized_name="Prefixes", required=True)

    def __repr__(self):
        return '<Destination({}, [{}])>'.format(self.destination_id, ",".join(self.prefixes))


class DestinationRate(Model):
    rate_id = StringType(serialized_name="RateId", required=True)
    dest_id = StringType(serialized_name="DestinationId", required=True)
    rounding_method = StringType(serialized_name="RoundingMethod", default="*up")
    rounding_decimals = IntType(serialized_name="RoundingDecimals", default=4)
    rate = StringType(serialized_name="Rate")
    max_cost = FloatType(serialized_name="MaxCost")
    max_cost_strategy = StringType(serialized_name="MaxCostStrategy")

    def __repr__(self):
        return '<DestinationRate(rate_id={self.rate_id}, dest_id={self.dest_id},...)>'.format(self=self)


class RatingPlan(Model):
    dest_rate_id = StringType(serialized_name="DestinationRatesId", required=True)
    timing_id = StringType(serialized_name="TimingId", required=True)
    weight = IntType(serialized_name="Weight", default=10)

    def __repr__(self):
        return '<RatingPlan(dest_rate_id={self.dest_rate_id}, timing_id={self.timing_id},...)>'.format(self=self)


class RatingPlanActivation(Model):
    rating_plan_id = StringType(serialized_name="RatingPlanId", required=True)
    fallback_subjects = StringType(serialized_name="FallbackSubjects")
    activation_time = DateTimeType(serialized_name="ActivationTime", serialized_format="%Y-%m-%dT%H:%M:%SZ")

    def __repr__(self):
        return '<RatingPlanActivation(rating_plan_id={self.rating_plan_id},...)>'.format(self=self)


class Account(Model):
    account = StringType(serialized_name="ID", required=True)   # todo: result['ID'].split(":")[1]
    allow_negative = BooleanType(default=False, serialized_name="AllowNegative")
    disabled = BooleanType(default=False, serialized_name="Disabled")

    def __repr__(self):
        return '<Account(account={self.account},...)>'.format(self=self)


