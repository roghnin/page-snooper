from time import sleep
import gmail
import costco
from datetime import datetime
import pytz

if __name__ == '__main__':
    while(True):
        print(datetime.now(pytz.timezone('US/Eastern')).strftime("%d/%m/%Y %H:%M:%S"))
        print("snooping...")
        try:
            costco.snoop()
        except Exception:
            pass
        print("sleep.")
        sleep(10 * 60)
