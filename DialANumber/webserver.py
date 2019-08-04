#!/usr/bin/python3

import threading
import logging
import io
import flask

FAV_ICON = [
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d,
  0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x1e, 0x00, 0x00, 0x00, 0x1e,
  0x08, 0x06, 0x00, 0x00, 0x00, 0x3b, 0x30, 0xae, 0xa2, 0x00, 0x00, 0x00,
  0x06, 0x62, 0x4b, 0x47, 0x44, 0x00, 0xff, 0x00, 0xff, 0x00, 0xff, 0xa0,
  0xbd, 0xa7, 0x93, 0x00, 0x00, 0x00, 0x09, 0x70, 0x48, 0x59, 0x73, 0x00,
  0x00, 0x0b, 0x13, 0x00, 0x00, 0x0b, 0x13, 0x01, 0x00, 0x9a, 0x9c, 0x18,
  0x00, 0x00, 0x00, 0x07, 0x74, 0x49, 0x4d, 0x45, 0x07, 0xe0, 0x01, 0x16,
  0x0a, 0x20, 0x30, 0x2c, 0x48, 0x01, 0x09, 0x00, 0x00, 0x02, 0xa7, 0x49,
  0x44, 0x41, 0x54, 0x48, 0xc7, 0xed, 0x96, 0xcf, 0x6b, 0x13, 0x41, 0x14,
  0xc7, 0xbf, 0xb3, 0xbb, 0x93, 0x9d, 0xd9, 0xb8, 0xf9, 0x51, 0xe9, 0xee,
  0x92, 0x6d, 0x4c, 0xd3, 0xea, 0x86, 0x92, 0x92, 0x26, 0x96, 0x10, 0x96,
  0xd2, 0x5e, 0x43, 0x21, 0xb8, 0xe7, 0xfe, 0x03, 0xc5, 0x43, 0xaf, 0x82,
  0x1e, 0xd2, 0x1f, 0x8a, 0x88, 0x88, 0x60, 0xf1, 0x2e, 0x78, 0xd4, 0x93,
  0x07, 0x0f, 0x39, 0x88, 0x17, 0xf5, 0xd0, 0x43, 0x3d, 0x78, 0xf2, 0xa2,
  0x07, 0x3d, 0x88, 0xb6, 0x82, 0x54, 0x85, 0x84, 0x62, 0xc6, 0x4b, 0x56,
  0xb7, 0x26, 0xd5, 0xb8, 0x09, 0x39, 0xf5, 0xc1, 0x83, 0xd9, 0xe1, 0xf1,
  0x3e, 0xef, 0xbd, 0x9d, 0x37, 0x6f, 0x80, 0x3e, 0xc4, 0xb2, 0xac, 0x35,
  0xc6, 0x98, 0xe6, 0x38, 0xce, 0x5f, 0xed, 0x0c, 0xc3, 0xb8, 0xec, 0x79,
  0x9e, 0x86, 0x61, 0x4a, 0x26, 0x93, 0x59, 0xf7, 0xd7, 0xcb, 0xcb, 0xcb,
  0xa7, 0x33, 0x99, 0xcc, 0xf9, 0xd9, 0xd9, 0xd9, 0xbc, 0x10, 0x42, 0xf2,
  0xf7, 0x53, 0xa9, 0xd4, 0xa5, 0xa1, 0x01, 0xab, 0xd5, 0x2a, 0x00, 0xc0,
  0x34, 0xcd, 0x2b, 0x9c, 0xf3, 0x07, 0x8a, 0xa2, 0x7c, 0x07, 0x20, 0x7c,
  0x95, 0x65, 0x59, 0x50, 0x4a, 0xdf, 0x44, 0xa3, 0xd1, 0x67, 0x42, 0x08,
  0x65, 0x28, 0xd0, 0x7a, 0xbd, 0x0e, 0x00, 0x18, 0x1b, 0x1b, 0xbb, 0x4a,
  0x08, 0x11, 0x41, 0x60, 0x2f, 0xa5, 0x94, 0xee, 0x4f, 0x4d, 0x4d, 0xe5,
  0x87, 0x02, 0x4f, 0x26, 0x93, 0x0f, 0xff, 0x05, 0x04, 0x20, 0xfc, 0xc0,
  0x08, 0x21, 0x22, 0x9b, 0xcd, 0x3a, 0x00, 0x48, 0x68, 0xa8, 0x61, 0x18,
  0x6b, 0xbe, 0xe3, 0xc9, 0xc9, 0xc9, 0xd2, 0xf8, 0xf8, 0x78, 0xad, 0x17,
  0x54, 0x55, 0xd5, 0x4f, 0x00, 0xc0, 0x18, 0x6b, 0x74, 0x32, 0x6f, 0x79,
  0x9e, 0x17, 0x71, 0x5d, 0x37, 0x1c, 0x58, 0x51, 0x94, 0x6f, 0xbe, 0x73,
  0xce, 0xf9, 0x73, 0x55, 0x55, 0x5f, 0x1d, 0x97, 0x2d, 0x63, 0xec, 0xae,
  0xa2, 0x28, 0x4d, 0x7f, 0x2f, 0x16, 0x8b, 0xd5, 0x43, 0x41, 0xd3, 0xe9,
  0x74, 0xb5, 0x9f, 0x12, 0xff, 0xa1, 0x6d, 0x7f, 0x1d, 0x8d, 0x46, 0xbf,
  0x86, 0x02, 0x33, 0xc6, 0xae, 0x87, 0x00, 0x1f, 0xd1, 0xbd, 0xbd, 0x3d,
  0xf5, 0xd8, 0x6a, 0x02, 0x40, 0xa5, 0x52, 0xc1, 0xce, 0xce, 0x0e, 0x4c,
  0xd3, 0x2c, 0x4e, 0x4c, 0x4c, 0x7c, 0xdc, 0xdd, 0xdd, 0xfd, 0xc0, 0x39,
  0x7f, 0xa4, 0x28, 0xca, 0xeb, 0xb0, 0xe7, 0xa3, 0xdd, 0x6e, 0x47, 0x56,
  0x56, 0x56, 0x64, 0x00, 0x88, 0xc7, 0xe3, 0x65, 0xd7, 0x75, 0xdf, 0x36,
  0x1a, 0x8d, 0xcf, 0x5d, 0x86, 0xba, 0xae, 0xdf, 0xf1, 0x23, 0x9d, 0x9e,
  0x9e, 0xbe, 0xa0, 0xeb, 0xfa, 0x2d, 0x4a, 0xa9, 0x18, 0x44, 0x3d, 0xcf,
  0x8b, 0x6b, 0x9a, 0xf6, 0x12, 0x80, 0x90, 0x24, 0x49, 0xcc, 0xcc, 0xcc,
  0x9c, 0xe9, 0x02, 0x53, 0x4a, 0x83, 0xfd, 0xf8, 0x98, 0x73, 0xbe, 0x39,
  0x68, 0xa9, 0x4b, 0xa5, 0x52, 0x21, 0xf8, 0xcd, 0x18, 0xdb, 0xf4, 0x79,
  0xbf, 0xae, 0x3b, 0x21, 0x44, 0xb0, 0x4c, 0xa4, 0x63, 0x3c, 0x90, 0xb4,
  0x5a, 0x2d, 0xe9, 0x8f, 0xf2, 0xff, 0xe8, 0x02, 0x8f, 0x5a, 0x4e, 0xc0,
  0x27, 0xe0, 0xd1, 0x82, 0x65, 0x59, 0xc6, 0x40, 0x63, 0xed, 0xf7, 0x90,
  0x39, 0xd2, 0x92, 0x84, 0x10, 0xd2, 0x05, 0xd6, 0x34, 0xed, 0x1a, 0x00,
  0x48, 0x92, 0x04, 0xdb, 0xb6, 0x6f, 0x03, 0x50, 0x07, 0x05, 0x5b, 0x96,
  0xf5, 0x2e, 0x91, 0x48, 0x3c, 0xf5, 0x93, 0xc9, 0xe5, 0x72, 0xf7, 0x8e,
  0x18, 0x2c, 0x2e, 0x2e, 0x02, 0x00, 0xe6, 0xe6, 0xe6, 0xce, 0x6e, 0x6d,
  0x6d, 0x45, 0x3b, 0x81, 0xdc, 0x18, 0xf4, 0xe6, 0x2a, 0x97, 0xcb, 0x29,
  0x00, 0x28, 0x14, 0x0a, 0x45, 0x21, 0x84, 0xdc, 0x57, 0xb4, 0xba, 0xae,
  0xdf, 0x0c, 0x8e, 0xb9, 0x30, 0xba, 0xb1, 0xb1, 0x71, 0xea, 0xbf, 0xcb,
  0x34, 0x3f, 0x3f, 0x9f, 0x90, 0x65, 0xf9, 0xa0, 0xd7, 0xac, 0xed, 0x47,
  0x93, 0xc9, 0xe4, 0x76, 0xa8, 0xff, 0x13, 0x8b, 0xc5, 0xfc, 0x67, 0x6d,
  0x2e, 0x9f, 0xcf, 0x97, 0x82, 0x4e, 0x4d, 0xd3, 0xdc, 0x2e, 0x16, 0x8b,
  0xf9, 0xa5, 0xa5, 0xa5, 0x73, 0x9c, 0xf3, 0x2f, 0xfe, 0x7e, 0x24, 0x12,
  0x79, 0xe1, 0x38, 0x4e, 0x7a, 0x75, 0x75, 0xd5, 0x00, 0x80, 0x85, 0x85,
  0x85, 0xc1, 0x0e, 0x49, 0xad, 0x56, 0x4b, 0x06, 0xc1, 0x96, 0x65, 0xad,
  0x07, 0x0e, 0xe5, 0x7e, 0x00, 0xfc, 0x64, 0xa8, 0x7d, 0x1c, 0xe8, 0x82,
  0xd1, 0x5e, 0x20, 0xc1, 0x91, 0x39, 0x52, 0xb0, 0x6d, 0xdb, 0x87, 0xc1,
  0xac, 0x9b, 0xcd, 0xe6, 0x41, 0xaf, 0x19, 0x4b, 0x29, 0x3d, 0x1c, 0x7a,
  0x84, 0xba, 0xae, 0xdf, 0xef, 0xbc, 0xa1, 0xdf, 0xbb, 0xae, 0x9b, 0xc8,
  0x66, 0xb3, 0xfe, 0xdb, 0xfb, 0x22, 0x21, 0x44, 0xc8, 0xb2, 0xdc, 0xb4,
  0x6d, 0xbb, 0xd2, 0xaf, 0xbf, 0x9f, 0xad, 0xaf, 0x2e, 0x97, 0x6c, 0x36,
  0xc9, 0x2e, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42,
  0x60, 0x82
]

SENSOR = None

app = flask.Flask("DialANumber")

@app.route("/")
def MainHandler():
    global SENSOR
    temp, pressure, humidity = SENSOR.ReadMeasurementsFresh()
    out = [
        "<pre>",
        "Temperature in Celsius : %.2f C" % temp,
        "Relative Humidity : %.2f %%" % humidity,
        "Pressure : %.2f hPa " % pressure,
        "</pre>",
    ]
    return "\n".join(out)

@app.route("/favicon.ico")
def IconHandler():
    return flask.send_file(io.BytesIO(bytes(FAV_ICON)),
                           mimetype='image/x-icon')
    
        
def RunServer(port):
    app.run(host="0.0.0.0", debug=False, port=port)

def RunServerInThread(port, sensor):
    global SENSOR
    SENSOR = sensor
    threading.Thread(target=RunServer, args=(port,)).start()

if __name__ == "__main__":
    import PiLib.bme280 as bme280
    SENSOR = bme280.SensorBME280()
    logging.basicConfig(level=logging.INFO)
    RunServer(port=9999)
    logging.info("exit server")

