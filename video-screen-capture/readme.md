# Diagnosing Pipette Drift via Screen Capture Video

When I suspect pipette drift is a problem, I often video-record my pipettes and play it back at high speed. This can reveal extremely slow drift which can cause massive problems on time scales of tens of minutes. Tools in this folder assist in this image capture.

This text is a summary of this topic, written in [answer to a question on ResearchGate](https://www.researchgate.net/post/How_do_I_fix_the_drift_of_pipettes_to_do_whole-cell_patch_clamp):

I recommend video-recording your pipette in the recording conditions and reviewing it at high speed. In my case, I wrote a script to take a screenshot every 2 seconds and convert it into a video file.

I used a manual micromanipulator and compared it with movement from two axon headstages with different pipette holders and realized the problem was in the axon headstage / holders. \
https://www.youtube.com/watch?v=JlAYViKUClw&list=UUs3-qUELPY-2AOHa7Q_db5w

I then compared long vs. short plastic pipette holders we had in the lab and realized the shorter ones dramatically outperformed the longer ones\
https://www.youtube.com/watch?v=_-4f0T2Hifo&list=UUs3-qUELPY-2AOHa7Q_db5w

I imagine the plastic (or the rubber holding the pipette) is changing its shape due to temperature fluctuations, and minimizing the size of the plastic pipette holder produced improved stability in my case.

I tried many things to maximize stability of my patch-clamp setup, including wrapping the faraday cage with trash bags to minimize air flow and temperature fluctuation through the cage. Although it looks ridiculous, there was a lot of instant improvement, so I continue to operate it this way. 

Some of the techniques I tried improved stability, some did not, but in every case video recording pipette drift was crucial to critically evaluating (A) how much of a problem there was and (B) which changes to my setup improved the situation.

Note finally that what I thought was mild "drift" was actually very serious random "wiggle", such that hour-long pipette location change was minimal, but minutes-long instability was resulting in poor patches for long durations in a way that I never would have noticed if I didn't video record the movement. I wonder if your probably may be similar... a total difference on final position of one cell body over two hours may be deceptively mild compared to the total movement actually experienced.

Good luck!

https://www.youtube.com/watch?v=JlAYViKUClw&list=UUs3-qUELPY-2AOHa7Q_db5w

https://www.youtube.com/watch?v=_-4f0T2Hifo&list=UUs3-qUELPY-2AOHa7Q_db5w
