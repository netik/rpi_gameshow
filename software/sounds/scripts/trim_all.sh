for i in wav/*.wav; do wav/trim_silence.sh $i trimmed/`basename $i`; done
