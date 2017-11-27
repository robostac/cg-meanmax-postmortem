package main

import (
	"fmt"
	"math"
	"os"
)

//import "os"

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/

type point struct {
	x float64
	y float64
}

func (p *point) Distance(op point) float64 {
	xx := p.x - op.x
	yy := p.y - op.y
	return math.Sqrt(xx*xx + yy*yy)
}

type Reaper struct {
	p point
	v point
}

func main() {
	oiled := 0
	for {
		if oiled > 0 {
			oiled--
		}
		var myScore int
		fmt.Scan(&myScore)
		fmt.Fprintln(os.Stderr, myScore)

		var enemyScore1 int
		fmt.Scan(&enemyScore1)
		fmt.Fprintln(os.Stderr, enemyScore1)

		var enemyScore2 int
		fmt.Scan(&enemyScore2)
		fmt.Fprintln(os.Stderr, enemyScore2)
		etgt := 1
		if enemyScore2 > enemyScore1 {
			etgt = 2
		}
		var myRage int
		fmt.Scan(&myRage)
		fmt.Fprintln(os.Stderr, myRage)

		var enemyRage1 int
		fmt.Scan(&enemyRage1)
		fmt.Fprintln(os.Stderr, enemyRage1)

		var enemyRage2 int
		fmt.Scan(&enemyRage2)
		fmt.Fprintln(os.Stderr, enemyRage2)

		var unitCount int
		fmt.Scan(&unitCount)
		fmt.Fprintln(os.Stderr, unitCount)
		var me Reaper
		var dest Reaper
		var doof Reaper
		var tgt point
		var tgt2 point
		var tgt3 point
		var md = 000000.0
		var md2 = 1000000.0
		var md3 = 1000000.0
		var erunner Reaper
		var enemyBest point
		var enemyBestD = 10000000.0
		for i := 0; i < unitCount; i++ {
			var unitId, unitType, player int
			var mass float64
			var radius, x, y, vx, vy, extra, extra2 int

			fmt.Scan(&unitId, &unitType, &player, &mass, &radius, &x, &y, &vx, &vy, &extra, &extra2)
			fmt.Fprintln(os.Stderr, unitId, unitType, player, mass, radius, x, y, vx, vy, extra, extra2)
			if player == 0 {
				if unitType == 0 {
					me = Reaper{point{float64(x), float64(y)}, point{float64(vx), float64(vy)}}
				}
				if unitType == 1 {
					dest = Reaper{point{float64(x), float64(y)}, point{float64(vx), float64(vy)}}
				}
				if unitType == 2 {
					doof = Reaper{point{float64(x), float64(y)}, point{float64(vx), float64(vy)}}
				}
			}
			p := point{float64(x), float64(y)}
			if unitType == 4 {

				dd := float64(extra+1) / p.Distance(me.p)
				if dd > md {
					md = dd
					tgt = p
				}
				dd = p.Distance(erunner.p)
				if dd < enemyBestD && dd < 2000 {
					enemyBestD = dd
					enemyBest = p
				}
			}
			if unitType == 3 && extra > 0 {
				dd := p.Distance(dest.p)
				if dd < md2 {
					md2 = dd
					tgt2 = p
				}
			}
			if unitType == 0 && player == etgt {
				erunner = Reaper{point{float64(x), float64(y)}, point{float64(vx), float64(vy)}}
				dd := p.Distance(doof.p)
				if dd < md3 {
					md3 = dd
					tgt3.x = erunner.p.x + erunner.v.x
					tgt3.y = erunner.p.y + erunner.v.y
				}
			}

		}
		d := point{0, 0}
		// fmt.Fprintln(os.Stderr, "Debug messages...")
		if tgt != d {
			fmt.Println(int(tgt.x-1.5*me.v.x), int(tgt.y-1.5*me.v.y), 300) // Write action to stdout
		} else {
			//fmt.Println(int(tgt2.x-me.v.x), int(tgt2.y-me.v.y), 300) // Write action to stdout
			fmt.Println(int(d.x), int(d.y), 300) // Write action to stdout
		}
		if false && myRage > 60 && dest.p.Distance(point{erunner.p.x + erunner.v.x, erunner.p.y + erunner.v.y}) < 2000 {
			fmt.Println("SKILL", erunner.p.x+erunner.v.x, erunner.p.y+erunner.v.y)
		} else {
			fmt.Println(int(tgt2.x), int(tgt2.y), 300) // Write action to stdout
		}
		if enemyBest != d && myRage > 30 && (doof.p.Distance(enemyBest) < 2000) && oiled == 0 && tgt.Distance(enemyBest) > 1000 {
			fmt.Println("SKILL", enemyBest.x, enemyBest.y)
			oiled = 3
		} else {
			fmt.Println(int(tgt3.x), int(tgt3.y), 300) // Write action to stdout
		}
	}
}
