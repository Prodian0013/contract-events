from .models.transfer import Transfer

class EventAnalyzer:
    def __init__(self, event_name):
        self.event_name = event_name

    def get_events(self, events_list):
        events = list(filter((lambda event: event is not None), map(self._analyze, events_list)))
        return events

    def _analyze(self, event_dict):
        return None


class TransferEventAnalyzer(EventAnalyzer):
    def __init__(self):
        EventAnalyzer.__init__(self, 'Transfer')

    def _analyze(self, event_dict):
        if event_dict['event'] == self.event_name:
            return Transfer(
                block_time=event_dict['blockNumber'],
                amount=event_dict['args']['value'],
                to_address=event_dict['args']['to'],
                from_address=event_dict['args']['from'],
                timestamp=event_dict['timestamp']
            )
        else:
            return None
