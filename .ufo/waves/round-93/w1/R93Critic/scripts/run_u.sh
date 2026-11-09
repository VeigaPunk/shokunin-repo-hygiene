#!/bin/bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin
S=/fast/scratch/hyaku/souji-r93/R93Critic; D=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-93/w1/R93Critic
for m in U1-or-unknown U2-width-lt4 U3-width-lt2 U5-eq-minus1; do
 for pop in r93 r92; do
  P=census/round-93/c1-false-rows.tsv; H=census/round-93/c1-false-row-harness.py
  if [ $pop = r92 ]; then P=census/round-92/c1-false-rows.tsv; H=census/round-92/c1-false-row-harness.py; fi
  W=$S/cu-$m-$pop; rm -rf $W; mkdir -p $W
  python3 -B $H --counter $S/c2x/$m.py --lane . --fleet-root /home/vgpnk/Projects/shokunin --work $W --population $P > $D/receipts/unchosen-$m-$pop.txt 2>&1
  echo "$m $pop rc=$?" >> $D/receipts/unchosen-summary.txt
  grep -E "match=no|^SUMMARY" $D/receipts/unchosen-$m-$pop.txt >> $D/receipts/unchosen-summary.txt
 done
done
echo DONE >> $D/receipts/unchosen-summary.txt
