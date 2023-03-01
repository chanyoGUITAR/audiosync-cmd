# audiosync-cmd

#### This tool automatically syncs matching video and audio files using recurrence quantification analysis (RQA). The tool allows you to adjust the sampling rate, hop length, and ftt window size so you can achieve near-perfect synchronization.

#### At the start of this project, I used dynamic time warping (DTW) instead of recurrence quantification analysis (RQA) to synchronize the two audio tracks. This method seemed efficient for my purposes, but didn't achieve near-perfect synchronization on some tests. This led me to implement RQA, which maximizes alignment paths and relies on similarity rather than distance.

#### More information on RQA can be discovered [here](https://en.wikipedia.org/wiki/Recurrence_quantification_analysis) on Wikipedia, and a similar project has been documented on this [pdf](http://www.mtg.upf.edu/system/files/publications/Roma-Waspaa-2014.pdf)

# ※Modified for my own use.

I am rewriting this for a guitar solo project I am doing on Youtube.　Thanks to the producer.
Specifically, I'm changing the process to one where the audio of just the guitar solo is first combined with the video, then replaced with the entire music, and then the video is cut off for the length of that WAV.
As to why this process is necessary, you might want to take a look at the video.
- > https://youtube.com/playlist?list=PL0E3ck3lAqT1ze5KnzRZmRp9MZyUA7q6-

This code helped me a great deal.

## setup
#### Python 2
`pip install -r requirements.txt`
#### Python 3
`pip3 install -r requirements.txt`

## usage

#### use the help command
`python audiosync.py --help`

#### arguments

##### required
`-v, --video | path to video file`

`-a, --audio | path to audio file`

`-o, --output | path to output file`

##### optional

`-f, --fft | fft window size | recommended to be a power of 2 | default: 4410`

`-hl, --hoplength | hop length | the number of samples between successive frames | default: 512`

`-sr, --samplingrate | sampling rate in Hz | Most applications use 44.1kHz | default: 44100Hz`

`-d, --duration | duration to check for offsets | default: 120 seconds`
