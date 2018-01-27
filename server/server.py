from aiohttp import web
import socketio

measurements = []
N = 40

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

class KalmanFilter(object):

    def __init__(self, process_variance, estimated_measurement_variance):
        self.process_variance = process_variance
        self.estimated_measurement_variance = estimated_measurement_variance
        self.posteri_estimate = 0.0
        self.posteri_error_estimate = 1.0

    def input_latest_noisy_measurement(self, measurement):
        priori_estimate = self.posteri_estimate
        priori_error_estimate = self.posteri_error_estimate + self.process_variance

        blending_factor = priori_error_estimate / (priori_error_estimate + self.estimated_measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

    def get_latest_estimated_measurement(self):
        return self.posteri_estimate

process_variance = 1.2
measurement_standard_deviation = 1.1
estimated_measurement_variance = measurement_standard_deviation ** 2
kf = KalmanFilter(process_variance, estimated_measurement_variance)

def remove_white_noise():
  global measurements
  alpha = 2 / (N + 1)
  nominator = 0
  denom = 0
  for i in range(0, N):
    D = measurements[N - 1 - i]
    q = pow((1 - alpha), i)
    nominator += (D * q)
    denom += q

  measurements = []
  return (nominator / denom)


def kf_filter(observation):
  kf.input_latest_noisy_measurement(observation)
  print(kf.get_latest_estimated_measurement())


def logdata(acc):
    if len(measurements) < 10:
      measurements.append(acc)
    else:
      measurements.append(acc)
      kf_filter(acc)

@sio.on('shoot')
async def shoot(sid, data):
  print("Shoot!")

@sio.on('acc')
async def acc(sid, data):
  logdata(float(data))

@sio.on('heading')
async def heading(sid, data):
  h = float(data)
  logdata(h)

if __name__ == '__main__':
    web.run_app(app)

