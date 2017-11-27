#### Overview

Thanks to PB4, Magus, Agade and Recurse for a fun contest.

I finished third in a very tight battle for the top 4-5 spots. 

Once I saw the contest I decided I was going to try and compete with an AVX based sim, which I'd used before for the CSB multi. For those that don't know AVX is a set of instructions on recent intel processors that operates on 256 bit registers - usually used for 4 double values or 8 float values. One instruction will modify all 8 values at the same time, which can be a large speed up. Marchete has a tech.io tutorial available [here](https://tech.io/playgrounds/283/sse-avx-vectorization). 

Playing CSB with AVX is fairly simple - there are a fixed low number of pods and checkpoints. My implementation runs 8 different games in parallel, so you can try 8 different moves at once and evaluate them. This gave a speed up of 5-6x in CSB.

I very quickly came to realise that AVX here would be much more complicated - there are a lot more objects and varying numbers per game (eg skill effects change depending on the moves used as does wrecks / tankers).  Quite often avx code can look very similar to standard code, but as soon as conditionals get involved it gets much more complicated. By the end I was getting 30-80K sims per turn - until Sunday my bot would only use 20 milliseconds per turn to make submits faster, but I changed it to 40 milliseconds for my final testing. There is still a lot of performance to be gained I feel, a lot of the features I added on top of my previous implementation weren't optimal (I quite often fell back into non vectorised code for handling skills).


#### Getting to gold

As my simulation was going to take a lot of time to develop I submitted a basic heuristic bot in order to unlock all the rules / be able to test things against the top bots. This prioritised closest water / tankers / enemy reapers. This got me 300th in silver when gold opened, and adding oil got me into gold. Source for that is available [here](https://github.com/robostac/cg-meanmax-postmortem/meanmax.go) 

#### Simulation Testing

As I was concerned about the accuracy of simulations after porting it from java to vectorised c++ I wrote a simulation tester to check entire games quickly. Originally I planned to use the data given for replays to generate the games, but found that it wasn't usuable for this (some data was missing and other data wasn't easy to know - velocities in the replay are given before friction, so I'd have to implement oil in my tester to get this to work). Instead I changed my simple bot to output the inputs each turn and downloaded the json outputs from that. I saved a few games without skills to start off with, and then a few games against the current top of the league. In my c++ code I then added a check for the -test command line option to support testing an input.

Due to my usage of AVX my tester outputs 8 turns and then expects 8 responses - this let me check that each of the 8 simulated turns was kept entirely separate. I allowed off by one errors on velocity / position due to my usage of floats instead of doubles. I've never successfully managed to get skill_2.json to work as there is a turn with so many collisions the errors become unmanageable.

My simulation tester (warning, horrible quickly written python) is available [here](https://github.com/robostac/cg-meanmax-postmortem/checksim.py), with some example test data in the [tests](https://github.com/robostac/cg-meanmax-postmortem/tests) directory.

#### Genetic Algorithm

I reused my GA code from csb - the only modification needed was to add a third object to each solution. Each pod gets an array of ints which are then mapped to different moves. Crossover is done by taking two solutions and having 50% chance to take a move from either solution. There is then a 50% chance to mutate any one move to a new random move. The top 8 were kept into the next generation.

Moves 0-35 were targets at 10 degree increments, always with 300 thrust. I had the targets far outside the circle so didn't correct for current position as it would be accurate enough. Until Sunday I was using depth 5, but reduced it to 4 in the afternoon as it performed better.

* Reaper moves 36-41 would cast tar on reaper / destroyer (for player 0 / 1 / 2)
* Destroyer moves 36-39 would fire a grenade 50 points to the N / S / E / W of my reaper. Moves 40-43 would fire a grenade 50 points E/W of the enemy reapers.
* Doof had enough extra moves to fire oil directly into the center of any wreck.

Each solution was tested against an basic enemy (reaper moves to closest water, destroyer/doof do nothing). I also simulated being each enemy for 5 milliseconds and tested my solution against the best two enemies. My solution would then get the minimum score from the 2 different simulations.

I got into legend without any skill implementation in my sim, purely on collection of water. I then added skills on the last Saturday. I wanted to have more targets, but I never got any measurable improvement.


#### Eval

I struggled a lot with eval, as changes I thought would be good often made it worse. In the end I had:

Reaper:
- Distance squared from center 
- Distance squared from destroyer 
- Distance from enemy doof / other enemy doof

Destroyer:
- Distance squared from center.
- Distance from enemy reaper / other enemy reaper
- Distance from 'best' tanker. This was the minimum of each tanker scored as distance * (3/(water+1)), so the more water it had the less it reduced my score.

Doof
- Distance from winning enemy reaper.

Overall 
- Rage * 10
- (2 x My Score - enemy1 score - enemy2score) * 1000 + score from above.
- Using an invalid (range / rage) skill cost 20000 points, as it's easier to filter this during eval than solution generation.

I could not get any eval that included reaper distances to water to be better than this, so wrecks weren't included at all in my eval.

On sunday I was fed up of my reaper going after tankers it thought the enemy would destroy, so I removed any water spawned during my simulations by enemy tankers. This change pushed me into competing for the top spots - without it I think I would have been around 10th place.

#### Failed idea (that might have potential)

On sunday I was struggling to get a noticeable improvement, so decided to copy  my CSB minmax implementation and come up with a way to use that in MM. The best I had was doing my GA for 10 milliseconds for the doof / destroyer, and then minmaxing my reaper against the closest enemy. This would occasionally do amazing things to get water and win games, but usually it would bang into other pods that I hadn't used in the minmax. Also as it was very rare to get beyond depth 3 it wasn't great at finding water that was a long way away. On submit this version never really got past the bottom quarter of legend, but it was able to win some games.

#### Overall

- I liked the additional complexity, added challenges to get a working sim and made move selection much harder.
- Symetrical 1v1v1 was an interesting change which I failed to take advatange of. Looking at winrates at the end I had a much higher 1st place positioning than the other top players, but my 2nd place percentage was terrible. Possibly if I'd optimised more for not losing I'd have got a higher position. This also meant my bot would often start mid legend and slowly work towards the top, whereas I saw other people going straight into the top fairly reguarly (before the legend recalc I was actually 7th and kept climbing during the recalc).
- Submit times were really annoying, by the end it was well over 2 hours. 
- An hour before the contest ended I saw ixanezis a long way at the top with a new bot so quickly made some changes to try and compensate. I was convinced I'd made a huge mistake when that bot finished submission in 7th, but I think it was probably worthwhile.


