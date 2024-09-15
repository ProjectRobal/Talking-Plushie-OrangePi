import smbus2 as smbus

import wm8960

i2c = smbus.SMBus(1)

wm=wm8960.WM8960(i2c, sample_rate=16_000,
    adc_sync=wm8960.SYNC_ADC,
    sysclk_source=wm8960.SYSCLK_PLL,
    mclk_freq=24_000_000,
    left_input=wm8960.INPUT_MIC1,
    right_input=wm8960.INPUT_MIC2)

wm.enable_module(wm8960.MODULE_SPEAKER)
#wm.enable_module(wm8960.MODULE_MONO_OUT)
#wm.volume(wm8960.MODULE_HEADPHONE,100,100)
wm.volume(wm8960.MODULE_SPEAKER, 100,100)
#wm.mono(True)

print("OK")
