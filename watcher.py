# sample client at bottom

# naive trade :)
class Trade:
    def __init__(self, entry_time, entry_price):
      self.entry_time = entry_time
      self.entry_price = entry_price
      self.exit_time = None
      self.exit_price = None

# Watcher
# my base class - essentially observes and responds to stream (ie price)

# this is based on ideas I have where there are several 'stages' to the setup
# a trigger, to look for a signal, to look for an entry etc etc.
# I wanted to get away from if .. else trees and it felt 'statey'

# Watcher basically manages some call backs if the outside world wants to know 
# about a change of state. \
# raise_event is just a convenience wrapper
# processor is the function that executes at each tick - or what state is the machine/watcher in

class Watcher:
    def __init__(self, callbacks):
        self.callbacks = callbacks
        self.processor = setup
        
    def setup(self, data = None):
        # global init here rather than in constructor to allow 'reseting' the machine
        # ie changing 'state' to 'setup'
        pass

    # convenience as puts 'None checking' in one place
    def raise_event(self, name, data):
        cb = self.callbacks.get(name)
        if cb is not None:
            cb(data)
    
# really contrived implementation
# if price closes three times in a row in a direction, enter in that direction for 3 candles
class GapWatcher(Watcher):
    def __init__(self, callbacks, target_gap):
        super().__init__(callbacks)
        self.target_gap = target_gap
    
    # client calls this once per data item in the stream
    # this is with an eye to making the engine common for both backtesting and trading.
    def tick(self, row):
      self.row = row
      self.processor()
      
    # every implementation of Watcher should have 'setup' both to initialise and to 'reset the machine' 
    def setup(self):
        self.trade = Trade()
        self.current_gap = 0
        self.current_hold = 0
        self.proccesor = self.measuring
        # changed state above to measuring and now call the processor again directly as the next state needs to run.
        # I think this is handy as I have direct control over whether I can process a candle in one 'state'
        # and then change state and choose whether the new state also processes straight away or waits for the next tick
        self.processor()
    
    # the rest of the methods in GapWatcher are effectively the states.
    # I call raise_event each so any callbacks fire at the client
    
    # does what it says on the tin. Finds a run of three candles in one direction
    def measuring(self):
      
        # this can obviously return anything .. here its just the time of the candle
        self.raise_event('measuring', self.row.time)
        
        if self.current_gap > 0: 
            if self.row.aspect == 1:
                self.current_gap += 1
            else
                self.current_gap = -1
        elif self.current_gap < 0:
            if self.row.aspect == -1:
                self.current_gap -=1
            else
                self.current_gap = 1
        else: # current_gap == 0 (ie first iter)
            self.current_gap = self.row.aspect
        
        if self.current_gap >= self.target_gap:
            # found a run of three - enter the trade
            self.processor = self.entering
            # manually call processor again so I can enter on this candles close
            self.processor()

    def entering(self):
        
        self.trade.entry_time = self.row.time
        self.trade.entry_price = self.row.mid_close
        
        # choice of where to raise the event. Needed to delay here until trade was populated.
        self.raise_event('entering', self.trade)
        
        # here I don't call self.processor() manually as I want it to start counting on the next candle
        # so I just assign the next state
        self.processor = self.counting
        
    def counting(self):
        
        self.current_hold += 1
        self.raise_event('counting', self.current_hold)
        
        if self.current.hold == 3:
            self.trade.exit_time = self.row.time
            self.trade.exit_price = self.row.mid_close
            self.processor = self.closing
            self.processor()
    
    def closing(self):
        # client could 'register' for this and add the trade to a list of closed trades
        self.raise_event('closing', self.trade)
        self.processor = self.setup
        self.processor()

if __name__ == '__main__':
    trades = []
    
    df = pd.read_pickle('some dataframe')
    
    def add_trade(t):
        trades.append(t)
        
    def entering_trade(t):
        print(f'entering trade @{t.entry_price}')
        
    callbacks = {
        'closing' : add_trade,
        'entering' : entering_trade
    }
    w = GapWatcher(callbacks, target_gap = 3)
    
    for row in df.itertuples():
        w.tick(row)
       

        
        
        
        
