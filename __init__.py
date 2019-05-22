# Copyright 2017 Mycroft AI, Inc.
#

from adapt.intent import IntentBuilder

from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import getLogger
from mycroft.audio import wait_while_speaking
from mycroft.util.parse import extractnumber, extract_datetime


class CAT_UK_Demo(MycroftSkill):
    def __init__(self):
        super(CAT_UK_Demo, self).__init__(name="CAT_UK_Demo")

    def is_yes(self, utt):
        return ("yes" in utt or "yeah" in utt or "sure" in utt
                or "please" in utt);
   
    def is_yesno(self, utt):
        return (self.is_yes(utt) or "no" in utt or "nope" in utt
                or "cancel" in utt);

    # Demo query:  When is my vehicle tax due for renewal
    @intent_handler(IntentBuilder("").require("Taxes").require("Renewal"))
    def handle_tax_query(self, message):
        # TODO: Lookup and load from a database
        data = { "duedate": "December 31st, 2020" }
        self.speak_dialog("taxes.due", data)
        wait_while_speaking()

        r = self.get_response('want.taxes.paid', validator=self.is_yesno,
                              on_fail="say.yes.or.no", num_retries=2)
        if self.is_yes(r):
            data = { }
            email = '\n'.join(self.translate_template('tax.email', data))
            self.send_email("Tax receipt", email)
            self.speak_dialog("taxes.paid")
       
    # Demo query:  When is my car insurance due for renewal
    @intent_handler(IntentBuilder("").require("Query").
        require("Insurance").require("Renewal"))
    def handle_insurance_quote(self, message):

        # TODO: Lookup and load from a database
        data = { "duedate": "January 1st, 2020" }
        self.speak_dialog("insurance.due", data)
        wait_while_speaking()

        r = self.get_response('want.new.quote', validator=self.is_yesno,
                              on_fail="say.yes.or.no", num_retries=2)
        if self.is_yes(r):
            # Create the quote email
            data = { }
            email = '\n'.join(self.translate_template('quote.email', data))
            self.send_email("Insurance quote", email)
            self.speak_dialog("sending.new.quote")
        
    # Demo query:  What is the traffic
    #              What is the traffic like to Sussex
    @intent_handler(IntentBuilder("").require("Traffic").
                    optionally("Dest").optionally("PostCode"))
    def handle_traffic_report(self, message):
        # TODO: Get traffic report from online database, requires contract
        dest = message.data.get("Dest", None)
        postcode = message.data.get("PostCode", None)
        if postcode:
            dest = postcode
        if not dest:
            r = self.get_response('get.destination', num_retries=2)
            if not r:
                return
            dest = r
            
        data = { "dest": dest,
                 "travel_time" : "2.5 hours",
                 "condition": "very slow" }
        self.speak_dialog("travel.report", data)


    # Demo query: I need a delivery quotation
    @intent_handler(IntentBuilder("").require("Quotation").require("Delivery"))
    def handle_delivery_quotation(self, message):
        car = self.get_response('get.car.type', num_retries=2)
        if not car:
            return

        origin = self.get_response('get.origin', num_retries=2)
        if not origin:
            return

        dest = self.get_response('get.destination', num_retries=2)
        if not dest:
            return

        self.speak("The estimated cost will be 65.41 pounds")
        wait_while_speaking()
        r = self.get_response('want.to.book', validator=self.is_yesno,
                              on_fail="say.yes.or.no", num_retries=2)
        if self.is_yes(r):
            self.speak("Your delivery has been booked.")
            
    # Demo query: How much is my car currently worth
    @intent_handler(IntentBuilder("").require("Car").require("Worth").optionally("Reg"))
    def handle_car_worth(self, message):
        car = message.data.get("Reg", None)
        if not car:
            car = self.get_response('get.car.type.or.reg', num_retries=2)
        if not car:
            return

        self.speak("That car is currently valued at 5500 pounds trade, 5900 pounds private and will deprecate by 150 pounds per month")

    # Demo query: I like to hire a car
    @intent_handler(IntentBuilder("").require("Hire").require("Car"))
    def handle_rent_car(self, message):
        date = self.get_response('get.from.date', num_retries=2)
        if not date:
            return
        date = extract_datetime(date)[0]

        duration = self.get_response('get.rental.duration', num_retries=2)
        if not duration:
            return
        duration = int(extractnumber(duration))  # assumes days were spoken
        days = str(duration)

        # TODO: Use the date in the calc somehow?
        cost = 35+10*duration  # cost calc is 35 + 10 per day
        self.speak("The cost to hire a car for " + days +
                   " days will be "+str(cost)+" pounds")
        wait_while_speaking()
        r = self.get_response('want.to.book', validator=self.is_yesno,
                              on_fail="say.yes.or.no", num_retries=2)
        if self.is_yes(r):
            start = '{:%A, %B %d}'.format(date)
            self.speak("Your car has been booked for " + start)

        


def create_skill():
    return CAT_UK_Demo()
