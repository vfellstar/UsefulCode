from datetime import datetime

def check_if_expired(cls, category_id:str, datetime_to_test:datetime): 
    # ALL GOOD :) TODO integrate into a scheduler - probably do this through the document data manager so you can update the location when deleted too!
    upload_date = datetime_to_test
    time_now = datetime.now()
    time_difference = time_now - datetime_to_test
    hours_passed = time_difference.total_seconds() / 3600
    
    print(f"HOURS PASSED: {hours_passed}")
    hourspassed = 10 # ten hours
    if hourspassed >= hours_passed:
        
        return False
    else:
        return True