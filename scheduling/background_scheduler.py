import threading, time, schedule, logging, os
from datetime import datetime, timedelta
from pprint import pprint

logging.info("Starting Scheduler.")

from etc.settings import Setting
from modules.document_modules.document_monitoring import DocumentMonitoring
document_monitoring = DocumentMonitoring()


check_frequency = 10
def run_continuously(interval=check_frequency):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def test_scheduler():
    print("\n>>> Scheduler Working.\n")
schedule.every().minute.do(test_scheduler)

def delete_expired_files():
    list_of_topics = os.listdir(Setting.STORED_DIR.value)
    list_of_files  = []
    for topic in list_of_topics:
        list_of_tags = os.listdir(os.path.join(Setting.STORED_DIR.value, topic))
        list_of_files.extend([os.path.join(Setting.STORED_DIR.value, topic, tag, file) for tag in list_of_tags for file in os.listdir(os.path.join(Setting.STORED_DIR.value, topic, tag))])
    expired = [document_monitoring.check_if_expired(document_monitoring.get_document_upload_time(document)) for document in list_of_files]
    for doc_loc, expire in zip(list_of_files, expired):
        if expire:
            try:
                document_monitoring.delete_document(doc_loc)
            except Exception:
                pass
            try:
                os.remove(doc_loc)
            except Exception:
                pass
schedule.every().day.at("00:01").do(delete_expired_files)



stop_run_continuously = run_continuously()

time.sleep(check_frequency)

def stop_scheduler(): 
    logging.info("Stopping scheduler")
    stop_run_continuously.set()