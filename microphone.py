import numpy as np
from polarData import polarData
from pythonAudioMeasurements.audioSample import audioSample
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve as convolve
import cmath




class Microphone:

    def __init__(self, polar, position=[0,0], c=343e3):
        """
        position should be a vector x,y of the relative positoin
        from the specified origin
        position, c must have the same distance units, defaults assume mm


        ---------------------------------------------------------------------
        polar           | polarData object containing the characteristic data 
                        | for the mic
        ---------------------------------------------------------------------
        position        | list [x,y] relative to the origin see units below
        ---------------------------------------------------------------------
        c               | speed of sound in the given medium - should be same 
                        | units as ~position~ (assumed to be mm/s)
        ---------------------------------------------------------------------
        
        
        """
        
        self.polar = polar
        self.position = np.array(position)
        self.c = c

    def normal_origin_dist(self, theta):
        """
        if a plane wave is traveling in at an angle theta, 
        calculates the distance from the origin that the microphone is 
        normal to sound wave

        this is the "addition distance" covered by a plane wave between
        when the mirophone experiences the sound and when it would be 
        experienced at the origin

        ---------------------------------------------------------------------
        theta			| angle of approach (degrees)
        ---------------------------------------------------------------------
        
        """

        # conversion to radians
        theta *= (np.pi/180)

        # unit vector antiparellel to wave direction (from origin to plane)
        plane_direction = np.array([np.cos(theta), np.sin(theta)])

        return np.dot(plane_direction, self.position)


    def apply(self, signal, theta):

        """
        Return the audioSample that results from the ~signal~ approaching as  
        a plane wave at angle ~theta~ from the origin

        This transformation of the signal consists of the effects from both 

        ---------------------------------------------------------------------
        INPUTS
        ---------------------------------------------------------------------
        signal			| (audioSample) the input signal 
        ---------------------------------------------------------------------
        theta			| (float, int) angle of approach (degrees)
        ---------------------------------------------------------------------

        ---------------------------------------------------------------------
        OUTPUTS
        ---------------------------------------------------------------------
        (audioSample) resulting from the described transformation
        ---------------------------------------------------------------------
       """ 

        mic = self.apply_microphone(signal, theta)
        return self.apply_xy(mic, theta)


    def apply_xy(self, signal, theta):

        """
        Applies the phase shift to a signal resluting from its (x,y)
        position, effectively collapses the microphone to the origin

        Leverages that in the freq domain e^(j*t_0*w)*X(w) shifts the 
        corresponding time domain signal by t_0

        ---------------------------------------------------------------------
        INPUTS
        ---------------------------------------------------------------------
        same as Microphone.apply(self, signal, theta)
        ---------------------------------------------------------------------

        ---------------------------------------------------------------------
        OUTPUTS
        ---------------------------------------------------------------------
        (audioSample) resulting from the described transformation
        ---------------------------------------------------------------------
        """

        # get the component frequencies
        signal.toFreq()

        signal.plot(both=True)

        freqs = signal.f()

        print(freqs)

        # time-domain shift
        delta_t =  self.normal_origin_dist(theta)/self.c


        # the resulting phase shift
        phase_shift = np.exp(-1j*2*np.pi*freqs*delta_t)

        result = audioSample(signal*phase_shift, type="f",Fs=signal.fs) 


        signal.toTime()

        return result

    def apply_xy_conv(self, signal, theta):

        """
        same as apply_xy but implemented in the time domain
        """

        # get the component frequencies
        signal.toTime()

        signal.plot(both=True)


        # time-domain shift
        delta_t =  self.normal_origin_dist(theta)/self.c
        delta_n = int(delta_t*signal.fs)
        shift_t = np.zeros(len(signal))
        shift_t[delta_n] = 1


        result = audioSample(convolve(signal, shift_t, "same"), type="t",Fs=signal.fs)


        signal.toTime()

        return result

    def apply_microphone(self, signal, theta, f_targ=None):
        """
        the input signal must have been taken at the same sample rate
        for this to work. 
        """

        # get the frequency response of the microphone at the given theta
        mic_response = self.polar.getData(theta)
        mic_response.removeDCOffset()

        # if f_targ:
        #     for i, f in enumerate(mic_response.f()):
        #         if f >= f_targ: 
        #             mic_response.toFreq()
                    # print(f, abs(mic_response[i]))
                    # break

        # must have signal of same fs as mic response
        assert mic_response.fs == signal.fs, "your input signal must have the same " + \
        "sampling frequency. the microphone has fs: %d, and your signal as %d"%(mic_response.fs, signal.fs)

        
        signal.toTime()
        mic_response.toTime()

        result = convolve(signal, mic_response, "same")

        # print(max(signal))
        # print(np.average(signal))
        # print(sum(signal))
        # print(max(result))
        # print(np.average(result))
        # print(sum(result))

    
        return audioSample(result, Fs=signal.fs) 



if __name__ == "__main__":
    pass