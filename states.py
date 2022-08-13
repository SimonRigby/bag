class SomeClass:

    def __init__(self, callbacks):
        self._processor = _some_state
        self._callbacks = callbacks
      
    def tick(self, data):
        self._processor(data)
        
        
    def some_state(self, data):
        # do stuff before conditions are evaluated
        
        if condition:
            # do stuff if condition is true
            # note: or defer it to the state change if that makes sense
            # maybe calling self._processor() again which would apply the new state
            # without needing a 'tick()'
            self._processor = self._some_other_state
            self._processor(data) # because we need the new state to run on this data point (tick)
            
            # and even raise an event if neccesary
            cb = self._callbacks.get('some_other_state')
            if cb is not None:
                cb(data)
            
        # anything that needs tidying up
        # possibly not wise - after all we have transferred state

    def some_other_state(self, data):
        # do stuff
        if condition:
            self._processor = self._some_state
        # and/or do stuff

   
if __name__ == '__main__':
    
    def some_callback(data):
      # do some with the rasied event
      print('event raised', data)
    
    callbacks = { 'some_other_state': some_callback }
    s = SomeClass(callbacks)
    for x in some_collection:
        s.tick(x)
