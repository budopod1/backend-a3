from time import perf_counter


class Timer:
    def __init__(self):
        self.last_tick = perf_counter()
        self.time_delta = 0
    
    def tick(self):
        now = perf_counter()
        self.time_delta = now - self.last_tick
        self.last_tick = now

    def fps(self):
        return 1 / self.time_delta


class Stopwatch:
    def __init__(self):
        self.real_start = perf_counter()
        self.start()

    def total(self):
        return perf_counter() - self.real_start
    
    def start(self):
        self.started = perf_counter()

    def time(self):
        return perf_counter() - self.started

    def step(self, event):
        print(f"{event}: {self.time()}")
        self.start()


class Cooldown:
    def __init__(self, time=0):
        self.start(time)

    def start(self, time=0):
        self.time = time
        self.reset()

    def reset(self):
        self.end = perf_counter() + self.time

    def expired(self):
        return perf_counter() > self.end
