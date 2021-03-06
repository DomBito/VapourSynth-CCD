# VapourSynth-CCD
Unoptimized port of CCD for VapourSynth

CCD - Camcorder Color Denoise - is an amazing VirtualDub filter made by Sergey Stolyarevsky (according to [this Doom9 thread](https://forum.doom9.net/showthread.php?t=181549&page=2)).
**It's a chroma denoiser that works great on old sources such as VHSes and DVDs.**

This VS function tries to replicate what the original CCD plugin does.

## Usage
ccd(clip,threshold=5,shownoise=False)

- clip: The video is meant to be bt601 YUV format
- threshold: [>=0] just use something between 3 and 15 and you will get reasonable results.
- shownoise: if True, returns the removed chroma noise on a black luma clip instead of the filtered video.
- output: bt601 YUV420P8 format


## Vapoursynth Developers, please re-write this efficiently

Looking at the original CCD's source code, one can notice that the filter basically does a conditional convolution with 16 pixels (+ the center one) in a 25x25 matrix, like so:

![conv matrix illustration](https://github.com/DomBito/VapourSynth-CCD/blob/main/matrix.png?raw=true)

The condition is given by the threshold. If the Euclidian distance between the RGB values of the center pixel and a given pixel in the convolution matrix is less than the threshold, then this pixel is considered in the convolution/average.
After the convolution, the videonode is converted back to YUV, and only the chroma channels are replaced by the convoluted clip, thus preserving luma information.

Even though this filter is very much usable, my programming skills are lacking to make this work as fast as the original one. I don't know how to do conditional convolutions in VS using its tools and I also don't know how to use Vapoursynth's C, C++ or Rust API to make an optimized version of this.
