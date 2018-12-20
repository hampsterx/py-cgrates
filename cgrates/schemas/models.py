import datetime
from schematics.models import Model as DefaultModel
from . import fields

class Model(DefaultModel):

    def to_dict(self):
        return self.to_primitive()


class CDR(Model):
    origin_id = fields.StringType(serialized_name="OriginID")
    category = fields.StringType(serialized_name="Category")
    request_type = fields.StringType(serialized_name="RequestType")
    direction = fields.StringType(serialized_name="Direction")
    destination = fields.StringType(serialized_name="Destination")
    setup_time = fields.DateTimeType(serialized_name="SetupTime", serialized_format="%Y-%m-%dT%H:%M:%S%z")
    answer_time = fields.DateTimeType(serialized_name="AnswerTime", serialized_format="%Y-%m-%dT%H:%M:%S%z")
    usage = fields.StringType(serialized_name="Usage")
    tenant = fields.StringType(serialized_name="Tenant")
    type_of_record = fields.StringType(serialized_name="ToR")

    def __repr__(self):
        return '<CDR(origin_id={self.origin_id},...)>'.format(self=self)

class VoiceCDR(CDR):
    type_of_record = fields.StringType(default="*voice", serialized_name="ToR")

class DataCDR(CDR):
    type_of_record = fields.StringType(default="*data", serialized_name="ToR")

class SMSCDR(CDR):
    type_of_record = fields.StringType(default="*sms", serialized_name="ToR")


class Rate(Model):
    connect_fee = fields.FloatType(default=0, serialized_name="ConnectFee")
    rate = fields.FloatType(serialized_name="Rate")
    rate_unit = fields.SecondsType(serialized_name="RateUnit")
    rate_increment = fields.SecondsType(serialized_name="RateIncrement")
    group_interval_start = fields.SecondsType(serialized_name="GroupIntervalStart", required=False)

    def __repr__(self):
        return '<Rate(rate={self.rate}, rate_unit={self.rate_unit},...)>'.format(self=self)

class Destination(Model):
    destination_id = fields.StringType(serialized_name="Id", required=True)
    prefixes = fields.ListType(fields.StringType(), serialized_name="Prefixes", required=True)

    def __repr__(self):
        return '<Destination({}, [{}])>'.format(self.destination_id, ",".join(self.prefixes))


class DestinationRate(Model):
    rate_id = fields.StringType(serialized_name="RateId", required=True)
    dest_id = fields.StringType(serialized_name="DestinationId", required=True)
    rounding_method = fields.StringType(serialized_name="RoundingMethod", default="*up")
    rounding_decimals = fields.IntType(serialized_name="RoundingDecimals", default=4)
    rate = fields.StringType(serialized_name="Rate")
    max_cost = fields.FloatType(serialized_name="MaxCost")
    max_cost_strategy = fields.StringType(serialized_name="MaxCostStrategy")

    def __repr__(self):
        return '<DestinationRate(rate_id={self.rate_id}, dest_id={self.dest_id},...)>'.format(self=self)


class RatingPlan(Model):
    dest_rate_id = fields.StringType(serialized_name="DestinationRatesId", required=True)
    timing_id = fields.StringType(serialized_name="TimingId", required=True)
    weight = fields.IntType(serialized_name="Weight", default=10)

    def __repr__(self):
        return '<RatingPlan(dest_rate_id={self.dest_rate_id}, timing_id={self.timing_id},...)>'.format(self=self)


class RatingPlanActivation(Model):
    rating_plan_id = fields.StringType(serialized_name="RatingPlanId", required=True)
    fallback_subjects = fields.StringType(serialized_name="FallbackSubjects")
    activation_time = fields.DateTimeType(serialized_name="ActivationTime", serialized_format="%Y-%m-%dT%H:%M:%SZ")

    def __repr__(self):
        return '<RatingPlanActivation(rating_plan_id={self.rating_plan_id},...)>'.format(self=self)


class Account(Model):
    account = fields.StringType(serialized_name="ID", required=True)   # todo: result['ID'].split(":")[1]
    allow_negative = fields.BooleanType(default=False, serialized_name="AllowNegative")
    disabled = fields.BooleanType(default=False, serialized_name="Disabled")

    # todo: map these to correct types
    balance_map = fields.StringType(serialized_name="BalanceMap")
    unit_counters = fields.StringType(serialized_name="UnitCounters")
    action_triggers = fields.StringType(serialized_name="ActionTriggers")

    def __repr__(self):
        return '<Account(account={self.account},...)>'.format(self=self)


class Timing(Model):

    timing_id = fields.StringType(serialized_name="ID", required=True)
    time = fields.TimeType(default=datetime.time(0, 0, 0), serialized_name="Time")
    week_days = fields.AnyOrListType(fields.IntType(), default=[], serialized_name="WeekDays")
    month_days = fields.AnyOrListType(fields.IntType(), default=[], serialized_name="MonthDays")
    months = fields.AnyOrListType(fields.IntType(), default=[], serialized_name="Months")
    years = fields.AnyOrListType(fields.IntType(), default=[], serialized_name="Years")

    def __repr__(self):
        return '<Timing(timing_id={self.timing_id},...)>'.format(self=self)
