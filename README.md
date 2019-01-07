# Python CGRateS Api Client

[![PyPI version](https://badge.fury.io/py/py-cgrates.svg)](https://badge.fury.io/py/py-cgrates)

WIP

See: https://github.com/cgrates/cgrates



## Install

    pip install py_cgrates

## Usage 

## Account Management - Create
        
    from cgrates import Client
    from cgrates import models
    
    api = Client(tenant="demo")  # host=localhost, port=2080
    
    account = api.add_account(account="AcmeWidgets")
    
    => <Account(account=AcmeWidgets,...)>
    
    dest = api.add_destination("DST_64", prefixes=["64"])
    
    => <Destination(DST_64, [64])>
    
    rates = api.add_rates(rate_id="RT_STANDARD", rates=[
    models.Rate({"rate": 0.25, "rate_unit": 60, "rate_increment": 60})
    ])
    
    => [<Rate(rate=0.25, rate_unit=60,...)>]
    
    dest_rates = api.add_destination_rates(dest_rate_id="DR_64", dest_rates=[
    models.DestinationRate({"rate_id": "RT_STANDARD", "dest_id": "DST_64"})
    ])
    
    => [<DestinationRate(rate_id=RT_STANDARD, dest_id=DST_64,...)>]
    
    timing = api.add_timing(timing_id="WEEKEND", week_days=[6, 7])
    
    => <Timing(timing_id=WEEKEND,...)>
    
    rating_plans = api.add_rating_plans(rating_plan_id="RPL_CASUAL", rating_plans=[
    models.RatingPlan({"dest_rate_id": "DR_64", "timing_id": "WEEKEND"})
    ])
    
    => [<RatingPlan(dest_rate_id=DR_64, timing_id=WEEKEND,...)>]
    
    rating_profiles = api.add_rating_profiles(rating_profile_id="RPF_1", subject="*any",rating_plan_activations=[
    models.RatingPlanActivation({'rating_plan_id': 'RPL_CASUAL', 'activation_time': datetime.now()})
    ])
    
    api.reload_cache()
    


## Account Management - Get/List
    
    api = Client(tenant="demo")
    
    account = api.get_account(account="AcmeWidgets")
    
    => <Account(account=AcmeWidgets,...)>
    
    dest = api.get_destination(destination_id="DST_64")
    
    => <Destination(DST_64, [64])>
    
    rates = api.get_rates(rate_id="RT_STANDARD")
    
    => [<Rate(rate=0.25, rate_unit=60,...)>]
    
    timing = api.get_timing(timing_id="WEEKEND")
    
    => <Timing(timing_id=WEEKEND,...)>
    
    rating_plans = api.get_rating_plans(rating_plan_id="RPL_CASUAL")
    
    => [<RatingPlan(dest_rate_id=DR_64, timing_id=WEEKEND,...)>]

        